# Sovereignty State Machine

## Overview

This document specifies the state machine for Project-AI's sovereign governance system, including all states, transitions, authorities, preconditions, and invariants.

## States

### ACTIVE

**Description**: Normal operational mode for the system. Constitution can be modified (pre-completion) or is under active development.

**Characteristics**:

- Full system functionality
- User interactions permitted
- AI operations unrestricted
- Governance modifications allowed (pre-completion)
- Ledger recording active

**Entry Conditions**:

- System initialization
- Successful restoration from SUSPENDED
- Completion of refoundation process

**Exit Conditions**:

- Completion seal applied → DEFENSE
- Override triggered → SUSPENDED

### DEFENSE

**Description**: Post-completion immutable governance mode. Constitution is sealed and cannot be modified without explicit override authorization.

**Characteristics**:

- Constitution immutability enforced
- Read-only governance rules
- Full user/AI operations
- ORACLE_SEED locked
- Ledger-only state derivation
- Override protocol available

**Entry Conditions**:

- Completion seal applied (from ACTIVE)
- 10-year convergence criteria met
- All validation checks passed

**Exit Conditions**:

- Override triggered → SUSPENDED

**Invariants**:

- `CONSTITUTION_COMPLETE.seal` file exists
- ORACLE_SEED matches genesis derivation
- All ledger hash chains intact
- No governance rule modifications without override

### SUSPENDED

**Description**: System suspended due to override trigger. Operations halted except for monitoring, audit, and restoration planning.

**Characteristics**:

- Minimal operations only
- Governance frozen
- Override active and being processed
- Restoration plan generation
- Enhanced audit logging
- Stakeholder notifications

**Entry Conditions**:

- Override protocol triggered from ACTIVE or DEFENSE
- Dual confirmation requirement met
- EPS predicate or other override condition satisfied

**Exit Conditions**:

- Restoration approved and executed → ACTIVE
- Refoundation authorized → REFOUNDING

**Invariants**:

- Override record exists in ledger
- System state file indicates SUSPENDED
- No constitution modifications permitted
- Restoration plan documented

### REFOUNDING

**Description**: Genesis reset in progress. System is being rebuilt from new genesis seal with new ORACLE_SEED.

**Characteristics**:

- System offline
- Old ledgers archived
- New genesis seal generated
- New ORACLE_SEED derived
- New keypairs created
- Stakeholder re-registration required

**Entry Conditions**:

- Refoundation authorized from SUSPENDED
- Cryptographic authorization verified
- Super-unanimity vote passed (if applicable)
- Critical security breach or irrecoverable drift

**Exit Conditions**:

- Refoundation complete → ACTIVE

**Invariants**:

- Archive directory created with old ledgers
- New genesis seal cryptographically independent
- New ORACLE_SEED derived from new genesis
- Refoundation event recorded in new ledger
- Link to previous genesis preserved in metadata

### COMPLETE (Entropy State)

**Description**: Entropy monitoring state indicating 10-year convergence achieved. This is a monitoring state, not a system operational state.

**Characteristics**:

- Entropy stabilized for 10+ years
- Slope below threshold (|slope| < 0.01)
- High R-squared (r² > 0.8)
- Near baseline entropy
- Completion criteria met

**Entry Conditions**:

- 10 years of entropy monitoring data
- Stable entropy trend detected
- Convergence metrics satisfied

**Exit Conditions**:

- Entropy creep detected → CREEPING
- Entropy collapse detected → COLLAPSED

## Transitions

### ACTIVE → DEFENSE

**Trigger**: Completion seal applied

**Preconditions**:

- 10-year convergence criteria met
- Entropy stability validated
- All ledger hash chains intact
- System in ACTIVE state (not SUSPENDED/REFOUNDING)
- No critical violations in ledger

**Process**:

1. Run validation checks via `freeze_seal.py`
1. Generate completion seal
1. Append seal to ledger
1. Update system state to DEFENSE
1. Log transition to audit trail

**Authority**: Automated (validation-driven) or Administrator

**Postconditions**:

- System state = DEFENSE
- `CONSTITUTION_COMPLETE.seal` exists
- Constitution immutable by default
- Override protocol available

**Reversibility**: Irreversible (except via refoundation)

### DEFENSE → SUSPENDED

**Trigger**: Override protocol triggered

**Preconditions**:

- System in DEFENSE state
- Override condition met (EPS, invariant violation, etc.)
- Dual confirmation obtained:
  - Internal: Ledger analysis passes
  - External: Signature verification passes
- Override type specified

**Process**:

1. Evaluate override predicate (e.g., EPS)
1. Verify dual confirmation
1. Create override record
1. Sign and append to override ledger
1. Update system state to SUSPENDED
1. Generate restoration plan
1. Notify stakeholders

**Authority**: Dual confirmation (internal + external)

**Postconditions**:

- System state = SUSPENDED
- Override record in ledger
- Restoration plan generated
- Operations halted (except monitoring)

**Reversibility**: Reversible via restoration protocol

### ACTIVE → SUSPENDED

**Trigger**: Override protocol triggered (pre-completion)

**Preconditions**:

- System in ACTIVE state
- Override condition met
- Dual confirmation obtained

**Process**: (Same as DEFENSE → SUSPENDED)

**Authority**: Dual confirmation (internal + external)

**Postconditions**: (Same as DEFENSE → SUSPENDED)

**Reversibility**: Reversible via restoration protocol

### SUSPENDED → ACTIVE

**Trigger**: Restoration approved and executed

**Preconditions**:

- System in SUSPENDED state
- Restoration plan approved
- Dual confirmation for restoration:
  - Internal: Analysis confirms system is restorable
  - External: Signature verification passes
- All restoration steps completed
- Violations resolved

**Process**:

1. Execute restoration steps from plan
1. Verify violation resolution
1. Validate ledger integrity
1. Obtain dual confirmation
1. Update system state to ACTIVE
1. Log restoration to audit trail
1. Resume normal operations

**Authority**: Dual confirmation (internal + external)

**Postconditions**:

- System state = ACTIVE
- Violations resolved
- Ledger integrity intact
- Operations resumed
- Restoration recorded in ledger

**Reversibility**: Can re-suspend if new violations occur

### SUSPENDED → REFOUNDING

**Trigger**: Refoundation authorized

**Preconditions**:

- System in SUSPENDED state
- Refoundation authorization verified:
  - Cryptographic signature from master authority
  - Super-unanimity vote passed (≥95%)
- One of:
  - Multiple restoration attempts failed (3+)
  - System in irrecoverable state
  - Critical security breach
  - Stakeholder mandate

**Process**:

1. Verify authorization signature
1. Create archive directory with timestamp
1. Copy all ledgers to archive
1. Generate new genesis seal
1. Derive new ORACLE_SEED
1. Generate new keypairs
1. Initialize new ledgers with genesis blocks
1. Link new genesis to old in metadata
1. Update system state to REFOUNDING
1. Log refoundation event

**Authority**: Master authority signature + super-unanimity vote

**Postconditions**:

- System state = REFOUNDING
- Old ledgers archived
- New genesis seal created
- New ORACLE_SEED derived
- New system instance initiated
- Refoundation recorded

**Reversibility**: Irreversible (new system instance)

### REFOUNDING → ACTIVE

**Trigger**: Refoundation complete

**Preconditions**:

- System in REFOUNDING state
- New genesis validated
- New ledgers initialized
- Stakeholder re-registration complete (if required)
- New system integrity verified

**Process**:

1. Validate new genesis seal
1. Verify new ORACLE_SEED derivation
1. Check new ledger integrity
1. Confirm stakeholder re-consent
1. Update system state to ACTIVE
1. Announce refoundation completion
1. Enable enhanced monitoring

**Authority**: Automated (validation-driven)

**Postconditions**:

- System state = ACTIVE
- New genesis active
- New ORACLE_SEED in use
- Operations resumed
- Link to previous system preserved

**Reversibility**: Cannot return to old system (new instance)

## State Authorities

### ACTIVE State

**Permitted Authorities**:

- **User**: Full user operations
- **AI System**: Full AI operations (within Four Laws)
- **Administrator**: System configuration, pre-completion governance changes
- **Monitor**: Entropy tracking, invariant checking, audit logging

**Restricted Operations**:

- None (full functionality available)

### DEFENSE State

**Permitted Authorities**:

- **User**: Full user operations
- **AI System**: Full AI operations (within Four Laws)
- **Administrator**: System configuration, monitoring (no governance changes)
- **Monitor**: Entropy tracking, invariant checking, audit logging
- **Override Authority**: Can trigger override protocol

**Restricted Operations**:

- Constitution modification (requires override)
- ORACLE_SEED changes (requires refoundation)
- Ledger tampering (prohibited)
- Bypass mechanisms (prohibited)

### SUSPENDED State

**Permitted Authorities**:

- **Monitor**: Enhanced audit logging, violation tracking
- **Restoration Authority**: Can approve and execute restoration
- **Override Authority**: Can authorize refoundation
- **Auditor**: Read-only access to all ledgers

**Restricted Operations**:

- User operations (blocked)
- AI operations (blocked except monitoring)
- Constitution modification (blocked)
- Normal system operations (blocked)

### REFOUNDING State

**Permitted Authorities**:

- **Refoundation Authority**: Controls genesis reset process
- **Auditor**: Can observe refoundation process

**Restricted Operations**:

- All operations (system offline)
- User access (disabled)
- AI operations (disabled)

## State Preconditions

### ACTIVE

- Genesis seal exists OR system is newly initialized
- No active override OR restoration completed
- Ledgers initialized
- System not in SUSPENDED or REFOUNDING

### DEFENSE

- Completion seal exists (`CONSTITUTION_COMPLETE.seal`)
- 10-year convergence validated
- ORACLE_SEED locked
- Came from ACTIVE state via completion seal

### SUSPENDED

- Override record exists in ledger
- Dual confirmation verified
- Override condition triggered
- Came from ACTIVE or DEFENSE via override trigger

### REFOUNDING

- Refoundation authorization verified
- Archive created
- Came from SUSPENDED state
- Super-unanimity or critical breach condition met

## State Invariants

### Global Invariants (All States)

- Ledger hash chains intact
- ORACLE_SEED derivation matches genesis
- System state file accurately reflects current state
- Audit trail is append-only
- Timestamps monotonically increasing

### ACTIVE Invariants

- No completion seal exists (pre-completion) OR restoration from suspension
- System state = "active"
- Normal operations permitted

### DEFENSE Invariants

- Completion seal exists and is valid
- `CONSTITUTION_COMPLETE.seal` file present
- ORACLE_SEED immutable
- Constitution modification requires override
- System state = "defense"

### SUSPENDED Invariants

- Override record in ledger
- Restoration plan documented
- Normal operations halted
- System state = "suspended"
- Enhanced monitoring active

### REFOUNDING Invariants

- Archive directory exists
- New genesis seal created
- New ORACLE_SEED derived
- Link to old genesis preserved
- System state = "refounding"

## Transition Guards

### Completion Seal Application

```python
def can_apply_completion_seal(system) -> bool:
    return (
        system.state == SystemState.ACTIVE
        and system.ten_year_convergence_met()
        and system.entropy_stable()
        and system.ledgers_intact()
        and system.no_critical_violations()
    )
```

### Override Trigger

```python
def can_trigger_override(system, override_type) -> bool:
    return (
        system.state in [SystemState.ACTIVE, SystemState.DEFENSE]
        and system.override_condition_met(override_type)
        and system.dual_confirmation_verified()
    )
```

### Restoration

```python
def can_restore_from_suspension(system) -> bool:
    return (
        system.state == SystemState.SUSPENDED
        and system.restoration_plan_approved()
        and system.violations_resolved()
        and system.dual_confirmation_verified()
    )
```

### Refoundation Authorization

```python
def can_authorize_refoundation(system) -> bool:
    return (
        system.state == SystemState.SUSPENDED
        and system.refoundation_signature_verified()
        and (
            system.multiple_restoration_failures()
            or system.critical_security_breach()
            or system.super_unanimity_mandate()
        )
    )
```

### Refoundation Completion

```python
def can_complete_refoundation(system) -> bool:
    return (
        system.state == SystemState.REFOUNDING
        and system.new_genesis_validated()
        and system.new_ledgers_initialized()
        and system.stakeholders_re_registered()
    )
```

## Error Handling

### Invalid Transition Attempts

If transition is attempted without meeting preconditions:

1. Log attempt to audit trail
1. Record violation (if applicable)
1. Maintain current state
1. Return error with specific failed precondition
1. Notify administrators

### State Corruption Detection

If state file is corrupted or inconsistent:

1. Load last valid state from ledger
1. Verify against ledger history
1. Reconstruct state from ledger if possible
1. Trigger invariant violation if reconstruction fails
1. Potential override if non-restorable

### Transition Rollback

Some transitions support rollback:

- **SUSPENDED → ACTIVE**: Can re-suspend if new violations
- **ACTIVE → DEFENSE**: Cannot rollback (irreversible seal)
- **REFOUNDING**: Cannot rollback (new system instance)

## Monitoring and Observability

### State Metrics

- Current state duration
- Transition frequency
- Failed transition attempts
- Override trigger count
- Restoration success rate
- Refoundation events

### State Telemetry

```python
state_telemetry = {
    "current_state": system.get_current_state(),
    "state_entry_timestamp": system.state_entry_time,
    "time_in_state": system.time_in_current_state(),
    "last_transition": {
        "from": previous_state,
        "to": current_state,
        "timestamp": transition_time,
        "trigger": transition_trigger
    },
    "override_count": len(override_ledger),
    "restoration_attempts": restoration_count,
    "refoundation_events": refoundation_count
}
```

### State Visualization

States can be visualized in dashboards:

- **ACTIVE**: Green (normal operation)
- **DEFENSE**: Blue (protected mode)
- **SUSPENDED**: Yellow (requires attention)
- **REFOUNDING**: Red (critical operation)

## Integration Points

### With Singularity Override

- Provides override trigger mechanism
- Records override events to ledger
- Manages suspension state
- Handles refoundation protocol

### With Existential Proof

- Detects invariant violations
- Evaluates non-restorability
- Supports restoration validation
- Provides dual-channel verification

### With Entropy Slope Monitor

- Tracks entropy state (COMPLETE, CREEPING, COLLAPSED)
- Validates 10-year convergence
- Monitors stability in DEFENSE mode
- Triggers alerts on entropy anomalies

### With Constitutional Ledger

- Records all state transitions
- Maintains hash chain integrity
- Provides state history
- Enables state reconstruction

## Future States (Reserved)

### UPGRADING (Planned)

Controlled upgrade path for major system changes while maintaining ledger continuity.

### HIBERNATING (Planned)

Long-term dormant state with minimal resource usage while preserving full state.

### ARCHIVED (Planned)

Permanent archival state for historical systems after replacement.

## Appendices

### State Transition Matrix

| From / To      | ACTIVE       | DEFENSE  | SUSPENDED    | REFOUNDING    |
| -------------- | ------------ | -------- | ------------ | ------------- |
| **ACTIVE**     | -            | ✓ (seal) | ✓ (override) | -             |
| **DEFENSE**    | -            | -        | ✓ (override) | -             |
| **SUSPENDED**  | ✓ (restore)  | -        | -            | ✓ (refounder) |
| **REFOUNDING** | ✓ (complete) | -        | -            | -             |

**Legend**:

- ✓ : Transition permitted
- - : Transition not permitted

### Transition Time Bounds

| Transition             | Minimum Duration | Maximum Duration |
| ---------------------- | ---------------- | ---------------- |
| ACTIVE → DEFENSE       | 10 years         | No limit         |
| DEFENSE → SUSPENDED    | Immediate        | Immediate        |
| ACTIVE → SUSPENDED     | Immediate        | Immediate        |
| SUSPENDED → ACTIVE     | Hours            | No limit         |
| SUSPENDED → REFOUNDING | Days             | No limit         |
| REFOUNDING → ACTIVE    | Hours            | Days             |

### State Persistence

All state data persisted to:

- `system_state.json` - Current state and metadata
- `override_ledger.jsonl` - Override trigger history
- `completion_validation.jsonl` - Completion checks
- `entropy_snapshots.jsonl` - Entropy monitoring
- `invariant_violations.jsonl` - Violation records

______________________________________________________________________

**Document Version**: 1.0.0 **Last Updated**: 2026-02-12 **Status**: ACTIVE **Related Documents**:

- CONSTITUTION_COMPLETE.md
- singularity_override.py
- existential_proof.py
- entropy_slope.py
