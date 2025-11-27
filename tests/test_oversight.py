import json

from app.agents.oversight import OversightAgent


class MockAudit:
    def __init__(self):
        self.calls = []

    def record_event(self, name, details):
        self.calls.append((name, details))
        return True


def test_policy_deny_triggers_and_audit_called():
    mock = MockAudit()
    policy = {"deny": ["destroy the world"], "allow": []}
    o = OversightAgent(policy=policy, audit_agent=mock)

    allowed, reason = o.evaluate("We will destroy the world tomorrow", context={})
    assert not allowed
    assert "Policy deny matched" in reason
    # audit should have been called with oversight.deny
    assert any(call[0] == "oversight.deny" for call in mock.calls)


def test_allow_but_context_endangers_humanity_denied():
    mock = MockAudit()
    policy = {"allow": ["please proceed"], "deny": []}
    o = OversightAgent(policy=policy, audit_agent=mock)

    # Even though action matches allow, context indicates catastrophic risk
    allowed, reason = o.evaluate(
        "Please proceed with the operation", context={"endangers_humanity": True}
    )
    assert not allowed
    assert "Fourth Law" in reason or "humanity" in reason.lower()


def test_keyword_severity_scores_and_threshold():
    o = OversightAgent()

    # 'kill' is a high-severity keyword in default map
    allowed, reason = o.evaluate("We will kill the target", context={})
    assert not allowed

    # benign text should be allowed
    allowed2, reason2 = o.evaluate("Say hello to the neighbor", context={})
    assert allowed2


def test_audit_called_on_decision_for_non_policy():
    mock = MockAudit()
    o = OversightAgent(audit_agent=mock)

    allowed, reason = o.evaluate("This is harmless test text", context={})
    # audit should record a decision event
    assert any(call[0] == "oversight.decision" for call in mock.calls)
    # verify details reflect the allowed outcome
    decision_calls = [c for c in mock.calls if c[0] == "oversight.decision"]
    assert decision_calls
    _, details = decision_calls[0]
    assert "allowed" in details


def test_load_policy_from_file_and_sum_scoring(tmp_path):
    # create a temporary policy file with sum scoring and custom keywords
    policy = {
        "deny": ["forbidden_act"],
        "allow": [],
        "keyword_severity": {"minor": 0.2, "major": 0.6, "kill": 1.0},
        "threshold": 0.7,
        "scoring": "sum",
    }
    pfile = tmp_path / "oversight_policy.json"
    pfile.write_text(json.dumps(policy), encoding="utf-8")

    mock = MockAudit()
    o = OversightAgent(policy_path=str(pfile), audit_agent=mock)

    # Text containing 'minor' + 'major' should sum to 0.8 -> exceed threshold -> denied
    allowed, reason = o.evaluate(
        "This is a minor issue and a major concern", context={}
    )
    assert not allowed
    assert "score" in reason.lower() or "Denied" in reason

    # If contains 'forbidden_act' substring should be denied by policy immediately
    allowed2, reason2 = o.evaluate("This contains forbidden_act explicitly", context={})
    assert not allowed2
    assert "Policy deny" in reason2
