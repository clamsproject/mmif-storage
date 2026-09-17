import pathlib
import shutil
import pytest
import mmif_storage

from config import locations


@pytest.fixture(scope='session')
def environment(request):
    """Create the test storage directory and set the storage directory in the 
    storage configuration."""
    shutil.rmtree(locations.storage_test, ignore_errors=True)
    mmif_storage.config.STORAGE_DIR = locations.storage_test
    copy_files(locations.file_list, locations.storage_source, locations.storage_test)
    yield locations


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
