# GitHub Copilot Instructions for Project-AI

## Repository Overview

This is a Python desktop application called "Project-AI" that provides a personal AI assistant with multiple features. The app is built using PyQt6 for the GUI and integrates with OpenAI's GPT models for AI functionality.

**Tech Stack:**
- Python 3.8+ (primary language)
- PyQt6 for desktop GUI
- OpenAI API for AI features
- scikit-learn for machine learning
- pandas, numpy, matplotlib for data analysis
- cryptography (Fernet) for encryption
- pytest for testing
- Node.js test infrastructure (npm test)

## Project Structure

```
src/app/
├── main.py                          # Application entrypoint
├── core/                            # Core business logic
│   ├── user_manager.py              # User profiles and authentication
│   ├── learning_paths.py            # AI learning path generation
│   ├── intent_detection.py          # ML-based intent detection
│   ├── data_analysis.py             # Data analysis utilities
│   ├── security_resources.py        # Security resources manager
│   ├── location_tracker.py          # Location tracking with encryption
│   └── emergency_alert.py           # Emergency alert system
└── gui/                             # PyQt6 GUI components
    ├── dashboard.py                 # Main UI with tabs
    ├── dashboard_handlers.py        # Dashboard event handlers
    ├── login.py                     # Login dialog
    └── user_management.py           # User management UI

tests/                               # Test files (pytest)
tools/                               # Migration and utility scripts
.github/workflows/                   # CI/CD workflows
```

## Code Standards and Conventions

### Python Style
- Follow PEP 8 style guide
- Use flake8 for linting (configured in CI)
- Break long lines across multiple lines to satisfy line length limits, especially for:
  - Long string literals
  - Function arguments
  - Dictionary entries
  - QMessageBox strings (extract into variables before calling)

### Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes
- Extract long QMessageBox strings into variables before calling the function to maintain line length limits

### Code Formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length: typically 79-100 characters
- Break long lines appropriately

### Type Hints
- Use Python typing annotations where appropriate
- Follow typing best practices

### Comments and Documentation
- Use docstrings for all public functions and classes
- Keep comments clear and concise
- Document complex logic and business rules

## Security Guidelines

### Environment Variables and Secrets
- **NEVER commit secrets, API keys, or passwords to source control**
- Load environment variables from `.env` files using python-dotenv's `load_dotenv()` at initialization
- Required environment variables:
  - `OPENAI_API_KEY` - OpenAI API key (optional)
  - `SMTP_USERNAME` - Email for emergency alerts
  - `SMTP_PASSWORD` - SMTP password
  - `FERNET_KEY` - Base64-encoded Fernet key for encryption
  - `DATA_DIR` - App data directory (default: `data`)
  - `LOG_DIR` - Log directory (default: `logs`)

### Authentication and Password Handling
- Use passlib CryptContext with:
  - pbkdf2_sha256 as preferred scheme
  - bcrypt for backward compatibility
  - Set `deprecated='auto'`
- Store password hashes, never plaintext passwords
- User data stored in JSON with encrypted fields

### Encryption
- Use Fernet encryption for sensitive data (location history, secrets)
- Always use `FERNET_KEY` from environment variables
- Use `html_escape` as a sanitizer to avoid cross-site scripting vulnerabilities

### Input Validation
- Validate and sanitize all user inputs
- Use proper error handling for external API calls
- Handle file operations safely

## Build, Test, and Lint Commands

### Python Testing
```bash
# Run all tests
pytest -q

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_user_manager.py
```

### Python Linting
```bash
# Lint all Python files
flake8 .

# Lint specific file
flake8 src/app/core/user_manager.py
```

### Node.js Testing
```bash
# Install dependencies
npm ci

# Run all tests
npm test

# Run JavaScript tests only
npm run test:js

# Run Python tests via npm
npm run test:python
```

### Setup and Installation
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -e .
# OR
pip install -r requirements.txt  # if available

# Run the application
python src/app/main.py
```

## GitHub Actions CI/CD

### Workflows
- **node-ci.yml**: Runs both Node.js and Python CI jobs
  - Node CI: Installs dependencies, detects and runs JS tests
  - Python CI: Detects Python files, runs flake8 and pytest

### Best Practices for Workflows
- Use `>>` (append) not `>` (overwrite) when writing to `$GITHUB_OUTPUT` in workflow steps
- Use explicit permissions blocks in GitHub Actions workflows to limit GITHUB_TOKEN scope (e.g., `permissions: contents: read`)
- Use `node --test` without globs for default test command to auto-discover tests and avoid failures when no tests exist

## Dependencies Management

### Python Dependencies
- Listed in `setup.py`:
  - PyQt6 (GUI framework)
  - openai (AI integration)
  - requests (HTTP client)
  - python-dotenv (environment variables)
  - cryptography (encryption)
  - geopy (geolocation)
  - PyPDF2 (PDF handling)
  - numpy, pandas (data processing)
  - matplotlib (visualization)
  - scikit-learn (machine learning)
  - passlib (password hashing)
  - joblib (model serialization)

### Adding New Dependencies
- Add to `setup.py` in the `install_requires` list
- For development dependencies, consider adding a separate `dev` extra
- Update documentation if the dependency requires configuration

## Testing Practices

### Python Tests
- Use pytest framework
- Tests located in `tests/` directory
- Test files should match pattern `test_*.py`
- Use fixtures for common setup
- Mock external dependencies (OpenAI API, SMTP, etc.)

### Test Structure
- Arrange-Act-Assert pattern
- Clear test names describing what is being tested
- One assertion concept per test when possible

## Common Patterns

### User Management
- User profiles stored in JSON format
- Password hashing with passlib
- Role-based access (admin, member)
- Profile pictures and preferences per user

### Error Handling
- Use try-except blocks for external API calls
- Log errors appropriately
- Provide user-friendly error messages in GUI

### GUI Development
- Use PyQt6 signals and slots for event handling
- Separate UI code from business logic
- Create reusable dialogs and widgets
- Handle window close events properly

## Important Files

- **src/app/main.py**: Application entry point, loads `.env`
- **src/app/core/user_manager.py**: Central user management and authentication
- **src/app/gui/dashboard.py**: Main application window with tabbed interface
- **tools/migrate_users.py**: Migration tool for password hashing updates
- **.env**: Environment variables (not in source control)
- **package.json**: Node.js configuration and test scripts
- **setup.py**: Python package configuration and dependencies

## Additional Notes

### First-Run Experience
- App detects no users and prompts for admin account creation
- Admin can manage users from the "Users" tab
- Login dialog shows "Table of Contents" view after authentication

### Mobile Support
- Designed with future mobile extension in mind
- Core logic separated from GUI for reusability

### Feature Modules
1. Location Tracking: IP-based geolocation with optional GPS, encrypted history
2. Security Resources: Curated security/CTF/privacy repos with GitHub API integration
3. Learning Paths: Personalized learning path generation via OpenAI
4. Emergency Alerts: Email alerts to contacts with location information
5. Data Analysis: CSV/XLSX/JSON loading, statistics, visualizations, clustering
6. AI Tutor: Conversational interface with intent detection

## When Making Changes

1. **Always run tests** before and after changes: `pytest -q`
2. **Lint your code**: `flake8 .`
3. **Check for security issues**: Review for secrets, input validation, encryption
4. **Update documentation** if adding features or changing behavior
5. **Follow existing patterns** in the codebase
6. **Use minimal changes** - change only what's necessary
7. **Test GUI changes** manually by running the application
8. **Consider backward compatibility** when modifying user data formats
