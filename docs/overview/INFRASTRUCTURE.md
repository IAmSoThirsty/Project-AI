# Infrastructure Documentation

This document describes the infrastructure configuration and setup for Project-AI.

## Project Structure

```text
Project-AI/
├── .github/
│   ├── workflows/           # GitHub Actions CI/CD
│   │   ├── codacy-analysis.yml
│   │   ├── deploy.yml
│   │   └── node-ci.yml
│   ├── scripts/
│   └── instructions/
├── src/
│   ├── app/                 # Main application
│   │   ├── core/            # Core modules
│   │   ├── gui/             # PyQt6 GUI
│   │   ├── agents/          # AI agents
│   │   └── main.py
│   ├── auth/                # Authentication
│   └── ui/                  # UI components
├── tests/                   # Test suite
├── web/                     # Web components
│   ├── backend/
│   └── frontend/
├── data/                    # Data files and cache
├── logs/                    # Application logs
├── docs/                    # Documentation
├── examples/                # Example files
├── .env                     # Environment configuration (local)
├── .env.example             # Environment template
├── .editorconfig            # IDE formatting
├── .gitignore               # Git exclusions
├── .dockerignore            # Docker exclusions
├── .markdownlint.json       # Markdown linter config
├── .python-version          # Python version (pyenv)
├── pyrightconfig.json       # Type checker config
├── pyproject.toml           # Python project metadata
├── setup.py                 # Installation script
├── requirements.txt         # Python dependencies
├── package.json             # Node.js metadata
├── Dockerfile               # Docker build definition
├── docker-compose.yml       # Docker Compose config
├── MANIFEST.in              # Distribution manifest
├── CONTRIBUTING.md          # Contributing guide
└── INFRASTRUCTURE.md        # This file
```

## Configuration Files

### Python Configuration

- **`pyproject.toml`**: Main project configuration (PEP 517/518)
  - Project metadata (name, version, dependencies)
  - Tool configurations (ruff, pytest, black)
  - Python version requirement: 3.11+

- **`setup.py`**: Installation entry point
  - Minimal configuration (delegates to pyproject.toml)
  - Defines console scripts entry points

- **`requirements.txt`**: Pinned dependencies
  - Generated from pyproject.toml
  - Use for reproducible installations

- **`pyrightconfig.json`**: Type checking configuration
  - Type checking mode: "standard"
  - Python version: 3.11

### Development Configuration

- **`.env`**: Environment variables (local only, not committed)
  - `OPENAI_API_KEY`: OpenAI API credentials
  - `SMTP_USERNAME`: Email service credentials
  - `FERNET_KEY`: Encryption key for sensitive data

- **`.editorconfig`**: IDE formatting rules
  - Enforces consistent indentation and line endings
  - Supported by most modern IDEs

- **`.python-version`**: Python version for pyenv
  - Ensures consistent Python version across team

- **`.markdownlint.json`**: Markdown linting rules
  - Enforces consistent markdown formatting

### Build and Distribution

- **`MANIFEST.in`**: Distribution file manifest
  - Includes non-Python files in distributions
  - Specifies QSS stylesheets, JSON configs, examples

### Git Configuration

- **`.gitignore`**: Files excluded from version control
  - Virtual environments, caches, secrets, OS files
  - Comprehensive Python and Node.js exclusions

## Containerization

### Docker

- **`Dockerfile`**: Multi-stage build for production
  - Stage 1: Build wheels from dependencies
  - Stage 2: Runtime image with only necessary packages
  - Health checks included
  - Optimized for size and security

- **`.dockerignore`**: Files excluded from Docker build
  - Reduces build context size
  - Excludes unnecessary files

### Docker Compose

- **`docker-compose.yml`**: Local development environment
  - Service: project-ai
  - Volume mounts for live code editing
  - Environment variable support
  - Network isolation

**Usage:**

```bash
# Start development environment
docker-compose up

# Rebuild image
docker-compose build

# Stop containers
docker-compose down
```

## CI/CD Workflows

### GitHub Actions

Located in `.github/workflows/`:

#### 1. **node-ci.yml** - Node.js and Python CI

- **Triggers**: Push and PR to main
- **Node.js Jobs**:
  - Install dependencies
  - Type checking (if available)
  - Run tests
  - Coverage reports
  - Build
  - npm audit (security scan)
- **Python Jobs**:
  - Detect Python files
  - Install test dependencies
  - Run flake8
  - Run pytest with coverage
  - Generate JUnit reports
  - Annotate failures

#### 2. **codacy-analysis.yml** - Optional Code Quality

- **Status**: Disabled by default (template)
- **Triggers**: Push and PR to main
- **To Enable**:
  1. Create Codacy account at <https://codacy.com>
  2. Add repository secret: `CODACY_API_TOKEN`
  3. Uncomment job steps

#### 3. **deploy.yml** - Optional Deployment

- **Status**: Disabled by default (template)
- **Triggers**: Push to main
- **To Enable for SSH Deployment**:
  1. Add repository secrets:
     - `SSH`: Private SSH key
     - `HOST`: Deployment server hostname
     - `PORT`: SSH port (optional)
     - `USER`: SSH username (optional)
  2. Uncomment deployment steps
  3. Customize deployment commands

## Package Management

### Python Dependencies

**Core Dependencies** (in `pyproject.toml`):

- PyQt6: GUI framework
- scikit-learn: Machine learning
- openai: GPT API integration
- cryptography: Encryption utilities
- geopy: Geolocation services
- Additional: pandas, numpy, matplotlib, requests, python-dotenv

**Development Dependencies**:

- ruff: Code linting and formatting
- pytest: Testing framework
- pytest-cov: Coverage reporting
- black: Code formatter

### Node.js Configuration

**`package.json`**:

- Version: 1.0.0
- Scripts: test, lint, format, dev, build
- Engines: Node.js 18+

## Environment Setup

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 2. Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e ".[dev]"
pip install -r requirements.txt

# 4. Set up environment file
cp .env.example .env
# Edit .env with your credentials

# 5. Run application
python -m app.main
```

### Docker Development

```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f

# Run commands in container
docker-compose exec project-ai bash
```

## Code Quality

### Linting

```bash
# Check code
ruff check .

# Auto-fix issues
ruff check . --fix
```

### Testing

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

### Type Checking

Configured in `pyrightconfig.json`. Check with Pylance in VS Code or:

```bash
python -m pylance
```

## Deployment

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Linting passes (ruff)
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated

### Building Distribution

```bash
# Build wheel and source distribution
python -m build

# Upload to PyPI
twine upload dist/*
```

### Docker Deployment

```bash
# Build production image
docker build -t project-ai:1.0.0 .

# Tag for registry
docker tag project-ai:1.0.0 myregistry/project-ai:1.0.0

# Push to registry
docker push myregistry/project-ai:1.0.0

# Run on server
docker run -d \
  --name project-ai \
  -e OPENAI_API_KEY=... \
  -e FERNET_KEY=... \
  -v /data:/app/data \
  -v /logs:/app/logs \
  myregistry/project-ai:1.0.0
```

## Security

### Secrets Management

- Store secrets in `.env` (not committed)
- Use GitHub repository secrets for CI/CD
- Rotate credentials regularly
- Never commit `.env` or private keys

### Dependency Security

```bash
# Check for vulnerabilities
npm audit
pip install pip-audit && pip-audit

# Update dependencies safely
pip install --upgrade -r requirements.txt
```

## Monitoring and Logging

### Application Logs

Logs are stored in `logs/` directory with structure:

```text
logs/
├── app.log              # Main application log
├── errors.log           # Error-only log
└── access.log           # Access log (if applicable)
```

### Health Checks

Docker containers include health checks:

```bash
docker ps  # Shows health status
```

## Troubleshooting

### Python Environment Issues

```bash
# Verify Python version
python --version  # Should be 3.11+

# Check virtual environment
which python  # Should show .venv path

# Reinstall dependencies
pip install -e ".[dev]"
pip install -r requirements.txt --force-reinstall
```

### Docker Issues

```bash
# Clean build
docker-compose down
docker system prune -a
docker-compose up --build

# View detailed logs
docker-compose logs --tail=100 -f

# Rebuild specific service
docker-compose build --no-cache project-ai
```

### Linting/Type Checking

```bash
# Check for configuration conflicts
cat pyrightconfig.json
cat pyproject.toml

# Clear caches
rm -rf .ruff_cache .pytest_cache __pycache__
```

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
