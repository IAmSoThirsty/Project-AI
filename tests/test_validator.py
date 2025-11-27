from app.agents.validator import ValidatorAgent


def test_validator_basic():
    v = ValidatorAgent()
    ok, msg = v.validate("hello")
    assert ok

    ok2, msg2 = v.validate("")
    assert not ok2

    ok3, msg3 = v.validate(None)
    assert not ok3
