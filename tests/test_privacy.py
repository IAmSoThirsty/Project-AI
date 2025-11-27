from app.agents.privacy import PrivacyGuardian


def test_find_and_redact():
    p = PrivacyGuardian()
    text = "contact me at test@example.com or +1 555 1234567"
    findings = p.find_pii(text)
    assert any(f["type"] == "email" for f in findings)
    red = p.redact(text)
    assert "[REDACTED_EMAIL]" in red
    assert "[REDACTED_PHONE]" in red
