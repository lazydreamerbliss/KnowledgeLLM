import json
import os
import time
from datetime import datetime
from uuid import uuid4

from PIL import Image
from redis.commands.search.document import Document
from torch import Tensor
from tqdm import tqdm

from image_knowledge.image_lib_embedder import ImageLibEmbedder
from image_knowledge.image_lib_vector_db import ImageLibVectorDb
from sqlite.image_lib_table import ImageLibTable
from sqlite.sql_image_lib import DB_NAME
from vector_db.redis_client import BatchedPipeline


class ImageLib:
    """Define an image library
    """

    def __init__(self, lib_path: str, lib_name: str | None = None, force_init: bool = False, local_mode: bool = True):
        """
        Args:
            lib_path (str): Path to the image library
            lib_name (str | None, optional): Name to the image library, mandatory for a new library. Defaults to None.
            force_init (bool, optional): Force reset and reinitialize the image library. Defaults to False.
            local_mode (bool, optional): True for use local index, False for use Redis. Defaults to True.
        """
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
            tqdm.write(f'Initializing library manifest...', end=' ')
            self.__lib_manifest: dict = self.__initialize_lib_manifest(lib_name)
        else:
            tqdm.write(f'Loading library manifest...', end=' ')
            self.__lib_manifest: dict = self.__parse_lib_manifest()

        if not self.__lib_manifest:
            raise ValueError('Library manifest not initialized')
        tqdm.write(f'Loaded')

        # Connect to DB and vector DB (embedder here)
        self.table: ImageLibTable = ImageLibTable(lib_path)
        self.vector_db: ImageLibVectorDb = ImageLibVectorDb(use_redis=not local_mode,
                                                            lib_uuid=self.__lib_manifest['uuid'],
                                                            lib_namespace=self.__lib_manifest["lib_name"],
                                                            lib_path=lib_path)
        self.embedder: ImageLibEmbedder = ImageLibEmbedder()

        # Initialize the library when it is a new lib or force_init is True
        if force_init or new_lib:
            if force_init and not new_lib:
                tqdm.write(
                    f'Initialize library DB: {lib_path}, this is a force init operation and existing library data will be purged')
                self.__lib_manifest['last_scanned'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.__update_lib_manifest()
                self.vector_db.clean_all_data()
                self.table.clean_all_data()
            else:
                tqdm.write(f'Initialize library DB: {lib_path} for new library')
            self.__full_scan_and_initialize_lib()
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

    def __full_scan_and_initialize_lib(self):
        """Get all files and relative path info under lib_path, including files in all sub folders under lib_path

        Args:
            lib_name (str): _description_
        """
        save_pipeline: BatchedPipeline | None = self.vector_db.get_save_pipeline(batch_size=200)
        files: list[str] = list()
        for root, _, filenames in os.walk(self.lib_path):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self.lib_path))
        tqdm.write(f'Library scanned, found {len(files)} files in {self.lib_path}')

        dimension: int = 512
        with save_pipeline:
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

                # Write DB entry
                timestamp: datetime = datetime.now()
                uuid: str = str(uuid4())
                relative_path: str = os.path.dirname(file)
                filename: str = os.path.basename(file)
                # (timestamp, uuid, path, filename)
                self.table.insert_row((timestamp, uuid, relative_path, filename))

                # Embed the image and write vector DB entry
                start_time: float = time.time()
                embeddings: list[float] = self.embedder.embed_image_as_list(img)
                dimension = len(embeddings)
                time_taken: float = time.time() - start_time
                tqdm.write(f'Image embedded: {file}, dimension: {len(embeddings)}, cost: {time_taken:.2f}s')
                self.vector_db.add(uuid, embeddings, save_pipeline)

        self.vector_db.persist()
        tqdm.write('Creating index...')
        self.vector_db.initialize_index(dimension)
        tqdm.write(f'Image library DB initialized')

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
        image_embedding: bytes = self.embedder.embed_image_as_bytes(img)
        docs: list[Document] = self.vector_db.query(image_embedding)
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

        start: float = time.time()
        text_embedding: bytes = self.embedder.embed_text(text)
        docs: list[Document] = self.vector_db.query(text_embedding)
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

    def text_image_similarity(self, tokens: list[str], img: Image.Image) -> dict[str, float]:
        if not tokens or not img:
            return dict()

        probs: Tensor = self.embedder.compute_text_image_similarity(tokens, img)
        res: dict[str, float] = dict()
        for i in range(len(tokens)):
            res[tokens[i]] = probs[0][i].item()

        return res
