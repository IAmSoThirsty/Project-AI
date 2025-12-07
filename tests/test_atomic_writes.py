import json
import os
import time
import hashlib
import multiprocessing

from app.core.ai_systems import (
    _atomic_write_json,
    _acquire_lock,
    _release_lock,
    AIPersona,
    MemoryExpansionSystem,
    LearningRequestManager,
    RequestPriority,
)


def _writer_proc(path: str, idx: int, loops: int = 10, pause: float = 0.01):
    """Process target that writes JSON repeatedly to the same file."""
    # Import inside process to avoid spawn issues
    from app.core.ai_systems import _atomic_write_json

    for i in range(loops):
        _atomic_write_json(path, {"writer": idx, "i": i})
        time.sleep(pause)


def memory_writer(data_dir: str, k: int):
    """Top-level memory writer for multiprocessing (picklable)."""
    from app.core.ai_systems import MemoryExpansionSystem

    m = MemoryExpansionSystem(data_dir=data_dir)
    m.add_knowledge("cat", f"key_{k}", {"val": k})


def test_atomic_write_creates_file_and_content_is_valid(tmp_path):
    fn = tmp_path / "kb.json"
    _atomic_write_json(str(fn), {"a": 1})
    with open(fn, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["a"] == 1


def test_lock_timeout(tmp_path):
    lockfile = str(tmp_path / "test.lock")
    # create the lockfile to simulate held lock
    with open(lockfile, "w", encoding="utf-8") as f:
        f.write("held")
    # _acquire_lock should fail quickly with short timeout
    ok = _acquire_lock(lockfile, timeout=0.2, poll=0.01)
    assert ok is False
    # cleanup
    _release_lock(lockfile)


def test_lock_prevents_simultaneous_writes_threaded(tmp_path):
    target = str(tmp_path / "shared.json")
    procs = []
    for i in range(4):
        p = multiprocessing.Process(target=_writer_proc, args=(target, i, 20, 0.005))
        p.start()
        procs.append(p)
    for p in procs:
        p.join(timeout=10)
        if p.is_alive():
            # Ensure we don't leave orphan processes; terminate and fail the test
            p.terminate()
            p.join(timeout=1)
            assert False, "Writer process did not exit in time"

    # After concurrent writes, ensure JSON file is valid
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert "writer" in data and "i" in data


def test_persona_save_runs_atomically(tmp_path):
    data_dir = str(tmp_path / "data")
    persona = AIPersona(data_dir=data_dir, user_name="Tester")
    persona.adjust_trait("curiosity", -0.1)
    state_file = os.path.join(data_dir, "ai_persona", "state.json")
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
    assert "personality" in state and "curiosity" in state["personality"]


def test_memory_add_knowledge_persists_atomically(tmp_path):
    data_dir = str(tmp_path / "data")
    mem = MemoryExpansionSystem(data_dir=data_dir)
    # Run a few concurrent writers using multiprocessing
    procs = []
    for i in range(6):
        p = multiprocessing.Process(target=memory_writer, args=(data_dir, i))
        p.start()
        procs.append(p)
    for p in procs:
        p.join(timeout=10)
        if p.is_alive():
            # Ensure we don't leave orphan processes; terminate and fail the test
            p.terminate()
            p.join(timeout=1)
            assert False, "Memory writer process did not exit in time"

    kb_file = os.path.join(data_dir, "memory", "knowledge.json")
    with open(kb_file, "r", encoding="utf-8") as f:
        kb = json.load(f)
    assert "cat" in kb


def test_learning_requests_persistence_with_vault(tmp_path):
    data_dir = str(tmp_path / "data_lr")
    mgr1 = LearningRequestManager(data_dir=data_dir)
    req_id = mgr1.create_request("persist_test", "vault_content")
    assert req_id
    ok = mgr1.deny_request(req_id, "Deny for vault", to_vault=True)
    assert ok
    # reload manager and verify vault persisted
    mgr2 = LearningRequestManager(data_dir=data_dir)
    content_hash = hashlib.sha256(b"vault_content").hexdigest()
    assert content_hash in mgr2.black_vault
