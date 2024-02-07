import os
import pickle
import shutil
from datetime import datetime
from functools import wraps
from threading import Event
from typing import Any, Callable

from utils.constants.lib_constants import sorted_by_labels, view_styles
from utils.exceptions.lib_errors import LibraryError

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
    LIB_DATA_FOLDER,
}

BASIC_metadata: dict = {
    'type': '',
    'uuid': '',  # UUID of the library
    'name': '',
    'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'view_style': 'grid',
    'sorted_by': 'name',
    'favorite_list': set(),
    'exclusion_list': DEFAULT_EXCLUSION_LIST,
}

BASIC_profile: dict = {
    'uuid': '',  # UUID of the library
    'embedded_files': dict(),  # List of embedded files under the library
    'unfinished_files': dict(),  # List of files that are not finished embedding yet
}


def ensure_lib_is_ready(func):
    """Decorator to ensure the library is ready before calling the function
    """
    @wraps(func)
    def wrapper(self: 'LibraryBase', *args, **kwargs):
        if not self.lib_is_ready():
            raise LibraryError(f'Library is not ready: {self._path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


def ensure_metadata_ready(func):
    """Decorator to ensure the library's metadata exists
    """
    @wraps(func)
    def wrapper(self: 'LibraryBase', *args, **kwargs):
        if not self._metadata:
            raise LibraryError(f'Library is not ready: {self._path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


class LibraryBase:

    # Metadata for the library
    METADATA_FILE: str = 'metadata.bin'
    # Metadata for library file's scan profile
    SCAN_PROFILE_FILE: str = 'scan_profile.bin'

    def __init__(self, lib_path: str):
        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise LibraryError(f'Invalid lib path: {lib_path}')

        # UUID of the library
        self.uuid: str = ''
        # Path to the library root folder
        self._path_lib: str = lib_path
        # Path to the library's data folder
        self._path_lib_data: str = os.path.join(self._path_lib, LIB_DATA_FOLDER)
        # In-memory metadata
        self._metadata: dict = dict()
        self.__path_metadata: str = os.path.join(self._path_lib_data, LibraryBase.METADATA_FILE)
        # In-memory scan profile, for tracking the embedded files
        self._scan_profile: dict = dict()
        self.__path_scan_profile: str = os.path.join(self._path_lib_data, LibraryBase.SCAN_PROFILE_FILE)
        # Ensure the library's data folder exists
        if not os.path.isdir(self._path_lib_data):
            os.makedirs(self._path_lib_data)

    """
    Interface methods
    """

    def set_embedder(embedder: Any):
        """Set embedder for library
        """
        raise NotImplementedError()

    def lib_is_ready(self) -> bool:
        """Check if the library is ready for use
        - If not, means only the metadata file created
        """
        raise NotImplementedError()

    def demolish(self):
        """Completely destroy the library
        """
        raise NotImplementedError()

    def initialize(self,
                   force_init: bool = False,
                   progress_reporter: Callable[[int], None] | None = None,
                   cancel_event: Event | None = None):
        """Initialize the library

        Args:
            force_init (bool, optional): If the initialization is a force re-initialization. Defaults to False.
            reporter (Callable[[int], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.
            cancel_event (Event | None, optional): The event object to check if the initialization is cancelled. Defaults to None.
        """
        raise NotImplementedError()

    def use_doc(self,
                relative_path: str,
                provider_type: Any,
                force_init: bool = False,
                progress_reporter: Callable[[int], None] | None = None,
                cancel_event: Event | None = None):
        """Initialize or switch to a document under current library
        - If target document is not in metadata, then this is an uninitialized document, call __initialize_doc()
        - Otherwise load the document provider and vector DB for the target document directly
        - Target document's provider type is mandatory

        Args:
            relative_path (str): The target document's relative path based on current library
            provider_type (Type[D]): The target document's provider's type info
            force_init (bool, optional): If the initialization is a force re-initialization, this will delete doc's previous embeddings (if any). Defaults to False.
            reporter (Callable[[int], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.
            cancel_event (Event | None, optional): The event object to check if the initialization is cancelled. Defaults to None.
        """
        raise NotImplementedError()

    def add_file(self, folder_relative_path: str, source_file: str):
        """Add given source file to the library under the given folder
        """
        raise NotImplementedError()

    def move_file(self, relative_path: str, new_relative_path: str):
        """Move the given file under current library and retain the existing embedding information
        """
        if relative_path == new_relative_path:
            return
        if not relative_path or not new_relative_path:
            raise LibraryError('Invalid relative path')

        relative_path = relative_path.lstrip(os.path.sep)
        doc_path: str = os.path.join(self._path_lib, relative_path)
        if not os.path.isfile(doc_path):
            raise LibraryError('Invalid doc path')

        new_relative_path = new_relative_path.lstrip(os.path.sep)
        new_doc_path: str = os.path.join(self._path_lib, new_relative_path)
        if os.path.isfile(new_doc_path):
            raise LibraryError('Filename already exists')

        # Move the file
        os.makedirs(os.path.dirname(new_doc_path), exist_ok=True)
        shutil.move(doc_path, new_doc_path)

        # Adjust the embedding info in metadata if this image has been embedded
        uuid: str | None = self.get_embedded_files().pop(relative_path, None)
        if uuid:
            self.get_embedded_files()[new_relative_path] = uuid
            self._save_scan_profile()

    def rename_file(self, relative_path: str, new_name: str):
        """Rename the given file under current library and retain the existing embedding information
        """
        if not relative_path or not new_name:
            raise LibraryError('Invalid relative path')

        filename: str = os.path.basename(relative_path)
        if filename == new_name:
            return

        relative_path = relative_path.lstrip(os.path.sep)
        new_name = new_name.strip()
        new_relative_path = os.path.join(os.path.dirname(relative_path), new_name)
        self.move_file(relative_path, new_relative_path)

    def delete_files(self, relative_paths: list[str], **kwargs):
        """Delete the given file from the library, remove from both file system and embedding
        """
        raise NotImplementedError()

    """
    Task manager methods
    """

    def report_progress(self,
                        progress_reporter: Callable[[int], None] | None,
                        current_progress: int):
        """Report the progress of current task
        """
        if not progress_reporter:
            return
        if current_progress is None or current_progress < 0 or current_progress > 100:
            return
        try:
            progress_reporter(current_progress)
        except:
            pass

    """
    Metadata file & scan profile methods
    """

    def _save_metadata(self):
        """Save the metadata file for any updates
        """
        if not os.path.isfile(self.__path_metadata):
            raise LibraryError(f'Metadata file missing: {self.__path_metadata}')
        pickle.dump(self._metadata, open(self.__path_metadata, 'wb'))

    def _save_scan_profile(self):
        """Save the scan profile file for any updates
        """
        if not os.path.isfile(self.__path_scan_profile):
            raise LibraryError(f'Metadata file missing: {self.__path_scan_profile}')
        pickle.dump(self._scan_profile, open(self.__path_scan_profile, 'wb'))

    def metadata_exists(self) -> bool:
        """Check if the metadata & scan profile file exists
        """
        return os.path.isfile(self.__path_metadata) and os.path.isfile(self.__path_scan_profile)

    def initialize_metadata(self, initial: dict):
        """Initialize the metadata & scan profile file for the library
        - Only called when the library is under a fresh initialization (metadata file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        if not initial or not initial.get('uuid'):
            raise LibraryError('Invalid initial data')

        self._metadata = initial
        self.uuid = initial['uuid']
        pickle.dump(initial, open(self.__path_metadata, 'wb'))

    def initialize_scan_profile(self, initial: dict):
        """Initialize the profile file for the library
        - Scan profile can only be initialized after metadata, as the UUID will be used to verify initial data
        """
        if not self._metadata:
            raise LibraryError('Must initialize metadata before initialize scan profile')
        if not initial:
            raise LibraryError('Initial data must be provided for a new library')

        if self.uuid != initial['uuid']:
            raise LibraryError('Scan profile UUID mismatched with metadata UUID')
        pickle.dump(initial, open(self.__path_scan_profile, 'wb'))
        self._scan_profile = initial

    def load_metadata(self, given_uuid: str, given_name: str):
        """Load the metadata & scan profile file of the library
        """
        try:
            content: dict = pickle.load(open(self.__path_metadata, 'rb'))
        except:
            raise LibraryError(f'Invalid metadata file: {self.__path_metadata}')
        if not content:
            raise LibraryError(f'Invalid metadata file: {self.__path_metadata}')
        if not content.get('uuid', None) or content['uuid'] != given_uuid:
            raise LibraryError(f'Metadata UUID mismatched: {self.__path_metadata}')
        self._metadata = content
        self.uuid = content['uuid']
        if content['name'] != given_name:
            self.change_lib_name(given_name)

    def load_scan_profile(self, given_uuid: str):
        try:
            content: dict = pickle.load(open(self.__path_scan_profile, 'rb'))
        except:
            raise LibraryError(f'Invalid scan profile: {self.__path_scan_profile}')
        if not content:
            raise LibraryError(f'Invalid scan profile: {self.__path_scan_profile}')
        if not content.get('uuid', None) or content['uuid'] != given_uuid:
            raise LibraryError(f'Scan profile UUID mismatched with metadata UUID: {self.__path_scan_profile}')
        self._scan_profile = content

    def delete_metadata(self):
        """Delete the metadata & scan profile file of the library
        - Can only call on the deletion of current library
        """
        if os.path.isfile(self.__path_metadata):
            os.remove(self.__path_metadata)
        if os.path.isfile(self.__path_scan_profile):
            os.remove(self.__path_scan_profile)

    """
    Public methods to read library metadata & scan profile info
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

    @ensure_lib_is_ready
    def get_embedded_files(self) -> dict[str, str]:
        return self._scan_profile['embedded_files']

    @ensure_lib_is_ready
    def get_unfinished_files(self) -> dict[str, str]:
        return self._scan_profile['unfinished_files']

    """
    Public methods to change library metadata & scan profile info
    """

    @ensure_metadata_ready
    def change_lib_name(self, new_name: str):
        if not new_name or new_name == self._metadata['name']:
            return
        self._metadata['name'] = new_name
        self._save_metadata()

    @ensure_metadata_ready
    def change_view_style(self, new_style: str):
        if not new_style or new_style not in view_styles:
            return
        self._metadata['view_style'] = new_style
        self._save_metadata()

    @ensure_metadata_ready
    def change_sorted_by(self, new_sorted_by: str):
        if not new_sorted_by or new_sorted_by not in sorted_by_labels:
            return
        self._metadata['sorted_by'] = new_sorted_by
        self._save_metadata()

    @ensure_metadata_ready
    def change_favorite_list(self, new_list: set[str]):
        self._metadata['favorite_list'] = new_list
        self._save_metadata()

    @ensure_metadata_ready
    def change_exclusion_list(self, new_list: set[str]):
        self._metadata['exclusion_list'] = new_list
        self._save_metadata()
