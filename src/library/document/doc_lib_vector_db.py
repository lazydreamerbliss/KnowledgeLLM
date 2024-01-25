import os
from functools import wraps

import numpy as np

from db.vector.mem_vector_db import InMemoryVectorDb
from db.vector.redis_client import BatchedPipeline


def ensure_vector_db_connected(func):
    """Decorator to ensure at least one vector DB is connected before calling the function
    """
    @wraps(func)
    def wrapper(self: 'DocLibVectorDb', *args, **kwargs):
        if not self.mem_vector_db:
            raise ValueError('Vector DB not connected')
        return func(self, *args, **kwargs)
    return wrapper


class DocLibVectorDb:
    """It maintains a vector database on memory only
    """
    INDEX_FOLDER: str = '__index__'  # All index files are stored in this folder under a library

    def __init__(self, data_folder: str, db_name: str):
        if not data_folder or not db_name:
            raise ValueError('Invalid input')

        idx_path: str = os.path.join(data_folder, self.INDEX_FOLDER)
        idx_file: str = f'{db_name}.idx'
        # No need to check if path and file are valid, InMemoryVectorDb will do it
        self.mem_vector_db: InMemoryVectorDb = InMemoryVectorDb(idx_path, idx_file)

    @ensure_vector_db_connected
    def initialize_index(self, vector_dimension: int, training_set: np.ndarray, dataset_size: int):
        if training_set is None:
            raise ValueError('training_set is None')

        # Use IVF index for in-memory vector DB
        self.mem_vector_db.initialize_index(vector_dimension, training_set=training_set,
                                            training_set_uuid=None, expected_dataset_size=dataset_size)

    @ensure_vector_db_connected
    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        raise NotImplementedError('In-memory vector DB does not support batched pipeline')

    @ensure_vector_db_connected
    def add(self, uuid: str, embeddings: list[float], pipeline: BatchedPipeline | None = None):
        self.mem_vector_db.add(uuid, embeddings)

    @ensure_vector_db_connected
    def remove(self, uuid: str, pipeline: BatchedPipeline | None = None):
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

    @staticmethod
    def delete_mem_db_folder(lib_path: str):
        """Delete the in-memory vector DB folder
        """
        folder_path: str = os.path.join(lib_path, DocLibVectorDb.INDEX_FOLDER)
        if os.path.isdir(folder_path):
            os.rmdir(folder_path)

    @ensure_vector_db_connected
    def persist(self):
        self.mem_vector_db.persist()

    @ensure_vector_db_connected
    def query(self, embeddings: np.ndarray, top_k: int = 10, extra_params: dict | None = None) -> list:
        """Query the given embeddings against the index for similar images
        """
        if embeddings is None or not top_k or top_k <= 0:
            return list()

        return self.mem_vector_db.query(embeddings, top_k)

    @ensure_vector_db_connected
    def db_is_empty(self) -> bool:
        """Check if the vector DB is empty
        - For in-memory, check if the index file exists
        """
        if self.mem_vector_db:
            return not self.mem_vector_db.index_exists()
        return True
