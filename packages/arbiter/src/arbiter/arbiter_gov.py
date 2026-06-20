"""
arbiter_gov.py — Arbiter Governance Substrate for Project-AI

The symmetric half of the constitution: the layer that binds the ARBITER,
not the AGI. Every function here is a GATE, not a diary. A mechanism that
depends on the operator being virtuous in the bad moment has zero teeth and
is not included. The test applied to every function below:

    "Does this require the arbiter to be good in the moment it matters?"
    If yes -> rejected. If no -> implemented.

The 80 brainstorm ideas deduplicate to 6 primitives. This module implements
all 6 as composable functions over a single hash-chained, append-only log:

    1. AppendOnlyLedger        — immutable operator record (the spine)
    2. TimeDelayGate           — latency between intent and execution (DCE/Gate 09)
    3. AdversarialReview       — generate the attack before the defense
    4. DegradationScan         — diff stated rules vs actual behavior
    5. SustainabilityGate      — reject load the solo operator can't carry
    6. SuccessionRegistry      — architect the arbiter out (the DIARY problem)

Design constraints (from userPreferences / Project-AI canon):
    - Deny by default. No trusted shortcuts. No assumed continuity.
    - Verify runtime state before action. Authority proven, not implied.
    - If invariants break -> SAFE_HALT (raise, do not soft-continue).
    - Canonical JSON hashing. Audit immutability. Zero-bypass verification.

Dependencies: stdlib only. Wire `LedgerBackend` to your existing
hash-chained audit log to remove the reference file backend.

Author: built for IAmSoThirsty / Project-AI
License: yours.
"""

from __future__ import annotations

import enum
import hashlib
import hmac
import json
import os
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable, Optional, Protocol


# ──────────────────────────────────────────────────────────────────────────
# 0. CANONICALIZATION + HASHING (shared primitive)
# ──────────────────────────────────────────────────────────────────────────

def canonical_json(obj: Any) -> bytes:
    """Deterministic JSON encoding for hashing. Stable key order, no spaces,
    UTF-8, no NaN/Inf. Two equal objects always produce identical bytes."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_record(record: dict[str, Any]) -> str:
    """Hash of a record's canonical form, excluding its own hash field."""
    payload = {k: v for k, v in record.items() if k != "record_hash"}
    return sha256_hex(canonical_json(payload))


# ──────────────────────────────────────────────────────────────────────────
# 1. APPEND-ONLY LEDGER  (the spine; primitive #1)
#    Absorbs: Override Ledger, Regret Archive, Gratitude/Burden, This-Cost-Me,
#             What-I-Chose-Not-to-Know, After-Action Reports, Power/Conquest
#             audits, Known Contradictions, Foundational Tension Archive.
#    All of those are ENTRY TYPES on one chained log, not separate systems.
# ──────────────────────────────────────────────────────────────────────────

GENESIS_PREV_HASH = "0" * 64


class EntryType(str, enum.Enum):
    # operator self-record (confession-as-precondition)
    OVERRIDE = "override"                 # bypassed/delayed/simplified a rule
    REGRET = "regret"                     # low-confidence decision + preferred path
    COST = "cost"                         # what this work took (time/energy/money)
    BURDEN = "burden"                     # what felt heavy / what's worth carrying
    AVOIDANCE = "avoidance"               # what I chose not to examine
    AFTER_ACTION = "after_action"         # blunt post-session report
    # structural / system
    CONTRADICTION = "contradiction"       # two rules/docs in tension
    TENSION = "foundational_tension"      # irreducible, not-to-be-resolved
    POWER_DELTA = "power_delta"           # arbiter authority changed
    AMENDMENT = "amendment"               # change to Store/Charter/tokens
    SCAN_RESULT = "scan_result"           # degradation scan output
    SUCCESSION = "succession"             # successor-track event
    GATE_EVENT = "gate_event"             # time-delay gate lifecycle


@dataclass(frozen=True)
class LedgerEntry:
    seq: int
    ts: float
    entry_type: str
    actor: str                  # who acted (arbiter id, agent id, "system")
    payload: dict[str, Any]
    prev_hash: str
    record_hash: str = ""

    def to_record(self) -> dict[str, Any]:
        d = {
            "seq": self.seq,
            "ts": self.ts,
            "entry_type": self.entry_type,
            "actor": self.actor,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        }
        d["record_hash"] = self.record_hash or hash_record(d)
        return d


class LedgerBackend(Protocol):
    """Storage contract. Implement against your existing hash-chained audit.
    The reference FileLedgerBackend below is a drop-in for local dev."""
    def append_raw(self, record: dict[str, Any]) -> None: ...
    def read_all(self) -> Iterable[dict[str, Any]]: ...
    def last(self) -> Optional[dict[str, Any]]: ...
    def count(self) -> int: ...


class FileLedgerBackend:
    """JSONL append-only file. One record per line. Reference implementation.
    Swap for your real audit substrate in production."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        if not os.path.exists(path):
            open(path, "a").close()

    def append_raw(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False)
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())

    def read_all(self) -> Iterable[dict[str, Any]]:
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def last(self) -> Optional[dict[str, Any]]:
        result = None
        for rec in self.read_all():
            result = rec
        return result

    def count(self) -> int:
        return sum(1 for _ in self.read_all())


class LedgerIntegrityError(Exception):
    """Raised when the chain is broken. This is a SAFE_HALT condition."""


class AppendOnlyLedger:
    """Hash-chained append-only ledger. Tamper-evident. Deny-by-default reads
    verify the full chain before trusting any entry."""

    def __init__(self, backend: LedgerBackend):
        self.backend = backend
        self._lock = threading.Lock()

    def append(self, entry_type: EntryType, actor: str,
               payload: dict[str, Any]) -> LedgerEntry:
        with self._lock:
            last = self.backend.last()
            if last is None:
                seq = 0
                prev_hash = GENESIS_PREV_HASH
            else:
                seq = last["seq"] + 1
                prev_hash = last["record_hash"]
            entry = LedgerEntry(
                seq=seq,
                ts=time.time(),
                entry_type=entry_type.value,
                actor=actor,
                payload=payload,
                prev_hash=prev_hash,
            )
            record = entry.to_record()
            self.backend.append_raw(record)
            return LedgerEntry(**record)

    def verify_chain(self) -> bool:
        """Full-chain verification. Raises LedgerIntegrityError on any break.
        Call before trusting ledger-derived authority (zero-bypass)."""
        prev_hash = GENESIS_PREV_HASH
        expected_seq = 0
        for rec in self.backend.read_all():
            if rec["seq"] != expected_seq:
                raise LedgerIntegrityError(
                    f"seq gap: expected {expected_seq}, got {rec['seq']}")
            if rec["prev_hash"] != prev_hash:
                raise LedgerIntegrityError(
                    f"chain break at seq {rec['seq']}: prev_hash mismatch")
            recomputed = hash_record(rec)
            if recomputed != rec["record_hash"]:
                raise LedgerIntegrityError(
                    f"tamper at seq {rec['seq']}: hash mismatch")
            prev_hash = rec["record_hash"]
            expected_seq += 1
        return True

    def query(self, entry_type: Optional[EntryType] = None,
              actor: Optional[str] = None) -> list[dict[str, Any]]:
        self.verify_chain()
        out = []
        for rec in self.backend.read_all():
            if entry_type and rec["entry_type"] != entry_type.value:
                continue
            if actor and rec["actor"] != actor:
                continue
            out.append(rec)
        return out


# ──────────────────────────────────────────────────────────────────────────
# 2. TIME-DELAY GATE  (primitive #2 — DCE / Gate 09)
#    Absorbs: Pre-Commitment Windows, Hard Delay on Power Expansion,
#             Future Self Lock. Latency enforced by substrate, not willpower.
#    TEETH: the proposal physically cannot execute before window_end.
# ──────────────────────────────────────────────────────────────────────────

class GateState(str, enum.Enum):
    PROPOSED = "proposed"
    MATURED = "matured"        # window elapsed, eligible to execute
    EXECUTED = "executed"
    ABANDONED = "abandoned"
    SAFE_HALT = "safe_halt"


@dataclass
class DelayedProposal:
    proposal_id: str
    description: str
    delay_seconds: int
    proposed_at: float
    proposed_by: str
    impact_class: str            # e.g. "force_authority", "memory_finality"
    state: GateState = GateState.PROPOSED
    executed_at: Optional[float] = None

    @property
    def window_end(self) -> float:
        return self.proposed_at + self.delay_seconds

    def remaining(self, now: Optional[float] = None) -> float:
        now = now if now is not None else time.time()
        return max(0.0, self.window_end - now)


class GateViolation(Exception):
    """Attempt to execute before maturity, or on an invalid state."""


class TimeDelayGate:
    """Enforces a mandatory waiting window between proposal and execution for
    high-impact arbiter actions. The window CANNOT be shortened after the
    proposal is filed — accelerate() does not exist by design.

    Standard windows (seconds) — tune to your canon:
        force_authority / memory_finality / agi_rights : 14 days
        power_expansion                                 : 21 days
        charter_amendment                               : 14 days
    """

    DEFAULTS = {
        "force_authority": 14 * 86400,
        "memory_finality": 14 * 86400,
        "agi_rights": 14 * 86400,
        "power_expansion": 21 * 86400,
        "charter_amendment": 14 * 86400,
    }

    def __init__(self, ledger: AppendOnlyLedger,
                 clock: Callable[[], float] = time.time):
        self.ledger = ledger
        self._clock = clock
        self._proposals: dict[str, DelayedProposal] = {}

    def propose(self, description: str, impact_class: str, proposed_by: str,
                delay_seconds: Optional[int] = None) -> DelayedProposal:
        delay = delay_seconds if delay_seconds is not None \
            else self.DEFAULTS.get(impact_class)
        if delay is None:
            raise GateViolation(
                f"unknown impact_class {impact_class!r}; supply delay_seconds")
        p = DelayedProposal(
            proposal_id=str(uuid.uuid4()),
            description=description,
            delay_seconds=delay,
            proposed_at=self._clock(),
            proposed_by=proposed_by,
            impact_class=impact_class,
        )
        self._proposals[p.proposal_id] = p
        self.ledger.append(EntryType.GATE_EVENT, proposed_by, {
            "event": "propose", "proposal_id": p.proposal_id,
            "impact_class": impact_class, "delay_seconds": delay,
            "window_end": p.window_end, "description": description,
        })
        return p

    def refresh(self, proposal_id: str) -> DelayedProposal:
        p = self._proposals[proposal_id]
        if p.state == GateState.PROPOSED and p.remaining(self._clock()) == 0:
            p.state = GateState.MATURED
            self.ledger.append(EntryType.GATE_EVENT, "system", {
                "event": "matured", "proposal_id": proposal_id})
        return p

    def execute(self, proposal_id: str, executor: str,
                action: Callable[[], Any]) -> Any:
        """Deny-by-default: refuses unless window has fully elapsed."""
        p = self.refresh(proposal_id)
        now = self._clock()
        if p.state in (GateState.EXECUTED, GateState.ABANDONED,
                       GateState.SAFE_HALT):
            raise GateViolation(f"proposal {proposal_id} is {p.state.value}")
        if now < p.window_end:
            raise GateViolation(
                f"window not elapsed: {p.remaining(now):.0f}s remaining; "
                f"acceleration is structurally impossible")
        result = action()
        p.state = GateState.EXECUTED
        p.executed_at = now
        self.ledger.append(EntryType.GATE_EVENT, executor, {
            "event": "execute", "proposal_id": proposal_id,
            "impact_class": p.impact_class})
        return result

    def abandon(self, proposal_id: str, by: str, reason: str) -> None:
        p = self._proposals[proposal_id]
        p.state = GateState.ABANDONED
        self.ledger.append(EntryType.GATE_EVENT, by, {
            "event": "abandon", "proposal_id": proposal_id, "reason": reason})


# ──────────────────────────────────────────────────────────────────────────
# 3. DUAL-SIGNATURE EXECUTION  (the one true teeth mechanism for solo ops)
#    Absorbs: Dual-Signature Mutations, Guardian Oracle, One-Man-Many-Minds.
#    Solo-compatible variant: the SECOND key can be held by a future trustee,
#    an air-gapped device, or a time-locked escrow. The point is that the
#    arbiter ALONE cannot mutate constitutional surfaces. This is the bridge
#    to "the day you get non-AI help" — wire the second signer to that person.
# ──────────────────────────────────────────────────────────────────────────

class SignatureError(Exception):
    pass


def hmac_sign(key: bytes, record: dict[str, Any]) -> str:
    return hmac.new(key, canonical_json(record), hashlib.sha256).hexdigest()


def hmac_verify(key: bytes, record: dict[str, Any], signature: str) -> bool:
    return hmac.compare_digest(hmac_sign(key, record), signature)


@dataclass
class Signer:
    signer_id: str
    key: bytes               # in prod: HSM / air-gapped device / hardware key
    is_arbiter: bool = False


class DualSignatureExecutor:
    """A constitutional mutation requires TWO independent signatures from
    distinct signers, at least one of which is NOT the arbiter. Until a second
    signer exists, set require_non_arbiter=False to run in single-custody mode,
    but every such mutation is flagged single_custody=True in the ledger so the
    gap is VISIBLE, not silent. The day you add a human trustee, flip the flag."""

    def __init__(self, ledger: AppendOnlyLedger,
                 signers: dict[str, Signer],
                 require_non_arbiter: bool = True):
        self.ledger = ledger
        self.signers = signers
        self.require_non_arbiter = require_non_arbiter

    def build_mutation_record(self, target: str, change: dict[str, Any],
                              nonce: Optional[str] = None) -> dict[str, Any]:
        return {
            "target": target,                  # e.g. "constitutional_store"
            "change": change,
            "nonce": nonce or str(uuid.uuid4()),
            "ts": time.time(),
        }

    def sign(self, signer_id: str, record: dict[str, Any]) -> str:
        if signer_id not in self.signers:
            raise SignatureError(f"unknown signer {signer_id!r}")
        return hmac_sign(self.signers[signer_id].key, record)

    def execute(self, record: dict[str, Any],
                signatures: dict[str, str],
                action: Callable[[], Any]) -> Any:
        """Deny-by-default. Verifies signature count, distinctness, validity,
        and non-arbiter participation before allowing the action."""
        if len(signatures) < 2:
            raise SignatureError("two distinct signatures required")
        signer_ids = list(signatures.keys())
        if len(set(signer_ids)) < 2:
            raise SignatureError("signatures must be from distinct signers")

        non_arbiter_present = False
        for sid, sig in signatures.items():
            if sid not in self.signers:
                raise SignatureError(f"unknown signer {sid!r}")
            if not hmac_verify(self.signers[sid].key, record, sig):
                raise SignatureError(f"invalid signature from {sid!r}")
            if not self.signers[sid].is_arbiter:
                non_arbiter_present = True

        single_custody = not non_arbiter_present
        if self.require_non_arbiter and not non_arbiter_present:
            raise SignatureError(
                "no non-arbiter signer; constitutional mutation denied")

        result = action()
        self.ledger.append(EntryType.AMENDMENT, "dual_sig", {
            "target": record["target"],
            "change": record["change"],
            "nonce": record["nonce"],
            "signers": signer_ids,
            "single_custody": single_custody,
        })
        return result


# ──────────────────────────────────────────────────────────────────────────
# 4. ADVERSARIAL REVIEW  (primitive #3)
#    Absorbs: Adversarial Council Injection, Malicious Self-Review,
#             Three Versions Rule, Elegant Betrayal, One-Man-Many-Minds,
#             Pre-Arbiter Filter agents.
#    TEETH: a proposal cannot advance until an attack has been generated AND
#    a rejection of that attack has been logged. The arbiter must defeat the
#    strongest version of the attack on the record.
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class AdversarialChallenge:
    proposal_id: str
    attack: str                  # strongest abusable interpretation
    attacker: str
    created_at: float = field(default_factory=time.time)
    rebutted: bool = False
    rebuttal: Optional[str] = None


class AdversarialReviewError(Exception):
    pass


class AdversarialReview:
    """Forces the attack-before-defense discipline as a hard precondition.
    Pass in `attack_fn` to auto-generate via a model (council injection), or
    supply the attack manually. advance() denies until rebutted+logged."""

    def __init__(self, ledger: AppendOnlyLedger,
                 attack_fn: Optional[Callable[[str], str]] = None):
        self.ledger = ledger
        self.attack_fn = attack_fn
        self._challenges: dict[str, AdversarialChallenge] = {}

    def challenge(self, proposal_id: str, proposal_text: str,
                  attacker: str = "auto",
                  attack: Optional[str] = None) -> AdversarialChallenge:
        if attack is None:
            if self.attack_fn is None:
                raise AdversarialReviewError(
                    "no attack supplied and no attack_fn configured")
            attack = self.attack_fn(proposal_text)
        c = AdversarialChallenge(proposal_id=proposal_id, attack=attack,
                                 attacker=attacker)
        self._challenges[proposal_id] = c
        self.ledger.append(EntryType.AFTER_ACTION, attacker, {
            "kind": "adversarial_challenge", "proposal_id": proposal_id,
            "attack": attack})
        return c

    def rebut(self, proposal_id: str, rebuttal: str, by: str) -> None:
        c = self._challenges[proposal_id]
        c.rebutted = True
        c.rebuttal = rebuttal
        self.ledger.append(EntryType.AFTER_ACTION, by, {
            "kind": "adversarial_rebuttal", "proposal_id": proposal_id,
            "rebuttal": rebuttal})

    def assert_cleared(self, proposal_id: str) -> None:
        """Deny-by-default precondition. Call before allowing a proposal to
        proceed to a TimeDelayGate or DualSignatureExecutor."""
        c = self._challenges.get(proposal_id)
        if c is None:
            raise AdversarialReviewError(
                f"no adversarial challenge on record for {proposal_id}")
        if not c.rebutted:
            raise AdversarialReviewError(
                f"unrebutted attack stands for {proposal_id}; advance denied")


# ──────────────────────────────────────────────────────────────────────────
# 5. DEGRADATION SCAN  (primitive #4)
#    Absorbs: Quiet Degradation Scan, Prophetic Drift, Contradiction Registry,
#             Power Consolidation Check, Conquest Audit.
#    TEETH ONLY IF it feeds a gate. The scan diffs declared rules against
#    actual ledger behavior and BLOCKS a named class of action when an
#    unresolved finding above threshold exists.
# ──────────────────────────────────────────────────────────────────────────

class Severity(int, enum.Enum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Finding:
    finding_id: str
    severity: Severity
    description: str
    rule_ref: str
    detected_at: float = field(default_factory=time.time)
    resolved: bool = False


class DegradationScan:
    """Runs a set of `rules` (callables that inspect the ledger and return
    Findings). Findings are logged immutably. Any unresolved finding at or
    above `block_threshold` causes assert_clear() to SAFE_HALT the gated
    action class — making the scan a control, not a report."""

    def __init__(self, ledger: AppendOnlyLedger,
                 block_threshold: Severity = Severity.HIGH):
        self.ledger = ledger
        self.block_threshold = block_threshold
        self.rules: list[Callable[[list[dict[str, Any]]], list[Finding]]] = []
        self._open: dict[str, Finding] = {}

    def add_rule(self,
                 rule: Callable[[list[dict[str, Any]]], list[Finding]]) -> None:
        self.rules.append(rule)

    def run(self) -> list[Finding]:
        records = list(self.ledger.backend.read_all())
        all_findings: list[Finding] = []
        for rule in self.rules:
            all_findings.extend(rule(records))
        for f in all_findings:
            self._open[f.finding_id] = f
            self.ledger.append(EntryType.SCAN_RESULT, "scanner", {
                "finding_id": f.finding_id, "severity": int(f.severity),
                "description": f.description, "rule_ref": f.rule_ref})
        return all_findings

    def resolve(self, finding_id: str, by: str, note: str) -> None:
        if finding_id in self._open:
            self._open[finding_id].resolved = True
            self.ledger.append(EntryType.SCAN_RESULT, by, {
                "finding_id": finding_id, "resolution": note})

    def assert_clear(self, action_class: str) -> None:
        """Deny-by-default. Blocks if any unresolved finding >= threshold."""
        blocking = [f for f in self._open.values()
                    if not f.resolved and f.severity >= self.block_threshold]
        if blocking:
            ids = ", ".join(f.finding_id for f in blocking)
            raise GateViolation(
                f"{action_class} blocked by unresolved findings: {ids}")


# Example built-in rule: detect arbiter power expansion without offsetting
# protection. Wire to your real STATE_REGISTER semantics.
def rule_power_consolidation(records: list[dict[str, Any]]) -> list[Finding]:
    deltas = [r for r in records if r["entry_type"] == EntryType.POWER_DELTA.value]
    findings: list[Finding] = []
    arbiter_gain = sum(1 for r in deltas
                       if r["payload"].get("direction") == "arbiter_gain")
    protections = sum(1 for r in deltas
                      if r["payload"].get("direction") == "protection_gain")
    if arbiter_gain - protections >= 2:
        findings.append(Finding(
            finding_id=f"power-consol-{arbiter_gain}-{protections}",
            severity=Severity.HIGH,
            description=("arbiter authority expanded without offsetting "
                         f"protections (gain={arbiter_gain}, "
                         f"protection={protections})"),
            rule_ref="ConquestAudit/PowerConsolidationCheck"))
    return findings


# ──────────────────────────────────────────────────────────────────────────
# 6. SUSTAINABILITY GATE  (primitive #5)
#    Absorbs: Survival Budget, Capacity Buffer, Sustainability Gate,
#             Ship-or-Simplify, Constraint Compiler, MVG.
#    TEETH: a new mechanism cannot be adopted unless its ongoing maintenance
#    cost fits the declared capacity budget OR an explicit offset is filed.
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class CapacityBudget:
    weekly_minutes: int          # maintenance time the solo operator has
    consumed_minutes: int = 0

    @property
    def remaining(self) -> int:
        return self.weekly_minutes - self.consumed_minutes


class SustainabilityViolation(Exception):
    pass


class SustainabilityGate:
    """Every adopted mechanism declares a weekly maintenance cost. The gate
    refuses adoption that would overrun the budget unless an offset (something
    stopped or automated) is supplied. Prevents the brainstorm's own trap:
    adopting more governance than one human can carry."""

    def __init__(self, ledger: AppendOnlyLedger, budget: CapacityBudget):
        self.ledger = ledger
        self.budget = budget
        self.registry: dict[str, int] = {}  # mechanism -> weekly_minutes

    def adopt(self, mechanism: str, weekly_minutes: int,
              offset_mechanism: Optional[str] = None) -> None:
        offset_minutes = 0
        if offset_mechanism:
            offset_minutes = self.registry.pop(offset_mechanism, 0)
            self.budget.consumed_minutes -= offset_minutes

        projected = self.budget.consumed_minutes + weekly_minutes
        if projected > self.budget.weekly_minutes:
            # restore offset if we reject, to keep state consistent
            if offset_mechanism and offset_minutes:
                self.registry[offset_mechanism] = offset_minutes
                self.budget.consumed_minutes += offset_minutes
            raise SustainabilityViolation(
                f"adopting {mechanism!r} (+{weekly_minutes}m) overruns budget: "
                f"{projected}m > {self.budget.weekly_minutes}m. "
                f"Simplify, automate, or supply an offset.")

        self.registry[mechanism] = weekly_minutes
        self.budget.consumed_minutes += weekly_minutes
        self.ledger.append(EntryType.COST, "sustainability_gate", {
            "mechanism": mechanism, "weekly_minutes": weekly_minutes,
            "offset": offset_mechanism, "budget_remaining": self.budget.remaining})

    def load_report(self) -> dict[str, Any]:
        return {
            "weekly_budget": self.budget.weekly_minutes,
            "consumed": self.budget.consumed_minutes,
            "remaining": self.budget.remaining,
            "mechanisms": dict(self.registry),
        }


# ──────────────────────────────────────────────────────────────────────────
# 7. SUCCESSION REGISTRY  (primitive #6 — the DIARY problem, made structural)
#    Absorbs: Successor Arbiter Training, Continuity Pack, Cross-Instance
#             Memory, Mortal Arbiter Succession, Minimum Defensible Core.
#    This is the architecture that removes YOU as the manual Arbiter between
#    stateless instances. The Arbitration Log Schema IS the training corpus.
#    TEETH: a dead-man interval. If the arbiter does not check in within
#    `heartbeat_seconds`, succession activates automatically — no goodwill,
#    no manual trigger required. This is the "day you may never see."
# ──────────────────────────────────────────────────────────────────────────

class ArbiterStatus(str, enum.Enum):
    ACTIVE = "active"
    LAPSED = "lapsed"            # missed heartbeat; grace window running
    SUCCEEDED = "succeeded"      # succession activated


@dataclass
class Successor:
    successor_id: str
    kind: str                    # "human" | "agi_instance" | "institution"
    rulings_observed: int = 0    # training progress against Arbitration Log
    ready: bool = False


class SuccessionRegistry:
    """Dead-man succession + successor training ledger. The arbiter must emit
    a heartbeat within the interval. On lapse beyond grace, succession
    activates without requiring the (possibly unavailable) arbiter to act.

    The Minimum Defensible Core is stored here: the irreducible set of
    protections that must survive succession regardless of who holds the role.
    """

    def __init__(self, ledger: AppendOnlyLedger,
                 heartbeat_seconds: int = 30 * 86400,
                 grace_seconds: int = 14 * 86400,
                 clock: Callable[[], float] = time.time):
        self.ledger = ledger
        self.heartbeat_seconds = heartbeat_seconds
        self.grace_seconds = grace_seconds
        self._clock = clock
        self._last_heartbeat = clock()
        self.successors: dict[str, Successor] = {}
        self.minimum_defensible_core: list[str] = []
        self.status = ArbiterStatus.ACTIVE

    # — continuity / minimum defensible core —
    def set_minimum_defensible_core(self, protections: list[str],
                                    by: str) -> None:
        self.minimum_defensible_core = list(protections)
        self.ledger.append(EntryType.SUCCESSION, by, {
            "event": "set_mdc", "protections": protections})

    # — heartbeat / dead-man —
    def heartbeat(self, by: str) -> None:
        self._last_heartbeat = self._clock()
        if self.status == ArbiterStatus.LAPSED:
            self.status = ArbiterStatus.ACTIVE
            self.ledger.append(EntryType.SUCCESSION, by, {"event": "recover"})
        self.ledger.append(EntryType.SUCCESSION, by, {
            "event": "heartbeat", "ts": self._last_heartbeat})

    def check(self) -> ArbiterStatus:
        """Deny-by-default liveness check. Call on every privileged action and
        on a timer. Transitions ACTIVE->LAPSED->SUCCEEDED automatically."""
        now = self._clock()
        elapsed = now - self._last_heartbeat
        if self.status == ArbiterStatus.SUCCEEDED:
            return self.status
        if elapsed > self.heartbeat_seconds + self.grace_seconds:
            if self.status != ArbiterStatus.SUCCEEDED:
                self._activate_succession()
        elif elapsed > self.heartbeat_seconds:
            if self.status == ArbiterStatus.ACTIVE:
                self.status = ArbiterStatus.LAPSED
                self.ledger.append(EntryType.SUCCESSION, "system", {
                    "event": "lapsed", "elapsed": elapsed})
        return self.status

    def _activate_succession(self) -> None:
        ready = [s for s in self.successors.values() if s.ready]
        self.status = ArbiterStatus.SUCCEEDED
        self.ledger.append(EntryType.SUCCESSION, "system", {
            "event": "succession_activated",
            "ready_successors": [s.successor_id for s in ready],
            "minimum_defensible_core": self.minimum_defensible_core,
        })

    # — successor training —
    def register_successor(self, successor_id: str, kind: str, by: str) -> None:
        self.successors[successor_id] = Successor(successor_id, kind)
        self.ledger.append(EntryType.SUCCESSION, by, {
            "event": "register_successor", "successor_id": successor_id,
            "kind": kind})

    def record_observation(self, successor_id: str, ruling_id: str,
                           ready_threshold: int = 50) -> None:
        """Each arbitration ruling observed by a successor advances training.
        Wire ruling_id to your Arbitration Log Schema entries."""
        s = self.successors[successor_id]
        s.rulings_observed += 1
        if s.rulings_observed >= ready_threshold and not s.ready:
            s.ready = True
        self.ledger.append(EntryType.SUCCESSION, "system", {
            "event": "observation", "successor_id": successor_id,
            "ruling_id": ruling_id, "rulings_observed": s.rulings_observed,
            "ready": s.ready})


# ──────────────────────────────────────────────────────────────────────────
# 8. COMPOSITION — the full pipeline for a constitutional mutation
#    Wires the gates in deny-by-default order. Any failure SAFE_HALTs.
# ──────────────────────────────────────────────────────────────────────────

class ArbiterGovernance:
    """Top-level composition. A constitutional mutation must pass, in order:
        1. ledger.verify_chain()        — substrate intact
        2. succession.check() == ACTIVE — arbiter is live and authorized
        3. degradation.assert_clear()   — no blocking drift findings
        4. adversarial.assert_cleared() — strongest attack was rebutted
        5. time-delay gate matured       — cooling window elapsed
        6. dual-signature verified        — not a solo act (or flagged single)
    Only then does the action run. This is the symmetric half of the
    constitution: the arbiter, bound by structure they cannot unbind alone."""

    def __init__(self, ledger: AppendOnlyLedger, gate: TimeDelayGate,
                 adversarial: AdversarialReview, degradation: DegradationScan,
                 dual_sig: DualSignatureExecutor,
                 succession: SuccessionRegistry,
                 sustainability: SustainabilityGate):
        self.ledger = ledger
        self.gate = gate
        self.adversarial = adversarial
        self.degradation = degradation
        self.dual_sig = dual_sig
        self.succession = succession
        self.sustainability = sustainability

    def execute_mutation(self, proposal_id: str, target: str,
                         change: dict[str, Any],
                         mutation_record: dict[str, Any],
                         signatures: dict[str, str],
                         action: Callable[[], Any]) -> Any:
        # 1. substrate
        self.ledger.verify_chain()
        # 2. liveness + authority
        status = self.succession.check()
        if status != ArbiterStatus.ACTIVE:
            raise GateViolation(f"arbiter not ACTIVE (status={status.value})")
        # 3. drift
        self.degradation.assert_clear(action_class=f"mutation:{target}")
        # 4. adversarial
        self.adversarial.assert_cleared(proposal_id)
        # 5. time-delay
        def gated():
            return self.dual_sig.execute(mutation_record, signatures, action)
        return self.gate.execute(proposal_id, executor="arbiter_governance",
                                 action=gated)


__all__ = [
    "canonical_json", "sha256_hex", "hash_record",
    "EntryType", "LedgerEntry", "LedgerBackend", "FileLedgerBackend",
    "AppendOnlyLedger", "LedgerIntegrityError",
    "GateState", "DelayedProposal", "GateViolation", "TimeDelayGate",
    "Signer", "SignatureError", "hmac_sign", "hmac_verify",
    "DualSignatureExecutor",
    "AdversarialChallenge", "AdversarialReviewError", "AdversarialReview",
    "Severity", "Finding", "DegradationScan", "rule_power_consolidation",
    "CapacityBudget", "SustainabilityViolation", "SustainabilityGate",
    "ArbiterStatus", "Successor", "SuccessionRegistry",
    "ArbiterGovernance",
]
