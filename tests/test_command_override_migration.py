"""Test for CommandOverrideSystem - password functionality removed."""

from app.core.command_override import CommandOverrideSystem


def test_command_override_basic_functionality(tmp_path):
    """Test basic command override without authentication."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    sys = CommandOverrideSystem(data_dir=str(data_dir))

    # Test direct protocol override
    assert sys.override_protocol("content_filter", False) is True
    assert sys.is_protocol_enabled("content_filter") is False

    # Test re-enabling
    assert sys.override_protocol("content_filter", True) is True
    assert sys.is_protocol_enabled("content_filter") is True

