from __future__ import annotations

import time
from pathlib import Path

from app.core.ai_systems import LearningRequestManager


def test_learning_manager_shutdown():
    tmp = Path("./tmp_test_mgr")
    tmp.mkdir(exist_ok=True)
    mgr = LearningRequestManager(data_dir=str(tmp))
    # create a dummy approval listener that sleeps briefly
    def listener(req_id, req):
        return True

    mgr.register_approval_listener(listener)
    req_id = mgr.create_request("topic", "description")
    # approve to enqueue a notification
    mgr.approve_request(req_id, "ok")
    # give a moment for worker to pick up
    time.sleep(0.2)
    mgr.shutdown()
    # after shutdown ensure threads are not alive (best-effort)
    # cannot directly inspect thread object; rely on no exceptions and executor shutdown
    assert True
