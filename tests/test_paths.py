import mmif_storage
from mmif_storage.model import storage
from utils import environment


class TestStoragePath():

    def test_path_properties_for_directory(self, environment):
        """Test basic properties of the directory path."""
        name = 'd41d8cd98f00b204e9800998ecf8427e'
        rel_path = f'swt-detection/v8.6/{name}'
        full_path = f'tests/tmp-storage/{rel_path}'
        shortname = 'swt-detection/v8.6/d41d8cd9/'
        p = storage.StoragePath(rel_path)
        assert p.name == name
        assert p.shortpathname == shortname
        assert str(p.full_path) == full_path
        assert str(p.rel_path) == rel_path

    def test_path_properties_for_file(self, environment):
        """Test basic properties of the file path."""
        dname = 'd41d8cd98f00b204e9800998ecf8427e'
        fname = 'cpb-aacip-f551104e446-clip1.mmif'
        fstem = 'cpb-aacip-f551104e446-clip1'
        rel_path = f'swt-detection/v8.6/{dname}/{fname}'
        full_path = f'tests/tmp-storage/{rel_path}'
        p = storage.StoragePath(rel_path)
        assert p.name == fname
        assert p.stem == fstem
        assert str(p.full_path) == full_path
        assert str(p.rel_path) == rel_path
        assert len(p) == 6

    def test_iterdir(self, environment):
        """Checking the contents of a directory."""
        rel_path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        p = storage.StoragePath(rel_path)
        subs = list(sorted([sub.name for sub in p.iterdir()]))
        expected_subs = ['cpb-aacip-f551104e446-clip1.mmif',
                         'cpb-aacip-f551104e446-clip2.mmif',
                         'smolvlm2-captioner']
        assert subs == expected_subs

    def test_directories(self, environment):
        """Checking the contents of a directory."""
        rel_path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        p = storage.StoragePath(rel_path)
        dirs = list(sorted([sub.name for sub in p.directories()]))
        expected_dirs = ['smolvlm2-captioner']
        assert dirs == expected_dirs

    def test_files(self, environment):
        """Checking the contents of a directory."""
        rel_path = 'swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e'
        p = storage.StoragePath(rel_path)
        files = list(sorted([sub.name for sub in p.files()]))
        expected_files = ['cpb-aacip-f551104e446-clip1.mmif',
                         'cpb-aacip-f551104e446-clip2.mmif']
        assert files == expected_files

    def test_deep_dirs(self, environment):
        name = 'd41d8cd98f00b204e9800998ecf8427e'
        rel_path = f'swt-detection/v8.6/{name}'
        p = storage.StoragePath(rel_path)
        rel_paths = [str(sub[1]) for sub in p.ddir()]
        expected_rel_path = 'smolvlm2-captioner/v1.0/d41d8cd98f00b204e9800998ecf8427e'
        assert len(rel_paths) == 1
        assert rel_paths[0] == expected_rel_path
