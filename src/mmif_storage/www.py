import os
import re
import io
import sys
import json
import tempfile
from pathlib import Path
from operator import itemgetter

from flask import Flask, request, jsonify, Blueprint, render_template
from jinja2 import Template

import mmif_storage
from mmif_storage.model.analytics import storage_analytics
from mmif_storage.utils import ServerDirectory, MmifFile, ParameterFile
from mmif_storage.utils import path_from_workflow_specs, strip_prefix


bp = Blueprint('www', __name__, template_folder='templates')


DEBUG = True


@bp.get('/www/')
@bp.get('/www/index.html')
def index():
    return render_template('index.html')


@bp.get('/www/search_mmif.html')
def search_mmif_get():
    return render_template('search_mmif.html', status=None)


@bp.post('/www/search_mmif.html')
def search_mmif_post():
    # TODO: this is a tad messy, and there is some overlap here with 
    # mmif_storage.mmif_storage.download_mmif(), may need some refactoring
    
    guid = request.form.get('guid', '')
    workflow = request.form.get('workflow', '')
    debug(f'guid = {guid}')
    debug(f'workflow = {" ".join(str(workflow).split())}')
    
    status = None
    message = None
    mmif_file = None
    mmif_files = []
    workflow_path = None

    if not workflow:
        status = 'no-workflow'
        message = 'Missing required parameter: need at least a workflow'
        message = json.dumps({"message": message}, indent=2)
    else:
        workflow_path = path_from_workflow_specs(
            {"guid": guid, "workflow": json.loads(workflow)})
        debug(f'workflow_path = {workflow_path}')
        full_workflow_path = os.path.join(mmif_storage.config.STORAGE_DIR, workflow_path)
        if not guid:
            # get the files at the workflow path
            status = 'workflow'
            mmif_files = sorted([p.stem for p in Path(full_workflow_path).glob('*')])
        elif isinstance(guid, str):
            # get the one MMIF file, but check for its existence
            status = 'workflow-guid'
            mmif_file = Path(full_workflow_path) / f'{guid}.mmif'
            if not mmif_file.exists():
                status = 'workflow-guid-no-files'
                message = json.dumps(
                    {"message" : f"File does not exist at that path",
                     "filename": mmif_file.name,
                     "pathname": workflow_path}, indent=2)
    
    debug(f'status = {status}')
    mmif_files = [mf for mf in mmif_files if not (mf[-5:] in ('.desc', '.summ'))]
    debug(f'Found {len(mmif_files)} MMIF files for workflow')

    return render_template(
        'search_mmif.html',
        status=status, message=message, guid=guid, workflow=workflow,
        path=workflow_path, mmif_file=mmif_file, mmif_files=mmif_files)


@bp.get('/www/browse_paths.html')
def browse_paths():
    sdir = ServerDirectory(mmif_storage.config.STORAGE_DIR, request.args.get("path"))
    return render_template('browse_paths.html', sdir=sdir)


@bp.get('/www/view_mmif.html')
def view_file():
    mode = request.args.get("mode")
    mfile = MmifFile(mmif_storage.config.STORAGE_DIR, Path(request.args.get("path")))
    debug(f'mode = {mode}')
    if mode in ('summary', 'collapsible'):
        # Doing this upfront (unlike with the description) to avoid issues with
        # the summary size later.
        debug(f'Creating summary for {mfile.path.name}')
        mfile.create_summary()
    return render_template('view_mmif.html', mfile=mfile, mode=mode)


'''
@bp.get(f'/www/inspector/{INDEX_PAGE}')
def inspector_index():
    data = InspectorData(INDEX_PAGE)
    rendered_template = data.template.render(
        summary=Summary(data.summ_file, data.summary))
    return update_rendered(rendered_template, data.css_file)


@bp.get(f'/www/inspector/{VIEWS_PAGE}')
def inspector_views():
    return display_inspector_page(VIEWS_PAGE)


@bp.get(f'/www/inspector/{TIMEFRAMES_PAGE}')
def inspector_timeframes():
    data = InspectorData(TIMEFRAMES_PAGE)
    rendered_template = data.template.render(
        summary=Summary(data.summ_file, data.summary))
    return update_rendered(rendered_template, data.css_file, data.js_file)


@bp.get(f'/www/inspector/{TRANSCRIPT_PAGE}')
def inspector_transcript():
    data = InspectorData(TRANSCRIPT_PAGE)
    rendered_template = data.template.render(
        summary=Summary(data.summ_file, data.summary))
    return update_rendered(rendered_template, data.css_file, data.js_file)


@bp.get(f'/www/inspector/{CAPTIONS_PAGE}')
def inspector_captions():
    data = InspectorData(CAPTIONS_PAGE)
    rendered_template = data.template.render(
        summary=Summary(data.summ_file, data.summary))
    return update_rendered(rendered_template, data.css_file, data.js_file)


def display_inspector_page(page_name: str) -> str:
    data = InspectorData(page_name)
    rendered_template = data.template.render(
        summary=Summary(data.summ_file, data.summary))
    return update_rendered(rendered_template, data.css_file, data.js_file)
'''


@bp.get('/www/analytics.html')
def analytics():
    analytics = storage_analytics()
    properties = {p: analytics[p] for p in analytics.keys() if p != 'workflows'}
    workflows = sorted(analytics['workflows'], key=itemgetter('path'))
    for workflow in workflows:
        workflow['full_path'] = Path(mmif_storage.config.STORAGE_DIR) / workflow['path']
    return render_template(
        'analytics.html', properties=properties, workflows=workflows)


class InspectorData:

    def __init__(self, page_name: str):
        templates_dir = Path(inspector.__file__).parent / 'templates'
        self.template = Template((Path(templates_dir) / page_name).read_text())
        self.css_file = Path(inspector.__file__).parent / CSS_PAGE
        self.js_file = Path(inspector.__file__).parent / JS_PAGE
        mmif_file = Path(request.args.get("path"))
        self.summ_file = Path(mmif_storage.config.STORAGE_DIR) / mmif_file.parent / f'{mmif_file.stem}.summ.json'

    @property
    def summary(self):
        # TODO: assumes the summary exists, may need a test here or in the template
        return json.loads(self.summ_file.read_text())

    
def update_rendered(html: str, css_file: Path, js_file: Path = None):
    """Method to add the stylesheet and javascript that the inspector files need."""
    # TODO: make adding the javascript file optional for some pages
    # TODO: this way of adding path GET variable to subpages is fragile
    path = request.args.get("path")
    buffer = io.StringIO()
    for line in html.split('\n'):
        if line == '</head>':
            buffer.write(f'<style>\n{css_file.read_text().strip()}\n</style>\n')
            if js_file is not None:
                buffer.write(f'<script>\n{js_file.read_text().strip()}\n</script>\n')
        elif '[ <a href="views.html">Views</a>' in line:
            buffer.write(f'[ <a href="views.html?path={path}">Views</a>\n')
        elif line == '| <a href="timeframes.html">TimeFrames</a>':
            buffer.write(f'| <a href="timeframes.html?path={path}"">TimeFrames</a>\n')
        elif line == '| <a href="transcript.html">Transcript</a>':
            buffer.write('| <a href="transcript.html?path={path}"">Transcript</a>\n')
        elif line == '| <a href="captions.html">Captions</a>':
            buffer.write(f'| <a href="captions.html?path={path}"">Captions</a>\n')
        else:
            buffer.write(f'{line}\n')
    return buffer.getvalue()


def debug(message: str):
    if DEBUG:
        print(f'DEBUG {message}')

