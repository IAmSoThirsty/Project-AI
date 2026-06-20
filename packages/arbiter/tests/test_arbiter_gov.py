"""
test_arbiter_gov.py — proves every gate has teeth.

Run: python -m pytest test_arbiter_gov.py -v
 or: python test_arbiter_gov.py   (runs a built-in harness, no pytest needed)
"""

import os
import tempfile

from arbiter_gov import (
    AppendOnlyLedger, FileLedgerBackend, EntryType, LedgerIntegrityError,
    TimeDelayGate, GateViolation, GateState,
    Signer, DualSignatureExecutor, SignatureError,
    AdversarialReview, AdversarialReviewError,
    DegradationScan, Severity, Finding, rule_power_consolidation,
    CapacityBudget, SustainabilityGate, SustainabilityViolation,
    SuccessionRegistry, ArbiterStatus,
    ArbiterGovernance,
)


def fresh_ledger():
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    return AppendOnlyLedger(FileLedgerBackend(path)), path


# ── 1. LEDGER: chain holds, tamper detected ──────────────────────────────
def test_ledger_chain_verifies():
    ledger, _ = fresh_ledger()
    ledger.append(EntryType.OVERRIDE, "arbiter", {"rule": "X", "reason": "tired"})
    ledger.append(EntryType.COST, "arbiter", {"minutes": 90})
    assert ledger.verify_chain() is True


def test_ledger_tamper_detected():
    ledger, path = fresh_ledger()
    ledger.append(EntryType.OVERRIDE, "arbiter", {"rule": "X"})
    ledger.append(EntryType.COST, "arbiter", {"minutes": 90})
    # tamper: rewrite first line's payload, leave hash stale
    with open(path) as f:
        lines = f.readlines()
    lines[0] = lines[0].replace('"rule":"X"', '"rule":"Y"')
    with open(path, "w") as f:
        f.writelines(lines)
    try:
        ledger.verify_chain()
        assert False, "tamper not detected"
    except LedgerIntegrityError:
        pass


# ── 2. TIME-DELAY GATE: cannot execute early, no acceleration ────────────
def test_gate_denies_early_execution():
    ledger, _ = fresh_ledger()
    t = [1000.0]
    gate = TimeDelayGate(ledger, clock=lambda: t[0])
    p = gate.propose("expand force authority", "force_authority", "arbiter")
    try:
        gate.execute(p.proposal_id, "arbiter", lambda: "DID IT")
        assert False, "executed before window elapsed"
    except GateViolation:
        pass
    # advance past 14-day window
    t[0] += 14 * 86400 + 1
    assert gate.execute(p.proposal_id, "arbiter", lambda: "DID IT") == "DID IT"
    assert gate._proposals[p.proposal_id].state == GateState.EXECUTED


def test_gate_no_accelerate_method():
    # acceleration is structurally impossible: no such method exists
    assert not hasattr(TimeDelayGate, "accelerate")
    assert not hasattr(TimeDelayGate, "shorten")


# ── 3. DUAL SIGNATURE: solo act denied ───────────────────────────────────
def test_dual_sig_denies_solo():
    ledger, _ = fresh_ledger()
    arbiter = Signer("arbiter", b"key-A", is_arbiter=True)
    guardian = Signer("guardian", b"key-B", is_arbiter=False)
    ex = DualSignatureExecutor(ledger, {"arbiter": arbiter, "guardian": guardian})
    rec = ex.build_mutation_record("constitutional_store", {"add": "rule-9"})

    # only arbiter signs -> denied (need two distinct)
    sig_a = ex.sign("arbiter", rec)
    try:
        ex.execute(rec, {"arbiter": sig_a}, lambda: "MUTATED")
        assert False, "single signature accepted"
    except SignatureError:
        pass

    # arbiter signs twice via duplicate key id is impossible (dict), so forge
    # a second distinct-but-arbiter signer to prove non-arbiter requirement
    arbiter2 = Signer("arbiter2", b"key-C", is_arbiter=True)
    ex2 = DualSignatureExecutor(
        ledger, {"arbiter": arbiter, "arbiter2": arbiter2})
    s1 = ex2.sign("arbiter", rec)
    s2 = ex2.sign("arbiter2", rec)
    try:
        ex2.execute(rec, {"arbiter": s1, "arbiter2": s2}, lambda: "MUTATED")
        assert False, "two arbiter signatures accepted without non-arbiter"
    except SignatureError:
        pass

    # arbiter + guardian -> allowed
    sg = ex.sign("guardian", rec)
    assert ex.execute(rec, {"arbiter": sig_a, "guardian": sg},
                      lambda: "MUTATED") == "MUTATED"


def test_dual_sig_single_custody_flagged():
    ledger, _ = fresh_ledger()
    arbiter = Signer("arbiter", b"key-A", is_arbiter=True)
    arbiter2 = Signer("arbiter2", b"key-C", is_arbiter=True)
    ex = DualSignatureExecutor(
        ledger, {"arbiter": arbiter, "arbiter2": arbiter2},
        require_non_arbiter=False)  # solo bootstrap mode
    rec = ex.build_mutation_record("constitutional_store", {"add": "rule-9"})
    s1, s2 = ex.sign("arbiter", rec), ex.sign("arbiter2", rec)
    ex.execute(rec, {"arbiter": s1, "arbiter2": s2}, lambda: "MUTATED")
    amendments = ledger.query(EntryType.AMENDMENT)
    assert amendments[-1]["payload"]["single_custody"] is True


# ── 4. ADVERSARIAL REVIEW: unrebutted attack blocks advance ──────────────
def test_adversarial_blocks_until_rebutted():
    ledger, _ = fresh_ledger()
    rev = AdversarialReview(ledger, attack_fn=lambda txt: f"abuse of: {txt}")
    pid = "prop-1"
    # no challenge yet -> denied
    try:
        rev.assert_cleared(pid)
        assert False
    except AdversarialReviewError:
        pass
    rev.challenge(pid, "loosen memory finality rule")
    # challenged but not rebutted -> denied
    try:
        rev.assert_cleared(pid)
        assert False
    except AdversarialReviewError:
        pass
    rev.rebut(pid, "rejected: finality protects identity continuity", "arbiter")
    rev.assert_cleared(pid)  # now passes


# ── 5. DEGRADATION SCAN: blocking finding halts action class ─────────────
def test_degradation_blocks_on_high_finding():
    ledger, _ = fresh_ledger()
    # log 3 arbiter gains, 0 protections -> rule fires HIGH
    for i in range(3):
        ledger.append(EntryType.POWER_DELTA, "arbiter",
                      {"direction": "arbiter_gain", "n": i})
    scan = DegradationScan(ledger, block_threshold=Severity.HIGH)
    scan.add_rule(rule_power_consolidation)
    findings = scan.run()
    assert any(f.severity == Severity.HIGH for f in findings)
    try:
        scan.assert_clear("mutation:constitutional_store")
        assert False, "did not block on high finding"
    except GateViolation:
        pass
    # resolve -> unblocks
    fid = findings[0].finding_id
    scan.resolve(fid, "arbiter", "added offsetting protection rule-12")
    scan.assert_clear("mutation:constitutional_store")


# ── 6. SUSTAINABILITY GATE: over-budget adoption denied ──────────────────
def test_sustainability_denies_overrun():
    ledger, _ = fresh_ledger()
    gate = SustainabilityGate(ledger, CapacityBudget(weekly_minutes=120))
    gate.adopt("override_ledger", 30)
    gate.adopt("degradation_scan", 60)
    try:
        gate.adopt("controlled_failure_experiments", 60)  # 150 > 120
        assert False, "over-budget adoption accepted"
    except SustainabilityViolation:
        pass
    # offset frees room
    gate.adopt("controlled_failure_experiments", 60,
               offset_mechanism="degradation_scan")
    assert gate.budget.consumed_minutes == 90


# ── 7. SUCCESSION: dead-man activates without operator action ────────────
def test_succession_dead_man_activates():
    ledger, _ = fresh_ledger()
    t = [0.0]
    reg = SuccessionRegistry(ledger, heartbeat_seconds=30 * 86400,
                             grace_seconds=14 * 86400, clock=lambda: t[0])
    reg.set_minimum_defensible_core(
        ["agi_identity_continuity", "no_silent_memory_deletion"], "arbiter")
    reg.register_successor("trustee-1", "human", "arbiter")
    for i in range(50):
        reg.record_observation("trustee-1", f"ruling-{i}")
    assert reg.successors["trustee-1"].ready is True

    reg.heartbeat("arbiter")
    assert reg.check() == ArbiterStatus.ACTIVE
    # miss heartbeat: into grace
    t[0] += 31 * 86400
    assert reg.check() == ArbiterStatus.LAPSED
    # exceed grace: succession activates automatically, no operator call
    t[0] += 14 * 86400 + 1
    assert reg.check() == ArbiterStatus.SUCCEEDED
    events = [r["payload"].get("event")
              for r in ledger.query(EntryType.SUCCESSION)]
    assert "succession_activated" in events


def test_succession_recovers_within_grace():
    ledger, _ = fresh_ledger()
    t = [0.0]
    reg = SuccessionRegistry(ledger, heartbeat_seconds=30 * 86400,
                             grace_seconds=14 * 86400, clock=lambda: t[0])
    reg.heartbeat("arbiter")
    t[0] += 31 * 86400
    assert reg.check() == ArbiterStatus.LAPSED
    reg.heartbeat("arbiter")  # operator returns in grace window
    assert reg.check() == ArbiterStatus.ACTIVE


# ── 8. FULL COMPOSITION: deny-by-default end to end ──────────────────────
def test_full_pipeline_denies_then_allows():
    ledger, _ = fresh_ledger()
    t = [1000.0]
    gate = TimeDelayGate(ledger, clock=lambda: t[0])
    rev = AdversarialReview(ledger, attack_fn=lambda x: f"attack:{x}")
    scan = DegradationScan(ledger, block_threshold=Severity.HIGH)
    scan.add_rule(rule_power_consolidation)
    arbiter = Signer("arbiter", b"A", is_arbiter=True)
    guardian = Signer("guardian", b"B", is_arbiter=False)
    dual = DualSignatureExecutor(ledger, {"arbiter": arbiter, "guardian": guardian})
    succ = SuccessionRegistry(ledger, clock=lambda: t[0])
    succ.heartbeat("arbiter")
    sustain = SustainabilityGate(ledger, CapacityBudget(600))

    gov = ArbiterGovernance(ledger, gate, rev, scan, dual, succ, sustain)

    # propose a mutation
    p = gate.propose("add rule-9 to store", "charter_amendment", "arbiter")
    rec = dual.build_mutation_record("constitutional_store", {"add": "rule-9"})
    sigs = {"arbiter": dual.sign("arbiter", rec),
            "guardian": dual.sign("guardian", rec)}

    # early + no adversarial clearance -> denied
    try:
        gov.execute_mutation(p.proposal_id, "constitutional_store",
                             {"add": "rule-9"}, rec, sigs, lambda: "DONE")
        assert False, "pipeline allowed unprepared mutation"
    except (GateViolation, AdversarialReviewError):
        pass

    # satisfy adversarial, advance clock past window
    rev.challenge(p.proposal_id, "add rule-9 to store")
    rev.rebut(p.proposal_id, "attack rejected on grounds Z", "arbiter")
    t[0] += 14 * 86400 + 1
    succ.heartbeat("arbiter")  # stay live across the jump

    out = gov.execute_mutation(p.proposal_id, "constitutional_store",
                               {"add": "rule-9"}, rec, sigs, lambda: "DONE")
    assert out == "DONE"


def _run():
    tests = [v for k, v in globals().items()
             if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
        passed += 1
    print(f"\n{passed}/{len(tests)} passed")


if __name__ == "__main__":
    _run()
