import os
import shutil
from time import time
from typing import Callable, Generic, Type, TypeVar
from uuid import uuid4

import numpy as np
import numpy.typing as npt
from constants.lib_constants import LibTypes
from knowledge_base.document.doc_embedder import DocEmbedder
from library.document.doc_lib_vector_db import DocLibVectorDb
from library.document.doc_provider_base import DocProviderBase
from library.document.sql import DB_NAME
from library.embedding_record_table import *
from library.lib_base import *
from loggers import doc_lib_logger as LOGGER
from utils.errors.task_errors import (LockAcquisitionFailure,
                                      TaskCancellationException)
from utils.lock_context import LockContext
from utils.task_runner import report_progress

"""
from sentence_transformers import CrossEncoder, SentenceTransformer
from faiss import IndexFlatL2, IndexIVFFlat  # Put faiss import AFTER sentence_transformers, strange SIGSEGV error otherwise on OSX
"""


D = TypeVar('D', bound=DocProviderBase)


class DocumentLib(Generic[D], LibraryBase):
    """Define a generic document library
    - A document library is a collection of many different documents such as novels, articles, chat history
    - Each document will have it's own document DB table for storing raw data in DB in a structured way
    - Each document will also have it's own vector DB for storing embeddings of each document
    - A document library can only have one active document at a time
    """

    def __init__(self,
                 lib_path: str,
                 lib_name: str,
                 uuid: str):
        """
        Args:
            lib_path (str): Path to the library
            lib_name (str): Name to the library
            uuid (str): UUID of the library
        """
        if not uuid or not lib_name:
            raise LibraryError('Invalid UUID or library name')
        super().__init__(lib_path)

        # Load metadata
        LOGGER.info(f'Loading metadata for {lib_name}')
        if not self._metadata_exists():
            initial_metadata: dict = BASIC_METADATA | {
                'type': LibTypes.DOCUMENT.value,
                'uuid': uuid,
                'name': lib_name,
            }
            self.initialize_metadata(initial_metadata)
        else:
            self.load_metadata(uuid, lib_name)

        if not self._metadata or not self.uuid:
            raise LibraryError('Library metadata not initialized')

        self.doc_type: str = ''  # The type of current active document
        self.path_db: str = os.path.join(self._path_lib_data, DB_NAME)
        self._embedding_table: EmbeddingRecordTable = EmbeddingRecordTable(self.path_db)

        self.__doc_provider: D | None = None
        self.__vector_db: DocLibVectorDb | None = None
        self.__embedder: DocEmbedder | None = None

    """
    Private methods
    """

    def __initialize_doc(self,
                         relative_path: str,
                         provider_type: Type[D],
                         uuid: str,
                         progress_reporter: Callable[[int, int, str | None], None] | None,
                         cancel_event: Event | None):
        """Initialize a document under the library
        """
        if not relative_path:
            raise LibraryError('Invalid relative path')

        if self._embedding_table.relative_path_exists(relative_path, ongoing=False):
            self.use_doc(relative_path, provider_type)
            return

        doc_path: str = os.path.join(self.path_lib, relative_path)
        if not os.path.isfile(doc_path):
            raise LibraryError(f'Invalid doc path: {doc_path}')

        with LockContext(self._file_lock) as lock:
            if not lock.acquired:
                raise LockAcquisitionFailure('There is already a scan task running')

            # Start to track embedding and progress
            with OngoingEmbeddingManager(self._embedding_table, relative_path, uuid):
                # Create doc provider for this doc
                LOGGER.info(f'Document initialization started for {relative_path}')
                self.__doc_provider = provider_type(self.path_db,
                                                    uuid,
                                                    doc_path=doc_path,
                                                    progress_reporter=progress_reporter)
                total: int = self.__doc_provider.get_record_count()

                # Do embedding, and create vector DB for this doc
                # - The threshold "7020" is from IVF's warning message "WARNING clustering 2081 points to 180 centroids: please provide at least 7020 training points"
                use_IVF: bool = total > 7020
                self.__vector_db = DocLibVectorDb(self._path_lib_data, uuid)

                embedding_list: list[npt.ArrayLike] = list()
                previous_progress: int = -1
                first_round: bool = True
                start: float = time()

                LOGGER.info(f'Total records: {total}, start embedding')
                for i, row in enumerate(self.__doc_provider.get_all_records()):
                    if cancel_event and cancel_event.is_set():
                        LOGGER.info('Embedding cancelled')
                        raise TaskCancellationException('Library initialization cancelled')

                    # If reporter is given, report progress to task manager
                    # - Reduce report frequency, only report when progress changes
                    current_progress: int = int(i / total * 100)
                    if current_progress > previous_progress:
                        previous_progress = current_progress
                        report_progress(progress_reporter, current_progress, current_phase=2, phase_name='EMBEDDING')

                    key_text: str = self.__doc_provider.get_key_text_from_record(row)
                    embedding: np.ndarray = self.__embedder.embed_text(key_text)  # type: ignore

                    # For IVF case, save all embeddings for further training
                    if use_IVF:
                        embedding_list.append(embedding)
                        continue

                    # For non-IVF (Flat) case, add embedding to index directly
                    if first_round:
                        first_round = False
                        dimension: int = embedding.size
                        self.__vector_db.initialize_index(dimension, training_set=None)
                    self.__vector_db.add(None, embedding.tolist())

                if use_IVF:
                    # "ndarray.shape" is used to get the dimension of a matrix, the type is tuple
                    # The length of the tuple is the dimension of the array, and each element represents the length of the array in that dimension:
                    # - For a 2D matrix, the shape is a tuple of length 2: shape[0] is the number of rows, shape[1] is the number of columns
                    # - For example: self.embeddings.shape is (1232, 76), which means there are 1232 texts, and each text is converted to a 76-dimension vector
                    embeddings: np.ndarray = np.asarray(embedding_list)
                    text_count: int = embeddings.shape[0]
                    dimension: int = embeddings.shape[1]
                    LOGGER.info(f'Building index with dimension {dimension}')
                    self.__vector_db.initialize_index(dimension, training_set=embeddings, dataset_size=text_count)
                    LOGGER.info('Index built')

                self.__vector_db.persist()

            timestamp: datetime = datetime.now()
            time_taken: float = time() - start
            # Row format: (id, timestamp, ongoing, uuid, relative_path)
            self._embedding_table.insert_row((timestamp, 0, uuid, relative_path))
            LOGGER.info(f'Document initialization finished for {relative_path}, cost: {time_taken:.2f}s')

    def __retrieve(self, text: str, top_k: int = 10) -> list[tuple]:
        """Get top_k most similar candidates under the given document (relative path)
        """
        if not text or top_k <= 0:
            return list()

        # If no provider/vector DB
        if not self.__doc_provider or not self.__vector_db:
            raise LibraryError('No active document, please switch to a document first')

        LOGGER.info(f'Retrieving {top_k} candidates for {text}')
        query_embedding: np.ndarray = self.__embedder.embed_text(text)  # type: ignore
        ids: list[np.int64] = self.__vector_db.query(np.asarray([query_embedding]), top_k)
        res: list[tuple] = list()

        for i64 in ids:
            # If number of candidates is lesser than top_k, then the rest IDs are all -1
            i: int = int(i64)
            if i == -1:
                break

            # in-mem index's ID starts from 0 but DB's ID column starts from 1, plus 1
            record: tuple | None = self.__doc_provider.get_record_by_id(i + 1)
            if record:
                res.append(record)
        return res

    def __rerank(self, text: str, candidate_rows: list[tuple]) -> list[tuple]:
        if not self.__doc_provider:
            raise LibraryError('No active document, please switch to a document first')

        LOGGER.info(f'Reranking {len(candidate_rows)} candidates for {text}')
        candidates_str: list[str] = [
            self.__doc_provider.get_key_text_from_record(c) for c in candidate_rows
        ]
        scores: npt.ArrayLike = self.__embedder.predict_similarity_batch(text, candidates_str)  # type: ignore

        # Re-sort the ranking result
        # - np.argsort() returns the ID from original array (`scores`) based on it's corresponding score in ascending order, use [::-1] to reverse it
        # - https://blog.csdn.net/maoersong/article/details/21875705
        sorted_ids: list[int] = np.argsort(scores)[::-1].tolist()

        # Reorder the candidates list by the ranking
        return [candidate_rows[i] for i in sorted_ids]

    """
    Overridden public methods from LibraryBase
    """

    def is_ready(self) -> bool:
        if not self._metadata_exists() or not self._embedding_table or \
                not self.__vector_db or not self.__embedder or not self.__doc_provider:
            return False
        return True

    def use_doc(self,
                relative_path: str,
                provider_type: Type[D],
                force_init: bool = False,
                progress_reporter: Callable[[int, int, str | None], None] | None = None,
                cancel_event: Event | None = None):
        if not relative_path:
            raise LibraryError('Invalid relative path')
        if not self.__embedder:
            raise LibraryError('Embedder not set')

        relative_path = relative_path.strip().lstrip(os.path.sep)
        LOGGER.info(f'Switching to document {relative_path}, force init: {force_init}')

        # Check if the file is gone before switch to given doc
        # - Also clean up the embedding if there are leftover
        if not os.path.isfile(os.path.join(self.path_lib, relative_path)):
            if self._embedding_table.relative_path_exists(relative_path):
                self.delete_file_embedding(relative_path)
            LOGGER.error(f'Document {relative_path} does not exist')
            raise LibraryError('File does not exist')

        need_initialization: bool = force_init or \
            not self._embedding_table.relative_path_exists(relative_path, ongoing=False)
        if not need_initialization:
            # If no need to initialize, just switch to the doc
            LOGGER.info(f'Target document already initialized, load data from disk')
            uuid: str = self._embedding_table.get_uuid(relative_path, ongoing=False)  # type: ignore
            self.__doc_provider = provider_type(self.path_db,
                                                uuid,
                                                doc_path=None,
                                                progress_reporter=progress_reporter)
            self.__vector_db = DocLibVectorDb(self._path_lib_data, uuid)
        else:
            # Clean up existing embeddings or leftover if any when:
            # - If this is a force init
            # - If given doc is in ongoing list
            if force_init or self._embedding_table.relative_path_exists(relative_path, ongoing=True):
                LOGGER.info(
                    f'Clean up existing embeddings for {relative_path} because of force init or target doc is in ongoing list')
                self.delete_file_embedding(relative_path)

            try:
                LOGGER.info(f'Document initialization started for {relative_path}')
                uuid: str = str(uuid4())
                self.__initialize_doc(relative_path, provider_type, uuid, progress_reporter, cancel_event)
            except Exception as e:
                # On cancel, clean this doc's leftover
                self.delete_file_embedding(relative_path)
                if isinstance(e, TaskCancellationException):
                    LOGGER.warn('Document initialization cancelled, progress abandoned')
                else:
                    LOGGER.error(f'Document initialization failed: {e}')
                    raise LibraryError(f'Document initialization failed: {e}')

        if self.__doc_provider:
            self.doc_type = self.__doc_provider.DOC_TYPE

    def demolish(self):
        """Delete the doc library, it purges all library data
        1. Delete vector index folder
        2. Delete DB file
        3. Delete metadata file

        Simply purge the library data folder
        """
        LOGGER.warning(f'Demolish document library: {self.path_lib}')
        with LockContext(self._file_lock) as lock:
            if not lock.acquired:
                raise LockAcquisitionFailure('There is already a scan task running, cancel the task and try again')

            self._embedding_table = None  # type: ignore
            self.__embedder = None
            self.__doc_provider = None
            self.__vector_db = None
            shutil.rmtree(self._path_lib_data)
            LOGGER.warning(f'Library demolished: {self.path_lib}')

    def delete_file_embedding(self, relative_path: str) -> bool:
        """Remove the embedding of given document but keep the file
        1. Delete the document's table from DB
        2. Delete the document's vector index
        """
        if not relative_path:
            return False

        relative_path = relative_path.strip().lstrip(os.path.sep)
        if not relative_path:
            return False

        # UUID is mandatory for data cleanup, retrieve UUID from scan history
        uuid: str | None = self._embedding_table.get_uuid(relative_path)
        if not uuid:
            return False

        is_active_doc: bool = False
        if self.__doc_provider:
            # If doc provider instance exists, then provider's table name is the active doc's UUID
            is_active_doc = self.__doc_provider.get_table_name() == uuid

        if not is_active_doc:
            # For non-active doc, create temp provider and temp vector DB to delete leftover
            LOGGER.warn(f'Remove document embedding for: {relative_path}, UUID: {uuid}, this document is not active')
            tmp_provider: DocProviderBase = DocProviderBase(self.path_db,
                                                            uuid)
            tmp_provider.delete_table()
            tmp_vector_db: DocLibVectorDb = DocLibVectorDb(self._path_lib_data, uuid)
            tmp_vector_db.delete_db()
        else:
            LOGGER.warn(f'Remove document embedding for: {relative_path}, UUID: {uuid}, this document is active')
            self.__doc_provider.delete_table()  # type: ignore
            self.__doc_provider = None
            self.__vector_db.delete_db()  # type: ignore
            self.__vector_db = None
            self.doc_type = ''

        # Remove doc from embedding history after deletion if this doc is tracked
        self._embedding_table.delete_by_relative_path(relative_path)
        return True

    """
    Public methods
    """

    def lib_is_ready_on_current_doc(self, relative_path: str) -> bool:
        """Check if library is ready on the given document
        """
        if not self.is_ready() or not relative_path:
            return False

        relative_path = relative_path.strip().lstrip(os.path.sep)
        if not self._embedding_table.relative_path_exists(relative_path, ongoing=False):
            return False

        # Doc provider's table name is the active doc's UUID
        return self.__doc_provider.get_table_name() == self._embedding_table.get_uuid(relative_path)  # type: ignore

    def set_embedder(self, embedder: DocEmbedder):
        self.__embedder = embedder

    """
    Query methods
    """

    @ensure_lib_is_ready
    def query(self, query_text: str, top_k: int = 10, rerank: bool = False) -> list[tuple]:
        """Query given text in the active document

        Args:
            query_text (str): _description_
            top_k (int, optional): _description_. Defaults to 10.
            rerank (bool, optional): If the result should be reranked. Defaults to False.
            rerank_lambda (int, optional): The function used to fetch specific data from a row for rerank.
            It needs to accept a tuple (the row data) and return a string. Defaults to None.
        """
        LOGGER.info(f'Querying {query_text} with top {top_k} matches')
        if rerank:
            candidates: list[tuple] = self.__retrieve(query_text, top_k * 10)
            reranked: list[tuple] = self.__rerank(query_text, candidates)
            return reranked[:top_k]
        else:
            return self.__retrieve(query_text, top_k)
