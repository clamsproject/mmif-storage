clean:
	rm -rf build
	rm -rf src/mmif_storage_mv.egg-info
	rm -rf storage-response*

build:
	python -m build
