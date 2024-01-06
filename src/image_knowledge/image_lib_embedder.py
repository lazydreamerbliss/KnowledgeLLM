from datetime import datetime
from pathlib import Path
from uuid import uuid4

import faiss
import numpy as np
import torch
from faiss import IndexFlatL2, IndexIVFFlat
from PIL import Image
from redis import ResponseError
from redis.commands.search.document import Document
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.result import Result
from torch import FloatTensor, Tensor
from transformers import (ChineseCLIPModel, ChineseCLIPProcessor, CLIPModel,
                          CLIPProcessor, CLIPTokenizer)
from transformers.models.clip.modeling_clip import CLIPOutput
from transformers.tokenization_utils_base import BatchEncoding

from redis_client import BatchedPipeline, RedisClient
from sqlite.sql_image_lib import DB_NAME


def ensure_redis(func):
    def wrapper(self: ImageLibEmbedder, *args, **kwargs):
        if self.redis is None or not self.redis.connected or not self.index_name:
            raise ValueError("Redis is not connected")
        return func(self, *args, **kwargs)
    return wrapper


class ImageLibEmbedder:
    """It maintains a vector database on either Redis or in-memory for given image library, and provides methods to
    the functionality of embedding images and querying similar images
    """
    # Model folder: ../../../local_models/...
    MODEL_FOLDER: str = f'{Path(__file__).parent.parent.parent}/local_models'
    IDX_FILENAME: str = 'image_lib.idx'
    model_path: str = f'{MODEL_FOLDER}/openai--clip-vit-base-patch16/snapshots/57c216476eefef5ab752ec549e440a49ae4ae5f3'
    model_path_cn: str = f'{MODEL_FOLDER}/OFA-Sys--chinese-clip-vit-base-patch16/snapshots/36e679e65c2a2fead755ae21162091293ad37834'

    def __init__(self, use_redis: bool = True,
                 lib_uuid: str | None = None,
                 lib_namespace: str | None = None,
                 lib_path: str | None = None):  # Required for in-memory vector DB
        self.redis: RedisClient | None = None
        self.namespace: str | None = None
        self.index_name: str | None = None

        self.mem_index: IndexIVFFlat | None = None
        self.mem_embeddings: np.ndarray | None = None
        self.mem_index_path: str | None = None

        # if use_redis:
        if not lib_uuid or not lib_namespace:
            raise ValueError('Namespace and library UUID are mandatory for using redis as vector DB')

        # For redis, connect directly
        self.redis = RedisClient(host="localhost", port=6379, password="test123")
        if not self.redis.connected:
            raise ValueError('Redis not connected')
        self.namespace = lib_namespace
        self.index_name = f'v_idx:{lib_uuid}'
        # else:
        #     if not lib_path:
        #         raise ValueError('Path to library is mandatory for using in-memory vector DB')

        #     # For in-memory, load index from file system
        #     lib_path = os.path.expanduser(lib_path)
        #     index_file_path: str = os.path.join(lib_path, ImageLibEmbedder.IDX_FILENAME)
        #     if not os.path.isfile(index_file_path):
        #         raise ValueError('Index file not found')
        #     try:
        #         self.mem_index_path = index_file_path
        #         tqdm.write(f'Loading index for library from disk...')
        #         self.mem_index = faiss.read_index(self.mem_index_path)
        #     except:
        #         raise ValueError('Corrupted index file')

        # Use CLIP to embed images
        # - https://huggingface.co/docs/transformers/model_doc/clip
        self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(ImageLibEmbedder.model_path)
        self.model: CLIPModel = CLIPModel.from_pretrained(ImageLibEmbedder.model_path)  # type: ignore
        self.tokenizer: CLIPTokenizer = CLIPTokenizer.from_pretrained(ImageLibEmbedder.model_path)
        self.model_cn: ChineseCLIPModel = ChineseCLIPModel.from_pretrained(
            ImageLibEmbedder.model_path_cn)  # type: ignore
        self.processor_cn: ChineseCLIPProcessor = ChineseCLIPProcessor.from_pretrained(
            ImageLibEmbedder.model_path_cn)

    def __embed_image(self, img: Image.Image) -> np.ndarray:
        """Embed an image

        Args:
            img (Image.Image): _description_
            relative_path (str | None, optional): Logging only. Defaults to None.

        Returns:
            np.ndarray: _description_
        """
        # The batch size is set to 1, so the first element of the output is the embedding of the image
        # - https://huggingface.co/transformers/model_doc/clip.html#clipmodel
        batch_size: int = 1

        # Use processor to build input data for CLIP model, and use model to get image features
        clip_input: BatchEncoding = self.processor(images=img, return_tensors="pt", padding=True)
        image_features: Tensor = self.model.get_image_features(clip_input.get('pixel_values'))[batch_size-1]
        return image_features.numpy().astype(np.float32)

    def initialize_vector_db_index_redis(self, vector_dimension: int):
        """Create index for current image library only

        Raises:
            ValueError: _description_
            e: _description_

        Returns:
            bool: _description_
        """
        if not self.redis or not self.redis.connected or not self.index_name:
            raise ValueError('Redis not connected')

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
            self.redis.client.ft(self.index_name).create_index(fields=schema, definition=definition)
        except ResponseError as e:
            if e.args[0] == 'Index already exists':
                return
            raise e

    def __initialize_vector_db_index_mem(self, vector_dimension: int):
        # `cell_count` is the number of K-means centroids to use for clustering
        cluster_count: int = 100
        quantizer: IndexFlatL2 = IndexFlatL2(vector_dimension)
        self.mem_index = IndexIVFFlat(quantizer, vector_dimension, cluster_count)

    def embed_image(self, img: Image.Image, use_grad: bool = False) -> np.ndarray:
        """Embed the given image
        - About use_grad(): https://datascience.stackexchange.com/questions/32651/what-is-the-use-of-torch-no-grad-in-pytorch
        """
        if not use_grad:
            with torch.no_grad():
                return self.__embed_image(img)
        else:
            return self.__embed_image(img)

    def embed_image_as_list(self, img: Image.Image, use_grad: bool = False) -> list[float]:
        """Embed an image and return vector as list
        """
        embeddings: np.ndarray = self.embed_image(img, use_grad)
        return embeddings.tolist()

    def embed_image_as_bytes(self, img: Image.Image, use_grad: bool = False) -> bytes:
        """Embed an image and return vector as bytes
        """
        embeddings: np.ndarray = self.embed_image(img, use_grad)
        return embeddings.tobytes()

    def embed_text(self, text: str, use_grad: bool = False) -> bytes:
        """Embed the given text
        """
        inputs: BatchEncoding = self.tokenize_text(text)
        text_features: FloatTensor = self.model.get_text_features(**inputs)  # type: ignore

        if not use_grad:
            with torch.no_grad():
                return text_features.numpy().astype(np.float32).tobytes()
        return text_features.numpy().astype(np.float32).tobytes()

    def tokenize_text(self, text: str) -> BatchEncoding:
        """Tokenize the given text
        """
        return self.processor(text, return_tensors="pt", padding=True)

    def get_save_pipeline(self, batch_size: int = 1000) -> BatchedPipeline | None:
        if not self.redis or not self.redis.connected:
            raise ValueError('Redis not connected')

        return self.redis.batched_pipeline(batch_size)

    def save_to_vector_db(self, uuid: str, embeddings: list[float], pipeline: BatchedPipeline | None = None):
        """Save given embedding to vector DB (either Redis or in-memory)
        """
        if not self.redis or not self.redis.connected:
            raise ValueError('Redis not connected')

        # IMPORTANT: key is lib_name + uuid, which means all keys in redis are grouped by lib_name
        if pipeline:
            pipeline.json_set(f'{self.namespace}:{uuid}', embeddings)
        else:
            self.redis.json_set(f'{self.namespace}:{uuid}', embeddings)

    def remove_from_vector_db(self, uuid: str, pipeline: BatchedPipeline | None = None):
        """Remove given embedding from vector DB (either Redis or in-memory)
        """
        if not self.redis or not self.redis.connected:
            raise ValueError('Redis not connected')

        if pipeline:
            pipeline.json_delete(f'{self.namespace}:{uuid}')
        else:
            self.redis.delete(f'{self.namespace}:{uuid}')

    def clean_vector_db(self):
        """Fully clean the library data for reset
        - Remove all keys in vector DB
        """
        if not self.redis or not self.redis.connected:
            raise ValueError('Redis not connected')

        self.redis.delete_by_prefix(f'{self.namespace}:')
        self.redis.snapshot()

    def delete_vector_db(self):
        """Fully delete the library data
        1. Remove all keys in vector DB
        2. Delete the index
        """
        if not self.redis or not self.redis.connected or not self.index_name:
            raise ValueError('Redis not connected')

        self.clean_vector_db()
        self.redis.client.ft(self.index_name).dropindex()
        self.redis.save()

    def persist(self):
        """Persist index to disk
        """
        if not self.redis or not self.redis.connected:
            raise ValueError('Redis not connected')

        self.redis.save()

    def query(self, embeddings: bytes, top_k: int = 10, extra_params: dict | None = None) -> list[Document]:
        """Query the given embeddings against the index for similar images
        """
        if not self.redis or not self.redis.connected or not self.index_name:
            raise ValueError('Redis not connected')

        if not embeddings or not top_k or top_k <= 0:
            return list()

        param: dict = {"query_vector": embeddings} if not extra_params else \
                      {"query_vector": embeddings} | extra_params
        query: Query = Query(f'(*)=>[KNN {top_k} @vector $query_vector AS vector_score]')\
            .sort_by("vector_score").return_fields("$").dialect(2)
        search_result: Result = self.redis.client.ft(self.index_name).search(query, param)  # type: ignore
        return search_result.docs

    def similarity_query(self, text_list: list[str], img: Image.Image) -> Tensor:
        """Query the given text and image against the CLIP model for similarity
        """
        # Use processor to build input data for CLIP model, with both text and image functionalities
        clip_input: BatchEncoding = self.processor(text=text_list, images=img, return_tensors="pt", padding=True)
        # Unpack the batched encoding and feed it to the CLIP model directly to process both text and image
        image_features: CLIPOutput = self.model(**clip_input)
        # Get the logits from the CLIP model
        return image_features.logits_per_image.softmax(dim=1)
