# Evidence Harvester Agent

**Status**: ✅ Production Ready  
**Test Coverage**: 20/20 tests passing  
**Lines of Code**: ~750 (implementation) + ~550 (tests)  
**Last Updated**: 2026-05-13

## Quick Start

```python
from app.agents.evidence_harvester import EvidenceHarvesterAgent

# Initialize
agent = EvidenceHarvesterAgent()

# Collect evidence
result = agent.harvest_all_evidence()

# Generate report
report = agent.generate_evidence_report(
    result['evidence_groups'],
    output_format="markdown"
)
print(report)
```

## What It Does

The Evidence Harvester Agent **collects, organizes, and verifies evidence** that Project-AI's behavior is real, tested, and reproducible. It provides:

1. **Structured evidence collection** across 8 categories
2. **Clear proof statements** (what it proves AND what it doesn't prove)
3. **Production vs simulated** evidence separation
4. **Staleness detection** (marks evidence >7 days old)
5. **Missing evidence identification** with remediation steps
6. **Verification commands** for re-running checks
7. **Content hash tracking** (SHA-256) to detect tampering
8. **Actionable recommendations** for evidence health

## Evidence Categories

| Category | Examples | Proof Statements |
|----------|----------|------------------|
| **Test Results** | `.pytest_cache`, `.coverage` | Proves tests ran, NOT that they passed |
| **CI Logs** | GitHub Actions workflows, `ci-reports/` | Proves workflows configured, NOT recent runs |
| **Audit Events** | `audit_log.yaml`, `acceptance_ledger.jsonl` | Proves logging enabled, NOT all checks passed |
| **Governance** | `canonical/scenario.yaml`, drift alerts | Proves scenarios exist, NOT that they pass |
| **Docker** | `Dockerfile`, `docker-compose.yml` | Proves configs exist, NOT successful builds |
| **Runtime Health** | Health endpoints (`/health`) | Proves services running, NOT all systems functional |
| **Denial Proofs** | Denial test suites | Proves tests exist, NOT that they pass |
| **Execution Tickets** | Execution gate implementation | Proves gate exists, NOT all routes use it |

## Key Features

### 🔍 Honest Proof Statements

Every evidence item clearly states:
- ✅ **What it PROVES**: "Pytest has been executed recently"
- ❌ **What it DOES NOT PROVE**: "All tests passed or coverage is adequate"

### 🏭 Production vs Simulated

Filter evidence by quality:
```python
# Production only
result = agent.harvest_all_evidence(include_simulated=False)

# Include test/simulated evidence
result = agent.harvest_all_evidence(include_simulated=True)
```

### ⏰ Staleness Detection

Evidence older than 7 days is marked stale:
```python
item.is_stale  # True if >7 days old
```

### 🔐 Content Hashing

SHA-256 hashes detect content changes:
```python
item.content_hash  # "a3f5b21c... (64 hex chars)"
```

### 📋 Missing Evidence

Identifies expected artifacts that are missing:
```python
missing = agent.find_missing_evidence()
# [{"category": "test_results", "expected_path": ".coverage", "reason": "..."}]
```

### 💡 Recommendations

Actionable guidance:
- "Update 5 stale test_results items by re-running verification commands"
- "Collect 3 missing evidence items (run recommended commands)"
- "Increase production evidence collection (more simulated than production)"

## Files

```
src/app/agents/evidence_harvester.py    # Agent implementation (750 LOC)
tests/test_evidence_harvester.py         # 20 tests (550 LOC)
docs/agents/EVIDENCE_HARVESTER.md        # Full documentation
examples/evidence_harvester_example.py   # Usage examples
```

## Testing

```bash
# Run all tests
pytest tests/test_evidence_harvester.py -v

# Run example
python examples/evidence_harvester_example.py
```

**Test Coverage**: 20 tests covering:
- Initialization and configuration
- Evidence harvesting (all 8 categories)
- Verification workflows
- Report generation (markdown + JSON)
- Missing evidence detection
- Staleness tracking
- Hash-based integrity checks
- Recommendations generation

## Example Output

### Evidence Summary
```
Total evidence items:     23
  ├─ Production:          23
  └─ Simulated:           0
Categories covered:       6
Stale items (>7 days):    0
Missing items:            3
```

### Evidence Item
```
[PROD] ✓ Current - pytest_last_run
  Source: .pytest_cache/v/cache/lastfailed
  Proves: Pytest has been executed recently
  Does NOT Prove: All tests passed or coverage is adequate
  Verify with: pytest -v
  Hash: a3f5b21c...
```

### Report Formats

**Markdown**:
```markdown
## TEST RESULTS

### ✅ pytest_last_run [PRODUCTION]
**Source:** `.pytest_cache/v/cache/lastfailed`
**✅ Proves:** Pytest has been executed recently
**❌ Does NOT Prove:** All tests passed
**Verify with:** `pytest -v`
```

**JSON**:
```json
{
  "test_results": [{
    "item_name": "pytest_last_run",
    "what_it_proves": "Pytest has been executed recently",
    "is_production": true,
    "is_stale": false
  }]
}
```

## Integration

### With CognitionKernel

All operations route through governance:
```python
# Automatically logged to audit trail
result = agent.harvest_all_evidence()
```

### With Other Agents

- **OversightAgent**: Evidence for deny-rate monitoring
- **ValidatorAgent**: Schema compliance verification
- **ExplainabilityAgent**: Explanation generation for gaps

## Use Cases

1. **Compliance Audits**: Generate evidence reports for stakeholders
2. **Quality Assurance**: Track test/CI artifact freshness
3. **Governance Reviews**: Verify governance decision trails
4. **Deployment Verification**: Confirm Docker artifacts before deployment
5. **Continuous Verification**: Detect stale or missing evidence
6. **Security Audits**: Verify denial paths and zero-bypass proofs

## Design Principles

1. **Honesty**: Never overstate what evidence proves
2. **Clarity**: Explicit limitations for every proof statement
3. **Reproducibility**: Verification commands for re-running checks
4. **Integrity**: Content hashing to detect tampering
5. **Actionability**: Recommendations guide remediation
6. **Separation**: Clear distinction between production and simulated

## Governance Compliance

✅ Routes through CognitionKernel  
✅ Logs all actions to audit trail  
✅ Follows KernelRoutedAgent pattern  
✅ No code execution (read-only)  
✅ Path validation before file reads  
✅ Peer-level communication style  

## Limitations

- **Snapshot-based**: Evidence reflects state at harvest time, not continuous
- **Local scope**: Limited to filesystem and localhost services
- **No auto-remediation**: Identifies issues but doesn't fix them
- **File-based**: Does not harvest from external APIs (except health endpoints)

## Next Steps

After installing this agent:

1. Run `python examples/evidence_harvester_example.py`
2. Review generated reports (`evidence_report.md`, `evidence_report.json`)
3. Address missing evidence items
4. Schedule regular harvesting (daily or after major changes)
5. Integrate with CI/CD for automated evidence collection

## License

Part of Project-AI - see repository LICENSE for details.
