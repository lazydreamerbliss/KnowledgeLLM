import argparse

from server.server import flask_app


def run_server():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-P", type=int, default=5000, help="Listening port (default: 5000)")
    parser.add_argument("--host", "-H", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--debug", "-D", default=False, required=False, action="store_true",
                        help="True when argument is provided for debug")
    args = parser.parse_args()

    debug: bool = args.debug
    host: str = args.host
    port: int = args.port
    flask_app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_server()
else:
    # Run with gunicorn
    # - See docker-compose.prod.yml `gunicorn --bind 0.0.0.0:5000 main:gunicorn_app`
    # - doc: https://docs.gunicorn.org/en/stable/run.html
    gunicorn_app = flask_app
