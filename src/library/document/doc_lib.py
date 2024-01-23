import os
from typing import Generic, Type, TypeVar
from uuid import uuid4

import numpy as np
import numpy.typing as npt
from tqdm import tqdm

from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.document.provider import DocProviderBase
from library.document.doc_lib_vector_db import DocLibVectorDb
from library.document.sql import DB_NAME
from library.lib_base import *
from utils.tqdm_context import TqdmContext

"""
import numpy as np
import numpy.typing as npt
from sentence_transformers import CrossEncoder, SentenceTransformer
from faiss import IndexFlatL2, IndexIVFFlat  # Put faiss import AFTER sentence_transformers, strange SIGSEGV error otherwise on OSX
from tqdm import tqdm
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
                 uuid: str):
        """
        Args:
            lib_path (str): Path to the library
            uuid (str): UUID of the library
        """
        if not uuid:
            raise ValueError('Invalid UUID')
        super().__init__(lib_path)

        # Load manifest
        with TqdmContext('Loading library manifest...', 'Loaded'):
            if not self.manifest_file_exists():
                initial_manifest: dict = BASIC_MANIFEST | {
                    'uuid': uuid,
                    'embedded_docs': dict(),  # List of embedded documents under the library
                    'unfinished_docs': dict(),  # List of documents that are not finished embedding yet
                }
                self.initialize_lib_manifest(initial_manifest)
            else:
                self.parse_lib_manifest(uuid)
        if not self.manifest or not self.uuid:
            raise ValueError('Library manifest not initialized')

        self.path_db: str = os.path.join(self.path_lib, DB_NAME)
        self.doc_provider: D | None = None
        self.vector_db: DocLibVectorDb | None = None
        self.embedder: DocEmbedder | None = None

    def lib_is_ready(self) -> bool:
        if not self.manifest_file_exists():
            return False
        if not self.embedder:
            return False
        if not self.doc_provider:
            return False
        return True

    def set_embedder(self, embedder: DocEmbedder):
        self.embedder = embedder

    def __initialize_doc(self, relative_path: str, provider_type: Type[D]):
        """Initialize a document under the library
        """
        if not relative_path:
            raise ValueError('Invalid relative path')

        relative_path = relative_path.lstrip(os.path.sep)
        if relative_path in self.manifest['embedded_docs']:
            self.switch_doc(relative_path, provider_type)
            return

        doc_path: str = os.path.join(self.path_lib, relative_path)
        if not os.path.isfile(doc_path):
            raise ValueError(f'Invalid doc path: {doc_path}')

        # Pre-check if given doc is in unfinished list, clean up leftover if any
        if relative_path in self.manifest['unfinished_docs']:
            old_uuid: str = self.manifest['unfinished_docs'][relative_path]
            self.remove_doc_embedding(None, old_uuid, provider_type)
            self.manifest['unfinished_docs'].pop(relative_path, None)
            self.update_lib_manifest()

        # Record info in manifest before embedding
        uuid: str = str(uuid4())
        self.manifest['unfinished_docs'][relative_path] = uuid
        self.update_lib_manifest()

        # Create doc provider for this doc
        self.doc_provider = provider_type(self.path_db,
                                          uuid,
                                          doc_path=doc_path,
                                          re_dump=False)  # type: ignore

        # Do embedding, and create vector DB for this doc
        self.vector_db = DocLibVectorDb(self.path_lib, uuid)
        embeddings_list: list[npt.ArrayLike] = [self.embedder.embed_text(self.doc_provider.EMBED_LAMBDA(t)) for t in  # type: ignore
                                                tqdm(self.doc_provider.get_all_records(), desc='Embedding data', ascii=' |')]
        embeddings: np.ndarray = np.asarray(embeddings_list)

        # "ndarray.shape" is used to get the dimension of a matrix, the type is tuple
        # The length of the tuple is the dimension of the array, and each element represents the length of the array in that dimension:
        # - For a 2D matrix, the shape is a tuple of length 2: shape[0] is the number of rows, shape[1] is the number of columns
        # - For example: self.embeddings.shape is (1232, 76), which means there are 1232 texts, and each text is converted to a 76-dimension vector
        text_count: int = embeddings.shape[0]
        dimension: int = embeddings.shape[1]
        with TqdmContext(f'Building index with dimension {dimension}...', 'Done'):
            self.vector_db.initialize_index(dimension, training_set=embeddings, dataset_size=text_count)
            self.vector_db.persist()

        # Record info in manifest after finished embedding
        self.manifest['unfinished_docs'].pop(relative_path, None)
        self.manifest['embedded_docs'][relative_path] = uuid
        self.update_lib_manifest()

    def switch_doc(self, relative_path: str, provider_type: Type[D]):
        """Switch to another document under the library
        - If target document is not in manifest, then this is an uninitialized document, call initialize_doc()
        - Otherwise load the document provider and vector DB for the target document directly
        - Target document's provider type is mandatory
        """
        if not relative_path:
            raise ValueError('Invalid relative path')

        relative_path = relative_path.lstrip(os.path.sep)
        if relative_path not in self.manifest['embedded_docs']:
            self.__initialize_doc(relative_path, provider_type)
            return

        with TqdmContext(f'Switching to doc {relative_path}, loading data...', 'Done'):
            uuid: str = self.manifest['embedded_docs'][relative_path]
            self.doc_provider = provider_type(self.path_db,
                                              uuid,
                                              doc_path=None,
                                              re_dump=False)  # type: ignore
            self.vector_db = DocLibVectorDb(self.path_lib, uuid)

    def remove_doc_embedding(self, relative_path: str | None, uuid: str | None, provider_type: Type[D]):
        """Remove the embedding of a document under the library
        1. Delete the document's table from DB
        2. Delete the document's vector index

        If relative_path is None, then uuid must be provided, and vice versa
        If both are provided, then relative_path will be used
        """
        if not relative_path and not uuid:
            raise ValueError('Invalid relative path and UUID')

        if relative_path:
            relative_path = relative_path.lstrip(os.path.sep)
            if relative_path not in self.manifest['embedded_docs']:
                return
            uuid = self.manifest['embedded_docs'][relative_path]

        # The UUID after current code line will be either the provided UUID or the one in manifest here
        is_current_doc: bool = False
        if self.doc_provider:
            is_current_doc = self.doc_provider.table.table_name == uuid

        with TqdmContext(f'Removing embedding data for {relative_path}...', 'Done'):
            if not is_current_doc:
                # Remove the document's table from DB
                tmp_provider: DocProviderBase = provider_type(self.path_db,
                                                              uuid,
                                                              doc_path=None,
                                                              re_dump=False)  # type: ignore
                tmp_provider.delete_table()
                # Remove the document's vector index
                tmp_vector_db: DocLibVectorDb = DocLibVectorDb(self.path_lib, uuid)  # type: ignore
                tmp_vector_db.delete_db()
            else:
                self.doc_provider.delete_table()  # type: ignore
                self.doc_provider = None
                self.vector_db.delete_db()  # type: ignore
                self.vector_db = None

        # Record info in manifest after finished deletion
        self.manifest['embedded_docs'].pop(relative_path, None)
        self.update_lib_manifest()

    def delete_lib(self):
        """Delete the doc library, it purges all library data
        1. Delete vector index folder
        2. Delete DB file
        3. Delete manifest file
        """
        DocLibVectorDb.delete_mem_db_folder(self.path_lib)
        DocProviderBase.delete_db_file(self.path_db)

        self.path_manifest
        if os.path.isfile(self.path_manifest):
            os.remove(self.path_manifest)

    def __retrieve(self, text: str, top_k: int = 10) -> list[tuple]:
        """Get top_k most similar candidates under the given document (relative path)
        """

        if not text or top_k <= 0:
            return list()

        # If no provider/vector DB
        if not self.doc_provider or not self.vector_db:
            raise ValueError('No active document, please switch to a document first')

        query_embedding: npt.ArrayLike = self.embedder.embed_text(text)  # type: ignore
        ids: list[np.int64] = self.vector_db.query(np.asarray([query_embedding]), top_k)  # type: ignore
        res: list[tuple] = list()

        for i64 in ids:
            # If number of candidates is lesser than top_k, then the rest IDs are all -1
            i: int = int(i64)
            if i == -1:
                break

            # in-mem index's ID starts from 0 but DB's ID column starts from 1, plus 1
            record: tuple | None = self.doc_provider.get_record_by_id(i + 1)
            if record:
                res.append(record)
        return res

    def __rerank(self, text: str, candidates: list[tuple]) -> list[tuple]:
        if not self.doc_provider:
            raise ValueError('No active document, please switch to a document first')

        tqdm.write(f'Reranking {len(candidates)} candidates...')
        candidates_str: list[str] = [self.doc_provider.RERANK_LAMBDA(c) for c in candidates]  # type: ignore
        scores: npt.ArrayLike = self.embedder.predict_similarity_batch(text, candidates_str)  # type: ignore

        # Re-sort the ranking result
        # - np.argsort() returns the indices in ascending order, so here we use [::-1] to reverse it
        # - https://blog.csdn.net/maoersong/article/details/21875705
        sorted_ids: np.ndarray = np.argsort(scores)[::-1]

        # Reorder the candidates list by the ranking
        return [candidates[i] for i in sorted_ids]

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
