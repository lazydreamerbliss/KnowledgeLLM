import os
import pickle

import faiss
import numpy as np
from faiss import IndexFlatL2, IndexIDMap2, IndexIVFFlat
from redis import ResponseError
from redis.commands.search.document import Document
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.result import Result
from tqdm import tqdm

from image_knowledge.redis_client import BatchedPipeline, RedisClient
from sqlite.sql_image_lib import DB_NAME


class InMemoryVectorDbFlat:
    """It maintains a vector database (FLAT) in-memory for given image library
    - It needs to persist the index to disk for reuse
    """
    IDX_FILENAME: str = 'mem_db.idx'

    def __init__(self, db_path, index_filename: str | None = None):
        if not db_path:
            raise ValueError('A path is mandatory for using in-memory vector DB')

        tqdm.write(f'Loading index from disk...', end=' ')
        db_path = os.path.expanduser(db_path)
        if not os.path.isdir(db_path):
            raise ValueError('Path does not exist')

        index_filename = index_filename or InMemoryVectorDbFlat.IDX_FILENAME
        index_file_path: str = os.path.join(db_path, index_filename)
        self.mem_index_path: str = index_file_path
        self.mem_index: IndexFlatL2 | None = None

        # self.mem_index: IndexIVFFlat | None = None
        if os.path.isfile(index_file_path):
            try:
                obj = pickle.load(open(index_file_path, 'rb'))
                self.mem_index = obj['index']
                tqdm.write(f'Loaded index from {index_file_path}')
            except:
                raise ValueError('Corrupted index file')
        else:
            tqdm.write(f'Index file {index_file_path} not found, this is a new database')

    def initialize_index(self, vector_dimension: int):
        self.mem_index = IndexFlatL2(vector_dimension)

    def add(self, uuid: str, embeddings: np.ndarray):
        """Save given embedding to vector DB
        """
        if not self.mem_index:
            raise ValueError('Index not initialized')

        self.mem_index.add(embeddings)  # type: ignore

    def remove(self, uuid: str):
        """Remove given embedding from vector DB
        """
        self.mem_index.remove_ids()

    def clean_all_data(self):
        """Fully clean the library data for reset
        - Remove all keys in vector DB within the namespace
        """
        pass

    def delete_db(self):
        """Fully drop and delete the library data
        1. Remove all keys in vector DB
        2. Delete the index
        """
        pass

    def persist(self):
        """Persist index to disk
        """
        pickle.dump({
            'id_mapping_index': self.id_mapping_index,
            'index': self.mem_index
        }, open(self.mem_index_path, 'wb'))

    def query(self, embeddings: bytes, top_k: int = 10, extra_params: dict | None = None) -> list[Document]:
        """Query the given embeddings against the index for similar images
        """
        pass
