import os
import re
import zipfile
from mimetypes import guess_type

range_pattern: re.Pattern = re.compile(r'(?P<start>\d+)-(?P<end>\d+)')


def chunk_read(file_path: str, start: int, end: int | None = None) -> tuple[bytes, int, int, int]:
    """Read a chunk of file at given path, starting from byte position start and ending at byte position end

    Returns: (chunk of content, start, length, file_size)
    """
    if not file_path or not os.path.isfile(file_path):
        return b'', 0, 0, 0

    file_size: int = os.stat(file_path).st_size
    if end is not None:
        length: int = end + 1 - start
    else:
        length: int = file_size - start

    with open(file_path, 'rb') as f:
        f.seek(start)
        chunk: bytes = f.read(length)
    return chunk, start, length, file_size


def zip_directory(dir: str, zip_file_path: str):
    """Compress given directory into a zip file
    """
    root: str = os.path.abspath(os.path.join(dir, os.pardir))
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip:
        for parent_path, _, files in os.walk(dir):
            zip.write(parent_path, os.path.relpath(parent_path, root))
            for filename in files:
                file_path = os.path.join(parent_path, filename)
                if os.path.isfile(file_path):
                    zip.write(file_path, os.path.join(os.path.relpath(parent_path, root), filename))
