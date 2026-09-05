# API Examples

This goes into a little more detail then what you get in the SwaggerUI automatic documentation at [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

We are assuming that there is a MMIF Storage API up and running, and that the MMIF Storage content at least has the following paths:

```
swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e
swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e
```

This can be obtained by:

1. Running swt-detection version v.8.6 without setting any properties.
2. Running smolvlm2-captioner version v1.0 on the output of the above, again without setting any properties.

> TODO. Need to also provide the input files. Maybe invest in creating a download with all data. Or include a mmif-storage directory example in here.

Examples below will need to be adjusted when your MMIF Storage is different.

All examples are using curl invocation.


## Analytics

To get all analytics:

```json
curl -X 'GET' 'http://127.0.0.1:8000/api/mmif/analytics' -H 'accept: application/json'
```

To get all paths in the MMIF Storage::

```json
curl -X 'GET' 'http://127.0.0.1:8000/api/mmif/paths' -H 'accept: application/json'
```


## Peeking

The input is a workflow description. The output is the workflow identifier for the workflow, plus any files at that workflow.

```json
curl -X POST 'http://127.0.0.1:8000/api/mmif/peek' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "workflow": [
    { "app": "swt-detection", "version": "v8.6", "properties": {} },
    { "app": "smolvlm2-captioner", "version": "v1.0", "properties": {} } ]
}'
```

If you use SwaggerUI you can also simply enter the following:

```json
{
  "workflow": [
    { "app": "swt-detection", "version": "v8.6", "properties": {} },
    { "app": "smolvlm2-captioner", "version": "v1.0", "properties": {} } ]
}
```


## File upload

```
curl -X POST 127.0.0.1:8001/api/mmif/upload -d @src/cpb-aacip-f551104e446-clip1.mmif

FastAPI:

curl -X POST 'http://127.0.0.1:8000/api/mmif/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@src/cpb-aacip-f551104e446-clip1.mmif'
```

```
curl -X POST 127.0.0.1:8001/api/mmif/upload?overwrite=True -d @<some_mmif_file>
```


## File download

Downloading a single MMIF file. In addition to a workflow this also requires
an identifier (a GUID in the aapb case). The return value is a MMIF file.

```
Flask:

curl -X POST 127.0.0.1:8001/api/mmif/download \
    -H 'Content-Type: "application/json"' \
    -d '{"guid": "cpb-aacip-4071f72dd46-clip1",
         "workflow": {"swt-detection/v8.6": {}}}'

FastAPI:

curl -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "guid": "cpb-aacip-4071f72dd46-clip1",
        "workflow": {"swt-detection/v8.6": {}}}'
```

Here is one that should not return a MMIF file because the workflow is not in the storage.

```
curl -X POST 127.0.0.1:8001/api/mmif/download \
    -H 'Content-Type: "application/json"' \
    -d '{"guid": "cpb-aacip-4071f72dd46-clip1",
         "workflow": {"swt-detection/v8.6": {"pretty": "True"}}}'

FastAPI

curl -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "guid": "cpb-aacip-4071f72dd46-clip1",
        "workflow": {"swt-detection/v8.6": {"Pretty": "True"}}}'
```

Same as above, but now with a list of identifiers, which returns a zip file.
The list can be of length one in which case you still get a zip file and not
a JSON/MMIF file as above. Note the addition of the --output argument, without it you may get a warning that the output can mess up the terminal.

```
curl -X POST 127.0.0.1:8001/api/mmif/download \
    -H 'Content-Type: "application/json"' \
    --output storage-response.zip \
    -d '{"guid": ["cpb-aacip-4071f72dd46-clip1", "cpb-aacip-c72fd5cbadc"],
         "workflow": {"swt-detection/v8.6": {}}}'

FastAPI:

curl \
  -X 'POST' 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  --output storage-response.zip \
  -d '{ "guid": ["cpb-aacip-4071f72dd46-clip1"],
        "workflow": {"swt-detection/v8.6": {}}}'
```

Using workflow identifiers. As an alternative we can use the workflow identifier,
this works whether the guid value is a string or a list.

```
curl -X POST 127.0.0.1:8001/api/mmif/download \
    -H 'Content-Type: "application/json"' \
    -d '{"guid": "cpb-aacip-4071f72dd46-clip1",
         "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}'

curl -X POST 127.0.0.1:8001/api/mmif/download \
    -H 'Content-Type: "application/json"' \
    --output tmp.zip \
    -d '{"guid": ["cpb-aacip-4071f72dd46-clip1", "cpb-aacip-c72fd5cbadc"],
         "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}'

FastAPI:

curl -X 'POST' \
  'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"guid": "cpb-aacip-4071f72dd46-clip1",
       "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}'
       
curl -X 'POST' \
  'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  --output storage-response.zip \
  -d '{"guid": ["cpb-aacip-4071f72dd46-clip1", "cpb-aacip-c72fd5cbadc"],
         "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}'
         
```