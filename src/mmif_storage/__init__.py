import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask


load_dotenv()

DATABASE = Path(__file__).parent / 'database.db'
ASSET_DIR = os.environ.get('ASSET_DIR')
STORAGE_DIR = os.environ.get('STORAGE_DIR')
BUILD_DB = bool(int(os.environ.get('BUILD_DB')))
DEVELOPER_MODE = bool(int(os.environ.get('DEVELOPER_MODE')))


def create_app(build_db=BUILD_DB, developer_mode=DEVELOPER_MODE):

    from mmif_storage.model.database import initialize_database
    
    app = Flask(__name__)
    app.config.from_prefixed_env()
    register_blueprints(app, developer_mode)
    initialize_database(build_db)

    @app.cli.command("create-db")
    def create_db():
        """Create the assets database and populate it."""
        initialize_database(populate=True)
        print('Assets database created and populated')

    return app


def register_blueprints(app: Flask, developer_mode: bool):

    from mmif_storage.www import bp as bp_www
    from mmif_storage.routes.home import bp as bp_home
    from mmif_storage.routes.assets import bp as bp_assets
    from mmif_storage.routes.analytics import bp as bp_analytics
    from mmif_storage.routes.upload import bp as bp_upload
    from mmif_storage.routes.download import bp as bp_download
    from mmif_storage.experiments import bp as bp_experiments

    app.register_blueprint(bp_www)
    app.register_blueprint(bp_home)
    app.register_blueprint(bp_assets)
    app.register_blueprint(bp_analytics)
    app.register_blueprint(bp_upload)
    app.register_blueprint(bp_download)
    if developer_mode:
        app.register_blueprint(bp_experiments)
