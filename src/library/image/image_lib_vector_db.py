import os
from functools import wraps

import numpy as np
from redis.commands.search.query import Query
from redis.commands.search.result import Result

from db.vector.mem_vector_db import InMemoryVectorDb
from db.vector.redis_client import BatchedPipeline
from db.vector.redis_vector_db import RedisVectorDb
from utils.exceptions.db_errors import VectorDbError


def ensure_vector_db_connected(func):
    """Decorator to ensure at least one vector DB is connected before calling the function
    """
    @wraps(func)
    def wrapper(self: 'ImageLibVectorDb', *args, **kwargs):
        if not self.redis_vector_db and not self.mem_vector_db:
            raise VectorDbError('Vector DB not connected')
        return func(self, *args, **kwargs)
    return wrapper


class ImageLibVectorDb:
    """It maintains a vector database on either Redis or in-memory for given image library
    """
    IDX_FILENAME = 'image_lib.idx'

    def __init__(self, use_redis: bool = False,
                 lib_uuid: str | None = None,
                 data_folder: str | None = None,
                 ignore_index_error: bool = False):
        # If use redis, UUID and namespace are mandatory
        if use_redis and not lib_uuid:
            raise VectorDbError('Library UUID is mandatory for using redis as vector DB')
        # If use in-memory DB, library path is mandatory
        if not use_redis and not data_folder:
            raise VectorDbError('Library path is mandatory for using in-memory vector DB')

        self.redis_vector_db: RedisVectorDb | None = None
        self.mem_vector_db: InMemoryVectorDb | None = None
        if use_redis:
            self.redis_vector_db = RedisVectorDb(namespace=lib_uuid, index_name=f'v_idx:{lib_uuid}')  # type: ignore
        else:
            self.mem_vector_db = InMemoryVectorDb(data_folder=data_folder,
                                                  index_filename=ImageLibVectorDb.IDX_FILENAME,
                                                  ignore_index_error=ignore_index_error)

    @ensure_vector_db_connected
    def initialize_index(self, vector_dimension: int):
        if self.redis_vector_db:
            self.redis_vector_db.initialize_index(vector_dimension)
        elif self.mem_vector_db:
            # Use flat index for in-memory vector DB, no training data provided
            self.mem_vector_db.initialize_index(vector_dimension, track_id=True)

    @ensure_vector_db_connected
    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        if self.redis_vector_db:
            return self.redis_vector_db.get_save_pipeline(batch_size)
        raise NotImplementedError('In-memory vector DB does not support batched pipeline')

    @ensure_vector_db_connected
    def add(self, uuid: str, embedding: list[float], pipeline: BatchedPipeline | None = None):
        if self.redis_vector_db:
            self.redis_vector_db.add(uuid, embedding, pipeline)
        elif self.mem_vector_db:
            self.mem_vector_db.add(uuid, embedding)

    @ensure_vector_db_connected
    def remove(self, uuid: str, pipeline: BatchedPipeline | None = None):
        if self.redis_vector_db:
            self.redis_vector_db.remove(uuid, pipeline)
        elif self.mem_vector_db:
            self.mem_vector_db.remove([uuid], ids=None)

    @ensure_vector_db_connected
    def remove_many(self, uuids: list[str]):
        if self.mem_vector_db:
            self.mem_vector_db.remove(uuids, ids=None)
        raise NotImplementedError('Redis vector DB does not support remove many, use batched pipeline to remove instead')

    @ensure_vector_db_connected
    def clean_all_data(self):
        if self.redis_vector_db:
            self.redis_vector_db.clean_all_data()
        elif self.mem_vector_db:
            self.mem_vector_db.clean_all_data()

    @ensure_vector_db_connected
    def delete_db(self):
        if self.redis_vector_db:
            self.redis_vector_db.delete_db()
        elif self.mem_vector_db:
            self.mem_vector_db.delete_db()

    @staticmethod
    def delete_mem_db_file(lib_path: str):
        """Delete the in-memory vector DB file
        """
        file_path: str = os.path.join(lib_path, ImageLibVectorDb.IDX_FILENAME)
        if os.path.isfile(file_path):
            os.remove(file_path)

    @ensure_vector_db_connected
    def persist(self):
        if self.redis_vector_db:
            self.redis_vector_db.persist()
        elif self.mem_vector_db:
            self.mem_vector_db.persist()

    @ensure_vector_db_connected
    def query(self, embedding: np.ndarray, top_k: int = 10, extra_params: dict | None = None) -> list:
        """Query the given embedding against the index for similar images
        """
        if embedding is None or not top_k or top_k <= 0:
            return list()

        if self.redis_vector_db:
            embedding_as_bytes: bytes = embedding.tobytes()
            param: dict = {"query_vector": embedding_as_bytes} if not extra_params else \
                {"query_vector": embedding_as_bytes} | extra_params
            query: Query = Query(f'(*)=>[KNN {top_k} @vector $query_vector AS vector_score]')\
                .sort_by("vector_score").return_fields("$").dialect(2)
            search_result: Result = self.redis_vector_db.get_search().search(query, param)  # type: ignore
            return search_result.docs
        elif self.mem_vector_db:
            return self.mem_vector_db.query(embedding, top_k)
        raise VectorDbError('Vector DB not connected')

    @ensure_vector_db_connected
    def db_is_empty(self) -> bool:
        """Check if the vector DB is empty
        - For redis, check if the namespace exists
        - For in-memory, check if the index file exists
        """
        if self.redis_vector_db:
            return not self.redis_vector_db.namespace_exists()
        elif self.mem_vector_db:
            return not self.mem_vector_db.index_exists()
        return True
