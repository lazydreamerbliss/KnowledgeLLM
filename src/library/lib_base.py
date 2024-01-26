import json
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable

BASIC_MANIFEST: dict = {
    'NOTE': 'DO NOT delete this file or modify it manually',
    'uuid': '',  # UUID of the library, uniquely identify the library
    'created_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'last_scanned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}


def ensure_lib_is_ready(func):
    """Decorator to ensure the library is ready before calling the function
    """
    @wraps(func)
    def wrapper(self: 'LibraryBase', *args, **kwargs):
        if not self.lib_is_ready():
            raise ValueError(f'Library is not ready: {self.path_lib}')
        return func(self, *args, **kwargs)
    return wrapper


class LibraryBase:
    LIB_DATA_FOLDER: str = '__lib_data__'
    MANIFEST_FILE: str = 'manifest.json'

    def __init__(self, lib_path: str):
        # Expand the lib path to absolute path
        lib_path = os.path.expanduser(lib_path)
        if not os.path.isdir(lib_path):
            raise ValueError(f'Invalid lib path: {lib_path}')

        self.path_lib: str = lib_path
        self.path_lib_data: str = os.path.join(self.path_lib, LibraryBase.LIB_DATA_FOLDER)
        self.path_manifest: str = os.path.join(self.path_lib_data, LibraryBase.MANIFEST_FILE)
        self.manifest: dict = dict()
        self.uuid: str = ''

        if not os.path.isdir(self.path_lib_data):
            os.makedirs(self.path_lib_data)

    def lib_is_ready(self) -> bool:
        """Check if the library is ready for use
        - If not, means only the manifest file created
        """
        raise NotImplementedError()

    def delete_lib(self):
        """Delete the library
        """
        raise NotImplementedError()

    def initialize(self, force_init: bool = False, reporter: Callable[[int], None] | None = None):
        """Initialize the library

        Args:
            force_init (bool, optional): If the initialization is a force re-initialization. Defaults to False.
            reporter (Callable[[int], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    def use_doc(self, relative_path: str, provider_type: Any, reporter: Callable[[int], None] | None = None):
        """Initialize or switch to a document under current library
        - If target document is not in manifest, then this is an uninitialized document, call __initialize_doc()
        - Otherwise load the document provider and vector DB for the target document directly
        - Target document's provider type is mandatory

        Args:
            relative_path (str): The target document's relative path based on current library
            provider_type (Type[D]): The target document's provider's type info
            reporter (Callable[[int], None] | None, optional): The reporter function which reports progress to task runner
            It accepts a integer from 0~100 to represent current progress of initialization. Defaults to None.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    def manifest_file_exists(self) -> bool:
        """Check if the manifest file exists
        """
        return os.path.isfile(self.path_manifest)

    def initialize_lib_manifest(self, initial_manifest: dict):
        """Initialize the manifest file for the library
        - Only called when the library is under a fresh initialization (manifest file not exists), the UUID should not be changed after this
        - File missing or modify the UUID manually will cause the library's index missing
        """
        if not initial_manifest:
            raise ValueError('Initial manifest must be provided for a new library')

        with open(self.path_manifest, 'w') as f:
            json.dump(initial_manifest, f)

        self.manifest = initial_manifest
        self.uuid = initial_manifest.get('uuid', '')

    def update_lib_manifest(self):
        """Update the manifest file for the library
        """
        if not os.path.isfile(self.path_manifest):
            raise ValueError(f'Manifest file missing: {self.path_manifest}')

        with open(self.path_manifest, 'w') as f:
            json.dump(self.manifest, f)

    def parse_lib_manifest(self, given_uuid: str):
        """Parse the manifest file of the library
        """
        if not os.path.isfile(self.path_manifest):
            raise ValueError(f'Manifest file missing: {self.path_manifest}')

        content: dict | None = None
        with open(self.path_manifest, 'r') as f:
            content = json.load(f)
        if not content or not content.get('uuid') or content.get('uuid') != given_uuid:
            raise ValueError(f'Invalid manifest file: {self.path_manifest}')

        self.manifest = content
        self.uuid = content.get('uuid', '')

    def delete_manifest_file(self):
        """Delete the manifest file of the library
        """
        if os.path.isfile(self.path_manifest):
            os.remove(self.path_manifest)
