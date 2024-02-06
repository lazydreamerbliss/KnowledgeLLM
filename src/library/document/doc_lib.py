import os
import shutil
from typing import Callable, Generic, Type, TypeVar
from uuid import uuid4

import numpy as np
import numpy.typing as npt
from tqdm import tqdm

from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.document.doc_provider_base import DocProviderBase
from library.document.doc_lib_vector_db import DocLibVectorDb
from library.document.sql import DB_NAME
from library.lib_base import *
from utils.exceptions.task_errors import TaskCancellationException
from utils.tqdm_context import TqdmContext

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
            uuid (str): UUID of the library
        """
        if not uuid or not lib_name:
            raise LibraryError('Invalid UUID or library name')
        super().__init__(lib_path)

        # Load metadata
        with TqdmContext('Loading library metadata...', 'Loaded'):
            if not self.metadata_exists():
                initial_metadata: dict = BASIC_metadata | {
                    'type': 'document',
                    'uuid': uuid,
                    'name': lib_name,
                }
                self.initialize_metadata(initial_metadata)
                initial_scan_profile: dict = BASIC_profile | {
                    'uuid': uuid,
                }
                self.initialize_metadata(initial_scan_profile, scan_profile=True)
            else:
                self.load_metadata(uuid, lib_name)
        if not self._metadata or not self.uuid:
            raise LibraryError('Library metadata not initialized')

        self.path_db: str = os.path.join(self._path_lib_data, DB_NAME)
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
                         progress_reporter: Callable[[int], None] | None,
                         cancel_event: Event | None):
        """Initialize a document under the library
        """
        if not relative_path:
            raise LibraryError('Invalid relative path')

        if relative_path in self.get_embedded_files():
            self.use_doc(relative_path, provider_type)
            return

        doc_path: str = os.path.join(self._path_lib, relative_path)
        if not os.path.isfile(doc_path):
            raise LibraryError(f'Invalid doc path: {doc_path}')

        # Pre-check if given doc is in unfinished list, clean up leftover if any
        if relative_path in self.get_unfinished_files():
            self.remove_doc_embedding(relative_path, provider_type)

        # Record info in metadata before embedding
        self.get_unfinished_files()[relative_path] = uuid
        self._save_scan_profile()

        # Create doc provider for this doc
        self.__doc_provider = provider_type(self.path_db,
                                            uuid,
                                            doc_path=doc_path,
                                            re_dump=False)  # type: ignore
        total: int = self.__doc_provider.get_record_count()

        # Do embedding, and create vector DB for this doc
        # - The threshold "7020" is from IVF's warning message "WARNING clustering 2081 points to 180 centroids: please provide at least 7020 training points"
        use_IVF: bool = total > 7020
        self.__vector_db = DocLibVectorDb(self._path_lib_data, uuid)

        embedding_list: list[npt.ArrayLike] = list()
        previous_progress: int = -1
        first_round: bool = True
        for i, row in tqdm(enumerate(self.__doc_provider.get_all_records()), desc='Embedding data', ascii=' |'):
            if cancel_event and cancel_event.is_set():
                tqdm.write('Embedding cancelled')
                raise TaskCancellationException('Library initialization cancelled')

            # If reporter is given, report progress to task manager
            # - Reduce report frequency, only report when progress changes
            current_progress: int = int(i / total * 100)
            if current_progress > previous_progress:
                previous_progress = current_progress
                self.report_progress(progress_reporter, current_progress)

            key_text: str = self.__doc_provider.get_key_text_from_record(row)
            embedding: np.ndarray = self.__embedder.embed_text(key_text)  # type: ignore

            # For IVF case, save all embeddings for further training
            if use_IVF:
                embedding_list.append(embedding)  # type: ignore
                continue

            # For non-IVF (Flat) case, add embedding to index directly
            if first_round:
                first_round = False
                dimension: int = embedding.size
                self.__vector_db.initialize_index(dimension, training_set=None)
            self.__vector_db.add(None, embedding.tolist())

        if use_IVF:
            embeddings: np.ndarray = np.asarray(embedding_list)

            # "ndarray.shape" is used to get the dimension of a matrix, the type is tuple
            # The length of the tuple is the dimension of the array, and each element represents the length of the array in that dimension:
            # - For a 2D matrix, the shape is a tuple of length 2: shape[0] is the number of rows, shape[1] is the number of columns
            # - For example: self.embeddings.shape is (1232, 76), which means there are 1232 texts, and each text is converted to a 76-dimension vector
            text_count: int = embeddings.shape[0]
            dimension: int = embeddings.shape[1]
            with TqdmContext(f'Building index with dimension {dimension}...', 'Done'):
                self.__vector_db.initialize_index(dimension, training_set=embeddings, dataset_size=text_count)

        self.__vector_db.persist()

        # Record info in metadata after finished embedding
        self.get_unfinished_files().pop(relative_path, None)
        self.get_embedded_files()[relative_path] = uuid
        self._save_scan_profile()

    def __retrieve(self, text: str, top_k: int = 10) -> list[tuple]:
        """Get top_k most similar candidates under the given document (relative path)
        """
        if not text or top_k <= 0:
            return list()

        # If no provider/vector DB
        if not self.__doc_provider or not self.__vector_db:
            raise LibraryError('No active document, please switch to a document first')

        query_embedding: np.ndarray = self.__embedder.embed_text(text)  # type: ignore
        ids: list[np.int64] = self.__vector_db.query(np.asarray([query_embedding]), top_k)  # type: ignore
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

        tqdm.write(f'Reranking {len(candidate_rows)} candidates...')
        candidates_str: list[str] = [
            self.__doc_provider.get_key_text_from_record(c) for c in candidate_rows
        ]  # type: ignore
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

    def lib_is_ready(self) -> bool:
        if not self.metadata_exists():
            return False
        if not self.__embedder:
            return False
        if not self.__doc_provider:
            return False
        return True

    def use_doc(self,
                relative_path: str,
                provider_type: Type[D],
                force_init: bool = False,
                progress_reporter: Callable[[int], None] | None = None,
                cancel_event: Event | None = None):
        if not relative_path:
            raise LibraryError('Invalid relative path')
        if not self.__embedder:
            raise LibraryError('Embedder not set')

        relative_path = relative_path.lstrip(os.path.sep)
        embedded_files: dict[str, str] = self.get_embedded_files()
        need_initialization: bool = force_init or relative_path not in embedded_files
        # If no need to initialize, just switch to the doc and return
        if not need_initialization:
            with TqdmContext(f'Switching to doc {relative_path}, loading data...', 'Done'):
                uuid: str = embedded_files[relative_path]
                self.__doc_provider = provider_type(self.path_db,
                                                    uuid,
                                                    doc_path=None,
                                                    re_dump=False)  # type: ignore
                self.__vector_db = DocLibVectorDb(self._path_lib_data, uuid)
            return

        # Do initialization
        # - Clean up leftover for force_init
        if force_init and relative_path in embedded_files:
            self.remove_doc_embedding(relative_path, provider_type)

        try:
            uuid: str = str(uuid4())
            self.__initialize_doc(relative_path, provider_type, uuid, progress_reporter, cancel_event)
        except TaskCancellationException:
            # On cancel, clean this doc's leftover and remove from embedding history
            self.remove_doc_embedding(relative_path, provider_type)
            self.get_unfinished_files().pop(relative_path, None)
            self._save_scan_profile()

    def demolish(self):
        """Delete the doc library, it purges all library data
        1. Delete vector index folder
        2. Delete DB file
        3. Delete metadata file

        Simply purge the library data folder
        """
        self.__embedder = None
        self.__doc_provider = None
        self.__vector_db = None
        shutil.rmtree(self._path_lib_data)

    def add_file(self, folder_relative_path: str, source_file: str):
        pass

    def delete_files(self, relative_path: str, **kwargs):
        if not relative_path:
            raise LibraryError('Invalid relative path')

        provider_type: Type[D] = kwargs.get('provider_type', None)
        if not provider_type:
            raise LibraryError('Provider type not provided')

        relative_path = relative_path.lstrip(os.path.sep)
        doc_path: str = os.path.join(self._path_lib, relative_path)
        if os.path.isfile(doc_path):
            os.remove(doc_path)
        self.remove_doc_embedding(relative_path, provider_type)

    """
    Public methods
    """

    def lib_is_ready_on_current_doc(self, relative_path: str) -> bool:
        """Check if library is ready on the given document
        - This need to ensure lib_is_ready() and confirm the given relative_path is the current doc
        """
        if not self.lib_is_ready() or not relative_path:
            return False

        relative_path = relative_path.lstrip(os.path.sep)
        if relative_path not in self.get_embedded_files():
            return False
        return self.__doc_provider.get_table_name() == self.get_embedded_files()[relative_path]  # type: ignore

    def set_embedder(self, embedder: DocEmbedder):
        self.__embedder = embedder

    def remove_doc_embedding(self, relative_path: str, provider_type: Type[D]):
        """Remove the embedding of a document under the library
        1. Delete the document's table from DB
        2. Delete the document's vector index

        - Relative path is mandatory, with optional UUID
        - Optional UUID is used to remove existing embedding if the relative path is not in scan profile, this can happen when the embedding is cancelled in half way
        - Provided relative path does not need to be exists in file system, as the file might be deleted already but the leftover still exists
        """
        if not relative_path:
            raise LibraryError('Invalid relative path')

        relative_path = relative_path.lstrip(os.path.sep)

        # UUID is mandatory for data cleanup, retrieve UUID from scan profile
        embedded_files: dict[str, str] = self.get_embedded_files()
        unfinished_files: dict[str, str] = self.get_unfinished_files()
        if relative_path in embedded_files:
            uuid = embedded_files[relative_path]
        elif relative_path in unfinished_files:
            uuid = unfinished_files[relative_path]
        else:
            raise LibraryError(f'Provided relative path cannot be found in scan profile: {relative_path}')

        is_active_doc: bool = False
        if self.__doc_provider:
            is_active_doc = self.__doc_provider.get_table_name() == uuid

        with TqdmContext(f'Removing embedding data for {uuid}...', 'Done'):
            if not is_active_doc:
                # For non-active doc, create temp provider and temp vector DB to delete leftover
                tmp_provider: DocProviderBase = provider_type(self.path_db,
                                                              uuid,
                                                              doc_path=None,
                                                              re_dump=False)  # type: ignore
                tmp_provider.delete_table()
                tmp_vector_db: DocLibVectorDb = DocLibVectorDb(self._path_lib_data, uuid)  # type: ignore
                tmp_vector_db.delete_db()
            else:
                self.__doc_provider.delete_table()  # type: ignore
                self.__doc_provider = None
                self.__vector_db.delete_db()  # type: ignore
                self.__vector_db = None

        # Remove doc from embedding history after deletion
        embedded_files.pop(relative_path, None)
        unfinished_files.pop(relative_path, None)
        self._save_scan_profile()

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
        tqdm.write(f'Q: {query_text}, get top {top_k} matches...')
        if rerank:
            candidates: list[tuple] = self.__retrieve(query_text, top_k * 10)
            reranked: list[tuple] = self.__rerank(query_text, candidates)
            return reranked[:top_k]
        else:
            return self.__retrieve(query_text, top_k)
