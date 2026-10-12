import os
import pathlib
import shutil
import pytest
import mmif_storage

from config import locations


@pytest.fixture(scope='session')
def empty_storage(request):
    """Create the empty test storage directory and set the storage directory in
    the storage configuration. This is just for the side effects so it is not
    yielding anything."""
    shutil.rmtree(locations.empty_storage, ignore_errors=True)
    os.mkdir(locations.empty_storage)
    mmif_storage.config.MMIF_STORAGE_DIR = locations.empty_storage


@pytest.fixture(scope='session')
def example_storage(request):
    """Create the test storage directory and set the storage directory in the 
    storage configuration. Like the ficture above, this is just for the side
    effect of setting up the storage."""
    mmif_storage.config.MMIF_STORAGE_DIR = locations.example_storage
    shutil.rmtree(locations.empty_storage, ignore_errors=True)
    shutil.rmtree(locations.example_storage, ignore_errors=True)
    os.mkdir(locations.empty_storage)
    copy_files(locations.file_list, locations.storage_source, locations.example_storage)


def copy_files(file_list: str, indir: str, outdir: str):
    """Copy a list of file paths in a file from one directory to the other,
    preserving the paths.""" 
    with open(file_list) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            f_in = pathlib.Path(indir) / line.strip()
            f_out = pathlib.Path(outdir) / line.strip()
            f_out.parent.mkdir(parents=True, exist_ok=True)
            f_out.write_text(f_in.read_text())
