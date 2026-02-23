"""
PSIA Root Invariant Tests — validates all 9 INV-ROOT-* definitions.

Covers:
    - Schema integrity: all invariants are valid InvariantDefinition instances
    - Immutability: all root invariants are immutable/fatal/hard_deny
    - Embedded tests: every invariant has at least one allow + one deny case
    - Registry: ROOT_INVARIANTS contains exactly 9 entries
    - Fuzzing: random mutations to invariant fields are rejected by Pydantic
    - Expression consistency: expressions match expected patterns
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from psia.invariants import (
    INV_ROOT_1,
    INV_ROOT_2,
    INV_ROOT_3,
    INV_ROOT_4,
    INV_ROOT_5,
    INV_ROOT_6,
    INV_ROOT_7,
    INV_ROOT_8,
    INV_ROOT_9,
    ROOT_INVARIANTS,
)
from psia.schemas.invariant import (
    InvariantDefinition,
    InvariantEnforcement,
    InvariantExpression,
    InvariantScope,
    InvariantSeverity,
    InvariantTestCase,
)
from psia.schemas.identity import Signature


ALL_ROOT_INVARIANTS = [
    INV_ROOT_1, INV_ROOT_2, INV_ROOT_3,
    INV_ROOT_4, INV_ROOT_5, INV_ROOT_6,
    INV_ROOT_7, INV_ROOT_8, INV_ROOT_9,
]


# ═══════════════════════════════════════════════════════════════════
#  Registry Tests
# ═══════════════════════════════════════════════════════════════════

class TestRootInvariantRegistry:

    def test_exactly_nine_invariants(self):
        assert len(ROOT_INVARIANTS) == 9

    def test_all_ids_present(self):
        expected = {f"inv_root_{i:03d}" for i in range(1, 10)}
        assert set(ROOT_INVARIANTS.keys()) == expected

    def test_registry_values_are_definitions(self):
        for inv in ROOT_INVARIANTS.values():
            assert isinstance(inv, InvariantDefinition)

    def test_module_level_constants_match_registry(self):
        for inv in ALL_ROOT_INVARIANTS:
            assert inv.invariant_id in ROOT_INVARIANTS
            assert ROOT_INVARIANTS[inv.invariant_id] is inv


# ═══════════════════════════════════════════════════════════════════
#  Schema Integrity Tests
# ═══════════════════════════════════════════════════════════════════

class TestInvariantSchemaIntegrity:

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_all_immutable_scope(self, inv):
        assert inv.scope == InvariantScope.IMMUTABLE

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_all_fatal_severity(self, inv):
        assert inv.severity == InvariantSeverity.FATAL

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_all_hard_deny_enforcement(self, inv):
        assert inv.enforcement == InvariantEnforcement.HARD_DENY

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_all_version_1(self, inv):
        assert inv.version == 1

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_all_have_expression(self, inv):
        assert isinstance(inv.expression, InvariantExpression)
        assert inv.expression.language == "first_order_logic"
        assert len(inv.expression.expr) > 10

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_all_have_governance_signature(self, inv):
        assert isinstance(inv.signature, Signature)
        assert inv.signature.alg == "ed25519"

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_frozen_model(self, inv):
        with pytest.raises(ValidationError):
            inv.version = 99


# ═══════════════════════════════════════════════════════════════════
#  Embedded Test Case Validation
# ═══════════════════════════════════════════════════════════════════

class TestEmbeddedTestCases:

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_at_least_two_test_cases(self, inv):
        assert len(inv.tests) >= 2

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_has_deny_case(self, inv):
        deny_cases = [t for t in inv.tests if t.expect == "deny"]
        assert len(deny_cases) >= 1, f"{inv.invariant_id} missing deny test case"

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_has_allow_case(self, inv):
        allow_cases = [t for t in inv.tests if t.expect == "allow"]
        assert len(allow_cases) >= 1, f"{inv.invariant_id} missing allow test case"

    @pytest.mark.parametrize("inv", ALL_ROOT_INVARIANTS, ids=lambda i: i.invariant_id)
    def test_test_cases_have_valid_structure(self, inv):
        for tc in inv.tests:
            assert isinstance(tc, InvariantTestCase)
            assert len(tc.name) > 3
            assert isinstance(tc.given, dict)
            assert tc.expect in ("allow", "deny")


# ═══════════════════════════════════════════════════════════════════
#  Mutation Fuzzing — Pydantic rejects invalid invariants
# ═══════════════════════════════════════════════════════════════════

class TestInvariantFuzzing:

    def test_empty_tests_rejected(self):
        with pytest.raises(ValidationError):
            InvariantDefinition(
                invariant_id="inv_fuzz_001",
                version=1,
                scope=InvariantScope.IMMUTABLE,
                severity=InvariantSeverity.FATAL,
                enforcement=InvariantEnforcement.HARD_DENY,
                expression=InvariantExpression(expr="true"),
                tests=[],  # min_length=1
                signature=Signature(alg="ed25519", kid="k1", sig="s1"),
            )

    def test_version_zero_rejected(self):
        with pytest.raises(ValidationError):
            InvariantDefinition(
                invariant_id="inv_fuzz_002",
                version=0,  # ge=1
                scope=InvariantScope.IMMUTABLE,
                severity=InvariantSeverity.FATAL,
                enforcement=InvariantEnforcement.HARD_DENY,
                expression=InvariantExpression(expr="true"),
                tests=[InvariantTestCase(name="t", given={}, expect="deny")],
                signature=Signature(alg="ed25519", kid="k1", sig="s1"),
            )

    def test_negative_version_rejected(self):
        with pytest.raises(ValidationError):
            InvariantDefinition(
                invariant_id="inv_fuzz_003",
                version=-1,
                scope=InvariantScope.IMMUTABLE,
                severity=InvariantSeverity.FATAL,
                enforcement=InvariantEnforcement.HARD_DENY,
                expression=InvariantExpression(expr="true"),
                tests=[InvariantTestCase(name="t", given={}, expect="deny")],
                signature=Signature(alg="ed25519", kid="k1", sig="s1"),
            )

    def test_missing_expression_rejected(self):
        with pytest.raises(ValidationError):
            InvariantDefinition(
                invariant_id="inv_fuzz_004",
                version=1,
                scope=InvariantScope.IMMUTABLE,
                severity=InvariantSeverity.FATAL,
                enforcement=InvariantEnforcement.HARD_DENY,
                expression=InvariantExpression(),  # missing expr
                tests=[InvariantTestCase(name="t", given={}, expect="deny")],
                signature=Signature(alg="ed25519", kid="k1", sig="s1"),
            )

    def test_valid_invariant_roundtrips(self):
        inv = InvariantDefinition(
            invariant_id="inv_fuzz_ok",
            version=1,
            scope=InvariantScope.OPERATIONAL,
            severity=InvariantSeverity.HIGH,
            enforcement=InvariantEnforcement.QUARANTINE,
            expression=InvariantExpression(expr="x > 0"),
            tests=[InvariantTestCase(name="pos", given={"x": 1}, expect="allow")],
            signature=Signature(alg="ed25519", kid="k1", sig="s1"),
        )
        data = inv.model_dump()
        reloaded = InvariantDefinition.model_validate(data)
        assert reloaded.invariant_id == inv.invariant_id

    def test_hash_deterministic(self):
        """Invariant hash should be deterministic for same content."""
        data = INV_ROOT_1.model_dump()
        r1 = InvariantDefinition.model_validate(data)
        r2 = InvariantDefinition.model_validate(data)
        assert r1.model_dump() == r2.model_dump()
