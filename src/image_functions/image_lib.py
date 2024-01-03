import json
import os
import time
from uuid import uuid4

import numpy as np
import torch
from PIL import Image
from redis import ResponseError
from redis.commands.search.document import Document
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.result import Result
from torch import FloatTensor, Tensor
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor, CLIPTokenizer
from transformers.models.clip.modeling_clip import CLIPOutput
from transformers.tokenization_utils_base import BatchEncoding

from redis_client import RedisClient
from sqlite.image_lib_table import ImageLibTable
from sqlite.image_lib_table_sql import DB_NAME


class ImageLib:
    model_name: str = "openai/clip-vit-base-patch16"

    def __init__(self, lib_path: str, lib_name: str | None = None, force_init: bool = False):
        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise ValueError(f'Invalid lib path: {lib_path}')

        new_lib: bool = self.__is_new_lib(lib_path)
        if new_lib and not lib_name:
            raise ValueError('A library name must be provided for a new image library')

        # Load manifest
        self.lib_path: str = lib_path
        if new_lib:
            tqdm.write(f'Initialize library manifest')
            self.lib_manifest: dict = self.__initialize_lib_manifest(lib_name)
        else:
            tqdm.write(f'Load library manifest')
            self.lib_manifest: dict = self.__parse_lib_manifest()

        # Connect to DB and Redis
        self.table: ImageLibTable = ImageLibTable(lib_path)
        self.redis: RedisClient = RedisClient(host="localhost", port=6379, password="test123")
        if not self.redis.connected:
            raise ValueError('Redis not connected')
        self.namespace = self.lib_manifest["lib_name"]
        self.index_name = f'v_idx:{self.lib_manifest["uuid"]}'

        # Use CLIP to embed images
        # - https://huggingface.co/docs/transformers/model_doc/clip
        self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(ImageLib.model_name)
        self.model: CLIPModel = CLIPModel.from_pretrained(ImageLib.model_name)  # type: ignore
        self.tokenizer: CLIPTokenizer = CLIPTokenizer.from_pretrained(ImageLib.model_name)

        # Initialize the library when it is a new lib or force_init is True
        if force_init or new_lib:
            if force_init and not new_lib:
                tqdm.write(
                    f'Initialize library DB: {lib_path}, this is a force init operation and existing library data will be purged')
                self.__reset_lib()
            else:
                tqdm.write(f'Initialize library DB: {lib_path} for new library')
            self.__initialize_lib()
        else:
            tqdm.write(f'Load library DB: {lib_path}')

    def __is_new_lib(self, lib_path: str) -> bool:
        """Check if the image library is new

        Returns:
            bool: _description_
        """
        return not (os.path.isfile(os.path.join(lib_path, DB_NAME))
                    and os.path.isfile(os.path.join(lib_path, 'manifest.json')))

    def __initialize_lib_manifest(self, lib_name: str | None) -> dict:
        """Initialize the manifest file for the image library
        - Only called when the library is under a fresh initialization (manifest file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        if not lib_name:
            raise ValueError('A name must be provided for a new image library')

        file_path: str = os.path.join(self.lib_path, 'manifest.json')
        if os.path.isfile(file_path):
            raise ValueError(f'Manifest file already exists: {file_path}')

        initial_manifest: dict = {
            'NOTE': 'DO NOT delete this file or modify it manually',
            'lib_name': lib_name,  # Name of the library, must be unique and it will be used as the prefix of the redis index
            'alias': lib_name,     # Name alias for the library, for display
            'uuid': str(uuid4()),
        }
        with open(file_path, 'w') as f:
            json.dump(initial_manifest, f)
        return initial_manifest

    def __update_lib_manifest(self):
        """Update the manifest file for the image library
        """
        if not self.lib_manifest:
            raise ValueError('Library manifest not initialized')

        file_path: str = os.path.join(self.lib_path, 'manifest.json')
        if not os.path.isfile(file_path):
            raise ValueError(f'Manifest file missing: {file_path}')

        with open(file_path, 'w') as f:
            json.dump(self.lib_manifest, f)

    def __parse_lib_manifest(self) -> dict:
        """Parse the manifest file of the image library
        """
        file_path: str = os.path.join(self.lib_path, 'manifest.json')
        if not os.path.isfile(file_path):
            raise ValueError(f'Manifest file missing: {file_path}')

        content: dict | None = None
        with open(file_path, 'r') as f:
            content = json.load(f)
        if not content or not content.get('uuid') or not content.get('lib_name'):
            raise ValueError(f'Invalid manifest file: {file_path}')

        return content

    def __reset_lib(self):
        """Fully reset the image library
        1. Remove all keys in Redis
        2. Clear the DB
        """
        if not self.redis.connected:
            raise ValueError('Redis not connected')

        self.table.empty_table()
        self.redis.delete_by_prefix(f'{self.namespace}:')
        self.redis.snapshot()

    def __initialize_lib(self):
        """Get all files and relative path info under lib_path, including files in all sub folders under lib_path

        Args:
            lib_name (str): _description_
        """
        files: list[str] = list()
        for root, _, filenames in os.walk(self.lib_path):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self.lib_path))
        tqdm.write(f'Library scanned, found {len(files)} files in {self.lib_path}')

        dimension: int = 512
        redis_pipeline = self.redis.batched_pipeline(batch_size=200)
        for file in tqdm(files, desc=f'Processing images', unit='item', ascii=' |'):
            try:
                # Validate if the file is an image and insert it into the table
                # - After verify() the file stream is closed, need to reopen it
                img: Image.Image = Image.open(os.path.join(self.lib_path, file))
                img.verify()
                img = Image.open(os.path.join(self.lib_path, file))
            except:
                tqdm.write(f'Invalid image: {file}, skip')
                continue

            uuid: str = str(uuid4())
            relative_path: str = os.path.dirname(file)
            filename: str = os.path.basename(file)
            # (uuid, path, filename)
            self.table.insert_row((uuid, relative_path, filename))

            if redis_pipeline:
                embeddings: list[float] = self.embed_image_as_list(img, file)
                dimension = len(embeddings)
                # IMPORTANT: key is lib_name + uuid, which means all keys in redis are grouped by lib_name
                redis_pipeline.json_set(f'{self.namespace}:{uuid}', embeddings)

        if redis_pipeline:
            redis_pipeline.execute()
        self.redis.save()

        tqdm.write('Creating index...')
        if not self.__create_index(dimension):
            raise ValueError('Failed to create index')
        tqdm.write(f'Image library DB initialized')

    def __create_index(self, vector_dimension: int) -> bool:
        """Create index for current image library only

        Raises:
            ValueError: _description_
            e: _description_

        Returns:
            bool: _description_
        """
        if not self.lib_manifest:
            raise ValueError('Library manifest not initialized')

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
            res: str = self.redis.client.ft(self.index_name).create_index(fields=schema, definition=definition)
            return res == 'OK'
        except ResponseError as e:
            if e.args[0] == 'Index already exists':
                return True
            raise e

    def __embed_image(self, img: Image.Image, use_grad: bool) -> np.ndarray:
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
        if not use_grad:
            return image_features.numpy().astype(np.float32)
        else:
            # https://bobbyhadz.com/blog/cant-call-numpy-on-tensor-that-requires-grad
            return image_features.detach().numpy().astype(np.float32)

    def __embed_image_wrapper(self, img: Image.Image, relative_path: str | None = None, use_grad: bool = False) -> np.ndarray:
        """About use_grad(): https://datascience.stackexchange.com/questions/32651/what-is-the-use-of-torch-no-grad-in-pytorch
        """
        start: float = time.time()
        if not use_grad:
            with torch.no_grad():
                embeddings: np.ndarray = self.__embed_image(img, use_grad=False)
        else:
            embeddings: np.ndarray = self.__embed_image(img, use_grad=True)
        time_taken: float = time.time() - start
        if relative_path:
            tqdm.write(f'Image embedded: {relative_path}, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')
        else:
            tqdm.write(f'Image embedded, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')
        return embeddings

    def __embed_text(self, text: str, use_grad: bool = False) -> bytes:
        inputs: BatchEncoding = self.tokenizer(text, return_tensors="pt")
        text_features: FloatTensor = self.model.get_text_features(**inputs)  # type: ignore
        if not use_grad:
            with torch.no_grad():
                return text_features.numpy().astype(np.float32).tobytes()
        else:
            return text_features.detach().numpy().astype(np.float32).tobytes()

    def embed_image_as_list(self, img: Image.Image, relative_path: str | None = None, use_grad: bool = False) -> list[float]:
        """Embed an image and return vector as list
        """
        embeddings: np.ndarray = self.__embed_image_wrapper(img, relative_path, use_grad)
        return embeddings.tolist()

    def embed_image_as_bytes(self, img: Image.Image, relative_path: str | None = None, use_grad: bool = False) -> bytes:
        """Embed an image and return vector as bytes
        """
        embeddings: np.ndarray = self.__embed_image_wrapper(img, relative_path, use_grad)
        return embeddings.tobytes()

    def delete_lib(self):
        """Delete the image library, it purges all library data
        1. Reset the library
        2. Drop the library index
        3. Delete the manifest file
        4. Delete the DB file
        """
        if not self.redis.connected:
            raise ValueError('Redis not connected')

        self.__reset_lib()
        self.redis.client.ft(self.index_name).dropindex()
        self.redis.save()

        manifest_file: str = os.path.join(self.lib_path, 'manifest.json')
        if os.path.isfile(manifest_file):
            os.remove(manifest_file)

        db_file: str = os.path.join(self.lib_path, DB_NAME)
        if os.path.isfile(db_file):
            os.remove(db_file)

    def change_lib_name(self, new_name: str):
        """Change the library name for display (alias only)
        - This will not change the library's UUID and `lib_name` in the manifest file

        Args:
            new_name (str): _description_
        """
        if not self.lib_manifest:
            raise ValueError('Library manifest not initialized')

        self.lib_manifest['alias'] = new_name
        self.__update_lib_manifest()

    def remove_item_from_lib(self, uuid: str):
        if not self.redis.connected:
            raise ValueError('Redis not connected')

        self.redis.delete(f'{self.namespace}:{uuid}')
        self.table.delete_row_by_uuid(uuid)

    def image_for_image_search(self, img: Image.Image, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not img or not top_k or top_k <= 0:
            return list()

        if not self.redis.connected:
            raise ValueError('Redis not connected')
        start: float = time.time()

        image_embedding: bytes = self.embed_image_as_bytes(img)
        param: dict = {"query_vector": image_embedding} if not extra_params else \
                      {"query_vector": image_embedding} | extra_params

        # Query for top K results against given vector
        query: Query = Query(f'(*)=>[KNN {top_k} @vector $query_vector AS vector_score]')\
            .sort_by("vector_score").return_fields("$").dialect(2)
        search_result: Result = self.redis.client.ft(self.index_name).search(query, param)  # type: ignore
        docs: list[Document] = search_result.docs

        time_taken: float = time.time() - start
        tqdm.write(f'Image search with image similarity completed, cost: {time_taken:.2f}s')

        # Parse the result, get file data from DB
        # - The redis key of an image is `lib_name`:`uuid`
        res: list[tuple] = list()
        for doc in docs:
            uuid: str = doc.id.split(':')[1]
            row: tuple | None = self.table.select_row_by_uuid(uuid)
            if row:
                res.append(row)

        return res

    def text_for_image_search(self, text: str, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not text or not top_k or top_k <= 0:
            return list()

        if not self.redis.connected:
            raise ValueError('Redis not connected')
        start: float = time.time()

        text_embedding: bytes = self.__embed_text(text)
        param: dict = {"query_vector": text_embedding} if not extra_params else \
                      {"query_vector": text_embedding} | extra_params

        # Query for top K results against given vector
        query: Query = Query(f'(*)=>[KNN {top_k} @vector $query_vector AS vector_score]')\
            .sort_by("vector_score").return_fields("$").dialect(2)
        search_result: Result = self.redis.client.ft(self.index_name).search(query, param)  # type: ignore
        docs: list[Document] = search_result.docs

        time_taken: float = time.time() - start
        tqdm.write(f'Image search with text similarity completed, cost: {time_taken:.2f}s')

        # Parse the result, get file data from DB
        # - The redis key of an image is `lib_name`:`uuid`
        res: list[tuple] = list()
        for doc in docs:
            uuid: str = doc.id.split(':')[1]
            row: tuple | None = self.table.select_row_by_uuid(uuid)
            if row:
                res.append(row)

        return res

    def text_similarity_with_image(self, tokens: list[str], img: Image.Image) -> dict[str, float]:
        if not tokens or not img:
            return dict()

        # Use processor to build input data for CLIP model, with both text and image functionalities
        clip_input: BatchEncoding = self.processor(text=tokens, images=img, return_tensors="pt", padding=True)
        # Unpack the batched encoding and feed it to the CLIP model directly to process both text and image
        image_features: CLIPOutput = self.model(**clip_input)
        # Get the logits from the CLIP model
        probs: Tensor = image_features.logits_per_image.softmax(dim=1)

        res: dict[str, float] = dict()
        for i in range(len(tokens)):
            res[tokens[i]] = probs[0][i].item()

        return res
