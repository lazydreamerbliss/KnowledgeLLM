import json
import os
import re
import time
from sqlite3 import Cursor
from uuid import uuid4

import numpy as np
from PIL import Image
from redis import ResponseError
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from torch import Tensor
from tqdm import tqdm
from transformers import BatchEncoding, CLIPModel, CLIPProcessor

from redis_client import RedisClient
from sqlite.image_lib_table import ImageLibTable
from sqlite.image_lib_table_sql import DB_NAME


class ImageLib:
    model_name: str = "openai/clip-vit-base-patch16"

    def __init__(self, lib_path: str, lib_name: str | None = None, force_init: bool = False):
        if not lib_name:
            # Get the last part of the lib path as the lib name
            lib_name = re.split(r'[/\\]', lib_path)[-1]

        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not lib_name or not os.path.isdir(lib_path):
            raise ValueError(f'Invalid lib path: {lib_path}')

        self.lib_path: str = lib_path
        self.lib_name: str = lib_name
        self.lib_manifest: dict | None = None
        self.redis: RedisClient = RedisClient(host="localhost", port=6379, password="test123")
        self.model: CLIPModel = CLIPModel.from_pretrained(ImageLib.model_name)  # type: ignore
        self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(ImageLib.model_name)

        # Check if library DB exists under the given path
        # - Check must be done before initializing the table, since table initialization will create a DB file and lead to a false positive
        if force_init or not os.path.isfile(os.path.join(lib_path, DB_NAME)):
            self.table: ImageLibTable = ImageLibTable(lib_path)
            if force_init:
                tqdm.write(f'Initialize library DB: {lib_path}, this is a force init operation')
                self.__reset_lib()
            else:
                tqdm.write(f'Initialize library DB: {lib_path}')

            self.__initialize_lib()
            return

        tqdm.write(f'Loading library DB: {lib_path}')
        self.__parse_lib_manifest()
        self.table: ImageLibTable = ImageLibTable(lib_path)

    def __initialize_lib_manifest(self):
        """Initialize the manifest file for the image library
        - Only called when the library is under a fresh initialization (manifest file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        file_path: str = os.path.join(self.lib_path, 'manifest.json')
        if os.path.isfile(file_path):
            return

        initial_manifest: dict = {
            'NOTE': 'DO NOT delete this file or modify it manually',
            'lib_name': self.lib_name,
            'uuid': str(uuid4()),
        }
        with open(file_path, 'w') as f:
            json.dump(initial_manifest, f)

    def __reset_lib(self):
        """Fully reset the image library
        1. Select all from DB and delete UUIDs from Redis
        2. Clean up DB
        """
        if not self.redis.connected:
            raise ValueError('Redis not connected')

        cursor: Cursor = self.table.select_all()
        for row in tqdm(cursor, desc=f'Delete library items', unit='item', ascii=' |'):
            # row[0] is the id, row[1] is the uuid
            self.redis.delete(row[1])
        self.table.empty_table()

    def __initialize_lib(self):
        """Get all files and relative path info under lib_path, including files in all sub folders under lib_path

        Args:
            lib_name (str): _description_
        """
        self.__initialize_lib_manifest()
        self.__parse_lib_manifest()

        files: list[str] = []
        for root, _, filenames in os.walk(self.lib_path):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self.lib_path))
        tqdm.write(f'Found {len(files)} files in {self.lib_path}')

        redis_pipeline = self.redis.batched_pipeline(batch_size=200)
        for file in tqdm(files, desc=f'Processing images', unit='item', ascii=' |'):
            try:
                # Validate if the file is an image and insert it into the table
                # - After verify() the file is closed, reopen it
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
                embeddings: list[float] = self.embed_image(img, file)
                redis_pipeline.json_set(uuid, embeddings)

        if redis_pipeline:
            redis_pipeline.execute()
        self.redis.save()

        tqdm.write('Creating index...')
        if not self.__create_index():
            raise ValueError('Failed to create index')
        tqdm.write(f'Image library DB initialized')

    def __parse_lib_manifest(self) -> None:
        file_path: str = os.path.join(self.lib_path, 'manifest.json')
        if not os.path.isfile(file_path):
            raise ValueError(f'Invalid manifest file: {file_path}')

        content: dict | None = None
        with open(file_path, 'r') as f:
            content = json.load(f)
        if not content or not content.get('uuid'):
            raise ValueError(f'Invalid manifest file: {file_path}')

        self.lib_manifest = content

    def __create_index(self) -> bool:
        if not self.lib_manifest:
            raise ValueError('Library manifest not initialized')
        lib_uuid: str = self.lib_manifest['uuid']
        vector_dimension = 512

        # VectorField is a field type that allows to index dense vectors for similarity search and filtering, it has 3 parameters and 1 optional parameter as dict:
        # - name: The name of the field, must be unique in the index
        # - algorithm: The algorithm used to index the vector, can be one of the following:
        schema = (
            VectorField(
                "$",
                "FLAT",  # Flat vector field, simple but expensive (O(n))
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dimension,
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name="vector",
            ),
        )

        # Set a prefix for the index, for later query, also as a namespace and possible isolation from normal data
        # - Use `{lib_name}-*` to query all related data
        vector_idx_prefix: str = f"{self.lib_name}-"
        definition: IndexDefinition = IndexDefinition(prefix=[vector_idx_prefix], index_type=IndexType.JSON)

        # Create the vector index
        vector_idx_name: str = f"v_idx_img_lib:{lib_uuid}"
        try:
            res: str = self.redis.client.ft(vector_idx_name).create_index(
                fields=schema, definition=definition
            )
            return res == 'OK'
        except ResponseError as e:
            if e.args[0] == 'Index already exists':
                return True
            raise e

    def embed_image(self, img: Image.Image, relative_path: str | None = None) -> list[float]:
        """Embed an image

        Args:
            img (Image.Image): _description_
            relative_path (str | None, optional): Logging only. Defaults to None.

        Returns:
            list[float]: _description_
        """
        # The batch size is set to 1, so the first element of the output is the embedding of the image
        # - https://huggingface.co/transformers/model_doc/clip.html#clipmodel
        batch_size: int = 1
        start: float = time.time()

        inputs: BatchEncoding = self.processor(images=img, return_tensors="pt", padding=True)
        image_features: Tensor = self.model.get_image_features(inputs.pixel_values)[batch_size-1]
        # https://bobbyhadz.com/blog/cant-call-numpy-on-tensor-that-requires-grad
        embeddings: list[float] = image_features.detach().numpy().astype(np.float32).tolist()

        time_taken: float = time.time() - start
        if relative_path:
            tqdm.write(f'Image embedded: {relative_path}, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')
        else:
            tqdm.write(f'Image embedded, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')
        return embeddings

    def remove_item_from_lib(self, uuid: str):
        if not self.redis.connected:
            raise ValueError('Redis not connected')

        self.redis.delete(uuid)
        self.table.delete_row_by_uuid(uuid)
