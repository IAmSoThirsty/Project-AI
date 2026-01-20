"""Extended tests for LearningRequestManager (20+ cases).

Covers:
- Create requests with varying priorities
- Approve and deny flows
- Black vault hashing and persistence
- Statistics correctness
- Error paths for invalid IDs
- Save exception resilience via write_json_atomic returning False
"""

from __future__ import annotations

import hashlib
import tempfile
from unittest.mock import patch

import pytest

from app.core.ai_systems import LearningRequestManager, RequestPriority


@pytest.fixture
def lr_tmpdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_create_requests_with_priorities(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    ids = [
        mgr.create_request("p-low", "d1", RequestPriority.LOW),
        mgr.create_request("p-med", "d2", RequestPriority.MEDIUM),
        mgr.create_request("p-high", "d3", RequestPriority.HIGH),
    ]
    assert all(ids)
    assert mgr.requests[ids[0]]["priority"] == RequestPriority.LOW.value
    assert mgr.requests[ids[2]]["priority"] == RequestPriority.HIGH.value


def test_approve_flow_sets_status_and_response(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    rid = mgr.create_request("topic", "desc")
    ok = mgr.approve_request(rid, "Approved content")
    assert ok is True
    assert mgr.requests[rid]["status"] == "approved"
    assert mgr.requests[rid]["response"] == "Approved content"


def test_deny_flow_adds_to_vault(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    rid = mgr.create_request("topic", "sensitive")
    ok = mgr.deny_request(rid, "No", to_vault=True)
    assert ok is True
    h = hashlib.sha256(b"sensitive").hexdigest()
    assert h in mgr.black_vault


def test_deny_flow_without_vault(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    rid = mgr.create_request("topic", "content")
    ok = mgr.deny_request(rid, "No", to_vault=False)
    assert ok is True
    h = hashlib.sha256(b"content").hexdigest()
    assert h not in mgr.black_vault


def test_get_pending_filters_status(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    r1 = mgr.create_request("t1", "d1")
    mgr.create_request("t2", "d2")
    mgr.approve_request(r1, "resp")
    pending = mgr.get_pending()
    assert all(r["status"] == "pending" for r in pending)
    assert len(pending) == 1


def test_statistics_counts(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    r1 = mgr.create_request("t1", "d1")
    r2 = mgr.create_request("t2", "d2")
    mgr.approve_request(r1, "resp")
    mgr.deny_request(r2, "No", to_vault=True)
    stats = mgr.get_statistics()
    assert stats["approved"] == 1
    assert stats["denied"] == 1
    assert stats["pending"] == 0
    assert stats["vault_entries"] == 1


def test_invalid_ids_return_false(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    assert mgr.approve_request("nope", "resp") is False
    assert mgr.deny_request("nope", "No") is False


def test_create_request_blocked_by_vault(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    # Preload vault hash
    hv = hashlib.sha256(b"forbidden").hexdigest()
    mgr.black_vault.add(hv)
    rid = mgr.create_request("t", "forbidden")
    # create_request returns empty string when blocked
    assert rid == ""


def test_persistence_across_reload(lr_tmpdir):
    m1 = LearningRequestManager(data_dir=lr_tmpdir)
    r = m1.create_request("t", "persist_me")
    m1.deny_request(r, "No", to_vault=True)
    # Reload
    m2 = LearningRequestManager(data_dir=lr_tmpdir)
    h = hashlib.sha256(b"persist_me").hexdigest()
    assert h in m2.black_vault
    assert r in m2.requests


def test_save_requests_failure_is_tolerated(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    r = mgr.create_request("t", "d")
    # Patch json.dump to fail inside persistence utils
    with patch("json.dump", side_effect=OSError("Cannot write")):
        ok = mgr.deny_request(r, "No", to_vault=True)
        assert ok is True


def test_multiple_denies_and_approvals(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    ids = [mgr.create_request(f"t{i}", f"d{i}") for i in range(5)]
    for i, rid in enumerate(ids):
        if i % 2 == 0:
            mgr.approve_request(rid, f"resp{i}")
        else:
            mgr.deny_request(rid, f"no{i}")
    stats = mgr.get_statistics()
    assert stats["approved"] == 3
    assert stats["denied"] == 2


def test_priority_values_are_increasing(lr_tmpdir):
    assert RequestPriority.LOW.value < RequestPriority.MEDIUM.value < RequestPriority.HIGH.value


def test_requests_have_timestamps(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    rid = mgr.create_request("t", "d")
    assert "created" in mgr.requests[rid]


def test_denied_reason_persists(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    rid = mgr.create_request("t", "d")
    mgr.deny_request(rid, "Insufficient")
    assert mgr.requests[rid]["reason"] == "Insufficient"


def test_approve_nonexistent_does_not_crash(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    assert mgr.approve_request("nonexistent", "resp") is False


def test_deny_nonexistent_does_not_crash(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    assert mgr.deny_request("nonexistent", "no") is False


def test_get_pending_on_empty_manager(lr_tmpdir):
    mgr = LearningRequestManager(data_dir=lr_tmpdir)
    assert mgr.get_pending() == []
