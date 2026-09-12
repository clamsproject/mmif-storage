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
from mmif_storage.errors import StorageServerError, FileExistsWarning


app = FastAPI()


class WorkflowItem(BaseModel):
    app: str
    version: str
    properties: dict


class Workflow(BaseModel):
    workflow: List[WorkflowItem]

    def simplify(self) -> dict:
        """Translate the workflow object into the kind of representation needed by
        storage.peek()."""
        return { f'{item.app}/{item.version}': item.properties for item in self.workflow }


class PeekResult(BaseModel):
    workflow_id: str
    filenames: list


class DownloadRequest(BaseModel):
    guid: str | list[str]
    workflow_id: str | None = None
    workflow: dict | None = []
    #workflow: List[WorkflowItem] | None


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
    peek_result = storage.peek(data.simplify())
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
            "status": "succes" }
    except FileExistsWarning as e:
        return { 
            "warning": "Existing file was not overwritten",
            "destination": e.path,
            "filename": file.filename }


@app.post('/download', tags=['Upload and Download'])
def download(request: DownloadRequest) -> MmifFile | list | Any:
    """Download a MMIF file or a zip file with MMIF files and some housekeeping data."""
    # TODO. The return type is a bit of a mess now. MmifFile is obvious. The second
    # type is for when single file download fails. The third is for when a Zipfile 
    # is returned. I tried StreamingResponse, but that ran into validation errors.
    if request.workflow_id is not None:
        # TODO: maybe add a check that the value is an existing workflow
        wfid = request.workflow_id
    else:
        wfid = storage.generate_workflow_identifier_from_workflow_data(request.workflow)
    num_views = len(request.workflow)
    guid = request.guid
    workflow_dir = os.path.join(mmif_storage.config.STORAGE_DIR, wfid)
    if not wfid:
        # TODO: does this make sense?
        return jsonify({'error': 'Missing required parameters: need at least a workflow'})
    if isinstance(guid, str):
        return get_mmif_file(workflow_dir, guid, num_views)
    elif isinstance(guid, list):
        return get_mmif_files(workflow_dir, guid, num_views)


@app.delete('/delete_path', tags=["Destructive Behavior"])
def delete():
    """Delete all data at a workflow path. This also deletes all downstream data."""
    return PlainTextResponse("Not yet implemented")


@app.delete('/empty_storage', tags=["Destructive Behavior"])
def empty():
    """Delete all data from the storage."""
    return PlainTextResponse("Not yet implemented")


def get_mmif_file(workflow_id: str, guid: str, num_views: int) -> dict:
    """
    Return the MMIF object (as a dictionary) for a workflow and a single file
    identifier. If there is no such MMIF file return a dictionary with an error
    message.
    """
    try:
        return storage.get_mmif_for_guid(workflow_id, guid, num_views)
    except StorageServerError as e:
        return {"warning": str(e)}


def get_mmif_files(workflow_id: str, guids: list, num_views: int):
    """
    When retrieving multiple MMIFs for a workflow, we return a zip file.

    The user will need to add '--output <FILE>' arg to the curl request, which
    seems to be needed even with the use of download_name below. In fact, that
    parameter does not seem to be needed when using --output. Need to look into
    this a bit.
    """
    mem_file = storage.create_zipfile(workflow_id, guids)
    return StreamingResponse(mem_file, media_type="application/octet-stream")
