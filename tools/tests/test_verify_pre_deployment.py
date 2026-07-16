from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[1] / "verify_pre_deployment.py"
SPEC = importlib.util.spec_from_file_location("verify_pre_deployment", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_current_repo_pre_deployment_gate_passes() -> None:
    results = MODULE.verify_all(MODULE.ROOT)

    assert results[-1] == "pre-deployment docs: 4 check(s) passed"
    assert any(result.startswith("compose manifest: 9") for result in results)


def test_env_example_rejects_real_token(tmp_path: Path) -> None:
    env_file = tmp_path / ".env.example"
    env_file.write_text(
        "\n".join(
            (
                "PROJECT_AI_API_TOKEN=real-token",
                "PROJECT_AI_API_URL=http://127.0.0.1:8000",
                "PROJECT_AI_DESKTOP_SMOKE=1",
                "QT_QPA_PLATFORM=offscreen",
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="real API token"):
        MODULE.verify_env_example(tmp_path)


def test_ci_workflow_requires_expected_jobs(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yaml").write_text("jobs:\n  python: {}\n", encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="CI jobs mismatch"):
        MODULE.verify_ci_workflow(tmp_path)
