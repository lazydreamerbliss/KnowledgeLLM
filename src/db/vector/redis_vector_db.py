from redis import ResponseError
from redis.commands.search import Search
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from db.vector.redis_client import BatchedPipeline, RedisClient
from utils.tqdm_context import TqdmContext


class RedisVectorDb:
    """It maintains a vector database on Redis
    """

    def __init__(self, namespace: str, index_name: str):
        if not namespace or not index_name:
            raise ValueError('Namespace and index name are mandatory for using redis as vector DB')

        with TqdmContext('Connecting to Redis vector DB...', 'Connected'):
            self.redis: RedisClient = RedisClient()
            self.namespace: str = namespace
            self.index_name: str = index_name

    def initialize_index(self, vector_dimension: int):
        """Create index for current image library only

        Raises:
            ValueError: _description_
            e: _description_

        Returns:
            bool: _description_
        """
        # Define redis index schema
        # - https://redis.io/docs/get-started/vector-database/
        schema = (
            VectorField(
                "$",  # The path to the vector field in the JSON object
                # Specifies the indexing method, which is either a FLAT or a hierarchical navigable small world graph (HNSW)
                "FLAT",
                {
                    "TYPE": "FLOAT32",  # Sets the type of a vector component, in this case a 32-bit floating point number
                    "DIM": vector_dimension,  # The length or dimension of the embeddings
                    "DISTANCE_METRIC": "COSINE",  # Distance function used to compare vectors: https://en.wikipedia.org/wiki/Cosine_similarity
                },
                as_name="vector",
            ),
        )

        # Define the key-space for the index
        # - Each library has its own index, so `lib_name` (as key prefix) should be unique across all libraries
        definition: IndexDefinition = IndexDefinition(prefix=[f'{self.namespace}:'], index_type=IndexType.JSON)

        # Create the index
        try:
            self.redis.client().ft(self.index_name).create_index(fields=schema, definition=definition)
        except ResponseError as e:
            if e.args[0] == 'Index already exists':
                return
            raise e

    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        """Get a batched save pipeline for vector DB
        """
        return self.redis.batched_pipeline(batch_size)

    def add(self, uuid: str, embeddings: list[float], pipeline: BatchedPipeline | None = None):
        """Save given embedding to vector DB
        """
        if pipeline:
            pipeline.json_set(f'{self.namespace}:{uuid}', embeddings)
        else:
            self.redis.json_set(f'{self.namespace}:{uuid}', embeddings)

    def remove(self, uuid: str, pipeline: BatchedPipeline | None = None):
        """Remove given embedding from vector DB
        """
        if pipeline:
            pipeline.json_delete(f'{self.namespace}:{uuid}')
        else:
            self.redis.delete(f'{self.namespace}:{uuid}')

    def clean_all_data(self):
        """Fully clean the library data for reset
        - Remove all keys in vector DB within the namespace
        """
        self.redis.delete_by_prefix(f'{self.namespace}:')
        self.redis.snapshot()

    def delete_db(self):
        """Fully drop and delete the library data
        1. Remove all keys in vector DB
        2. Delete the index
        """
        self.clean_all_data()
        self.redis.client().ft(self.index_name).dropindex()
        self.redis.save()

    def persist(self):
        """Persist index to disk
        """
        self.redis.save()

    def get_search(self) -> Search:
        return self.redis.client().ft(self.index_name)

    def namespace_exists(self) -> bool:
        """Check if the namespace exists
        - It tries to get one key with the namespace prefix
        """
        return self.redis.get_one_with_prefix(f'{self.namespace}:') is not None
