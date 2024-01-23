import os
from copy import deepcopy

from library.document.doc_lib import DocumentLib
from library.image.image_lib import ImageLib
from library.lib_base import LibraryBase

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
    '__pycache__',
    'node_modules',
}


class LibObj:
    """Define a library object for server side to use
    """

    def __init__(self):
        self.name: str = ''
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
    """Manager for libraries
    """

    def __init__(self, config_obj: dict):
        # KV: uuid -> Library
        self.libraries: dict[str, LibObj] = config_obj.get('libraries', dict())
        # KV: uuid -> favorite_list
        self.favorite_list: dict[str, list[str]] = config_obj.get('favorite_list', dict())
        # KV: uuid -> exclusion_list
        self.exclusion_list: dict[str, set[str]] = config_obj.get('exclusion_list', dict())

        self.current_lib: str = config_obj.get('current_lib', '')
        self.instance: LibraryBase | None = None  # The instance of currently active library
        if self.current_lib and self.current_lib not in self.libraries:
            self.current_lib = ''
        else:
            self.instanize_lib()

    def to_dict(self) -> dict:
        return {
            'libraries': self.libraries,
            'favorite_list': self.favorite_list,
            'exclusion_list': self.exclusion_list,
            'current_lib': self.current_lib,
        }

    def instanize_lib(self) -> bool:
        self.instance = None
        if self.current_lib and self.current_lib in self.libraries:
            try:
                obj: LibObj = self.libraries[self.current_lib]
                if obj.type == 'image':
                    self.instance = ImageLib(obj.path, obj.uuid, local_mode=True)
                elif obj.type == 'video':
                    pass
                elif obj.type == 'document':
                    self.instance = DocumentLib(obj.path, obj.uuid)
                elif obj.type == 'general':
                    pass
                return True
            except:
                return False
        return False
