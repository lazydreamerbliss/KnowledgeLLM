import os
from functools import wraps

import numpy as np

from db.vector.mem_vector_db import InMemoryVectorDb
from db.vector.redis_client import BatchedPipeline
from utils.exceptions.db_errors import LibraryVectorDbError, VectorDbCoreError


def ensure_vector_db_connected(func):
    """Decorator to ensure at least one vector DB is connected before calling the function
    """
    @wraps(func)
    def wrapper(self: 'DocLibVectorDb', *args, **kwargs):
        if not self.mem_vector_db:
            raise LibraryVectorDbError('Vector DB not connected')
        return func(self, *args, **kwargs)
    return wrapper


class DocLibVectorDb:
    """It maintains a vector database on memory only
    """
    INDEX_FOLDER: str = '__index__'  # All index files are stored in this folder under library's data folder

    def __init__(self, data_folder: str, db_name: str):
        if not data_folder or not db_name:
            raise LibraryVectorDbError('Invalid input')

        idx_path: str = os.path.join(data_folder, self.INDEX_FOLDER)
        idx_file: str = f'{db_name}.idx'
        # No need to check if path and file are valid, InMemoryVectorDb will do it
        self.mem_vector_db: InMemoryVectorDb = InMemoryVectorDb(idx_path, idx_file)

    @ensure_vector_db_connected
    def initialize_index(self, vector_dimension: int, training_set: np.ndarray | None, dataset_size: int = -1):
        self.mem_vector_db.initialize_index(vector_dimension,
                                            training_set=training_set,
                                            training_set_uuid_list=None,  # No need to track ID for document library
                                            expected_dataset_size=dataset_size)

    @ensure_vector_db_connected
    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        raise NotImplementedError('In-memory vector DB does not support batched pipeline')

    @ensure_vector_db_connected
    def add(self, uuid: str | None, embedding: list[float]):
        self.mem_vector_db.add(uuid, embedding)

    @ensure_vector_db_connected
    def remove(self, uuid: str):
        self.mem_vector_db.remove([uuid], ids=None)

    @ensure_vector_db_connected
    def remove_many(self, uuids: list[str]):
        self.mem_vector_db.remove(uuids, ids=None)

    @ensure_vector_db_connected
    def clean_all_data(self):
        self.mem_vector_db.clean_all_data()

    @ensure_vector_db_connected
    def delete_db(self):
        self.mem_vector_db.delete_db()

    @ensure_vector_db_connected
    def persist(self):
        self.mem_vector_db.persist()

    @ensure_vector_db_connected
    def query(self, embedding: np.ndarray, top_k: int = 10, extra_params: dict | None = None) -> list:
        """Query the given embedding against the index for similar images
        """
        if embedding is None or not top_k or top_k <= 0:
            return list()

        try:
            return self.mem_vector_db.query(embedding, top_k)
        except VectorDbCoreError:
            raise LibraryVectorDbError(f'Index not found, current document needs to be re-embedded')
