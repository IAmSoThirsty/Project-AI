"""Tests for the deterministic SHA256SUMS generator/verifier.

Fixture-based unit tests exercise every failure mode on a synthetic package tree,
and one integration test asserts the real package's SHA256SUMS is a fixed point of
the generator (regenerated, drift-free) so this file also guards the checked-in
record going stale again.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Load tools/checksums.py directly; it is a standalone script, not an installed module.
_spec = importlib.util.spec_from_file_location(
    "v3q_checksums", PACKAGE_ROOT / "tools" / "checksums.py"
)
assert _spec is not None and _spec.loader is not None
checksums = importlib.util.module_from_spec(_spec)
sys.modules["v3q_checksums"] = checksums
_spec.loader.exec_module(checksums)


def _make_package(tmp_path: Path, files: dict[str, bytes]) -> Path:
    root = tmp_path / "pkg"
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return root


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_generate_is_sorted_lf_and_self_excluding(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"b.py": b"b\n", "a.py": b"a\n", "sub/c.txt": b"c\n"})
    text = checksums.generate(root)
    assert "\r\n" not in text
    assert text.endswith("\n")
    paths = [line.split("  ./", 1)[1] for line in text.splitlines()]
    assert paths == sorted(paths) == ["a.py", "b.py", "sub/c.txt"]
    assert checksums.CHECKSUM_FILENAME not in text  # never records itself
    # Deterministic across repeated calls.
    assert checksums.generate(root) == text


def test_written_record_verifies_clean_and_is_idempotent(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n", "sub/c.txt": b"c\n"})
    checksums.write(root)
    assert checksums.verify(root) == []
    first = (root / checksums.CHECKSUM_FILENAME).read_bytes()
    checksums.write(root)
    assert (root / checksums.CHECKSUM_FILENAME).read_bytes() == first


def test_stale_hash_is_detected(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    checksums.write(root)
    (root / "a.py").write_bytes(b"changed\n")
    problems = checksums.verify(root)
    assert any("stale hash for a.py" in p for p in problems)


def test_missing_recorded_file_is_detected(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n", "gone.py": b"g\n"})
    checksums.write(root)
    (root / "gone.py").unlink()
    problems = checksums.verify(root)
    assert any("missing on disk: gone.py" in p for p in problems)


def test_unrecorded_distributed_file_is_detected(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    checksums.write(root)
    (root / "surprise.py").write_bytes(b"s\n")
    problems = checksums.verify(root)
    assert any("not recorded" in p and "surprise.py" in p for p in problems)


def test_duplicate_path_is_detected(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    digest = _sha(b"a\n")
    (root / checksums.CHECKSUM_FILENAME).write_bytes(
        f"{digest}  ./a.py\n{digest}  ./a.py\n".encode()
    )
    problems = checksums.verify(root)
    assert any("duplicate path recorded: a.py" in p for p in problems)


def test_path_traversal_is_detected(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    digest = _sha(b"a\n")
    (root / checksums.CHECKSUM_FILENAME).write_bytes(
        f"{digest}  ./a.py\n{'0' * 64}  ./../escape.txt\n".encode()
    )
    problems = checksums.verify(root)
    assert any("escapes the package" in p for p in problems)


def test_private_key_material_is_excluded_and_rejected(tmp_path: Path) -> None:
    # A private key on disk is never enumerated into the record...
    root = _make_package(
        tmp_path, {"a.py": b"a\n", "owner-private.json": b"{}\n", "keys-private.json": b"{}\n"}
    )
    listed = checksums.iter_distributed_files(root)
    assert "owner-private.json" not in listed
    assert "keys-private.json" not in listed
    assert "a.py" in listed
    # ...and if one is smuggled into the record, verification rejects it.
    a_digest = _sha(b"a\n")
    key_digest = _sha(b"{}\n")
    (root / checksums.CHECKSUM_FILENAME).write_bytes(
        f"{a_digest}  ./a.py\n{key_digest}  ./owner-private.json\n".encode()
    )
    problems = checksums.verify(root)
    assert any("private-key material must never be recorded" in p for p in problems)


def test_crlf_record_is_flagged(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    digest = _sha(b"a\n")
    (root / checksums.CHECKSUM_FILENAME).write_bytes(f"{digest}  ./a.py\r\n".encode())
    problems = checksums.verify(root)
    assert any("CRLF" in p for p in problems)


def test_self_reference_is_rejected(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    digest = _sha(b"a\n")
    (root / checksums.CHECKSUM_FILENAME).write_bytes(
        f"{digest}  ./a.py\n{'0' * 64}  ./SHA256SUMS\n".encode()
    )
    problems = checksums.verify(root)
    assert any("must not record itself" in p for p in problems)


def test_excluded_dirs_are_not_enumerated(tmp_path: Path) -> None:
    root = _make_package(
        tmp_path,
        {
            "a.py": b"a\n",
            "__pycache__/a.pyc": b"x",
            ".venv/lib/mod.py": b"y",
            "pkg.egg-info/x": b"z",
        },
    )
    listed = checksums.iter_distributed_files(root)
    assert listed == ["a.py"]


def test_malformed_record_fails_closed(tmp_path: Path) -> None:
    root = _make_package(tmp_path, {"a.py": b"a\n"})
    (root / checksums.CHECKSUM_FILENAME).write_bytes(b"not-a-valid-line\n")
    problems = checksums.verify(root)
    assert problems  # non-empty: does not silently verify nothing


# --- Integration: the real package record must be a drift-free fixed point ---


def test_real_package_record_has_no_drift() -> None:
    assert checksums.verify(PACKAGE_ROOT) == []


def test_real_record_preserves_historical_signed_artifacts() -> None:
    # The signed 1.1.0 ratified manifest and its ratification record are historical
    # evidence; they must be inside the checksum scope, not excluded as "generated".
    listed = set(checksums.iter_distributed_files(PACKAGE_ROOT))
    assert "thirstys-standard-v3q.ratified.manifest.yaml" in listed
    assert "owner-ratification.json" in listed
    assert "thirstys-standard-v3q.successor.manifest.yaml" in listed


def test_regeneration_is_stable_on_the_real_package() -> None:
    assert checksums.generate(PACKAGE_ROOT) == (PACKAGE_ROOT / "SHA256SUMS").read_text(
        encoding="utf-8"
    )
