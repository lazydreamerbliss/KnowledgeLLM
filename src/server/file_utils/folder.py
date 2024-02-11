import os
import re
from typing import Any

from library.lib_item import DirectoryItem, FileItem
from server.file_utils.file import humanized_size
from singleton import lib_manager
from utils.constants.file_constants import FILE_ICON_MAPPING
from utils.constants.lib_constants import SORTED_BY_LABELS

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
    if not absolute_path:
        return absolute_path
    absolute_path = absolute_path.strip()
    if not absolute_path:
        return absolute_path

    absolute_path = absolute_path.rstrip(os.path.sep)
    return decode_hash_tag(absolute_path)


def preprocess_relative_path(relative_path: str) -> str:
    """Preprocess relative path, remove all heading/trailing system separators, and replace hash tags
    """
    if not relative_path:
        return relative_path
    relative_path = relative_path.strip()
    if not relative_path:
        return relative_path

    relative_path = relative_path.rstrip(os.path.sep).lstrip(os.path.sep)
    return decode_hash_tag(relative_path)


def __DirectoryItem_post_process(item: DirectoryItem) -> dict[str, Any]:
    if not item:
        return {}

    display_length: int = DISPLAY_NAME_LENGTH_GRID if lib_manager.get_lib_view_style() == 'grid' else DISPLAY_NAME_LENGTH_LIST
    return {
        'display_name': f'{item.name[0:display_length]}...' if len(item.name) > display_length else item.name,
        'name': item.name,
        'url': encode_hash_tag(item.name),
        'parent_path': encode_hash_tag(item.parent_path),
        'icon': '/icons/folder5.png',
        'dtc': item.dtc,
        'dtm': item.dtm,
        'size': '-',
    }


def __FileItem_post_process(item: FileItem) -> dict[str, Any]:
    if not item:
        return {}

    f_icon: str = ''
    if item.extension:
        for icon in FILE_ICON_MAPPING:
            extension_group: set[str] = FILE_ICON_MAPPING[icon]
            if item.extension in extension_group:
                f_icon = f'icons/file_type/{icon}'
                break
    if not f_icon:
        f_icon = 'icons/file_type/unknown.png'

    display_length: int = DISPLAY_NAME_LENGTH_GRID if lib_manager.get_lib_view_style() == 'grid' else DISPLAY_NAME_LENGTH_LIST
    display_length = DISPLAY_NAME_LENGTH_GRID if lib_manager.get_lib_type() == 'image' else display_length
    return {
        'display_name': f'{item.name[0:display_length]}...' if len(item.name) > display_length else item.name,
        'name': item.name,
        'url': encode_hash_tag(item.name),
        'parent_path': encode_hash_tag(item.parent_path),
        'icon': f_icon,
        'dtc': item.dtc,
        'dtm': item.dtm,
        'size': humanized_size(item.size_b),
        'size_b': item.size_b,
        'supported': item.supported,
    }


def post_process_and_sort_folder_items(dir_list: list[DirectoryItem],
                                       file_list: list[FileItem],
                                       sorted_by: str = 'Name') -> tuple[list[dict], list[dict]]:
    """Post process and sort folder items by given sort_by label
    """
    dir_list_dict: list[dict] = [__DirectoryItem_post_process(item) for item in dir_list]
    file_list_dict: list[dict] = [__FileItem_post_process(item) for item in file_list]

    sorted_by = sorted_by if sorted_by and sorted_by in SORTED_BY_LABELS else 'Name'
    key_d: str = 'display_name' if sorted_by == 'Name' \
        else 'dtc' if sorted_by == 'Date Created' \
        else 'dtm' if sorted_by == 'Date Modified' else 'display_name'
    key_f: str = 'display_name' if sorted_by == 'Name' \
        else 'dtc' if sorted_by == 'Date Created' \
        else 'dtm' if sorted_by == 'Date Modified' else 'size_b'

    dir_list_dict.sort(key=lambda x: x[key_d])
    file_list_dict.sort(key=lambda x: x[key_f])
    return dir_list_dict, file_list_dict
