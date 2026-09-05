"""

Now has the following functionality from the old Flask server:

- peek
- analytics
- file download (single file)
- file download (zipfile)
- file upload

Need to add all the search functionality from the Shack, which will require moving
some code from the clamshack to this repository in mmif_storage.model.

Other things to do:
- upload now always overwrites old file

Use __main__.py to test calling this programmatically.

"""

import os
from typing import Dict, List, Any

from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

from mmif import View
from mmif_storage.model import storage, analytics
from mmif_storage.errors import StorageServerError


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


@app.get('/api/mmif/analytics', tags=['Analytics'])
def get_analytics():
    """Return full analytics of the MMIF storage content."""
    return analytics.storage_analytics()


@app.get('/api/mmif/paths', tags=['Analytics'])
def get_paths():
    """Return all workflow paths in the MMIF storage."""
    stats = analytics.storage_analytics()
    return [wf["path"] for wf in stats["workflows"]]


@app.post('/api/mmif/peek', tags=['Peek and Search'])
def peek(data: Workflow) -> PeekResult:
    peek_result = storage.peek(data.simplify())
    return PeekResult(
        workflow_id=peek_result['workflow_id'],
        filenames=peek_result['filenames'])


@app.post('/api/mmif/download', tags=['Upload and Download'])
def download(request: DownloadRequest) -> MmifFile | list | Any:
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
    storage_dir = os.environ.get('STORAGE_DIR')
    workflow_dir = os.path.join(storage_dir, wfid)
    if not wfid:
        # TODO: does this make sense?
        return jsonify({'error': 'Missing required parameters: need at least a workflow'})
    if isinstance(guid, str):
        return get_mmif_file(workflow_dir, guid, num_views)
    elif isinstance(guid, list):
        return get_mmif_files(workflow_dir, guid, num_views)


@app.post('/api/mmif/upload', tags=['Upload and Download'])
async def upload(file: UploadFile):
    contents = await file.read()
    storage.upload_mmif(contents, overwrite=True, binary=True)
    return file


def get_mmif_file(workflow_id: str, guid: str, num_views: int) -> dict:
    """
    Return the MMIF object (as a dictionary) for a workflow and a single file
    identifier. If there is no such MMIF file return a dictionary with an error
    message.
    """
    try:
        return storage.get_mmif_for_guid(workflow_id, guid, num_views)
    except StorageServerError as e:
        return {"error": str(e)}, 201


def get_mmif_files(workflow_id: str, guids: list, num_views: int):
    """
    When retrieving multiple MMIFs for a workflow, we return a zip file.

    The user will need to add '--output <FILE>' arg to the curl request, which
    seems to be needed even with the use of download_name below. In fact, that
    parameter does not seem to be needed when using --output. Need to look into
    this a bit.
    """
    mem_file = storage.create_zipfile(workflow_id, guids)
    print('>>>', mem_file)
    return StreamingResponse(mem_file, media_type="application/octet-stream")
