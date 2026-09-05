import os
from dotenv import load_dotenv
from flask import Flask


load_dotenv()

STORAGE_DIR = os.environ.get('STORAGE_DIR')


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    register_blueprints(app)
    return app


def register_blueprints(app: Flask):
    from mmif_storage.www import bp as bp_www
    app.register_blueprint(bp_www)
