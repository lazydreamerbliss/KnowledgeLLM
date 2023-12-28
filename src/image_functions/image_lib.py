import os
import re
import time
from uuid import uuid4

import numpy as np
from PIL import Image
from redis.client import Pipeline
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
        self.table: ImageLibTable = ImageLibTable(lib_name, lib_path)
        self.redis: RedisClient = RedisClient(host="redis-server", port=6379, decode_responses=True)

        self.model: CLIPModel = CLIPModel.from_pretrained(ImageLib.model_name)  # type: ignore
        self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(ImageLib.model_name)

        # Check if DB exists in the lib path, initialize the lib if not exists
        if force_init or not os.path.exists(os.path.join(lib_path, DB_NAME)):
            tqdm.write(f'Initializing table: {lib_name}')
            self.table.empty_table()
            self.__initialize_image_lib()

    def __initialize_image_lib(self):
        """Get all files and relative path info under lib_path, including files in all sub folders under lib_path

        Args:
            lib_name (str): _description_
        """
        files: list[str] = []
        for root, _, filenames in os.walk(self.lib_path):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self.lib_path))
        tqdm.write(f'Found {len(files)} files in {self.lib_path}')

        pipeline_batch_size: int = 200
        redis_pipeline: Pipeline | None = self.redis.pipeline()
        if not redis_pipeline:
            tqdm.write('Redis server not connected, skip embedding')

        for file in tqdm(files):
            
            tqdm.write(f'Processing image: {file}')
            
            try:
                # Validate if the file is an image and insert it into the table
                img: Image.Image = Image.open(os.path.join(self.lib_path, file))
                img.verify()
            except:
                tqdm.write(f'Invalid image: {file}, skip')
                continue

            uuid: str = str(uuid4())
            if redis_pipeline:
                embeddings: list[float] = self.img_embedder(img, file)
                redis_pipeline.json().set(uuid, '$', embeddings)
                if len(redis_pipeline) >= pipeline_batch_size:
                    redis_pipeline.execute()
                    redis_pipeline = self.redis.pipeline()

            self.table.insert_row((uuid, file))

        if redis_pipeline:
            redis_pipeline.execute()
        tqdm.write(f'Image library initialized: {self.lib_path}')

    def img_embedder(self, img: Image.Image, file_path: str | None = None) -> list[float]:
        # The batch size is set to 1, so the first element of the output is the embedding of the image
        # - https://huggingface.co/transformers/model_doc/clip.html#clipmodel
        batch_size: int = 1
        start: float = time.time()

        inputs: BatchEncoding = self.processor(images=img, return_tensors="pt", padding=True)
        image_features = self.model.get_image_features(inputs.pixel_values)[batch_size-1]
        embeddings: list[float] = image_features.numpy().astype(np.float32).tolist()

        time_taken: float = time.time() - start
        if file_path:
            tqdm.write(f'Image embedded: {file_path}, dimension: {len(embeddings)}, cost: {time_taken:.1f}s')
        else:
            tqdm.write(f'Image embedded, dimension: {len(embeddings)}, cost: {time_taken:.1f}s')
        return embeddings
