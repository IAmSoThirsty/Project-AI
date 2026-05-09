PYTHON=py -3.12

.PHONY: test lint format precommit run

run:
	$(PYTHON) -m src.app.main

test:
	$(PYTHON) -m pytest -v

lint:
	$(PYTHON) -m ruff check .

format:
	isort src tests --profile black
	$(PYTHON) -m ruff check . --fix
	black src tests

precommit:
	pre-commit run --all-files
