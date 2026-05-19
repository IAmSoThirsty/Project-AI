# Evidence Harvester Agent

## Overview

The **Evidence Harvester Agent** collects, organizes, and verifies evidence that Project-AI behavior is real, tested, and reproducible. It provides structured evidence reports with clear proof statements, limitations, and actionable verification recommendations.

## Purpose

- **Transparency**: Make Project-AI's real behavior visible and verifiable
- **Reproducibility**: Track artifacts that prove functionality can be reproduced
- **Quality Assurance**: Separate simulated evidence from production evidence
- **Continuous Verification**: Detect stale or incomplete evidence
- **Audit Trail**: Provide evidence for compliance and governance reviews

## Evidence Categories

The agent harvests evidence across eight categories:

### 1. Test Results
- Pytest execution logs (`.pytest_cache`)
- Coverage reports (`.coverage`, `htmlcov/`)
- Test result artifacts

**Proves**: Tests have been executed  
**Does NOT Prove**: All tests passed or coverage is adequate

### 2. CI Logs
- GitHub Actions workflow configurations
- CI pipeline reports (`ci-reports/`)
- Workflow execution history

**Proves**: CI workflows are configured  
**Does NOT Prove**: Recent successful runs

### 3. Audit Events
- Governance audit log (`governance/audit_log.yaml`)
- Acceptance ledger with RFC 3161 timestamps (`data/acceptance_ledger.jsonl`)

**Proves**: Governance decisions are logged  
**Does NOT Prove**: All events pass governance checks

### 4. Governance Decisions
- Canonical scenario definition (`canonical/scenario.yaml`)
- Governance drift alerts (`data/governance_drift_alerts/`)

**Proves**: Ground truth scenarios exist  
**Does NOT Prove**: Scenarios pass all invariants

### 5. Docker Artifacts
- Dockerfile
- docker-compose.yml configuration

**Proves**: Container build configuration exists  
**Does NOT Prove**: Images build successfully

### 6. Runtime Health
- Triumvirate server health endpoint (`http://localhost:8001/health`)

**Proves**: Services are running and responsive  
**Does NOT Prove**: All systems are functional

### 7. Denial Proofs
- Test files verifying denial paths:
  - `test_four_laws_1000_disallowed_high_level.py`
  - `test_integration_pipeline_blocking.py`
  - `test_boundary.py`

**Proves**: Denial test suites exist  
**Does NOT Prove**: Tests pass or cover all denial paths

### 8. Execution Tickets
- Execution gate implementation (`src/app/core/execution_gate.py`)
- Signed ticket evidence

**Proves**: Ticket signing is implemented  
**Does NOT Prove**: All executions route through gate

## API Reference

### Core Methods

#### `harvest_all_evidence(include_simulated: bool = True, staleness_days: int = 7) -> dict`

Collect all available evidence across all categories.

**Arguments**:
- `include_simulated`: Include simulated/test evidence (default: True)
- `staleness_days`: Mark evidence older than this many days as stale (default: 7)

**Returns**:
```python
{
    "evidence_groups": {
        "test_results": [EvidenceItem, ...],
        "ci_logs": [EvidenceItem, ...],
        # ... other categories
    },
    "summary": {
        "total_items": 42,
        "production_items": 30,
        "simulated_items": 12,
        "stale_items": 5,
        "categories": 8,
        "missing_items": 3
    },
    "missing_evidence": [...],
    "recommendations": [...]
}
```

#### `verify_evidence_item(item: EvidenceItem) -> dict`

Re-verify a single evidence item.

#### `generate_evidence_report(evidence_groups: dict, output_format: str = "markdown") -> str`

Generate human-readable evidence report.

#### `find_missing_evidence() -> list[dict]`

Identify expected evidence that is missing.

## Usage Examples

### Basic Evidence Collection

```python
from app.agents.evidence_harvester import EvidenceHarvesterAgent

# Initialize agent
agent = EvidenceHarvesterAgent()

# Collect all evidence
result = agent.harvest_all_evidence(include_simulated=True)

print(f"Found {result['summary']['total_items']} evidence items")

# Generate markdown report
report = agent.generate_evidence_report(
    result['evidence_groups'],
    output_format="markdown"
)
```

### Production-Only Evidence

```python
result = agent.harvest_all_evidence(include_simulated=False)
prod_count = result['summary']['production_items']
```

### Find Missing Evidence

```python
missing = agent.find_missing_evidence()
for item in missing:
    print(f"Missing: {item['category']} - {item['reason']}")
```

## EvidenceItem Structure

```python
@dataclass
class EvidenceItem:
    category: str               # Evidence category
    item_name: str             # Unique identifier
    source_path: str           # File path or URL
    what_it_proves: str        # Clear proof statement
    what_it_does_not_prove: str  # Explicit limitations
    timestamp: str             # ISO 8601 timestamp
    is_production: bool        # True = production, False = simulated
    is_stale: bool            # True if older than staleness threshold
    verification_command: str | None  # Command to re-verify
    content_hash: str | None  # SHA-256 hash of content
    metadata: dict[str, Any]  # Additional context
```

## Integration with CognitionKernel

All operations route through CognitionKernel for governance tracking:

```python
result = agent.harvest_all_evidence()  # ← Routed through kernel
# Logs action, execution type, risk level to audit trail
```

## Testing

Full test coverage:

```bash
pytest tests/test_evidence_harvester.py -v
```

20 tests covering initialization, harvesting, verification, reporting, and recommendations.

## Best Practices

1. **Run regularly**: Schedule evidence harvesting daily or after major changes
2. **Track staleness**: Re-run verification commands for stale evidence
3. **Separate concerns**: Use `include_simulated=False` for production audits
4. **Verify hashes**: Check content hashes to detect tampering
5. **Act on missing evidence**: Prioritize collection of missing critical evidence

## Security Considerations

- **Path validation**: All file paths validated before reading
- **No code execution**: Evidence collection is read-only
- **Hash verification**: SHA-256 hashes prevent tampering
- **Kernel routing**: All operations log through governance audit trail
