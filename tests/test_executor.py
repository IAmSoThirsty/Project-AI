from app.agents.executor import ExecutorAgent


def test_execute_plan_dry_run():
    ex = ExecutorAgent()
    res = ex.execute_plan(["step1", ""], dry_run=True)
    assert isinstance(res, list)
    assert res[0]["status"] == "ok"
    assert res[1]["status"] == "skipped"
