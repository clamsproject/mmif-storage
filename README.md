# MMIF Storage

Code to interact with a set of MMIF files. It contains a Python interface, a web server API and a browser.

The required Python version is 3.12 or higher.


## Requirements and Installation

You need Python version 3.12 or higher.

Installation is a simple pip-install:

```bash
pip install mmif-storage
```


## Usage

You can use this code to run a FastAPI web service, start a Flask Server, or directly interact with the MMIF data from Python.


### FastAPI

To start the FastAPI web service:

```bash
start_api --dir DIRECTORY --host HOSTNAME --port PORT
```

All options are optional, the default directory is your current working directory and the default host and port are `0.0.0.0` and `8000`. You get erratic behavior including perhaps some server errors if you start the API from a directory that is not a MMIF Storage directory or when the argument that you hand in is not a MMIF Storage directory. See the [data/storage-example](https://github.com/clamsproject/mmif-storage/tree/develop/data/storage-example) directory for a small example storage directory.

Once started, the root of the API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000). You can also load the page with all available routes at [http://127.0.0.1:8000/routes](http://127.0.0.1:8000/routes) and access the Swagger UI interface at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). 

See the [API examples document](https://github.com/clamsproject/mmif-storage/blob/develop/docs/api-examples.md) for example API calls.


### Web Browser

To start the MMIF Storage browser do:

```bash
start_www --dir DIRECTORY --host HOSTNAME --port PORT
```

The defaults are the same except that the default port is `5000`. As with the web service API, expect weird behavior if you use a directory that is not a MMIF Storage directory.

With the default settings, point your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000). 


### Python API

Let's assume we started Python from the `src` directory and that all requirements are loaded.

First import the configuration and the main modules:

```python
>>> from mmif_storage import config
>>> from mmif_storage.model import storage, analytics
```

After these imports we have access to all function in the analytics and storage modules. The configuration show that it wants to use the small example storage:

```python
>>> config
Config(STORAGE_DIR='../data/storage-example')
```

You can change this if you want:

```python
>>> config.STORAGE_DIR = 'any/old/directory'
```

But let's not do that and go straight to three examples. The first example is to use the analytics module to get all paths in the storage:

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

And now we can use the peek results to extract a MMIF file:

```python
>>> result = storage.get_mmif_file('swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'cpb-aacip-f551104e446-clip1', 1)
>>> print(len(result)
35349
```

> Note the weird third argument, it is intended to be the number of views in the MMIF file to be rewound, which is quite impossible to know apart from just guessing it is just the one view. So this may break down on cases where an app creates more than one view. See [issue #5](https://github.com/clamsproject/mmif-storage/issues/5).



## Developer Notes

As a developer you propably want to run from the source code with an editable install:

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

<!--

TODO: the follopwing does not work anymore.

To run the MMIF browser in production:

```bash
gunicorn "mmif_storage:create_app()" -b 0.0.0.0:8001
```

The port number is used here because by default gunicorn runs on 8000, which may already be taken by the API. The browser then runs at [http://127.0.0.1:8001/www/](http://127.0.0.1:8001/www/).

-->
