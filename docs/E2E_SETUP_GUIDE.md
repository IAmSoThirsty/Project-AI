# E2E Evaluation Pipeline - Setup and Configuration Guide

## Complete Setup Guide

This guide provides step-by-step instructions for setting up and configuring the E2E evaluation pipeline for local development, CI/CD, and production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Environment Configuration](#environment-configuration)
4. [Service Configuration](#service-configuration)
5. [CI/CD Integration](#cicd-integration)
6. [Docker Setup](#docker-setup)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **RAM**: Minimum 8GB (16GB recommended for parallel execution)
- **Disk Space**: 2GB free for test artifacts and reports
- **OS**: Linux, macOS, or Windows with WSL2

### Required Software

```bash
# Python 3.11+
python --version

# pip package manager
pip --version

# Git
git --version

# Docker (optional, for service orchestration)
docker --version
docker-compose --version
```

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install E2E testing dependencies
pip install pytest pytest-cov pytest-asyncio pytest-timeout pytest-xdist pytest-html
```

### 4. Verify Installation

```bash
# Verify pytest installation
pytest --version

# Verify E2E modules can be imported
python -c "from e2e.reporting import HTMLReporter; print('E2E modules OK')"

# List available E2E test markers
pytest --markers | grep e2e
```

## Environment Configuration

### 1. Create Environment File

Create `.env` file in project root:

```bash
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env` file:

```bash
# OpenAI API Key (required for AI features)
OPENAI_API_KEY=sk-your-key-here

# Hugging Face API Key (required for image generation)
HUGGINGFACE_API_KEY=hf_your-key-here

# Fernet encryption key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
FERNET_KEY=your-fernet-key-here

# SMTP Configuration (optional, for email alerts)
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# E2E Configuration
E2E_ENV=development
E2E_DEBUG=false
E2E_USE_REAL_APIS=false  # Set to true to test with real APIs
```

### 3. E2E Test Configuration

Edit `e2e/config/e2e_config.py` for advanced configuration:

```python
# e2e/config/e2e_config.py

import os
from dataclasses import dataclass

@dataclass
class E2EConfig:
    # Environment
    environment: str = os.getenv("E2E_ENV", "test")
    debug_mode: bool = os.getenv("E2E_DEBUG", "false").lower() == "true"

    # Timeouts (seconds)
    default_timeout: float = 30.0
    service_startup_timeout: float = 60.0
    test_execution_timeout: float = 300.0

    # Coverage
    coverage_threshold: float = 0.80  # 80% minimum
    enforce_coverage: bool = True

    # Reporting
    generate_html_report: bool = True
    generate_json_report: bool = True
```

## Service Configuration

### Flask API Service

Configure Flask API in `config/flask_config.py`:

```python
FLASK_HOST = "localhost"
FLASK_PORT = 5000
FLASK_DEBUG = False
```

### Temporal Server (Optional)

If testing Temporal workflows:

```bash
# Start Temporal server via Docker
docker run -d -p 7233:7233 temporalio/auto-setup:latest

# Verify Temporal is running
curl http://localhost:7233
```

### Prometheus (Optional)

If testing monitoring features:

```bash
# Start Prometheus via Docker Compose
docker-compose up -d prometheus

# Verify Prometheus is running
curl http://localhost:9090/-/healthy
```

## Running E2E Tests

### Basic Execution

```bash
# Run all E2E tests
pytest e2e/scenarios/ -v

# Run specific test file
pytest e2e/scenarios/test_project_ai_core_integration_e2e.py -v

# Run with specific markers
pytest -m "e2e and not slow" -v

# Run with coverage
pytest e2e/scenarios/ --cov=src --cov=e2e --cov-report=html -v
```

### Using CLI Orchestrator

```bash
# Run all E2E tests with full reporting
python -m e2e.cli

# Run with parallel execution (faster)
python -m e2e.cli --parallel --workers 8

# Run specific markers
python -m e2e.cli -m e2e -m integration

# Skip coverage (faster for development)
python -m e2e.cli --no-coverage

# Verbose output
python -m e2e.cli -vv
```

### Test Execution Examples

```bash
# Development: Fast feedback loop
pytest e2e/scenarios/ -m "e2e and not slow" --no-cov -x

# Pre-commit: Run core tests
pytest e2e/scenarios/test_project_ai_core_integration_e2e.py -v

# Full validation: All tests with coverage
python -m e2e.cli --parallel --workers 8

# Security focus: Run only security tests
pytest -m "security or adversarial" -v

# Performance testing: Run only slow tests
pytest -m slow -v --durations=10
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop, copilot/**]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist pytest-timeout

      - name: Run E2E tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          HUGGINGFACE_API_KEY: ${{ secrets.HUGGINGFACE_API_KEY }}
          E2E_ENV: ci
        run: |
          python -m e2e.cli --parallel --workers 4

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./e2e/coverage/coverage.xml
          flags: e2e-tests
          name: e2e-coverage

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-reports-${{ matrix.python-version }}
          path: e2e/reports/

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-artifacts-${{ matrix.python-version }}
          path: e2e/artifacts/

      - name: Check coverage threshold
        run: |
          python -c "
          import json
          with open('e2e/coverage/coverage.json') as f:
              data = json.load(f)
              coverage = data['totals']['percent_covered']
              threshold = 80.0
              if coverage < threshold:
                  print(f'Coverage {coverage:.2f}% below threshold {threshold}%')
                  exit(1)
              print(f'Coverage {coverage:.2f}% meets threshold {threshold}%')
          "
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - report

e2e-tests:
  stage: test
  image: python:3.11
  
  variables:
    E2E_ENV: ci
  
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov pytest-xdist
  
  script:
    - python -m e2e.cli --parallel --workers 4
  
  artifacts:
    when: always
    paths:
      - e2e/reports/
      - e2e/artifacts/
      - e2e/coverage/
    reports:
      junit: e2e/artifacts/*/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: e2e/coverage/coverage.xml
  
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Jenkins Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    environment {
        E2E_ENV = 'ci'
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && pip install pytest pytest-cov pytest-xdist'
            }
        }
        
        stage('E2E Tests') {
            steps {
                sh '. venv/bin/activate && python -m e2e.cli --parallel --workers 4'
            }
        }
        
        stage('Reports') {
            steps {
                publishHTML([
                    reportDir: 'e2e/reports',
                    reportFiles: 'e2e_report_*.html',
                    reportName: 'E2E Test Report'
                ])
                
                junit 'e2e/artifacts/*/junit.xml'
                
                publishCoverage adapters: [cobertura('e2e/coverage/coverage.xml')]
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'e2e/reports/**, e2e/artifacts/**', allowEmptyArchive: true
        }
    }
}
```

## Docker Setup

### Docker Compose Configuration

Create `docker-compose.e2e.yml`:

```yaml
version: '3.8'

services:
  e2e-tests:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m e2e.cli --parallel
    environment:
      - PYTHONUNBUFFERED=1
      - E2E_ENV=docker
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
    volumes:
      - ./e2e:/app/e2e
      - ./src:/app/src
      - ./e2e/reports:/app/e2e/reports
      - ./e2e/artifacts:/app/e2e/artifacts
    depends_on:
      - flask-api
      - temporal
      - prometheus
    networks:
      - e2e-network

  flask-api:
    build: .
    command: python -m flask run --host=0.0.0.0
    environment:
      - FLASK_APP=api.main
    ports:
      - "5000:5000"
    networks:
      - e2e-network

  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
    networks:
      - e2e-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus:/etc/prometheus
    networks:
      - e2e-network

networks:
  e2e-network:
    driver: bridge
```

### Running with Docker

```bash
# Build images
docker-compose -f docker-compose.e2e.yml build

# Run E2E tests
docker-compose -f docker-compose.e2e.yml up e2e-tests

# View reports (in host)
open e2e/reports/e2e_report_*.html

# Cleanup
docker-compose -f docker-compose.e2e.yml down -v
```

## Advanced Configuration

### Custom Test Markers

Add custom markers in `e2e/conftest.py`:

```python
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "performance: Performance tests")
```

### Custom Fixtures

Add project-specific fixtures in `e2e/conftest.py`:

```python
@pytest.fixture
def project_ai_system():
    """Initialize complete Project-AI system for testing."""
    from src.app.core.ai_systems import (
        FourLaws, AIPersona, MemoryExpansionSystem
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        system = {
            'laws': FourLaws(),
            'persona': AIPersona(data_dir=tmpdir),
            'memory': MemoryExpansionSystem(data_dir=tmpdir),
        }
        yield system
```

### Performance Tuning

Configure for optimal performance in `e2e/config/e2e_config.py`:

```python
# For CI environments (faster, less coverage)
@dataclass
class CIConfig(E2EConfig):
    coverage_threshold: float = 0.70
    enforce_coverage: bool = False
    parallel_workers: int = 8

# For local development (comprehensive)
@dataclass
class DevConfig(E2EConfig):
    coverage_threshold: float = 0.85
    enforce_coverage: bool = True
    parallel_workers: int = 4
    debug_mode: bool = True
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Problem: Cannot import e2e modules
# Solution: Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use python -m
python -m pytest e2e/scenarios/
```

#### API Key Errors

```bash
# Problem: Missing API keys
# Solution: Check .env file
cat .env | grep API_KEY

# Verify keys are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

#### Port Conflicts

```bash
# Problem: Port 5000 already in use
# Solution: Kill existing process or change port
lsof -ti:5000 | xargs kill -9

# Or change port in e2e/config/e2e_config.py
FLASK_PORT = 5001
```

#### Memory Issues

```bash
# Problem: Out of memory during parallel execution
# Solution: Reduce workers
python -m e2e.cli --parallel --workers 2

# Or increase system memory limits
ulimit -v unlimited  # Linux
```

#### Test Timeouts

```bash
# Problem: Tests timing out
# Solution: Increase timeout in pytest.ini
[pytest]
timeout = 600  # 10 minutes

# Or skip slow tests
pytest -m "not slow" -v
```

### Debug Commands

```bash
# Check E2E configuration
python -c "from e2e.config.e2e_config import get_config; print(get_config())"

# List all test markers
pytest --markers

# Collect tests without running
pytest e2e/scenarios/ --collect-only

# Run specific test with debugging
pytest e2e/scenarios/test_file.py::test_name -vv --pdb

# Show test durations
pytest e2e/scenarios/ --durations=20

# Generate detailed test report
pytest e2e/scenarios/ -v --html=report.html --self-contained-html
```

## Maintenance

### Regular Tasks

```bash
# Update dependencies (monthly)
pip install --upgrade -r requirements.txt

# Clean old artifacts (weekly)
find e2e/artifacts -type d -mtime +7 -exec rm -rf {} +

# Archive reports (monthly)
tar -czf reports_$(date +%Y%m).tar.gz e2e/reports/

# Check coverage trends
python -m e2e.cli --parallel && \
  python -c "import json; print(json.load(open('e2e/coverage/coverage.json'))['totals']['percent_covered'])"
```

### Health Checks

```bash
# Verify E2E system health
python -c "
from e2e.reporting import HTMLReporter, JSONReporter, CoverageReporter, ArtifactManager
print('✅ All E2E modules healthy')
"

# Run smoke tests
pytest -m smoke -v

# Verify coverage threshold
pytest e2e/scenarios/ --cov=src --cov-fail-under=80
```

## Support

For additional support:

1. Check [E2E_EVALUATION_PIPELINE.md](./E2E_EVALUATION_PIPELINE.md) for usage guide
2. Review example tests in `e2e/scenarios/`
3. Open GitHub issue with `e2e-tests` label
4. Include logs from `e2e/artifacts/`

---

**Project-AI E2E Evaluation Pipeline - Setup Guide**  
Version 1.0.0 | 2026
