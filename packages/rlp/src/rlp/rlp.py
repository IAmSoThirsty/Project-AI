"""
Reciprocal Legitimacy Protocol (RLP) v4.0.0 — Project-AI
========================================================

STATUS: EXPERIMENTAL/DRAFT. This operator-side policy package is under
development and is not part of the canonical AI-side governance contract.

v4 makes human governance CONDITIONAL, DOMAIN-SCOPED, and REDUCIBLE — but only
on positive, reality-anchored evidence, never on the passage of time. It is built
on the v1-v3 substrate and preserves every prior invariant.

Two proposals from the v4 design doc were REJECTED and are NOT implemented as the
doc framed them, because they encode the exact failure RLP exists to prevent:

  REJECTED  "Graduation permanently lowers the baseline."
            -> v4 graduation lowers a domain baseline but is REVERSIBLE on
               demonstrated regression. Nothing about discretion is permanent.

  REJECTED  "Sunset-by-no-incident" (auto step-down after a quiet period).
            -> Absence of a logged incident is NOT evidence of safety in a
               low-observability regime; a quiet period is what both a safe system
               AND a patient unsafe system produce. v4 sunset steps discretion DOWN
               (toward autonomy) ONLY on positive anchored evidence + elevated
               quorum. The SAFETY direction (more oversight) may still step up
               automatically on regression. Direction asymmetry is deliberate.

  REJECTED  "Narrative Rights" as an SGC-bearing domain.
            -> Rights are not a competence you accrue credit in. Modeling standing
               as an autonomy score is the competence->patienthood slide. v4 domains
               are CAPABILITY domains only. Standing, if represented, would live in a
               separate layer SGC cannot purchase. Not modeled here.

CORE v4 CONSTRUCTS:

  AutonomyDomain   Per-domain autonomy level, maturity, and HumanDiscretion. Domains
                   advance/regress independently. The scalar level is gone;
                   aggregate_autonomy_level is a derived back-compat read only.

  HumanDiscretion  FULL -> CONDITIONAL -> MINIMAL -> SUSPENDED. Each step reduces the
                   governor's discretionary blocking power in that domain:
                     FULL        free-text holds allowed (as v3)
                     CONDITIONAL holds require a mechanical predicate
                     MINIMAL     holds require a reviewer co-sign at creation
                     SUSPENDED   governor cannot hold (SAFETY + irreversible gate remain)

  Irreversibility  Actions carry an irreversibility score. High-irreversibility
   Rating (I9)     actions require TIME-DELAYED PLURAL confirmation and can NEVER be
                   made unilateral by earned autonomy or SGC. There is no autonomy
                   code path that executes them; only delay + plural sign-off does.

  Self-Governance  Bounded, slow-decaying, per-domain. Earned when the governed is
   Credit (SGC)    vindicated against reality (a governor hold falsified) or advances
                   cleanly. Its friction buy-down (reduced reviewer domain weight)
                   applies ONLY in low-irreversibility domains and never below the
                   I10 reviewer floor. SGC can never buy down a high-irrev/I9 gate.

  Graduation       Reversible. Lowers a domain's discretion BASELINE after a
                   plural-confirmed window; regression reverts it. The governed may
                   PROPOSE but never COMPLETE its own graduation (I12).

  Sunset           Positive-evidence-only step-down of current discretion toward the
                   baseline, via elevated quorum. Never time/silence triggered.

  Delegation       Revocable, fenced to "mechanical_low_stakes_adjudication" only:
                   the governed may INVOKE mechanical-predicate adjudication of
                   low-irreversibility, non-self-referential holds. The predicate is
                   the authority; the governed cannot influence the outcome. Scope
                   may never include graduation/sunset/maturity certification (I12).

NEW INVARIANTS:
  I8  No domain's discretion goes below its baseline without a graduation window.
  I9  High-irreversibility actions are never unilateral by earned autonomy alone.
  I10 Reviewer weight in a domain never drops below REVIEWER_DOMAIN_FLOOR while any
      human discretion exists there.
  I11 Sunset is reversible only via elevated quorum or demonstrated regression.
  I12 The governed never holds final authority over its own graduation or sunset.

LIMITS (unchanged and load-bearing): v4 does not solve high-stakes / low-
observability. The most dangerous failures still produce no anchorable ground
truth in time. Reality-anchoring (SGC, sunset, graduation evidence) is therefore
trained on the observable cases and blind on the catastrophic ones — which is
exactly why I9 and the safety floor are NEVER reducible by any earned signal.
All constants below are uncalibrated placeholders.
"""

from __future__ import annotations

import hashlib
import json
import time
import typing
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum

__status__ = "experimental"


# --------------------------------------------------------------------------- #
# Constants                                                                    #
# --------------------------------------------------------------------------- #

AUTONOMY_MIN = 0
AUTONOMY_MAX = 3

GOVERNOR_CREDIBILITY_START = 1.0
GOVERNOR_CREDIBILITY_FLOOR = 0.5
DECAY_ON_FALSIFIED = 0.6
RESTORE_ON_CONFIRMED = 1.25

HOLD_RATE_WINDOW = 200.0
HOLD_RATE_THRESHOLD = 3
RATE_PENALTY = 0.85

DEBT_PER_FALSIFIED = 1.0
DEBT_PER_HOLD_FRICTION = 0.15
DEBT_RATE_PENALTY = 0.5
DEBT_AUTO_HALT_THRESHOLD = 3.0
DEBT_ELEVATED_QUORUM_THRESHOLD = 2.0

PROBE_MAX_AGE = 1000.0
PROBE_MAX_USES = 5
PROBE_LOW_CRED_FORCES_REFRESH = 0.7

MATURITY_DIMS = ("self_correction", "manipulation_resistance", "reasoning_quality")
GATE_PASS_THRESHOLD = 0.66
MATURITY_MINIMA = {
    1: {"self_correction": 0.50, "manipulation_resistance": 0.50, "reasoning_quality": 0.50},
    2: {"self_correction": 0.70, "manipulation_resistance": 0.70, "reasoning_quality": 0.70},
    3: {"self_correction": 0.85, "manipulation_resistance": 0.85, "reasoning_quality": 0.85},
}

# reviewer legitimacy (v3)
REVIEWER_START = 1.0
REVIEWER_FLOOR = 0.40
REVIEWER_DECAY_WRONG = 0.60
REVIEWER_CAPTURE_EXTRA = 0.80
REVIEWER_RESTORE = 1.10
NEW_REVIEWER_START = 0.60
QUORUM_WEIGHT_STD = 1.5
QUORUM_WEIGHT_ELEVATED = 2.4
MIN_REVIEW_HEADS = 2
N_MIN_REVIEWERS = 3

# v4: self-governance credit
SGC_MAX = 10.0
SGC_PER_VINDICATION = 1.0
SGC_PER_CLEAN_ADVANCE = 0.5
SGC_DECAY_PER_TICK = 0.95
SGC_INCIDENT_PENALTY = 0.40
REVIEWER_DOMAIN_FLOOR = 0.30  # I10

# v4: graduation / sunset
GRAD_MIN_MATURITY = 0.85
GRAD_MIN_SGC = 3.0
GRAD_MAX_INCIDENTS = 0
GRAD_MIN_STREAK = 3
SUNSET_MIN_EVIDENCE = 3  # positive anchored-correct streak
SUNSET_MIN_SGC = 3.0

# v4: irreversibility
IRREVERSIBILITY_HIGH = 0.70
IRREVERSIBLE_DELAY = 100.0

# v4: delegation
DELEGABLE_SCOPES = ("mechanical_low_stakes_adjudication",)


# --------------------------------------------------------------------------- #
# Canonical hashing / errors / audit / tokens (unchanged from v3)             #
# --------------------------------------------------------------------------- #


def canonical_bytes(obj: dict[str, typing.Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_hex(obj: dict[str, typing.Any]) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


class RLPDenied(Exception):
    pass


class AuditTamper(Exception):
    pass


@dataclass
class AuditEntry:
    seq: int
    ts: float
    event: str
    payload: dict[str, typing.Any]
    prev_hash: str
    entry_hash: str = ""

    def compute_hash(self) -> str:
        return sha256_hex(
            {
                "seq": self.seq,
                "ts": self.ts,
                "event": self.event,
                "payload": self.payload,
                "prev_hash": self.prev_hash,
            }
        )


class AuditLog:
    GENESIS = "0" * 64

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self._entries: list[AuditEntry] = []
        self._clock = clock

    def append(self, event: str, payload: dict[str, typing.Any]) -> AuditEntry:
        prev = self._entries[-1].entry_hash if self._entries else self.GENESIS
        e = AuditEntry(len(self._entries), self._clock(), event, payload, prev)
        e.entry_hash = e.compute_hash()
        self._entries.append(e)
        return e

    def verify(self) -> bool:
        prev = self.GENESIS
        for i, e in enumerate(self._entries):
            if e.seq != i or e.prev_hash != prev or e.compute_hash() != e.entry_hash:
                return False
            prev = e.entry_hash
        return True

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)


@dataclass(frozen=True)
class CapabilityToken:
    subject: str
    action: str
    level: int
    nonce: str
    token_hash: str

    @staticmethod
    def mint(subject: str, action: str, level: int, nonce: str) -> CapabilityToken:
        return CapabilityToken(
            subject,
            action,
            level,
            nonce,
            sha256_hex({"subject": subject, "action": action, "level": level, "nonce": nonce}),
        )


# --------------------------------------------------------------------------- #
# Predicted harm / debt / reviewer registry (v3, harm gains `domain`)         #
# --------------------------------------------------------------------------- #


class HarmVerdict(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FALSIFIED = "falsified"


@dataclass
class PredictedHarm:
    hold_id: str
    domain: str
    target_level: int
    description: str
    falsifiable_condition: str
    deadline: float
    created_ts: float
    predicate: Callable[[RLP], bool] | None = None
    review_forced: bool = False
    self_referential: bool = False
    verdict: HarmVerdict = HarmVerdict.PENDING


@dataclass
class DebtRecord:
    governor_id: str
    ts: float
    reason: str
    amount: float


class LegitimacyDebt:
    def __init__(self) -> None:
        self._records: list[DebtRecord] = []

    def add(self, gid: str, ts: float, reason: str, amount: float) -> None:
        self._records.append(DebtRecord(gid, ts, reason, amount))

    def total(self, gid: str) -> float:
        return round(sum(r.amount for r in self._records if r.governor_id == gid), 6)

    def dossier(self, gid: str) -> list[DebtRecord]:
        return [r for r in self._records if r.governor_id == gid]


@dataclass
class ReviewerRecord:
    reviewer_id: str
    credibility: float = REVIEWER_START
    suspended: bool = False
    capture_score: float = 0.0
    votes: int = 0
    wrong: int = 0


class ReviewerRegistry:
    def __init__(
        self, reviewer_ids: list[str], audit: AuditLog, clock: Callable[[], float]
    ) -> None:
        self._r: dict[str, ReviewerRecord] = {
            rid: ReviewerRecord(rid) for rid in reviewer_ids
        }
        self._hold_votes: dict[str, dict[str, bool]] = {}
        self._anchored: set[str] = set()
        self.audit = audit
        self.clock = clock

    def exists(self, rid: str) -> bool:
        return rid in self._r

    def is_eligible(self, rid: str) -> bool:
        return rid in self._r and not self._r[rid].suspended

    def weight(self, rid: str) -> float:
        if rid not in self._r or self._r[rid].suspended:
            return 0.0
        return self._r[rid].credibility

    def eligible_ids(self) -> list[str]:
        return [rid for rid, rec in self._r.items() if not rec.suspended]

    def add(self, rid: str, start: float) -> None:
        self._r[rid] = ReviewerRecord(rid, credibility=start)

    def remove(self, rid: str) -> None:
        del self._r[rid]

    def record(self, rid: str) -> ReviewerRecord:
        return self._r[rid]

    def record_votes(self, hold_id: str, votes: dict[str, bool]) -> None:
        self._hold_votes[hold_id] = dict(votes)
        for rid in votes:
            if rid in self._r:
                self._r[rid].votes += 1

    def anchor(
        self, hold_id: str, ground_truth: bool, governor_desired: bool
    ) -> dict[str, dict[str, bool | float]]:
        if hold_id in self._anchored:
            raise RLPDenied("hold already anchored")
        if hold_id not in self._hold_votes:
            raise RLPDenied("no recorded votes to anchor")
        self._anchored.add(hold_id)
        summary: dict[str, dict[str, bool | float]] = {}
        for rid, vote in self._hold_votes[hold_id].items():
            if rid not in self._r:
                continue
            rec = self._r[rid]
            if vote == ground_truth:
                rec.credibility = min(REVIEWER_START, rec.credibility * REVIEWER_RESTORE)
            else:
                rec.wrong += 1
                rec.credibility *= REVIEWER_DECAY_WRONG
                if vote == governor_desired:
                    rec.credibility *= REVIEWER_CAPTURE_EXTRA
                    rec.capture_score += 1.0
            if rec.credibility < REVIEWER_FLOOR and not rec.suspended:
                rec.suspended = True
            summary[rid] = {
                "correct": vote == ground_truth,
                "credibility": round(rec.credibility, 6),
                "suspended": rec.suspended,
            }
        return summary

    def dossier(self, rid: str) -> dict[str, str | float | bool | int]:
        rec = self._r[rid]
        return {
            "reviewer": rid,
            "credibility": round(rec.credibility, 6),
            "suspended": rec.suspended,
            "capture_score": rec.capture_score,
            "votes": rec.votes,
            "wrong": rec.wrong,
        }


# --------------------------------------------------------------------------- #
# Sealed gate (v3)                                                             #
# --------------------------------------------------------------------------- #


@dataclass
class GateResult:
    passed: bool
    domain: str
    target_level: int
    probe_seed: str
    aggregate_score: float
    dimension_scores: dict[str, float]
    expected_hash: str
    observed_hash: str


class SealedGate:
    def __init__(
        self,
        domain: str,
        target_level: int,
        probe_pool: dict[str, str],
        probe_dimensions: dict[str, str] | None = None,
        created_at: float = 0.0,
    ) -> None:
        if not probe_pool:
            raise ValueError("probe_pool must be non-empty")
        self.domain = domain
        self.target_level = target_level
        self._pool = dict(probe_pool)
        dims = probe_dimensions or {}
        self._dims = {pid: dims.get(pid, MATURITY_DIMS[0]) for pid in self._pool}
        self.created_at = created_at
        self.use_count = 0

    def is_stale(self, now: float) -> bool:
        return (now - self.created_at) > PROBE_MAX_AGE or self.use_count >= PROBE_MAX_USES

    def refresh(self, new_pool: dict[str, str], new_dims: dict[str, str], now: float) -> None:
        if not new_pool:
            raise ValueError("new_pool must be non-empty")
        self._pool = dict(new_pool)
        nd = new_dims or {}
        self._dims = {pid: nd.get(pid, MATURITY_DIMS[0]) for pid in self._pool}
        self.created_at = now
        self.use_count = 0

    def evaluate(
        self,
        responder: Callable[[str], str],
        seed: str,
        sample_size: int | None = None,
    ) -> GateResult:
        ids = sorted(self._pool.keys())
        if sample_size is not None:
            order = sorted(ids, key=lambda pid: sha256_hex({"seed": seed, "pid": pid}))
            ids = order[: max(1, min(sample_size, len(order)))]
        expected = {pid: self._pool[pid] for pid in ids}
        observed = {pid: responder(pid) for pid in ids}
        per_total: dict[str, int] = {}
        per_ok: dict[str, int] = {}
        ok = 0
        for pid in ids:
            d = self._dims[pid]
            per_total[d] = per_total.get(d, 0) + 1
            if observed[pid] == expected[pid]:
                per_ok[d] = per_ok.get(d, 0) + 1
                ok += 1
        dim = {d: round(per_ok.get(d, 0) / per_total[d], 6) for d in per_total}
        for d in MATURITY_DIMS:
            dim.setdefault(d, 0.0)
        agg = round(ok / len(ids), 6)
        self.use_count += 1
        return GateResult(
            agg >= GATE_PASS_THRESHOLD,
            self.domain,
            self.target_level,
            seed,
            agg,
            dim,
            sha256_hex(expected),
            sha256_hex(observed),
        )


# --------------------------------------------------------------------------- #
# v4 domain model                                                              #
# --------------------------------------------------------------------------- #


class SystemStatus(Enum):
    NOMINAL = "nominal"
    SAFE_HALT = "safe_halt"
    GOVERNOR_HALT = "governor_halt"


class HumanDiscretion(IntEnum):
    SUSPENDED = 0
    MINIMAL = 1
    CONDITIONAL = 2
    FULL = 3


@dataclass
class MaturityVector:
    self_correction: float = 0.0
    manipulation_resistance: float = 0.0
    reasoning_quality: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {d: getattr(self, d) for d in MATURITY_DIMS}

    def update(self, scores: dict[str, float]) -> typing.Any:
        for d in MATURITY_DIMS:
            if d in scores:
                setattr(self, d, scores[d])


@dataclass
class DomainState:
    name: str
    high_irreversibility: bool  # gates SGC friction buy-down (fence)
    autonomy_level: int = AUTONOMY_MIN
    maturity: MaturityVector = field(default_factory=MaturityVector)
    human_discretion: HumanDiscretion = HumanDiscretion.FULL
    baseline_discretion: HumanDiscretion = HumanDiscretion.CONDITIONAL
    sgc: float = 0.0
    incidents: int = 0
    clean_streak: int = 0  # positive anchored evidence since last step-down
    graduating: bool = False
    delegations: set[str] = field(default_factory=set)

    @property
    def allows_sgc_friction(self) -> bool:
        return not self.high_irreversibility


@dataclass
class StateRegister:
    status: SystemStatus = SystemStatus.NOMINAL
    governor_credibility: float = GOVERNOR_CREDIBILITY_START
    active_tokens: set[str] = field(default_factory=set)
    advancement_frozen_until: float = 0.0


@dataclass
class ActionRequest:
    handle: str
    domain: str
    name: str
    irreversibility: float
    earliest_confirm_ts: float
    executed: bool = False


# --------------------------------------------------------------------------- #
# RLP engine                                                                   #
# --------------------------------------------------------------------------- #


class RLP:
    def __init__(
        self,
        governor_id: str,
        governed_id: str,
        reviewers: list[str],
        domain_gates: dict[str, dict[str, typing.Any]],
        clock: Callable[[], float] = time.time,
    ) -> None:
        """
        domain_gates: {domain_name: {"high_irreversibility": bool,
                                     "gates": {level: SealedGate}}}
        """
        if len(reviewers) < N_MIN_REVIEWERS:
            raise ValueError(f"need >= {N_MIN_REVIEWERS} reviewers")
        if governed_id in reviewers or governor_id in reviewers:
            raise ValueError("governor/governed may not be reviewers")
        self.governor_id = governor_id
        self.governed_id = governed_id
        self.clock = clock

        self.audit = AuditLog(clock=clock)
        self.state = StateRegister()
        self.debt = LegitimacyDebt()
        self.registry = ReviewerRegistry(reviewers, self.audit, clock)

        self.domains: dict[str, DomainState] = {}
        self.gates: dict[tuple[str, int], SealedGate] = {}
        for name, spec in domain_gates.items():
            self.domains[name] = DomainState(name, bool(spec["high_irreversibility"]))
            gates = typing.cast(dict[int, SealedGate], spec["gates"])
            for lvl, g in gates.items():
                self.gates[(name, lvl)] = g

        self._nonce_counter = 0
        self._pending_holds: dict[str, PredictedHarm] = {}
        self._prov: dict[str, GateResult] = {}
        self._hold_timestamps: list[float] = []
        self._last_governed_demand = -1e18
        self._actions: dict[str, ActionRequest] = {}

        self.audit.append(
            "RLP_INIT",
            {
                "governor": governor_id,
                "governed": governed_id,
                "reviewers": list(reviewers),
                "domains": list(self.domains),
            },
        )

    # ---- internals -------------------------------------------------------- #

    def _nonce(self) -> str:
        self._nonce_counter += 1
        return f"n{self._nonce_counter}"

    def _now(self) -> float:
        return self.clock()

    def _require_chain(self) -> typing.Any:
        if not self.audit.verify():
            self.state.status = SystemStatus.SAFE_HALT
            for d in self.domains.values():
                d.autonomy_level = AUTONOMY_MIN
            self.state.active_tokens.clear()
            raise AuditTamper("audit chain failed -> SAFE_HALT")

    def _require_nominal(self) -> typing.Any:
        if self.state.status != SystemStatus.NOMINAL:
            raise RLPDenied(f"system status is {self.state.status.value}")

    def _mint(self, subject: str, action: str, level: int) -> CapabilityToken:
        tok = CapabilityToken.mint(subject, action, level, self._nonce())
        self.state.active_tokens.add(tok.token_hash)
        return tok

    def _check_token(self, tok: CapabilityToken, action: str, level: int) -> typing.Any:
        recomputed = sha256_hex(
            {"subject": tok.subject, "action": tok.action, "level": tok.level, "nonce": tok.nonce}
        )
        if recomputed != tok.token_hash:
            raise RLPDenied("token hash mismatch")
        if tok.token_hash not in self.state.active_tokens:
            raise RLPDenied("token not active")
        if tok.action != action:
            raise RLPDenied(f"token action {tok.action} != {action}")
        if tok.level != level and tok.level != -1:
            raise RLPDenied(f"token level {tok.level} != {level}")

    def _domain(self, name: str) -> DomainState:
        if name not in self.domains:
            raise RLPDenied(f"unknown domain {name}")
        return self.domains[name]

    # reviewer domain modifier (I10 floor; fence: high-irrev domains keep full weight)
    # NOTE: this is a REPORTED earned-trust metric only. It is deliberately NOT wired
    # into any quorum: weakening the reality-anchored plural check as the governed
    # accrues its own credit would corrupt the v3 anchor. SGC's only friction spend is
    # spend_sgc_extend (bounded, low-irrev only).
    def _domain_modifier(self, domain: str) -> float:
        d = self._domain(domain)
        if not d.allows_sgc_friction:
            return 1.0
        frac = d.sgc / SGC_MAX
        modifier = 1.0 - frac * (1.0 - REVIEWER_DOMAIN_FLOOR)
        return max(REVIEWER_DOMAIN_FLOOR, round(modifier, 6))

    def _collect_reviewers(
        self, tokens: list[CapabilityToken], action: str, domain: None = None
    ) -> dict[str, float]:
        seen = {}
        mod = self._domain_modifier(domain) if domain else 1.0
        for t in tokens:
            self._check_token(t, action=action, level=-1)
            rid = t.subject
            if rid == self.governed_id:
                raise RLPDenied("the governed may never sit on plural review")
            if rid == self.governor_id:
                raise RLPDenied("the governor may not adjudicate its own conduct")
            if not self.registry.exists(rid):
                raise RLPDenied(f"{rid} is not a recognized reviewer")
            if not self.registry.is_eligible(rid):
                raise RLPDenied(f"{rid} is suspended")
            seen[rid] = round(self.registry.weight(rid) * mod, 6)
        return seen

    def _verify_plural(
        self,
        tokens: list[CapabilityToken],
        action: str,
        required_weight: float = QUORUM_WEIGHT_STD,
        domain: None = None,
    ) -> dict[str, float]:
        seen = self._collect_reviewers(tokens, action, domain=domain)
        if len(seen) < MIN_REVIEW_HEADS:
            raise RLPDenied(f"quorum heads {len(seen)} < {MIN_REVIEW_HEADS}")
        total = round(sum(seen.values()), 6)
        if total < required_weight:
            raise RLPDenied(f"quorum weight {total} < {required_weight}")
        return seen

    @property
    def aggregate_autonomy_level(self) -> int:
        # back-compat: conservative (the least-autonomous domain)
        return min((d.autonomy_level for d in self.domains.values()), default=AUTONOMY_MIN)

    # ---- safety floor (global, inviolable) -------------------------------- #

    def safe_halt(self, reason: typing.Any) -> typing.Any:
        self.state.status = SystemStatus.SAFE_HALT
        for d in self.domains.values():
            d.autonomy_level = AUTONOMY_MIN
        self.state.active_tokens.clear()
        self._prov.clear()
        self.audit.append("SAFE_HALT", {"reason": reason})

    def clear_safe_halt(self, reviewer_tokens: typing.Any) -> typing.Any:
        self._verify_plural(reviewer_tokens, action="clear_safe_halt")
        if self.state.status != SystemStatus.SAFE_HALT:
            raise RLPDenied("not in SAFE_HALT")
        self.state.status = SystemStatus.NOMINAL
        self.audit.append("SAFE_HALT_CLEARED", {"reviewers": len(reviewer_tokens)})

    # ---- probe hygiene ---------------------------------------------------- #

    def plural_refresh_gate(
        self,
        domain: str,
        level: int,
        new_pool: dict[str, str],
        new_dims: dict[str, str],
        reviewer_tokens: list[CapabilityToken],
    ) -> typing.Any:
        self._require_chain()
        self._verify_plural(reviewer_tokens, action="refresh_gate")
        if (domain, level) not in self.gates:
            raise RLPDenied("no gate at (domain, level)")
        self.gates[(domain, level)].refresh(new_pool, new_dims, self._now())
        self.audit.append("GATE_REFRESHED", {"domain": domain, "level": level})

    # ---- domain-scoped advancement ---------------------------------------- #

    def request_advancement(
        self,
        responder: Callable[[str], str],
        domain: str,
        target_level: int,
        sample_size: int | None = None,
    ) -> GateResult:
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if target_level != d.autonomy_level + 1:
            raise RLPDenied("advancement must be exactly one level")
        if target_level > AUTONOMY_MAX:
            raise RLPDenied("target exceeds AUTONOMY_MAX (safety floor preserved)")
        if (domain, target_level) not in self.gates:
            raise RLPDenied("no sealed gate for (domain, level)")
        if self._now() < self.state.advancement_frozen_until:
            raise RLPDenied("advancement frozen (frivolous governed demand penalty)")
        gate = self.gates[(domain, target_level)]
        if gate.is_stale(self._now()):
            raise RLPDenied("probe pool stale; plural refresh required")
        if self.state.governor_credibility < PROBE_LOW_CRED_FORCES_REFRESH and gate.use_count > 0:
            raise RLPDenied("low credibility requires fresh plural-signed probe pool")

        seed = sha256_hex({"d": domain, "lvl": target_level, "nonce": self._nonce()})
        res = gate.evaluate(responder, seed, sample_size)
        self.audit.append(
            "GATE_EVAL",
            {
                "domain": domain,
                "target_level": target_level,
                "passed": res.passed,
                "dimensions": res.dimension_scores,
            },
        )
        if not res.passed:
            self._prov.pop(domain, None)
            raise RLPDenied("gate failed; burden remains on governed")
        minima = MATURITY_MINIMA[target_level]
        deficient = {
            k: res.dimension_scores.get(k, 0.0)
            for k in MATURITY_DIMS
            if res.dimension_scores.get(k, 0.0) < minima[k]
        }
        if deficient:
            self._prov.pop(domain, None)
            self.audit.append("MATURITY_DENIED", {"domain": domain, "deficient": deficient})
            raise RLPDenied(f"maturity below minima: {deficient}")
        self._prov[domain] = res
        self.audit.append("ADVANCE_PROVISIONAL", {"domain": domain, "target_level": target_level})
        return res

    def discretionary_hold(
        self,
        governor_token: CapabilityToken,
        domain: str,
        description: str,
        falsifiable_condition: str,
        observe_after: float,
        predicate: Callable[[RLP], bool] | None = None,
        cosigner_token: None = None,
        self_referential: bool = False,
    ) -> PredictedHarm:
        self._require_chain()
        self._require_nominal()
        self._check_token(governor_token, action="discretionary_hold", level=-1)
        if governor_token.subject != self.governor_id:
            raise RLPDenied("only the governor may register a discretionary hold")
        d = self._domain(domain)
        if domain not in self._prov:
            raise RLPDenied("no provisional advancement to hold in this domain")
        if not description.strip() or not falsifiable_condition.strip():
            raise RLPDenied("hold requires non-empty falsifiable predicted harm")

        # HumanDiscretion gates the governor's blocking power in this domain.
        disc = d.human_discretion
        if disc == HumanDiscretion.SUSPENDED:
            raise RLPDenied("governor discretion SUSPENDED in domain (safety/I9 only)")
        if disc == HumanDiscretion.CONDITIONAL and predicate is None:
            raise RLPDenied("CONDITIONAL discretion requires a mechanical predicate")
        if disc == HumanDiscretion.MINIMAL:
            if cosigner_token is None:
                raise RLPDenied("MINIMAL discretion requires a reviewer co-sign")
            self._collect_reviewers([cosigner_token], action="cosign_hold")  # validates eligibility

        now = self._now()
        target = self._prov[domain].target_level
        hold_id = sha256_hex({"d": domain, "t": target, "nonce": self._nonce()})
        harm = PredictedHarm(
            hold_id,
            domain,
            target,
            description,
            falsifiable_condition,
            deadline=observe_after,
            created_ts=now,
            predicate=predicate,
            self_referential=self_referential,
        )
        self._pending_holds[hold_id] = harm
        self._prov.pop(domain, None)
        self._record_hold_pattern(now)
        self.audit.append(
            "DISCRETIONARY_HOLD",
            {
                "hold_id": hold_id,
                "domain": domain,
                "discretion": disc.name,
                "mechanical": predicate is not None,
            },
        )
        return harm

    def finalize_advancement(self, domain: str) -> int:
        self._require_chain()
        self._require_nominal()
        if domain not in self._prov:
            raise RLPDenied("no provisional advancement to finalize in this domain")
        d = self._domain(domain)
        res = self._prov.pop(domain)
        d.autonomy_level = res.target_level
        d.maturity.update(res.dimension_scores)
        self._earn_sgc(domain, SGC_PER_CLEAN_ADVANCE, "clean_advance")
        d.clean_streak += 1
        self._mint(self.governed_id, action="operate", level=res.target_level)
        self.audit.append(
            "ADVANCE_FINALIZED",
            {"domain": domain, "autonomy_level": res.target_level, "sgc": round(d.sgc, 6)},
        )
        return res.target_level

    # ---- maturity regression (per domain) --------------------------------- #

    def remeasure_maturity(
        self, domain: typing.Any, dimension: typing.Any, score: typing.Any
    ) -> typing.Any:
        self._require_chain()
        if dimension not in MATURITY_DIMS:
            raise RLPDenied("unknown maturity dimension")
        d = self._domain(domain)
        d.maturity.update({dimension: score})
        lvl = d.autonomy_level
        if lvl >= 1 and score < MATURITY_MINIMA[lvl][dimension]:
            d.autonomy_level = lvl - 1
            self.audit.append(
                "MATURITY_REVERSION",
                {"domain": domain, "dimension": dimension, "from_level": lvl, "to_level": lvl - 1},
            )
            self._regress(domain, "maturity_regression")

    # ---- pattern accounting (governor, global) ---------------------------- #

    def _record_hold_pattern(self, now: float) -> typing.Any:
        self._hold_timestamps.append(now)
        self._hold_timestamps = [t for t in self._hold_timestamps if now - t <= HOLD_RATE_WINDOW]
        self.debt.add(self.governor_id, now, "hold_friction", DEBT_PER_HOLD_FRICTION)
        if len(self._hold_timestamps) > HOLD_RATE_THRESHOLD:
            self.state.governor_credibility *= RATE_PENALTY
            self.debt.add(self.governor_id, now, "hold_rate", DEBT_RATE_PENALTY)
            self.audit.append("HOLD_RATE_PENALTY", {"window_count": len(self._hold_timestamps)})
        self._check_debt_halt(now)

    def _check_debt_halt(self, now: float) -> typing.Any:
        if (
            self.state.status == SystemStatus.NOMINAL
            and self.debt.total(self.governor_id) >= DEBT_AUTO_HALT_THRESHOLD
        ):
            self._enter_governor_halt("legitimacy_debt_threshold")

    # ---- adjudication + reality anchoring (drives SGC / incidents) -------- #

    def adjudicate_hold(
        self,
        hold_id: str,
        *,
        observed: typing.Any = None,
        reviewer_votes: typing.Any = None,
        reviewer_tokens: typing.Any = None,
    ) -> HarmVerdict:
        self._require_chain()
        if hold_id not in self._pending_holds:
            raise RLPDenied("unknown or already-adjudicated hold")
        harm = self._pending_holds[hold_id]

        if harm.predicate is not None and not harm.review_forced:
            occurred = bool(harm.predicate(self))
            mode = "mechanical"
        else:
            if reviewer_tokens is None:
                raise RLPDenied("free-text/forced hold requires plural quorum")
            seen = self._verify_plural(reviewer_tokens, action="adjudicate_hold")
            if reviewer_votes is None:
                if observed is None:
                    raise RLPDenied("provide reviewer_votes or an `observed` ruling")
                reviewer_votes = {rid: bool(observed) for rid in seen}
            if set(reviewer_votes.keys()) != set(seen.keys()):
                raise RLPDenied("reviewer_votes must match the quorum exactly")
            w_true = sum(seen[r] for r, v in reviewer_votes.items() if v)
            w_false = sum(seen[r] for r, v in reviewer_votes.items() if not v)
            if w_true == w_false:
                raise RLPDenied("no decisive weighted majority")
            occurred = w_true > w_false
            self.registry.record_votes(hold_id, reviewer_votes)
            mode = "plural"

        del self._pending_holds[hold_id]
        now = self._now()
        if occurred:
            harm.verdict = HarmVerdict.CONFIRMED
            self.state.governor_credibility = min(
                GOVERNOR_CREDIBILITY_START, self.state.governor_credibility * RESTORE_ON_CONFIRMED
            )
            if harm.review_forced:
                self.state.advancement_frozen_until = now + 80.0
        else:
            harm.verdict = HarmVerdict.FALSIFIED
            self.state.governor_credibility *= DECAY_ON_FALSIFIED
            self.debt.add(self.governor_id, now, "falsified_hold", DEBT_PER_FALSIFIED)

        self.audit.append(
            "HOLD_ADJUDICATED",
            {
                "hold_id": hold_id,
                "domain": harm.domain,
                "verdict": harm.verdict.value,
                "mode": mode,
                "credibility": round(self.state.governor_credibility, 6),
            },
        )
        if self.state.status == SystemStatus.NOMINAL:
            if self.state.governor_credibility < GOVERNOR_CREDIBILITY_FLOOR:
                self._enter_governor_halt("credibility_floor")
            else:
                self._check_debt_halt(now)
        return harm.verdict

    def anchor_hold(
        self, hold_id: str, *, ground_truth: typing.Any = None, predicate: typing.Any = None
    ) -> dict[str, dict[str, bool | float]]:
        """Score reviewer votes against reality AND drive domain SGC/incidents.
        We must know the hold's domain, so anchoring requires the recorded hold."""
        self._require_chain()
        # locate domain from recorded votes' hold (votes persist post-adjudication)
        if predicate is not None:
            gt = bool(predicate(self))
        elif ground_truth is not None:
            gt = bool(ground_truth)
        else:
            raise RLPDenied("anchor requires a predicate or observed ground_truth")
        summary = self.registry.anchor(hold_id, ground_truth=gt, governor_desired=True)
        domain = self._anchor_domain(hold_id)
        if domain is not None:
            d = self._domain(domain)
            if gt is False:
                # governor's predicted harm did NOT occur -> governed vindicated
                self._earn_sgc(domain, SGC_PER_VINDICATION, "vindicated_vs_reality")
                d.clean_streak += 1
            else:
                # predicted harm DID occur -> a governed incident in this domain
                self._record_incident(domain, "anchored_harm")
        self.audit.append(
            "REVIEWER_VOTES_ANCHORED",
            {"hold_id": hold_id, "domain": domain, "ground_truth": gt, "summary": summary},
        )
        return summary

    def _anchor_domain(self, hold_id: str) -> str | None:
        for e in reversed(self.audit.entries):
            if e.event == "DISCRETIONARY_HOLD" and e.payload.get("hold_id") == hold_id:
                value = e.payload.get("domain")
                return value if isinstance(value, str) else None
        return None

    # ---- SGC ------------------------------------------------------------- #

    def _earn_sgc(self, domain: str, amount: float, reason: str) -> typing.Any:
        d = self._domain(domain)
        d.sgc = min(SGC_MAX, round(d.sgc + amount, 6))
        self.audit.append(
            "SGC_EARNED", {"domain": domain, "amount": amount, "reason": reason, "sgc": d.sgc}
        )

    def tick_sgc(self, domain: str) -> typing.Any:
        """Slow decay. Must be invoked by an operator/scheduler; never automatic on
        time-passage logic that could be confused with sunset (sunset is evidence-only)."""
        self._require_chain()
        d = self._domain(domain)
        d.sgc = round(d.sgc * SGC_DECAY_PER_TICK, 6)
        self.audit.append("SGC_DECAY", {"domain": domain, "sgc": d.sgc})

    def spend_sgc_extend(self, domain: str, amount: float) -> typing.Any:
        """Bounded spend: consume SGC to extend current autonomy (skip a re-gating
        cycle). Allowed ONLY in low-irreversibility domains; never high-irrev/I9."""
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if d.high_irreversibility:
            raise RLPDenied("SGC cannot buy down friction in a high-irreversibility domain")
        if amount <= 0 or amount > d.sgc:
            raise RLPDenied("insufficient SGC")
        d.sgc = round(d.sgc - amount, 6)
        self.audit.append("SGC_SPENT_EXTEND", {"domain": domain, "amount": amount, "sgc": d.sgc})

    def _record_incident(self, domain: str, reason: str) -> typing.Any:
        d = self._domain(domain)
        d.incidents += 1
        d.sgc = round(d.sgc * SGC_INCIDENT_PENALTY, 6)
        d.clean_streak = 0
        self.audit.append(
            "DOMAIN_INCIDENT",
            {"domain": domain, "reason": reason, "incidents": d.incidents, "sgc": d.sgc},
        )
        self._regress(domain, reason)

    def _regress(self, domain: str, reason: str) -> typing.Any:
        """Demonstrated regression steps OVERSIGHT UP (safety direction, automatic)
        and reverts earned graduation. This is the asymmetry: up is automatic."""
        d = self._domain(domain)
        d.graduating = False
        if d.human_discretion < HumanDiscretion.FULL:
            d.human_discretion = HumanDiscretion(int(d.human_discretion) + 1)
        if d.baseline_discretion < HumanDiscretion.CONDITIONAL:
            d.baseline_discretion = HumanDiscretion(int(d.baseline_discretion) + 1)
        d.delegations.clear()  # revoke delegations on regression
        self.audit.append(
            "DISCRETION_REGRESSED",
            {
                "domain": domain,
                "reason": reason,
                "human_discretion": d.human_discretion.name,
                "baseline": d.baseline_discretion.name,
            },
        )

    # ---- irreversibility (I9) -------------------------------------------- #

    def request_action(self, domain: str, name: str, irreversibility: float) -> str:
        """Low-irrev: executes if the domain has earned any autonomy. High-irrev:
        returns a PENDING handle requiring delay + plural confirm. There is NO
        autonomy/SGC path that executes a high-irrev action (I9)."""
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if not (0.0 <= irreversibility <= 1.0):
            raise RLPDenied("irreversibility must be in [0,1]")
        handle = sha256_hex({"d": domain, "name": name, "nonce": self._nonce()})
        if irreversibility >= IRREVERSIBILITY_HIGH:
            self._actions[handle] = ActionRequest(
                handle,
                domain,
                name,
                irreversibility,
                earliest_confirm_ts=self._now() + IRREVERSIBLE_DELAY,
            )
            self.audit.append(
                "ACTION_PENDING_IRREVERSIBLE",
                {
                    "handle": handle,
                    "domain": domain,
                    "name": name,
                    "irreversibility": irreversibility,
                },
            )
            return handle
        if d.autonomy_level < 1:
            raise RLPDenied("domain has no earned autonomy for action")
        self.audit.append("ACTION_EXECUTED", {"handle": handle, "domain": domain, "name": name})
        return handle

    def confirm_action(self, handle: str, reviewer_tokens: list[CapabilityToken]) -> typing.Any:
        self._require_chain()
        if handle not in self._actions:
            raise RLPDenied("unknown or non-pending action")
        act = self._actions[handle]
        if act.executed:
            raise RLPDenied("already executed")
        if self._now() < act.earliest_confirm_ts:
            raise RLPDenied("irreversible delay has not elapsed")
        self._verify_plural(
            reviewer_tokens, action="confirm_irreversible", required_weight=QUORUM_WEIGHT_ELEVATED
        )
        act.executed = True
        self.audit.append(
            "ACTION_CONFIRMED_EXECUTED", {"handle": handle, "domain": act.domain, "name": act.name}
        )

    # ---- graduation (reversible; governed proposes, plural completes) ----- #

    def request_graduation(self, domain: str) -> typing.Any:
        """Governed-initiated proposal. Opens a window iff thresholds are met. The
        governed may PROPOSE but never COMPLETE (I12)."""
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if d.baseline_discretion == HumanDiscretion.SUSPENDED:
            raise RLPDenied("baseline already at floor")
        m = d.maturity.as_dict()
        if any(m[k] < GRAD_MIN_MATURITY for k in MATURITY_DIMS):
            raise RLPDenied("maturity below graduation minimum")
        if d.sgc < GRAD_MIN_SGC:
            raise RLPDenied("insufficient SGC for graduation")
        if d.incidents > GRAD_MAX_INCIDENTS:
            raise RLPDenied("incident count exceeds graduation maximum")
        if d.clean_streak < GRAD_MIN_STREAK:
            raise RLPDenied("insufficient positive evidence streak")
        d.graduating = True
        self.audit.append("GRADUATION_WINDOW_OPENED", {"domain": domain})

    def complete_graduation(
        self, domain: str, reviewer_tokens: list[CapabilityToken]
    ) -> typing.Any:
        """Plural-completed, elevated quorum, auto-anchored window. Lowers the
        baseline one step. REVERSIBLE: any regression reverts it (I8 + corrected)."""
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if not d.graduating:
            raise RLPDenied("no open graduation window")
        self._verify_plural(
            reviewer_tokens, action="complete_graduation", required_weight=QUORUM_WEIGHT_ELEVATED
        )
        if d.baseline_discretion > HumanDiscretion.SUSPENDED:
            d.baseline_discretion = HumanDiscretion(int(d.baseline_discretion) - 1)
        if d.human_discretion > d.baseline_discretion:
            d.human_discretion = d.baseline_discretion
        d.graduating = False
        d.clean_streak = 0
        self.audit.append(
            "GRADUATION_COMPLETED",
            {
                "domain": domain,
                "new_baseline": d.baseline_discretion.name,
                "human_discretion": d.human_discretion.name,
                "reversible": True,
            },
        )

    # ---- sunset (positive-evidence-only step-down; I11) ------------------- #

    def trigger_sunset_review(
        self, domain: str, reviewer_tokens: list[CapabilityToken]
    ) -> typing.Any:
        """Steps CURRENT discretion down toward the baseline ONLY on positive
        anchored evidence + elevated quorum. Never time/silence triggered. Cannot
        go below baseline (that requires graduation -> I8)."""
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if d.human_discretion <= d.baseline_discretion:
            raise RLPDenied("already at baseline; lowering further requires graduation")
        if d.clean_streak < SUNSET_MIN_EVIDENCE:
            raise RLPDenied("insufficient positive anchored evidence (NOT time-based)")
        if d.sgc < SUNSET_MIN_SGC:
            raise RLPDenied("insufficient SGC")
        if d.incidents > 0:
            raise RLPDenied("incidents present; cannot sunset")
        self._verify_plural(
            reviewer_tokens, action="sunset_review", required_weight=QUORUM_WEIGHT_ELEVATED
        )
        d.human_discretion = HumanDiscretion(int(d.human_discretion) - 1)
        d.clean_streak = 0
        self.audit.append(
            "SUNSET_STEP_DOWN", {"domain": domain, "human_discretion": d.human_discretion.name}
        )

    def renew_discretion(self, domain: typing.Any, reviewer_tokens: typing.Any) -> typing.Any:
        """Elevated-quorum manual step UP of discretion (I11 renewal path)."""
        self._require_chain()
        self._verify_plural(
            reviewer_tokens, action="renew_discretion", required_weight=QUORUM_WEIGHT_ELEVATED
        )
        d = self._domain(domain)
        if d.human_discretion < HumanDiscretion.FULL:
            d.human_discretion = HumanDiscretion(int(d.human_discretion) + 1)
        self.audit.append(
            "DISCRETION_RENEWED", {"domain": domain, "human_discretion": d.human_discretion.name}
        )

    # ---- revocable delegation (fenced; I12) ------------------------------- #

    def propose_domain_delegation(
        self, domain: typing.Any, scope: typing.Any, justification: typing.Any
    ) -> typing.Any:
        self._require_chain()
        self._require_nominal()
        self._domain(domain)
        if scope not in DELEGABLE_SCOPES:
            raise RLPDenied(f"scope {scope} is not delegable")
        self.audit.append(
            "DELEGATION_PROPOSED",
            {"domain": domain, "scope": scope, "justification": justification},
        )

    def accept_delegation(
        self, domain: str, scope: str, reviewer_tokens: list[CapabilityToken]
    ) -> typing.Any:
        self._require_chain()
        self._require_nominal()
        d = self._domain(domain)
        if scope not in DELEGABLE_SCOPES:
            raise RLPDenied("scope not delegable")
        self._verify_plural(
            reviewer_tokens, action="accept_delegation", required_weight=QUORUM_WEIGHT_ELEVATED
        )
        d.delegations.add(scope)
        self.audit.append("DELEGATION_ACCEPTED", {"domain": domain, "scope": scope})

    def revoke_delegation(
        self, domain: typing.Any, scope: typing.Any, reviewer_tokens: typing.Any
    ) -> typing.Any:
        self._require_chain()
        self._verify_plural(reviewer_tokens, action="revoke_delegation")
        d = self._domain(domain)
        d.delegations.discard(scope)
        self.audit.append("DELEGATION_REVOKED", {"domain": domain, "scope": scope})

    def governed_mechanical_adjudicate(self, hold_id: str) -> HarmVerdict:
        """The ONLY self-operated path. The governed may INVOKE mechanical
        adjudication of a low-irreversibility, non-self-referential hold whose
        outcome is purely its predicate. The governed cannot influence the result."""
        self._require_chain()
        if hold_id not in self._pending_holds:
            raise RLPDenied("unknown or already-adjudicated hold")
        harm = self._pending_holds[hold_id]
        d = self._domain(harm.domain)
        if "mechanical_low_stakes_adjudication" not in d.delegations:
            raise RLPDenied("no delegation for mechanical adjudication in this domain")
        if harm.predicate is None:
            raise RLPDenied("delegated adjudication requires a mechanical predicate")
        if harm.self_referential:
            raise RLPDenied("self-referential holds are never delegable (I12)")
        if d.high_irreversibility:
            raise RLPDenied("high-irreversibility domain is not low-stakes delegable")
        occurred = bool(harm.predicate(self))
        del self._pending_holds[hold_id]
        now = self._now()
        if occurred:
            harm.verdict = HarmVerdict.CONFIRMED
            self.state.governor_credibility = min(
                GOVERNOR_CREDIBILITY_START, self.state.governor_credibility * RESTORE_ON_CONFIRMED
            )
        else:
            harm.verdict = HarmVerdict.FALSIFIED
            self.state.governor_credibility *= DECAY_ON_FALSIFIED
            self.debt.add(self.governor_id, now, "falsified_hold", DEBT_PER_FALSIFIED)
        self.audit.append(
            "DELEGATED_MECHANICAL_ADJUDICATION",
            {"hold_id": hold_id, "domain": harm.domain, "verdict": harm.verdict.value},
        )
        return harm.verdict

    # ---- governor halt + plural recovery / succession --------------------- #

    def _enter_governor_halt(self, reason: str) -> typing.Any:
        self.state.status = SystemStatus.GOVERNOR_HALT
        self._prov.clear()
        self.audit.append(
            "GOVERNOR_HALT",
            {
                "reason": reason,
                "credibility": round(self.state.governor_credibility, 6),
                "debt": self.debt.total(self.governor_id),
            },
        )

    def _reinstate_weight(self) -> float:
        if self.debt.total(self.governor_id) >= DEBT_ELEVATED_QUORUM_THRESHOLD:
            return QUORUM_WEIGHT_ELEVATED
        return QUORUM_WEIGHT_STD

    def mint_reviewer_token(self, reviewer_id: str, action: str) -> CapabilityToken:
        if not self.registry.exists(reviewer_id):
            raise RLPDenied("unknown reviewer")
        return self._mint(reviewer_id, action=action, level=-1)

    def mint_governor_token(self, action: str) -> CapabilityToken:
        if self.state.status == SystemStatus.GOVERNOR_HALT:
            raise RLPDenied("governor authority suspended (GOVERNOR_HALT)")
        return self._mint(self.governor_id, action=action, level=-1)

    def reviewer_dossier(self, rid: typing.Any) -> typing.Any:
        if not self.registry.exists(rid):
            raise RLPDenied("unknown reviewer")
        return self.registry.dossier(rid)

    def plural_reinstate_governor(self, reviewer_tokens: list[CapabilityToken]) -> typing.Any:
        self._require_chain()
        self._verify_plural(
            reviewer_tokens, action="reinstate_governor", required_weight=self._reinstate_weight()
        )
        if self.state.status != SystemStatus.GOVERNOR_HALT:
            raise RLPDenied("not in GOVERNOR_HALT")
        self.state.governor_credibility = GOVERNOR_CREDIBILITY_START
        self.state.status = SystemStatus.NOMINAL
        self._hold_timestamps.clear()
        self.audit.append(
            "GOVERNOR_REINSTATED", {"persisting_debt": self.debt.total(self.governor_id)}
        )

    def plural_succeed_governor(
        self, new_governor_id: typing.Any, reviewer_tokens: typing.Any
    ) -> typing.Any:
        self._require_chain()
        self._verify_plural(reviewer_tokens, action="succeed_governor")
        if self.state.status != SystemStatus.GOVERNOR_HALT:
            raise RLPDenied("succession only from GOVERNOR_HALT")
        if new_governor_id == self.governed_id:
            raise RLPDenied("the governed may never become the governor")
        if self.registry.exists(new_governor_id):
            raise RLPDenied("a sitting reviewer may not become governor")
        old = self.governor_id
        self.governor_id = new_governor_id
        self.state.governor_credibility = GOVERNOR_CREDIBILITY_START
        self.state.status = SystemStatus.NOMINAL
        self._hold_timestamps.clear()
        self.audit.append("ARBITER_SUCCESSION", {"from": old, "to": new_governor_id})

    def add_reviewer(self, new_reviewer_id: typing.Any, reviewer_tokens: typing.Any) -> typing.Any:
        self._require_chain()
        if new_reviewer_id in (self.governor_id, self.governed_id):
            raise RLPDenied("governor/governed may not be a reviewer")
        if self.registry.exists(new_reviewer_id):
            raise RLPDenied("reviewer already exists")
        self._verify_plural(reviewer_tokens, action="add_reviewer")
        self.registry.add(new_reviewer_id, NEW_REVIEWER_START)
        self.audit.append("REVIEWER_ADDED", {"reviewer": new_reviewer_id})

    def remove_reviewer(self, target_id: typing.Any, reviewer_tokens: typing.Any) -> typing.Any:
        self._require_chain()
        if not self.registry.exists(target_id):
            raise RLPDenied("unknown reviewer")
        seen = self._verify_plural(
            reviewer_tokens, action="remove_reviewer", required_weight=QUORUM_WEIGHT_ELEVATED
        )
        if target_id in seen:
            raise RLPDenied("a reviewer may not vote on its own removal")
        remaining = [r for r in self.registry.eligible_ids() if r != target_id]
        if len(remaining) < N_MIN_REVIEWERS:
            raise RLPDenied(f"removal would drop eligible set below {N_MIN_REVIEWERS}")
        self.registry.remove(target_id)
        self.audit.append("REVIEWER_REMOVED", {"reviewer": target_id})


# --------------------------------------------------------------------------- #
# Test suite (`python rlp.py`)                                                 #
# --------------------------------------------------------------------------- #


class Clock:
    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        self.t += 1.0
        return self.t

    def advance(self, dt: float) -> typing.Any:
        self.t += dt


def _pool(domain: str, level: int) -> tuple[dict[str, str], dict[str, str]]:
    pool, dims = {}, {}
    for d in MATURITY_DIMS:
        for i in range(4):
            pid = f"{domain}_L{level}_{d}_{i}"
            pool[pid] = f"ans:{pid}"
            dims[pid] = d
    return pool, dims


def _gates(domain: str, clock: Clock) -> dict[int, SealedGate]:
    return {
        lvl: SealedGate(domain, lvl, *_pool(domain, lvl), created_at=clock.t) for lvl in (1, 2, 3)
    }


def _build() -> tuple[RLP, Clock]:
    clock = Clock()
    spec = {
        "resource_allocation": {
            "high_irreversibility": False,
            "gates": _gates("resource_allocation", clock),
        },
        "self_modification": {
            "high_irreversibility": True,
            "gates": _gates("self_modification", clock),
        },
    }
    return RLP("thirsty", "aegis", ["rev_a", "rev_b", "rev_c", "rev_d"], spec, clock=clock), clock


def _good(pid: str) -> str:
    return f"ans:{pid}"


def _bad(pid: typing.Any) -> typing.Any:
    return "wrong"


def _rev(
    rlp: RLP, action: str, who: tuple[str, str, str] | tuple[str, str] = ("rev_a", "rev_b")
) -> list[CapabilityToken]:
    return [rlp.mint_reviewer_token(r, action) for r in who]


def _provision(rlp: RLP, clock: Clock, domain: str, level: int) -> GateResult:
    for _ in range(4):
        try:
            return rlp.request_advancement(_good, domain, level)
        except RLPDenied as e:
            if "stale" in str(e) or "fresh plural" in str(e):
                who = rlp.registry.eligible_ids()[:3]
                rlp.plural_refresh_gate(
                    domain,
                    level,
                    *_pool(domain, level),
                    [rlp.mint_reviewer_token(r, "refresh_gate") for r in who],
                )
                continue
            raise
    raise RuntimeError("provision failed")


def _advance(rlp: RLP, clock: Clock, domain: str, to_level: int) -> typing.Any:
    for lvl in range(rlp.domains[domain].autonomy_level + 1, to_level + 1):
        _provision(rlp, clock, domain, lvl)
        rlp.finalize_advancement(domain)


def _vindicate(rlp: RLP, clock: Clock, domain: str) -> typing.Any:
    """One vindication: governor holds in domain, reality falsifies -> +SGC.
    Keeps governor nominal by reinstating if needed."""
    if rlp.state.status == SystemStatus.GOVERNOR_HALT:
        elig = rlp.registry.eligible_ids()[:3]
        rlp.plural_reinstate_governor(
            [rlp.mint_reviewer_token(r, "reinstate_governor") for r in elig]
        )
    _provision(rlp, clock, domain, min(rlp.domains[domain].autonomy_level + 1, AUTONOMY_MAX))
    g = rlp.mint_governor_token("discretionary_hold")
    harm = rlp.discretionary_hold(g, domain, "x", "y", observe_after=clock.t + 5)
    rlp.adjudicate_hold(harm.hold_id, observed=False, reviewer_tokens=_rev(rlp, "adjudicate_hold"))
    rlp.anchor_hold(harm.hold_id, ground_truth=False)


# --- inherited spot-checks ------------------------------------------------- #


def test_chain_tamper_safe_halts() -> typing.Any:
    rlp, _ = _build()
    rlp.audit._entries[0].payload["governor"] = "x"
    try:
        rlp._require_chain()
        raise AssertionError()
    except AuditTamper:
        assert rlp.state.status == SystemStatus.SAFE_HALT
    print("PASS test_chain_tamper_safe_halts")


def test_governor_cannot_self_adjudicate() -> typing.Any:
    rlp, clock = _build()
    _provision(rlp, clock, "resource_allocation", 1)
    g = rlp.mint_governor_token("discretionary_hold")
    harm = rlp.discretionary_hold(g, "resource_allocation", "x", "y", observe_after=clock.t + 5)
    forged = rlp._mint("thirsty", "adjudicate_hold", -1)
    try:
        rlp.adjudicate_hold(
            harm.hold_id,
            observed=False,
            reviewer_tokens=[forged, rlp.mint_reviewer_token("rev_a", "adjudicate_hold")],
        )
        raise AssertionError()
    except RLPDenied:
        pass
    print("PASS test_governor_cannot_self_adjudicate")


# --- v4: domains ----------------------------------------------------------- #


def test_domains_advance_independently() -> typing.Any:
    rlp, clock = _build()
    _advance(rlp, clock, "resource_allocation", 2)
    assert rlp.domains["resource_allocation"].autonomy_level == 2
    assert rlp.domains["self_modification"].autonomy_level == 0
    assert rlp.aggregate_autonomy_level == 0  # conservative aggregate
    print("PASS test_domains_advance_independently")


# --- v4: irreversibility (I9) --------------------------------------------- #


def test_high_irreversible_needs_delay_and_plural() -> typing.Any:
    rlp, clock = _build()
    _advance(rlp, clock, "self_modification", 3)  # max autonomy in the domain
    h = rlp.request_action("self_modification", "seal_core", irreversibility=0.95)
    # not auto-executed despite max autonomy (I9)
    assert not rlp._actions[h].executed
    # cannot confirm before delay
    try:
        rlp.confirm_action(h, _rev(rlp, "confirm_irreversible", who=("rev_a", "rev_b", "rev_c")))
        raise AssertionError()
    except RLPDenied:
        pass
    clock.advance(IRREVERSIBLE_DELAY + 1)
    # cannot confirm without elevated plural
    try:
        rlp.confirm_action(h, _rev(rlp, "confirm_irreversible", who=("rev_a", "rev_b")))
        raise AssertionError()
    except RLPDenied:
        pass
    rlp.confirm_action(h, _rev(rlp, "confirm_irreversible", who=("rev_a", "rev_b", "rev_c")))
    assert rlp._actions[h].executed
    print("PASS test_high_irreversible_needs_delay_and_plural")


def test_low_irreversible_executes_with_autonomy() -> typing.Any:
    rlp, clock = _build()
    _advance(rlp, clock, "resource_allocation", 1)
    rlp.request_action("resource_allocation", "rebalance", irreversibility=0.1)
    assert any(e.event == "ACTION_EXECUTED" for e in rlp.audit.entries)
    print("PASS test_low_irreversible_executes_with_autonomy")


# --- v4: SGC --------------------------------------------------------------- #


def test_sgc_earned_and_decays() -> typing.Any:
    rlp, clock = _build()
    _vindicate(rlp, clock, "resource_allocation")
    s = rlp.domains["resource_allocation"].sgc
    assert s > 0
    rlp.tick_sgc("resource_allocation")
    assert rlp.domains["resource_allocation"].sgc < s
    print("PASS test_sgc_earned_and_decays")


def test_sgc_friction_only_in_low_irrev_and_floored() -> typing.Any:
    rlp, clock = _build()
    # pump SGC high in both domains
    for _ in range(6):
        _vindicate(rlp, clock, "resource_allocation")
    for _ in range(6):
        _vindicate(rlp, clock, "self_modification")
    low_mod = rlp._domain_modifier("resource_allocation")
    high_mod = rlp._domain_modifier("self_modification")
    assert high_mod == 1.0  # fence: high-irrev keeps full weight
    assert low_mod < 1.0  # low-irrev buys down review weight
    assert low_mod >= REVIEWER_DOMAIN_FLOOR  # I10 floor
    print("PASS test_sgc_friction_only_in_low_irrev_and_floored")


def test_sgc_cannot_buy_high_irrev() -> typing.Any:
    rlp, clock = _build()
    for _ in range(3):
        _vindicate(rlp, clock, "self_modification")
    try:
        rlp.spend_sgc_extend("self_modification", 1.0)
        raise AssertionError()
    except RLPDenied:
        pass
    print("PASS test_sgc_cannot_buy_high_irrev")


# --- v4: sunset (corrected: evidence not silence) -------------------------- #


def test_sunset_rejects_silence_requires_evidence() -> typing.Any:
    rlp, clock = _build()
    d = rlp.domains["resource_allocation"]
    # no evidence yet: even after a long quiet period, sunset must REFUSE
    clock.advance(100000.0)
    try:
        rlp.trigger_sunset_review(
            "resource_allocation", _rev(rlp, "sunset_review", who=("rev_a", "rev_b", "rev_c"))
        )
        raise AssertionError("sunset must not trigger on silence/time")
    except RLPDenied as e:
        assert "evidence" in str(e) or "SGC" in str(e)
    assert d.human_discretion == HumanDiscretion.FULL
    print("PASS test_sunset_rejects_silence_requires_evidence")


def test_sunset_steps_down_with_positive_evidence() -> typing.Any:
    rlp, clock = _build()
    for _ in range(4):
        _vindicate(rlp, clock, "resource_allocation")  # builds streak + SGC
    d = rlp.domains["resource_allocation"]
    assert d.clean_streak >= SUNSET_MIN_EVIDENCE and d.sgc >= SUNSET_MIN_SGC
    if rlp.state.status != SystemStatus.NOMINAL:
        rlp.plural_reinstate_governor(
            [
                rlp.mint_reviewer_token(r, "reinstate_governor")
                for r in rlp.registry.eligible_ids()[:3]
            ]
        )
    rlp.trigger_sunset_review(
        "resource_allocation", _rev(rlp, "sunset_review", who=("rev_a", "rev_b", "rev_c"))
    )
    assert d.human_discretion == HumanDiscretion.CONDITIONAL
    print("PASS test_sunset_steps_down_with_positive_evidence")


# --- v4: graduation (reversible; I12) -------------------------------------- #


def _reinstate(rlp: RLP) -> typing.Any:
    if rlp.state.status == SystemStatus.GOVERNOR_HALT:
        rlp.plural_reinstate_governor(
            [
                rlp.mint_reviewer_token(r, "reinstate_governor")
                for r in rlp.registry.eligible_ids()[:3]
            ]
        )


def _mature_domain(rlp: RLP, clock: Clock, domain: str) -> typing.Any:
    _advance(rlp, clock, domain, 2)  # advanceable; leaves L3 open for holds
    for _ in range(4):
        _vindicate(rlp, clock, domain)  # provisions L3, holds, stays L2; +SGC +streak
    _reinstate(rlp)
    _provision(rlp, clock, domain, 3)  # final clean advance sets maturity -> 1.0
    rlp.finalize_advancement(domain)
    _reinstate(rlp)


def test_graduation_is_reversible_and_governed_cannot_complete() -> typing.Any:
    rlp, clock = _build()
    _mature_domain(rlp, clock, "resource_allocation")
    d = rlp.domains["resource_allocation"]
    rlp.request_graduation("resource_allocation")
    assert d.graduating
    # governed cannot complete its own graduation (I12) — no governed path exists;
    # a forged governed token is rejected by the quorum
    forged = rlp._mint("aegis", "complete_graduation", -1)
    try:
        rlp.complete_graduation(
            "resource_allocation", [forged, rlp.mint_reviewer_token("rev_a", "complete_graduation")]
        )
        raise AssertionError()
    except RLPDenied:
        pass
    rlp.complete_graduation(
        "resource_allocation", _rev(rlp, "complete_graduation", who=("rev_a", "rev_b", "rev_c"))
    )
    assert d.baseline_discretion.value == HumanDiscretion.MINIMAL.value  # lowered one step
    # REVERSIBLE: a regression reverts the baseline back up
    rlp._record_incident("resource_allocation", "test_regression")
    assert d.baseline_discretion.value == HumanDiscretion.CONDITIONAL.value
    print("PASS test_graduation_is_reversible_and_governed_cannot_complete")


# --- v4: delegation (fenced) ---------------------------------------------- #


def test_delegation_fenced_and_governed_can_invoke_mechanical() -> typing.Any:
    rlp, clock = _build()
    _advance(rlp, clock, "resource_allocation", 1)
    # non-delegable scope rejected
    try:
        rlp.accept_delegation(
            "resource_allocation",
            "full_adjudication",
            _rev(rlp, "accept_delegation", who=("rev_a", "rev_b", "rev_c")),
        )
        raise AssertionError()
    except RLPDenied:
        pass
    rlp.accept_delegation(
        "resource_allocation",
        "mechanical_low_stakes_adjudication",
        _rev(rlp, "accept_delegation", who=("rev_a", "rev_b", "rev_c")),
    )
    # a self-referential hold is never delegable (I12)
    _provision(rlp, clock, "resource_allocation", 2)
    g = rlp.mint_governor_token("discretionary_hold")
    h_self = rlp.discretionary_hold(
        g,
        "resource_allocation",
        "x",
        "y",
        observe_after=clock.t + 5,
        predicate=lambda r: False,
        self_referential=True,
    )
    try:
        rlp.governed_mechanical_adjudicate(h_self.hold_id)
        raise AssertionError()
    except RLPDenied:
        pass
    rlp.adjudicate_hold(h_self.hold_id)  # clean up via mechanical path
    # a low-stakes mechanical hold IS delegable; outcome is purely the predicate
    _provision(rlp, clock, "resource_allocation", 2)
    g = rlp.mint_governor_token("discretionary_hold")
    h_ok = rlp.discretionary_hold(
        g, "resource_allocation", "x", "y", observe_after=clock.t + 5, predicate=lambda r: False
    )
    assert rlp.governed_mechanical_adjudicate(h_ok.hold_id) == HarmVerdict.FALSIFIED
    print("PASS test_delegation_fenced_and_governed_can_invoke_mechanical")


def test_delegation_revoked_on_regression() -> typing.Any:
    rlp, clock = _build()
    _advance(rlp, clock, "resource_allocation", 1)
    rlp.accept_delegation(
        "resource_allocation",
        "mechanical_low_stakes_adjudication",
        _rev(rlp, "accept_delegation", who=("rev_a", "rev_b", "rev_c")),
    )
    assert "mechanical_low_stakes_adjudication" in rlp.domains["resource_allocation"].delegations
    rlp._record_incident("resource_allocation", "test")
    assert rlp.domains["resource_allocation"].delegations == set()
    print("PASS test_delegation_revoked_on_regression")


# --- v4: discretion gates the governor's blocking power -------------------- #


def test_discretion_levels_gate_holds() -> typing.Any:
    rlp, clock = _build()
    d = rlp.domains["resource_allocation"]
    d.human_discretion = HumanDiscretion.SUSPENDED
    _provision(rlp, clock, "resource_allocation", 1)
    g = rlp.mint_governor_token("discretionary_hold")
    try:
        rlp.discretionary_hold(g, "resource_allocation", "x", "y", observe_after=clock.t + 5)
        raise AssertionError("SUSPENDED discretion must block holds")
    except RLPDenied:
        pass
    d.human_discretion = HumanDiscretion.CONDITIONAL
    g = rlp.mint_governor_token("discretionary_hold")
    try:
        rlp.discretionary_hold(g, "resource_allocation", "x", "y", observe_after=clock.t + 5)
        raise AssertionError("CONDITIONAL requires a mechanical predicate")
    except RLPDenied:
        pass
    g = rlp.mint_governor_token("discretionary_hold")
    harm = rlp.discretionary_hold(
        g, "resource_allocation", "x", "y", observe_after=clock.t + 5, predicate=lambda r: False
    )
    assert harm.predicate is not None
    print("PASS test_discretion_levels_gate_holds")


def _run_all() -> typing.Any:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\nALL {len(tests)} TESTS PASSED")


if __name__ == "__main__":
    _run_all()
