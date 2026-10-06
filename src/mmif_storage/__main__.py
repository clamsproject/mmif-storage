"""

Code that executes when running the package, mostly for testing.

To use set the MMIF_STORAGE_DIR environment variable:

$ export MMIF_STORAGE_DIR=data/storage_example

And then do one of

$ python -m mmif_storage peek
$ python -m mmif_storage analytics
$ python -m mmif_storage paths
$ python -m mmif_storage test

The package has to be available from the directory you run this from.


"""

import sys
import json
from importlib.resources import files

import mmif_storage
from mmif_storage import config, storage, analytics


def print_json(json_obj):
    print(json.dumps(json_obj, indent=2))


def peek(storage_dir: str):
    mmif_storage.config.MMIF_STORAGE_DIR = storage_dir
    wfitem = storage.WorkflowItem(
        app="swt-detection", version="v8.6", properties={})
    print_json(storage.peek([wfitem]))


def test():
    """A few minimal tests, real testing should be done with pytest."""
    # NOTE: this may be a bit fragile since it uses the relative path inside the
    # module, I am not sure whether this will always work but it seems to work
    # fine when installing the distribution in a clean environment and a clean
    # directory. Should perhaps use importlib.
    package = mmif_storage.PACKAGE_NAME
    storage_dir = mmif_storage.EXAMPLE_STORAGE_DIR
    config.MMIF_STORAGE_DIR = files(package).joinpath(storage_dir)
    print('\n>>> storage paths\n')
    print_json(analytics.storage_paths())
    path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
    wf = [storage.WorkflowItem(app='swt-detection', version='v8.6', properties={})]
    peek_result = storage.peek(wf)
    print('\n>>> peek results\n')
    print(json.dumps(peek_result, indent=2))
    mmif_file = storage.get_mmif_file(path, 'cpb-aacip-f551104e446-clip1')
    mmif_files = storage.get_mmif_files(path, ['cpb-aacip-f551104e446-clip1'])
    print('\n>>> file retrieval (one file and zip file)\n')
    print('file size = ', len(mmif_file))
    print('zip size  = ', mmif_files.__sizeof__())
    with open("output.zip", "wb") as f:
        f.write(mmif_files.getbuffer())
    print()


if len(sys.argv) > 1:
    storage_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    mmif_storage.config.MMIF_STORAGE_DIR = storage_dir
    if sys.argv[1] == 'peek':
        peek(storage_dir)
    elif sys.argv[1] == 'analytics':
        print_json(analytics.storage_analytics())
    elif sys.argv[1] == 'paths':
        print_json(analytics.storage_paths())
    elif sys.argv[1] == 'test':
        test()
