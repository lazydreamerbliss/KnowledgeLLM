import os
import uuid
from urllib.parse import unquote

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   send_file)
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from server.config import CONFIG, IS_WINDOWS
from server.utils.file import *
from server.utils.folder import is_valid_relative_path, list_folder_content

librarian_routes = Blueprint('librarian_routes', __name__)


@librarian_routes.route('/', methods=['GET'])
def homePage():
    current_library_home: str = CONFIG.get_current_lib_path()
    if not current_library_home:
        return redirect('/library/')
    return redirect('/library/')


@librarian_routes.route('/changeView')
def change_view():
    v = int(request.args.get('view', 0))
    if v == 0 or v == 1:
        view_style = v
    else:
        view_style = 0

    return jsonify({
        "txt": view_style,
    })


@librarian_routes.route('/toggleSort')
def toggle_sort():
    if CONFIG.sorted_by not in sorted_by_labels:
        CONFIG.change_sorted_by('Name')

    # On toggle sort, always get next sort type in sorted_by_labels_ordered
    next_sorted_by = sorted_by_labels_ordered[(
        sorted_by_labels_ordered.index(CONFIG.sorted_by) + 1) % len(sorted_by_labels_ordered)]
    CONFIG.change_sorted_by(next_sorted_by)
    return jsonify({
        "txt": next_sorted_by,
    })


@librarian_routes.route('/library/', methods=['GET'])
@librarian_routes.route('/library/<relative_path>', methods=['GET'])
def list_library_content(relative_path: str = ''):
    if (CONFIG.is_excluded(relative_path) or not is_valid_relative_path(relative_path)):
        return render_template('error.html',
                               error_code=404,
                               error_text='Invalid Directory Path',
                               favorite_list=CONFIG.get_favorite_list())

    target_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    if os.path.isfile(target_path):
        return redirect('/file/'+relative_path)

    try:
        dir_dict, file_dict = list_folder_content(target_path, CONFIG.sorted_by)
        if CONFIG.view_style == 0:
            var1, var2 = "DISABLED", ""
            default_view_css_1, default_view_css_2 = '', 'style=display:none'
        else:
            var1, var2 = "", "DISABLED"
            default_view_css_1, default_view_css_2 = 'style=display:none', ''
    except:
        return render_template('error.html',
                               error_code=403,
                               error_text='Permission Denied',
                               favorite_list=CONFIG.get_favorite_list())

    splitted = relative_path.split('/')
    i: int = 0
    if IS_WINDOWS:
        current_dir_html: str = f'<a style="color:black;"href="/library/{splitted[0]}">{unquote(splitted[0])}</a>'
        i = 1
    else:
        current_dir_html: str = '<a href="/library/"><img src="/static/root.png" style="height:25px;width:25px;">&nbsp;</a>'

    for p in range(i, len(splitted)):
        current_dir_html += f' / <a style="color:black;"href="/library/{"/".join(splitted[0:p+1])}">{unquote(splitted[p])}</a>'
    return render_template('library.html',
                           current_path=relative_path,
                           favorite_list=CONFIG.get_favorite_list(),
                           default_view_css_1=default_view_css_1,
                           default_view_css_2=default_view_css_2,
                           view0_button=var1,
                           view1_button=var2,
                           current_dir_html=current_dir_html,
                           dir_dict=dir_dict,
                           file_dict=file_dict,
                           sorted_label_current=CONFIG.sorted_by)


@librarian_routes.route('/file/<relative_path>', defaults={"browse": True}, methods=['GET'])
@librarian_routes.route('/download/<relative_path>', defaults={"browse": False}, methods=['GET'])
def browse_file(relative_path: str = '', browse: bool = True):
    relative_path = relative_path.replace("|HASHTAG|", "#")
    if (CONFIG.is_excluded(relative_path) or not is_valid_relative_path(relative_path)):
        return render_template('error.html',
                               error_code=404,
                               error_text='Invalid File Path',
                               favorite_list=CONFIG.get_favorite_list())

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
        media_type, _ = get_media_type_and_extension(target_path)
        if media_type != MEDIA_TYPE_UNKNOWN:
            return get_file_content(target_path, start, end)
    return send_file(target_path)


@librarian_routes.route('/downloadFolder/<relative_path>')
def download_folder(relative_path: str = ''):
    if (CONFIG.is_excluded(relative_path) or not is_valid_relative_path(relative_path)):
        return render_template('error.html',
                               error_code=404,
                               error_text='Invalid Directory Path',
                               favorite_list=CONFIG.get_favorite_list())

    target_path: str = os.path.join(CONFIG.get_current_lib_path(), relative_path)
    zip_filename: str = f'{uuid.uuid4()}.zip'
    zip_file_path: str = os.path.join(target_path, zip_filename)
    try:
        zip_directory(target_path, zip_file_path)
        return send_file(zip_file_path)
    except:
        return render_template('error.html',
                               error_code=200,
                               error_text='Permission Denied',
                               favorite_list=CONFIG.get_favorite_list())


@librarian_routes.route('/upload/', methods=['POST'])
@librarian_routes.route('/upload/<relative_path>', methods=['POST'])
def uploadFile(relative_path: str = ''):
    if (CONFIG.is_excluded(relative_path) or not is_valid_relative_path(relative_path)):
        return render_template('error.html',
                               error_code=404,
                               error_text='Invalid Directory Path',
                               favorite_list=CONFIG.get_favorite_list())

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
                           favorite_list=CONFIG.get_favorite_list())
