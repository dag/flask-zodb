.PHONY: test

test:
	@pip install -q pytest
	@py.test tests.py
