# mmif-storage

Code to interact with a set of MMIF files. It contains a Python interface a web server API and a browser.


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

There are many example API calls in [docs/api-examples.md](docs/api-examples.md).

To run the MMIF browser do:

```bash
flask run
```

With the current environment setting the browser will be running at [http://127.0.0.1:5000/www/](http://127.0.0.1:5000/www/).
