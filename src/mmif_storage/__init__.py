"""

This init file does a few different kind of things:

- Import some names to the package toplevel.
- Create the flask app and register the single blueprint.
- Provide entry points for the project scripts that start the FastAPI and Flask
  servers.

"""


import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from pydantic import BaseModel
from flask import Flask
import uvicorn

from mmif_storage.model.storage import StoragePath


load_dotenv()


class Config(BaseModel):
    """For now the configuration only holds the storage directory. It is trying
    to grab a default from the environment, which may or may not include a setting
    for the storage directory. The setting here is overruled when you start your
    FastAPI/Flask server with the start_api or start_www commands."""
    STORAGE_DIR: str | None = os.environ.get('STORAGE_DIR')


# Default host name and ports
HOSTNAME = '0.0.0.0'
FLASK_PORT = 5000
FASTAPI_PORT = 8000


config = Config()


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    register_blueprints(app)
    return app


def register_blueprints(app: Flask):
    from mmif_storage.www import bp as bp_www
    app.register_blueprint(bp_www)


def parse_arguments(api=True) -> argparse.Namespace:
    port = FASTAPI_PORT if api else FLASK_PORT
    host = HOSTNAME
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--dir', type=str, default=os.getcwd(),
        help="MMIF Storage directory, default is the current directory")
    argparser.add_argument(
        '--host',type=str, default=host, help=f'host name, default is {host}')
    argparser.add_argument(
        '--port', type=int, default=port, help=f"port number, default is {port}")
    # NOTE. There used to be a --debug option, but it was disabled for two reasons.
    # Most importantly, when running in debug mode the auto-reload loop breaks in
    # the sense that the restart ignores your original command line arguments so it
    # reverts to defaults. There are ways around this (the recommended fix is to
    # use environment variables, which I did not want to do). The other reason is
    # that we do not really need a debug mode when starting the API and browser as
    # done by start_api() and start_www().
    args = argparser.parse_args(sys.argv[1:])
    if not Path(args.dir).is_dir():
        exit(f'Directory "{args.dir}" does not exist, exiting...')
    return args


def start_api():
    from mmif_storage.api import app as api_app
    args = parse_arguments(api=True)
    config.STORAGE_DIR = args.dir
    uvicorn.run("mmif_storage.api:app", host=args.host, port=args.port)


def start_www():
    args = parse_arguments(api=False)
    config.STORAGE_DIR = args.dir
    # TODO: should replace this with gunicorn
    create_app().run(host=args.host, port=args.port)
