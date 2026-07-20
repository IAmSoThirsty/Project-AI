from __future__ import annotations

import importlib.util
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

import pytest

MODULE_PATH = Path(__file__).parents[1] / "run_ci_coverage.py"
SPEC = importlib.util.spec_from_file_location("run_ci_coverage", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_test_file_filter_matches_pytest_convention() -> None:
    assert MODULE._is_test_file(PurePosixPath("tests/test_api.py"))
    assert MODULE._is_test_file(PurePosixPath("tests/api_test.py"))
    assert not MODULE._is_test_file(PurePosixPath("tests/helper.py"))
    assert not MODULE._is_test_file(PurePosixPath("tests/test_data.json"))


def test_collection_filter_honors_testpaths_and_norecursedirs() -> None:
    test_paths = (PurePosixPath("packages"), PurePosixPath("tests"))
    ignored = frozenset({"_staging", "reference"})

    assert MODULE._is_collectable_test_file(
        PurePosixPath("packages/api/tests/test_api.py"), test_paths, ignored
    )
    assert not MODULE._is_collectable_test_file(
        PurePosixPath("packages/_staging/api/tests/test_api.py"), test_paths, ignored
    )
    assert not MODULE._is_collectable_test_file(
        PurePosixPath("scripts/test_release.py"), test_paths, ignored
    )


def test_candidate_test_files_include_untracked_nonignored_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\ntestpaths = ["tests"]\nnorecursedirs = ["reference"]\n',
        encoding="utf-8",
    )
    observed: dict[str, tuple[str, ...]] = {}

    def fake_run(arguments: tuple[str, ...], **_kwargs: object) -> SimpleNamespace:
        observed["arguments"] = arguments
        return SimpleNamespace(
            stdout=b"tests/test_tracked.py\0tests/test_untracked.py\0tests/reference/test_old.py\0"
        )

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert MODULE.candidate_test_files(tmp_path) == (
        PurePosixPath("tests/test_tracked.py"),
        PurePosixPath("tests/test_untracked.py"),
    )
    assert observed["arguments"][3:] == (
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "-z",
    )


def test_balanced_batches_preserve_every_file_and_subsystem() -> None:
    paths = tuple(
        PurePosixPath(path)
        for path in (
            "packages/api/tests/test_api.py",
            "packages/api/tests/test_auth.py",
            "packages/kernel/tests/test_kernel.py",
            "apps/desktop/tests/test_desktop.py",
            "tests/test_integration.py",
            "tools/tests/test_verifier.py",
        )
    )

    batches = MODULE.balanced_batches(paths, 3)

    assert sorted(path for batch in batches for path in batch) == sorted(paths)
    assert any(
        {
            PurePosixPath("packages/api/tests/test_api.py"),
            PurePosixPath("packages/api/tests/test_auth.py"),
        }.issubset(batch)
        for batch in map(set, batches)
    )
    assert max(map(len, batches)) - min(map(len, batches)) <= 1


def test_balanced_batches_reject_zero_batches() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        MODULE.balanced_batches((), 0)


def test_resource_intensive_waterfall_batch_runs_last() -> None:
    paths = (
        PurePosixPath("packages/thirstys-waterfall/tests/test_basic.py"),
        PurePosixPath("packages/cerberus/tests/test_cerberus_sandbox.py"),
        PurePosixPath("packages/workflows/tests/test_workflows.py"),
    )

    batches = MODULE.balanced_batches(paths, 2)

    assert batches[-1] == (PurePosixPath("packages/thirstys-waterfall/tests/test_basic.py"),)


def test_batch_disables_partial_threshold_but_preserves_coverage_collection() -> None:
    arguments = MODULE._pytest_arguments((PurePosixPath("tests/test_example.py"),))

    assert "--cov-fail-under=0" in arguments
    assert "--cov-append" in arguments
    assert "--cov-branch" in arguments
    assert "--cov=kernel" in arguments
    assert arguments[-1] == "tests/test_example.py"
