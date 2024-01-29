import os
import re
from datetime import datetime

from utils.constants.lib_constants import *
from server.file_utils.file import humanized_size
from server.file_utils.file_constants import ICON_MAPPING
from singleton import lib_manager

HASH_TAG: str = '#'
HASH_TAG_ENCODED: str = '|&hash;|'
HASH_TAG_PATTERN: re.Pattern = re.compile(r'#')
HASH_TAG_ENCODED_PATTERN: re.Pattern = re.compile(r'\|&hash;\|')
DISPLAY_NAME_LENGTH_LIST: int = 24
DISPLAY_NAME_LENGTH_GRID: int = 16


def encode_hash_tag(text: str) -> str:
    if not text:
        return text
    return HASH_TAG_PATTERN.sub(HASH_TAG_ENCODED, text)


def decode_hash_tag(text: str) -> str:
    if not text:
        return text
    return HASH_TAG_ENCODED_PATTERN.sub(HASH_TAG, text)


def preprocess_absolute_path(absolute_path: str) -> str:
    """Preprocess absolute path, remove trailing system separators, and replace hash tags
    """
    absolute_path = absolute_path.strip()
    if not absolute_path:
        return absolute_path

    absolute_path = absolute_path.rstrip(os.path.sep)
    return decode_hash_tag(absolute_path)


def preprocess_relative_path(relative_path: str) -> str:
    """Preprocess relative path, remove all heading/trailing system separators, and replace hash tags
    """
    relative_path = relative_path.strip()
    if not relative_path:
        return relative_path

    relative_path = relative_path.rstrip(os.path.sep).lstrip(os.path.sep)
    return decode_hash_tag(relative_path)


class DirectoryItem:
    def __init__(self):
        self.display_name: str = ''  # The name to be displayed on the UI
        self.name: str = ''  # The real name
        self.url: str = ''  # The url encoded name, for navigation
        self.current_path: str = ''  # The current path of parent folder, relative to the root of current library
        self.icon: str = ''
        self.dtc: str = ''
        self.dtm: str = ''
        self.size: str = ''

    def to_dict(self) -> dict[str, str]:
        display_length: int = DISPLAY_NAME_LENGTH_GRID if lib_manager.get_lib_view_style() == 'grid' else DISPLAY_NAME_LENGTH_LIST
        return {
            'display_name': f'{self.display_name[0:display_length]}...' if len(self.display_name) > display_length else self.display_name,
            'name': self.name,
            'url': encode_hash_tag(self.name),
            'current_path': encode_hash_tag(self.current_path),
            'icon': self.icon,
            'dtc': self.dtc,
            'dtm': self.dtm,
            'size': self.size
        }


class FileItem:
    def __init__(self):
        self.display_name: str = ''  # The name to be displayed on the UI
        self.name: str = ''  # The real name
        self.url: str = ''  # The url encoded name, for navigation
        self.current_path: str = ''  # The current path of parent folder, relative to the root of current library
        self.icon: str = ''
        self.dtc: str = ''
        self.dtm: str = ''
        self.size: str = ''
        self.size_b: int = -1
        self.supported: bool = False

    def to_dict(self) -> dict[str, str | bool | int]:
        display_length: int = DISPLAY_NAME_LENGTH_GRID if lib_manager.get_lib_view_style() == 'grid' else DISPLAY_NAME_LENGTH_LIST
        display_length = DISPLAY_NAME_LENGTH_GRID if lib_manager.get_lib_type() == 'image' else display_length
        return {
            'display_name': f'{self.display_name[0:display_length]}...' if len(self.display_name) > display_length else self.display_name,
            'name': self.name,
            'url': encode_hash_tag(self.name),
            'current_path': encode_hash_tag(self.current_path),
            'icon': self.icon,
            'dtc': self.dtc,
            'dtm': self.dtm,
            'size': self.size,
            'size_b': self.size_b,
            'supported': self.supported
        }


def list_folder_content(relative_path: str, sort_by: str = 'Name') -> tuple[list[dict], list[dict]]:
    """List the content of a folder, return a tuple of directory list and file list

    Args:
        relative_path (str): The relative path of the folder to be scanned, starting from the root of current library
        sort_by (str, optional): _description_. Defaults to 'Name'.

    Returns:
        tuple[list[dict], list[dict]]: _description_
    """
    lib_path: str | None = lib_manager.get_lib_path()
    if not lib_path:
        return (list(), list())

    folder_to_be_scanned: str = os.path.join(lib_path, relative_path)
    all_items: list[str] = os.listdir(folder_to_be_scanned)
    dir_list: list[dict] = list()
    file_list: list[dict] = list()

    all_dirs: dict[str, str] = {name: os.path.join(folder_to_be_scanned, name)
                                for name in all_items if os.path.isdir(os.path.join(folder_to_be_scanned, name))}
    for name, fullpath in all_dirs.items():
        dir_relative_path: str = os.path.join(relative_path, name)
        if lib_manager.is_excluded(dir_relative_path):
            continue

        d_item: DirectoryItem = DirectoryItem()
        d_item.display_name = name
        d_item.name = name
        d_item.url = name
        d_item.current_path = relative_path
        d_item.icon = '/icons/folder5.png'
        try:
            d_stats: os.stat_result = os.stat(fullpath)
            d_item.dtc = datetime.utcfromtimestamp(d_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            d_item.dtm = datetime.utcfromtimestamp(d_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        except:
            d_item.dtc = "-"
            d_item.dtm = "-"
        d_item.size = "-"
        dir_list.append(d_item.to_dict())

    all_files: dict[str, str] = {name: os.path.join(folder_to_be_scanned, name)
                                 for name in all_items if os.path.isfile(os.path.join(folder_to_be_scanned, name))}
    for name, fullpath in all_files.items():
        file_relative_path: str = os.path.join(relative_path, name)
        if lib_manager.is_excluded(file_relative_path):
            continue

        f_icon: str = ''
        extension: str = os.path.splitext(name)[1]
        if extension:
            extension = extension[1:].lower()
            for icon in ICON_MAPPING:
                if extension in ICON_MAPPING[icon]:
                    f_icon = f'icons/file_type/{icon}'
                    break
        if not f_icon:
            f_icon = 'icons/file_type/unknown.png'

        f_item: FileItem = FileItem()
        f_item.display_name = name
        f_item.name = name
        f_item.url = name
        f_item.current_path = relative_path
        f_item.icon = f_icon
        f_item.supported = extension in supported_formats
        try:
            f_stats: os.stat_result = os.stat(fullpath)
            f_item.dtc = datetime.utcfromtimestamp(f_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            f_item.dtm = datetime.utcfromtimestamp(f_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            f_item.size = humanized_size(f_stats.st_size)
            f_item.size_b = f_stats.st_size
        except:
            f_item.dtc = "-"
            f_item.dtm = "-"
            f_item.size = "-"
            f_item.size_b = -1
        file_list.append(f_item.to_dict())

    return sort_folder_items(dir_list, file_list, sort_by)


def sort_folder_items(dir_list: list[dict], file_list: list[dict], sorted_by: str) -> tuple[list[dict], list[dict]]:
    """Sort items by given sort_by label
    """
    sorted_by = sorted_by if sorted_by and sorted_by in sorted_by_labels else 'Name'
    key_d: str = 'display_name' if sorted_by == 'Name' \
        else 'dtc' if sorted_by == 'Date Created' \
        else 'dtm' if sorted_by == 'Date Modified' else 'display_name'
    key_f: str = 'display_name' if sorted_by == 'Name' \
        else 'dtc' if sorted_by == 'Date Created' \
        else 'dtm' if sorted_by == 'Date Modified' else 'size_b'

    dir_list.sort(key=lambda x: x[key_d])
    file_list.sort(key=lambda x: x[key_f])
    return dir_list, file_list


def is_valid_relative_path(relative_path: str) -> bool:
    """Check if provided path is a sub directory/file of the current directory
    """
    if not relative_path:
        return True

    lib_path: str | None = lib_manager.get_lib_path()
    if not lib_path:
        return False
    full_path: str = os.path.join(lib_path, relative_path)
    return os.path.exists(full_path)
