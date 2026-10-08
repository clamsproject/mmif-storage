import sys
import json
from pathlib import Path
from types import ModuleType, FunctionType
from gc import get_referents

from mmif.utils.cli import describe
from mmif.utils.workflow_helper import generate_param_hash


def getsize(obj):
    # Based on an answer from Aaron Hall in
    # https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
    BLACKLIST = type, ModuleType, FunctionType
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


def load_json(fname: str) -> dict:
    return json.loads(Path(fname).read_text())    


def path_from_workflow_specs(workflow_spec: dict):
    """
    Helper method to read in a json object containing the names of the app in a 
    workflow and their parameters, and then build a path out of the apps and the
    hashed parameters.

    NOTE. This is similar to workflow_helper.generate_workflow_identifier in the
    mmif.utils package, but different in that it takes a workflow spec dictionary
    rather than a MMIF file, it also does not need to deal with apps that generate
    multiple views.
    """
    wf_path = []
    for clams_app, parameters in workflow_spec['workflow'].items():
        param_hash = generate_param_hash(parameters)
        wf_path.extend([clams_app, param_hash])
    return '/'.join(wf_path)


def strip_prefix(prefix: str, path: Path) -> Path:
    return Path(*path.parts[len(Path(prefix).parts):])


def path_as_string(p: Path) -> str:
    """Return a string for the directory path in the MMIF storage. It abbreviates
    the hash value of the parameters for clarity."""
    path_string = ''
    for triple in path_as_tuples(p):
        if len(triple) == 3:
            app, version, hash_value = triple
            if hash_value.endswith('.json'):
                path_string += f'{app}/{version}/{hash_value[:8]}.json'
            else:
                path_string += f'{app}/{version}/{hash_value[:8]}/'
        else:
            path_string += '/'.join([p for p in triple])
    return path_string if path_string else '~'


def path_as_tuples(p: Path) -> list[tuple]:
    """Return the path a a list of tuples <appname, appversion, paramhash>. The
    last element in the list is not necessarily a tuple of lenth 3, it could also
    be <appname, appversion> or <appname>."""
    parts = p.parts
    return [parts[i:i + 3] for i in range(0, len(parts), 3)]
