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


### Python API

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

Let's now go straight to three examples. The first example is to use the analytics module to get all paths in the storage:

```python
>>> analytics.storage_paths()
['swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e', 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e/smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e/spacy-wrapper/v2.3/5fe49d06725497b274b6eaaf0fe0c5d2', 'dummy-app/v0.1/d41d8cd98f00b204e9800998ecf8427e']
```

The second is to use the peek method in the storage module. It uses the WorkflowItem since in order to peek into the storage we need to know where we are to peek:

```python
>>> wf = [storage.WorkflowItem(app='swt-detection', version='v8.6', properties={})]
>>> storage.peek(wf)
{'workflow_id': 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e', 'filenames': ['cpb-aacip-f551104e446-clip2', 'cpb-aacip-f551104e446-clip1']}
```

The third example is to retrieve a MMIF file. We can use the peek results to extract one:

```python
>>> path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
>>> result = storage.get_mmif_file(path, 'cpb-aacip-f551104e446-clip1')
>>> print(len(result))
35349
```
