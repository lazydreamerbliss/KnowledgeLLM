import base64
import os
import zipfile
from io import BytesIO
from mimetypes import guess_extension, guess_type

from PIL import Image


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
                file_path: str = os.path.join(parent_path, filename)
                if os.path.isfile(file_path):
                    zip.write(file_path, os.path.join(os.path.relpath(parent_path, root), filename))


def open_image_as_base64(path: str) -> str | None:
    """Open given image and convert to base64 string with file type header
    """
    if not path:
        return None

    _, extension = os.path.splitext(path)
    if not extension:
        return None

    extension = extension[1:].lower()
    try:
        buffer: BytesIO = BytesIO()
        img = Image.open(path)
        img.save(buffer, format=extension)
        base64_bytes: bytes = base64.b64encode(buffer.getvalue())
        return f'data:image/{extension};base64,{base64_bytes.decode("utf-8")}'
    except Exception:
        return None


def open_base64_as_image(base64_image: str) -> tuple[Image.Image | None, str | None]:
    """Convert a base64 image to PIL image and return with file extension info
    - The given base64 string MUST have file type header
    """
    if not base64_image:
        return None, None

    try:
        file_type, _ = guess_type(base64_image)
        if not file_type:
            return None, None

        # A special case: jpg is not a valid MINE type (but it is a valid extension), convert to jpeg manually
        if file_type == 'image/jpg':
            file_type = 'image/jpeg'
        extension: str | None = guess_extension(file_type)
        if not extension:
            return None, None
    except BaseException:
        return None, None

    try:
        _, body = base64_image.split(',')
        return Image.open(BytesIO(base64.b64decode(body))), extension
    except BaseException:
        return None, None
