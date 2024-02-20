import os
import pickle

from env import CONFIG_FOLDER
from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.image.image_embedder import ImageEmbedder
from library.document.doc_lib import DocumentLib
from library.image.image_lib import ImageLib
from library.lib_base import LibraryBase
from tqdm import tqdm
from utils.exceptions.lib_errors import LibraryError, LibraryManagerException
from utils.task_runner import TaskRunner
from utils.tqdm_context import TqdmContext

UUID_EMPTY: str = '00000000-0000-0000-0000-000000000000'
CONFIG_FILE: str = 'librarian.cfg'


class LibInfoObj:
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

    def __init__(self, task_runner: TaskRunner):
        if not task_runner:
            raise LibraryManagerException('Task runner is not provided')

        self.task_runner: TaskRunner = task_runner
        self.__path_config: str = os.path.join(CONFIG_FOLDER, CONFIG_FILE)
        # KV: uuid -> Library
        self.__libraries: dict[str, LibInfoObj] = dict()
        # Current library instance
        self.instance: LibraryBase | None = None

        current_lib: str = ''
        try:
            if not os.path.isfile(self.__path_config):
                obj: dict = dict()
            else:
                obj: dict = pickle.load(open(self.__path_config, 'rb'))
                self.__libraries = obj['libraries']
                current_lib = obj['current_lib']
            if current_lib:
                if current_lib not in self.__libraries:
                    raise LibraryManagerException('Config file corrupted')
                self.__instanize_lib(current_lib)
        except BaseException:
            raise LibraryManagerException('Config file corrupted')

    def __save(self):
        pickle.dump(
            {
                'libraries': self.__libraries,
                'current_lib': self.instance.uuid if self.instance else ''
            },
            open(self.__path_config, 'wb'))

    """
    Get current library information
    """

    def get_current_lib_info(self) -> LibInfoObj | None:
        """Get the general info of current library
        """
        if not self.instance:
            return None
        return self.__libraries[self.instance.uuid]

    def lib_exists(self, uuid: str) -> bool:
        return uuid in self.__libraries

    def get_library_list(self) -> list[LibInfoObj]:
        """Get the list of all existing libraries, sorted
        """
        res: list[LibInfoObj] = [self.__libraries[uuid] for uuid in self.__libraries]
        res.sort(key=lambda x: x.name)
        return res

    def get_library_path_list(self) -> list[str]:
        """Get the list of all libraries (lib paths), sorted
        """
        res: list[str] = [self.__libraries[uuid].path for uuid in self.__libraries]
        return res

    """
    Manager operations for managing current library
    """

    def use_library(self, uuid: str) -> bool:
        """Switch to another library with given UUID
        """
        if uuid and uuid in self.__libraries:
            if self.__instanize_lib(uuid):
                self.__save()
                return True
        return False

    def create_library(self, new_lib: LibInfoObj, switch_to: bool = False):
        """Add a library to the manager, this only write the library info to config file unless the switch_to flag is set
        - Pre check to params must be done before calling this method
        """
        if new_lib.uuid in self.__libraries or new_lib.path in self.get_library_path_list():
            if new_lib.uuid in self.__libraries and new_lib.path == self.__libraries[new_lib.uuid].path:
                # If the new library's same UUID and and same path all matched, just do instanize and return
                tqdm.write(f'Library with same UUID and path already created, library name: {new_lib.name}')
                return
            raise LibraryManagerException('Library with same UUID or path already exists')

        self.__libraries[new_lib.uuid] = new_lib
        if switch_to:
            if self.__instanize_lib(new_lib.uuid):
                self.__save()
        else:
            self.__save()

    def demolish_library(self):
        """Demolish current library
        """
        if not self.instance:
            raise LibraryManagerException('Only an active library can be deleted')

        uuid: str = self.instance.uuid
        with TqdmContext(f'Demolishing library: {self.__libraries[uuid]}...', 'Done'):
            self.instance.demolish()
            self.instance = None
            self.__libraries.pop(uuid)
            self.__favorite_list = set()
            self.__save()

    def change_name(self, new_name: str):
        """Change library name for both library instance and the config file of manager
        """
        if not self.instance or not new_name:
            return

        obj: LibInfoObj | None = self.get_current_lib_info()
        if not obj:
            return

        self.instance.change_lib_name(new_name)
        obj.name = new_name
        self.__save()

    def change_view_style(self, new_style: str):
        """Change view style for both library instance and the config file of manager
        """
        if not self.instance or not new_style:
            return

        obj: LibInfoObj | None = self.get_current_lib_info()
        if not obj:
            return

        self.instance.change_view_style(new_style)
        self.__save()

    def change_sorted_by(self, new_sorted_by: str):
        """Change sorted by for both library instance and the config file of manager
        """
        if not self.instance or not new_sorted_by:
            return

        obj: LibInfoObj | None = self.get_current_lib_info()
        if not obj:
            return

        self.instance.change_sorted_by(new_sorted_by)
        self.__save()

    """
    Library operations
    """

    def __instanize_lib(self, lib_uuid: str) -> bool:
        """Build instance for current active library and load library metadata

        Return True if the instanization is succeeded, otherwise False
        """
        if self.instance and self.instance.uuid == lib_uuid:
            return True

        self.instance = None
        if lib_uuid in self.__libraries:
            try:
                obj: LibInfoObj = self.__libraries[lib_uuid]
                if obj.type == 'image':
                    self.instance = ImageLib(obj.path, obj.name, obj.uuid, local_mode=True)
                elif obj.type == 'video':
                    pass
                elif obj.type == 'document':
                    self.instance = DocumentLib(obj.path, obj.name, obj.uuid)
                elif obj.type == 'general':
                    pass
                return True
            except Exception as e:
                tqdm.write(f'Library instanization failed, error: {e}')
                return False
        return False

    def make_library_ready(self, **kwargs) -> str:
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
            if self.instance.is_ready():
                return UUID_EMPTY

            self.instance.set_embedder(ImageEmbedder())
            # The phase count is 1 for image library's initialization task
            task_id: str = self.task_runner.submit_task(self.instance.full_scan, None, True, True, 1,
                                                        force_init=kwargs.get('force_init', False))
            return task_id

        # Document library case
        if isinstance(self.instance, DocumentLib):
            if not kwargs or 'relative_path' not in kwargs or 'provider_type' not in kwargs \
                    or not kwargs['relative_path'] or not kwargs['provider_type']:
                raise LibraryManagerException('Invalid parameters for DocumentLib')

            if self.instance.lib_is_ready_on_current_doc(kwargs['relative_path']):
                return UUID_EMPTY

            relative_path: str = kwargs['relative_path']
            relative_path = relative_path.lstrip(os.path.sep)
            lite_mode: bool = kwargs.get('lite_mode', False)
            self.instance.set_embedder(DocEmbedder(lite_mode=lite_mode))
            # The phase count is 2 for document library's initialization task
            task_id: str = self.task_runner.submit_task(self.instance.use_doc, None, True, True, 2,
                                                        relative_path=relative_path,
                                                        provider_type=kwargs['provider_type'],
                                                        force_init=kwargs.get('force_init', False))
            return task_id

        # And more...
        # TODO: Add more library types here

        raise LibraryManagerException('Library type not supported')
