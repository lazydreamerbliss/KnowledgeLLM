import os
import re
from datetime import datetime

from server.config import *
from server.utils.file import humanized_size


class DirectoryItem:
    def __init__(self):
        self.display_name: str = ''
        self.name: str = ''
        self.url: str = ''
        self.current_path: str = ''
        self.icon: str = ''
        self.dtc: str = ''
        self.dtm: str = ''
        self.size: str = ''

    def set_name(self, name: str):
        self.name = name
        self.display_name = f'{name[0:32]}...' if len(name) > 32 else name
        self.url = re.sub("#", "|HASHTAG|", name)

    def to_dict(self) -> dict[str, str]:
        return {
            'display_name': self.display_name,
            'name': self.name,
            'url': self.url,
            'current_path': self.current_path,
            'icon': self.icon,
            'dtc': self.dtc,
            'dtm': self.dtm,
            'size': self.size
        }


class FileItem:
    def __init__(self):
        self.display_name: str = ''
        self.name: str = ''
        self.url: str = ''
        self.current_path: str = ''
        self.icon: str = ''
        self.dtc: str = ''
        self.dtm: str = ''
        self.size: str = ''
        self.size_b: int = -1
        self.supported: bool = False

    def set_name(self, name: str):
        self.name = name
        self.display_name = f'{name[0:32]}...' if len(name) > 32 else name
        self.url = re.sub("#", "|HASHTAG|", name)

    def to_dict(self) -> dict[str, str | bool | int]:
        return {
            'display_name': self.display_name,
            'name': self.name,
            'url': self.url,
            'current_path': self.current_path,
            'icon': self.icon,
            'dtc': self.dtc,
            'dtm': self.dtm,
            'size': self.size,
            'size_b': self.size_b,
            'supported': self.supported
        }


def list_folder_content(relative_path: str, sort_by: str = 'Name') -> tuple[list[dict], list[dict]]:
    """List the content of a folder, return a tuple of directory list and file list
    """
    target_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    all_items: list[str] = os.listdir(target_path)
    dir_list: list[dict] = list()
    file_list: list[dict] = list()
    current_path: str = os.getcwd()
    for name in list(filter(lambda x: os.path.isdir(x), all_items)):
        dir_stats = os.stat(name)
        d_item: DirectoryItem = DirectoryItem()
        d_item.set_name(name)
        d_item.current_path = current_path
        d_item.icon = 'folder5.png'
        d_item.dtc = datetime.utcfromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        d_item.dtm = datetime.utcfromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        d_item.size = "-"
        dir_list.append(d_item.to_dict())

    for name in list(filter(lambda x: os.path.isfile(x), all_items)):
        f_icon: str = ''
        extension: str = os.path.splitext(name)[1]
        if extension:
            extension = extension[1:].lower()
            for icon in icon_dict:
                if extension in icon_dict[icon]:
                    f_icon = f'file_icon/{icon}'
                    break
        if not f_icon:
            f_icon = 'file_icon/unknown-icon.png'

        f_item: FileItem = FileItem()
        f_item.set_name(name)
        f_item.current_path = current_path
        f_item.icon = f_icon
        f_item.supported = extension in supported_formats
        try:
            dir_stats = os.stat(name)
            f_item.dtc = datetime.utcfromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            f_item.dtm = datetime.utcfromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            f_item.size = humanized_size(dir_stats.st_size)
            f_item.size_b = dir_stats.st_size
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

    full_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    return os.path.exists(full_path)
