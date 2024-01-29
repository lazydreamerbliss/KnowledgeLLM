import os
import pickle
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

BASIC_METADATA: dict = {
    'type': '',
    'uuid': '',
    'name': '',
    'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'last_scanned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
        if not self.lib_is_ready():
            raise LibraryError(f'Library is not ready: {self.path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


def ensure_metadata_ready(func):
    """Decorator to ensure the library's metadata exists
    """
    @wraps(func)
    def wrapper(self: 'LibraryBase', *args, **kwargs):
        if not self._metadata:
            raise LibraryError(f'Library is not ready: {self.path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


class LibraryBase:

    METADATA_FILE: str = 'metadata.bin'

    def __init__(self, lib_path: str):
        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise LibraryError(f'Invalid lib path: {lib_path}')

        # Path to the library root folder
        self.path_lib: str = lib_path
        # Path to the library's data folder
        self.path_lib_data: str = os.path.join(self.path_lib, LIB_DATA_FOLDER)
        # Path to the library's metadata file
        self.path_metadata: str = os.path.join(self.path_lib_data, LibraryBase.METADATA_FILE)
        # UUID of the library
        self.uuid: str = ''
        # In-memory metadata
        self._metadata: dict = dict()

        if not os.path.isdir(self.path_lib_data):
            os.makedirs(self.path_lib_data)

    """
    Interface methods
    """

    def lib_is_ready(self) -> bool:
        """Check if the library is ready for use
        - If not, means only the metadata file created
        """
        raise NotImplementedError()

    def delete_lib(self):
        """Delete the library
        """
        raise NotImplementedError()

    def initialize(self, force_init: bool = False, progress_reporter: Callable[[int], None] | None = None, cancel_event: Event | None = None):
        """Initialize the library

        Args:
            force_init (bool, optional): If the initialization is a force re-initialization. Defaults to False.
            reporter (Callable[[int], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.
            cancel_event (Event | None, optional): The event object to check if the initialization is cancelled. Defaults to None.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    def use_doc(self, relative_path: str, provider_type: Any, force_init: bool = False, progress_reporter: Callable[[int], None] | None = None, cancel_event: Event | None = None):
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

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    """
    Metadata file methods
    """

    def metadata_file_exists(self) -> bool:
        """Check if the metadata file exists
        """
        return os.path.isfile(self.path_metadata)

    def initialize_metadata(self, initial_metadata: dict):
        """Initialize the metadata file for the library
        - Only called when the library is under a fresh initialization (metadata file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        if not initial_metadata:
            raise LibraryError('Initial metadata must be provided for a new library')

        pickle.dump(initial_metadata,  open(self.path_metadata, 'wb'))
        self._metadata = initial_metadata
        self.uuid = initial_metadata['uuid']

    def save_metadata(self):
        """Save the metadata file for any updates
        """
        if not os.path.isfile(self.path_metadata):
            raise LibraryError(f'metadata file missing: {self.path_metadata}')

        pickle.dump(self._metadata,  open(self.path_metadata, 'wb'))

    def load_metadata(self, given_uuid: str, given_name: str):
        """Load the metadata file of the library
        """
        if not os.path.isfile(self.path_metadata):
            raise LibraryError(f'metadata file missing: {self.path_metadata}')

        try:
            content: dict = pickle.load(open(self.path_metadata, 'rb'))
        except:
            content: dict = dict()
        if not content or not content.get('uuid', None) or content['uuid'] != given_uuid:
            raise LibraryError(f'Invalid metadata file: {self.path_metadata}')

        self._metadata = content
        self.uuid = content['uuid']

        if content['name'] != given_name:
            self.change_lib_name(given_name)

    def delete_metadata(self):
        """Delete the metadata file of the library
        - Can only call on the deletion of current library
        """
        if os.path.isfile(self.path_metadata):
            os.remove(self.path_metadata)

    """
    Public methods to read library metadata info
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
        self._metadata['name'] = new_name
        self.save_metadata()

    @ensure_metadata_ready
    def change_view_style(self, new_style: str):
        if not new_style or new_style not in view_styles:
            return
        self._metadata['view_style'] = new_style
        self.save_metadata()

    @ensure_metadata_ready
    def change_sorted_by(self, new_sorted_by: str):
        if not new_sorted_by or new_sorted_by not in sorted_by_labels:
            return
        self._metadata['sorted_by'] = new_sorted_by
        self.save_metadata()

    @ensure_metadata_ready
    def change_favorite_list(self, new_list: set[str]):
        self._metadata['favorite_list'] = new_list
        self.save_metadata()

    @ensure_metadata_ready
    def change_exclusion_list(self, new_list: set[str]):
        self._metadata['exclusion_list'] = new_list
        self.save_metadata()
