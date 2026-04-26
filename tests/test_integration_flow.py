import os
import tempfile

from app.core.ai_systems import AIPersona, LearningRequestManager
from app.core.user_manager import UserManager


def test_end_to_end_user_learning_persona_flow():
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = os.path.join(tmpdir, "users.json")
        learning_dir = os.path.join(tmpdir, "learning")
        persona_dir = os.path.join(tmpdir, "persona")

        user_manager = UserManager(users_file=users_file)
        assert user_manager.create_user("integration", "test123") is True

        learning = LearningRequestManager(data_dir=learning_dir)
        req_id = learning.create_request("feature", "Add integration tests")
        assert req_id in learning.requests

        # Approve request to simulate workflow
        approved = learning.approve_request(req_id, response="Approved for integration")
        assert approved is True

        persona = AIPersona(data_dir=persona_dir)
        persona.update_conversation_state(is_user=True)
        time_before = persona.last_user_message_time

        persona.update_conversation_state(is_user=False)
        persona.update_conversation_state(is_user=True)
        time_after = persona.last_user_message_time

        assert persona.total_interactions >= 3
        assert time_before is not None
        assert time_after is not None
        assert time_after >= time_before

        # Ensure user info persisted and password hash present
        user_manager2 = UserManager(users_file=users_file)
        user_record = user_manager2.users.get("integration")
        assert user_record is not None
        assert "password_hash" in user_record
