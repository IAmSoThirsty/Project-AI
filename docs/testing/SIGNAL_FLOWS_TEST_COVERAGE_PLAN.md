# Signal Flows Test Coverage Plan - 100% Target

**File**: `src/app/pipeline/signal_flows.py` (639 lines, 11 functions)  
**Test File**: `tests/test_signal_flows_comprehensive.py`  
**Target**: 100% line, branch, and function coverage  
**Status**: Framework complete, 40/102 tests implemented (39%)

---

## Executive Summary

The signal processing kernel (`signal_flows.py`) is the highest-risk file in the Project-AI monolithic architecture.

**What it handles**:
- PII redaction (GDPR/HIPAA/CCPA compliance)
- Circuit breakers (availability guarantee)  
- Retry logic (operational stability)
- Vault integration (security boundary)
- Audit trail (forensic capability)

**Current Status**: 20% line coverage, 15% branch coverage  
**Target**: 100% line coverage, 100% branch coverage  
**Gap**: 62 tests remaining

---

## Test Implementation Status

### ✅ Implemented (40/102 tests)

1. **Status Code Tests** (7/7) ✅
   - All 5 status codes validated
   - Callers can handle: processed, denied, failed, throttled, ignored

2. **Processing Phases** (6/6) ✅
   - 4-phase pipeline tested
   - Validation → Transcription → Threshold → Retry

3. **Per-Service Retry** (3/10) ⚠️
   - Basic isolation verified
   - Missing: thread safety, reset mechanism, overflow

4. **PII Redaction** (12/15) ⚠️
   - Core patterns covered (email, phone, SSN, IP, IPv6, addresses, credit cards)
   - Missing: international formats, Unicode edge cases

5. **Circuit Breakers** (3/12) ⚠️  
   - State machine tested (CLOSED → OPEN → HALF_OPEN)
   - Missing: integration with actual services

6. **Error Handling** (2/15) ⚠️
   - Basic edge cases (None text, backoff)
   - Missing: comprehensive error paths

7. **Batch Processing** (3/5) ⚠️
   - Main scenarios tested
   - Missing: large batch, all-failure batch

8. **Utility Functions** (4/10) ⚠️
   - Key helpers tested
   - Missing: complete helper coverage

### ❌ Not Implemented (62/102 tests)

- **Integration Tests** (0/15) - CRITICAL GAP
- **Thread Safety** (0/10) - CRITICAL GAP
- **Remaining PII Edge Cases** (3/15)
- **Circuit Breaker Integration** (9/12)
- **Error Path Completion** (13/15)
- **Performance Tests** (10/10)

---

## Critical Gaps Analysis

### 1. Integration Points (0% tested) - CRITICAL BLOCKER

**What's Missing**: Tests verifying subsystem communication

**Required Tests**:
```python
# Error Aggregator → Vault Flush
test_error_aggregator_vault_flush_on_denial()
test_error_aggregator_vault_flush_on_failure()

# Audit Logging
test_audit_logging_validation_phase()
test_audit_logging_transcription_phase()
test_audit_logging_processing_phase()
test_audit_logging_all_status_transitions()

# Incident ID Correlation
test_incident_id_in_response()
test_incident_id_in_audit_events()
test_incident_id_in_vault_entries()

# Vault Integration
test_vault_deduplication()
test_vault_storage_on_denial()
test_vault_storage_on_failure()

# Config Loader
test_config_threshold_loading()
test_config_transcript_enable_flag()
```

**Impact if Missing**:
- ❌ Can't guarantee no data loss
- ❌ Can't guarantee complete audit trail
- ❌ Can't correlate incidents across systems
- ❌ Vault may contain duplicates
- ❌ Config changes may not take effect

### 2. Thread Safety (0% tested) - CRITICAL BLOCKER

**What's Missing**: Concurrent access validation

**Required Tests**:
```python
# Concurrent Signal Processing
test_concurrent_10_signals_same_service()
test_concurrent_10_signals_different_services()
test_concurrent_retry_counter_increments()

# Race Condition Detection
test_retry_tracker_race_conditions()
test_circuit_breaker_race_conditions()
test_incident_id_uniqueness_concurrent()

# Thread Safety Guarantees
test_retry_lock_acquisition()
test_no_deadlocks_under_load()
```

**Impact if Missing**:
- ❌ Race conditions in retry_tracker
- ❌ Duplicate incident IDs possible
- ❌ Circuit breaker state corruption
- ❌ Service isolation broken under load

### 3. Error Paths (0% tested for main function) - CRITICAL BLOCKER

**What's Missing**: process_signal() error handling

**Required Tests**:
```python
# Missing Required Fields
test_signal_missing_signal_id()
test_signal_missing_source()
test_signal_missing_text_and_summary()

# Circuit Breaker OPEN States  
test_validation_circuit_breaker_open()
test_transcription_circuit_breaker_open()
test_processing_circuit_breaker_open()

# Retry Exhaustion
test_retry_exhausted_with_permanent_error()
test_retry_success_on_third_attempt()

# Forbidden Phrases in Transcript
test_forbidden_phrase_in_transcript()
test_pii_in_transcript()
```

**Impact if Missing**:
- ❌ Silent failures on missing fields
- ❌ Undefined behavior when CB open
- ❌ Retry logic not fully validated
- ❌ Transcript validation gaps

---

## Test Execution Plan

### Phase 1: Integration Tests (IMMEDIATE - TODAY)
**Priority**: P0 (CRITICAL)  
**Tests to Add**: 15  
**Expected Coverage Gain**: +25%  
**Time Estimate**: 4 hours

**Tasks**:
1. Create fixtures for all subsystems (vault, audit, aggregator, config)
2. Test error aggregator → vault flush
3. Test audit logging for all phases
4. Test incident ID correlation
5. Test vault deduplication
6. Test config loader integration

**Success Criteria**:
- ✅ All subsystem calls verified
- ✅ Data flows between components tested
- ✅ No untested integration points

### Phase 2: Thread Safety Tests (IMMEDIATE - TODAY)
**Priority**: P0 (CRITICAL)  
**Tests to Add**: 10  
**Expected Coverage Gain**: +15%  
**Time Estimate**: 3 hours

**Tasks**:
1. Setup concurrent test harness
2. Test retry_tracker thread safety
3. Test circuit breaker thread safety
4. Test incident ID uniqueness
5. Verify no race conditions
6. Verify no deadlocks

**Success Criteria**:
- ✅ 100 concurrent signals process correctly
- ✅ No race conditions detected
- ✅ All counters accurate under load

### Phase 3: Error Path Completion (TODAY)
**Priority**: P1 (HIGH)  
**Tests to Add**: 13  
**Expected Coverage Gain**: +20%  
**Time Estimate**: 3 hours

**Tasks**:
1. Test all missing field scenarios
2. Test all circuit breaker OPEN states
3. Test retry exhaustion
4. Test transcript validation
5. Test boundary conditions

**Success Criteria**:
- ✅ All error paths tested
- ✅ All edge cases covered
- ✅ Graceful degradation verified

### Phase 4: PII Edge Cases (TOMORROW)
**Priority**: P1 (HIGH)  
**Tests to Add**: 3  
**Expected Coverage Gain**: +5%  
**Time Estimate**: 1 hour

**Tasks**:
1. Add Japan phone format
2. Add Brazil phone format  
3. Add remaining credit card types
4. Add PO Box addresses
5. Test Unicode in addresses

**Success Criteria**:
- ✅ All international formats covered
- ✅ All card types redacted
- ✅ Unicode handling verified

### Phase 5: Circuit Breaker Integration (TOMORROW)
**Priority**: P2 (MEDIUM)  
**Tests to Add**: 9  
**Expected Coverage Gain**: +10%  
**Time Estimate**: 2 hours

**Tasks**:
1. Test validation CB with actual validation
2. Test transcription CB with actual transcription
3. Test processing CB with actual processing
4. Test recovery scenarios
5. Test metrics reporting

**Success Criteria**:
- ✅ All CBs integrate with services
- ✅ Recovery tested
- ✅ Metrics accurate

### Phase 6: Performance & Remaining (AS NEEDED)
**Priority**: P3 (LOW)  
**Tests to Add**: 12  
**Expected Coverage Gain**: +5%  
**Time Estimate**: 2 hours

---

## Coverage Targets by End of Day

### Today (End of Business)
| Metric | Current | Target | Tests Added |
|--------|---------|--------|-------------|
| Line Coverage | 20% | 80% | +38 tests |
| Branch Coverage | 15% | 75% | Integration + Thread Safety + Errors |
| Integration Tests | 0 | 15 | All subsystems |
| Thread Safety | 0 | 10 | Concurrent access |
| Total Tests | 40 | 78 | +38 |

### Tomorrow (End of Business)
| Metric | Current | Target | Tests Added |
|--------|---------|--------|-------------|
| Line Coverage | 80% | 100% | +24 tests |
| Branch Coverage | 75% | 100% | PII + CB + Performance |
| All Categories | 78 | 102 | Complete |

---

## Risk Mitigation

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Dynamic imports hard to mock | Test failures | Use module-level patches | ⚠️ In Progress |
| Thread timing issues | Flaky tests | Deterministic synchronization | 📋 Planned |
| External deps (Whisper) | Test fragility | Mock all external calls | ✅ Done |
| Long test runtime | Slow CI | Parallelize with pytest-xdist | 📋 Planned |
| Coverage gaps from defensive code | <100% | Document and justify | 📋 As needed |

---

## Quality Gates

### Before Merge
- [ ] ≥90% line coverage
- [ ] ≥85% branch coverage  
- [ ] All P0 tests passing
- [ ] All P1 tests passing
- [ ] No failing tests

### Before Production
- [ ] 100% line coverage
- [ ] 100% branch coverage
- [ ] 100% function coverage
- [ ] All 102 tests passing
- [ ] Thread safety validated
- [ ] Performance benchmarks met
- [ ] Documentation complete

---

## Current Blockers

1. **Mock Strategy** - Dynamic imports need module-level patching (In Progress)
2. **Test Infrastructure** - Need proper fixtures for all subsystems (In Progress)
3. **Time Constraint** - 62 tests remaining, need focused effort (Action: prioritize P0/P1)

---

## Honest Assessment

**Production Ready?** ❌ NO

**Reason**: Critical gaps in:
- Integration testing (0%)
- Thread safety (0%)
- Error path coverage (0% of main function)

**What's Needed**: 38 more tests (P0 + P1) minimum before considering production.

**Current Status**: Architecture excellent, implementation complete, validation incomplete.

**ETA to Production-Ready**: 2 days with focused test implementation.

---

**Document Control**  
**Created**: 2026-02-23  
**Last Updated**: 2026-02-23  
**Owner**: Test Engineering  
**Review Cycle**: Daily until 100% coverage achieved  
**Stakeholder**: Security & Compliance (GDPR/HIPAA implications)
