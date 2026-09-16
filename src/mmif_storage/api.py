"""

Now has the following functionality from the old Flask server:

- peek
- analytics
- file download (single file)
- file download (zipfile)
- file upload

Need to add all the search functionality from the Shack, which will require moving
some code from the clamshack to this repository in mmif_storage.model.

"""

import os
import io
from typing import Dict, List, Any

from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, PlainTextResponse

from mmif import View

import mmif_storage
from mmif_storage.model import storage, analytics
from mmif_storage.errors import DownloadWarning, FileExistsWarning


app = FastAPI()


class WorkflowItem(BaseModel):
    app: str
    version: str
    properties: dict


class Workflow(BaseModel):
    workflow: List[WorkflowItem]


class PeekResult(BaseModel):
    workflow_id: str
    filenames: list


class DownloadRequest(BaseModel):
    guid: str | list[str]
    workflow_id: str | None = None
    workflow: List[WorkflowItem] | None = []


class DownloadFileRequest(DownloadRequest):
    guid: str


class DownloadFilesRequest(DownloadRequest):
    guid: list[str]


class MmifFile(BaseModel):
    metadata: dict
    documents: list[dict]
    views: list[dict]

    model_config = ConfigDict(arbitrary_types_allowed=True)


@app.get('/', tags=["Intro"])
def index():
    """Landing page for the API"""
    text = \
        "\nThis is the MMIF Storage API Server.\n\n" \
        + "Use\n\n    GET /help\n\nfor a list of routes.\n\n"
    return PlainTextResponse(text)


@app.get('/help', tags=["Intro"])
def help():
    """Documentation for all routes"""
    help_string = io.StringIO("")
    for path_url, path_data in app.openapi()["paths"].items():
        for key in path_data.keys():
            help_string.write(f'\n{key.upper()} {path_url}\n')
            help_string.write(f"\n    {path_data[key].get('description')}\n")
    help_string.write('\n')
    return (PlainTextResponse(help_string.getvalue()))


@app.get('/analytics', tags=['Analytics'])
def get_analytics():
    """Return full analytics of the MMIF storage content."""
    return analytics.storage_analytics()


@app.get('/paths', tags=['Analytics'])
def get_paths():
    """Return all workflow paths in the MMIF storage."""
    stats = analytics.storage_analytics()
    return [wf["path"] for wf in stats["workflows"]]


@app.post('/peek', tags=['Peek and Search'])
def peek(data: Workflow) -> PeekResult:
    """Show the workflow identifier for a workflow and show all MMIF files at that
    workflow identifier."""
    peek_result = storage.peek(data.workflow)
    return PeekResult(
        workflow_id=peek_result['workflow_id'],
        filenames=peek_result['filenames'])


@app.post('/upload', tags=['Upload and Download'])
async def upload(file: UploadFile, overwrite: bool = False) -> dict:
    """Upload a MMIF file, creating a landing spot in the storage if needed."""
    contents = await file.read()
    try:
        path = storage.upload_mmif(contents, mmif_storage.config.STORAGE_DIR,
                                   overwrite=overwrite, binary=True)
        return {
            "destination": str(path),
            "filename": file.filename,
            "filesize": file.size,
            "status": "file-uploaded" }
    except FileExistsWarning as e:
        return { 
            "destination": e.path,
            "filesize": file.size,
            "filename": file.filename,
            "status": "file-not-uploaded",
            "message": "Existing file was not overwritten"}


@app.post('/download', tags=['Upload and Download'])
def download(request: DownloadRequest):
    """Download a serialized MMIF file or a zip file with MMIF files and some
    housekeeping data. This is an older route that combines the functionalities
    of the newer /download_file and /download_files routes."""
    if isinstance(request.guid, str):
        return download_file(request)
    else:
        return download_files(request)


@app.post('/download_file', tags=['Upload and Download'])
def download_file(request: DownloadFileRequest):
    """Download a serialized MMIF file given a single identifier and a workflow
    identifier or a workflow description."""
    wfid = _get_workflow_id(request)
    num_views = len(request.workflow)
    guid = request.guid
    if not wfid:
        return jsonify({'error': 'Missing required parameters: need at least a workflow'})
    # Return the MMIF object (as a dictionary) for a workflow and a single file
    # identifier. If there is no such MMIF file return a dictionary with an error
    # message.
    try:
        return PlainTextResponse(storage.get_mmif_file(wfid, guid, num_views))
    except DownloadWarning as e:
        return {"DownloadWarning": str(e)}


@app.post('/download_files', tags=['Upload and Download'])
def download_files(request: DownloadFilesRequest):
    """Download a zip file with MMIF files and some housekeeping data."""
    wfid = _get_workflow_id(request)
    num_views = len(request.workflow)
    guid = request.guid
    workflow_dir = os.path.join(mmif_storage.config.STORAGE_DIR, wfid)
    if not wfid:
        return jsonify({'error': 'Missing required parameters: need at least a workflow'})
    return get_mmif_files(workflow_dir, guid, num_views)


def _get_workflow_id(request: DownloadRequest) -> str:
    if request.workflow_id is not None:
        return request.workflow_id
    else:
        return storage.generate_identifier_from_workflow(request.workflow)


@app.delete('/delete_path', tags=["Destructive Behavior"])
def delete():
    """Delete all data at a workflow path. This also deletes all downstream data."""
    return PlainTextResponse("Not yet implemented")


@app.delete('/empty_storage', tags=["Destructive Behavior"])
def empty():
    """Delete all data from the storage."""
    return PlainTextResponse("Not yet implemented")


def get_mmif_files(workflow_id: str, guids: list, num_views: int):
    """
    When retrieving multiple MMIFs for a workflow, we return a zip file.

    The user will need to add '--output <FILE>' arg to the curl request.
    """
    mem_file = storage.create_zipfile(workflow_id, guids)
    return StreamingResponse(mem_file, media_type="application/octet-stream")
