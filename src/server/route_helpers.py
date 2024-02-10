import binascii

from flask import render_template

from singleton import lib_manager
from utils.constants.lib_constants import LIBRARY_TYPES_CN


def encode(x: str) -> str:
    return binascii.hexlify(x.encode('utf-8')).decode()


def decode(x: str) -> str:
    return binascii.unhexlify(x.encode('utf-8')).decode()


def render_error_page(error_code: int, error_text: str) -> str:
    return render_template('error.html',
                           error_code=error_code,
                           error_text=error_text,
                           current_lib=lib_manager.get_lib_uuid(),
                           favorite_list=lib_manager.__favorite_list,
                           library_list=lib_manager.get_library_list(),
                           library_types=LIBRARY_TYPES_CN)


def verify_relative_path(relative_path: str) -> str | None:
    """Verify is a relative path is accessible, return None if valid, otherwise return error page
    """
    if lib_manager.is_excluded(relative_path) or not lib_manager.is_valid_relative_path(relative_path):
        return render_error_page(404, '无法访问该路径，当前仓库没有该路径，或已被隐藏')
    return None
