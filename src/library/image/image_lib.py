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

from db.vector.redis_client import BatchedPipeline
from knowledge_base.image.image_embedder import ImageEmbedder
from library.image.image_lib_table import ImageLibTable
from library.image.image_lib_vector_db import ImageLibVectorDb
from library.image.sql import DB_NAME
from library.lib_base import LibBase, ensure_lib_is_ready
from utils.tqdm_context import TqdmContext


class ImageLib(LibBase):
    """Define an image library
    - Each image library will have only one table for storing images' metadata, such as UUID, path, filename, etc.
    """

    def __init__(self,
                 lib_path: str,
                 lib_name: str | None = None,
                 local_mode: bool = True):
        """
        Args:
            lib_path (str): Path to the library
            lib_name (str | None, optional): Name to the library, mandatory for a new library. Defaults to None.
            local_mode (bool, optional): True for use local index, False for use Redis. Defaults to True.
        """
        super().__init__(lib_path)

        # Load manifest
        with TqdmContext('Loading library manifest...', 'Loaded'):
            if not self.manifest_file_exists():
                if not lib_name:
                    raise ValueError('Library name must be provided for a new library')

                initial_manifest: dict = {
                    'NOTE': 'DO NOT delete this file or modify it manually',
                    'lib_name': lib_name,  # Name of the library, must be unique and it will be used as the prefix of the redis index
                    'alias': lib_name,     # Name alias for the library, for display
                    'uuid': str(uuid4()),
                    'type': 'image',
                    'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'last_scanned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.manifest = self.initialize_lib_manifest(initial_manifest)
            else:
                self.manifest = self.parse_lib_manifest()
        if not self.manifest:
            raise ValueError('Library manifest not initialized')

        self.path_db: str = os.path.join(self.path_lib, DB_NAME)
        self.path_vector_db: str = os.path.join(self.path_lib, ImageLibVectorDb.IDX_FILENAME)
        self.table: ImageLibTable | None = None
        self.vector_db: ImageLibVectorDb | None = None
        self.embedder: ImageEmbedder | None = None
        self.local_mode: bool = local_mode

    def lib_is_ready(self) -> bool:
        if not self.manifest_file_exists():
            return False
        if not self.table:
            return False
        if not self.vector_db:
            return False
        if not self.embedder:
            return False
        return True

    def set_embedder(self, embedder: ImageEmbedder):
        self.embedder = embedder

    def initialize(self, force_init: bool = False):
        ready: bool = self.lib_is_ready()
        if ready and not force_init:
            return

        if not self.embedder:
            raise ValueError('Embedder not set')

        # Load SQL DB and vector DB, and "not ready" has two cases:
        # 1. The lib is a new lib
        # 2. The lib is an existing lib but not loaded
        if not ready:
            self.table = ImageLibTable(self.path_lib)
            self.vector_db = ImageLibVectorDb(use_redis=not self.local_mode,
                                              lib_uuid=self.manifest['uuid'],
                                              lib_namespace=self.manifest["lib_name"],
                                              lib_path=self.path_lib)

        # If DBs are all loaded (case#2, an existing lib) and not force init, return directly
        if not force_init and self.table.table_row_count() > 0 and not self.vector_db.db_is_empty():  # type: ignore
            return

        # Refresh ready status, initialize the library for force init or new lib cases
        ready = self.lib_is_ready()
        if ready:
            with TqdmContext(f'Forcibly re-initializing library: {self.path_lib}, purging existing library data...', 'Cleaned'):
                self.manifest['last_scanned'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.update_lib_manifest()
                self.vector_db.clean_all_data()  # type: ignore
                self.table.clean_all_data()  # type: ignore
        else:
            tqdm.write(f'Initialize library DB: {self.path_lib} for new library')

        # Do full scan and initialize the lib
        self.__full_scan_and_initialize_lib()

    def __write_entry(self, file: str, embeddings: list[float], save_pipeline: BatchedPipeline | None = None):
        """Write an image entry to both DB and vector DB
        - An UUID is generated to identify the image globally
        """
        timestamp: datetime = datetime.now()
        uuid: str = str(uuid4())
        relative_path: str = os.path.dirname(file)
        filename: str = os.path.basename(file)
        # (timestamp, uuid, path, filename)
        self.table.insert_row((timestamp, uuid, relative_path, filename))  # type: ignore
        self.vector_db.add(uuid, embeddings, save_pipeline)  # type: ignore

    def __do_scan(self) -> Generator[tuple[str, list[float]], None, None]:
        files: list[str] = list()
        for root, _, filenames in os.walk(self.path_lib):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self.path_lib))
        tqdm.write(f'Library scanned, found {len(files)} files in {self.path_lib}')

        for file in tqdm(files, desc=f'Processing images', unit='item', ascii=' |'):
            try:
                # Validate if the file is an image and insert it into the table
                # - After verify() the file stream is closed, need to reopen it
                img: Image.Image = Image.open(os.path.join(self.path_lib, file))
                img.verify()
                img = Image.open(os.path.join(self.path_lib, file))
            except:
                tqdm.write(f'Invalid image: {file}, skip')
                continue

            start_time: float = time.time()
            embeddings: list[float] = self.embedder.embed_image_as_list(img)  # type: ignore
            time_taken: float = time.time() - start_time
            tqdm.write(f'Image embedded: {file}, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')

            yield file, embeddings

    def __full_scan_and_initialize_lib(self, scan_only: bool = False):
        """Get all files and relative path info under self.path_lib, including files in all sub folders under lib_path

        Args:
            lib_name (str): _description_
        """
        save_pipeline: BatchedPipeline | None = None
        try:
            save_pipeline = self.vector_db.get_save_pipeline(batch_size=200)  # type: ignore
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
                            self.vector_db.initialize_index(dimension)  # type: ignore
                    self.__write_entry(file, embeddings)

        if not scan_only:
            self.vector_db.persist()  # type: ignore
            if not self.local_mode:
                with TqdmContext('Creating index...', 'Index created'):
                    self.vector_db.initialize_index(dimension)  # type: ignore
            tqdm.write(f'Image library DB initialized')
        else:
            tqdm.write(f'Image library scanned')

    @ensure_lib_is_ready
    def delete_lib(self):
        """Delete the image library, it purges all library data
        1. Clean and delete the vector DB
        2. Delete the table
        3. Delete the DB file
        4. Delete the manifest file
        """
        self.vector_db.delete_db()  # type: ignore

        self.table.clean_all_data()  # type: ignore
        if os.path.isfile(self.path_db):
            os.remove(self.path_db)

        self.path_manifest
        if os.path.isfile(self.path_manifest):
            os.remove(self.path_manifest)

    def change_lib_name(self, new_name: str):
        """Change the library name for display (alias only)
        - This will not change the library's UUID and `lib_name` in the manifest file
        """
        self.manifest['alias'] = new_name
        self.update_lib_manifest()

    @ensure_lib_is_ready
    def remove_item_from_lib(self, uuid: str):
        self.vector_db.remove(uuid)  # type: ignore
        self.table.delete_row_by_uuid(uuid)  # type: ignore

    def get_scan_gap(self) -> int:
        """Get the time gap from last scan in days
        """
        last_scanned: datetime = datetime.strptime(self.manifest['last_scanned'], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - last_scanned).days

    @ensure_lib_is_ready
    def image_for_image_search(self, img: Image.Image, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not img or not top_k or top_k <= 0:
            return list()

        start: float = time.time()
        image_embedding: np.ndarray = self.embedder.embed_image(img)  # type: ignore
        docs: list = self.vector_db.query(np.asarray([image_embedding]))  # type: ignore
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
                row: tuple | None = self.table.select_row_by_uuid(possible_uuid)  # type: ignore
                if row:
                    res.append(row)
        else:
            casted_redis: list[Document] = docs
            for doc in casted_redis:
                uuid: str = doc.id.split(':')[1]
                row: tuple | None = self.table.select_row_by_uuid(uuid)  # type: ignore
                if row:
                    res.append(row)

        return res

    @ensure_lib_is_ready
    def text_for_image_search(self, text: str, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not text or not top_k or top_k <= 0:
            return list()

        start: float = time.time()
        # Text embedding is a 2D array, the first element is the embedding of the text
        text_embedding: np.ndarray = self.embedder.embed_text(text)[0]  # type: ignore
        docs: list = self.vector_db.query(np.asarray([text_embedding]))  # type: ignore
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
                row: tuple | None = self.table.select_row_by_uuid(possible_uuid)  # type: ignore
                if row:
                    res.append(row)
        else:
            casted_redis: list[Document] = docs
            for doc in casted_redis:
                uuid: str = doc.id.split(':')[1]
                row: tuple | None = self.table.select_row_by_uuid(uuid)  # type: ignore
                if row:
                    res.append(row)

        return res

    @ensure_lib_is_ready
    def text_image_similarity(self, tokens: list[str], img: Image.Image) -> dict[str, float]:
        if not tokens or not img:
            return dict()

        probs: Tensor = self.embedder.compute_text_image_similarity(tokens, img)  # type: ignore
        res: dict[str, float] = dict()
        for i in range(len(tokens)):
            res[tokens[i]] = probs[0][i].item()

        return res
