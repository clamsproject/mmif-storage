"""

Testing the Python storage API, also includes tests for the analytics module.

An alternative for the fixture is to mock the storage location:

    from unittest.mock import patch
    @patch('mmif_storage.config.MMIF_STORAGE_DIR','data/storage-example')    

"""


import json
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
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(test_config.locations.upload_file_spacy) as fh:
            contents = fh.read()
            upload_result = storage.upload_mmif(contents, overwrite=False)
            assert len(upload_result.parts) == 10
            assert upload_result.parts[-1] == fname
        workflow = [WorkflowItem('swt-detection', 'v8.6', {}),
                    WorkflowItem('smolvlm2-captioner', 'v1.0', {}),
                    WorkflowItem('spacy-wrapper', 'v2.2', {})]
        peek_result = storage.peek(workflow)
        assert len(pathlib.Path(peek_result['workflow_id']).parts) == 9
        assert len(peek_result['filenames']) == 1

    def test_rewind_swt(self, empty_storage):
        """Retrieve descendant and rewind from swt-smolvlm-spacy to swt."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'cpb-aacip-f551104e446-clip1'
        expected_apps = {'http://apps.clams.ai/swt-detection/v8.6'}
        # Full file is 37198, after rewinding spacy and smolvlm it should be 23229
        mmif_file = storage.get_mmif_file(wfid, identifier)
        assert len(str(mmif_file)) == 23229
        # The only app in the views list should be swt
        mmif_obj = json.loads(mmif_file)
        apps = set([view['metadata']['app'] for view in mmif_obj['views']])
        assert expected_apps == apps

    def test_rewind_smolvlm2(self, empty_storage):
        """Retrieve descendant and rewind from swt-smolvlm-spacy to swt-smolvlm."""
        wfid = (
            'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
            '/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e')
        identifier = 'cpb-aacip-f551104e446-clip1'
        expected_apps = {
            'http://apps.clams.ai/swt-detection/v8.6',
            'http://apps.clams.ai/smolvlm2-captioner/v1.0'}
        mmif_file = storage.get_mmif_file(wfid, identifier)
        # Full file is 37198, after rewinding spacy it should be 24516
        assert len(str(mmif_file)) == 24516
        # The two apps in the views list should be swt and smolvlm
        mmif_obj = json.loads(mmif_file)
        apps = set([view['metadata']['app'] for view in mmif_obj['views']])
        assert expected_apps == apps


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
        mmif_file = storage.get_mmif_file(wfid, identifier)
        assert len(str(mmif_file)) == 35349

    def test_download_failure(self, example_storage):
        """Try download using a non-existing identifier, this should raise a
        DownloadWarning."""
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        identifier = 'XXXX'
        with pytest.raises(DownloadWarning):
            storage.get_mmif_file(wfid, identifier)

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
