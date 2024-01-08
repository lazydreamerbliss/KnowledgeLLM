import numpy as np
from faiss import IndexFlatL2, IndexIVFFlat
from redis import ResponseError
from redis.commands.search.document import Document
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.result import Result
from tqdm import tqdm

from image_knowledge.mem_vector_db import InMemoryVectorDbFlat
from image_knowledge.redis_client import BatchedPipeline, RedisClient
from image_knowledge.redis_vector_db import RedisVectorDb
from sqlite.sql_image_lib import DB_NAME


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

        self.redis_vector_db: RedisVectorDb = RedisVectorDb(namespace=lib_namespace, index_name=f'v_idx:{lib_uuid}')
        self.mem_vector_db: InMemoryVectorDbFlat = InMemoryVectorDbFlat(lib_path, ImageLibVectorDb.IDX_FILENAME)
        tqdm.write(f'Connected')

    def initialize_index(self, vector_dimension: int):
        self.redis_vector_db.initialize_index(vector_dimension)

    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        return self.redis_vector_db.get_save_pipeline(batch_size)

    def add(self, uuid: str, embeddings: list[float], pipeline: BatchedPipeline | None = None):
        self.redis_vector_db.add(uuid, embeddings, pipeline)

    def remove(self, uuid: str, pipeline: BatchedPipeline | None = None):
        self.redis_vector_db.remove(uuid, pipeline)

    def clean_all_data(self):
        self.redis_vector_db.clean_all_data()

    def delete_db(self):
        self.redis_vector_db.delete_db()

    def persist(self):
        self.redis_vector_db.persist()

    def query(self, embeddings: bytes, top_k: int = 10, extra_params: dict | None = None) -> list[Document]:
        """Query the given embeddings against the index for similar images
        """
        if not embeddings or not top_k or top_k <= 0:
            return list()

        param: dict = {"query_vector": embeddings} if not extra_params else \
                      {"query_vector": embeddings} | extra_params
        query: Query = Query(f'(*)=>[KNN {top_k} @vector $query_vector AS vector_score]')\
            .sort_by("vector_score").return_fields("$").dialect(2)
        search_result: Result = self.redis_vector_db.get_search().search(query, param)  # type: ignore
        return search_result.docs
