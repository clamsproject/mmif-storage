"""

For testing and debugging just the upload functionality.

"""

import shutil
from importlib.resources import files

from mmif_storage import config, storage, create_storage_example


TMPDIR = 'tmp-storage'

shutil.rmtree(TMPDIR, ignore_errors=True)
create_storage_example(target_dir=TMPDIR)
config.MMIF_STORAGE_DIR = TMPDIR

print('>>>', config)
mmif_file = files("mmif_storage").joinpath("data/cpb-aacip-f551104e446-clip1.mmif")

print('>>> uploading', mmif_file)
storage.upload_mmif(mmif_file.read_text())
