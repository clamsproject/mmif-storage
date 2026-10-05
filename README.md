# MMIF Storage

Python interface to interact with a set of MMIF files, for Python version 3.12 or higher.

MMIF files are stored by saving them in paths that reflect how the file was generated, that is, the path reflects the processing steps involved in creating the file. Each step in the file-creation workflow has three components:

1. The name of the CLAMS application.
2. The version of the application.
3. A hash value calculated from the parameter dictionary used when running the application.

Each of these will be reflected in the path to the MMIF file created under those conditions. For example, running swt-detection version v8.6 with no parameters as a first processing step and adding the resulting file to the storage generates the following path (where the hash value is the one you always get when the parameter dictionary is empty):

```
swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e
```

See the [data/storage-example](https://github.com/clamsproject/mmif-storage/tree/v0.2.0.rc3/data/storage-example) directory for a small example storage directory which contains two files that were processed by two CLAMS apps.


## Python API

Before you start you may want to set an environment variable that points to the MMIF Storage directory that you want to use (this example is for a Bash shell, update if needed):

```bash
export MMIF_STORAGE_DIR=/path/to/storage
```

In Python, first import the configuration and the main modules:

```python
>>> from mmif_storage import config, storage, analytics
```

After this we have access to all function in the analytics and storage modules. Unless you set an environment variable for the storage directory you will see the following when you check the configuration:

```python
>>> config
Config(MMIF_STORAGE_DIR=None)
```

You can change this with:

```python
>>> config.MMIF_STORAGE_DIR = 'any/old/directory'
```

### Storage information and other statistics

The analytics module provides two functions: `storage_paths()` and storage_analytics()`. Use the first to get all paths in the storage:

```python
>>> analytics.storage_paths()
['swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e', 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2', 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e']
```

And use `analytics.storage_analytics()` to see some more information:

```python
>>> analytics.storage_analytics()
```

The result is more verbose than just the list of paths and includes total counts of MMIF files and work flows and some more information for each workflow.


### Peeking into the storage directory

Use the peek method in the storage module. It uses the WorkflowItem since in order to peek into the storage we need to know where we are to peek:

```python
>>> wf = [storage.WorkflowItem(app='swt-detection', version='v8.6', properties={})]
>>> storage.peek(wf)
{'workflow_id': 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'filenames': ['cpb-aacip-f551104e446-clip2', 'cpb-aacip-f551104e446-clip1']}
```


### Retrieving MMIF files

To retrieve a file you need a workflow path and we can use the prior peek results to get at that information:

```python
>>> path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
>>> result = storage.get_mmif_file(path, 'cpb-aacip-f551104e446-clip1')
>>> len(result)
35349
```

Instead of `get_mmif_file()` you can use `get_mmif_files()` and turn the second parameter into a list:

```python
>>> result = storage.get_mmif_files(path, ['cpb-aacip-f551104e446-clip1'])
```

If there are more identifiers in the list the return value needs to include all matching MMIF files. This could be done in a JSON object but it i sfar more convenient to use a zip archive. Therefore, the return value of `get_mmif_files()` is a BytesIO object, which should be saved into a zip file.

```python
>>> with open("output.zip", "wb") as f:
...     f.write(result.getbuffer())
```


### Uploading MMIF files

To upload a file first read its contents and then use the `upload_mmif()` method from the storage module:

```python
>>> from importlib.resources import files
>>> mmif_file = files("mmif_storage").joinpath("data/cpb-aacip-f551104e446-clip1.mmif")
>>> storage.upload_mmif(mmif_file.read_text())
PosixPath('dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e/cpb-aacip-f551104e446-clip1.mmif')
```

The first two lines are some boiler plate code to retrieve the example file from the package data, the last line calls the storage API and if succesfull it returns the relative path to the uploaded file.

You can upload a file repeatedly, in which case the old file will be overwritten, use the `overwrite` parameter to avoid that:

```python
>>> storage.upload_mmif(mmif_file.read_text(), overwrite=False)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/marc/Desktop/projects/clams/code/clamsproject/mmif-storage/src/mmif_storage/storage.py", line 77, in upload_mmif
    raise FileExistsWarning(path=relative_path)
mmif_storage.errors.FileExistsWarning: File already exists
```

You can use `peek()` to confirm that the storage was updated:

```python
>>> storage.peek([storage.WorkflowItem(app='swt-detection', version='v8.6', properties={})])
{'workflow_id': 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e', 'filenames': ['cpb-aacip-f551104e446-clip1']}
```


<!--
from mmif_storage import config, storage, analytics
config.MMIF_STORAGE_DIR = 'tmp-store'
path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
storage.peek([storage.WorkflowItem(app='swt-detection', version='v8.6', properties={})])

result = storage.get_mmif_files(path, ['cpb-aacip-f551104e446-clip1'])
with open("output.zip", "wb") as f: f.write(result.getbuffer())
-->
