"""Integration test that flows through user onboarding, learning requests, and persona stats."""

from pathlib import Path

from app.core.ai_systems import (
    AIPersona,
    LearningRequestManager,
    RequestPriority,
    RequestStatus,
)
from app.core.user_manager import UserManager


def test_user_learning_request_persona_flow(tmp_path: Path):
    data_dir = tmp_path / "integration_data"
    data_dir.mkdir()

    users_file = data_dir / "users.json"
    manager = UserManager(users_file=str(users_file))

    assert manager.create_user("hero", "StrongPass123!")
    assert manager.authenticate("hero", "StrongPass123!")
    assert manager.current_user == "hero"

    user_data = manager.get_user_data("hero")
    assert user_data["persona"] == "friendly"
    assert "password_hash" not in user_data

    persona = AIPersona(data_dir=str(data_dir))
    persona.update_conversation_state(is_user=True)
    persona.update_conversation_state(is_user=False)

    persona_stats = persona.get_statistics()
    assert persona_stats["interactions"] >= 2

    refreshed_persona = AIPersona(data_dir=str(data_dir))
    assert refreshed_persona.total_interactions >= persona_stats["interactions"]

    request_manager = LearningRequestManager(data_dir=str(data_dir))
    description = (
        "Integration test prompt that references user hero and learning flows."
    )
    req_id = request_manager.create_request(
        topic="Integration workflows",
        description=description,
        priority=RequestPriority.HIGH,
    )
    assert req_id
    assert request_manager.requests[req_id]["status"] == RequestStatus.PENDING.value

    pending = request_manager.get_pending()
    assert any(req["description"] == description for req in pending)

    assert request_manager.approve_request(req_id, "Approved with details.")
    stats = request_manager.get_statistics()
    assert stats["approved"] == 1
    assert stats["pending"] == 0

    reloaded_manager = LearningRequestManager(data_dir=str(data_dir))
    assert req_id in reloaded_manager.requests
    assert reloaded_manager.requests[req_id]["status"] == RequestStatus.APPROVED.value
