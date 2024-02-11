import os
import uuid

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   send_file)
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from lib_manager import LibInfoObj
from server.file_utils.file import *
from server.file_utils.folder import *
from server.route_helpers import *
from singleton import lib_manager
from utils.constants.lib_constants import *
from utils.file import zip_directory

librarian_routes = Blueprint('librarian_routes', __name__)


@librarian_routes.route('/', methods=['GET'])
def homePage():
    lib_manager.use_library('')
    return render_template('home.html',
                           current_lib=None,
                           favorite_list=lib_manager.__favorite_list,
                           library_list=lib_manager.get_library_list(),
                           library_types=LIBRARY_TYPES_CN)


@librarian_routes.route('/toggleViewStyle', methods=['GET'])
def toggle_view_style():
    view_style: str = request.args.get('viewStyle', 'grid')
    lib_manager.change_view_style(view_style)
    return jsonify({})


@librarian_routes.route('/toggleSort', methods=['GET'])
def toggle_sort():
    instance: LibraryBase | None = lib_manager.instance
    if not instance:
        return render_error_page(404, '仓库不存在')

    if instance.get_sorted_by() not in SORTED_BY_LABELS:
        lib_manager.change_sorted_by('Name')

    # On toggle sort, always get next sort type in sorted_by_labels_ordered
    next_sorted_by = SORTED_BY_LABELS_ORDERED[(
        SORTED_BY_LABELS_ORDERED.index(instance.get_sorted_by()) + 1) % len(SORTED_BY_LABELS_ORDERED)]
    lib_manager.change_sorted_by(next_sorted_by)
    return jsonify({})


@librarian_routes.route('/addLibrary', methods=['POST'])
def add_library():
    lib_name: str = request.form.get('lib_name', '').strip()
    lib_path: str = request.form.get('lib_path', '').strip()
    lib_type: str = request.form.get('lib_type', '').strip()
    if not lib_type or lib_type not in LIBRARY_TYPES:
        return render_error_page(404, '无法添加仓库，仓库类型不正确')

    if not lib_name or not lib_path:
        return render_error_page(404, '无法添加仓库，仓库名或路径为空')

    lib_path = os.path.expanduser(lib_path)
    lib_path = preprocess_absolute_path(lib_path)

    # Check if path is valid
    if not os.path.isdir(lib_path) or not os.access(lib_path, os.R_OK):
        return render_error_page(404, '无法添加仓库，无法访问仓库内容')

    # Check if given absolute path is duplicated
    if lib_path in lib_manager.get_library_path_list():
        return render_error_page(404, '无法添加仓库，已存在相同路径的仓库')

    lib: LibInfoObj = LibInfoObj()
    lib.name = lib_name
    lib.uuid = str(uuid.uuid4())
    lib.path = lib_path
    lib.type = lib_type
    lib_manager.create_library(lib, switch_to=True)
    return redirect('/library/')


@librarian_routes.route('/library/', methods=['GET'])
@librarian_routes.route('/library/<path:relative_path>', methods=['GET'])
def list_library_content(relative_path: str = ''):
    instance: LibraryBase | None = lib_manager.instance
    if not instance:
        return render_error_page(404, '仓库不存在')

    # If lib uuid param is provided, means switch to and list content for another library's relative path
    # Otherwise, list content for current library with given relative path
    uuid: str | None = request.args.get('uuid', '')
    if lib_manager.lib_exists(uuid) and uuid != instance.uuid:
        lib_manager.use_library(uuid)
    if not uuid:
        uuid = instance.uuid

    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    # If relative path is a file, redirect to file page
    lib_path: str = instance.path_lib
    full_path: str = os.path.join(lib_path, relative_path)
    if os.path.isfile(full_path):
        return redirect('/file/'+relative_path)

    # List folder content
    try:
        dir_list, file_list = lib_manager.get_lib_instance().list_folder_content(relative_path)  # type: ignore
        dir_dict, file_dict = post_process_and_sort_folder_items(dir_list, file_list, instance.get_sorted_by())
    except:
        return render_error_page(404, '无法读取仓库文件')

    grid_view_button_style, list_view_button_style = "DISABLED", ""
    template_name: str = 'library_grid.html'
    if instance.get_view_style() == VIEW_STYLES[0]:
        grid_view_button_style, list_view_button_style = "DISABLED", ""
        template_name = 'library_grid.html'
        if lib_manager.get_lib_info().type == 'image':  # type: ignore
            template_name = 'library_gallery_grid.html'
    elif instance.get_view_style() == VIEW_STYLES[1]:
        grid_view_button_style, list_view_button_style = "", "DISABLED"
        template_name = 'library_list.html'
        if lib_manager.get_lib_info().type == 'image':  # type: ignore
            template_name = 'library_gallery_list.html'
    return render_template(template_name,
                           current_lib=instance.uuid,
                           parent_path=relative_path,
                           favorite_list=lib_manager.__favorite_list,
                           library_list=lib_manager.get_library_list(),
                           library_types=LIBRARY_TYPES_CN,
                           grid_view_button_style=grid_view_button_style,
                           list_view_button_style=list_view_button_style,
                           breadcrumb_path=relative_path.split('/'),
                           dir_dict=dir_dict,
                           file_dict=file_dict,
                           sorted_label_current=SORTED_BY_LABELS_CN[instance.get_sorted_by()])


@librarian_routes.route('/file/<path:relative_path>', defaults={"browse": True}, methods=['GET'])
def browse_file(relative_path: str = '', browse: bool = True):
    instance: LibraryBase | None = lib_manager.instance
    if not instance:
        return render_error_page(404, '仓库不存在')

    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    # If relative path is a folder, redirect to folder page
    lib_path: str = instance.path_lib
    full_path: str = os.path.join(lib_path, relative_path)
    if os.path.isdir(full_path):
        return redirect('/library/'+relative_path)

    # Read file content
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
        category, _ = get_file_category(full_path)
        if category != FILE_CATEGORY_UNKNOWN:
            return get_file_content(full_path, start, end)
    return send_file(full_path)


@librarian_routes.route('/downloadFolder/<relative_path>')
def download_folder(relative_path: str = ''):
    instance: LibraryBase | None = lib_manager.instance
    if not instance:
        return render_error_page(404, '仓库不存在')

    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    lib_path: str = instance.path_lib
    full_path: str = os.path.join(lib_path, relative_path)
    zip_filename: str = f'{uuid.uuid4()}.zip'
    zip_file_path: str = os.path.join(full_path, zip_filename)
    try:
        zip_directory(full_path, zip_file_path)
        return send_file(zip_file_path)
    except:
        return render_error_page(404, '无法下载文件夹')


@librarian_routes.route('/upload/', methods=['POST'])
@librarian_routes.route('/upload/<path:relative_path>', methods=['POST'])
def uploadFile(relative_path: str = ''):
    instance: LibraryBase | None = lib_manager.instance
    if not instance:
        return render_error_page(404, '仓库不存在')

    relative_path = preprocess_relative_path(relative_path)
    error_page: str | None = verify_relative_path(relative_path)
    if error_page:
        return error_page

    lib_path: str = instance.path_lib
    full_path: str = os.path.join(lib_path, relative_path)
    file_list: list[FileStorage] = request.files.getlist('file_list')
    success_count: int = 0
    msg: str = ''
    for file in file_list:
        if not file or not file.filename:
            continue
        file_path: str = os.path.join(full_path, file.filename)
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
                           favorite_list=lib_manager.__favorite_list,
                           library_list=lib_manager.get_library_list(),
                           library_types=LIBRARY_TYPES_CN,)
