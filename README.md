# mmif-storage

Code to interact with a set of MMIF files. It contains a Python interface, a web server API and a browser.

The recommended Python version is 3.11 or higher, but older version may just work fine. 

### Setting up

- Install dependencies from `requirements.txt`.
- Move to the `src` directory.
- Copy `.env.sample` into `.env`.
- Edit settings in `.env` if needed. The most like change is to `STORAGE_DIR`, which now points to the small toy storage directory that is included in this repository.

To check whether you can run the main module:

```bash
python -m mmif_storage peek
```


### Using the API and the browser

To start the API do one of the following:

```bash
fastapi run mmif_storage/api.py
uvicorn mmif_storage.api:app
```

Add the `--reload` option to either command when developing. See [docs/api-examples.md](docs/api-examples.md) for example API calls.

To run the MMIF browser do:

```bash
gunicorn "mmif_storage:create_app()" -b :5000
```

The port number is used here because by default gunicorn runs on 8000, which may already be taken by the API.

For development use

```bash
flask run
```

With the current environment settings the browser will be running at [http://127.0.0.1:5000/www/](http://127.0.0.1:5000/www/).


### Command line scripts

If you have installed the `mmif-storage` package you can also use the command line scripts. Here are a few examples on how to start the Web API:

```bash
run_api
run_api <PATH_TO_DIRECTORY>
run_api <PATH_TO_DIRECTORY> --port 8001 --reload
```

The API uses the current directory as the default MMIF Storage directory, but you can specify any directory. You can also change the port (default is port 8000) and set up the server to reload automatically when something changes in the current directory, notice that such reloading only works out as wished when you start the API from the code directory.
