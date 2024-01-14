from pathlib import Path

from flask import Flask, Response, render_template
from flask_fontawesome import FontAwesome

from server.config import CONFIG
from server.routes import librarian_routes

template_folder: str = f'{Path(__file__).parent}/templates'
flask_app = Flask("librarian", template_folder=template_folder)
flask_app.register_blueprint(librarian_routes)
fa = FontAwesome(flask_app)


@flask_app.errorhandler(404)
def not_found(e):
    return render_template('error.html',
                           error_code=404,
                           error_text='Page Not Found',
                           favorite_list=CONFIG.get_favorite_list()), 404


@flask_app.after_request
def after_request(response: Response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response
