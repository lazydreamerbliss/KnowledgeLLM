import binascii

from flask import render_template

from library.lib_base import LibraryBase
from singleton import lib_manager
from utils.constants.lib_constants import LIBRARY_TYPES_CN


def encode(x: str) -> str:
    return binascii.hexlify(x.encode('utf-8')).decode()


def decode(x: str) -> str:
    return binascii.unhexlify(x.encode('utf-8')).decode()


def render_error_page(error_code: int, error_text: str) -> str:
    instance: LibraryBase | None = lib_manager.instance
    return render_template('error.html',
                           error_code=error_code,
                           error_text=error_text,
                           current_lib=instance.uuid if instance else None,
                           favorite_list=instance.get_favorite_list() if instance else None,
                           library_list=lib_manager.get_library_list(),
                           library_types=LIBRARY_TYPES_CN)


def verify_relative_path(relative_path: str) -> str | None:
    """Verify is a relative path is accessible, return None if valid, otherwise return error page
    """
    instance: LibraryBase | None = lib_manager.instance
    if not instance:
        return render_error_page(404, '仓库不存在')
    if not instance.is_accessible(relative_path):
        return render_error_page(404, '无法访问该路径，当前仓库没有该路径，或已被隐藏')
    return None
