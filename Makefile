PYTHON=python

.PHONY: test lint format precommit run

run:
	$(PYTHON) -m src.app.main

test:
	pytest -v

lint:
	ruff check .

format:
	isort src tests --profile black
	ruff check . --fix
	black src tests

precommit:
	pre-commit run --all-files
