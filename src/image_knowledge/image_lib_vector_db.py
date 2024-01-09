from functools import wraps

import numpy as np
from redis.commands.search.document import Document
from redis.commands.search.query import Query
from redis.commands.search.result import Result

from vector_db.mem_vector_db import InMemoryVectorDb
from vector_db.redis_client import BatchedPipeline
from vector_db.redis_vector_db import RedisVectorDb


def ensure_vector_db_connected(func):
    """Decorator to ensure at least one vector DB is connected before calling the function
    """
    @wraps(func)
    def wrapper(self: 'ImageLibVectorDb', *args, **kwargs):
        if not self.redis_vector_db and not self.mem_vector_db:
            raise ValueError('Vector DB not connected')
        return func(self, *args, **kwargs)
    return wrapper


class ImageLibVectorDb:
    """It maintains a vector database on either Redis or in-memory for given image library
    """
    IDX_FILENAME = 'image_lib.idx'

    def __init__(self, use_redis: bool = True,
                 lib_uuid: str | None = None,
                 lib_namespace: str | None = None,
                 lib_path: str | None = None):  # Required for in-memory vector DB
        # if use_redis:
        if use_redis and not lib_uuid or not lib_namespace:
            raise ValueError('Namespace and library UUID are mandatory for using redis as vector DB')
        if not use_redis and not lib_path:
            raise ValueError('Library path is mandatory for using in-memory vector DB')

        self.redis_vector_db: RedisVectorDb | None = None
        self.mem_vector_db: InMemoryVectorDb | None = None
        if use_redis:
            self.redis_vector_db = RedisVectorDb(namespace=lib_namespace, index_name=f'v_idx:{lib_uuid}')
        else:
            self.mem_vector_db = InMemoryVectorDb(lib_path, ImageLibVectorDb.IDX_FILENAME)

    @ensure_vector_db_connected
    def initialize_index(self, vector_dimension: int):
        if self.redis_vector_db:
            self.redis_vector_db.initialize_index(vector_dimension)
        elif self.mem_vector_db:
            # Use flat index for in-memory vector DB, no training data provided
            self.mem_vector_db.initialize_index(vector_dimension)

    @ensure_vector_db_connected
    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        if self.redis_vector_db:
            return self.redis_vector_db.get_save_pipeline(batch_size)
        raise NotImplementedError('In-memory vector DB does not support batched pipeline')

    @ensure_vector_db_connected
    def add(self, uuid: str, embeddings: list[float], pipeline: BatchedPipeline | None = None):
        if self.redis_vector_db:
            self.redis_vector_db.add(uuid, embeddings, pipeline)
        elif self.mem_vector_db:
            self.mem_vector_db.add(uuid, embeddings)

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

    @ensure_vector_db_connected
    def persist(self):
        if self.redis_vector_db:
            self.redis_vector_db.persist()
        elif self.mem_vector_db:
            self.mem_vector_db.persist()

    @ensure_vector_db_connected
    def query(self, embeddings: np.ndarray, top_k: int = 10, extra_params: dict | None = None) -> list:
        """Query the given embeddings against the index for similar images
        """
        if embeddings is None or not top_k or top_k <= 0:
            return list()

        if self.redis_vector_db:
            embeddings_as_bytes: bytes = embeddings.tobytes()
            param: dict = {"query_vector": embeddings_as_bytes} if not extra_params else \
                {"query_vector": embeddings_as_bytes} | extra_params
            query: Query = Query(f'(*)=>[KNN {top_k} @vector $query_vector AS vector_score]')\
                .sort_by("vector_score").return_fields("$").dialect(2)
            search_result: Result = self.redis_vector_db.get_search().search(query, param)  # type: ignore
            return search_result.docs
        elif self.mem_vector_db:
            return self.mem_vector_db.query(embeddings, top_k)
        raise ValueError('Vector DB not connected')
