"""

Import some names to the package toplevel, set up the configuration and
define the project scripts.

"""

import os
import sys
import argparse
from pathlib import Path
from importlib.resources import files

from pydantic import BaseModel

from mmif_storage import storage, analytics
from mmif_storage.storage import StoragePath, peek, upload_mmif
from mmif_storage.storage import get_mmif_file, get_mmif_files
from mmif_storage.analytics import storage_analytics, storage_paths


PACKAGE_NAME = "mmif_storage"
EXAMPLE_STORAGE_DIR = "data/storage-example"


class Config(BaseModel):
    """For now the configuration only holds the storage directory. It is trying
    to grab a default from the environment, which may or may not include a setting
    for the storage directory. The setting here is overruled when you start your
    FastAPI/Flask server with the start_api or start_www commands."""
    MMIF_STORAGE_DIR: str | None = os.environ.get('MMIF_STORAGE_DIR')


config = Config()


def parse_arguments() -> argparse.Namespace:
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '-d', type=str, required=True,
        metavar='DIRECTORY', help="output directory")
    return argparser.parse_args(sys.argv[1:])


def create_storage_example():
    """Create a directory with the storage example in src/mmif_storage/data. This
    is intended for other tools like those in mmif-storage-api and clamshack so
    they can quickly build an example for experimenting or testing, without having
    to maintain the MMIF data."""
    args = parse_arguments()
    target_dir = Path(args.d)
    if target_dir.exists():
        exit(f"Directory '{args.d}' already exists, exiting...")
    storage_example = files(PACKAGE_NAME).joinpath(EXAMPLE_STORAGE_DIR)
    for root, _dirs, fnames in storage_example.walk(on_error=print):
        for fname in fnames:
            if not Path(fname).suffix in ('.json', '.mmif'):
                continue
            in_path = root / fname
            short_path = str(in_path)[len(str(storage_example)):]
            if short_path.startswith('/'):
                short_path = short_path[1:]
            out_path = target_dir / short_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(in_path.read_text())
