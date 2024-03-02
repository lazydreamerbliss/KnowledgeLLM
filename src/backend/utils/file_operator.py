import os
import shutil
from typing import Callable, Generator

from constants.lib_constants import LIB_DATA_FOLDER
from loggers import lib_logger as LOGGER


class FileOperator:
    """
    Operator for file A/R/W/D operations
    - It works on a given root path, and all operations are relative to this root path
    - No pre-checks in methods as this is internal functionality, and expecting callers will do the work
    """

    def __init__(self, root_path: str):
        """
        Args:
            root_path (str): The root path of the file operator, all relative paths within this class are based on this root path
        """
        self.root_path: str = root_path

    def folder_walker(self,
                      relative_path: str,
                      relative_to_source_folder: bool = False) -> Generator[str, None, None]:
        """Get all files under given folder under current library

        Args:
            relative_path (str): The source folder to be scanned
            relative_to_source_folder (bool): Whether the returned relative path should be relative to
                the given source folder, rather than be relative to root path of the file operator

        Returns:
            Generator[str, None, None]: The generator of relative paths of all files under the given folder
        """
        lib_data_folder_abs_path: str = os.path.join(self.root_path, LIB_DATA_FOLDER)
        source_folder_full_path = os.path.join(self.root_path, relative_path)
        for root, _, filenames in os.walk(source_folder_full_path):
            # Skip the library data folder when relative_path is not provided
            if root == lib_data_folder_abs_path:
                continue

            for filename in filenames:
                # Relative path built from os.path.relpath does not start with os.path.sep, no need to strip
                file_abs_path: str = os.path.join(root, filename)
                if relative_to_source_folder:
                    file_relative_path: str = os.path.relpath(file_abs_path, source_folder_full_path)
                else:
                    file_relative_path: str = os.path.relpath(file_abs_path, self.root_path)
                yield file_relative_path

    def add_file(self, target_relative_path: str, source_file: str) -> bool:
        raise NotImplementedError()

    def move_file(self,
                  src_relative_path: str,
                  dest_relative_path: str,
                  is_rename: bool = False,
                  update_record: Callable[[str, str], bool] | None = None) -> bool:
        """Move a file from source relative path to destination relative path

        Args:
            src_relative_path (str): The relative path of the source file
            dest_relative_path (str): The relative path of the destination file
            is_rename (bool): Whether this method is called from rename operation
            update_record (Callable[[str, str], None] | None): The callback function to be called after the move operation
                - dest_relative_path as the first param (new relative path after move)
                - src_relative_path as the second param (old relative path before move)

        Either src_relative_path or src_full_path should be provided
        """
        if is_rename:
            dest_filename: str = os.path.basename(dest_relative_path)
            LOGGER.info(f'Rename file {src_relative_path} -> {dest_filename}')
        else:
            LOGGER.info(f'Move file: {src_relative_path} -> {dest_relative_path}')

        src_full_path = os.path.join(self.root_path, src_relative_path)
        if not os.path.isfile(src_full_path):
            LOGGER.error(f'Source file not exists: {src_relative_path}')
            return False

        dest_full_path = os.path.join(self.root_path, dest_relative_path)
        if os.path.isfile(dest_full_path):
            LOGGER.error(f'File with same name already exists on target: {dest_relative_path}')
            return False

        # Create destination folder for target file and move the file
        os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
        shutil.move(src_full_path, dest_full_path)

        # Call the updater callback if exists to update the record
        if update_record:
            update_record(dest_relative_path, src_relative_path)
        return True

    def delete_file(self, relative_path: str) -> bool:
        full_path: str = os.path.join(self.root_path, relative_path)
        if os.path.isfile(full_path):
            os.remove(full_path)
            return True
        return False

    def move_folder(self,
                    src_relative_path: str,
                    dest_relative_path: str,
                    is_rename: bool = False,
                    update_record: Callable[[str, str], bool] | None = None) -> bool:
        """Move a folder from source relative path to destination relative path
        - Walk in the folder to fetch all files
        - Move each file to its new location under destination folder
        - Delete the source folder after all files are moved

        Args:
            src_relative_path (str): The relative path of the source folder
            dest_relative_path (str): The relative path of the destination folder
            is_rename (bool): Whether this method is called from rename operation
            update_record (Callable[[str, str], None] | None): The callback function to be called after the move operation
                - dest_relative_path as the first param (new relative path after move)
                - src_relative_path as the second param (old relative path before move)
        """
        if is_rename:
            dest_foldername: str = os.path.basename(dest_relative_path)
            LOGGER.info(f'Rename folder {src_relative_path} -> {dest_foldername}')
        else:
            LOGGER.info(f'Move folder: {src_relative_path} -> {dest_relative_path}')

        src_full_path: str = os.path.join(self.root_path, src_relative_path)
        if not os.path.isdir(src_full_path):
            LOGGER.error(f'Source folder not exists: {src_relative_path}')
            return False

        dest_full_path: str = os.path.join(self.root_path, dest_relative_path)
        if os.path.isdir(dest_full_path):
            LOGGER.error(f'Folder with same name already exists on target: {dest_relative_path}')
            return False

        # file_relative_path is the relative path to the folder to be moved
        all_success: bool = True
        for file_relative_path in self.folder_walker(src_relative_path, relative_to_source_folder=True):
            src_file_relative_path: str = os.path.join(src_relative_path, file_relative_path)
            dest_file_relative_path: str = os.path.join(dest_relative_path, file_relative_path)
            all_success = self.move_file(src_relative_path=src_file_relative_path,
                                         dest_relative_path=dest_file_relative_path,
                                         is_rename=is_rename,
                                         update_record=update_record) and all_success

        if all_success:
            if is_rename:
                LOGGER.info(f'Folder renamed successfully')
            else:
                LOGGER.info(f'Folder moved successfully')
            shutil.rmtree(src_full_path)
            return True

        LOGGER.warn(f'Not all files are successfully operated, see logs for details')
        return False
