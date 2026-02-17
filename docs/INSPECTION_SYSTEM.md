# Repository Inspection & Audit System

## Institutional-Grade Inspection, Audit, and Cataloging Subsystem

**Version:** 1.0.0 **Author:** Project-AI Team **Date:** 2026-02-08

______________________________________________________________________

## Overview

The Repository Inspection & Audit System provides comprehensive, institution-grade inspection, audit, and cataloging capabilities for the Project-AI monolith. This subsystem delivers:

- **Full repository-wide inventory** and classification of all files, modules, components, and subsystems
- **Automated file errors, lint, markdown, and syntax checks** conforming to best-of-breed standards
- **End-to-end integrity checks** including cross-referenced catalog and dependency analysis
- **Institutional density assessment** quantifying code coverage, documentation, integration, and rigor
- **Comprehensive audit reports** in machine-readable (JSON/YAML) and human-readable (Markdown) formats
- **Strict modular integration** with Project-AI's config-driven infrastructure

______________________________________________________________________

## Architecture

### Core Components

```
src/app/inspection/
├── __init__.py                   # Module exports
├── repository_inspector.py       # File inventory & classification
├── integrity_checker.py          # Dependency analysis & validation
├── quality_analyzer.py           # Density & quality assessment
├── lint_checker.py              # Automated linting & syntax checks
├── report_generator.py          # Machine-readable reports (JSON/YAML)
├── catalog_builder.py           # Human-readable markdown catalogs
├── audit_pipeline.py            # Complete audit orchestration
├── cli.py                       # Command-line interface
└── api.py                       # REST API integration
```

### Component Responsibilities

#### 1. **RepositoryInspector** (`repository_inspector.py`)

- Discovers all files in repository
- Classifies by type (Python, JavaScript, Markdown, etc.)
- Labels status (implemented, planned, future, deprecated, etc.)
- Analyzes Python AST for classes, functions, docstrings
- Identifies logical components and subsystems
- Computes file-level metrics

#### 2. **IntegrityChecker** (`integrity_checker.py`)

- Builds complete dependency graph
- Detects circular dependencies
- Validates all imports
- Identifies dead/unused code
- Generates cross-reference catalog
- Maps module relationships

#### 3. **QualityAnalyzer** (`quality_analyzer.py`)

- Computes documentation coverage
- Calculates maintainability index
- Assesses logical cohesion
- Evaluates architectural rigor
- Generates component quality scores
- Provides improvement recommendations

#### 4. **LintChecker** (`lint_checker.py`)

- Runs Python linters (ruff, flake8, mypy)
- Validates Markdown formatting
- Checks YAML/JSON syntax
- Scans for security issues (bandit)
- Validates file encoding and line endings
- Categorizes issues by severity

#### 5. **ReportGenerator** (`report_generator.py`)

- Generates JSON reports (full detail)
- Generates YAML reports (human-readable)
- Creates summary reports (dashboards)
- Computes overall health score (0-100)
- Assigns letter grade (A-F)
- Provides actionable recommendations

#### 6. **CatalogBuilder** (`catalog_builder.py`)

- Generates institutional-grade markdown
- Creates executive summary
- Builds file inventory tables
- Documents component relationships
- Lists integrity issues
- Provides prioritized recommendations

#### 7. **AuditPipeline** (`audit_pipeline.py`)

- Orchestrates all inspection phases
- Manages execution workflow
- Integrates with CognitionKernel
- Handles error recovery
- Tracks audit progress
- Generates final reports

______________________________________________________________________

## Quick Start

### Command-Line Usage

```bash

# Run full audit on current directory

python inspection_cli.py

# Run audit on specific repository

python inspection_cli.py --repo /path/to/repo

# Customize output location

python inspection_cli.py --output ./my_reports

# Disable specific phases (for speed)

python inspection_cli.py --no-lint --no-quality

# Use custom configuration

python inspection_cli.py --config my_config.yaml

# Verbose output

python inspection_cli.py --verbose
```

### Programmatic Usage

```python
from app.inspection.audit_pipeline import run_audit

# Simple usage

results = run_audit("/path/to/repo")

# With configuration

results = run_audit(
    repo_root="/path/to/repo",
    output_dir="./audit_reports",
    enable_lint=True,
    enable_quality=True,
    enable_integrity=True,
    generate_reports=True,
    generate_catalog=True,
)

# Check results

if results.success:
    print(f"Health Score: {results.overall_assessment['health_score']:.1f}/100")
    print(f"Grade: {results.overall_assessment['grade']}")
    print(f"Reports: {list(results.reports.keys())}")
    print(f"Catalog: {results.catalog_path}")
else:
    print(f"Audit failed: {results.error}")
```

### API Usage

```python
import requests

# Start an audit

response = requests.post(
    "http://localhost:8000/api/v1/inspection/audit",
    json={
        "repo_path": "/path/to/repo",
        "enable_lint": True,
        "generate_reports": True,
    }
)
audit_id = response.json()["audit_id"]

# Check status

response = requests.get(f"http://localhost:8000/api/v1/inspection/audit/{audit_id}")
results = response.json()

print(f"Health Score: {results['overall_health_score']}")
print(f"Grade: {results['grade']}")
```

______________________________________________________________________

## Configuration

### Configuration File

Create `inspection_config.yaml`:

```yaml

# Repository settings

repository:
  root: "."
  exclusions:

    - "*.log"
    - ".cache"

  include_git_metadata: true

# Output settings

output:
  directory: "audit_reports"
  formats: ["json", "yaml", "markdown"]

# Enable/disable phases

inspection:
  enabled: true
integrity:
  enabled: true
quality:
  enabled: true
lint:
  enabled: true

# Thresholds

thresholds:
  health_score:
    excellent: 90  # Grade A
    good: 80       # Grade B
    fair: 70       # Grade C
    poor: 60       # Grade D
```

Load configuration:

```bash
python inspection_cli.py --config inspection_config.yaml
```

______________________________________________________________________

## Output Formats

### Machine-Readable Reports

#### JSON Report (`audit_report_YYYYMMDD_HHMMSS.json`)

Complete detailed report with all inspection data, suitable for programmatic processing.

```json
{
  "metadata": {
    "report_version": "1.0.0",
    "generated_at": "2026-02-08T07:14:02",
    "repository": "/path/to/repo"
  },
  "inspection": { ... },
  "integrity": { ... },
  "quality": { ... },
  "lint": { ... },
  "overall_assessment": {
    "health_score": 85.5,
    "grade": "B",
    "recommendations": [...]
  }
}
```

#### YAML Report (`audit_report_YYYYMMDD_HHMMSS.yaml`)

Human-readable structured format with same data as JSON.

#### Summary Report (`audit_summary_YYYYMMDD_HHMMSS.json`)

Condensed report for dashboards and quick review.

### Human-Readable Catalog

#### Markdown Catalog (`AUDIT_CATALOG_YYYYMMDD_HHMMSS.md`)

Institutional-grade documentation with:

- Executive summary with health score
- Repository statistics
- File inventory (by type)
- Component catalog
- Dependency analysis
- Quality assessment
- Lint findings
- Integrity issues
- Actionable recommendations

______________________________________________________________________

## Health Scoring

### Overall Health Score (0-100)

Computed from four equally-weighted factors:

1. **Documentation** (25 points)

   - Average documentation coverage across files
   - Penalizes missing docstrings

1. **Maintainability** (25 points)

   - Based on maintainability index (0-100)
   - Considers complexity and comment ratio

1. **Integrity** (25 points)

   - Penalizes integrity issues (missing imports, dead code)
   - Penalizes circular dependencies

1. **Lint** (25 points)

   - Penalizes lint errors and warnings
   - Errors weighted higher than warnings

### Letter Grades

| Score Range | Grade | Quality Level |
| ----------- | ----- | ------------- |
| 90-100      | A     | Excellent     |
| 80-89       | B     | Good          |
| 70-79       | C     | Fair          |
| 60-69       | D     | Poor          |
| < 60        | F     | Failing       |

______________________________________________________________________

## Status Classifications

Files and components are classified by status:

| Status          | Description                            |
| --------------- | -------------------------------------- |
| `implemented`   | Fully implemented and in active use    |
| `planned`       | Documented but not yet implemented     |
| `future_update` | Implemented but marked for updates     |
| `not_in_use`    | Implemented but not currently utilized |
| `would_be_nice` | Desirable enhancement                  |
| `could_be_nice` | Optional enhancement                   |
| `should_have`   | Important missing component            |
| `deprecated`    | Marked for removal                     |
| `unknown`       | Status cannot be determined            |

Status detection uses keywords in docstrings and comments:

- `TODO`, `PLANNED`, `NOT YET IMPLEMENTED` → `planned`
- `DEPRECATED`, `OBSOLETE`, `LEGACY` → `deprecated`
- `FUTURE ENHANCEMENT`, `NEEDS REFACTORING` → `future_update`

______________________________________________________________________

## Linting Tools

### Supported Linters

The system auto-detects and uses available linters:

| Tool       | Purpose                        | Language     |
| ---------- | ------------------------------ | ------------ |
| **ruff**   | Fast Python linter (preferred) | Python       |
| **flake8** | Python linter (fallback)       | Python       |
| **mypy**   | Type checker                   | Python       |
| **bandit** | Security scanner               | Python       |
| Built-in   | Markdown validation            | Markdown     |
| Built-in   | YAML/JSON syntax               | Config files |

### Installing Linters

```bash

# Install recommended linters

pip install ruff mypy bandit

# Or use requirements-dev.txt

pip install -r requirements-dev.txt
```

______________________________________________________________________

## Integration Points

### CognitionKernel Integration

When CognitionKernel is available, audits route through it for governance:

```python
from app.core.cognition_kernel import CognitionKernel
from app.inspection.audit_pipeline import AuditPipeline, AuditConfig

kernel = CognitionKernel()
config = AuditConfig(repo_root="/path/to/repo")

pipeline = AuditPipeline(config=config, kernel=kernel)
results = pipeline.run()  # Routes through kernel
```

### API Integration

Add to FastAPI app:

```python
from fastapi import FastAPI
from app.inspection.api import router

app = FastAPI()
app.include_router(router)
```

Endpoints:

- `POST /api/v1/inspection/audit` - Start audit
- `GET /api/v1/inspection/audit/{audit_id}` - Get results
- `GET /api/v1/inspection/reports` - List reports
- `GET /api/v1/inspection/reports/{filename}` - Download report

______________________________________________________________________

## Testing

### Running Tests

```bash

# Run all inspection tests

pytest tests/inspection/ -v

# Run specific test file

pytest tests/inspection/test_repository_inspector.py -v

# Run with coverage

pytest tests/inspection/ --cov=app.inspection --cov-report=html
```

### Test Structure

```
tests/inspection/
├── __init__.py
├── test_repository_inspector.py  # File discovery & analysis tests
├── test_integrity_checker.py     # Dependency & integrity tests
├── test_quality_analyzer.py      # Quality metrics tests
├── test_lint_checker.py          # Linting tests
└── test_audit_pipeline.py        # End-to-end pipeline tests
```

______________________________________________________________________

## Best Practices

### Performance Optimization

1. **Disable unnecessary phases** for faster audits:

   ```bash
   python inspection_cli.py --no-lint  # Skip linting
   ```

1. **Use exclusions** to skip large directories:

   ```yaml
   repository:
     exclusions:

       - "node_modules"
       - "venv"
       - "*.log"

   ```

1. **Run incrementally** during development

1. **Schedule full audits** nightly for CI/CD

### CI/CD Integration

```yaml

# .github/workflows/audit.yml

name: Repository Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v2
      - name: Run Audit

        run: |
          pip install -e .
          python inspection_cli.py --output audit_reports

      - name: Upload Reports

        uses: actions/upload-artifact@v2
        with:
          name: audit-reports
          path: audit_reports/
```

______________________________________________________________________

## Troubleshooting

### Common Issues

#### Import errors

```
ModuleNotFoundError: No module named 'app.inspection'
```

**Solution:** Set PYTHONPATH:

```bash
export PYTHONPATH=src
python inspection_cli.py
```

#### Linting tools not found

```
Lint checking failed: No linters available
```

**Solution:** Install linters:

```bash
pip install ruff mypy bandit
```

#### Permission denied

```
PermissionError: [Errno 13] Permission denied
```

**Solution:** Check output directory permissions:

```bash
chmod 755 audit_reports
```

______________________________________________________________________

## Advanced Usage

### Custom Lint Checker

Extend `LintChecker` for custom rules:

```python
from app.inspection.lint_checker import LintChecker, LintIssue

class CustomLintChecker(LintChecker):
    def _check_custom_rules(self, file_path):
        issues = []
        with open(file_path) as f:
            for i, line in enumerate(f, 1):
                if "bad_pattern" in line:
                    issues.append(LintIssue(
                        file=str(file_path),
                        line=i,
                        severity="warning",
                        rule="custom-001",
                        message="Bad pattern found",
                        source="custom"
                    ))
        return issues
```

### Custom Report Format

Create custom report generators:

```python
from app.inspection.report_generator import ReportGenerator

class CustomReportGenerator(ReportGenerator):
    def generate_html_report(self, data):

        # Generate HTML report

        html = "<html>...</html>"
        output_path = self.output_dir / "audit_report.html"
        output_path.write_text(html)
        return str(output_path)
```

______________________________________________________________________

## API Reference

### AuditConfig

Configuration for audit pipeline:

```python
@dataclass
class AuditConfig:
    repo_root: str | Path
    output_dir: str | Path = "audit_reports"
    exclusions: list[str] | None = None
    enable_lint: bool = True
    enable_quality: bool = True
    enable_integrity: bool = True
    include_git_metadata: bool = True
    generate_reports: bool = True
    generate_catalog: bool = True
    test_results: dict[str, Any] | None = None
```

### AuditResults

Results from audit pipeline:

```python
@dataclass
class AuditResults:
    success: bool
    timestamp: str
    execution_time_seconds: float
    inspection: dict[str, Any] | None
    integrity: dict[str, Any] | None
    quality: dict[str, Any] | None
    lint: dict[str, Any] | None
    reports: dict[str, str] | None
    catalog_path: str | None
    overall_assessment: dict[str, Any] | None
    error: str | None
```

______________________________________________________________________

## Contributing

### Adding New Checkers

1. Create new checker class in `src/app/inspection/`
1. Inherit from appropriate base class
1. Implement required methods
1. Add to `AuditPipeline._do_run()`
1. Update documentation
1. Add tests in `tests/inspection/`

### Extending File Types

To support new file types:

1. Add to `FileType` enum in `repository_inspector.py`
1. Add extension mapping in `EXTENSION_MAP`
1. Implement analysis method (e.g., `_analyze_rust_file`)
1. Add linting support in `lint_checker.py`

______________________________________________________________________

## License

MIT License - Part of Project-AI

______________________________________________________________________

## Support

For issues, questions, or contributions:

- **Issues:** https://github.com/IAmSoThirsty/Project-AI/issues
- **Documentation:** See `PROGRAM_SUMMARY.md`
- **Team:** Project-AI Team

______________________________________________________________________

*Generated by Project-AI Inspection & Audit System v1.0.0*
