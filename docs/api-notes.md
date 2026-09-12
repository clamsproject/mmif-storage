# API Notes

Some notes on current efforts for this repository.


## File upload

Links:

- [stackoverflow: how-to-upload-file-using-fastapi](https://stackoverflow.com/questions/63048825/how-to-upload-file-using-fastapi)

- [tiangolo: request-files/#import-file](https://fastapi.tiangolo.com/tutorial/request-files/#import-file)
   - To receive uploaded files, first install python-multipart.
	- Add it to your project: $ uv add python-multipart
	- This is because uploaded files are sent as "form data".

- [medium: fastapi-file-uploads](https://medium.com/@ThinkingLoop/fastapi-file-uploads-clean-fast-and-foolproof-4ecf0f00404f)

- [betterstack: uploading-files-using-fastapi](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)

Note that storage.upload_mmif() takes a MMIF string


## File download

Links:

- [OneUptime: How to Implement File Downloads in FastAPI](https://oneuptime.com/blog/post/2026-02-03-fastapi-file-downloads/view)
- [Medium: Create in-memory zip files in Python](https://medium.com/@vickypalaniappan12/create-in-memory-zip-files-in-python-79193fbbc6c3)

