import json
import os
import time
from datetime import datetime
from typing import Generator
from uuid import uuid4

import numpy as np
from PIL import Image
from redis.commands.search.document import Document
from torch import Tensor
from tqdm import tqdm

from image_knowledge.image_embedder import ImageEmbedder
from image_knowledge.image_lib_vector_db import ImageLibVectorDb
from sqlite.image_lib_table import ImageLibTable
from sqlite.sql_image_lib import DB_NAME
from utils.tqdm_context import TqdmContext
from vector_db.redis_client import BatchedPipeline


class ImageLib:
    """Define an image library
    """

    def __init__(self,
                 embedder: ImageEmbedder,
                 lib_path: str,
                 lib_name: str | None = None,
                 force_init: bool = False,
                 local_mode: bool = True):
        """
        Args:
            lib_path (str): Path to the image library
            lib_name (str | None, optional): Name to the image library, mandatory for a new library. Defaults to None.
            force_init (bool, optional): Force reset and reinitialize the image library. Defaults to False.
            local_mode (bool, optional): True for use local index, False for use Redis. Defaults to True.
        """
        if not embedder:
            raise ValueError('Image embedder is empty')

        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise ValueError(f'Invalid lib path: {lib_path}')

        new_lib: bool = self.__is_new_lib(lib_path)
        if new_lib and not lib_name:
            raise ValueError('A library name must be provided for a new image library')

        # Load manifest
        self.lib_path: str = lib_path
        with TqdmContext('Loading library manifest...', 'Loaded'):
            if new_lib:
                self.__lib_manifest: dict = self.__initialize_lib_manifest(lib_name)
            else:
                self.__lib_manifest: dict = self.__parse_lib_manifest()

        if not self.__lib_manifest:
            raise ValueError('Library manifest not initialized')

        # Connect to DB and vector DB (embedder here)
        self.table: ImageLibTable = ImageLibTable(lib_path)
        self.vector_db: ImageLibVectorDb = ImageLibVectorDb(use_redis=not local_mode,
                                                            lib_uuid=self.__lib_manifest['uuid'],
                                                            lib_namespace=self.__lib_manifest["lib_name"],
                                                            lib_path=lib_path)
        self.embedder: ImageEmbedder = embedder
        self.local_mode: bool = local_mode

        # Initialize the library when it is a new lib or force_init is True
        if force_init or new_lib:
            if force_init and not new_lib:
                tqdm.write(
                    f'Initialize library: {lib_path}, this is a force init operation and existing library data will be purged')
                self.__lib_manifest['last_scanned'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.__update_lib_manifest()
                self.vector_db.clean_all_data()
                self.table.clean_all_data()
            else:
                tqdm.write(f'Initialize library DB: {lib_path} for new library')
            self.__full_scan_and_initialize_lib()

    def __is_new_lib(self, lib_path: str) -> bool:
        """Check if the image library is new
        - If DB file or manifest file is missing, then it is a new library even though vector DB might exist
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
            'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_scanned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        with open(file_path, 'w') as f:
            json.dump(initial_manifest, f)
        return initial_manifest

    def __update_lib_manifest(self):
        """Update the manifest file for the image library
        """
        file_path: str = os.path.join(self.lib_path, 'manifest.json')
        if not os.path.isfile(file_path):
            raise ValueError(f'Manifest file missing: {file_path}')

        with open(file_path, 'w') as f:
            json.dump(self.__lib_manifest, f)

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

    def __write_entry(self, file: str, embeddings: list[float], save_pipeline: BatchedPipeline | None = None):
        """Write an image entry to both DB and vector DB
        - An UUID is generated to identify the image globally
        """
        timestamp: datetime = datetime.now()
        uuid: str = str(uuid4())
        relative_path: str = os.path.dirname(file)
        filename: str = os.path.basename(file)
        # (timestamp, uuid, path, filename)
        self.table.insert_row((timestamp, uuid, relative_path, filename))
        self.vector_db.add(uuid, embeddings, save_pipeline)

    def __do_scan(self) -> Generator[tuple[str, list[float]], None, None]:
        files: list[str] = list()
        for root, _, filenames in os.walk(self.lib_path):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self.lib_path))
        tqdm.write(f'Library scanned, found {len(files)} files in {self.lib_path}')

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

            start_time: float = time.time()
            embeddings: list[float] = self.embedder.embed_image_as_list(img)
            time_taken: float = time.time() - start_time
            tqdm.write(f'Image embedded: {file}, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')

            yield file, embeddings

    def __full_scan_and_initialize_lib(self, scan_only: bool = False):
        """Get all files and relative path info under lib_path, including files in all sub folders under lib_path

        Args:
            lib_name (str): _description_
        """
        save_pipeline: BatchedPipeline | None = None
        try:
            save_pipeline = self.vector_db.get_save_pipeline(batch_size=200)
        except NotImplementedError:
            pass

        dimension: int = -1
        if save_pipeline:
            # Use batched pipeline when available
            with save_pipeline:
                for file, embeddings in self.__do_scan():
                    if not scan_only:
                        if dimension == -1:
                            dimension = len(embeddings)
                        self.__write_entry(file, embeddings, save_pipeline)
        else:
            # Otherwise, save the embeddings one by one
            for file, embeddings in self.__do_scan():
                # If this is the first embedding and in local mode, initialize the index first as memory vector DB needs to build index before adding data
                if not scan_only:
                    if dimension == -1 and self.local_mode:
                        dimension = len(embeddings)
                        with TqdmContext('Creating index...', 'Index created'):
                            self.vector_db.initialize_index(dimension)
                    self.__write_entry(file, embeddings)

        if not scan_only:
            self.vector_db.persist()
            if not self.local_mode:
                with TqdmContext('Creating index...', 'Index created'):
                    self.vector_db.initialize_index(dimension)
            tqdm.write(f'Image library DB initialized')
        else:
            tqdm.write(f'Image library scanned')

    def force_initialize_lib(self):
        """Force initialize the image library
        """
        tqdm.write(
            f'Initialize library: {self.lib_path}, this is a force init operation and existing library data will be purged')
        self.__lib_manifest['last_scanned'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__update_lib_manifest()
        self.vector_db.clean_all_data()
        self.table.clean_all_data()
        self.__full_scan_and_initialize_lib()

    def scan_lib(self):
        self.__full_scan_and_initialize_lib(scan_only=True)

    def delete_lib(self):
        """Delete the image library, it purges all library data
        1. Clean and delete the vector DB
        2. Delete the table
        3. Delete the DB file
        4. Delete the manifest file
        """
        self.vector_db.delete_db()
        self.table.clean_all_data()

        db_file: str = os.path.join(self.lib_path, DB_NAME)
        if os.path.isfile(db_file):
            os.remove(db_file)

        manifest_file: str = os.path.join(self.lib_path, 'manifest.json')
        if os.path.isfile(manifest_file):
            os.remove(manifest_file)

    def change_lib_name(self, new_name: str):
        """Change the library name for display (alias only)
        - This will not change the library's UUID and `lib_name` in the manifest file

        Args:
            new_name (str): _description_
        """
        self.__lib_manifest['alias'] = new_name
        self.__update_lib_manifest()

    def remove_item_from_lib(self, uuid: str):
        self.vector_db.remove(uuid)
        self.table.delete_row_by_uuid(uuid)

    def get_scan_gap(self) -> int:
        """Get the time gap from last scan in days
        """
        last_scanned: datetime = datetime.strptime(self.__lib_manifest['last_scanned'], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - last_scanned).days

    def image_for_image_search(self, img: Image.Image, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not img or not top_k or top_k <= 0:
            return list()

        start: float = time.time()
        image_embedding: np.ndarray = self.embedder.embed_image(img)
        docs: list = self.vector_db.query(image_embedding)
        time_taken: float = time.time() - start
        tqdm.write(f'Image search with image similarity completed, cost: {time_taken:.2f}s')

        # Parse the result, get file data from DB
        # - The local key of an image is `uuid` or `id` of the vector in the index
        # - The redis key of an image is `lib_name`:`uuid`
        res: list[tuple] = list()
        if self.local_mode:
            casted_local: list[int | str] = docs
            for possible_uuid in casted_local:
                if isinstance(possible_uuid, int):
                    raise ValueError('ID tracking not enabled, cannot get UUID')
                row: tuple | None = self.table.select_row_by_uuid(possible_uuid)
                if row:
                    res.append(row)
        else:
            casted_redis: list[Document] = docs
            for doc in casted_redis:
                uuid: str = doc.id.split(':')[1]
                row: tuple | None = self.table.select_row_by_uuid(uuid)
                if row:
                    res.append(row)

        return res

    def text_for_image_search(self, text: str, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not text or not top_k or top_k <= 0:
            return list()

        start: float = time.time()
        # Text embedding is a 2D array, the first element is the embedding of the text
        text_embedding: np.ndarray = self.embedder.embed_text(text)[0]
        docs: list = self.vector_db.query(text_embedding)
        time_taken: float = time.time() - start
        tqdm.write(f'Image search with text similarity completed, cost: {time_taken:.2f}s')

        # Parse the result, get file data from DB
        # - The local key of an image is `uuid` or `id` of the vector in the index
        # - The redis key of an image is `lib_name`:`uuid`
        res: list[tuple] = list()
        if self.local_mode:
            casted_local: list[int | str] = docs
            for possible_uuid in casted_local:
                if isinstance(possible_uuid, int):
                    raise ValueError('ID tracking not enabled, cannot get UUID')
                row: tuple | None = self.table.select_row_by_uuid(possible_uuid)
                if row:
                    res.append(row)
        else:
            casted_redis: list[Document] = docs
            for doc in casted_redis:
                uuid: str = doc.id.split(':')[1]
                row: tuple | None = self.table.select_row_by_uuid(uuid)
                if row:
                    res.append(row)

        return res

    def text_image_similarity(self, tokens: list[str], img: Image.Image) -> dict[str, float]:
        if not tokens or not img:
            return dict()

        probs: Tensor = self.embedder.compute_text_image_similarity(tokens, img)
        res: dict[str, float] = dict()
        for i in range(len(tokens)):
            res[tokens[i]] = probs[0][i].item()

        return res
