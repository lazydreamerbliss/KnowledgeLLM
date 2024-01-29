import os
from typing import Callable, Generic, Type, TypeVar
from uuid import uuid4

import numpy as np
import numpy.typing as npt
from tqdm import tqdm

from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.document.doc_provider import DocProviderBase
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
        super().__init__(lib_path)

        # Load metadata
        with TqdmContext('Loading library metadata...', 'Loaded'):
            if not self.metadata_file_exists():
                initial_metadata: dict = BASIC_METADATA | {
                    'type': 'document',
                    'uuid': uuid,
                    'name': lib_name,
                    'embedded_docs': dict(),  # List of embedded documents under the library
                    'unfinished_docs': dict(),  # List of documents that are not finished embedding yet
                }
                self.initialize_metadata(initial_metadata)
            else:
                self.load_metadata(uuid, lib_name)
        if not self._metadata or not self.uuid:
            raise LibraryError('Library metadata not initialized')

        self.path_db: str = os.path.join(self.path_lib_data, DB_NAME)
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

        if relative_path in self._metadata['embedded_docs']:
            self.use_doc(relative_path, provider_type)
            return

        doc_path: str = os.path.join(self.path_lib, relative_path)
        if not os.path.isfile(doc_path):
            raise LibraryError(f'Invalid doc path: {doc_path}')

        # Pre-check if given doc is in unfinished list, clean up leftover if any
        if relative_path in self._metadata['unfinished_docs']:
            old_uuid: str = self._metadata['unfinished_docs'][relative_path]
            self.remove_doc_embedding(None, old_uuid, provider_type)
            self._metadata['unfinished_docs'].pop(relative_path, None)
            self.save_metadata()

        # Record info in metadata before embedding
        self._metadata['unfinished_docs'][relative_path] = uuid
        self.save_metadata()

        # Create doc provider for this doc
        self.__doc_provider = provider_type(self.path_db,
                                            uuid,
                                            doc_path=doc_path,
                                            re_dump=False)  # type: ignore

        # Do embedding, and create vector DB for this doc
        embeddings_list: list[npt.ArrayLike] = list()
        total_records: int = self.__doc_provider.get_record_count()
        previous_progress: int = -1
        for i, row in tqdm(enumerate(self.__doc_provider.get_all_records()), desc='Embedding data', ascii=' |'):
            if cancel_event and cancel_event.is_set():
                tqdm.write('Embedding cancelled')
                raise TaskCancellationException('Library initialization cancelled')

            # If reporter is given, report progress to task manager
            # - Reduce report frequency, only report when progress changes
            if progress_reporter:
                try:
                    current_progress: int = int(i / total_records * 100)
                    if current_progress > previous_progress:
                        previous_progress = current_progress
                        progress_reporter(current_progress)
                except:
                    pass

            embeddings_list.append(self.__embedder.embed_text(self.__doc_provider.EMBED_LAMBDA(row)))  # type: ignore
        embeddings: np.ndarray = np.asarray(embeddings_list)

        # "ndarray.shape" is used to get the dimension of a matrix, the type is tuple
        # The length of the tuple is the dimension of the array, and each element represents the length of the array in that dimension:
        # - For a 2D matrix, the shape is a tuple of length 2: shape[0] is the number of rows, shape[1] is the number of columns
        # - For example: self.embeddings.shape is (1232, 76), which means there are 1232 texts, and each text is converted to a 76-dimension vector
        text_count: int = embeddings.shape[0]
        dimension: int = embeddings.shape[1]
        self.__vector_db = DocLibVectorDb(self.path_lib_data, uuid)
        with TqdmContext(f'Building index with dimension {dimension}...', 'Done'):
            self.__vector_db.initialize_index(dimension, training_set=embeddings, dataset_size=text_count)
            self.__vector_db.persist()

        # Record info in metadata after finished embedding
        self._metadata['unfinished_docs'].pop(relative_path, None)
        self._metadata['embedded_docs'][relative_path] = uuid
        self.save_metadata()

    def __retrieve(self, text: str, top_k: int = 10) -> list[tuple]:
        """Get top_k most similar candidates under the given document (relative path)
        """
        if not text or top_k <= 0:
            return list()

        # If no provider/vector DB
        if not self.__doc_provider or not self.__vector_db:
            raise LibraryError('No active document, please switch to a document first')

        query_embedding: npt.ArrayLike = self.__embedder.embed_text(text)  # type: ignore
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

    def __rerank(self, text: str, candidates: list[tuple]) -> list[tuple]:
        if not self.__doc_provider:
            raise LibraryError('No active document, please switch to a document first')

        tqdm.write(f'Reranking {len(candidates)} candidates...')
        candidates_str: list[str] = [self.__doc_provider.RERANK_LAMBDA(c) for c in candidates]  # type: ignore
        scores: npt.ArrayLike = self.__embedder.predict_similarity_batch(text, candidates_str)  # type: ignore

        # Re-sort the ranking result
        # - np.argsort() returns the indices in ascending order, so here we use [::-1] to reverse it
        # - https://blog.csdn.net/maoersong/article/details/21875705
        sorted_ids: np.ndarray = np.argsort(scores)[::-1]

        # Reorder the candidates list by the ranking
        return [candidates[i] for i in sorted_ids]

    """
    Overridden public methods from LibraryBase
    """

    def lib_is_ready(self) -> bool:
        if not self.metadata_file_exists():
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
        need_initialization: bool = force_init or relative_path not in self._metadata['embedded_docs']
        # If no need to initialize, just switch to the doc and return
        if not need_initialization:
            with TqdmContext(f'Switching to doc {relative_path}, loading data...', 'Done'):
                uuid: str = self._metadata['embedded_docs'][relative_path]
                self.__doc_provider = provider_type(self.path_db,
                                                    uuid,
                                                    doc_path=None,
                                                    re_dump=False)  # type: ignore
                self.__vector_db = DocLibVectorDb(self.path_lib_data, uuid)
            return

        # Do initialization
        if force_init and relative_path in self._metadata['embedded_docs']:
            self.remove_doc_embedding(relative_path, None, provider_type)

        uuid: str = str(uuid4())
        try:
            self.__initialize_doc(relative_path, provider_type, uuid, progress_reporter, cancel_event)
        except TaskCancellationException:
            # On cancel, clean this doc's leftover
            self.remove_doc_embedding(None, uuid, provider_type)
            self._metadata['unfinished_docs'].pop(relative_path, None)
            self.save_metadata()

    def delete_lib(self):
        """Delete the doc library, it purges all library data
        1. Delete vector index folder
        2. Delete DB file
        3. Delete metadata file
        """
        DocLibVectorDb.delete_mem_db_folder(self.path_lib_data)
        DocProviderBase.delete_db_file(self.path_db)

        self.path_metadata
        if os.path.isfile(self.path_metadata):
            os.remove(self.path_metadata)

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
        if relative_path not in self._metadata['embedded_docs']:
            return False
        return self.__doc_provider.table.table_name == self._metadata['embedded_docs'][relative_path]  # type: ignore

    def set_embedder(self, embedder: DocEmbedder):
        self.__embedder = embedder

    def remove_doc_embedding(self, relative_path: str | None, uuid: str | None, provider_type: Type[D]):
        """Remove the embedding of a document under the library
        1. Delete the document's table from DB
        2. Delete the document's vector index

        If relative_path is None, then UUID must be provided, and vice versa
        If both are provided, only relative_path will be used
        """
        if not relative_path and not uuid:
            raise LibraryError('Invalid relative path and UUID')

        if relative_path:
            relative_path = relative_path.lstrip(os.path.sep)
            if relative_path not in self._metadata['embedded_docs']:
                return
            uuid = self._metadata['embedded_docs'][relative_path]

        # The UUID after current code line will be either the provided UUID or the one in metadata here
        is_current_doc: bool = False
        if self.__doc_provider:
            is_current_doc = self.__doc_provider.table.table_name == uuid

        with TqdmContext(f'Removing embedding data for {relative_path}...', 'Done'):
            if not is_current_doc:
                # Remove the document's table from DB
                tmp_provider: DocProviderBase = provider_type(self.path_db,
                                                              uuid,
                                                              doc_path=None,
                                                              re_dump=False)  # type: ignore
                tmp_provider.delete_table()
                # Remove the document's vector index
                tmp_vector_db: DocLibVectorDb = DocLibVectorDb(self.path_lib_data, uuid)  # type: ignore
                tmp_vector_db.delete_db()
            else:
                self.__doc_provider.delete_table()  # type: ignore
                self.__doc_provider = None
                self.__vector_db.delete_db()  # type: ignore
                self.__vector_db = None

        # Record info in metadata after finished deletion
        self._metadata['embedded_docs'].pop(relative_path, None)
        self.save_metadata()

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
