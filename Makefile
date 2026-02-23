PYTHON=python

.PHONY: test lint format precommit run paper test-paper

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

paper:
	cd docs/research && pdflatex paper.tex && pdflatex paper.tex

test-paper:
	pytest tests/test_psia_concurrency.py tests/test_psia_liveness.py tests/test_psia_threat_model.py tests/test_shadow_operational_semantics.py tests/test_shadow_thirst_type_system.py -v
