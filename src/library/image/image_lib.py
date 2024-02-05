import os
import shutil
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
from library.lib_base import *
from utils.exceptions.task_errors import TaskCancellationException
from utils.tqdm_context import TqdmContext


class ImageLib(LibraryBase):
    """Define an image library
    - Each image library will have only one table for storing images' metadata, such as UUID, path, filename, etc.
    """

    def __init__(self,
                 lib_path: str,
                 lib_name: str,
                 uuid: str,
                 local_mode: bool = True):
        """
        Args:
            lib_path (str): Path to the library
            uuid (str): UUID of the library
            local_mode (bool, optional): True for use local index, False for use Redis. Defaults to True.
        """
        if not uuid or not lib_name:
            raise LibraryError('Invalid UUID or library name')
        super().__init__(lib_path)

        # Load metadata
        with TqdmContext('Loading library metadata...', 'Loaded'):
            if not self.metadata_exists():
                initial_metadata: dict = BASIC_metadata | {
                    'type': 'image',
                    'uuid': uuid,
                    'name': lib_name,
                    'last_scanned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.initialize_metadata(initial_metadata)
            else:
                self.load_metadata(uuid, lib_name)
        if not self._metadata or not self.uuid:
            raise LibraryError('Library metadata not initialized')

        self.local_mode: bool = local_mode
        self.__table: ImageLibTable | None = None
        self.__vector_db: ImageLibVectorDb | None = None
        self.__embedder: ImageEmbedder | None = None

    """
    Private methods
    """

    def __write_entry(self, file: str, embedding: list[float], save_pipeline: BatchedPipeline | None = None):
        """Write an image entry (file info + embedding) to both DB and vector DB
        - An UUID is generated to identify the image globally
        """
        timestamp: datetime = datetime.now()
        uuid: str = str(uuid4())
        relative_path: str = os.path.dirname(file)
        filename: str = os.path.basename(file)
        # (timestamp, uuid, path, filename)
        self.__table.insert_row((timestamp, uuid, relative_path, filename))  # type: ignore
        self.__vector_db.add(uuid, embedding, save_pipeline)  # type: ignore

    def __do_scan(self,
                  progress_reporter: Callable[[int], None] | None,
                  scan_only: bool = False) -> Generator[tuple[str, list[float] | None], None, None]:
        """Scan the library and embed the images on the fly

        Args:
            progress_reporter (Callable[[int], None] | None): The progress reporter function to report the progress to task manager
            scan_only (bool, optional): If do file scan only (without embeddinga). Defaults to False.

        Yields:
            Generator[tuple[str, list[float] | None], None, None]: _description_
        """
        files: list[str] = list()
        for root, _, filenames in os.walk(self._path_lib):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root, filename), self._path_lib))
        total_files: int = len(files)
        tqdm.write(f'Library scanned, found {total_files} files in {self._path_lib}')

        previous_progress: int = -1
        for i, file in tqdm(enumerate(files), desc=f'Processing images', unit='item', ascii=' |'):
            try:
                # Validate if the file is an image and insert it into the table
                # - After verify() the file stream is closed, need to reopen it
                img: Image.Image = Image.open(os.path.join(self._path_lib, file))
                img.verify()
                img = Image.open(os.path.join(self._path_lib, file))
            except:
                tqdm.write(f'Invalid image: {file}, skip')
                continue

            # If reporter is given, report progress to task manager
            # - Reduce report frequency, only report when progress changes
            if progress_reporter:
                try:
                    current_progress: int = int(i / total_files * 100)
                    if current_progress > previous_progress:
                        previous_progress = current_progress
                        progress_reporter(current_progress)
                except:
                    pass

            if not scan_only:
                start_time: float = time.time()
                embedding: list[float] = self.__embedder.embed_image_as_list(img)  # type: ignore
                time_taken: float = time.time() - start_time
                tqdm.write(f'Image embedded: {file}, dimension: {len(embedding)}, cost: {time_taken:.2f}s')
                yield file, embedding
            else:
                yield file, None

    def __full_scan_and_initialize_lib(self,
                                       progress_reporter: Callable[[int], None] | None,
                                       cancel_event: Event | None,
                                       scan_only: bool = False):
        """Get all files and relative path info under self.path_lib, including files in all sub folders under lib_path
        """
        save_pipeline: BatchedPipeline | None = None
        try:
            save_pipeline = self.__vector_db.get_save_pipeline(batch_size=200)  # type: ignore
        except NotImplementedError:
            pass

        dimension: int = -1
        if save_pipeline:
            # Use batched pipeline when available
            with save_pipeline:
                for file, embedding in self.__do_scan(progress_reporter):
                    if not embedding:
                        raise LibraryError('Embedding not found')
                    if cancel_event is not None and cancel_event.is_set():
                        tqdm.write(f'Library initialization cancelled')
                        raise TaskCancellationException('Library initialization cancelled')

                    if not scan_only:
                        if dimension == -1:
                            dimension = len(embedding)
                        self.__write_entry(file, embedding, save_pipeline)
        else:
            # Otherwise, save the embedding one by one
            for file, embedding in self.__do_scan(progress_reporter):
                if not embedding:
                    raise LibraryError('Embedding not found')
                if cancel_event is not None and cancel_event.is_set():
                    tqdm.write(f'Library initialization cancelled')
                    raise TaskCancellationException('Library initialization cancelled')

                # If this is the first embedding and in local mode, initialize the index first as memory vector DB needs to build index before adding data
                if not scan_only:
                    if dimension == -1 and self.local_mode:
                        dimension = len(embedding)
                        with TqdmContext('Creating index...', 'Index created'):
                            self.__vector_db.initialize_index(dimension)  # type: ignore
                    self.__write_entry(file, embedding)

        if not scan_only:
            self.__vector_db.persist()  # type: ignore
            if not self.local_mode:
                with TqdmContext('Creating index...', 'Index created'):
                    self.__vector_db.initialize_index(dimension)  # type: ignore
            tqdm.write(f'Image library DB initialized')
        else:
            tqdm.write(f'Image library scanned')

    """
    Overridden public methods from LibraryBase
    """

    def lib_is_ready(self) -> bool:
        if not self.metadata_exists():
            return False
        if not self.__table:
            return False
        if not self.__vector_db:
            return False
        if not self.__embedder:
            return False
        return True

    def initialize(self,
                   force_init: bool = False,
                   progress_reporter: Callable[[int], None] | None = None,
                   cancel_event: Event | None = None):
        ready: bool = self.lib_is_ready()
        if ready and not force_init:
            return

        if not self.__embedder:
            raise LibraryError('Embedder not set')

        # Load SQL DB and vector DB, and "not ready" has two cases:
        # 1. The lib is a new lib
        # 2. The lib is an existing lib but not loaded
        if not ready:
            self.__table = ImageLibTable(self._path_lib_data)
            self.__vector_db = ImageLibVectorDb(use_redis=not self.local_mode,
                                                lib_uuid=self._metadata['uuid'],
                                                data_folder=self._path_lib_data)

        # If DBs are all loaded (case#2, an existing lib) and not force init, return directly
        if not force_init and self.__table.row_count() > 0 and not self.__vector_db.db_is_empty():  # type: ignore
            return

        # Refresh ready status, initialize the library for force init or new lib cases
        ready = self.lib_is_ready()
        if ready:
            with TqdmContext(f'Forcibly re-initializing library: {self._path_lib}, purging existing library data...', 'Cleaned'):
                self.__vector_db.clean_all_data()  # type: ignore
                self.__table.clean_all_data()  # type: ignore
        else:
            tqdm.write(f'Initialize library DB: {self._path_lib} for new library')

        self._metadata['last_scanned'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._save_metadata()

        # Do full scan and initialize the lib
        try:
            self.__full_scan_and_initialize_lib(progress_reporter, cancel_event)
        except TaskCancellationException:
            # On cancel, clean the DB
            self.__vector_db.clean_all_data()  # type: ignore
            self.__table.clean_all_data()  # type: ignore

    def demolish(self):
        """Delete the image library, it purges all library data
        1. Delete vector index, delete file directly if local mode, otherwise delete from Redis
        2. Delete DB file
        3. Delete metadata file

        Simply purge the library data folder
        """
        if not self.local_mode:
            if not self.__vector_db:
                raise LibraryError('For Redis vector DB, the library must be initialized before demolish')
            self.__vector_db.delete_db()

        self.__embedder = None
        self.__table = None
        self.__vector_db = None
        shutil.rmtree(self._path_lib_data)

    """
    Public methods
    """

    def set_embedder(self, embedder: ImageEmbedder):
        self.__embedder = embedder

    @ensure_lib_is_ready
    def remove_item_from_lib(self, uuid: str):
        self.__vector_db.remove(uuid)  # type: ignore
        self.__table.delete_row_by_uuid(uuid)  # type: ignore

    def get_scan_gap(self) -> int:
        """Get the time gap from last scan in days
        """
        last_scanned: datetime = datetime.strptime(self._metadata['last_scanned'], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - last_scanned).days

    @ensure_lib_is_ready
    def image_for_image_search(self, img: Image.Image, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not img or not top_k or top_k <= 0:
            return list()

        start: float = time.time()
        image_embedding: np.ndarray = self.__embedder.embed_image(img)  # type: ignore
        docs: list = self.__vector_db.query(np.asarray([image_embedding]), top_k)  # type: ignore
        time_taken: float = time.time() - start
        tqdm.write(f'Image search with image similarity completed, cost: {time_taken:.2f}s')

        # Parse the result, get file data from DB
        # - The local key of an image is `uuid` or `id` of the vector in the index
        # - The redis key of an image is `lib_uuid`:`img_uuid`
        res: list[tuple] = list()
        if self.local_mode:
            casted_local: list[int | str] = docs
            for possible_uuid in casted_local:
                if isinstance(possible_uuid, int):
                    raise LibraryError('ID tracking not enabled, cannot get UUID')
                row: tuple | None = self.__table.select_row_by_uuid(possible_uuid)  # type: ignore
                if row:
                    res.append(row)
        else:
            casted_redis: list[Document] = docs
            for doc in casted_redis:
                uuid: str = doc.id.split(':')[1]
                row: tuple | None = self.__table.select_row_by_uuid(uuid)  # type: ignore
                if row:
                    res.append(row)

        return res

    @ensure_lib_is_ready
    def text_for_image_search(self, text: str, top_k: int = 10, extra_params: dict | None = None) -> list[tuple]:
        if not text or not top_k or top_k <= 0:
            return list()

        start: float = time.time()
        # Text embedding is a 2D array, the first element is the embedding of the text
        text_embedding: np.ndarray = self.__embedder.embed_text(text)[0]  # type: ignore
        docs: list = self.__vector_db.query(np.asarray([text_embedding]), top_k)  # type: ignore
        time_taken: float = time.time() - start
        tqdm.write(f'Image search with text similarity completed, cost: {time_taken:.2f}s')

        # Parse the result, get file data from DB
        # - The local key of an image is `uuid` or `id` of the vector in the index
        # - The redis key of an image is `lib_uuid`:`img_uuid`
        res: list[tuple] = list()
        if self.local_mode:
            casted_local: list[int | str] = docs
            for possible_uuid in casted_local:
                if isinstance(possible_uuid, int):
                    raise LibraryError('ID tracking not enabled, cannot get UUID')
                row: tuple | None = self.__table.select_row_by_uuid(possible_uuid)  # type: ignore
                if row:
                    res.append(row)
        else:
            casted_redis: list[Document] = docs
            for doc in casted_redis:
                uuid: str = doc.id.split(':')[1]
                row: tuple | None = self.__table.select_row_by_uuid(uuid)  # type: ignore
                if row:
                    res.append(row)

        return res

    @ensure_lib_is_ready
    def text_image_similarity(self, tokens: list[str], img: Image.Image) -> dict[str, float]:
        if not tokens or not img:
            return dict()

        probs: Tensor = self.__embedder.compute_text_image_similarity(tokens, img)  # type: ignore
        res: dict[str, float] = dict()
        for i in range(len(tokens)):
            res[tokens[i]] = probs[0][i].item()

        return res
