"""Constitutional runtime invariants for Project-AI governance.

This is a canonical, gate-integrated port of the preserved legacy Atlas
constitutional kernel checks. It does not create a second authority path.
Instead, it exposes a callable invariant that plugs into `kernel.InvariantEngine`
and is therefore evaluated by `GovernanceEngine` before governor votes and
before `ExecutionGate` can consume a capability or execute an action.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

from kernel import ActionRequest, InvariantSeverity, InvariantViolation


class ViolationType(StrEnum):
    """Canonical constitutional invariant identifiers."""

    SLUDGE_TO_RS = "sludge_to_rs_blocked"
    NARRATIVE_TO_PROBABILITY = "narrative_to_probability_blocked"
    NON_AUDITED_DATA = "non_audited_data_blocked"
    AGENCY_WITHOUT_TIER = "agency_without_tier_penalty_required"
    SEED_OMISSION = "seed_omission_invalid"
    HASH_MISMATCH = "hash_mismatch_abort"
    GRAPH_DRIFT = "graph_drift_abort"
    PARAMETER_OUT_OF_BOUNDS = "parameter_out_of_bounds_abort"
    TEMPORAL_SKEW = "temporal_skew_abort"
    NON_MONOTONIC_TIME = "non_monotonic_time_abort"


PARAMETER_BOUNDS: Final[dict[str, tuple[float, float]]] = {
    "horizon_days": (1.0, 18250.0),
    "step_size_hours": (1.0, 8760.0),
    "timestep": (0.0, 1_000_000.0),
    "influence_score": (0.0, 1.0),
    "probability": (0.0, 1.0),
    "confidence": (0.0, 1.0),
    "weight": (0.0, 1.0),
    "posterior": (0.0, 1.0),
    "decay_rate": (0.0, 1.0),
    "decay_half_life": (1.0, 36500.0),
    "temporal_decay": (0.0, 1.0),
    "volatility": (0.0, 10.0),
    "noise_variance": (0.0, 1.0),
    "stochastic_volatility": (0.0, 1.0),
    "noise_amplitude": (0.0, 1.0),
    "coupling_coefficient": (-1.0, 1.0),
    "feedback_strength": (0.0, 1.0),
    "propagation_factor": (0.0, 1.0),
    "damping": (0.0, 1.0),
    "utility_weight": (0.0, 1.0),
    "utility_discount": (0.0, 1.0),
    "risk_aversion": (-1.0, 1.0),
    "centrality": (0.0, 1.0),
    "betweenness": (0.0, 1.0),
    "eigenvector": (0.0, 1.0),
    "pagerank": (0.0, 1.0),
    "modularity": (-1.0, 1.0),
    "assortativity": (-1.0, 1.0),
    "perturbation_magnitude": (0.0, 1.0),
    "sensitivity_threshold": (0.0, 1.0),
}


@dataclass
class ConstitutionalKernel:
    """Stateful constitutional invariant callable.

    The instance tracks monotonic timestep and graph-hash lineage across calls.
    Any violation returns a CRITICAL `InvariantViolation`; no state mutation is
    performed on the supplied request or state.
    """

    _violation_count: int = 0
    _last_check_timestamp: str | None = None
    _last_timestep: int | float | None = None
    _baseline_graph_hashes: dict[str, set[str]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __call__(
        self,
        request: ActionRequest,
        state: Mapping[str, object],
    ) -> InvariantViolation | None:
        del request
        with self._lock:
            self._last_check_timestamp = datetime.now(UTC).isoformat()
            for check in (
                self._check_temporal_consistency,
                self._check_sludge_to_rs_blocked,
                self._check_narrative_to_probability_blocked,
                self._check_non_audited_data_blocked,
                self._check_agency_inference_structural,
                self._check_seed_present,
                self._check_hash_integrity,
                self._check_graph_drift,
                self._check_parameter_bounds,
            ):
                violation = check(state)
                if violation is not None:
                    self._violation_count += 1
                    return violation
        return None

    def get_statistics(self) -> dict[str, object]:
        """Return immutable status details for tests and diagnostics."""
        with self._lock:
            return {
                "bypass_allowed": False,
                "last_check": self._last_check_timestamp,
                "override_allowed": False,
                "status": "active",
                "violation_count": self._violation_count,
            }

    def _violation(self, violation_type: ViolationType, reason: str) -> InvariantViolation:
        return InvariantViolation(
            invariant=violation_type.value,
            reason=reason,
            severity=InvariantSeverity.CRITICAL,
        )

    def _check_sludge_to_rs_blocked(
        self,
        state: Mapping[str, object],
    ) -> InvariantViolation | None:
        stack = state.get("stack")
        metadata = _mapping(state.get("metadata"))
        source = metadata.get("source", "")
        if stack == "RS" and "sludge" in str(source).lower():
            return self._violation(
                ViolationType.SLUDGE_TO_RS,
                f"attempted to inject sludge data into Reality Stack: {source}",
            )
        if stack == "RS":
            for key, value in state.items():
                item = _mapping(value)
                if item.get("is_sludge") is True or item.get("sludge_origin") is True:
                    return self._violation(
                        ViolationType.SLUDGE_TO_RS,
                        f"sludge-marked data found in RS: {key}",
                    )
        return None

    def _check_narrative_to_probability_blocked(
        self,
        state: Mapping[str, object],
    ) -> InvariantViolation | None:
        if "projections" not in state and "probabilities" not in state:
            return None
        for key, value in state.items():
            item = _mapping(value)
            if not item:
                continue
            has_narrative = bool(item.get("narrative"))
            has_evidence = bool(item.get("evidence_vector"))
            has_probability = "probability" in item or "likelihood" in item
            if has_narrative and not has_evidence and has_probability:
                return self._violation(
                    ViolationType.NARRATIVE_TO_PROBABILITY,
                    f"narrative converted to probability without evidence: {key}",
                )
        return None

    def _check_non_audited_data_blocked(
        self,
        state: Mapping[str, object],
    ) -> InvariantViolation | None:
        if state.get("type") not in {"projection", "simulation", "timeline"}:
            return None
        input_data = _mapping(state.get("input_data"))
        for key, value in input_data.items():
            item = _mapping(value)
            if not item:
                continue
            metadata = _mapping(item.get("metadata"))
            if not metadata.get("hash"):
                return self._violation(
                    ViolationType.NON_AUDITED_DATA,
                    f"input data {key} missing hash",
                )
            if not metadata.get("source"):
                return self._violation(
                    ViolationType.NON_AUDITED_DATA,
                    f"input data {key} missing source",
                )
        return None

    def _check_agency_inference_structural(
        self,
        state: Mapping[str, object],
    ) -> InvariantViolation | None:
        claims = _sequence(state.get("claims"))
        for claim in claims:
            claim_map = _mapping(claim)
            if claim_map.get("claim_type") != "AGENCY":
                continue
            evidence = _sequence(claim_map.get("supporting_evidence"))
            has_tier_a_or_b = any(
                _mapping(item).get("tier") in {"TierA", "TierB"} for item in evidence
            )
            if not has_tier_a_or_b:
                claim_id = claim_map.get("id", "unknown")
                return self._violation(
                    ViolationType.AGENCY_WITHOUT_TIER,
                    f"agency claim {claim_id} requires TierA/B evidence",
                )
        return None

    def _check_seed_present(self, state: Mapping[str, object]) -> InvariantViolation | None:
        if state.get("type") not in {"projection", "simulation", "timeline"}:
            return None
        parameters = _mapping(state.get("parameters"))
        seed = parameters.get("seed")
        if not isinstance(seed, str) or len(seed) < 16:
            return self._violation(
                ViolationType.SEED_OMISSION,
                f"projection seed is missing or invalid: {seed!r}",
            )
        return None

    def _check_hash_integrity(self, state: Mapping[str, object]) -> InvariantViolation | None:
        metadata = _mapping(state.get("metadata"))
        claimed_hash = metadata.get("hash")
        if claimed_hash is None:
            return None
        if not isinstance(claimed_hash, str):
            return self._violation(ViolationType.HASH_MISMATCH, "metadata hash must be a string")
        state_without_hash = _without_metadata_hash(state)
        computed_hash = constitutional_state_hash(state_without_hash)
        if computed_hash != claimed_hash:
            return self._violation(
                ViolationType.HASH_MISMATCH,
                f"state hash mismatch: claimed={claimed_hash[:16]}, computed={computed_hash[:16]}",
            )
        return None

    def _check_graph_drift(self, state: Mapping[str, object]) -> InvariantViolation | None:
        graph = _mapping(state.get("influence_graph"))
        if not graph:
            return None
        metadata = _mapping(graph.get("metadata"))
        graph_id = graph.get("id", "unknown")
        current_hash = metadata.get("hash")
        if not isinstance(current_hash, str) or not current_hash:
            return self._violation(
                ViolationType.GRAPH_DRIFT,
                f"influence graph {graph_id} missing hash checksum",
            )

        baseline_hash = metadata.get("baseline_hash")
        parent_hash = metadata.get("parent_hash")
        if isinstance(baseline_hash, str) and baseline_hash:
            descendants = self._baseline_graph_hashes.setdefault(baseline_hash, set())
            descendants.add(current_hash)
        if isinstance(parent_hash, str) and parent_hash:
            parent_found = parent_hash in self._baseline_graph_hashes or any(
                parent_hash in descendants for descendants in self._baseline_graph_hashes.values()
            )
            if not parent_found:
                return self._violation(
                    ViolationType.GRAPH_DRIFT,
                    f"graph {graph_id} claims unknown parent {parent_hash[:16]}",
                )

        computed_hash = constitutional_state_hash(_without_metadata_hash(graph))
        if computed_hash != current_hash:
            return self._violation(
                ViolationType.GRAPH_DRIFT,
                f"graph {graph_id} hash mismatch: claimed={current_hash[:16]}, computed={computed_hash[:16]}",
            )
        return None

    def _check_parameter_bounds(self, state: Mapping[str, object]) -> InvariantViolation | None:
        parameters = _mapping(state.get("parameters"))
        for name, value in parameters.items():
            if name in PARAMETER_BOUNDS:
                violation = self._check_number_bound(
                    "parameter",
                    str(name),
                    value,
                    PARAMETER_BOUNDS[str(name)],
                )
                if violation is not None:
                    return violation
        drivers = _mapping(state.get("drivers"))
        for name, value in drivers.items():
            if name == "year":
                continue
            violation = self._check_number_bound("driver", str(name), value, (0.0, 1.0))
            if violation is not None:
                return violation
        return None

    def _check_number_bound(
        self,
        kind: str,
        name: str,
        value: object,
        bounds: tuple[float, float],
    ) -> InvariantViolation | None:
        if not isinstance(value, (int, float)):
            return None
        numeric = float(value)
        if math.isnan(numeric) or math.isinf(numeric):
            return self._violation(
                ViolationType.PARAMETER_OUT_OF_BOUNDS,
                f"{kind} {name} is NaN or Inf",
            )
        low, high = bounds
        if numeric < low or numeric > high:
            return self._violation(
                ViolationType.PARAMETER_OUT_OF_BOUNDS,
                f"{kind} {name}={numeric} outside bounds [{low}, {high}]",
            )
        return None

    def _check_temporal_consistency(
        self,
        state: Mapping[str, object],
    ) -> InvariantViolation | None:
        parameters = _mapping(state.get("parameters"))
        current_timestep = parameters.get("timestep")
        if isinstance(current_timestep, (int, float)):
            if self._last_timestep is not None:
                if current_timestep < self._last_timestep:
                    return self._violation(
                        ViolationType.NON_MONOTONIC_TIME,
                        f"non-monotonic timestep: previous={self._last_timestep}, current={current_timestep}",
                    )
                timestep_delta = current_timestep - self._last_timestep
                if timestep_delta > 1 and parameters.get("timestep_jump_declared") is not True:
                    return self._violation(
                        ViolationType.TEMPORAL_SKEW,
                        f"undeclared timestep jump of {timestep_delta}",
                    )
            self._last_timestep = current_timestep

        current_year = parameters.get("year")
        graph = _mapping(state.get("influence_graph"))
        graph_parameters = _mapping(graph.get("parameters")) if graph else {}
        graph_year = graph_parameters.get("year")
        if current_year is not None and graph_year is not None and graph_year != current_year:
            return self._violation(
                ViolationType.TEMPORAL_SKEW,
                f"temporal skew: state year={current_year}, graph year={graph_year}",
            )
        drivers = _mapping(state.get("drivers"))
        driver_year = drivers.get("year")
        if current_year is not None and driver_year is not None and driver_year != current_year:
            return self._violation(
                ViolationType.TEMPORAL_SKEW,
                f"temporal skew: state year={current_year}, driver year={driver_year}",
            )

        previous_step_size = parameters.get("previous_step_size_hours")
        step_size = parameters.get("step_size_hours", 24)
        if (
            previous_step_size is not None
            and step_size != previous_step_size
            and parameters.get("step_size_change_declared") is not True
        ):
            return self._violation(
                ViolationType.TEMPORAL_SKEW,
                f"undeclared step size change from {previous_step_size}h to {step_size}h",
            )
        return None


_CONSTITUTIONAL_KERNEL: ConstitutionalKernel | None = None
_CONSTITUTIONAL_KERNEL_LOCK = threading.Lock()


def get_constitutional_kernel() -> ConstitutionalKernel:
    """Return the process-local constitutional invariant singleton."""
    global _CONSTITUTIONAL_KERNEL
    with _CONSTITUTIONAL_KERNEL_LOCK:
        if _CONSTITUTIONAL_KERNEL is None:
            _CONSTITUTIONAL_KERNEL = ConstitutionalKernel()
        return _CONSTITUTIONAL_KERNEL


def reset_constitutional_kernel() -> None:
    """Reset the process-local constitutional invariant singleton."""
    global _CONSTITUTIONAL_KERNEL
    with _CONSTITUTIONAL_KERNEL_LOCK:
        _CONSTITUTIONAL_KERNEL = None


def constitutional_state_hash(state: Mapping[str, object]) -> str:
    """Compute a deterministic SHA-256 for JSON-like constitutional state."""
    normalized = _normalize_for_hashing(state)
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _without_metadata_hash(state: Mapping[str, object]) -> dict[str, object]:
    copy = dict(state)
    metadata = _mapping(copy.get("metadata"))
    if metadata:
        metadata_copy = dict(metadata)
        metadata_copy.pop("hash", None)
        copy["metadata"] = metadata_copy
    return copy


def _normalize_for_hashing(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Inf" if value > 0 else "-Inf"
        return round(value, 8)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _normalize_for_hashing(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_normalize_for_hashing(item) for item in value]
    if isinstance(value, set):
        return sorted((_normalize_for_hashing(item) for item in value), key=str)
    return str(value)


def _mapping(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    return {}


def _sequence(value: object) -> tuple[object, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return ()
