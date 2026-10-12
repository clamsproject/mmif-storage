"""

Testing the Python storage API, also includes tests for the analytics module.

An alternative for the fixture is to mock the storage location:

    from unittest.mock import patch
    @patch('mmif_storage.config.MMIF_STORAGE_DIR','data/storage-example')    

"""


import pathlib
import pytest
from collections import namedtuple

import mmif_storage
from mmif_storage import config, analytics, storage
from mmif_storage.errors import DownloadWarning, FileExistsWarning
from utils import empty_storage, example_storage

import config as test_config


WorkflowItem = namedtuple('WorkflowItem', ['app', 'version', 'properties'])


class TestEmptyStorage():

    def test_upload(self, empty_storage):
        """Upload a file and check wether it is put in the correct spot and whether
        peeking for its workflow identifier gets the correct result."""
        # TODO: must be updated once we get the input file fixed because now it does
        # not include a spacy
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(test_config.locations.upload_file_spacy) as fh:
            contents = fh.read()
            upload_result = storage.upload_mmif(contents, overwrite=False)
            assert len(upload_result.parts) == 7
            assert upload_result.parts[-1] == fname
        workflow = [WorkflowItem('dummy-app', 'v0.1', {})]
        peek_result = storage.peek(workflow)
        assert 'workflow_id' in peek_result
        #assert peek_result['workflow_id'] == wfid

    def test_rewind(self, empty_storage):
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'cpb-aacip-f551104e446-clip1'
        #mmif_file = storage.get_mmif_file(wfid, identifier, 1)
        #assert len(str(mmif_file)) == 35349


class TestExampleStorage():

    def test_storage_dir(self, example_storage):
        """Check whether the storage directory exist."""
        storage_directory = config.MMIF_STORAGE_DIR
        assert storage_directory == test_config.locations.example_storage
        assert pathlib.Path(storage_directory).is_dir()

    def test_paths(self, example_storage):
        """Check whether the number of paths is correct."""
        storage_directory = config.MMIF_STORAGE_DIR
        assert len(analytics.storage_paths()) == 3

    def test_analytics(self, example_storage):
        """Check whether the analytics seem right."""
        storage_directory = config.MMIF_STORAGE_DIR
        assert len(analytics.storage_analytics()) == 5

    def test_peek(self, example_storage):
        """Peeking into a particular directory."""
        workflow = [WorkflowItem('swt-detection', 'v8.6', {})]
        result = storage.peek(workflow)
        expected_result = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        assert result['workflow_id'] == expected_result
        assert len(result['filenames']) == 2
        assert 'cpb-aacip-f551104e446-clip1' in result['filenames']

    def test_download_succes(self, example_storage):
        """Try downloading a file that exists in the storage."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'cpb-aacip-f551104e446-clip1'
        mmif_file = storage.get_mmif_file(wfid, identifier, 1)
        assert len(str(mmif_file)) == 35349

    def test_download_failure(self, example_storage):
        """Try download using a non-existing identifier, this should raise a
        DownloadWarning."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'XXXX'
        with pytest.raises(DownloadWarning):
            storage.get_mmif_file(wfid, identifier, 1)

    def test_download_zip(self, example_storage):
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifiers = ['cpb-aacip-f551104e446-clip1']
        zip_file = storage.get_mmif_files(wfid, identifiers)
        # Using __sizeof__() instead of sys.getsizeof() to get the core size without
        # any additional garbage collector overhead. 
        zip_file_size = zip_file.__sizeof__()
        assert zip_file_size == 8626

    def test_upload(self, example_storage):
        """Upload a file and check wether it is put in the correct spot and whether
        peeking for its workflow identifier gets the correct result."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(test_config.locations.upload_file_dummy) as fh:
            contents = fh.read()
            upload_result = storage.upload_mmif(contents, overwrite=False)
            assert str(upload_result) == f'{wfid}/{fname}'
        workflow = [WorkflowItem('dummy-app', 'v0.1', {})]
        peek_result = storage.peek(workflow)
        assert peek_result['workflow_id'] == wfid

    def test_upload_again(self, example_storage):
        """Check whether uploading a file that is already there gives the correct
        exception."""
        with open(test_config.locations.upload_file_dummy) as fh:
            contents = fh.read()
            with pytest.raises(FileExistsWarning):
                storage.upload_mmif(contents, overwrite=False)


def print_path(path: pathlib.Path):
    print()
    for n, part in enumerate(path.parts):
        print(f'--- {"  "*n} {part}')
