"""

Testing the storage and its web API.

An alternative for the fixture is to mock the storage location:

    from unittest.mock import patch
    @patch('mmif_storage.config.STORAGE_DIR','data/storage-example')    

"""


import os
import pathlib
import pytest
import shutil
from collections import namedtuple

import mmif_storage
from mmif_storage.model import storage
from mmif_storage.errors import DownloadWarning, FileExistsWarning
from utils import copy_files

#print('\n>>>', os.getcwd())
#print('>>>', mmif_storage.config.STORAGE_DIR)


WorkflowItem = namedtuple('WorkflowItem', ['app', 'version', 'properties'])

STORAGE_SOURCE = 'data/storage-example'
STORAGE_TEST = 'tests/tmp-storage'
FILE_LIST = 'tests/storage-files.txt'
UPLOAD_FILE = 'data/cpb-aacip-f551104e446-clip1.mmif'


class TestStorage():

    @pytest.fixture(scope='session')
    def storage_dir(self) -> str:
        shutil.rmtree(STORAGE_TEST, ignore_errors=True)
        mmif_storage.config.STORAGE_DIR = STORAGE_TEST
        copy_files(FILE_LIST, STORAGE_SOURCE, STORAGE_TEST)
        yield mmif_storage.config.STORAGE_DIR

    def test_storage_dir(self, storage_dir):
        """Check whether the storage directory exist."""
        storage_directory = mmif_storage.config.STORAGE_DIR
        assert storage_directory == 'tests/tmp-storage'
        assert pathlib.Path(storage_dir).is_dir()

    def test_peek(self, storage_dir):
        workflow = [WorkflowItem('swt-detection', 'v8.6', {})]
        result = storage.peek(workflow)
        expected_result = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        assert result['workflow_id'] == expected_result
        assert len(result['filenames']) == 2
        assert 'cpb-aacip-f551104e446-clip1' in result['filenames']

    def test_download_succes(self, storage_dir):
        """Try downloading a file that exists in the storage."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'cpb-aacip-f551104e446-clip1'
        mmif_file = storage.get_mmif_file(wfid, identifier, 1)
        assert len(str(mmif_file)) == 35349

    def test_download_failure(self, storage_dir):
        """Try download using a non-existing identifier, this should raise a
        DownloadWarning."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'XXXX'
        with pytest.raises(DownloadWarning):
            storage.get_mmif_file(wfid, identifier, 1)

    def test_upload(self, storage_dir):
        """Upload a file and check it is put in the correct spot and also check
        whether peeking for its workflow identifier gets the correct result."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(UPLOAD_FILE) as fh:
            contents = fh.read()
            upload_result = storage.upload_mmif(contents, overwrite=False)
            assert str(upload_result) == f'{wfid}/{fname}'
        workflow = [WorkflowItem('dummy-app', 'v0.1', {})]
        peek_result = storage.peek(workflow)
        assert peek_result['workflow_id'] == wfid

    def test_upload_again(self, storage_dir):
        """Check whether uploading a file that is already there gives the correct
        exception."""
        with open(UPLOAD_FILE) as fh:
            contents = fh.read()
            with pytest.raises(FileExistsWarning):
                storage.upload_mmif(contents, overwrite=False)
