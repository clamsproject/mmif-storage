clean:
	rm -rf build
	rm -rf src/mmif_storage_mv.egg-info

build:
	python -m build
