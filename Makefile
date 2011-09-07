.PHONY: test release docs

test:
	@pip install -q pytest
	@py.test tests.py

release:
	@python setup.py egg_info -Db '' build_sphinx sdist register upload_docs upload

docs:
	@python setup.py build_sphinx upload_docs
