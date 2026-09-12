"""
"""

import sys
import json

import mmif_storage
from mmif_storage.model import storage, analytics


def print_json(json_obj):
    print(json.dumps(json_obj, indent=2))


if len(sys.argv) > 1:

    if sys.argv[1] == 'peek':
        workflow = {"swt-detection/v8.6": {}}
        print_json(storage.peek(workflow))

    elif sys.argv[1] == 'analytics':
        print_json(analytics.storage_analytics())

    elif sys.argv[1] == 'paths':
        stats = analytics.storage_analytics()
        print_json([wf["path"] for wf in stats["workflows"]])
