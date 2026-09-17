import io
import pathlib
from fastapi.testclient import TestClient

import mmif_storage
from mmif_storage.api import app
from utils import environment


client = TestClient(app)


class TestAPI():

    def test_index(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "This is the MMIF Storage API Server." in response.text

    def test_peek(self, environment):
        wfid = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        body = {"workflow": [
                   {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post("/peek", json=body)
        assert response.status_code == 200
        assert response.json()['workflow_id'] == wfid
        assert len(response.json()['filenames']) == 2
        assert 'cpb-aacip-f551104e446-clip1' in response.json()['filenames']

    def test_peek_dummy(self, environment):
        """Since the dummy file is not uploaded yet this should get a correct workflow
        identifier but there should be no files at the workflow location."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        body = {"workflow": [
                   {"app": "dummy-app", "version": "v0.1", "properties": {}}]}
        response = client.post("/peek", json=body)
        assert response.status_code == 200
        assert response.json()['workflow_id'] == wfid
        assert len(response.json()['filenames']) == 0

    def test_download_succes(self, environment):
        """Try downloading a file that exists in the storage."""
        body = { "guid": "cpb-aacip-f551104e446-clip1",
                 "workflow": [
                     {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post('/download_file', json=body)
        assert response.status_code == 200
        assert len(response.text) == 35349

    def test_download_failure(self, environment):
        """Try download using a non-existing identifier, this should raise a
        DownloadWarning."""
        body = { "guid": "XXXXX",
                 "workflow": [
                     {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post('/download_file', json=body)
        assert "DownloadWarning" in response.json()

    def test_download_zip(self, environment):
        """Try downloading a zipfile given a list of identifiers."""
        # TODO: I am not sure how reliable the size of the response content is, may
        # need to use a range instead to make this more robust.
        body = { "guid": ["cpb-aacip-f551104e446-clip1"],
                 "workflow": [
                     {"app": "swt-detection", "version": "v8.6", "properties": {}}]}
        response = client.post('/download_files', json=body)
        assert response.status_code == 200
        assert len(response.content) == 8204

    def test_upload(self, environment):
        """Upload a file and check it is put in the correct spot and also check
        whether peeking for its workflow identifier gets the correct result."""
        wfid = 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e'
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        with open(environment.upload_file) as fh:
            contents = fh.read().encode("utf-8")
            file_payload = {
                "file": (environment.upload_file, io.BytesIO(contents), "text/plain"),
                "overwrite": "False"}
            response = client.post('/upload', files=file_payload)
            assert response.status_code == 200
            assert response.json()['destination'] == f'{wfid}/{fname}'
        body = {"workflow": [
                   {"app": "dummy-app", "version": "v0.1", "properties": {}}]}
        peek_response = client.post('/peek', json=body)
        assert peek_response.json()['workflow_id'] == wfid
        assert pathlib.Path(fname).stem in peek_response.json()['filenames']

    def test_upload_again(self, environment):
        """Check whether uploading a file that is already there gives the correct
        status."""
        with open(environment.upload_file) as fh:
            contents = fh.read().encode("utf-8")
            file_payload = {
                "file": (environment.upload_file, io.BytesIO(contents), "text/plain"),
                "overwrite": "False"}
            response = client.post('/upload', files=file_payload)
            assert response.status_code == 200
            assert response.json()['status'] == 'file-not-uploaded'
