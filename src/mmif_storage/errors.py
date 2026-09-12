
class StorageServerError(Exception):
    pass


class StorageWarning(Warning):
    pass


class UploadWarning(StorageWarning):

    def __init__(self, message: str, path: str = None):
        self.msg = message
        self.path = path

    def __str__(self):
        return self.msg


class FileExistsWarning(UploadWarning):

    def __init__(self, path: str = None):
        super().__init__(message='File already exists', path=path)


class EmptyMmifWarning(StorageWarning):

    def __init__(self, path: str = None):
        self.msg = 'Not saving the MMIF file because it has no views'
        self.path = path

    def __str__(self):
        return self.msg
