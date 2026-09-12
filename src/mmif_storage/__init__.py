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
    """For now the configuration only holds the storage directory. It is trying
    to grab a default from the environment, which may or may not include the
    storage directory."""
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


def parse_arguments(api=True) -> argparse.Namespace:
    port = 8000 if api else 5000
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--dir', type=str, default=os.getcwd(),
        help="MMIF Storage directory, default is the current directory")
    argparser.add_argument(
        '--port', type=int, default=port, help=f"port number, default is {port}")
    args = argparser.parse_args(sys.argv[1:])
    if not Path(args.dir).is_dir():
        exit(f'Directory "{args.dir}" does not exist, exiting...')
    return args


def start_api():
    from mmif_storage.api import app as api_app
    args = parse_arguments(api=True)
    config.STORAGE_DIR = args.dir
    uvicorn.run("mmif_storage.api:app", port=args.port)


def start_www():
    args = parse_arguments(api=False)
    config.STORAGE_DIR = args.dir
    # TODO: should replace this with gunicorn
    create_app().run()
