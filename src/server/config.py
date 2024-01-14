import pickle
import sys
from pathlib import Path
from typing import Any

video_types: set[str] = {'mp4', 'webm', 'avi', 'mov', 'flv', 'wmv', '3gp', '3g2', 'mkv', 'mpeg', 'mpg', 'm4v', 'h264', 'h265',
                         'hevc', 'rmvb', 'rm', 'asf', 'swf', 'vob', 'ts', 'm2ts', 'divx', 'f4v', 'm2v', 'ogv', 'mxf', 'mts', 'svi', 'smi', 'm2t'}
audio_types: set[str] = {'mp3', "wav", "ogg", "mpeg", "aac", "3gpp", "3gpp2",
                         "aiff", "x-aiff", "amr", "mpga", 'oga', 'm4a', 'flac', 'aac', 'opus'}
image_types: set[str] = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
                         'svg', 'tiff', 'ico', 'jpe', 'jfif', 'pjpeg', 'pjp', 'avif', 'apng'}
code_types: set[str] = {'css', 'scss', 'html', 'py', 'js', 'cpp', 'c', 'java', 'go', 'php', 'ts', 'tsx', 'dart', 'sh', 'bat', 'h', 'hpp', 'rb', 'rs', 'cs',
                        'swift', 'kt', 'vb', 'lua', 'pl', 'm', 'r', 'sql', 'json', 'xml', 'yml', 'yaml', 'toml', 'ini', 'cfg', 'conf', 'md', 'markdown', 'rst', 'tex', 'latex', 'svg'}
sorted_by_labels: set[str] = {'Name', 'Date Created', 'Date Modified', 'Size'}
sorted_by_labels_ordered: list[str] = ['Name', 'Date Created', 'Date Modified', 'Size']
supported_formats: set[str] = {'mp4', "webm", "opgg", 'mp3', 'pdf', 'txt', 'html', 'css', 'svg', 'js', 'png', 'jpg'}
icon_dict: dict[str, set] = {
    'image-icon.png': image_types,
    'audio-icon.png': audio_types,
    'video-icon.png': video_types,
    'pdf-icon.png': {'pdf'},
    'doc-icon.png': {'docx', 'doc'},
    'txt-icon.png': {'txt'},
    'archive-icon.png': {'zip', 'rar', '7z'},
    'code-icon.png': code_types,
}

MEDIA_TYPE_IMAGE = 'icon'
MEDIA_TYPE_VIDEO = 'video'
MEDIA_TYPE_AUDIO = 'audio'
MEDIA_TYPE_UNKNOWN = 'unknown'
IS_WINDOWS = 'win32' in sys.platform or 'win64' in sys.platform


class LibraryType:
    IMAGE = 'image'
    DOCUMENT = 'document'
    GENERAL = 'general'


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
    # Config file is a static path
    #CONFIG_FILE: str = f'../config.pickle'
    CONFIG_FILE: str = f'{Path(__file__).parent.parent}/samples/config.pickle'

    def __init__(self):
        try:
            obj: dict = pickle.load(open(Config.CONFIG_FILE, 'rb'))
        except:
            obj: dict = dict()
        self.view_style: int = obj.get('view_style', 0)
        self.sorted_by: str = obj.get('sorted_by', 'Name')
        self.libraries: dict[str, dict] = obj.get('libraries', dict())
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

    def get_library_list(self) -> list[str]:
        """Get the list of libraries, sorted
        """
        res: list[str] = list(self.libraries.keys())
        res.sort()
        return res

    def switch_library(self, lib_name: str):
        """Switch to another library
        """
        if lib_name in self.libraries:
            self.current_lib = lib_name
            self.__save()

    def get_current_lib(self) -> dict:
        """Get the current library info
        """
        return self.libraries.get(self.current_lib, dict())

    def get_current_lib_path(self) -> str:
        return self.get_current_lib().get('path', '')

    def get_current_lib_type(self) -> str:
        return self.get_current_lib().get('type', '')

    def get_current_lib_name(self) -> str:
        return self.get_current_lib().get('name', '')

    def add_library(self, lib: Library, switch: bool = True) -> bool:
        """Add a library to the config
        """
        if lib.name in self.libraries:
            return False
        self.libraries[lib.name] = lib.to_dict()
        if switch:
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
        return self.favorite_list.get(self.current_lib, list())

    def add_favorite(self, relative_path: str):
        """Add a relative path as favorite of current library
        """
        if not self.current_lib:
            return

        if self.current_lib not in self.favorite_list:
            self.favorite_list[self.current_lib] = list()
        if relative_path not in self.favorite_list[self.current_lib]:
            self.favorite_list[self.current_lib].append(relative_path)
            self.__save()

    def remove_favorite(self, relative_path: str):
        """Remove a relative path from favorite of current library
        """
        if not self.current_lib:
            return

        if self.current_lib in self.favorite_list:
            if relative_path in self.favorite_list[self.current_lib]:
                self.favorite_list[self.current_lib].remove(relative_path)
                self.__save()

    def get_exclusion_list(self) -> set[str]:
        """Get the exclusion list of current library
        """
        return self.exclusion_list.get(self.current_lib, set())

    def add_exclusion(self, relative_path: str):
        """Add a relative path as exclusion of current library
        """
        if not self.current_lib:
            return

        if self.current_lib not in self.exclusion_list:
            self.exclusion_list[self.current_lib] = set()
        if relative_path not in self.exclusion_list[self.current_lib]:
            self.exclusion_list[self.current_lib].add(relative_path)
            self.__save()

    def remove_exclusion(self, relative_path: str):
        """Remove a relative path from exclusion of current library
        """
        if not self.current_lib:
            return

        if self.current_lib in self.exclusion_list:
            if relative_path in self.exclusion_list[self.current_lib]:
                self.exclusion_list[self.current_lib].remove(relative_path)
                self.__save()

    def is_excluded(self, relative_path: str) -> bool:
        """Check if a relative path is excluded in current library
        """
        if not self.current_lib:
            return False

        if self.current_lib in self.exclusion_list:
            return relative_path in self.exclusion_list[self.current_lib]
        return False

    def change_view_style(self, style: int):
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
