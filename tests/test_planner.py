from app.agents.planner import PlannerAgent


def test_plan_basic():
    p = PlannerAgent()
    steps = p.plan("build a thing")
    assert isinstance(steps, list)
    assert len(steps) >= 3
