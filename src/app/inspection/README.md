# Inspection & Audit Subsystem - Quick Reference

## Overview

The Repository Inspection & Audit System is a production-grade, institutional-quality subsystem for comprehensive repository analysis, quality assessment, and compliance reporting.

## Key Features

✅ **Complete File Inventory** - Discovers, classifies, and analyzes all repository files
✅ **Dependency Analysis** - Builds dependency graphs, detects circular dependencies
✅ **Quality Assessment** - Computes documentation coverage, maintainability index, cohesion
✅ **Automated Linting** - Python (ruff, mypy, bandit), Markdown, YAML/JSON validation
✅ **Machine-Readable Reports** - JSON/YAML with full audit data
✅ **Human-Readable Catalogs** - Institutional-grade Markdown documentation
✅ **Health Scoring** - 0-100 score with letter grade (A-F)
✅ **CLI Interface** - Rich terminal UI with progress tracking
✅ **REST API** - FastAPI endpoints for programmatic access
✅ **Config-Driven** - YAML configuration with sensible defaults

## Quick Start

```bash

# Simple audit

python inspection_cli.py

# With options

python inspection_cli.py --repo /path/to/repo --output ./reports --no-lint

# Using Python

from app.inspection.audit_pipeline import run_audit
results = run_audit("/path/to/repo")
print(f"Grade: {results.overall_assessment['grade']}")
```

## Output Example

```
Overall Health: 98.0/100 (Grade: A)

Statistics:
├── Files Analyzed: 1,234
├── Lines of Code: 45,678
├── Components: 45
├── Dependencies: 234
├── Integrity Issues: 12
└── Lint Issues: 5
```

## Architecture

```
Repository → Inspector → [Integrity, Quality, Lint] → Reports + Catalog
```

- **Inspector**: Discovers files, analyzes structure
- **Integrity**: Validates dependencies, detects issues
- **Quality**: Assesses documentation, maintainability
- **Lint**: Runs linters, checks syntax
- **Reports**: Generates JSON/YAML/Markdown outputs

## Integration Points

- **CognitionKernel**: Routes audits through governance layer
- **FastAPI**: REST API for programmatic access
- **CLI**: Command-line interface with rich output
- **CI/CD**: GitHub Actions workflow integration

## Key Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| Health Score | Overall repository quality | 0-100 |
| Documentation Coverage | Percentage of code with docstrings | 0-100% |
| Maintainability Index | Code maintainability score | 0-100 |
| Cohesion Score | Module organization quality | 0-100% |
| Integrity Issues | Missing imports, dead code, etc. | Count |
| Circular Dependencies | Dependency cycles detected | Count |

## File Status Labels

- `implemented` - Production-ready code
- `planned` - Documented but not implemented
- `future_update` - Needs refactoring/updates
- `deprecated` - Marked for removal
- `not_in_use` - Exists but unused

## Configuration

Create `inspection_config.yaml`:

```yaml
repository:
  root: "."
  exclusions: ["node_modules", "*.log"]

output:
  directory: "audit_reports"
  formats: ["json", "yaml", "markdown"]

integrity:
  check_circular_dependencies: true
  check_dead_code: true

quality:
  min_documentation_coverage: 0.5
  min_maintainability_index: 60.0

lint:
  enabled: true
  tools:
    python: ["ruff", "mypy", "bandit"]
```

## API Endpoints

- `POST /api/v1/inspection/audit` - Start audit
- `GET /api/v1/inspection/audit/{id}` - Get results
- `GET /api/v1/inspection/reports` - List reports
- `GET /api/v1/inspection/reports/{file}` - Download report

## Testing

```bash

# Run tests

pytest tests/inspection/ -v

# With coverage

pytest tests/inspection/ --cov=app.inspection
```

## Performance

- **Small repos (<100 files)**: < 1 second
- **Medium repos (100-1000 files)**: 1-10 seconds
- **Large repos (1000+ files)**: 10-60 seconds

Disable linting for faster audits: `--no-lint`

## Documentation

- **Full Documentation**: `docs/INSPECTION_SYSTEM.md`
- **Architecture**: See `src/app/inspection/__init__.py`
- **Examples**: Run `python inspection_cli.py --help`

## Requirements

- Python 3.11+
- PyYAML
- typer + rich (for CLI)
- fastapi + pydantic (for API)
- Optional: ruff, mypy, bandit (for linting)

## Support

Issues: https://github.com/IAmSoThirsty/Project-AI/issues

---

**Version**: 1.0.0
**Status**: Production-Ready
**Last Updated**: 2026-02-08
