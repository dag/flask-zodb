.PHONY: test release docs upload

test:
	@pip install -q pytest
	@py.test tests.py

release:
	@python setup.py egg_info -Db '' build_sphinx sdist

docs:
	@python setup.py build_sphinx upload_docs

upload: release
	@python setup.py upload
