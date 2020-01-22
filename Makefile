.PHONY: *

lint:
	tox -e lint

test:
	tox ./tests/test_config.cfg
