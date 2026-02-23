# Signal Processing Kernel - Test Strategy & Coverage Plan

**Module**: `src/app/pipeline/signal_flows.py` (763 lines)  
**Current Tests**: `tests/test_signal_flows_comprehensive.py` (39 tests, ~65% estimated coverage)  
**Target**: 95%+ branch coverage (100% line coverage)  
**Risk Level**: CRITICAL (PII, vault, audit, retry, circuit breakers)

---

## Executive Summary

signal_flows.py is the highest-risk kernel in Project-AI, handling:
- **PII redaction** (regulatory compliance: GDPR, HIPAA)
- **Circuit breakers** (availability protection)
- **Retry logic** (operational stability)
- **Vault integration** (data security)
- **Audit logging** (compliance forensics)

**Key Insight**: Focus on BRANCH coverage, not just line coverage. State machines and pattern matching create combinatorial branching that line coverage alone won't exercise.

---

## Risk-Based Priority Tiers

### Tier 1: CRITICAL (Start Here) - 24 Tests

#### Circuit Breaker Lifecycle (9 tests)
**Why Critical**: A circuit breaker with incorrect state transitions is worse than no circuit breaker. Looks fine until cascading failure hits production.

**Required Tests**:
1. **Validation CB full lifecycle**: CLOSED → (5 failures) → OPEN → (60s timeout) → HALF_OPEN → (3 successes) → CLOSED
2. **Transcription CB full lifecycle**: Same pattern with different thresholds
3. **Processing CB full lifecycle**: Same pattern
4. **HALF_OPEN → OPEN on failure**: Critical edge case - must reopen immediately
5. **Multiple CBs independent**: Validation fails shouldn't affect transcription CB
6. **Recovery timeout precision**: Verify exact 60s/30s/45s timeouts
7. **Success threshold**: Must require exact count (3) in HALF_OPEN
8. **State persistence**: CB state maintained across multiple calls
9. **Concurrent access**: Thread-safe state transitions under load

**Branch Coverage**: 3 states × 3 transitions × 2 outcomes = 18+ branches

#### Integration Tests (15 tests)
**Why Critical**: Validates cross-component contracts. Failures here mean the kernel doesn't integrate correctly with the rest of the system.

**Required Tests**:
1. **Error aggregator → vault** on validation failure (with error details)
2. **Error aggregator → vault** on processing failure (after max retries)
3. **Vault denial reasons**: Verify PII-redacted content stored with reason
4. **Audit log 'denied' status**: Validation failure logged correctly
5. **Audit log 'failed' status**: Max retries logged correctly
6. **Audit log 'throttled' status**: Rate limit logged correctly
7. **Audit log 'processed' status**: Success logged correctly
8. **Audit log 'ignored' status**: Below threshold logged correctly
9. **CB + validation**: Validate circuit breaker protects validation
10. **CB + transcription**: Validate CB protects transcription
11. **CB + processing**: Validate CB protects processing
12. **Config loader**: Live config reload during processing
13. **Redis retry counter**: Global throttling across processes (if Redis available)
14. **Redis fallback**: Graceful degradation when Redis unavailable
15. **incident_id correlation**: UUID present in all audit logs and responses

**Branch Coverage**: 5 status codes × 4 components = 20+ branches

### Tier 2: HIGH (Concurrency Bugs) - 7 Tests

#### Per-Service Retry Isolation
**Why High**: Subtle concurrency bugs in shared state. Can cause one service to throttle all services or vice versa.

**Required Tests**:
1. **Service A throttled, B processes**: Independent limits
2. **Service A resets, B unchanged**: Service-specific reset timing
3. **Concurrent service increments**: Thread-safe counter updates
4. **Lock contention**: Multiple threads incrementing same service
5. **Redis per-service keys**: Separate keys per service in Redis
6. **Global vs service limit**: Both limits enforced independently
7. **Service isolation under load**: 10 services processing concurrently

**Branch Coverage**: 2 tracking modes (Redis/memory) × 2 scopes (global/service) = 4+ branches

### Tier 3: MEDIUM (Coverage-Driven)

**Strategy**: Run coverage after Tier 1 & 2, then fill gaps revealed by branch coverage report.

**Likely Gaps** (based on code structure):
- PII redaction: Pattern match branches (6 redactors × match/no-match)
- process_signal phases: 4 phases × success/failure paths
- Retry backoff: Exponential backoff calculation edge cases
- Threshold checking: Score vs anomaly_score for incidents
- Config integration: Different config values

**Approach**:
```bash
pytest --cov=src.app.pipeline.signal_flows --cov-report=html --cov-branch
# Open htmlcov/signal_flows.py.html
# Look for red/yellow branches
# Write tests to cover them
```

### Tier 4: LOWER RISK (Only if Gaps Remain)

**De-prioritized** (based on actual risk):
- International phone formats beyond UK/Germany (low regulatory risk)
- Large batch tests (100 signals) - scaling issue, not correctness
- Unicode in addresses - edge case with low impact

---

## Coverage Analysis Framework

### High Branch Complexity Components

1. **Circuit Breaker State Machine**: 18+ branches
   - States: CLOSED, OPEN, HALF_OPEN
   - Transitions: success, failure, timeout
   - Outcomes: continue, raise, state change

2. **process_signal() Phases**: 15+ branches
   - Phase 1: Validation (success/CB failure/validation error)
   - Phase 2: Transcription (media/no media, Whisper available/unavailable, success/failure, CB)
   - Phase 3: Threshold (above/below for normal/incident)
   - Phase 4: Retry (1st success, 2nd success, 3rd success, all fail, transient/permanent errors)

3. **PII Redaction Pipeline**: 12+ branches
   - 6 redactors × (pattern match / no match)
   - Configurable enablement (enabled/disabled per redactor)

4. **Retry Tracking**: 8+ branches
   - Redis available/unavailable
   - Global vs service scope
   - Under limit / at limit / over limit
   - Success / transient error / permanent error

5. **Status Code Paths**: 5 distinct outcomes
   - 'processed', 'denied', 'failed', 'throttled', 'ignored'
   - Each with different return structure

### Measuring Success

**Minimum Acceptance Criteria**:
- ✅ 100% line coverage
- ✅ 95%+ branch coverage
- ✅ All Tier 1 tests passing
- ✅ All Tier 2 tests passing
- ✅ Coverage-driven Tier 3 tests for remaining gaps

**Branch Coverage Calculation**:
```
Branch Coverage = (Branches Executed / Total Branches) × 100%
```

**Current Estimate**: 65% branch coverage (39 tests)  
**Target After Tier 1**: 85% branch coverage (+24 tests)  
**Target After Tier 2**: 90% branch coverage (+7 tests)  
**Target After Tier 3**: 95%+ branch coverage (data-driven)

---

## Test Execution Commands

### Run All Tests
```bash
pytest tests/test_signal_flows_comprehensive.py -v
```

### Run with Branch Coverage
```bash
pytest tests/test_signal_flows_comprehensive.py \
  --cov=src.app.pipeline.signal_flows \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-branch
```

### View HTML Coverage Report
```bash
# After running tests with --cov-report=html
open htmlcov/index.html
# Look at "Branch Coverage" column
# Click signal_flows.py to see missed branches highlighted
```

### Run Specific Test Class
```bash
pytest tests/test_signal_flows_comprehensive.py::TestCircuitBreakerLifecycle -v
pytest tests/test_signal_flows_comprehensive.py::TestIntegration -v
```

### Run with Performance Profiling
```bash
pytest tests/test_signal_flows_comprehensive.py --durations=10
```

### Check for Flaky Tests
```bash
# Run tests 10 times to detect flakiness
pytest tests/test_signal_flows_comprehensive.py --count=10

# Run in parallel for speed
pytest tests/test_signal_flows_comprehensive.py -n auto
```

---

## Implementation Checklist

### Phase 1: Tier 1 Tests (24 tests)
- [ ] Write 9 circuit breaker lifecycle tests
- [ ] Write 15 integration tests
- [ ] Run coverage: `pytest --cov-branch`
- [ ] Verify Tier 1 branch coverage ≥ 85%

### Phase 2: Tier 2 Tests (7 tests)
- [ ] Write 7 per-service retry isolation tests
- [ ] Run coverage: `pytest --cov-branch`
- [ ] Verify cumulative branch coverage ≥ 90%

### Phase 3: Coverage-Driven Tier 3
- [ ] Generate HTML coverage report
- [ ] Identify uncovered branches (red/yellow in HTML)
- [ ] Write tests for each uncovered branch
- [ ] Iterate until branch coverage ≥ 95%

### Phase 4: Documentation & Validation
- [ ] Update test documentation
- [ ] Run full test suite: `pytest tests/`
- [ ] Generate final coverage report
- [ ] Store memory about test completion
- [ ] Update IMPLEMENTATION_COMPLETE.md with coverage metrics

---

## Common Pitfalls to Avoid

1. **Line Coverage Trap**: Don't celebrate 100% line coverage if branch coverage is <90%
2. **Test Count Fixation**: 102 tests is a guess. Let coverage guide actual need (probably 50-60 tests)
3. **Speculative Testing**: Don't write "international phone Japan" test if that branch is already covered
4. **Integration Last**: Integration tests should be FIRST, not last
5. **CB Without Lifecycle**: Testing CB in isolation != testing state transitions
6. **Mock Overuse**: Integration tests should use real components where safe
7. **Ignoring Thread Safety**: Retry tracking has shared state - test concurrency
8. **❌ CRITICAL: Timing-Based Concurrent Tests**: Using `time.sleep()` for synchronization creates flaky tests. Use `threading.Barrier` instead.
9. **❌ CRITICAL: Real Sleeps in Tests**: Don't use real `time.sleep(60)` for timeout tests. Mock `time.time()` and `time.sleep()` instead.
10. **❌ Race Conditions**: Concurrent tests without proper synchronization are environment-dependent and flaky.

---

## Success Indicators

**You're done when**:
1. Branch coverage ≥ 95%
2. All Tier 1 tests passing
3. All Tier 2 tests passing
4. Coverage report shows no critical branches missed
5. **Test suite runs in <10 seconds** (with mocked time)
6. **No flaky tests** (run 10 times via `pytest --count=10`, all pass)
7. All concurrent tests use `threading.Barrier` (deterministic)
8. All time-based tests mock `time.time()` and `time.sleep()`

**You can stop before 102 tests if**:
- Branch coverage ≥ 95%
- All critical paths covered
- No obvious gaps in coverage report

---

## References

- Implementation: `src/app/pipeline/signal_flows.py`
- Tests: `tests/test_signal_flows_comprehensive.py`
- Coverage Report: `htmlcov/signal_flows.py.html` (after running with `--cov-report=html`)
- Architecture: `docs/architecture/ENTERPRISE_MONOLITHIC_E2E_ARCHITECTURE.md`

**Last Updated**: 2026-02-23  
**Status**: Tier 1 & 2 tests in progress, coverage-driven approach adopted
