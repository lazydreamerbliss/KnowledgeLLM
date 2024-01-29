import os
import pickle
import sys
from pathlib import Path

from library.document.doc_lib import DocumentLib
from library.image.image_lib import ImageLib
from library.lib_base import LibraryBase
from utils.exceptions.lib_errors import LibraryError, LibraryManagerException
from utils.task_runner import TaskRunner
from utils.tqdm_context import TqdmContext

IS_WINDOWS = 'win32' in sys.platform or 'win64' in sys.platform
UUID_EMPTY = '00000000-0000-0000-0000-000000000000'
CONFIG_FOLDER = f'{Path(__file__).parent.parent.parent}/samples'


class LibCreationObj:
    """Define a library object for server side to create and use
    """

    def __init__(self):
        self.name: str = ''  # The only modifiable field
        self.uuid: str = ''
        self.path: str = ''
        self.type: str = ''

    def to_dict(self) -> dict[str, str]:
        return {
            'name': self.name,
            'uuid': self.uuid,
            'path': self.path,
            'type': self.type
        }


class LibraryManager:
    """This is a single threaded, single session app, so one manager instance globally is enough
    """

    CONFIG_FILE: str = 'librarian.bin'

    def __init__(self, task_runner: TaskRunner):
        if not task_runner:
            raise LibraryManagerException('Task runner is not provided')

        self.task_runner: TaskRunner = task_runner
        config_file_path: str = os.path.join(CONFIG_FOLDER, LibraryManager.CONFIG_FILE)
        try:
            obj: dict = pickle.load(open(config_file_path, 'rb'))
        except:
            # If failed to load and the config file does not exist, it means it's the first time to run the app
            # - Otherwise the config file is corrupted
            if not os.path.isfile(config_file_path):
                obj: dict = dict()
            else:
                raise LibraryManagerException('Config file corrupted')

        # KV: uuid -> Library
        self.libraries: dict[str, LibCreationObj] = obj.get('libraries', dict())
        # Filter lists for current library
        self.favorite_list: set[str] = set()
        self.exclusion_list: set[str] = set()

        # Current library instance and UUID
        self.instance: LibraryBase | None = None  # The instance of currently active library
        current_lib: str = obj.get('current_lib', '')
        if current_lib:
            if current_lib not in self.libraries:
                raise LibraryManagerException('Config file corrupted')
            self.instanize_lib(current_lib)

    def __save(self):
        pickle.dump(
            {
                'libraries': self.libraries,
                'current_lib': self.instance.uuid if self.instance else ''
            },
            open(LibraryManager.CONFIG_FILE, 'wb'))

    """
    Get current library information
    """

    def lib_exists(self, uuid: str) -> bool:
        return uuid in self.libraries

    def get_library_list(self) -> list[dict[str, str]]:
        """Get the list of all libraries, sorted
        """
        res: list[dict[str, str]] = [self.libraries[uuid].to_dict() for uuid in self.libraries]
        res.sort(key=lambda x: x['name'])
        return res

    def get_library_path_list(self) -> list[str]:
        """Get the list of all libraries (lib paths), sorted
        """
        res: list[str] = [self.libraries[uuid].path for uuid in self.libraries]
        return res

    def is_favorited(self, relative_path: str) -> bool:
        """Check if a relative path is favorited in current library
        - Only check if path is favorited
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.instance or not relative_path or not self.favorite_list:
            return False
        return relative_path in self.favorite_list

    def is_excluded(self, relative_path: str) -> bool:
        """Check if a relative path is excluded in current library
        - Check both file/folder name and it's relative path
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.instance or not relative_path or not self.exclusion_list:
            return False

        file_or_folder_name: str = os.path.basename(relative_path)
        return file_or_folder_name in self.exclusion_list or relative_path in self.exclusion_list

    def get_current_lib(self) -> LibCreationObj | None:
        """Get the general info of current library
        """
        if not self.instance:
            return None
        return self.libraries[self.instance.uuid]

    def get_lib_name(self) -> str | None:
        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return None
        return obj.name

    def get_lib_type(self) -> str | None:
        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return None
        return obj.type

    def get_lib_uuid(self) -> str | None:
        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return None
        return obj.uuid

    def get_lib_path(self) -> str | None:
        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return None
        return obj.path

    def get_lib_view_style(self) -> str:
        if not self.instance:
            return 'grid'
        return self.instance.get_view_style()

    def get_lib_sorted_by(self) -> str:
        if not self.instance:
            return 'name'
        return self.instance.get_sorted_by()

    """
    Manager operations for managing current library
    """

    def use_library(self, uuid: str):
        """Switch to another library with given UUID
        """
        if uuid and uuid in self.libraries:
            if self.instanize_lib(uuid):
                self.__save()

    def create_library(self, new_lib: LibCreationObj, switch_to: bool = False):
        """Add a library to the manager, this only write the library info to config file unless the switch_to flag is set
        - Pre check to params must be done before calling this method
        """
        if new_lib.uuid in self.libraries or new_lib.path in self.get_library_path_list():
            raise LibraryManagerException('Library with same UUID or path already exists')

        self.libraries[new_lib.uuid] = new_lib
        if switch_to:
            if self.instanize_lib(new_lib.uuid):
                self.__save()
        else:
            self.__save()

    def demolish_library(self):
        """Demolish current library
        """
        if not self.instance:
            raise LibraryManagerException('Only an active library can be deleted')

        uuid: str = self.instance.uuid
        with TqdmContext(f'Demolishing library: {self.libraries[uuid]}...', 'Done'):
            self.instance.demolish()
            self.instance = None
            self.libraries.pop(uuid)
            self.favorite_list = set()
            self.exclusion_list = set()
            self.__save()

    def change_name(self, new_name: str):
        if not self.instance or not new_name:
            return

        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return

        self.instance.change_lib_name(new_name)
        obj.name = new_name
        self.__save()

    def change_view_style(self, new_style: str):
        if not self.instance or not new_style:
            return

        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return

        self.instance.change_view_style(new_style)
        self.__save()

    def change_sorted_by(self, new_sorted_by: str):
        if not self.instance or not new_sorted_by:
            return

        obj: LibCreationObj | None = self.get_current_lib()
        if not obj:
            return

        self.instance.change_sorted_by(new_sorted_by)
        self.__save()

    """
    Library operations
    """

    def instanize_lib(self, lib_uuid: str) -> bool:
        """Build instance for current active library and load library metadata

        Return True if the instanization is succeeded, otherwise False
        """
        if self.instance and self.instance.uuid == lib_uuid:
            return True

        self.instance = None
        if lib_uuid in self.libraries:
            try:
                obj: LibCreationObj = self.libraries[lib_uuid]
                if obj.type == 'image':
                    self.instance = ImageLib(obj.path, obj.name, obj.uuid, local_mode=True)
                elif obj.type == 'video':
                    pass
                elif obj.type == 'document':
                    self.instance = DocumentLib(obj.path, obj.name, obj.uuid)
                elif obj.type == 'general':
                    pass

                if self.instance:
                    self.favorite_list = self.instance.get_favorite_list()
                    self.exclusion_list = self.instance.get_exclusion_list()
                return True
            except:
                return False
        return False

    def get_ready(self, **kwargs) -> str | None:
        """Preheat the library instance to make it workable:
        - If the library is new, it will start initialization and load data
        - If the library is already initialized, it will load saved data to memory directly

        If UUID_EMPTY is returned, it means the library is already ready
        - Otherwise use returned task ID to track the progress of preheat

        Returns:
            str | None: Task ID
        """
        if not self.instance:
            raise LibraryManagerException('Library is not selected')

        # Image library case
        if isinstance(self.instance, ImageLib):
            if self.instance.lib_is_ready():
                return UUID_EMPTY
            task_id: str = self.task_runner.submit_task(self.instance.initialize, None, True, True,
                                                        force_init=kwargs.get('force_init', False))
            return task_id

        # Document library case
        if isinstance(self.instance, DocumentLib):
            if not kwargs or 'relative_path' not in kwargs or 'provider_type' not in kwargs:
                raise LibraryError('Invalid parameters for DocumentLib')
            if self.instance.lib_is_ready_on_current_doc(kwargs['relative_path']):
                return UUID_EMPTY
            task_id: str = self.task_runner.submit_task(self.instance.use_doc, None, True, True,
                                                        relative_path=kwargs['relative_path'],
                                                        provider_type=kwargs['provider_type'],
                                                        force_init=kwargs.get('force_init', False))
            return task_id

        # And more...
        # TODO: Add more library types here

        return None

    def add_favorite(self, relative_path: str):
        """Add a relative path as favorite of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.instance or not relative_path:
            return

        if relative_path not in self.favorite_list:
            self.favorite_list.add(relative_path)
            self.instance.change_favorite_list(self.favorite_list)

    def remove_favorite(self, relative_path: str):
        """Remove a relative path from favorite of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.instance or not relative_path:
            return

        if relative_path in self.favorite_list:
            self.favorite_list.remove(relative_path)
            self.instance.change_favorite_list(self.favorite_list)

    def add_exclusion(self, relative_path: str):
        """Add a relative path as exclusion of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.instance or not relative_path:
            return

        if relative_path not in self.exclusion_list:
            self.exclusion_list.add(relative_path)
            self.instance.change_exclusion_list(self.exclusion_list)

    def remove_exclusion(self, relative_path: str):
        """Remove a relative path from exclusion of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.instance or not relative_path:
            return

        if relative_path in self.exclusion_list:
            self.exclusion_list.remove(relative_path)
            self.instance.change_exclusion_list(self.exclusion_list)
