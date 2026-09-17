"""

Testing the storage and its web API.

An alternative for the fixture is to mock the storage location:

    from unittest.mock import patch
    @patch('mmif_storage.config.STORAGE_DIR','data/storage-example')    

"""


import os
import sys
import pathlib
import pytest
import shutil
from collections import namedtuple

import mmif_storage
from mmif_storage.model import storage
from mmif_storage.errors import DownloadWarning, FileExistsWarning
from utils import environment


WorkflowItem = namedtuple('WorkflowItem', ['app', 'version', 'properties'])


class TestStorage():

    def test_storage_dir(self, environment):
        """Check whether the storage directory exist."""
        storage_directory = mmif_storage.config.STORAGE_DIR
        assert storage_directory == 'tests/tmp-storage'
        assert pathlib.Path(storage_directory).is_dir()

    def test_peek(self, environment):
        workflow = [WorkflowItem('swt-detection', 'v8.6', {})]
        result = storage.peek(workflow)
        expected_result = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        assert result['workflow_id'] == expected_result
        assert len(result['filenames']) == 2
        assert 'cpb-aacip-f551104e446-clip1' in result['filenames']

    def test_download_succes(self, environment):
        """Try downloading a file that exists in the storage."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'cpb-aacip-f551104e446-clip1'
        mmif_file = storage.get_mmif_file(wfid, identifier, 1)
        assert len(str(mmif_file)) == 35349

    def test_download_failure(self, environment):
        """Try download using a non-existing identifier, this should raise a
        DownloadWarning."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'XXXX'
        with pytest.raises(DownloadWarning):
            storage.get_mmif_file(wfid, identifier, 1)

    def test_download_zip(self, environment):
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifiers = ['cpb-aacip-f551104e446-clip1']
        full_path = pathlib.Path(mmif_storage.config.STORAGE_DIR) / wfid
        zip_file = storage.get_mmif_files(str(full_path), identifiers)
        # Using __sizeof__() instead of sys.getsizeof() to get the core size without
        # any additional garbage collector overhead. 
        zip_file_size = zip_file.__sizeof__()
        assert zip_file_size == 8626

    def test_upload(self, environment):
        """Upload a file and check it is put in the correct spot and also check
        whether peeking for its workflow identifier gets the correct result."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(environment.upload_file) as fh:
            contents = fh.read()
            upload_result = storage.upload_mmif(contents, overwrite=False)
            assert str(upload_result) == f'{wfid}/{fname}'
        workflow = [WorkflowItem('dummy-app', 'v0.1', {})]
        peek_result = storage.peek(workflow)
        assert peek_result['workflow_id'] == wfid

    def test_upload_again(self, environment):
        """Check whether uploading a file that is already there gives the correct
        exception."""
        with open(environment.upload_file) as fh:
            contents = fh.read()
            with pytest.raises(FileExistsWarning):
                storage.upload_mmif(contents, overwrite=False)
