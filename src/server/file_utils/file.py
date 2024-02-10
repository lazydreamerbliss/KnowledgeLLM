import os
import re
from mimetypes import guess_type

from flask import Response

from utils.constants.file_constants import *
from utils.file_system.file import chunk_read

range_pattern: re.Pattern = re.compile(r'(?P<start>\d+)-(?P<end>\d+)')


def get_file_content(file_path: str, start: int = 0, end: int | None = None) -> Response:
    """Get file content at given path, with range header support
    - Read full file if no range header is provided
    """
    mimetype, _ = guess_type(file_path)
    chunk, start, length, file_size = chunk_read(file_path, start, end)
    res = Response(chunk, 206, mimetype=mimetype, content_type=mimetype, direct_passthrough=True)
    res.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return res


def get_file_category(file_path: str) -> tuple[str, str]:
    """Return the category and file extension of give file on either image, video or audio
    """
    _, extension = os.path.splitext(file_path)
    category: str = FILE_CATEGORY_UNKNOWN
    if not extension:
        return category, extension

    extension = extension.lower()[1:]
    if extension in T_IMAGE:
        category = FILE_CATEGORY_IMAGE
    elif extension in T_VIDEO:
        category = FILE_CATEGORY_VIDEO
    elif extension in T_AUDIO:
        category = FILE_CATEGORY_AUDIO
    return category, extension


size_suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def humanized_size(n_bytes: int) -> str:
    """Return a humanized string representation of a number of bytes
    """
    i: int = 0
    f_bytes: float = float(n_bytes)
    while f_bytes >= 1024 and i < len(size_suffixes) - 1:
        f_bytes /= 1024.
        i += 1

    res: str = ('%.2f' % f_bytes).rstrip('0').rstrip('.')
    return f'{res} {size_suffixes[i]}'
