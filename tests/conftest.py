"""

Hooks to alter pytest behavior.

See https://docs.pytest.org/en/7.1.x/reference/reference.html#hooks

Here all we do is modify the test order. I want the storage tests to be performed
before the API tests.

Edit FILE_ORDER to update the order.

"""


import os


FILE_ORDER = [
    "test_storage.py",
    "test_api.py"
]


def pytest_collection_modifyitems(items):
    """Sorts collected test items in-place based on a predefined list of file names."""
    
    def get_file_index(item):
        # Extract the file name from the test item's location
        filename = os.path.basename(item.fspath)
        if filename in FILE_ORDER:
            return FILE_ORDER.index(filename)
        # Files not specified will run at the very end
        return len(FILE_ORDER)

    items.sort(key=get_file_index)
