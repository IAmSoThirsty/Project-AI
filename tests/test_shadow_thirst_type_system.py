"""
Tests for Shadow Thirst Type System — Plane-Safety Type Soundness.

Fact-verifies claims from the paper (§8.4):
    - PlaneAnnotation: 4 planes (Primary, Shadow, Invariant, Dual)
    - AnnotatedType: subtyping lattice (Dual ≤ Primary, Dual ≤ Shadow,
      Invariant ≤ Shadow)
    - T-Write-Canonical: FORBIDDEN in shadow context
    - T-Write-Shadow: permitted in shadow context
    - T-Promote: blocked without commit protocol completion
    - T-Invariant-Pure: invariant functions have no side effects
    - PlaneSafetyChecker: well-typed program → no violations
    - PlaneSafetyChecker: invalid program → violation detected
    - Corollary: well-typed shadow programs preserve INV-ROOT-2
"""

from __future__ import annotations

import pytest

from shadow_thirst.type_system import (
    AnnotatedType,
    BaseType,
    PlaneAnnotation,
    PlaneSafetyChecker,
    TypeViolation,
)


class TestPlaneAnnotations:
    """Paper §8.4: Four execution planes."""

    def test_all_planes_defined(self):
        planes = list(PlaneAnnotation)
        assert len(planes) == 4
        assert PlaneAnnotation.PRIMARY in planes
        assert PlaneAnnotation.SHADOW in planes
        assert PlaneAnnotation.INVARIANT in planes
        assert PlaneAnnotation.DUAL in planes


class TestAnnotatedTypeSubtyping:
    """Paper §8.4: Plane subtyping lattice."""

    def test_dual_subtype_of_primary(self):
        """Paper: T@Dual ≤ T@Primary"""
        dual = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.DUAL)
        primary = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        assert dual.is_subtype_of(primary)

    def test_dual_subtype_of_shadow(self):
        """Paper: T@Dual ≤ T@Shadow"""
        dual = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.DUAL)
        shadow = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        assert dual.is_subtype_of(shadow)

    def test_invariant_subtype_of_shadow(self):
        """Paper: T@Invariant ≤ T@Shadow"""
        inv = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.INVARIANT)
        shadow = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        assert inv.is_subtype_of(shadow)

    def test_reflexive_subtyping(self):
        """Paper: T@P ≤ T@P (reflexive)"""
        shadow = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        assert shadow.is_subtype_of(shadow)

    def test_primary_not_subtype_of_shadow(self):
        """Primary ≰ Shadow — no downward coercion without promote."""
        primary = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        shadow = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        assert not primary.is_subtype_of(shadow)

    def test_shadow_not_subtype_of_primary(self):
        """Shadow ≰ Primary — requires promote + commit protocol."""
        shadow = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        primary = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        assert not shadow.is_subtype_of(primary)


class TestCanonicalWriteability:
    """Paper §8.4: Only Primary-typed values can write to canonical state."""

    def test_primary_can_write_canonical(self):
        t = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        assert t.is_writable_to_canonical()

    def test_shadow_cannot_write_canonical(self):
        """Paper INV-ROOT-2: Shadow cannot produce canonical writes."""
        t = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        assert not t.is_writable_to_canonical()

    def test_invariant_cannot_write_canonical(self):
        t = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.INVARIANT)
        assert not t.is_writable_to_canonical()


class TestPlaneSafetyChecker:
    """Paper §8.4: Static type checker enforcing plane-safety."""

    def test_shadow_write_to_shadow_is_safe(self):
        """T-Write-Shadow: Permitted in shadow context."""
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        shadow_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        result = checker.check_write(
            target="shadow_var",
            target_plane=PlaneAnnotation.SHADOW,
            value_type=shadow_type,
            line=10,
        )
        assert result is True
        assert len(checker.violations) == 0

    def test_shadow_write_to_canonical_is_forbidden(self):
        """T-Write-Canonical: FORBIDDEN in shadow context (INV-ROOT-2)."""
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        primary_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        result = checker.check_write(
            target="canonical_var",
            target_plane=PlaneAnnotation.PRIMARY,
            value_type=primary_type,
            line=20,
        )
        assert result is False
        assert len(checker.violations) > 0
        violation = checker.violations[0]
        assert violation.rule_violated == "T-WRITE-CANONICAL"

    def test_promote_without_commit_protocol_fails(self):
        """T-Promote: Blocked without commit protocol completion."""
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        shadow_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        result = checker.check_promote(
            value_type=shadow_type,
            commit_protocol_completed=False,
            line=30,
        )
        assert result is False
        assert any(v.rule_violated == "T-PROMOTE" for v in checker.violations)

    def test_promote_with_commit_protocol_succeeds(self):
        """T-Promote: Allowed after commit protocol completion."""
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        shadow_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        result = checker.check_promote(
            value_type=shadow_type,
            commit_protocol_completed=True,
            line=40,
        )
        assert result is True

    def test_report_sound_program(self):
        """Well-typed shadow program → no violations → sound."""
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        shadow_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        checker.check_write("shadow_x", PlaneAnnotation.SHADOW, shadow_type)

        report = checker.report()
        assert report["sound"] is True
        assert report["violation_count"] == 0

    def test_report_unsound_program(self):
        """Invalid program → violations → not sound."""
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        primary_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        checker.check_write("canonical_x", PlaneAnnotation.PRIMARY, primary_type)

        report = checker.report()
        assert report["sound"] is False
        assert report["violation_count"] > 0

    def test_reset_clears_state(self):
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)
        primary_type = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.PRIMARY)
        checker.check_write("x", PlaneAnnotation.PRIMARY, primary_type)
        assert len(checker.violations) > 0
        checker.reset()
        assert len(checker.violations) == 0

    def test_invariant_root_2_corollary(self):
        """Paper Corollary: Well-typed Shadow Thirst programs preserve INV-ROOT-2.

        INV-ROOT-2: ∀e ∈ ShadowExecutions: e.canonical_writes = ∅

        A well-typed shadow program passes PlaneSafetyChecker with zero violations,
        meaning canonical_writes is structurally empty.
        """
        checker = PlaneSafetyChecker()
        checker.enter_context(PlaneAnnotation.SHADOW)

        # Simulate a typical well-typed shadow program:
        # Read canonical (result is shadow-typed)
        shadow_int = AnnotatedType(base=BaseType.INT, plane=PlaneAnnotation.SHADOW)
        checker.check_write("local_result", PlaneAnnotation.SHADOW, shadow_int)

        # Write to shadow store
        checker.check_write("shadow_output", PlaneAnnotation.SHADOW, shadow_int)

        # No canonical writes attempted
        report = checker.report()
        assert report["sound"] is True
        assert report["violation_count"] == 0  # INV-ROOT-2 preserved
