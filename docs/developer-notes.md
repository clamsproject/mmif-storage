## Developer Notes

As a developer you propably want to get the source code and do an editable install:

```bash
git clone https://github.com/clamsproject/mmif-storage
cd mmif-storage
pip install -e .
```

To check whether you can run the main module and see the example storage:

```bash
python -m mmif_storage test
```

This runs a couple of test and shows something like the following:

```
>>> storage paths

[
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2"
]

>>> peek results

{
  "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
  "filenames": [
    "cpb-aacip-f551104e446-clip2",
    "cpb-aacip-f551104e446-clip1"
  ]
}

>>> file retrieval (single MMIF file and a zip archive)

file size =  35349
zip size  =  8626
]
```

You can also peek into other storage directories

```bash
python -m mmif_storage paths PATH_TO_STORAGE
```
```
[
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e",
  "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2"
]
```


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
