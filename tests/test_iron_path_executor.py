"""Tests for Iron Path deterministic mutation governance."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.governance.iron_path_executor import (
    GovernanceBindingError,
    IronPathExecutor,
)


class TestIronPathExecutor:
    def test_default_deny_for_unknown_action(self, tmp_path: Path) -> None:
        executor = IronPathExecutor(decision_log_path=str(tmp_path / "decisions.jsonl"))

        req, result = executor.evaluate_policy(
            action="unknown.action",
            resource="resource://unknown",
            principal="tester",
            context={"trace_id": "t-1", "valid_actions": []},
        )

        assert req.evaluation_id == result.evaluation_id
        assert result.decision == "deny"
        assert "default deny" in result.reason.lower()

    def test_hard_mutation_requires_quorum_and_capability(self, tmp_path: Path) -> None:
        executor = IronPathExecutor(decision_log_path=str(tmp_path / "decisions.jsonl"))

        req, result = executor.evaluate_policy(
            action="user.delete",
            resource="user://alice",
            principal="admin",
            context={"trace_id": "t-2", "valid_actions": ["user.delete"]},
        )

        with pytest.raises(GovernanceBindingError, match="missing: capability_token"):
            executor.bind_mutation(
                action="user.delete",
                resource="user://alice",
                capability_token="",
                governance_context={"source": "test"},
                resolution_policy="default-deny-precedence",
                evaluation_request=req,
                evaluation_result=result,
                quorum_proof={"votes": ["a", "b", "c"]},
            )

        with pytest.raises(GovernanceBindingError, match="Quorum proof required"):
            executor.bind_mutation(
                action="user.delete",
                resource="user://alice",
                capability_token="cap-token",
                governance_context={"source": "test"},
                resolution_policy="default-deny-precedence",
                evaluation_request=req,
                evaluation_result=result,
                quorum_proof=None,
            )

    def test_append_only_replay_and_compensation(self, tmp_path: Path) -> None:
        executor = IronPathExecutor(decision_log_path=str(tmp_path / "decisions.jsonl"))

        req, result = executor.evaluate_policy(
            action="access.grant",
            resource="role://analyst",
            principal="admin",
            context={"trace_id": "t-3", "valid_actions": ["access.grant"]},
        )

        binding = executor.bind_mutation(
            action="access.grant",
            resource="role://analyst",
            capability_token="cap-token",
            governance_context={"source": "test"},
            resolution_policy="default-deny-precedence",
            evaluation_request=req,
            evaluation_result=result,
            quorum_proof={"votes": ["galahad", "cerberus", "codex"]},
        )

        record = executor.record_decision(
            principal="admin",
            binding=binding,
            evaluation_result=result,
            decision="allow",
            reason="Authorized",
        )

        compensation = executor.compensate(
            principal="admin",
            prior_record=record,
            capability_token="cap-token",
            reason="Compensating prior grant",
            quorum_proof={"votes": ["galahad", "cerberus", "codex"]},
        )

        records = executor.log.replay()

        assert len(records) == 2
        assert records[0].decision_record_id == record.decision_record_id
        assert records[1].decision_record_id == compensation.decision_record_id
        assert records[1].metadata["compensation_for"] == record.decision_record_id
