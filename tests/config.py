"""

Environment configurations for running the tests. This is pretty much all about
making sure we know where to find the setup data needed (example storage, an
example upload file, and the list of files from the example storage to take).

Edit STORAGE_TEST if you want to run the tests elsewhere.

TODO: tests should probably run in a temporary directory.

"""


from collections import namedtuple


Location = namedtuple(
    'Location', ['storage_source', 'storage_test', 'file_list', 'upload_file'])

STORAGE_SOURCE = 'data/storage-example'
STORAGE_TEST = 'tests/tmp-storage'
FILE_LIST = 'tests/storage-files.txt'
UPLOAD_FILE = 'data/cpb-aacip-f551104e446-clip1.mmif'


locations = Location(
    storage_source=STORAGE_SOURCE,
    storage_test=STORAGE_TEST,
    file_list=FILE_LIST,
    upload_file=UPLOAD_FILE)
