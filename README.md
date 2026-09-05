# mmif-storage

Code to interact with a set of MMIF files

To set up:

- Install dependencies from `requirements.txt`.
- Move to the `src` directory.
- Copy `.env.sample` into `.env`.
- Edit `STORAGE_DIR` in `.env` if needed.

To check whether you can run the main module::

```bash
python -m mmif_storage peek
```

### The Flask Server

This is to be retired, now just there for making sure the FastAPI has the same or better behavior. 

To start the Flask server:

```bash
flask run
```

### FastAPI

To start FastAPI:

```bash
fastapi dev mmif_storage/api.py
```

You can also do `uvicorn mmif_storage.api:app --reload`.

There are many example API calls in [docs/api-examples.md](docs/api-examples.md).
