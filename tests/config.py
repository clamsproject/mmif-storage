"""

Environment configurations for running the tests. This is pretty much all about
making sure we know where to find the setup data needed (example storage, an
example upload file, and the list of files from the example storage to take).

Edit EXAMPLE_STORE and EMPTY_STORAGE if you want to run the tests elsewhere.

"""

# TODO: tests should probably run in a temporary directory.


from collections import namedtuple


STORAGE_SOURCE = 'src/mmif_storage/data/storage-example'
EXAMPLE_STORAGE = 'tests/tmp-storage-example'
EMPTY_STORAGE = 'tests/tmp-storage-empty'
FILE_LIST = 'tests/storage-files.txt'
UPLOAD_FILE_DUMMY = 'src/mmif_storage/data/cpb-aacip-f551104e446-clip1.mmif'
UPLOAD_FILE_SPACY = (
    'src/mmif_storage/data/storage-example'
    '/swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
    '/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e'
    '/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2'
    '/cpb-aacip-f551104e446-clip1.mmif')


Location = namedtuple('Location', 
                      ['storage_source', 'empty_storage', 'example_storage',
                       'file_list', 'upload_file_dummy', 'upload_file_spacy'])

locations = Location(
    storage_source=STORAGE_SOURCE,
    empty_storage=EMPTY_STORAGE,
    example_storage=EXAMPLE_STORAGE,
    file_list=FILE_LIST,
    upload_file_dummy=UPLOAD_FILE_DUMMY,
    upload_file_spacy=UPLOAD_FILE_SPACY)
