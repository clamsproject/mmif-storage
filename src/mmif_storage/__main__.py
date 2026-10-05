"""

Code that executes when running the package, mostly for testing.

To use set the MMIF_STORAGE_DIR environment variable:

$ export MMIF_STORAGE_DIR=data/storage_example

And then do one of

$ python -m mmif_storage peek
$ python -m mmif_storage analytics
$ python -m mmif_storage paths

The package has to be available from the directory you run this from.


"""

import sys
import json

import mmif_storage
from mmif_storage import storage, analytics


def print_json(json_obj):
    print(json.dumps(json_obj, indent=2))


if len(sys.argv) > 1:

    if sys.argv[1] == 'peek':
        storage_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        mmif_storage.config.MMIF_STORAGE_DIR = storage_dir
        wfitem = storage.WorkflowItem(
            app="swt-detection", version="v8.6", properties={})
        print_json(storage.peek([wfitem]))

    elif sys.argv[1] == 'analytics':
        storage_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        mmif_storage.config.MMIF_STORAGE_DIR = storage_dir
        print_json(analytics.storage_analytics())

    elif sys.argv[1] == 'paths':
        storage_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        mmif_storage.config.MMIF_STORAGE_DIR = storage_dir
        print_json(analytics.storage_paths())
