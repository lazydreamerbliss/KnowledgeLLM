import os
from datetime import datetime

from singleton import lib_manager
from utils.constants.lib_constants import *


class DirectoryItem:
    def __init__(self):
        self.display_name: str = ''  # The file name to be displayed on the UI
        self.name: str = ''  # The real file name
        self.url: str = ''  # The URL encoded name, for navigation
        self.parent_path: str = ''  # The path of parent folder, relative to the root of current library
        self.icon: str = ''
        self.dtc: str = ''
        self.dtm: str = ''
        self.size: str = ''  # The humanized format of file size


class FileItem(DirectoryItem):
    def __init__(self):
        self.size_b: int = -1  # The actual size of the file in bytes
        self.extension: str = ''  # The file extension
        self.supported: bool = False


def list_folder_content(folder_relative_path: str) -> tuple[list[DirectoryItem], list[FileItem]]:
    """List the content of a folder

    Args:
        folder_relative_path (str): The relative path of the folder to be scanned, starting from the root of current library
    """
    dir_list: list[DirectoryItem] = list()
    file_list: list[FileItem] = list()
    lib_path: str | None = lib_manager.get_lib_path()
    if not lib_path:
        return dir_list, file_list

    folder_path: str = os.path.join(lib_path, folder_relative_path)
    all_folder_items: list[str] = os.listdir(folder_path)
    all_dirs: dict[str, str] = {name: os.path.join(folder_path, name)
                                for name in all_folder_items if os.path.isdir(os.path.join(folder_path, name))}
    for name, fullpath in all_dirs.items():
        dir_relative_path: str = os.path.join(folder_relative_path, name)
        if lib_manager.is_excluded(dir_relative_path):
            continue

        d_item: DirectoryItem = DirectoryItem()
        d_item.display_name = name
        d_item.name = name
        d_item.parent_path = folder_relative_path
        try:
            d_stats: os.stat_result = os.stat(fullpath)
            d_item.dtc = datetime.utcfromtimestamp(d_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            d_item.dtm = datetime.utcfromtimestamp(d_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        except:
            d_item.dtc = '-'
            d_item.dtm = '-'
        d_item.size = '-'
        dir_list.append(d_item)

    all_files: dict[str, str] = {name: os.path.join(folder_path, name)
                                 for name in all_folder_items if os.path.isfile(os.path.join(folder_path, name))}
    for name, fullpath in all_files.items():
        file_relative_path: str = os.path.join(folder_relative_path, name)
        if lib_manager.is_excluded(file_relative_path):
            continue

        _, extension = os.path.splitext(name)
        if extension:
            extension[1:].lower()
        f_item: FileItem = FileItem()
        f_item.display_name = name
        f_item.name = name
        f_item.parent_path = folder_relative_path
        f_item.extension = extension
        f_item.supported = extension in SUPPORTED_EXTENSIONS
        try:
            f_stats: os.stat_result = os.stat(fullpath)
            f_item.dtc = datetime.utcfromtimestamp(f_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            f_item.dtm = datetime.utcfromtimestamp(f_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            f_item.size = ''
            f_item.size_b = f_stats.st_size
        except:
            f_item.dtc = '-'
            f_item.dtm = '-'
            f_item.size = '-'
            f_item.size_b = -1
        file_list.append(f_item)

    return dir_list, file_list
