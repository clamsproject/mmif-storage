clean:
	rm -rf build
	rm -rf src/mmif_storage_mv.egg-info
	rm -rf storage-response*
	rm -rf tests/tmp-storage
	rm output.zip

build:
	python -m build

test:
	pytest --disable-warnings --tb=line
