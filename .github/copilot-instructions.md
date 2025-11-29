# Copilot Instructions for Project-AI

This document provides repository-specific instructions for GitHub Copilot to generate code that aligns with this project's conventions, architecture, and best practices.

## Project Overview

Project-AI is a Python desktop AI assistant application built with PyQt6. It provides features including user management, AI chat/tutoring, learning path generation, data analysis, security resources, location tracking, and emergency alerts.

## Architecture

### Directory Structure

```
src/app/
├── main.py           # Application entrypoint
├── core/             # Business logic (no GUI dependencies)
│   ├── user_manager.py
│   ├── location_tracker.py
│   ├── learning_paths.py
│   ├── data_analysis.py
│   ├── security_resources.py
│   ├── emergency_alert.py
│   └── intent_detection.py
├── gui/              # PyQt6 GUI components
│   ├── dashboard.py
│   ├── login.py
│   └── user_management.py
tests/                # pytest test files
tools/                # Utility scripts
```

### Core Principles

- **Separation of Concerns**: Keep PyQt6 GUI code in `src/app/gui/` and business logic in `src/app/core/`. GUI modules should import from core, not vice versa.
- **No Circular Imports**: Avoid circular dependencies between modules.

## Code Style and Conventions

### Python Style

- Follow PEP 8 guidelines
- Use descriptive variable names instead of single-letter or abbreviated names:
  - `user_manager` instead of `um`
  - `username` instead of `uname`
  - `user_data` instead of `udata`
- Use descriptive exception variable names that indicate context:
  - `encryption_error` instead of `e`
  - `decryption_error`, `ip_lookup_error`, etc.
- Use type hints where appropriate

### Line Length

- Maximum line length: 100 characters
- Extract long strings (especially for QMessageBox) into variables before calling functions:

```python
# Good
error_message = "This is a long error message that would exceed the line limit"
QMessageBox.warning(self, "Error", error_message)

# Avoid
QMessageBox.warning(self, "Error", "This is a long error message that would exceed the line limit")
```

## Security Practices

### Password Handling

- **Never store plaintext passwords**
- Use passlib's CryptContext with `pbkdf2_sha256` as primary scheme and `bcrypt` for backward compatibility:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

# Hash a password
password_hash = pwd_context.hash(password)

# Verify a password
is_valid = pwd_context.verify(password, stored_hash)
```

### Encryption

- Use Fernet encryption (from `cryptography` library) for sensitive data
- Load encryption key from `FERNET_KEY` environment variable
- Example pattern:

```python
import os
from cryptography.fernet import Fernet

env_key = os.getenv('FERNET_KEY')
if env_key:
    cipher_suite = Fernet(env_key.encode())
else:
    cipher_suite = Fernet(Fernet.generate_key())
```

### Environment Variables

Required/recommended environment variables:
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `SMTP_USERNAME` - Email for sending emergency alerts
- `SMTP_PASSWORD` - SMTP account password
- `FERNET_KEY` - Base64-encoded Fernet key for encryption
- `DATA_DIR` - Optional data directory path
- `LOG_DIR` - Optional log directory path

**Never commit secrets or API keys to source control.**

## Data Storage Patterns

### Per-User Data

Use username-prefixed JSON files for per-user data storage:

```python
# Pattern: {feature}_{username}.json
f"favorites_{username}.json"
f"history_{username}.json"
f"contacts_{username}.json"
```

### File Operations

- Use `encoding='utf-8'` when opening files
- Handle file not found gracefully
- Create parent directories if needed

## Testing

### Framework

- Use pytest for all tests
- Tests are located in the `tests/` directory
- Run tests with: `pytest -q` or `npm run test:python`

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_feature_does_something(tmp_path):
    # Arrange - set up test data
    test_file = tmp_path / "test.json"
    
    # Act - perform the action
    result = function_under_test()
    
    # Assert - verify the outcome
    assert result == expected_value
```

### File Operations in Tests

Use pytest's `tmp_path` fixture for file operations to ensure test isolation:

```python
def test_with_files(tmp_path):
    test_file = tmp_path / "users.json"
    # ... test code ...
```

## Dependencies

### Installing Dependencies

```bash
pip install -e .
```

Dependencies are defined in `setup.py` and include:
- PyQt6 (GUI framework)
- openai (AI/LLM integration)
- requests (HTTP requests)
- python-dotenv (environment variables)
- cryptography (Fernet encryption)
- geopy (geocoding)
- PyPDF2 (PDF handling)
- numpy, pandas, matplotlib (data processing and visualization)
- scikit-learn (machine learning)
- passlib (password hashing - used in codebase)

### Adding New Dependencies

When adding new dependencies:
1. Add to `setup.py` `install_requires` list
2. Document the purpose in commit message
3. Prefer well-maintained, security-audited packages

## GUI Development (PyQt6)

### Widget Patterns

- Create custom widgets by subclassing PyQt6 widgets
- Connect signals to slots for event handling
- Use layouts (QVBoxLayout, QHBoxLayout, QGridLayout) for responsive design

### Error Handling in GUI

Show user-friendly error messages:

```python
try:
    # operation that might fail
except SpecificException as operation_error:
    error_msg = f"Operation failed: {operation_error}"
    QMessageBox.warning(self, "Error", error_msg)
```

## Common Patterns

### Loading Environment Variables

```python
from dotenv import load_dotenv

load_dotenv()  # Call at application startup
```

### Logging

- Use Python's built-in `logging` module
- Configure appropriate log levels
- Store logs in `LOG_DIR` if specified

## CI/CD

### Linting

- Python: Use flake8 (`flake8 .`)
- Run linting before committing

### Running Tests

```bash
# Python tests
pytest -q

# Or via npm script
npm run test:python
```

## Common Tasks

### Creating a New Core Module

1. Create file in `src/app/core/`
2. Add necessary imports
3. Implement class or functions
4. Add corresponding tests in `tests/`

### Creating a New GUI Component

1. Create file in `src/app/gui/`
2. Import from core modules as needed
3. Subclass appropriate PyQt6 widget
4. Integrate with dashboard or other parent components

### Adding a New Feature

1. Implement business logic in `src/app/core/`
2. Create GUI components in `src/app/gui/`
3. Add tests for core logic
4. Update documentation if needed
