import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from pydantic import BaseModel
from flask import Flask
import uvicorn


load_dotenv()


class Config(BaseModel):
    STORAGE_DIR: str | None = os.environ.get('STORAGE_DIR')


config = Config()


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    register_blueprints(app)
    return app


def register_blueprints(app: Flask):
    from mmif_storage.www import bp as bp_www
    app.register_blueprint(bp_www)


def start_api():
    from mmif_storage.api import app as api_app
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'directory', type=str, nargs="?", default=os.getcwd(),
        help="MMIF Storage directory, default is current directory")
    argparser.add_argument(
        '--reload', action='store_true', help="turn on automatic reload on changes")
    argparser.add_argument(
        '--port', type=int, default=8000, help="port number, default is 8000")
    args = argparser.parse_args(sys.argv[1:])
    if not Path(args.directory).is_dir():
        exit(f'Directory "{args.directory}" does not exist, exiting...')
    config.STORAGE_DIR = args.directory
    uvicorn.run("mmif_storage.api:app", port=args.port, reload=args.reload)


def start_www():
    create_app().run()
