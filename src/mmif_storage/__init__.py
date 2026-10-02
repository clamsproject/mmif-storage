"""

This init file imports some names to the package toplevel and sets up the
configuration.

"""


import os
from dotenv import load_dotenv

from pydantic import BaseModel

from mmif_storage.model.storage import StoragePath, peek, upload_mmif
from mmif_storage.model.storage import get_mmif_file, get_mmif_files
from mmif_storage.model.analytics import storage_analytics, storage_paths


load_dotenv()


class Config(BaseModel):
    """For now the configuration only holds the storage directory. It is trying
    to grab a default from the environment, which may or may not include a setting
    for the storage directory. The setting here is overruled when you start your
    FastAPI/Flask server with the start_api or start_www commands."""
    STORAGE_DIR: str | None = os.environ.get('STORAGE_DIR')


config = Config()


def create():
    print('under-construction')
