from pathlib import Path

from flask import Flask, Response
from flask_fontawesome import FontAwesome

from server.routes import librarian_routes, render_error_page

template_folder: str = f'{Path(__file__).parent}/templates'
static_folder: str = f'{Path(__file__).parent}/static'
flask_app = Flask("The Librarian", template_folder=template_folder, static_folder=static_folder)

flask_app.register_blueprint(librarian_routes)
fa = FontAwesome(flask_app)


@flask_app.errorhandler(404)
def not_found(e):
    return render_error_page(404, '你来到了未知的荒原')


@flask_app.after_request
def after_request(response: Response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response
