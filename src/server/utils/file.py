import os
import re
import zipfile
from mimetypes import guess_type

from flask import Response

from server.config import *

range_pattern: re.Pattern = re.compile(r'(?P<start>\d+)-(?P<end>\d+)')


def __read_chunk(file_path: str, start: int, end: int | None = None) -> tuple[bytes, int, int, int]:
    """Read a chunk of file at given path, starting from byte position start and ending at byte position end

    Returns: chunk, start, length, file_size
    """
    file_size: int = os.stat(file_path).st_size
    if end is not None:
        length: int = end + 1 - start
    else:
        length: int = file_size - start

    with open(file_path, 'rb') as f:
        f.seek(start)
        chunk: bytes = f.read(length)
    return chunk, start, length, file_size


def get_file_content(file_path: str, start: int = 0, end: int | None = None) -> Response:
    """Get file content at given path, with range header support
    - Read full file if no range header is provided
    """
    mimetype, _ = guess_type(file_path)
    chunk, start, length, file_size = __read_chunk(file_path, start, end)
    res = Response(chunk, 206, mimetype=mimetype, content_type=mimetype, direct_passthrough=True)
    res.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return res


def get_media_type_and_extension(file_path: str) -> tuple[str, str]:
    """Return the media type and file extension of give file on either image, video or audio
    """
    _, extension = os.path.splitext(file_path)
    media_type: str = MEDIA_TYPE_UNKNOWN
    if not extension:
        return media_type, extension

    extension: str = extension.lower()[1:]
    if extension in image_types:
        media_type = MEDIA_TYPE_IMAGE
    elif extension in video_types:
        media_type = MEDIA_TYPE_VIDEO
    elif extension in audio_types:
        media_type = MEDIA_TYPE_AUDIO
    return media_type, extension


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


def zip_directory(dir: str, zip_file_path: str):
    """Compress given directory into a zip file
    """
    root: str = os.path.abspath(os.path.join(dir, os.pardir))
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip:
        for current_path, _, files in os.walk(dir):
            zip.write(current_path, os.path.relpath(current_path, root))
            for filename in files:
                file_path = os.path.join(current_path, filename)
                if os.path.isfile(file_path):
                    zip.write(file_path, os.path.join(os.path.relpath(current_path, root), filename))
