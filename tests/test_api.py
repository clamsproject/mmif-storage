import io
import os
import pathlib
import pytest
import shutil
from fastapi.testclient import TestClient

import mmif_storage
from mmif_storage.api import app
from utils import copy_files


STORAGE_SOURCE = 'data/storage-example'
STORAGE_TEST = 'tests/tmp-storage'
FILE_LIST = 'tests/storage-files.txt'
UPLOAD_FILE = 'data/cpb-aacip-f551104e446-clip1.mmif'


client = TestClient(app)



class TestAPI():

    @pytest.fixture(scope='session')
    def storage_dir(self) -> str:
        shutil.rmtree(STORAGE_TEST, ignore_errors=True)
        mmif_storage.config.STORAGE_DIR = STORAGE_TEST
        copy_files(FILE_LIST, STORAGE_SOURCE, STORAGE_TEST)
        yield mmif_storage.config.STORAGE_DIR

    def test_index(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "This is the MMIF Storage API Server." in response.text

    def test_peek(self, storage_dir):
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        body = {"workflow": [
                   {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post("/peek", json=body)
        assert response.status_code == 200
        assert response.json()['workflow_id'] == wfid
        assert len(response.json()['filenames']) == 2
        assert 'cpb-aacip-f551104e446-clip1' in response.json()['filenames']

    def test_peek_dummy(self, storage_dir):
        """Since the dummy file is not uploaded yet this should get a correct workflow
        identifier but there should be no files at the workflow location."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        body = {"workflow": [
                   {"app": "dummy-app", "version": "v0.1", "properties": {}}]}
        response = client.post("/peek", json=body)
        assert response.status_code == 200
        assert response.json()['workflow_id'] == wfid
        assert len(response.json()['filenames']) == 0

    def test_download_succes(self, storage_dir):
        """Try downloading a file that exists in the storage."""
        body = { "guid": "cpb-aacip-f551104e446-clip1",
                 "workflow": [
                     {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post('/download_file', json=body)
        assert response.status_code == 200
        assert len(response.text) == 35349

    def test_download_failure(self, storage_dir):
        """Try download using a non-existing identifier, this should raise a
        DownloadWarning."""
        body = { "guid": "XXXXX",
                 "workflow": [
                     {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post('/download_file', json=body)
        assert "DownloadWarning" in response.json()

    def test_upload(self, storage_dir):
        """Upload a file and check it is put in the correct spot and also check
        whether peeking for its workflow identifier gets the correct result."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(UPLOAD_FILE) as fh:
            contents = fh.read().encode("utf-8")
            file_payload = {
                "file": (UPLOAD_FILE, io.BytesIO(contents), "text/plain"),
                "overwrite": "False"}
            response = client.post('/upload', files=file_payload)
            assert response.status_code == 200
            assert response.json()['destination'] == f'{wfid}/{fname}'
        body = {"workflow": [
                   {"app": "dummy-app", "version": "v0.1", "properties": {}}]}
        peek_response = client.post('/peek', json=body)
        assert peek_response.json()['workflow_id'] == wfid
        assert pathlib.Path(fname).stem in peek_response.json()['filenames']

    def test_upload_again(self, storage_dir):
        """Check whether uploading a file that is already there gives the correct
        status."""
        with open(UPLOAD_FILE) as fh:
            contents = fh.read().encode("utf-8")
            file_payload = {
                "file": (UPLOAD_FILE, io.BytesIO(contents), "text/plain"),
                "overwrite": "False"}
            response = client.post('/upload', files=file_payload)
            assert response.status_code == 200
            assert response.json()['status'] == 'file-not-uploaded'
