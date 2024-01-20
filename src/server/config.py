import os
import pickle
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sorted_by_labels: set[str] = {'Name', 'Date Created', 'Date Modified', 'Size'}
sorted_by_labels_ordered: list[str] = ['Name', 'Date Created', 'Date Modified', 'Size']
view_styles: list[str] = ['grid', 'list']
supported_formats: set[str] = {'mp4', "webm", "opgg", 'mp3', 'pdf', 'txt', 'html', 'css', 'svg', 'js', 'png', 'jpg'}
library_types: set[str] = {'image', 'video', 'document', 'general'}
library_types_CN: list[dict] = [
    {'name': 'image', 'cn_name': '图片库'},
    {'name': 'video', 'cn_name': '媒体库'},
    {'name': 'document', 'cn_name': '文档库'},
    {'name': 'general', 'cn_name': '综合仓库'},
]

default_exclusion_list: set[str] = {
    '$RECYCLE.BIN',
    'System Volume Information',
    'Thumbs.db',
    'desktop.ini',
    '.DS_Store',
    '.localized',
    '.git',
    '.vscode',
    '.idea',
    '.gitattributes',
    '.gitmodules',
    '.gitkeep',
    '.gitconfig',
    '.gitmessage',
    '.gitignore_global',
    '.gitattributes_global',
    '__pycache__',
    'node_modules',
    'package-lock.json',
    'yarn.lock',
}

F_CATEGORY_IMAGE = 'icon'
F_CATEGORY_VIDEO = 'video'
F_CATEGORY_AUDIO = 'audio'
F_CATEGORY_UNKNOWN = 'unknown'
IS_WINDOWS = 'win32' in sys.platform or 'win64' in sys.platform


class Library:
    """Define a library object for server to use
    - The type can be 'image', 'document' and 'general'
    """

    def __init__(self):
        self.name: str = ''
        self.path: str = ''
        self.type: str = ''

    def to_dict(self) -> dict[str, str]:
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type
        }


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
        self.libraries: dict[str, Library] = obj.get('libraries', dict())
        self.favorite_list: dict[str, list[str]] = obj.get('favorite_list', dict())
        self.exclusion_list: dict[str, set[str]] = obj.get('exclusion_list', dict())
        self.current_lib: str = obj.get('current_lib', '')
        if self.current_lib not in self.libraries:
            self.current_lib = ''

    def __to_dict(self) -> dict[str, Any]:
        return {
            'view_style': self.view_style,
            'sorted_by': self.sorted_by,
            'libraries': self.libraries,
            'favorite_list': self.favorite_list,
            'exclusion_list': self.exclusion_list,
            'current_lib': self.current_lib,
        }

    def __save(self):
        pickle.dump(self.__to_dict(), open(Config.CONFIG_FILE, 'wb'))

    def get_library_list(self) -> list[dict[str, str]]:
        """Get the list of all libraries, sorted
        """
        res: list[dict[str, str]] = [self.libraries[lib_name].to_dict() for lib_name in self.libraries]
        res.sort(key=lambda x: x['name'])
        return res

    def get_library_path_list(self) -> list[str]:
        """Get the list of all libraries (lib paths), sorted
        """
        res: list[str] = [self.libraries[lib_name].path for lib_name in self.libraries]
        return res

    def switch_library(self, lib_name: str):
        """Switch to another library
        """
        if not lib_name or (lib_name and lib_name in self.libraries):
            self.current_lib = lib_name
            self.__save()

    def get_current_lib(self) -> Library | None:
        """Get the current library info
        """
        return self.libraries.get(self.current_lib, None)

    def get_current_lib_path(self) -> str:
        lib: Library | None = self.get_current_lib()
        return lib.path if lib else ''

    def get_current_lib_type(self) -> str:
        lib: Library | None = self.get_current_lib()
        return lib.type if lib else ''

    def get_current_lib_name(self) -> str:
        lib: Library | None = self.get_current_lib()
        return lib.name if lib else ''

    def add_library(self, lib: Library, switch_to: bool = True) -> bool:
        """Add a library to the config
        """
        if lib.name in self.libraries:
            return False
        self.libraries[lib.name] = lib
        if switch_to:
            self.current_lib = lib.name
        self.__save()
        return True

    def remove_library(self, lib_name: str):
        """Remove a library from the config
        """
        if lib_name in self.libraries:
            self.libraries.pop(lib_name)
            self.favorite_list.pop(lib_name, None)
            self.exclusion_list.pop(lib_name, None)
            self.__save()

    def get_favorite_list(self) -> list[str]:
        """Get the favorite list of current library
        """
        if self.current_lib not in self.favorite_list:
            self.favorite_list[self.current_lib] = list()
            self.__save()
        return self.favorite_list[self.current_lib]

    def add_favorite(self, relative_path: str):
        """Add a relative path as favorite of current library
        """
        if not self.current_lib or not relative_path:
            return

        favorite_list: list[str] = self.get_favorite_list()
        if relative_path not in favorite_list:
            favorite_list.append(relative_path)
            self.__save()

    def remove_favorite(self, relative_path: str):
        """Remove a relative path from favorite of current library
        """
        if not self.current_lib or not relative_path:
            return

        favorite_list: list[str] = self.get_favorite_list()
        if relative_path in favorite_list:
            favorite_list.remove(relative_path)
            self.__save()

    def get_exclusion_list(self) -> set[str]:
        """Get the exclusion list of current library
        """
        if self.current_lib not in self.exclusion_list:
            self.exclusion_list[self.current_lib] = deepcopy(default_exclusion_list)
            self.__save()
        return self.exclusion_list[self.current_lib]

    def add_exclusion(self, relative_path: str):
        """Add a relative path as exclusion of current library
        """
        if not self.current_lib or not relative_path:
            return

        exclusion_list: set[str] = self.get_exclusion_list()
        if relative_path not in exclusion_list:
            exclusion_list.add(relative_path)
            self.__save()

    def remove_exclusion(self, relative_path: str):
        """Remove a relative path from exclusion of current library
        """
        if not self.current_lib or not relative_path:
            return

        exclusion_list: set[str] = self.get_exclusion_list()
        if relative_path in exclusion_list:
            exclusion_list.remove(relative_path)
            self.__save()

    def is_excluded(self, relative_path: str) -> bool:
        """Check if a relative path is excluded in current library
        """
        if not self.current_lib or not relative_path:
            return False

        file_or_folder_name: str = os.path.basename(relative_path)
        exclusion_list: set[str] = self.get_exclusion_list()
        return file_or_folder_name in exclusion_list or relative_path in exclusion_list

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


CONFIG: Config = Config()
