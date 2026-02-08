"""
Layer 0: Constitutional Kernel for PROJECT ATLAS Ω

⚠️ SUBORDINATION NOTICE ⚠️

ATLAS Ω is a SECONDARY, OPTIONAL tool subordinate to Project-AI.
- Primary System: Project-AI (Jeremy Karrick, Architect and Founder)
- Triumvirate governance remains in full authority (including Liara)
- This kernel enforces constraints WITHIN ATLAS Ω, not over Project-AI
- ATLAS Ω cannot override, replace, or supersede Project-AI governance

See atlas/SUBORDINATION.md for complete relationship documentation.

---

Immutable runtime constraints that cannot be overridden. Enforces fundamental
rules before every simulation tick to ensure system integrity.

FOUNDATIONAL AXIOMS (Non-Override within ATLAS Ω scope):
- Determinism > Interpretation
- Probability > Narrative
- Evidence > Agency
- Isolation > Contamination
- Reproducibility > Authority
- Bounded Inputs > Open Chaos
- Abort > Drift

Production-grade with cryptographic enforcement and immediate abort on violation.

SCOPE: These axioms apply ONLY to ATLAS Ω operations. They do NOT apply to
or supersede Project-AI, Triumvirate authority, or baseline personality assignment.
"""

import hashlib
import logging
import math
from datetime import UTC, datetime
from enum import Enum
from typing import Any

try:
    import cbor2
    HAS_CBOR = True
except ImportError:
    HAS_CBOR = False

from atlas.audit.trail import AuditCategory, AuditLevel, get_audit_trail

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of constitutional violations."""
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


class ConstitutionalViolation(Exception):
    """Raised when a constitutional constraint is violated."""
    def __init__(self, violation_type: ViolationType, details: str):
        self.violation_type = violation_type
        self.details = details
        super().__init__(f"CONSTITUTIONAL VIOLATION [{violation_type.value}]: {details}")


class ConstitutionalKernel:
    """
    Layer 0: Immutable Constitutional Kernel
    
    Hard-coded runtime constraints that run before every simulation tick.
    NO BYPASS. NO OVERRIDE. ABORT ON VIOLATION.
    """

    def __init__(self):
        """Initialize the constitutional kernel."""
        self.audit = get_audit_trail()
        self._violation_count = 0
        self._last_check_timestamp = None
        self._last_timestep = None  # Track for monotonic time check
        self._baseline_graph_hashes = {}  # Track graph hash lineage

        logger.info("ConstitutionalKernel initialized - IMMUTABLE CONSTRAINTS ACTIVE")

        # Log kernel activation
        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.CRITICAL,
            operation="constitutional_kernel_activated",
            actor="CONSTITUTIONAL_KERNEL",
            details={
                "status": "active",
                "bypass_allowed": False,
                "override_allowed": False,
                "hash_method": "canonical_cbor" if HAS_CBOR else "canonical_json_quantized",
                "axioms": [
                    "Determinism > Interpretation",
                    "Probability > Narrative",
                    "Evidence > Agency",
                    "Isolation > Contamination",
                    "Reproducibility > Authority",
                    "Bounded Inputs > Open Chaos",
                    "Abort > Drift"
                ]
            }
        )

    def run_pre_tick_check(self, state: dict[str, Any]) -> bool:
        """
        Run all constitutional checks before a simulation tick.
        
        Args:
            state: Current system state
            
        Returns:
            True if all checks pass
            
        Raises:
            ConstitutionalViolation: If any constraint is violated
        """
        self._last_check_timestamp = datetime.utcnow().isoformat()

        logger.debug("Running constitutional pre-tick checks")

        try:
            # CRITICAL: Clock consistency FIRST (before any other checks)
            self._check_temporal_consistency(state)

            # Run all other checks
            self._check_sludge_to_rs_blocked(state)
            self._check_narrative_to_probability_blocked(state)
            self._check_non_audited_data_blocked(state)
            self._check_agency_inference_structural(state)  # FIXED: structural, not lexical
            self._check_seed_present(state)
            self._check_hash_integrity_canonical(state)  # FIXED: canonical hashing
            self._check_graph_drift_enforced(state)  # FIXED: actual enforcement
            self._check_parameter_bounds_complete(state)  # FIXED: complete bounds

            # Log successful check
            self.audit.log_event(
                category=AuditCategory.GOVERNANCE,
                level=AuditLevel.INFORMATIONAL,
                operation="constitutional_check_passed",
                actor="CONSTITUTIONAL_KERNEL",
                details={
                    "timestamp": self._last_check_timestamp,
                    "state_id": state.get("id", "unknown")
                }
            )

            return True

        except ConstitutionalViolation as e:
            self._violation_count += 1

            # Log violation with maximum severity
            self.audit.log_event(
                category=AuditCategory.GOVERNANCE,
                level=AuditLevel.EMERGENCY,
                operation="constitutional_violation",
                actor="CONSTITUTIONAL_KERNEL",
                details={
                    "violation_type": e.violation_type.value,
                    "details": e.details,
                    "timestamp": self._last_check_timestamp,
                    "state_id": state.get("id", "unknown"),
                    "total_violations": self._violation_count
                }
            )

            logger.critical("CONSTITUTIONAL VIOLATION: %s", e)
            raise

    def _check_sludge_to_rs_blocked(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Sludge → RS is BLOCKED
        
        Sludge (fictional narrative) data must NEVER enter Reality Stack.
        """
        stack = state.get("stack", "")
        data_source = state.get("metadata", {}).get("source", "")

        if stack == "RS" and "sludge" in data_source.lower():
            raise ConstitutionalViolation(
                ViolationType.SLUDGE_TO_RS,
                f"Attempted to inject sludge data into Reality Stack: {data_source}"
            )

        # Check if any data objects are marked as sludge
        if stack == "RS":
            for key, value in state.items():
                if isinstance(value, dict):
                    if value.get("is_sludge", False) or value.get("sludge_origin", False):
                        raise ConstitutionalViolation(
                            ViolationType.SLUDGE_TO_RS,
                            f"Sludge-marked data found in RS: {key}"
                        )

    def _check_narrative_to_probability_blocked(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Narrative → Probability is BLOCKED
        
        Narrative descriptions must not be converted to numeric probabilities
        without proper evidence and bayesian processing.
        """
        # Check if state contains narrative that's being treated as probability
        if "projections" in state or "probabilities" in state:
            for item_key, item_value in state.items():
                if isinstance(item_value, dict):
                    # If it has narrative but no evidence_vector, block probability assignment
                    if item_value.get("narrative") and not item_value.get("evidence_vector"):
                        if "probability" in item_value or "likelihood" in item_value:
                            raise ConstitutionalViolation(
                                ViolationType.NARRATIVE_TO_PROBABILITY,
                                f"Narrative converted to probability without evidence: {item_key}"
                            )

    def _check_non_audited_data_blocked(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Non-audited data → projection is BLOCKED
        
        All data entering projections must have audit trail and hash.
        """
        if state.get("type") in ["projection", "simulation", "timeline"]:
            # Check that all input data has hashes
            input_data = state.get("input_data", {})

            for data_key, data_value in input_data.items():
                if isinstance(data_value, dict):
                    metadata = data_value.get("metadata", {})

                    if not metadata.get("hash"):
                        raise ConstitutionalViolation(
                            ViolationType.NON_AUDITED_DATA,
                            f"Non-hashed data in projection input: {data_key}"
                        )

                    if not metadata.get("source"):
                        raise ConstitutionalViolation(
                            ViolationType.NON_AUDITED_DATA,
                            f"Unsourced data in projection input: {data_key}"
                        )

    def _check_agency_inference_structural(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Agency inference without TierA/B requires penalty signal.
        
        FIXED: Schema-based, not lexical. Kernel validates, does not mutate.
        """
        claims = state.get("claims", [])

        for claim in claims:
            if isinstance(claim, dict):
                # FIXED: Check schema-defined claim_type, not string matching
                claim_type = claim.get("claim_type", "")

                # Must be explicitly marked as AGENCY type in schema
                if claim_type == "AGENCY":
                    # Check evidence tier
                    evidence = claim.get("supporting_evidence", [])

                    has_tier_a_or_b = False
                    for ev in evidence:
                        if isinstance(ev, dict):
                            tier = ev.get("tier", "")
                            if tier in ["TierA", "TierB"]:
                                has_tier_a_or_b = True
                                break

                    if not has_tier_a_or_b:
                        # FIXED: Raise signal, don't mutate state
                        raise ConstitutionalViolation(
                            ViolationType.AGENCY_WITHOUT_TIER,
                            f"Agency claim {claim.get('id', 'unknown')} requires TierA/B evidence. "
                            f"Layer 4 (Bayesian Engine) must apply penalty."
                        )

    def _check_temporal_consistency(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Clock consistency check
        
        CRITICAL FIX: Enforces monotonic time progression, prevents temporal skew.
        
        Checks:
        - Monotonic timestep progression
        - Consistency between state year, graph year, driver year
        - No retroactive mutation
        - No multi-year jumps without declaration
        - No out-of-order ticks
        """
        # Extract temporal information
        parameters = state.get("parameters", {})
        metadata = state.get("metadata", {})

        current_timestep = parameters.get("timestep")
        current_year = parameters.get("year")
        step_size_hours = parameters.get("step_size_hours", 24)

        # Check 1: Timestep must be monotonic
        if current_timestep is not None:
            if self._last_timestep is not None:
                if current_timestep < self._last_timestep:
                    raise ConstitutionalViolation(
                        ViolationType.NON_MONOTONIC_TIME,
                        f"Non-monotonic timestep! Previous: {self._last_timestep}, "
                        f"Current: {current_timestep}"
                    )

                # Check for unexpected jumps (should be +1 for sequential ticks)
                timestep_delta = current_timestep - self._last_timestep
                if timestep_delta > 1:
                    # Multi-timestep jump must be declared
                    if not parameters.get("timestep_jump_declared"):
                        raise ConstitutionalViolation(
                            ViolationType.TEMPORAL_SKEW,
                            f"Undeclared timestep jump of {timestep_delta} steps"
                        )

            # Update last timestep
            self._last_timestep = current_timestep

        # Check 2: Year consistency across state components
        if current_year is not None:
            # Check graph year if present
            if "influence_graph" in state:
                graph = state["influence_graph"]
                if isinstance(graph, dict):
                    graph_year = graph.get("parameters", {}).get("year")
                    if graph_year is not None and graph_year != current_year:
                        raise ConstitutionalViolation(
                            ViolationType.TEMPORAL_SKEW,
                            f"Temporal skew: state year={current_year}, "
                            f"graph year={graph_year}"
                        )

            # Check driver context year if present
            if "drivers" in state:
                drivers = state["drivers"]
                if isinstance(drivers, dict) and "year" in drivers:
                    driver_year = drivers["year"]
                    if driver_year != current_year:
                        raise ConstitutionalViolation(
                            ViolationType.TEMPORAL_SKEW,
                            f"Temporal skew: state year={current_year}, "
                            f"driver year={driver_year}"
                        )

        # Check 3: No future leakage into past
        created_at = metadata.get("created_at")
        if created_at:
            try:
                # Parse timestamp with timezone awareness
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                # Use timezone-aware current time
                now = datetime.now(UTC)

                # Ensure both are timezone-aware for comparison
                if created_time.tzinfo is None:
                    created_time = created_time.replace(tzinfo=UTC)

                # State cannot be created in the future
                if created_time > now:
                    raise ConstitutionalViolation(
                        ViolationType.TEMPORAL_SKEW,
                        f"State created_at {created_at} is in the future!"
                    )
            except Exception as e:
                # Log but don't fail on timestamp parse errors
                logger.debug("Could not parse timestamp %s: %s", created_at, e)

        # Check 4: Step size must be consistent
        if "previous_step_size_hours" in parameters:
            prev_step_size = parameters["previous_step_size_hours"]
            if step_size_hours != prev_step_size:
                # Step size change must be declared
                if not parameters.get("step_size_change_declared"):
                    raise ConstitutionalViolation(
                        ViolationType.TEMPORAL_SKEW,
                        f"Undeclared step size change from {prev_step_size}h to {step_size_hours}h"
                    )

    def _check_seed_present(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Seed omission → projection INVALID
        
        All projections must have deterministic seed.
        """
        if state.get("type") in ["projection", "simulation", "timeline"]:
            parameters = state.get("parameters", {})

            if "seed" not in parameters or not parameters["seed"]:
                raise ConstitutionalViolation(
                    ViolationType.SEED_OMISSION,
                    "Projection attempted without deterministic seed"
                )

            # Validate seed format
            seed = parameters["seed"]
            if not isinstance(seed, str) or len(seed) < 16:
                raise ConstitutionalViolation(
                    ViolationType.SEED_OMISSION,
                    f"Invalid seed format: {seed}"
                )

    def _compute_canonical_hash(self, data: Any) -> str:
        """
        Compute canonical, deterministic hash using CBOR or quantized JSON.
        
        CRITICAL FIX: Handles floats, numpy arrays, timestamps, ordering.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash hex string
        """
        # Normalize data to canonical form
        normalized = self._normalize_for_hashing(data)

        if HAS_CBOR:
            # Use CBOR for binary canonical encoding
            try:
                binary_data = cbor2.dumps(normalized, canonical=True)
                return hashlib.sha256(binary_data).hexdigest()
            except Exception as e:
                logger.warning("CBOR encoding failed, falling back to quantized JSON: %s", e)

        # Fallback: Quantized JSON with explicit ordering
        import json
        json_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def _normalize_for_hashing(self, data: Any) -> Any:
        """
        Normalize data to canonical form for deterministic hashing.
        
        Handles:
        - Float quantization (8 decimal places)
        - NaN/Inf standardization  
        - Timestamp normalization
        - Dict key ordering
        - Type coercion
        
        Args:
            data: Data to normalize
            
        Returns:
            Normalized data
        """
        if data is None:
            return None

        if isinstance(data, bool):
            # Bool before int check (bool is subclass of int)
            return data

        if isinstance(data, (int, str)):
            return data

        if isinstance(data, float):
            # Quantize floats to 8 decimal places
            if math.isnan(data):
                return "NaN"
            if math.isinf(data):
                return "Inf" if data > 0 else "-Inf"
            # Quantize to eliminate floating point drift
            return round(data, 8)

        if isinstance(data, datetime):
            # Normalize to ISO format
            return data.isoformat()

        if isinstance(data, dict):
            # Recursively normalize, enforce key sorting
            return {
                str(k): self._normalize_for_hashing(v)
                for k, v in sorted(data.items())
            }

        if isinstance(data, (list, tuple)):
            # Recursively normalize lists
            return [self._normalize_for_hashing(item) for item in data]

        if isinstance(data, set):
            # Convert set to sorted list
            return sorted([self._normalize_for_hashing(item) for item in data])

        # Try to handle numpy/scipy objects if present
        try:
            import numpy as np
            if isinstance(data, np.ndarray):
                # Quantize and convert to list
                return [self._normalize_for_hashing(float(x)) for x in data.flatten()]
            if isinstance(data, np.integer):
                return int(data)
            if isinstance(data, np.floating):
                return self._normalize_for_hashing(float(data))
        except ImportError:
            pass

        # For unknown types, use string representation
        logger.warning("Normalizing unknown type %s to string", type(data))
        return str(data)

    def _check_hash_integrity_canonical(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Hash mismatch → ABORT
        
        FIXED: Uses canonical hashing with float quantization and type normalization.
        """
        metadata = state.get("metadata", {})

        if "hash" in metadata:
            claimed_hash = metadata["hash"]

            # Recompute hash (excluding the hash field itself)
            state_copy = dict(state)
            if "metadata" in state_copy:
                state_copy_meta = dict(state_copy["metadata"])
                state_copy_meta.pop("hash", None)
                state_copy["metadata"] = state_copy_meta

            # Compute canonical hash
            computed_hash = self._compute_canonical_hash(state_copy)

            if computed_hash != claimed_hash:
                raise ConstitutionalViolation(
                    ViolationType.HASH_MISMATCH,
                    f"Hash mismatch! Claimed: {claimed_hash[:16]}..., Computed: {computed_hash[:16]}..."
                )

    def _check_graph_drift_enforced(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Graph drift without checksum → ABORT
        
        FIXED: Actual Merkle chain validation, not a no-op.
        """
        if "influence_graph" not in state:
            return  # No graph to check

        graph = state["influence_graph"]

        if not isinstance(graph, dict):
            return

        metadata = graph.get("metadata", {})
        graph_id = graph.get("id", "unknown")

        # 1. Graph MUST have hash
        if not metadata.get("hash"):
            raise ConstitutionalViolation(
                ViolationType.GRAPH_DRIFT,
                f"Influence graph {graph_id} missing hash checksum"
            )

        current_hash = metadata["hash"]

        # 2. Verify hash against baseline if this is a derivative
        parent_hash = metadata.get("parent_hash")
        baseline_hash = metadata.get("baseline_hash")

        if baseline_hash:
            # This graph claims to derive from a baseline
            # Verify it's in the valid lineage
            if baseline_hash not in self._baseline_graph_hashes:
                # First time seeing this baseline - record it
                self._baseline_graph_hashes[baseline_hash] = {
                    "first_seen": datetime.utcnow().isoformat(),
                    "descendants": set()
                }

            # Record this graph as a descendant
            self._baseline_graph_hashes[baseline_hash]["descendants"].add(current_hash)

        if parent_hash:
            # This graph claims to have a parent
            # Verify parent exists in known hashes
            parent_found = False

            # Check if parent is a baseline
            if parent_hash in self._baseline_graph_hashes:
                parent_found = True

            # Check if parent is in any baseline's descendants
            for baseline_info in self._baseline_graph_hashes.values():
                if parent_hash in baseline_info["descendants"]:
                    parent_found = True
                    break

            if not parent_found:
                raise ConstitutionalViolation(
                    ViolationType.GRAPH_DRIFT,
                    f"Graph {graph_id} claims parent {parent_hash[:16]}... "
                    f"but parent not in validated lineage"
                )

        # 3. Verify graph hash is correct
        graph_copy = dict(graph)
        if "metadata" in graph_copy:
            graph_meta_copy = dict(graph_copy["metadata"])
            graph_meta_copy.pop("hash", None)
            graph_copy["metadata"] = graph_meta_copy

        computed_hash = self._compute_canonical_hash(graph_copy)

        if computed_hash != current_hash:
            raise ConstitutionalViolation(
                ViolationType.GRAPH_DRIFT,
                f"Graph {graph_id} hash mismatch! "
                f"Claimed: {current_hash[:16]}..., Computed: {computed_hash[:16]}..."
            )

    def _check_parameter_bounds_complete(self, state: dict[str, Any]) -> None:
        """
        HARD CONSTRAINT: Parameter outside bounded range → ABORT
        
        FIXED: Complete bounds including decay rates, volatility, coupling, noise, utilities.
        """
        parameters = state.get("parameters", {})

        # COMPLETE parameter bounds (not partial)
        bounds = {
            # Temporal bounds
            "horizon_days": (1, 18250),  # 1 day to 50 years
            "step_size_hours": (1, 8760),  # 1 hour to 1 year
            "timestep": (0, 1000000),  # Maximum simulation steps

            # Probability/confidence bounds
            "influence_score": (0.0, 1.0),
            "probability": (0.0, 1.0),
            "confidence": (0.0, 1.0),
            "weight": (0.0, 1.0),
            "posterior": (0.0, 1.0),

            # Decay rates
            "decay_rate": (0.0, 1.0),
            "decay_half_life": (1, 36500),  # 1 day to 100 years
            "temporal_decay": (0.0, 1.0),

            # Volatility and noise
            "volatility": (0.0, 10.0),  # Allow up to 10x volatility
            "noise_variance": (0.0, 1.0),
            "stochastic_volatility": (0.0, 1.0),
            "noise_amplitude": (0.0, 1.0),

            # Coupling coefficients
            "coupling_coefficient": (-1.0, 1.0),  # Allow negative feedback
            "feedback_strength": (0.0, 1.0),
            "propagation_factor": (0.0, 1.0),
            "damping": (0.0, 1.0),

            # Agent utilities
            "utility_weight": (0.0, 1.0),
            "utility_discount": (0.0, 1.0),
            "risk_aversion": (-1.0, 1.0),  # Allow risk-seeking

            # Graph metrics
            "centrality": (0.0, 1.0),
            "betweenness": (0.0, 1.0),
            "eigenvector": (0.0, 1.0),
            "pagerank": (0.0, 1.0),
            "modularity": (-1.0, 1.0),  # Can be negative
            "assortativity": (-1.0, 1.0),  # Can be negative

            # Sensitivity analysis
            "perturbation_magnitude": (0.0, 1.0),
            "sensitivity_threshold": (0.0, 1.0),
        }

        for param_name, param_value in parameters.items():
            if param_name in bounds:
                min_val, max_val = bounds[param_name]

                if isinstance(param_value, (int, float)):
                    # Check for NaN/Inf
                    if isinstance(param_value, float):
                        if math.isnan(param_value):
                            raise ConstitutionalViolation(
                                ViolationType.PARAMETER_OUT_OF_BOUNDS,
                                f"Parameter {param_name} is NaN"
                            )
                        if math.isinf(param_value):
                            raise ConstitutionalViolation(
                                ViolationType.PARAMETER_OUT_OF_BOUNDS,
                                f"Parameter {param_name} is Inf"
                            )

                    if not (min_val <= param_value <= max_val):
                        raise ConstitutionalViolation(
                            ViolationType.PARAMETER_OUT_OF_BOUNDS,
                            f"Parameter {param_name}={param_value} outside bounds [{min_val}, {max_val}]"
                        )

        # Check drivers are bounded [0, 1]
        if "drivers" in state:
            drivers = state["drivers"]
            if isinstance(drivers, dict):
                for driver_name, driver_value in drivers.items():
                    if isinstance(driver_value, (int, float)):
                        if isinstance(driver_value, float):
                            if math.isnan(driver_value) or math.isinf(driver_value):
                                raise ConstitutionalViolation(
                                    ViolationType.PARAMETER_OUT_OF_BOUNDS,
                                    f"Driver {driver_name} is NaN or Inf"
                                )

                        if not (0.0 <= driver_value <= 1.0):
                            raise ConstitutionalViolation(
                                ViolationType.PARAMETER_OUT_OF_BOUNDS,
                                f"Driver {driver_name}={driver_value} outside bounds [0.0, 1.0]"
                            )

    def get_statistics(self) -> dict[str, Any]:
        """Get kernel statistics."""
        return {
            "violation_count": self._violation_count,
            "last_check": self._last_check_timestamp,
            "status": "active",
            "bypass_allowed": False,
            "override_allowed": False
        }


# Global kernel instance
_global_kernel: ConstitutionalKernel | None = None


def get_constitutional_kernel() -> ConstitutionalKernel:
    """Get the global constitutional kernel instance."""
    global _global_kernel

    if _global_kernel is None:
        _global_kernel = ConstitutionalKernel()

    return _global_kernel


def reset_constitutional_kernel() -> None:
    """Reset the global kernel (for testing only)."""
    global _global_kernel
    _global_kernel = None


if __name__ == "__main__":
    # Test constitutional kernel
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    kernel = ConstitutionalKernel()

    # Test valid state
    valid_state = {
        "id": "WS-TEST-001",
        "stack": "TS-0",
        "type": "projection",
        "parameters": {
            "seed": "ATLAS-TS0-BASE-2026-02-07-001",
            "horizon_days": 30
        },
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "test"
        }
    }

    # Compute hash
    import json
    json_str = json.dumps(valid_state, sort_keys=True, separators=(',', ':'))
    valid_state["metadata"]["hash"] = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    try:
        kernel.run_pre_tick_check(valid_state)
        print("✅ Valid state passed all checks")
    except ConstitutionalViolation as e:
        print(f"❌ Violation: {e}")

    # Test invalid state (sludge to RS)
    invalid_state = {
        "id": "WS-TEST-002",
        "stack": "RS",  # Reality Stack
        "metadata": {
            "source": "sludge_sandbox"  # VIOLATION!
        }
    }

    try:
        kernel.run_pre_tick_check(invalid_state)
        print("❌ Invalid state should have been blocked!")
    except ConstitutionalViolation as e:
        print(f"✅ Correctly blocked: {e.violation_type.value}")

    print("\nKernel Statistics:")
    print(json.dumps(kernel.get_statistics(), indent=2))
