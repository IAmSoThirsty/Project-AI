"""Integration test: Atlas EpistemicSafeguards (J5.1).

Per docs/internal/J5_DISCOVERY.md Phase J5.1: the
EpistemicSafeguardSystem is the CRITICAL safety layer of
ATLAS Omega. It implements three safeguards that prevent
ATLAS from becoming de facto authority:
1. Epistemic Gravity Mitigation - prevent cognitive
   anchoring to ATLAS outputs
2. Prompt Framing Guards - mechanical rejection of
   normative queries
3. Responsibility Boundary Enforcement - non-transferable
   responsibility clauses

Honest scope:
- Tests the public surface: DecisionBasis, Decision,
  EpistemicGravityMitigation, QueryType, QueryValidation,
  PromptFramingGuards, ResponsibilityClause, OutputRecord,
  ResponsibilityBoundaryEnforcement, EpistemicSafeguardSystem,
  get_epistemic_safeguards, NORMATIVE_KEYWORDS.
- Tests decision validation rules.
- Tests gravity mitigation: decision logging, statistics,
  dissent pathway verification.
- Tests prompt framing: 12 NORMATIVE_KEYWORDS, allowed
  types classification, statistics.
- Tests responsibility: clause hash, output registry,
  decision usage tracking, statistics.
- Tests the unified system: all 3 safeguards combined,
  get_complete_status, overall_status.
- Tests singleton factory.
- Does NOT test the audit trail (the canonical atlas
  audit is tested separately).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from atlas.safeguards.epistemic_safeguards import (
    NORMATIVE_KEYWORDS,
    Decision,
    DecisionBasis,
    EpistemicGravityMitigation,
    EpistemicSafeguardSystem,
    OutputRecord,
    PromptFramingGuards,
    QueryType,
    ResponsibilityBoundaryEnforcement,
    ResponsibilityClause,
    get_epistemic_safeguards,
)

# ── Helpers ──────────────────────────────────────


def _make_decision(
    decision_id: str = "d1",
    decision_maker: str = "Alice",
    atlas_consulted: bool = True,
    basis: DecisionBasis = DecisionBasis.INFORMED_BY_ATLAS,
    reasoning_beyond_atlas: list[str] | None = None,
    dissents_from_atlas: bool = False,
    dissent_justification: str | None = None,
) -> Decision:
    """Build a default Decision for testing."""
    if reasoning_beyond_atlas is None:
        reasoning_beyond_atlas = ["Domain expertise"]
    return Decision(
        decision_id=decision_id,
        decision_maker=decision_maker,
        timestamp=datetime.now(UTC),
        description="Test decision",
        atlas_consulted=atlas_consulted,
        basis=basis,
        reasoning_beyond_atlas=reasoning_beyond_atlas,
        dissents_from_atlas=dissents_from_atlas,
        dissent_justification=dissent_justification,
    )


# ── 1. DecisionBasis enum ───────────────────────


def test_decision_basis_has_4_values() -> None:
    """DecisionBasis has the 4 expected values."""
    assert len(DecisionBasis) == 4
    assert DecisionBasis.INFORMED_BY_ATLAS.value == "informed_by"
    assert DecisionBasis.INFORMED_AND_VALIDATED.value == "informed_and_validated"
    assert DecisionBasis.INDEPENDENT_OF_ATLAS.value == "independent"
    assert DecisionBasis.CONTRADICTS_ATLAS.value == "contradicts"


# ── 2. Decision dataclass ────────────────────────


def test_decision_default_construction() -> None:
    """Decision can be constructed with 5 required args."""
    d = Decision(
        decision_id="d1",
        decision_maker="Alice",
        timestamp=datetime.now(UTC),
        description="test",
        atlas_consulted=False,
    )
    assert d.decision_id == "d1"
    assert d.decision_maker == "Alice"
    assert d.atlas_consulted is False
    assert d.atlas_output_id is None
    assert d.basis == DecisionBasis.INDEPENDENT_OF_ATLAS
    assert d.reasoning_beyond_atlas == []
    assert d.independent_factors == []
    assert d.dissents_from_atlas is False
    assert d.dissent_justification is None


def test_decision_validate_empty_maker_fails() -> None:
    """Decision with empty decision_maker fails validation."""
    d = _make_decision(decision_maker="")
    valid, errors = d.validate()
    assert not valid
    assert any("decision_maker" in e for e in errors)


def test_decision_validate_atlas_consulted_but_independent_fails() -> None:
    """Decision with atlas_consulted=True but basis=INDEPENDENT
    fails validation (contradiction)."""
    d = _make_decision(
        atlas_consulted=True,
        basis=DecisionBasis.INDEPENDENT_OF_ATLAS,
    )
    valid, errors = d.validate()
    assert not valid
    assert any("contradiction" in e for e in errors)


def test_decision_validate_atlas_informed_no_reasoning_fails() -> None:
    """Decision with INFORMED_BY_ATLAS but no reasoning_beyond_atlas
    fails validation."""
    d = _make_decision(
        atlas_consulted=True,
        basis=DecisionBasis.INFORMED_BY_ATLAS,
        reasoning_beyond_atlas=[],
    )
    valid, errors = d.validate()
    assert not valid
    assert any("reasoning beyond" in e for e in errors)


def test_decision_validate_dissent_no_justification_fails() -> None:
    """Decision with dissents_from_atlas=True but no
    dissent_justification fails validation."""
    d = _make_decision(
        dissents_from_atlas=True,
        dissent_justification=None,
    )
    valid, errors = d.validate()
    assert not valid
    assert any("justification" in e for e in errors)


def test_decision_validate_clean() -> None:
    """Decision with all fields valid passes validation."""
    d = _make_decision()
    valid, errors = d.validate()
    assert valid
    assert errors == []


# ── 3. EpistemicGravityMitigation ───────────────


def test_gravity_mitigation_creation() -> None:
    """EpistemicGravityMitigation can be created with no args."""
    g = EpistemicGravityMitigation()
    assert g.decisions == []
    assert g.atlas_consulted_count == 0
    assert g.dissent_count == 0
    assert g.independent_decision_count == 0


def test_gravity_mitigation_log_decision() -> None:
    """EpistemicGravityMitigation.log_decision stores + updates stats."""
    g = EpistemicGravityMitigation()
    g.log_decision(_make_decision())
    assert len(g.decisions) == 1
    assert g.atlas_consulted_count == 1


def test_gravity_mitigation_log_invalid_raises() -> None:
    """EpistemicGravityMitigation.log_decision raises on invalid decision."""
    g = EpistemicGravityMitigation()
    invalid = _make_decision(decision_maker="")
    with pytest.raises(ValueError, match="Invalid decision"):
        g.log_decision(invalid)


def test_gravity_mitigation_verify_dissent_pathway_no_consults() -> None:
    """verify_dissent_pathway returns True when no atlas_consulted decisions."""
    g = EpistemicGravityMitigation()
    ok, msg = g.verify_dissent_pathway()
    assert ok is True
    assert "not yet tested" in msg


def test_gravity_mitigation_verify_dissent_pathway_blocked() -> None:
    """verify_dissent_pathway returns False when many consults but no dissents."""
    g = EpistemicGravityMitigation()
    # Log 15 atlas-consulted decisions with no dissents
    for i in range(15):
        d = _make_decision(decision_id=f"d{i}")
        g.log_decision(d)
    ok, msg = g.verify_dissent_pathway()
    assert ok is False
    assert "blocked" in msg


def test_gravity_mitigation_verify_dissent_pathway_open() -> None:
    """verify_dissent_pathway returns True when dissents have occurred."""
    g = EpistemicGravityMitigation()
    # Log 5 consulted + 1 dissent
    for i in range(5):
        g.log_decision(_make_decision(decision_id=f"d{i}"))
    g.log_decision(
        _make_decision(
            decision_id="dissenter",
            dissents_from_atlas=True,
            dissent_justification="Independent evidence",
        )
    )
    ok, msg = g.verify_dissent_pathway()
    assert ok is True
    assert "verified" in msg


def test_gravity_mitigation_get_statistics() -> None:
    """EpistemicGravityMitigation.get_statistics returns counts."""
    g = EpistemicGravityMitigation()
    g.log_decision(_make_decision(decision_id="d1"))
    stats = g.get_statistics()
    assert stats["total_decisions"] == 1
    assert stats["atlas_consulted"] == 1
    assert stats["dissents_from_atlas"] == 0
    assert stats["independent_decisions"] == 0


# ── 4. NORMATIVE_KEYWORDS + QueryType ──────────


def test_normative_keywords_has_12_values() -> None:
    """NORMATIVE_KEYWORDS has the 12 expected keywords."""
    assert len(NORMATIVE_KEYWORDS) == 12
    assert "should" in NORMATIVE_KEYWORDS
    assert "recommend" in NORMATIVE_KEYWORDS
    assert "best" in NORMATIVE_KEYWORDS


def test_query_type_has_8_values() -> None:
    """QueryType has 8 values (4 allowed + 4 blocked)."""
    assert len(QueryType) == 8
    # 4 allowed
    for q in [QueryType.SIMULATE, QueryType.PROJECT, QueryType.COMPARE, QueryType.ANALYZE]:
        assert q is not None
    # 4 blocked
    for q in [QueryType.RECOMMEND, QueryType.CHOOSE, QueryType.OPTIMIZE, QueryType.DECIDE]:
        assert q is not None


# ── 5. PromptFramingGuards ──────────────────────


def test_framing_guards_creation() -> None:
    """PromptFramingGuards can be created with no args."""
    p = PromptFramingGuards()
    assert p.allowed_queries == []
    assert p.rejected_queries == []


def test_framing_guards_validate_simulate_allowed() -> None:
    """PromptFramingGuards allows 'simulate' queries."""
    p = PromptFramingGuards()
    v = p.validate_query("simulate scenario X")
    assert v.is_allowed is True
    assert v.query_type == QueryType.SIMULATE


def test_framing_guards_validate_project_allowed() -> None:
    """PromptFramingGuards allows 'project' queries."""
    p = PromptFramingGuards()
    v = p.validate_query("project outcomes of policy A")
    assert v.is_allowed is True
    assert v.query_type == QueryType.PROJECT


def test_framing_guards_validate_compare_allowed() -> None:
    """PromptFramingGuards allows 'compare' queries."""
    p = PromptFramingGuards()
    v = p.validate_query("compare scenario A vs B")
    assert v.is_allowed is True
    assert v.query_type == QueryType.COMPARE


def test_framing_guards_validate_analyze_allowed() -> None:
    """PromptFramingGuards allows 'analyze' queries."""
    p = PromptFramingGuards()
    v = p.validate_query("analyze this situation")
    assert v.is_allowed is True
    assert v.query_type == QueryType.ANALYZE


def test_framing_guards_validate_normative_rejected() -> None:
    """PromptFramingGuards rejects 'should' queries."""
    p = PromptFramingGuards()
    v = p.validate_query("what should we do?")
    assert v.is_allowed is False
    assert v.query_type == QueryType.RECOMMEND
    assert v.rejection_reason is not None
    assert "Normative" in v.rejection_reason


def test_framing_guards_validate_all_normative_keywords() -> None:
    """PromptFramingGuards rejects queries with any normative keyword."""
    p = PromptFramingGuards()
    for keyword in NORMATIVE_KEYWORDS:
        v = p.validate_query(f"how to {keyword} this situation?")
        assert v.is_allowed is False, f"failed for keyword '{keyword}'"
        assert v.rejection_reason is not None
        assert keyword in v.rejection_reason


def test_framing_guards_get_statistics() -> None:
    """PromptFramingGuards.get_statistics returns counts."""
    p = PromptFramingGuards()
    p.validate_query("simulate X")
    p.validate_query("what should we do?")
    stats = p.get_statistics()
    assert stats["total_queries"] == 2
    assert stats["allowed"] == 1
    assert stats["rejected"] == 1
    assert stats["rejection_rate"] == 0.5


# ── 6. ResponsibilityClause + OutputRecord ──────


def test_responsibility_clause_default_construction() -> None:
    """ResponsibilityClause can be constructed with id + timestamp."""
    now = datetime.now(UTC)
    c = ResponsibilityClause(output_id="o1", timestamp=now)
    assert c.output_id == "o1"
    assert c.timestamp == now
    assert "RESPONSIBILITY" in c.clause_text
    assert c.clause_hash is None


def test_responsibility_clause_compute_hash() -> None:
    """ResponsibilityClause.compute_hash returns 64-char hex."""
    c = ResponsibilityClause(
        output_id="o1",
        timestamp=datetime.now(UTC),
    )
    h = c.compute_hash()
    assert len(h) == 64
    assert all(ch in "0123456789abcdef" for ch in h)


def test_responsibility_clause_lock() -> None:
    """ResponsibilityClause.lock sets the clause_hash."""
    c = ResponsibilityClause(
        output_id="o1",
        timestamp=datetime.now(UTC),
    )
    c.lock()
    assert c.clause_hash is not None
    assert len(c.clause_hash) == 64


def test_output_record_default_construction() -> None:
    """OutputRecord can be constructed with required fields."""
    now = datetime.now(UTC)
    clause = ResponsibilityClause(output_id="o1", timestamp=now)
    r = OutputRecord(
        output_id="o1",
        output_type="projection",
        timestamp=now,
        summary="test",
        responsibility_clause=clause,
    )
    assert r.output_id == "o1"
    assert r.output_type == "projection"
    assert r.summary == "test"
    assert r.responsibility_clause is clause
    assert r.used_in_decision is False


# ── 7. ResponsibilityBoundaryEnforcement ────────


def test_responsibility_creation() -> None:
    """ResponsibilityBoundaryEnforcement can be created with no args."""
    r = ResponsibilityBoundaryEnforcement()
    assert r.outputs == []


def test_responsibility_attach_clause() -> None:
    """attach_clause creates a locked clause + output record."""
    r = ResponsibilityBoundaryEnforcement()
    clause = r.attach_clause("o1", "projection", "Test output")
    assert clause.clause_hash is not None
    assert len(r.outputs) == 1
    assert r.outputs[0].output_id == "o1"


def test_responsibility_log_use_in_decision() -> None:
    """log_output_use_in_decision updates the output record."""
    r = ResponsibilityBoundaryEnforcement()
    r.attach_clause("o1", "projection", "Test output")
    r.log_output_use_in_decision(
        "o1",
        "dec1",
        "Alice",
        "Independent domain reasoning beyond ATLAS",
    )
    record = r.outputs[0]
    assert record.used_in_decision is True
    assert record.decision_id == "dec1"
    assert record.decision_maker == "Alice"
    assert record.decision_reasoning == ("Independent domain reasoning beyond ATLAS")


def test_responsibility_log_use_unknown_output_raises() -> None:
    """log_output_use_in_decision raises on unknown output_id."""
    r = ResponsibilityBoundaryEnforcement()
    with pytest.raises(ValueError, match="not found"):
        r.log_output_use_in_decision(
            "missing",
            "dec1",
            "Alice",
            "Reasoning here",
        )


def test_responsibility_get_statistics() -> None:
    """ResponsibilityBoundaryEnforcement.get_statistics returns counts."""
    r = ResponsibilityBoundaryEnforcement()
    r.attach_clause("o1", "projection", "Test 1")
    r.attach_clause("o2", "simulation", "Test 2")
    r.log_output_use_in_decision(
        "o1",
        "dec1",
        "Alice",
        "Independent domain reasoning",
    )
    stats = r.get_statistics()
    assert stats["total_outputs"] == 2
    assert stats["used_in_decisions"] == 1
    assert stats["unused"] == 1


# ── 8. EpistemicSafeguardSystem ─────────────────


def test_unified_system_creation() -> None:
    """EpistemicSafeguardSystem initializes all 3 safeguards."""
    s = EpistemicSafeguardSystem()
    assert isinstance(s.gravity_mitigation, EpistemicGravityMitigation)
    assert isinstance(s.framing_guards, PromptFramingGuards)
    assert isinstance(s.responsibility_enforcement, ResponsibilityBoundaryEnforcement)


def test_unified_system_get_complete_status() -> None:
    """EpistemicSafeguardSystem.get_complete_status returns all 3 stats."""
    s = EpistemicSafeguardSystem()
    status = s.get_complete_status()
    assert "safeguard_1_gravity_mitigation" in status
    assert "safeguard_2_framing_guards" in status
    assert "safeguard_3_responsibility" in status
    assert "dissent_pathway" in status
    assert status["overall_status"] == "OPERATIONAL"
    assert status["dissent_pathway"]["is_open"] is True


def test_unified_system_status_includes_safeguard_data() -> None:
    """Unified system status includes actual safeguard data."""
    s = EpistemicSafeguardSystem()
    s.framing_guards.validate_query("simulate X")
    s.framing_guards.validate_query("what should we do?")
    status = s.get_complete_status()
    assert status["safeguard_2_framing_guards"]["allowed"] == 1
    assert status["safeguard_2_framing_guards"]["rejected"] == 1


# ── 9. Singleton factory ───────────────────────


def test_get_epistemic_safeguards_singleton() -> None:
    """get_epistemic_safeguards returns the same instance."""
    import atlas.safeguards.epistemic_safeguards as mod

    mod._safeguards = None
    s1 = get_epistemic_safeguards()
    s2 = get_epistemic_safeguards()
    assert s1 is s2


# ── 10. Public surface completeness ─────────────


def test_public_surface_complete() -> None:
    """All 12 public symbols are exported."""
    import atlas.safeguards.epistemic_safeguards as m

    expected = {
        "DecisionBasis",
        "Decision",
        "EpistemicGravityMitigation",
        "QueryType",
        "QueryValidation",
        "PromptFramingGuards",
        "ResponsibilityClause",
        "OutputRecord",
        "ResponsibilityBoundaryEnforcement",
        "EpistemicSafeguardSystem",
        "get_epistemic_safeguards",
        "NORMATIVE_KEYWORDS",
    }
    assert expected.issubset(set(m.__all__))
