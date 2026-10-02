# MMIF Storage

Code to interact with a set of MMIF files. You can use this package to run a FastAPI web service, run a Flask web server, or directly interact with the MMIF data from Python. The required Python version is 3.12 or higher.

MMIF files are stored by saving them in paths that reflect how the file was generated, that is, the path reflects the processing steps involved in creating the file. Each step in the file-creation workflow has three components:

1. The name of the CLAMS application.
2. The version of the application.
3. A hash value reflecting value created from the parameter dictionary used when running the application.

Each of these will be reflected in the path to the MMIF file created under those conditions. For example, running swt-detection version v8.6 with no parameters as a first processing step and adding the resulting file to the storage generates the following path (where the hash value is the one you get when parameter dictionary is empty):

```
swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e
```

See the [data/storage-example](https://github.com/clamsproject/mmif-storage/tree/v0.2.0.rc3/data/storage-example) directory for a small example storage directory which contains two files that were processed by two CLAMS apps.


### Web API

To start the FastAPI web service:

```bash
start_api --dir DIRECTORY --host HOSTNAME --port PORT
```

All options are optional, the default directory is your current working directory and the default host and port are `0.0.0.0` and `8000`. You get erratic behavior including perhaps some server errors if you start the API from a directory that is not a MMIF Storage directory or when the argument that you hand in is not a MMIF Storage directory. 

Once started, the root of the API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000). You can also load the page with all available routes at [http://127.0.0.1:8000/routes](http://127.0.0.1:8000/routes) and access the Swagger UI interface at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). 

See the [API examples document](https://github.com/clamsproject/mmif-storage/blob/v0.2.0.rc3/docs/api-examples.md) for example API calls.


### Web Browser

To start the MMIF Storage browser do:

```bash
start_www --dir DIRECTORY --host HOSTNAME --port PORT
```

The defaults are the same except that the default port is `5000`. As with the web service API, expect weird behavior if you use a directory that is not a MMIF Storage directory.

With the default settings, point your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000). 


### Python API

Before you start you may want to set an environment variable that points to the MMIF Storage directory that you want to use (this example is for a Bash shell, update if needed):

```bash
export STORAGE_DIR=/path/to/storage
```

In Python, first import the configuration and the main modules:

```python
>>> from mmif_storage import config
>>> from mmif_storage.model import storage, analytics
```

After this we have access to all function in the analytics and storage modules. Unless you set an environment variable for the storage directory you will see the following when you check the configuration:

```python
>>> config
Config(STORAGE_DIR=None)
```

You can change this with:

```python
>>> config.STORAGE_DIR = 'any/old/directory'
```

Let's now go straight to three examples. The first example is to use the analytics module to get all paths in the storage:

```python
>>> analytics.storage_paths()
['swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e', 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2', 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e']
```

The second is to use the peek method in the storage module. This is a bit more involved since it requires importing a Pydantic BaseModel that is defined in the `mmif_storage.api` module, and only then we can build a workflow and see what is going on at that workflow:

```python
>>> from mmif_storage.api import WorkflowItem
>>> wf = [WorkflowItem(app='swt-detection', version='v8.6', properties={})]
>>> storage.peek(wf)
{'workflow_id': 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'filenames': ['cpb-aacip-f551104e446-clip2', 'cpb-aacip-f551104e446-clip1']}
```

The third example is to retrieve a MMIF file. We can use the peek results to extract one:

```python
>>> path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
>>> result = storage.get_mmif_file(path, 'cpb-aacip-f551104e446-clip1')
>>> print(len(result)
35349
```


## Developer Notes

As a developer you propably want to get the source code, copy the example configuration settings, and do an editable install:

```bash
git clone https://github.com/clamsproject/mmif-storage
cd mmif-storage
pip install -e .
```

To check whether you can run the main module and see the storage:

```bash
cd src
python -m mmif_storage paths
```

```json
[
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2"
]
```

With the local install you can also start the API with one of the following:

```bash
fastapi run mmif_storage/api.py
uvicorn mmif_storage.api:app
```

And to run the MMIF browser do:

```bash
flask run
```

In order for that to work you first need to copy `src/.env/sample` into `.env` and edit settings as needed. The most likely change is to `STORAGE_DIR`, which now points to the small toy storage directory that is included in this repository.


### Building and installing

There is no pip-installable package on PyPI yet, but you can create a source archive and then install it. For building you run the following, which assumes that the Python build utility is installed:

```bash
python -m build
```

Then install anywhere by using the created archive:

```bash
pip install -r PATH_TO_ARCHIVE
```

### Containerization

Here we also assume that we have access to the source code.

Use Docker or Podman to build the image:

```bash
docker build -f Containerfile -t mmif-storage:0.2.0.rc3 .
```

Starting the container:

```bash
docker run --rm -d -v $PWD/data/storage-example:/data -p 8000:8000 mmif-storage:0.2.0.rc3
```

This assumes that we run this command from the top-level of the `mmif-storage` directory and therefore the container will use the mini example storage. It is the responsibilty of the developer to replace `$PWD/data/storage-example` with the path to the needed MMIF Storage directory. Also, the developer may have to replace the first port in the port mapping depending on local circumstances.