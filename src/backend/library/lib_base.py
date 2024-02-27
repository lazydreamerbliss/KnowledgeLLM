import os
import pickle
import shutil
from datetime import datetime
from functools import wraps
from threading import Event, Lock
from typing import Any, Callable

from constants.lib_constants import (SORTED_BY_LABELS, SUPPORTED_EXTENSIONS,
                                     VIEW_STYLES)
from library.lib_item import *
from library.scan_record_tracker import ScanRecordTracker
from loggers import lib_logger as LOGGER
from utils.errors.lib_errors import LibraryError

LIB_DATA_FOLDER: str = '__library_data__'

DEFAULT_EXCLUSION_LIST: set[str] = {
    '$RECYCLE.BIN',
    'System Volume Information',
    'Thumbs.db',
    'desktop.ini',
    '.DS_Store',
    '.localized',
    '__pycache__',
    'node_modules',
    LIB_DATA_FOLDER,  # The folder for library's data
}

BASIC_METADATA: dict = {
    'type': '',
    'uuid': '',  # UUID of the library
    'name': '',
    'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'view_style': 'grid',
    'sorted_by': 'name',
    'favorite_list': set(),
    'exclusion_list': DEFAULT_EXCLUSION_LIST,
}


def ensure_lib_is_ready(func):
    """Decorator to ensure the library is ready before calling the function
    """
    @wraps(func)
    def wrapper(self: 'LibraryBase', *args, **kwargs):
        if not self.is_ready():
            raise LibraryError(f'Library is not ready: {self.path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


def ensure_metadata_ready(func):
    """Decorator to ensure the library's metadata exists
    """
    @wraps(func)
    def wrapper(self: 'LibraryBase', *args, **kwargs):
        if not self._metadata:
            raise LibraryError(f'Library is not ready, metadata not initialized: {self.path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


class LibraryBase:

    # Metadata for the library
    METADATA_FILE: str = 'metadata.bin'

    def __init__(self, lib_path: str):
        LOGGER.info(f'Instanizing library: {lib_path}')

        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise LibraryError(f'Invalid lib path: {lib_path}')

        # UUID of the library
        self.uuid: str = ''
        # The current relative path user is browsing under the library
        self.current_path: str = ''

        # Static path info - these paths are not supposed to be changed after library's initialization
        # Path to the library root folder
        self.path_lib: str = lib_path
        # Path to the library's data folder
        self._path_lib_data: str = os.path.join(self.path_lib, LIB_DATA_FOLDER)
        # Path to the library metadata file
        self.__path_metadata: str = os.path.join(self._path_lib_data, LibraryBase.METADATA_FILE)

        # In-memory library metadata
        self._metadata: dict = dict()
        # Scan tracker to track embedded files under the library
        self._tracker: ScanRecordTracker | None = None

        # File scan is mutually exclusive, use a lock to prevent concurrent operations
        self._scan_lock = Lock()

        # Ensure the library's data folder exists
        if not os.path.isdir(self._path_lib_data):
            os.makedirs(self._path_lib_data)

    """
    Library methods
    """

    def set_embedder(self, embedder: Any):
        """Set embedder for library

        Embedder initialization is apart from initialize(), it is easy to switch to another embedder without a re-initialization
        """
        raise NotImplementedError()

    def is_ready(self) -> bool:
        """Check if the library is ready for use
        - If not, means only the metadata file created
        """
        raise NotImplementedError()

    def demolish(self):
        """Completely destroy the library
        """
        raise NotImplementedError()

    def full_scan(self,
                  force_init: bool = False,
                  progress_reporter: Callable[[int, int, str | None], None] | None = None,
                  cancel_event: Event | None = None):
        """Initialize the library

        Args:
            force_init (bool, optional): If the initialization is a force re-initialization. Defaults to False.
            reporter (Callable[[int, int, str | None], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.
            cancel_event (Event | None, optional): The event object to check if the initialization is cancelled. Defaults to None.
        """
        raise NotImplementedError()

    def use_doc(self,
                relative_path: str,
                provider_type: Any,
                force_init: bool = False,
                progress_reporter: Callable[[int, int, str | None], None] | None = None,
                cancel_event: Event | None = None):
        """Initialize or switch to a document under current library
        - If target document is not in metadata, then this is an uninitialized document, call __initialize_doc()
        - Otherwise load the document provider and vector DB for the target document directly
        - Target document's provider type is mandatory

        Args:
            relative_path (str): The target document's relative path based on current library
            provider_type (Type[D]): The target document's provider's type info
            force_init (bool, optional): If the initialization is a force re-initialization, this will delete doc's previous embeddings (if any). Defaults to False.
            reporter (Callable[[int, int, str | None], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.
            cancel_event (Event | None, optional): The event object to check if the initialization is cancelled. Defaults to None.
        """
        raise NotImplementedError()

    """
    File A/R/W/D operation methods
    """

    def add_file(self, parent_relative_path: str, source_file: str) -> bool:
        """Add given source file to the library under the given folder
        """
        raise NotImplementedError()

    def move_file(self, relative_path: str, new_relative_path: str, called_from_rename: bool = False) -> bool:
        """Move the given file under current library and retain the existing embedding information

        Args:
            relative_path (str): The relative path of the target file to be moved
            new_relative_path (str): The new relative path of the target file

        Returns:
            bool: True if the move operation is successful
        """
        if not self._tracker:
            raise LibraryError('Embedding tracker not ready')

        # Do pre-checks for move operation
        # No pre-checks for rename operation (called_from_rename=True), as rename_file() already did
        if not called_from_rename:
            if not relative_path or not new_relative_path:
                return False

            relative_path = relative_path.strip()
            new_relative_path = new_relative_path.strip()
            if relative_path == new_relative_path:
                return True

            relative_path = relative_path.lstrip(os.path.sep)
            new_relative_path = new_relative_path.lstrip(os.path.sep)
            LOGGER.info(f'Move file: {relative_path} -> {new_relative_path}')

        old_doc_path: str = os.path.join(self.path_lib, relative_path)
        if not os.path.isfile(old_doc_path):
            LOGGER.error(f'File not exists on source: {old_doc_path}')
            return False

        new_doc_path: str = os.path.join(self.path_lib, new_relative_path)
        if os.path.isfile(new_doc_path):
            LOGGER.error(f'File with same name already exists on target: {new_doc_path}')
            return False

        # Move the file
        os.makedirs(os.path.dirname(new_doc_path), exist_ok=True)
        shutil.move(old_doc_path, new_doc_path)

        # Update the scan record with new relative path to retain the embedding information
        self._tracker.update_record_path(new_relative_path, relative_path)
        return True

    def rename_file(self, relative_path: str, new_name: str) -> bool:
        """Rename the given file under current library and retain the existing embedding information
        - It will invoke move_file() to perform the actual rename operation

        Args:
            relative_path (str): The relative path of the target file to be renamed
            new_name (str): The new filename

        Returns:
            bool: True if the rename operation is successful
        """
        if not relative_path or not new_name:
            return False
        relative_path = relative_path.strip()
        new_name = new_name.strip()
        if not relative_path or not new_name:
            return False

        filename: str = os.path.basename(relative_path)
        if filename == new_name:
            return True

        LOGGER.info(f'Rename file {relative_path}, {filename} -> {new_name}')
        relative_path = relative_path.lstrip(os.path.sep)
        new_relative_path = os.path.join(os.path.dirname(relative_path), new_name)
        return self.move_file(relative_path, new_relative_path, called_from_rename=True)

    def delete_file(self, relative_path: str, **kwargs) -> bool:
        """Delete the given file from the library, remove from both file system and embedding
        """
        raise NotImplementedError()

    def list_folder_content(self, folder_relative_path: str) -> tuple[list[DirectoryItem], list[FileItem]]:
        """List the content of a folder, no recursion

        Args:
            folder_relative_path (str): The relative path of the folder to be scanned, starting from the root of current library
        """
        dir_list: list[DirectoryItem] = list()
        file_list: list[FileItem] = list()

        folder_relative_path = folder_relative_path.lstrip(os.sep)
        folder_full_path: str = os.path.join(self.path_lib, folder_relative_path)
        if not os.path.isdir(folder_full_path):
            return dir_list, file_list

        LOGGER.info(f'Listing folder content: {folder_relative_path}')
        for item_name in os.listdir(folder_full_path):
            item_path: str = os.path.join(folder_full_path, item_name)

            if os.path.isdir(item_path):
                dir_relative_path: str = os.path.join(folder_relative_path, item_name)
                if not self.is_accessible(dir_relative_path):
                    continue

                d_item: DirectoryItem = DirectoryItem()
                d_item.name = item_name
                d_item.parent_path = folder_relative_path
                try:
                    d_stats: os.stat_result = os.stat(item_path)
                    d_item.dtc = datetime.utcfromtimestamp(d_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    d_item.dtm = datetime.utcfromtimestamp(d_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                except BaseException:
                    d_item.dtc = '-'
                    d_item.dtm = '-'
                dir_list.append(d_item)

            else:
                file_relative_path: str = os.path.join(folder_relative_path, item_name)
                if not self.is_accessible(file_relative_path):
                    continue

                f_item: FileItem = FileItem()
                f_item.name = item_name
                f_item.parent_path = folder_relative_path

                _, extension = os.path.splitext(item_name)
                if extension:
                    extension[1:].lower()
                f_item.extension = extension
                f_item.supported = extension in SUPPORTED_EXTENSIONS
                f_item.embedded = False if not self._tracker else self._tracker.is_recorded(file_relative_path)
                try:
                    f_stats: os.stat_result = os.stat(item_path)
                    f_item.dtc = datetime.utcfromtimestamp(f_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    f_item.dtm = datetime.utcfromtimestamp(f_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    f_item.size_b = f_stats.st_size
                except BaseException:
                    f_item.dtc = '-'
                    f_item.dtm = '-'
                    f_item.size_b = -1
                file_list.append(f_item)

        LOGGER.info(f'Folder content listed, found: {len(dir_list)} folders, {len(file_list)} files')
        return dir_list, file_list

    def is_accessible(self, relative_path: str) -> bool:
        """Check if the given relative path is accessible under the library
        - Accessible means the file or folder is not in the exclusion list and it is under the library's root
        """
        if not relative_path:
            return True
        relative_path = relative_path.lstrip(os.path.sep)
        if not relative_path:
            return True

        LOGGER.info(f'Checking accessibility: {relative_path}')
        exclusion_list: set[str] = self.get_exclusion_list()
        if exclusion_list:
            file_or_folder_name: str = os.path.basename(relative_path)
            if file_or_folder_name in exclusion_list or relative_path in exclusion_list:
                return False
        full_path: str = os.path.join(self.path_lib, relative_path)
        return os.path.exists(full_path)

    """
    Metadata file methods
    """

    def _save_metadata(self):
        """Save the metadata file for any updates
        """
        if not os.path.isfile(self.__path_metadata):
            raise LibraryError(f'Metadata file missing: {self.__path_metadata}')

        LOGGER.info('Saving metadata')
        pickle.dump(self._metadata, open(self.__path_metadata, 'wb'))

    def _metadata_exists(self) -> bool:
        """Check if the metadata exists
        """
        return os.path.isfile(self.__path_metadata)

    def initialize_metadata(self, initial: dict):
        """Initialize the metadata for the library
        - Only called when the library is under a fresh initialization (metadata file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        if not initial or not initial.get('uuid'):
            raise LibraryError('Invalid initial data')

        LOGGER.info('Initializing metadata')
        self._metadata = initial
        self.uuid = initial['uuid']
        pickle.dump(initial, open(self.__path_metadata, 'wb'))

    def load_metadata(self, given_uuid: str, given_name: str):
        """Load the metadata of the library
        """
        LOGGER.info('Loading metadata')
        try:
            content: dict = pickle.load(open(self.__path_metadata, 'rb'))
        except BaseException:
            raise LibraryError(f'Invalid metadata file: {self.__path_metadata}')
        if not content:
            raise LibraryError(f'Invalid metadata file: {self.__path_metadata}')
        if not content.get('uuid', None) or content['uuid'] != given_uuid:
            raise LibraryError(f'Metadata UUID mismatched: {self.__path_metadata}')

        self._metadata = content
        self.uuid = content['uuid']
        if content['name'] != given_name:
            self.change_lib_name(given_name)

    def delete_metadata(self):
        """Delete the metadata file of the library
        - Can only call on the deletion of current library
        """
        LOGGER.info('Deleting metadata')
        if os.path.isfile(self.__path_metadata):
            os.remove(self.__path_metadata)

    def get_embedded_files(self) -> dict[str, str]:
        """Get the embedded files under the library with [relative_path: UUID]
        """
        if not self._tracker:
            raise LibraryError('Embedding tracker not ready')
        return self._tracker.get_all_records()

    """
    Public methods to read library metadata
    """

    @ensure_metadata_ready
    def get_lib_name(self) -> str:
        return self._metadata['name']

    @ensure_metadata_ready
    def get_view_style(self) -> str:
        return self._metadata['view_style']

    @ensure_metadata_ready
    def get_sorted_by(self) -> str:
        return self._metadata['sorted_by']

    @ensure_metadata_ready
    def get_favorite_list(self) -> set[str]:
        return self._metadata['favorite_list']

    @ensure_metadata_ready
    def get_exclusion_list(self) -> set[str]:
        return self._metadata['exclusion_list']

    """
    Public methods to change library metadata
    """

    @ensure_metadata_ready
    def change_lib_name(self, new_name: str):
        if not new_name or new_name == self._metadata['name']:
            return

        LOGGER.info(f'Changing library name: {self._metadata["name"]} -> {new_name}')
        self._metadata['name'] = new_name
        self._save_metadata()

    @ensure_metadata_ready
    def change_view_style(self, new_style: str):
        if not new_style or new_style not in VIEW_STYLES:
            return

        LOGGER.info(f'Changing view style: {self._metadata["view_style"]} -> {new_style}')
        self._metadata['view_style'] = new_style
        self._save_metadata()

    @ensure_metadata_ready
    def change_sorted_by(self, new_sorted_by: str):
        if not new_sorted_by or new_sorted_by not in SORTED_BY_LABELS:
            return

        LOGGER.info(f'Changing sorted by: {self._metadata["sorted_by"]} -> {new_sorted_by}')
        self._metadata['sorted_by'] = new_sorted_by
        self._save_metadata()
