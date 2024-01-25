import os
import pickle
import sys
from copy import deepcopy
from pathlib import Path

from server.biz.lib_manager import *

sorted_by_labels: set[str] = {'Name', 'Date Created', 'Date Modified', 'Size'}
sorted_by_labels_ordered: list[str] = ['Name', 'Date Created', 'Date Modified', 'Size']
sorted_by_labels_CN: dict[str, str] = {
    'Name': '文件名',
    'Date Created': '创建时间',
    'Date Modified': '修改时间',
    'Size': '大小',
}
view_styles: list[str] = ['grid', 'list']
supported_formats: set[str] = {'mp4', "webm", "opgg", 'mp3', 'pdf', 'txt', 'html', 'css', 'svg', 'js', 'png', 'jpg'}


F_CATEGORY_IMAGE = 'icon'
F_CATEGORY_VIDEO = 'video'
F_CATEGORY_AUDIO = 'audio'
F_CATEGORY_UNKNOWN = 'unknown'
IS_WINDOWS = 'win32' in sys.platform or 'win64' in sys.platform


class Config:
    """This is a single threaded, single session app, so one config instance globally is enough
    """
    # Config file is a static path
    # CONFIG_FILE: str = f'../librarian.cfg'
    CONFIG_FILE: str = f'{Path(__file__).parent.parent.parent}/samples/librarian.cfg'  # test only

    def __init__(self):
        try:
            obj: dict = pickle.load(open(Config.CONFIG_FILE, 'rb'))
        except:
            obj: dict = dict()
        self.view_style: str = obj.get('view_style', 0)
        self.sorted_by: str = obj.get('sorted_by', 'Name')
        self.lib_manager: LibraryManager = LibraryManager(obj.get('lib_manager', dict()))

    def __save(self):
        pickle.dump(
            {
                'view_style': self.view_style,
                'sorted_by': self.sorted_by,
                'lib_manager': self.lib_manager.to_dict(),
            },
            open(Config.CONFIG_FILE, 'wb'))

    """
    Readonly operations
    """

    def lib_exists(self, uuid: str) -> bool:
        if not uuid:
            return False
        return uuid in self.lib_manager.libraries

    def get_library_list(self) -> list[dict[str, str]]:
        """Get the list of all libraries, sorted
        """
        res: list[dict[str, str]] = [self.lib_manager.libraries[uuid].to_dict() for uuid in self.lib_manager.libraries]
        res.sort(key=lambda x: x['name'])
        return res

    def get_library_path_list(self) -> list[str]:
        """Get the list of all libraries (lib paths), sorted
        """
        res: list[str] = [self.lib_manager.libraries[uuid].path for uuid in self.lib_manager.libraries]
        return res

    def get_favorite_list(self) -> list[str]:
        """Get the favorite list of current library
        """
        if self.lib_manager.current_lib not in self.lib_manager.favorite_list:
            self.lib_manager.favorite_list[self.lib_manager.current_lib] = list()
        return self.lib_manager.favorite_list[self.lib_manager.current_lib]

    def get_exclusion_list(self) -> set[str]:
        """Get the exclusion list of current library
        """
        if self.lib_manager.current_lib not in self.lib_manager.exclusion_list:
            self.lib_manager.exclusion_list[self.lib_manager.current_lib] = deepcopy(default_exclusion_list)
        return self.lib_manager.exclusion_list[self.lib_manager.current_lib]

    def is_excluded(self, relative_path: str) -> bool:
        """Check if a relative path is excluded in current library
        - Check both file/folder name and it's relative path
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.lib_manager.current_lib or not relative_path:
            return False

        file_or_folder_name: str = os.path.basename(relative_path)
        exclusion_list: set[str] = self.get_exclusion_list()
        return file_or_folder_name in exclusion_list or relative_path in exclusion_list

    """
    Mutating operations
    """

    def change_view_style(self, style: str):
        """Change the view style
        """
        self.view_style = style
        self.__save()

    def change_sorted_by(self, sorted_by: str):
        """Change the sort method
        """
        if sorted_by not in sorted_by_labels:
            return
        self.sorted_by = sorted_by
        self.__save()

    def switch_library(self, uuid: str):
        """Switch to another library
        """
        if not uuid or (uuid and uuid in self.lib_manager.libraries):
            self.lib_manager.current_lib = uuid
            if self.lib_manager.instanize_lib():
                self.__save()

    def add_library(self, new_lib: LibObj, switch_to: bool = True) -> bool:
        """Add a library to the config
        - Pre check must be done before calling this method
        """
        if new_lib.uuid in self.lib_manager.libraries \
                or new_lib.path in self.get_library_path_list():
            return False

        self.lib_manager.libraries[new_lib.uuid] = new_lib
        self.lib_manager.favorite_list[new_lib.uuid] = list()
        self.lib_manager.exclusion_list[new_lib.uuid] = deepcopy(default_exclusion_list)
        if switch_to:
            self.lib_manager.current_lib = new_lib.uuid
            if self.lib_manager.instanize_lib():
                self.__save()
        else:
            self.__save()
        return True

    def remove_library(self, uuid: str):
        """Remove a library from the config
        """
        if uuid in self.lib_manager.libraries:
            self.lib_manager.libraries.pop(uuid)
            self.lib_manager.favorite_list.pop(uuid, None)
            self.lib_manager.exclusion_list.pop(uuid, None)
            if uuid == self.lib_manager.current_lib:
                self.lib_manager.current_lib = ''
                self.lib_manager.instance = None
            self.__save()

    def add_favorite(self, relative_path: str):
        """Add a relative path as favorite of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.lib_manager.current_lib or not relative_path:
            return

        favorite_list: list[str] = self.get_favorite_list()
        if relative_path not in favorite_list:
            favorite_list.append(relative_path)
            self.__save()

    def remove_favorite(self, relative_path: str):
        """Remove a relative path from favorite of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.lib_manager.current_lib or not relative_path:
            return

        favorite_list: list[str] = self.get_favorite_list()
        if relative_path in favorite_list:
            favorite_list.remove(relative_path)
            self.__save()

    def add_exclusion(self, relative_path: str):
        """Add a relative path as exclusion of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.lib_manager.current_lib or not relative_path:
            return

        exclusion_list: set[str] = self.get_exclusion_list()
        if relative_path not in exclusion_list:
            exclusion_list.add(relative_path)
            self.__save()

    def remove_exclusion(self, relative_path: str):
        """Remove a relative path from exclusion of current library
        - Ensure the relative_path is stripped and heading/trailing system path separator is removed before calling
        """
        if not self.lib_manager.current_lib or not relative_path:
            return

        exclusion_list: set[str] = self.get_exclusion_list()
        if relative_path in exclusion_list:
            exclusion_list.remove(relative_path)
            self.__save()

    def get_current_lib(self) -> LibObj | None:
        """Get the current library info
        """
        return self.lib_manager.libraries.get(self.lib_manager.current_lib, None)

    def get_current_lib_path(self) -> str:
        lib: LibObj | None = self.get_current_lib()
        return lib.path if lib else ''

    def get_current_lib_type(self) -> str:
        lib: LibObj | None = self.get_current_lib()
        return lib.type if lib else ''

    def get_current_lib_uuid(self) -> str:
        lib: LibObj | None = self.get_current_lib()
        return lib.uuid if lib else ''


CONFIG: Config = Config()
