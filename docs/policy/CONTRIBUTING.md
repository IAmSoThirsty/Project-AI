# Contributing to Project-AI

Thank you for interest in contributing to Project-AI! This guide will help you get started.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Git

## Setup Development Environment

### 1. Clone the repository

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
```

### 2. Create a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
pip install -r requirements.txt
```

### 4. Install pre-commit hooks (optional)

```bash
pip install pre-commit
pre-commit install
```

## Development Workflow

### Running Tests

```bash
# Run all tests
npm test

# Run Python tests only
pytest -v

# Run Python tests with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Run linter (ruff)
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Run type checker (Pylance via Pyright)
python -m pylance
```

### Running the Application Locally

#### Using Docker (recommended)

```bash
docker-compose up
```

#### Using Python directly

```bash
python -m app.main
```

## Code Style

- **Python**: Follow PEP 8, enforced by `ruff`
- **Line length**: 88 characters (Black compatible)
- **Type hints**: Required for all functions (Python 3.11+)
- **Docstrings**: Use triple-quoted strings for modules, classes, and functions

## Commit Messages

Use clear, descriptive commit messages:

```text
feat: Add new feature
fix: Fix bug in module
docs: Update documentation
refactor: Improve code structure
test: Add test coverage
chore: Update dependencies
```

## Pull Requests

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit with clear messages
3. Push to your fork: `git push origin feature/my-feature`
4. Create a Pull Request against `main` with a clear description
5. Ensure all checks pass (tests, linting, type checking)

## Reporting Issues

When reporting issues, please include:

- Python and Node versions
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

## Questions?

Feel free to open an issue for questions or discussions!
