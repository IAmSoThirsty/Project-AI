from app.agents.personalization import PersonalizationAgent


def test_profile_update_get():
    p = PersonalizationAgent()
    p.update_profile({"theme": "dark"})
    prof = p.get_profile()
    assert prof["theme"] == "dark"
