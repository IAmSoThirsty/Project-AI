from __future__ import annotations

import pytest
from thirstys_standard_runtime.cel_runtime import CELExecutionError, CELRuntime

cel_available = True
try:
    CELRuntime()
except CELExecutionError:
    cel_available = False

pytestmark = pytest.mark.skipif(
    not cel_available, reason="cel-python not installed in this environment"
)


def test_declared_cel_conditions_execute() -> None:
    runtime = CELRuntime()
    task = {
        "task_id": "task-1",
        "mode": "governance_system",
        "risk_level": "critical",
        "requires_continuity": True,
        "response_shape": "binary",
    }
    assert runtime.evaluate("true", {"task": task, "claim": {}}).value is True
    assert (
        runtime.evaluate("task.response_shape == 'binary'", {"task": task, "claim": {}}).value
        is True
    )
    assert (
        runtime.evaluate("task.requires_continuity == true", {"task": task, "claim": {}}).value
        is True
    )
    assert (
        runtime.evaluate(
            "task.mode in ['new_app','production_deployment','governance_system']",
            {"task": task, "claim": {}},
        ).value
        is True
    )
    assert (
        runtime.evaluate(
            "task.mode in ['new_app','production_deployment']", {"task": task, "claim": {}}
        ).value
        is False
    )
    assert (
        runtime.evaluate(
            "task.risk_level in ['high','critical']", {"task": task, "claim": {}}
        ).value
        is True
    )
    assert (
        runtime.evaluate(
            "claim.category == 'production_ready'",
            {"task": task, "claim": {"category": "production_ready"}},
        ).value
        is True
    )
    assert (
        runtime.evaluate(
            "claim.category == 'governance'",
            {"task": task, "claim": {"category": "production_ready"}},
        ).value
        is False
    )
