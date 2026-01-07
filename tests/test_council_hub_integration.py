import os
import tempfile

from app.core.council_hub import CouncilHub, get_council_hub


class DummyAgent:
    def __init__(self):
        self.received = []
        self.deactivated = False

    def receive_message(self, from_id: str, message: str):
        self.received.append((from_id, message))

    def deactivate(self):
        self.deactivated = True


def test_route_message_delivered_and_agent_registration():
    hub = CouncilHub()
    # ensure fresh singleton
    try:
        # register dummy agent
        agent = DummyAgent()
        hub.register_agent("dummy", agent)

        res = hub.route_message("tester", "dummy", "hello")
        assert res.get("delivered") is True
        assert agent.received == [("tester", "hello")]

        # route to project shorthand when no project registered -> unknown_recipient
        res2 = hub.route_message("tester", hub.project_shorthand, "ping")
        assert res2.get("delivered") is False
        assert res2.get("reason") == "unknown_recipient"
    finally:
        # cleanup singleton for other tests
        try:
            # reset module-level default hub
            from app.core import council_hub as _ch

            _ch._default_hub = None
        except Exception:
            pass


def test_cut_communication_disables_agent():
    hub = CouncilHub()
    try:
        agent = DummyAgent()
        hub.register_agent("to_cut", agent)
        # cut communication
        hub._cut_communication("to_cut")
        assert hub._agents["to_cut"]["active"] is False
        assert agent.deactivated is True
    finally:
        try:
            from app.core import council_hub as _ch

            _ch._default_hub = None
        except Exception:
            pass
