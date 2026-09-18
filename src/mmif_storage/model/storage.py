import os
import re
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from flask import jsonify

from clams_utils.aapb import guidhandler
from mmif import Mmif, utils
from mmif.utils.workflow_helper import describe_single_mmif, generate_param_hash
from mmif.utils.workflow_helper import generate_workflow_identifier
from mmif.utils.summarizer import Summary

import mmif_storage
from mmif_storage.errors import DownloadWarning, EmptyMmifWarning
from mmif_storage.errors import UploadWarning, FileExistsWarning
from mmif_storage.utils import path_as_string, strip_prefix


def peek(workflow_data: list) -> dict:
    """Return a dictionary with a workflow identifier and a list of files at that
    workflow. Return a warning if no workflow identifier could be created. The
    input is a list of workflow items, either as defined in the mmif_storage.api
    module or as any object with app, version and properties variables."""
    wfid = generate_identifier_from_workflow(workflow_data)
    if not wfid:
        return {
            'warning': 'Could not build a workflow identifier from the input given.'}
    wfpath = os.path.join(mmif_storage.config.STORAGE_DIR, wfid)
    return {
        'workflow_id': wfid,
        'filenames': get_files_at_workflow(wfpath)}


def upload_mmif(body: str,
                root: str | None = None,
                overwrite: str = True,
                binary=False) -> Path:

    """Upload the MMIF file in the body to the MMIF storage. Upload includes 
    writing parameter files for the views. Do not overwrite unless overwrite is
    True. Returns the relative path of the file written. Raises an UploadWarning
    for any of the boundary cases where an upload will not occur."""

    mmif = Mmif(body)
    cur_root = mmif_storage.config.STORAGE_DIR if root is None else root
    guid = get_guid(mmif)

    # Generate the workflow identifier from the MMIF views and retrieve the
    # parameter dictionaries from them, then write the parameter dictionaries
    # to the appropriate directories. The syntax of the path is
    # /local_storage_dir/app1name/app1version/app1paramhash/app2name/...
    wfid, param_dicts = generate_workflow_identifier(mmif, return_param_dicts=True)
    if wfid == '':
        # this happens when there are no views, just ignore these
        raise EmptyMmifWarning()
    write_parameters(cur_root, wfid, param_dicts)

    # Note that the absolute path is not necessarily absolute because cur_root
    # is allowed to be relative.
    relative_path = Path(wfid) / f'{guid}.mmif'
    absolute_path = Path(cur_root) / wfid / f'{guid}.mmif'

    # Check for cases when there will be no upload.
    if not mmif.views:
        raise UploadWarning('Upload file has no view content', path=relative_path)
    if absolute_path.exists() and not overwrite:
        raise FileExistsWarning(path=relative_path)

    mode = 'wb' if binary else 'w'
    with open(absolute_path, mode) as f:
        f.write(body)

    return relative_path


def get_guid(mmif: Mmif):
    """Get the first document and calculate the GUID from the its location,
    assumes that the first document is the main one that has the AAPB GUID.
    Raise an UploadWarning if no GUID could be found."""
    guid = guidhandler.get_aapb_guid_from(mmif.documents[0].location)
    if guid is None:
        raise UploadWarning('Document has no identifier')
    return guid


def get_files_at_workflow(workflow_path: Union[str, Path]) -> list:
    """Return the list of MMIF files at the workflow path."""
    return [p.stem for p in Path(workflow_path).glob('*.mmif')]


def write_parameters(root: str, wfid: str, param_dicts: list):
    """Write json parameter files for each step in the workflow."""
    path_name = None
    segments = wfid.split('/')
    if len(segments) % 3 != 0:
        raise UploadWarning(f"Malformed workflow identifier: {wfid} ")   
    for i in range(0, len(segments), 3):
        appn = segments[i]
        appv = segments[i + 1]
        param_hash = segments[i + 2]
        root = root / Path(appn) / appv / param_hash
        root.mkdir(parents=True, exist_ok=True)
        # TODO. This now overwrites an already existing parameter file, add some
        # kind of check here to catch weird cases? Maybe do not overwrite but warn
        # if contents are different.
        with open(root.with_suffix('.json'), 'w') as f:
            json.dump(param_dicts[i // 3], f, indent=2)


def get_mmif_file(workflow_id: str, identifier: str, num_views: int) -> str:
    """
    Retrieve the MMIF file for a workflow and an identifier. If none was found
    raise a DownloadWarning.
    """
    fname = identifier + ".mmif"
    path = os.path.join(mmif_storage.config.STORAGE_DIR, workflow_id, fname)
    # If the filepath exists, we return the content
    try:
        with open(path, 'r') as file:
            return file.read()
    # Otherwise we use the rewinder to check if the user provided a prefix of a
    # mmif workflow that we have previously stored.
    except FileNotFoundError:
        try:
            return rewind_time(workflow_id, fname, num_views)
        except FileNotFoundError:
            # The rewinder does not always succeed so we catch this exception
            # again and raise an application-specific exception.
            raise DownloadWarning(f'Did not find: {fname.split(".")[0]}')


def get_mmif_files(workflow_id: str, guids: list) -> BytesIO:
    """
    Return the MMIF files for a workflow and a list of identifiers. The results are
    returned as a zip file.
    """
    return create_zipfile(workflow_id, guids)


def rewind_time(workflow_id, guid, num_views) -> str:
    """
    This method takes in a workflow (path), a guid, and a number of views, and uses
    os.walk to iterate through directories that begin with that workflow. It takes
    the first mmif file that matches the guid and uses the rewind feature to include
    only the views indicated by the workflow.
    """
    # TODO: this should fail given it doesn't know where the storage directory is
    for home, dirs, files in os.walk(workflow_id):
        # find mmif with matching guid to rewind
        for file in files:
            if guid == file:
                # rewind the mmif
                with open(os.path.join(home, file), 'r') as f:
                    mmif = Mmif(f.read())
                    # we need to calculate the number of views to rewind
                    rewound = utils.rewind.rewind_mmif(mmif, len(mmif.views) - num_views)
                    return rewound.serialize()
    raise FileNotFoundError


def create_zipfile(workflow_id: str, guids: list) -> BytesIO:
    """
    When retrieving multiple MMIFs for a workflow, we construct a zip file that
    contains a file for each guid.
    """
    # TODO: the workflow id is actually an absolute path
    # TODO: this now creates the entire zipfile in memory, should instead use some
    # kind of streaming, and then probably update the way the caling code deals with
    # the reponse
    # See https://oneuptime.com/blog/post/2026-02-03-fastapi-file-downloads/view
    errors = dict()
    mem_file = BytesIO()
    with zipfile.ZipFile(mem_file, 'w', zipfile.ZIP_DEFLATED) as mmif_zip:
        statistics = { "number_of_files": 0, "total_size": 0, "file_names": []}
        for guid in guids:
            try:
                mmif_name = guid + ".mmif"
                path = os.path.join(workflow_id, mmif_name)
                mmif_zip.write(filename=path, arcname=f'storage-response/files/{mmif_name}')
                statistics["number_of_files"] += 1
                statistics["total_size"] += Path(path).stat().st_size
                statistics["file_names"].append(mmif_name)
            except FileNotFoundError:
                errors[guid] = {"Error": f"Did not find {guid}"}
        error_json = json.dumps(errors, indent=2)
        stats_json = json.dumps(statistics, indent=2)
        mmif_zip.writestr(
            zinfo_or_arcname="storage-response/workflow_path.txt", data=workflow_id)
        mmif_zip.writestr(
            zinfo_or_arcname="storage-response/errors.json", data=error_json)
        mmif_zip.writestr(
            zinfo_or_arcname="storage-response/stats.json", data=stats_json)
    mem_file.seek(0)
    return mem_file


def generate_identifier_from_workflow(data: list) -> str:
    """
    Build the relative workflow storage path from the request's JSON data. For
    example, with input data like

        [{"app": "swt-detection", "version": "v2.0", "properties": {"pretty": "True"}}]

    this function should return

        "swt-detection/v2.0/5fe49d06725497b274b6eaaf0fe0c5d2"

    This is similar to generate_workflow_identifier in mmif.utils.workflow_helper,
    but the latter takes full MMIF input. We should probably merge this into the 
    workflow_helper module.
    """
    wfid_segments = []
    for n, workflow_item in enumerate(data):
        clams_app = f"{workflow_item.app}/{workflow_item.version}"
        params = workflow_item.properties
        try:
            param_hash = generate_param_hash(params)
        except AttributeError:
            # in case the parameters input is not a proper dictionary
            param_hash = generate_param_hash({})
        wfid_segments.extend([clams_app, param_hash])
    wfid = '/'.join(wfid_segments)
    return wfid


class StoragePath():

    """Implements a path in the MMIF storage directory. Embeds a regular Path and
    provides some extra data and functionality relevant to the MMIF storage that
    the path is in."""

    def __init__(self, path: str = ''):
        """Embed Path instances for the relative path inside the storage and the
        full path. The path parameter contains the relative path from the mmif
        storage directory or the full path."""
        self.base_path = Path(mmif_storage.config.STORAGE_DIR)
        if str(path).startswith(str(self.base_path)):
            full_path = Path(path)
            rel_path = Path(*full_path.parts[len(self.base_path.parts):])
        else:
            full_path = Path(self.base_path) / path
            rel_path = Path(path)
        self.full_path = full_path
        self.rel_path = rel_path
        self._name = self.rel_path.name
        self.parameter_file = None
        if not self.full_path.suffix:
            parameter_file = self.full_path.with_suffix('.json')
            if parameter_file.exists():
                pfile = ParameterFile(self.rel_path.with_suffix('.json'))
                self.parameter_file = pfile


    def __str__(self):
        """String representation using the relative path."""
        return f'<StoragePath "{self.shortpathname}">'

    def __len__(self):
        """Length of the full path."""
        return len(self.full_path.parts)

    @property
    def name(self):
        """The final component of the relative path, if any."""
        return self._name

    @property
    def stem(self):
        """The stem of the relative path, if any."""
        return self.rel_path.stem

    @property
    def shortpathname(self):
        """Shortened name of the relative path."""
        return path_as_string(self.rel_path)

    @property
    def parts(self):
        return self.full_path.parts

    def is_dir(self):
        return self.full_path.is_dir()

    def is_file(self):
        return self.full_path.is_file()

    def iterdir(self):
        return self.full_path.iterdir()

    def path_for_display(self) -> str:
        # for display in the browser
        return ' > '.join(self.rel_path.parts)

    def pp(self):
        print(f'\n{self}')
        print(f'  base_path  = {self.base_path}')
        print(f'  rel_path  = {self.rel_path}')
        print(f'  full_path = {self.full_path}\n')

    def directories(self) -> list:
        """Return a list of Paths, one for each subdirectory."""
        dirs = [sub for sub in self.full_path.iterdir() if sub.is_dir()]
        return list(sorted([self.strip_prefix(d) for d in dirs]))

    def files(self, include_derived=False):
        """Return a list of Paths, one for each file in the directory."""
        # NOTE. Now property files and MMIF files are distinguished simply by using
        # the extension. Maybe use somehwhat more sophisticated code to get the file
        # with parameters, like re.match("[0-9a-z]{32}\.json", path.name")
        def is_derived(path: Path):
            return path.name.endswith('.summ.json') or path.name.endswith('.desc.json')
        files = [sub for sub in self.full_path.iterdir() if sub.is_file()]
        if not include_derived:
            files = [f for f in files if not is_derived(f)]
        # Another filter to exclude parameter files.
        files = [f for f in files if not f.suffix == '.json']
        return list(sorted([self.strip_prefix(f) for f in files]))

    def ddir(self) -> list:
        """Return the directories at depth 3. For each directory we get a pair with
        the full path and the relative path."""
        # TODO: maybe this should return a list of StoragePaths
        paths = []
        depth = len(self) + 3
        prefix_length = len(self.base_path.parts)
        for root, _, _ in self.full_path.walk():
            if len(root.parts) == depth:
                paths.append(
                    (Path(*root.parts[prefix_length:]), Path(*root.parts[-3:]) ))
        return paths

    def strip_prefix(self, path: Path) -> Path:
        return Path(*path.parts[len(self.base_path.parts):])

    def rmtree(self, indent=''):
        """Delete the path from the storage, if there is a sister path with the
        same name with a .json suffix, then delete that file as well."""
        shutil.rmtree(str(self.full_path))
        properties_file = StoragePath(
            f'{str(self.full_path.parent)}/{self.name}.json')
        if properties_file.is_file():
            properties_file.unlink()

    def unlink(self):
        """Remove the file from the storage and from the index."""
        # TODO: this does NOT remove the path from the index
        self.full_path.unlink()


class ParameterFile:

    def __init__(self, path: str):
        self.base_path = Path(mmif_storage.config.STORAGE_DIR)
        # rel_path is the relative path from the storage directory
        # full_path is the absolute path on the storage server
        self.rel_path = Path(path)
        self.full_path = self.base_path / path
        self.parameters = json.dumps(json.loads(self.full_path.read_text()), indent=2)
        self.size = self.full_path.stat().st_size

    def __str__(self):
        return f'<ParameterFile size={self.size} "{self.rel_path}">'


class MmifFile:

    """Keeps track of all information for a MMIF file on the storage server. This
    includes summary and description files, as well as various information from
    higher up the path including app parameter files."""

    # TODO: rename paths to be the same as for StorageDir and ParameterFile

    def __init__(self, path: Path):
        self.storage = Path(mmif_storage.config.STORAGE_DIR)
        self.path = path
        self.fullpath = self.storage / path
        self.summary = self.fullpath.parent / f'{self.fullpath.stem}.summ.json'
        self.summary_error = False
        self.description = self.fullpath.parent / f'{self.fullpath.stem}.desc.json'

    def summary_exists(self):
        return self.summary.exists()

    def description_exists(self):
        return self.description.exists()

    def relative_path(self) -> Path:
        """The relative path to the parent of the MMIF file."""
        return strip_prefix(self.storage, self.path.parent)

    def parameters(self) -> list:
        """A list of app-parameter pairs taken from all the apps involved in
        creating the MMIF file."""
        parameters = []
        for p in reversed(self.path.parents):
            if re.match("[0-9a-z]{32}", p.stem):
                param_file = self.storage / p.parent / f'{p.stem}.json'
                app_path = Path(*p.parts[-3:-1])
                param_content = param_file.read_text()
                parameters.append((app_path, param_content))
        return parameters

    def mmif_content(self) -> str:
        """The content of the MMIF file as a prettified string."""
        with open(self.fullpath, 'r') as fh:
            mmif_content = json.dumps(json.loads(fh.read()), indent=2)
            return mmif_content

    def mmif_size(self):
        return self.fullpath.stat().st_size

    def summary_size(self):
        return self.summary.stat().st_size

    def summary_size_as_string(self):
        return f'{self.summary.stat().st_size:,d}'
        # The weird thing is that using the following instead gives errors
        #    size = self.summary_size()
        #    return f'{size:,d}'
        # It looks like self is not an instance of MmifFile but None. I am
        # totally at a loss to why that would be, but this may not be the case
        # anymore now that summaries are generated earlier.

    def summary_content(self) -> str:
        """Get the summary of the MMIF file."""
        if self.summary_error:
            return '{ "message": "error when creating summary"}'
        else:
            return self.summary.read_text()

    def create_summary(self):
        if self.summary.exists():
            # TODO: maybe add functionality somewhere to recreate a summary
            return
        try:
            summary_obj = Summary(self.fullpath)
            summary_obj.report(outfile=self.summary)
        except Exception as e:
            self.summary_error = True

    def description_content(self) -> str:
        """Get the description of the MMIF file. In case there is no description,
        create it first."""
        if not self.description_exists():
            desc = describe_single_mmif(self.fullpath)
            with open(str(self.description), 'w') as fh:
                fh.write(json.dumps(desc, indent=2))
        return self.description.read_text()

    def pp(self):
        print(f'\n<{self.path.name}>')
        print(f'    base = {self.storage}')
        print(f'    mmif = {strip_prefix(self.storage, self.fullpath)}')
        print(f'    summ = {strip_prefix(self.storage, self.summary)}')
        print(f'    desc = {strip_prefix(self.storage, self.description)}\n')
