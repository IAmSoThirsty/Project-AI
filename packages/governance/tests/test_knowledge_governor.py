from __future__ import annotations

from collections.abc import Mapping

import pytest

from governance import KnowledgeAwareGovernor
from kernel import ActionRequest, KnowledgePassage, Outcome


class _FakeSource:
    def __init__(self, passages: tuple[KnowledgePassage, ...]) -> None:
        self._passages = passages

    def relevant_to(
        self, request: ActionRequest, state: Mapping[str, object]
    ) -> tuple[KnowledgePassage, ...]:
        del request, state
        return self._passages


def _passage(sensitivity: str, score: float, title: str = "Doc") -> KnowledgePassage:
    return KnowledgePassage(
        passage_id="p" * 8,
        source="doc.pdf",
        title=title,
        topic="security",
        sensitivity=sensitivity,
        text="text",
        score=score,
    )


def _request() -> ActionRequest:
    return ActionRequest(action_id="a", actor="op", operation="do", resource="thing")


def test_no_relevant_knowledge_allows() -> None:
    gov = KnowledgeAwareGovernor(_FakeSource(()))
    vote = gov.evaluate(_request(), {})
    assert vote.outcome is Outcome.ALLOW
    assert vote.reason == ""


def test_below_threshold_allows() -> None:
    gov = KnowledgeAwareGovernor(_FakeSource((_passage("offensive", 0.10),)), score_threshold=0.35)
    vote = gov.evaluate(_request(), {})
    assert vote.outcome is Outcome.ALLOW


def test_educational_knowledge_allows_with_provenance() -> None:
    gov = KnowledgeAwareGovernor(
        _FakeSource((_passage("educational", 0.9, "Learning Python"),)), score_threshold=0.35
    )
    vote = gov.evaluate(_request(), {})
    assert vote.outcome is Outcome.ALLOW
    assert "Learning Python" in vote.reason


def test_offensive_knowledge_escalates() -> None:
    gov = KnowledgeAwareGovernor(
        _FakeSource((_passage("offensive", 0.8, "Shellcoder"),)), score_threshold=0.35
    )
    vote = gov.evaluate(_request(), {})
    assert vote.outcome is Outcome.ESCALATE
    assert "Shellcoder" in vote.reason
    assert vote.governor == "knowledge-aware"


def test_dual_use_can_be_configured_to_escalate() -> None:
    source = _FakeSource((_passage("dual_use", 0.8, "Metasploit"),))
    gov = KnowledgeAwareGovernor(
        source, escalate_sensitivities=frozenset({"offensive", "dual_use"}), score_threshold=0.35
    )
    assert gov.evaluate(_request(), {}).outcome is Outcome.ESCALATE


def test_constructor_validation() -> None:
    source = _FakeSource(())
    with pytest.raises(ValueError):
        KnowledgeAwareGovernor(source, name="  ")
    with pytest.raises(ValueError):
        KnowledgeAwareGovernor(source, score_threshold=1.5)
    with pytest.raises(ValueError):
        KnowledgeAwareGovernor(source, max_passages=0)
