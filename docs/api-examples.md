# API Examples

This goes into a little more detail then what you get in the SwaggerUI automatic documentation at [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

We are assuming that that the MMIF Storage API is up and running on port 8000, and that it is using the example data in `data/storage-example` (which the sample environment file points at).

All examples are using curl invocation. If an output is given then it is pretty printed, which in real life you won't get unless you pipe the output through something like the jq utility.


## Analytics

To get all analytics:

```json
curl -X GET 'http://127.0.0.1:8000/api/mmif/analytics' -H 'accept: application/json'
```
```json
{
  "total_mmif_files": 4,
  "total_workflows": 2,
  "workflows": [
    {
      "path": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
      "spec": {
        "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e": {}
      },
      "mmif_count": 2
    },
    {
      "path": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e",
      "spec": {
        "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e": {},
        "smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e": {}
      },
      "mmif_count": 2
    }
  ],
  "non_terminal_mmif_count": 2,
  "dirty_workflow_mmif_count": 0
}
```

To get all paths in the MMIF Storage::

```json
curl -X GET 'http://127.0.0.1:8000/api/mmif/paths' -H 'accept: application/json'
```

```json
[
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e"
]
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
```json
{
  "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e",
  "filenames": [
    "cpb-aacip-f551104e446-clip2",
    "cpb-aacip-f551104e446-clip1"
  ]
}
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

In this case (unlike with the other examples) you need to be in the root directory of the repository for it to work since there is a file path in the curl command.

```json
curl -X POST 'http://127.0.0.1:8000/api/mmif/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/cpb-aacip-f551104e446-clip1.mmif'
```
```json
{
  "destination": "dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e/cpb-aacip-f551104e446-clip1.mmif",
  "file": {
    "filename": "cpb-aacip-f551104e446-clip1.mmif",
    "file": {},
    "size": 35342,
    "headers": {
      "content-disposition": "form-data; name=\"file\"; filename=\"cpb-aacip-f551104e446-clip1.mmif\"",
      "content-type": "application/octet-stream"
    },
    "_max_mem_size": 1048576
  }
}
```

This overwrites an older file if there was one, need to add option to prohibit overwrite.


## File download

Downloading a single MMIF file. In addition to a workflow this also requires
an identifier (a GUID in the aapb case). The return value is a MMIF file.

```json
curl -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "guid": "cpb-aacip-f551104e446-clip1",
        "workflow": {"swt-detection/v8.6": {}}}'
```

Here is one that should not return a MMIF file because the workflow is not in the storage.

```json
curl -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "guid": "cpb-aacip-f551104e446-clip1",
        "workflow": {"swt-detection/v8.6": {"Pretty": "True"}}}'
```
```json
{
  "warning": "Did not find: cpb-aacip-f551104e446-clip1"
}
```

Same as above, but now with a list of identifiers, which returns a zip file.
The list can be of length one in which case you still get a zip file and not
a JSON/MMIF file as above. Note the addition of the --output argument, without it you may get a warning that the output can mess up the terminal.

```json
curl \
  -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  --output storage-response.zip \
  -d '{ "guid": ["cpb-aacip-f551104e446-clip1"],
        "workflow": {"swt-detection/v8.6": {}}}'
```

Using workflow identifiers. As an alternative we can use the workflow identifier,
this works whether the guid value is a string or a list.

```json
curl -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"guid": "cpb-aacip-f551104e446-clip1",
       "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}'
```

```json     
curl -X POST 'http://127.0.0.1:8000/api/mmif/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  --output storage-response.zip \
  -d '{"guid": ["cpb-aacip-f551104e446-clip1", "cpb-aacip-c72fd5cbadc"],
         "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}'  
```