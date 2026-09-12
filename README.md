# mmif-storage

Code to interact with a set of MMIF files. It contains a Python interface, a web server API and a browser.

The recommended Python version is 3.11 or higher, but older version may just work fine. 

### Setting up

- Install dependencies from `requirements.txt`.
- Move to the `src` directory.
- Copy `.env.sample` into `.env`.
- Edit settings in `.env` if needed. The most like change is to `STORAGE_DIR`, which now points to the small toy storage directory that is included in this repository.

To check whether you can run the main module and see the storage:

```bash
python -m mmif_storage paths
```
```json
[
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e"
]
```


### Using the API and the browser

To start the API do one of the following:

```bash
fastapi run mmif_storage/api.py
uvicorn mmif_storage.api:app
```

See [docs/api-examples.md](docs/api-examples.md) for example API calls. The SwaggerUI page will be at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

To run the MMIF browser do:

```bash
gunicorn "mmif_storage:create_app()" -b 0.0.0.0:8001
```

The port number is used here because by default gunicorn runs on 8000, which may already be taken by the API. The browser then runs at [http://127.0.0.1:8001/www/](http://127.0.0.1:8001/www/).

For development use

```bash
flask run
```

With the current Flask environment settings the browser will then be running at [http://127.0.0.1:5000/www/](http://127.0.0.1:5000/www/).


### Building and installing

There is no pip-installable package on PyPI yet, but you can create a source archive and then install it. For building you run the following, which assumes that the Python build utility is installed:

```bash
python -m build
```

Then install anywhere by using the created archive:

```bash
pip install -r PATH_TO_THIS_REPOSITORY/dist/mmif_storage-0.1.0.tar.gz
```


### Command line scripts

If you have installed the `mmif-storage` package you can also use shell commands to start the API or browser. For these commands the environment settings are ignored.

To start the web API:

```bash
start_api --dir PATH_TO_DIRECTORY --port PORT
```

Both arguments are optional: the default port is 8000 and the default directory is the current directory.

To start the web browser:

```bash
start_www --dir PATH_TO_DIRECTORY --port PORT
```

Again both arguments are optional: the default port is 5000 and the default directory is the current directory.
