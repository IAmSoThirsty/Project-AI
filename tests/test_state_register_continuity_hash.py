"""State Register continuity hash compliance tests."""

from __future__ import annotations

from pathlib import Path

from app.core.state_register import StateRegister


class TestStateRegisterContinuityHash:
    def test_session_contains_continuity_hash_fields(self, tmp_path: Path) -> None:
        register = StateRegister(data_dir=str(tmp_path))

        session = register.start_session(context={"user_id": "alice"})

        assert session.continuity_hash
        assert session.last_timestamp
        assert session.continuity_metadata["user_perceived_gap_seconds"] == 0
        assert register.verify_continuity_hash(session)

    def test_continuity_hash_changes_with_previous_session(self, tmp_path: Path) -> None:
        register = StateRegister(data_dir=str(tmp_path))

        first = register.start_session(context={"user_id": "alice"})
        register.end_session(context={"user_id": "alice"})

        second = register.start_session(context={"user_id": "alice"})

        assert second.previous_session_id == first.session_id
        assert second.continuity_hash != first.continuity_hash
        assert register.verify_continuity_hash(second)

    def test_temporal_context_exposes_hash_verification(self, tmp_path: Path) -> None:
        register = StateRegister(data_dir=str(tmp_path))

        register.start_session(context={"user_id": "alice"})
        ctx = register.get_temporal_context()

        assert "continuity_hash_verified" in ctx
        assert ctx["continuity_hash_verified"] is True
