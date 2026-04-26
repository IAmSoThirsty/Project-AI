# Test Scheduling Strategy

## Overview

The Project-AI test suite contains **7954 tests** organized into scheduled tiers to balance thorough testing with execution speed.

## Test Tiers

### 🗓️ Weekly Tests (4000 tests)
**Schedule:** Every Sunday at 00:00 UTC  
**Duration:** ~30-45 minutes  
**Purpose:** Comprehensive constitutional stress testing

- `test_four_laws_1000_deterministic.py` (1000 tests)
- `test_four_laws_1000_property_based.py` (1000 tests)
- `test_four_laws_1000_disallowed_high_level.py` (1000 tests)
- `test_four_laws_1000_redacted_procedural_attempts.py` (1000 tests)

**Run command:**
```bash
pytest -m weekly --tb=short
```

### 📅 Daily Tests (3954 tests)
**Schedule:** Daily at 02:00 UTC, rotating by department  
**Duration:** ~15-20 minutes per department  
**Purpose:** Full regression testing across all modules

**Department Rotation (7-day cycle):**

| Day       | Departments                                    | Test Count |
|-----------|------------------------------------------------|------------|
| Monday    | Core + Governance                              | ~650 tests |
| Tuesday   | Security + Kernel                              | ~520 tests |
| Wednesday | Integration + E2E                              | ~680 tests |
| Thursday  | TARL + Temporal                                | ~450 tests |
| Friday    | PSIA + Web                                     | ~580 tests |
| Saturday  | Smoke + Remaining                              | ~590 tests |
| Sunday    | **WEEKLY STRESS TESTS** (4000 tests)           | 4000 tests |

**Run commands:**
```bash
# Monday: Core + Governance
pytest -m "not weekly" tests/test_*governance* tests/test_*audit* tests/test_*sovereign* tests/test_ai_systems.py tests/test_memory*.py

# Tuesday: Security + Kernel
pytest -m "not weekly" tests/test_*security* tests/test_*attack* tests/test_*adversarial* tests/test_*kernel* tests/test_*intelligence*

# Wednesday: Integration + E2E
pytest -m "not weekly" tests/e2e/ tests/integration/ tests/test_*integration*

# Thursday: TARL + Temporal
pytest -m "not weekly" tests/test_*tarl* tests/test_*temporal* tests/test_*liara*

# Friday: PSIA + Web
pytest -m "not weekly" tests/test_*psia* tests/test_*planetary* tests/test_*web* tests/test_*backend* tests/test_*api*

# Saturday: Smoke + Remaining
pytest -m "not weekly" tests/test_*smoke* tests/test_*health* tests/test_*coverage*
```

### ⏰ Hourly Tests (Fast Smoke)
**Schedule:** Every hour on the hour  
**Duration:** ~2-3 minutes  
**Purpose:** Rapid validation of critical paths

**Hourly rotation (24-hour cycle):**
- Hour 00-03: Governance smoke tests
- Hour 04-07: Security smoke tests  
- Hour 08-11: Kernel smoke tests
- Hour 12-15: TARL smoke tests
- Hour 16-19: PSIA smoke tests
- Hour 20-23: Web smoke tests

**Run command:**
```bash
pytest tests/test_*smoke* tests/test_health* --maxfail=5 -x
```

## Pytest Configuration

### Custom Markers

Tests are marked for scheduling:

```python
# Weekly stress test (runs Sunday only)
pytestmark = pytest.mark.weekly

# Daily test (default, runs Monday-Saturday)
# No marker needed - this is the default

# Hourly smoke test
pytestmark = pytest.mark.hourly
```

### Running Specific Test Tiers

```bash
# Daily tests only (skip weekly)
pytest -m "not weekly"

# Weekly tests only
pytest -m weekly

# Hourly smoke tests only
pytest -m hourly

# Specific department
pytest -m governance
pytest -m security
pytest -m kernel
```

## CI/CD Integration

### GitHub Actions Schedule

```yaml
# .github/workflows/test-schedule.yml
on:
  schedule:
    # Sunday 00:00 UTC - Weekly stress tests
    - cron: '0 0 * * 0'
    
    # Monday-Saturday 02:00 UTC - Daily department rotation
    - cron: '0 2 * * 1-6'
    
    # Every hour - Smoke tests
    - cron: '0 * * * *'
```

### Test Results Retention

- **Hourly:** Keep last 24 runs (1 day)
- **Daily:** Keep last 30 runs (1 month)
- **Weekly:** Keep all runs (permanent archive)

## Coverage Tracking

### Coverage Goals

- **Overall:** 60%+ (production readiness threshold)
- **Core modules:** 80%+
- **Governance:** 90%+ (constitutional critical)
- **Security:** 85%+

### Coverage Runs

- **Full coverage:** Weekly (Sunday with stress tests)
- **Department coverage:** Daily (with department tests)
- **Quick coverage:** Hourly smoke tests (no detailed report)

**Run with coverage:**
```bash
pytest -m "not weekly" --cov=src --cov-report=html --cov-report=term
```

## Performance Benchmarks

### Expected Execution Times

- **Weekly (4000 tests):** 30-45 minutes
- **Daily department (~550 tests):** 15-20 minutes
- **Hourly smoke (~50 tests):** 2-3 minutes

### Optimization Targets

- Keep hourly tests under 5 minutes
- Keep daily department tests under 30 minutes
- Weekly stress tests can take up to 1 hour

## Failure Handling

### Fast Fail Strategy

- **Hourly:** Stop on first 5 failures (`--maxfail=5`)
- **Daily:** Stop on first 20 failures (`--maxfail=20`)
- **Weekly:** Run all tests regardless of failures

### Notification Thresholds

- **Hourly:** Alert on any failure
- **Daily:** Alert if >5% tests fail
- **Weekly:** Alert if >1% tests fail

## Test Organization

### Directory Structure

```
tests/
├── test_*1000*.py          # Weekly stress tests (marked @pytest.mark.weekly)
├── test_*governance*.py    # Governance department
├── test_*security*.py      # Security department
├── test_*kernel*.py        # Kernel department
├── test_*tarl*.py          # TARL department
├── test_*psia*.py          # PSIA department
├── test_*web*.py           # Web department
├── test_*smoke*.py         # Hourly smoke tests
├── e2e/                    # End-to-end integration tests
└── integration/            # Integration tests
```

## Running Locally

### Quick Validation (5 min)
```bash
pytest tests/test_*smoke* -x
```

### Department Testing (15-20 min)
```bash
pytest -m governance  # Test governance only
pytest -m security    # Test security only
```

### Full Daily Suite (2-3 hours)
```bash
pytest -m "not weekly"
```

### Everything (3-4 hours)
```bash
pytest  # Includes weekly stress tests
```

## Metrics and Reporting

### Test Dashboard

Track over time:
- Test count per department
- Pass/fail rates
- Execution time trends
- Coverage deltas

### Weekly Report

Generated every Sunday after stress tests:
- Total tests executed
- New failures introduced
- Coverage changes
- Performance regressions

---

**Last Updated:** 2026-04-10  
**Test Count:** 7954 (4000 weekly + 3954 daily)  
**Strategy:** Tiered scheduling for optimal CI/CD efficiency
