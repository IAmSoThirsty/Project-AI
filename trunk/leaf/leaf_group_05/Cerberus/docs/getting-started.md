<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / getting-started.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / getting-started.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Getting Started with Cerberus Guard Bot

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager

## Installation

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/IAmSoThirsty/Cerberus.git
   cd Cerberus
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   make dev-install
   # or
   pip install -e ".[dev]"
   ```

4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

### Production Installation

```bash
pip install cerberus-guard-bot
```

## Quick Start

### Running the Demo

```bash
python -m cerberus.main
# or
make run
# or (after installation)
cerberus
```

### Using as a Library

```python
from cerberus.hub import HubCoordinator

# Initialize the hub
hub = HubCoordinator()

# Analyze content
result = hub.analyze("User input to check")

if result["is_safe"]:
    print("Content is safe")
else:
    print(f"Threat detected: {result['highest_threat']}")
```

## Development

### Running Tests

```bash
make test
# or
pytest
```

### Linting and Formatting

```bash
make lint      # Check for issues
make format    # Auto-fix issues
make typecheck # Run type checker
```

### Project Structure

```
Cerberus/
├── src/
│   └── cerberus/
│       ├── __init__.py
│       ├── main.py           # Entry point
│       ├── guardians/        # Guardian implementations
│       │   ├── base.py       # Base classes
│       │   ├── strict.py     # Strict rule-based guardian
│       │   ├── heuristic.py  # Heuristic scoring guardian
│       │   └── pattern.py    # Pattern matching guardian
│       └── hub/
│           └── coordinator.py # Central hub
├── tests/                    # Test files
├── config/                   # Configuration files
├── docs/                     # Documentation
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
└── Makefile                 # Development commands
```
