import binascii
import os
import uuid

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   send_file)
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from server.config import CONFIG, IS_WINDOWS
from server.file_utils.file import *
from server.file_utils.folder import *

librarian_routes = Blueprint('librarian_routes', __name__)


def encode(x):
    return binascii.hexlify(x.encode('utf-8')).decode()


def decode(x):
    return binascii.unhexlify(x.encode('utf-8')).decode()


def render_error_page(error_code: int, error_text: str) -> str:
    return render_template('error.html',
                           error_code=error_code,
                           error_text=error_text,
                           current_lib=CONFIG.get_current_lib_name(),
                           favorite_list=CONFIG.get_favorite_list(),
                           library_list=CONFIG.get_library_list(),
                           library_types=library_types_CN,)


def verify_relative_path(relative_path: str) -> str | None:
    """Verify is a relative path is accessible, return None if valid, otherwise return error page
    """
    if (CONFIG.is_excluded(relative_path) or not is_valid_relative_path(relative_path)):
        return render_error_page(404, '无法访问该路径，当前仓库没有该路径，或已被隐藏')
    return None


def preprocess_relative_path(relative_path: str) -> str:
    """Preprocess relative path, remove leading and trailing slashes, and replace slashes with backslashes on Windows
    """
    if not relative_path:
        return relative_path
    relative_path = relative_path.rstrip(os.path.sep)
    relative_path = relative_path.lstrip(os.path.sep)
    return decode_hash_tag(relative_path)


@librarian_routes.route('/', methods=['GET'])
def homePage():
    CONFIG.switch_library('')
    return render_template('home.html',
                           current_lib=CONFIG.get_current_lib_name(),
                           favorite_list=CONFIG.get_favorite_list(),
                           library_list=CONFIG.get_library_list(),
                           library_types=library_types_CN,)


@librarian_routes.route('/toggleViewStyle', methods=['GET'])
def toggle_view_style():
    view_style: str = request.args.get('viewStyle', 'grid')
    CONFIG.change_view_style(view_style)
    return jsonify({})


@librarian_routes.route('/toggleSort', methods=['GET'])
def toggle_sort():
    if CONFIG.sorted_by not in sorted_by_labels:
        CONFIG.change_sorted_by('Name')

    # On toggle sort, always get next sort type in sorted_by_labels_ordered
    next_sorted_by = sorted_by_labels_ordered[(
        sorted_by_labels_ordered.index(CONFIG.sorted_by) + 1) % len(sorted_by_labels_ordered)]
    CONFIG.change_sorted_by(next_sorted_by)
    return jsonify({})


@librarian_routes.route('/addLibrary', methods=['POST'])
def add_library():
    lib_name: str = request.form.get('lib_name', '').strip()
    lib_path: str = request.form.get('lib_path', '').strip()
    lib_path = lib_path.rstrip('\\') if IS_WINDOWS else lib_path.rstrip('/')
    lib_type: str = request.form.get('lib_type', '').strip()
    if not lib_type or lib_type not in library_types:
        return render_error_page(404, '无法添加仓库，仓库类型不正确')

    if not lib_name or not lib_path:
        return render_error_page(404, '无法添加仓库，仓库名或路径为空')

    # Check if name or path is duplicated
    if lib_name in CONFIG.libraries or lib_path in CONFIG.get_library_path_list():
        return render_error_page(404, '无法添加仓库，仓库名或路径和现有仓库重复')

    # Check if path is valid
    lib_path = os.path.expanduser(lib_path)
    if not os.path.isdir(lib_path) or not os.access(lib_path, os.R_OK):
        return render_error_page(404, '无法添加仓库，无法读取仓库内容')

    lib: Library = Library()
    lib.name = lib_name
    lib.path = lib_path
    lib.type = lib_type
    CONFIG.add_library(lib, switch_to=True)
    return redirect('/library/')


@librarian_routes.route('/library/', methods=['GET'])
@librarian_routes.route('/library/<path:relative_path>', methods=['GET'])
def list_library_content(relative_path: str = ''):
    # If lib param is provided, switch to that library, otherwise use current library
    target_lib: str = request.args.get('lib', '')
    if target_lib and target_lib in CONFIG.libraries and target_lib != CONFIG.get_current_lib_name():
        CONFIG.switch_library(target_lib)
    if not target_lib:
        target_lib = CONFIG.get_current_lib_name()

    if target_lib not in CONFIG.libraries:
        return render_error_page(404, '无法读取仓库文件')

    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    full_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    if os.path.isfile(full_path):
        return redirect('/file/'+relative_path)

    try:
        dir_dict, file_dict = list_folder_content(relative_path, CONFIG.sorted_by)
    except:
        return render_error_page(404, '无法读取仓库文件')

    grid_view_button_style, list_view_button_style = "DISABLED", ""
    template_name: str = 'library_grid.html'
    if CONFIG.view_style == view_styles[0]:
        grid_view_button_style, list_view_button_style = "DISABLED", ""
        template_name = 'library_grid.html'
        if CONFIG.get_current_lib_type() == 'image':
            template_name = 'library_gallery_grid.html'
    elif CONFIG.view_style == view_styles[1]:
        grid_view_button_style, list_view_button_style = "", "DISABLED"
        template_name = 'library_list.html'
        if CONFIG.get_current_lib_type() == 'image':
            template_name = 'library_gallery_list.html'
    return render_template(template_name,
                           current_lib=CONFIG.get_current_lib_name(),
                           current_path=relative_path,
                           favorite_list=CONFIG.get_favorite_list(),
                           library_list=CONFIG.get_library_list(),
                           library_types=library_types_CN,
                           grid_view_button_style=grid_view_button_style,
                           list_view_button_style=list_view_button_style,
                           breadcrumb_path=relative_path.split('/'),
                           dir_dict=dir_dict,
                           file_dict=file_dict,
                           sorted_label_current=sorted_by_labels_CN[CONFIG.sorted_by])


@librarian_routes.route('/file/<path:relative_path>', defaults={"browse": True}, methods=['GET'])
def browse_file(relative_path: str = '', browse: bool = True):
    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    target_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    if os.path.isdir(target_path):
        return redirect('/library/'+relative_path)

    start: int = 0
    end: int | None = None
    range_header: str | None = request.headers.get('Range', None)
    if range_header:
        match: re.Match | None = range_pattern.match(range_header)
        if not match:
            # Only return invalid when range header is provided but cannot be parsed
            return Response('Invalid range', 400)
        if match.group('start'):
            start = int(match.group('start'))
        if match.group('end'):
            end = int(match.group('end'))

    if browse:
        category, _ = get_file_category(target_path)
        if category != F_CATEGORY_UNKNOWN:
            return get_file_content(target_path, start, end)
    return send_file(target_path)


@librarian_routes.route('/downloadFolder/<relative_path>')
def download_folder(relative_path: str = ''):
    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    target_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    zip_filename: str = f'{uuid.uuid4()}.zip'
    zip_file_path: str = os.path.join(target_path, zip_filename)
    try:
        zip_directory(target_path, zip_file_path)
        return send_file(zip_file_path)
    except:
        return render_error_page(404, '无法下载文件夹')


@librarian_routes.route('/upload/', methods=['POST'])
@librarian_routes.route('/upload/<path:relative_path>', methods=['POST'])
def uploadFile(relative_path: str = ''):
    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    target_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    file_list: list[FileStorage] = request.files.getlist('file_list')
    success_count: int = 0
    msg: str = ''
    for file in file_list:
        if not file or not file.filename:
            continue
        file_path: str = os.path.join(target_path, file.filename)
        if os.path.exists(file_path) or not secure_filename(file.filename):
            msg = f'{msg}{file.filename} Failed because File Already Exists or File Type not secure<br>'
            continue
        try:
            file.save(file_path)
            msg = f'{msg}{file.filename} Uploaded<br>'
            success_count += 1
        except:
            msg = f'{msg}{file.filename} Failed<br>'

    failure_count: int = len(file_list) - success_count
    return render_template('uploadsuccess.html',
                           message=msg,
                           success_count=success_count,
                           failure_count=failure_count,
                           favorite_list=CONFIG.get_favorite_list(),
                           library_list=CONFIG.get_library_list(),
                           library_types=library_types_CN,)
