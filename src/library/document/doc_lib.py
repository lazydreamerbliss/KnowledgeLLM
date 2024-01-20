import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from sqlite3 import Connection
from uuid import uuid4

import numpy as np
import numpy.typing as npt
from tqdm import tqdm

from knowledge_base.document.doc_embedder import DocEmbedder
from library.document.doc_lib_vector_db import DocLibVectorDb
from library.document.doc_provider import DocProvider
from library.document.sql import DB_NAME, Record
from utils.tqdm_context import TqdmContext

"""
import numpy as np
import numpy.typing as npt
from sentence_transformers import CrossEncoder, SentenceTransformer
from faiss import IndexFlatL2, IndexIVFFlat  # Put faiss import AFTER sentence_transformers, strange SIGSEGV error otherwise on OSX
from tqdm import tqdm
"""


class DocLib:
    """Define a document library
    - A document library is a collection of many different documents such as novels, articles, chat history
    - Each document will have it's own document DB table for storing raw data in DB in a structured way
    - Each document will also have it's own vector DB for storing embeddings of each document
    """

    MANIFEST: str = 'manifest.json'

    # Model folder: ../../../local_models/...
    # "cross-encoder/ms-marco-MiniLM-L-12-v2": re-rank a list of texts by their semantic similarity (https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2)
    MODEL_FOLDER: str = f'{Path(__file__).parent.parent.parent}/local_models'
    transformer_path: str = f'shibing624/text2vec-base-chinese'
    # transformer_path: str = os.path.join(MODEL_FOLDER, 'shibing624--text2vec-base-chinese', '', '')
    cross_encoder_path: str = f'hfl/chinese-roberta-wwm-ext'
    # cross_encoder_path: str = os.path.join(MODEL_FOLDER, 'hfl--chinese-roberta-wwm-ext', '', '')

    def __init__(self,
                 embedder: DocEmbedder,
                 lib_path: str,
                 lib_name: str | None = None):
        """
        Args:
            lib_path (str): Path to the library
            lib_name (str | None, optional): Name to the library, mandatory for a new library. Defaults to None.
        """
        if not embedder:
            raise ValueError('Document embedder is empty')

        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise ValueError(f'Invalid lib path: {lib_path}')

        new_lib: bool = self.__is_new_lib(lib_path)
        if new_lib and not lib_name:
            raise ValueError('A library name must be provided for a new library')

        # Load manifest
        self.lib_path: str = lib_path
        with TqdmContext('Loading library manifest...', 'Loaded'):
            if new_lib:
                self.__lib_manifest: dict = self.__initialize_lib_manifest(lib_name)
            else:
                self.__lib_manifest: dict = self.__parse_lib_manifest()
        if not self.__lib_manifest:
            raise ValueError('Library manifest not initialized')

        self.db: Connection = sqlite3.connect(os.path.join(self.lib_path, DB_NAME))
        self.doc_provider: DocProvider | None = None
        self.vector_db: DocLibVectorDb | None = None
        self.embedder: DocEmbedder = embedder

    def __is_new_lib(self, lib_path: str) -> bool:
        """Check if the library is new
        - If DB file or manifest file is missing, then it is a new library even though vector DB might exist
        """
        return not (os.path.isfile(os.path.join(lib_path, DB_NAME))
                    and os.path.isfile(os.path.join(lib_path, DocLib.MANIFEST)))

    def __initialize_lib_manifest(self, lib_name: str | None) -> dict:
        """Initialize the manifest file for the library
        - Only called when the library is under a fresh initialization (manifest file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        if not lib_name:
            raise ValueError('A name must be provided for a new library')

        file_path: str = os.path.join(self.lib_path, DocLib.MANIFEST)
        if os.path.isfile(file_path):
            raise ValueError(f'Manifest file already exists: {file_path}')

        initial_manifest: dict = {
            'NOTE': 'DO NOT delete this file or modify it manually',
            'lib_name': lib_name,  # Name of the library, must be unique and it will be used as the prefix of the redis index
            'alias': lib_name,     # Name alias for the library, for display
            'uuid': str(uuid4()),
            'type': 'document',
            'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_scanned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'embedded_docs': dict(),  # List of embedded documents under the library
        }
        with open(file_path, 'w') as f:
            json.dump(initial_manifest, f)
        return initial_manifest

    def __update_lib_manifest(self):
        """Update the manifest file for the library
        """
        file_path: str = os.path.join(self.lib_path, DocLib.MANIFEST)
        if not os.path.isfile(file_path):
            raise ValueError(f'Manifest file missing: {file_path}')

        with open(file_path, 'w') as f:
            json.dump(self.__lib_manifest, f)

    def __parse_lib_manifest(self) -> dict:
        """Parse the manifest file of the library
        """
        file_path: str = os.path.join(self.lib_path, DocLib.MANIFEST)
        if not os.path.isfile(file_path):
            raise ValueError(f'Manifest file missing: {file_path}')

        content: dict | None = None
        with open(file_path, 'r') as f:
            content = json.load(f)
        if not content or not content.get('uuid') or not content.get('lib_name'):
            raise ValueError(f'Invalid manifest file: {file_path}')

        return content

    def initialize_doc(self, relative_path: str):
        """Initialize a document under the library
        """
        if not relative_path:
            raise ValueError('Invalid relative path')

        doc_path: str = os.path.join(self.lib_path, relative_path)
        if not os.path.isfile(doc_path):
            raise ValueError(f'Invalid doc path: {doc_path}')
        if relative_path in self.__lib_manifest['embedded_docs']:
            raise ValueError(f'Doc {relative_path} already initialized')

        # Create doc provider for this doc
        uuid: str = str(uuid4())
        self.doc_provider = DocProvider(self.db, uuid, doc_path, re_dump=True)

        # Do embedding, and create vector DB for this doc
        self.vector_db = DocLibVectorDb(self.lib_path, uuid)
        embeddings_list: list[npt.ArrayLike] = [self.embedder.embed_text(text) for text in
                                                tqdm(doc_provider.get_all_records(), desc='Embedding data', ascii=' |')]  # type: ignore
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

        # Record info in manifest
        self.__lib_manifest['embedded_docs'][relative_path] = uuid
        self.__update_lib_manifest()

    def switch_doc(self, relative_path: str):
        """Switch to another document under the library
        - Document library can only have one active document at a time
        - If target document is not in manifest, then this is an uninitialized document, call initialize_doc()
        - Otherwise load the document provider and vector DB for the target document directly
        """
        if not relative_path:
            raise ValueError('Invalid relative path')

        if relative_path not in self.__lib_manifest['embedded_docs']:
            self.initialize_doc(relative_path)
        else:
            with TqdmContext(f'Switching to doc {relative_path}, loading data...', 'Done'):
                uuid: str = self.__lib_manifest['embedded_docs'][relative_path]
                self.doc_provider = DocProvider(self.db, uuid)
                self.vector_db = DocLibVectorDb(self.lib_path, uuid)

    def remove_doc_embedding(self, relative_path: str):
        """Remove the embedding of a document under the library
        """
        if not relative_path:
            raise ValueError('Invalid relative path')

        if relative_path not in self.__lib_manifest['embedded_docs']:
            return

        # Remove the document's table from DB
        uuid: str = self.__lib_manifest['embedded_docs'][relative_path]
        self.doc_provider = DocProvider(self.db, uuid)
        self.doc_provider.delete_table()

        # Remove the document's vector index
        self.vector_db = DocLibVectorDb(self.lib_path, uuid)
        self.vector_db.delete_db()

        # Remove the document's record in manifest
        del self.__lib_manifest['embedded_docs'][relative_path]
        self.__update_lib_manifest()

    def __retrieve(self, text: str, top_k: int = 10, relative_path: str | None = None) -> list[Record]:
        """Get top_k most similar candidates under the given document (relative path)
        """
        if not text or top_k <= 0:
            return list()

        # If no provider/vector DB
        if not self.doc_provider or not self.vector_db:
            if not relative_path:
                raise ValueError('relative_path is mandatory when doc provider is empty')
            else:
                self.switch_doc(relative_path)

        query_embedding: npt.ArrayLike = self.embedder.embed_text(text)
        ids: list[int] = self.vector_db.query(np.asarray([query_embedding]), top_k)  # type: ignore
        res: list[Record] = list()
        for i in ids:
            # in-mem index's ID starts from 0 but DB's ID column starts from 1, so plus 1
            record: tuple | None = self.doc_provider.get_record_by_id(i + 1)  # type: ignore
            if record:
                res.append(Record(record))
        return res

    def __rerank(self, text: str, candidates: list[Record]) -> list[Record]:
        tqdm.write(f'Reranking {len(candidates)} candidates...')
        candidates_str: list[str] = [f'{r.text}' for r in candidates]
        scores: npt.ArrayLike = self.embedder.predict_similarity_batch(text, candidates_str)

        # Re-sort the ranking result
        # - np.argsort() returns the indices in ascending order, so here we use [::-1] to reverse it
        # - https://blog.csdn.net/maoersong/article/details/21875705
        sorted_ids: np.ndarray = np.argsort(scores)[::-1]

        # Reorder the candidates list by the ranking
        return [Record(candidates[i]) for i in sorted_ids]

    def query(self, query_text: str, top_k: int = 10, rerank: bool = False) -> list[Record]:
        tqdm.write(f'Q: {query_text}, get top {top_k} matches...')
        if rerank:
            candidates: list[Record] = self.__retrieve(query_text, top_k * 10)
            reranked: list[Record] = self.__rerank(query_text, candidates)
            return reranked[:top_k]

        return self.__retrieve(query_text, top_k)
