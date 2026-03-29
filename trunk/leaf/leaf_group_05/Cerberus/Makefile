.PHONY: install dev-install test lint format typecheck clean run help

help:
	@echo "Cerberus Guard Bot - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  dev-install  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linter (ruff)"
	@echo "  format       Format code with ruff"
	@echo "  typecheck    Run type checker (mypy)"
	@echo ""
	@echo "Run:"
	@echo "  run          Run the Cerberus Guard Bot"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean        Remove build artifacts and caches"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m cerberus.main
