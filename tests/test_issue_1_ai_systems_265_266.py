"""Test #1: ai_systems.py lines 265-266 - _save_requests exception handler."""

import tempfile
from unittest.mock import patch

from app.core.ai_systems import LearningRequestManager


def test_learning_save_requests_exception_lines_265_266():
    """Force _save_requests to trigger exception handler (lines 265-266).

    When json.dump fails, we should catch the exception and log it.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        learning = LearningRequestManager(data_dir=tmpdir)

        # Create a request
        req_id = learning.create_request("topic", "description")

        # Mock json.dump to raise an exception
        with patch("json.dump") as mock_dump:
            mock_dump.side_effect = OSError("Cannot write file")

            # Try to deny request (which calls _save_requests)
            # This should NOT raise - it should catch the exception
            result = learning.deny_request(req_id, "reason", to_vault=True)

            # Should still return True even though save failed
            assert result is True

            # Verify json.dump was called (it failed but that's okay)
            assert mock_dump.called


if __name__ == "__main__":
    test_learning_save_requests_exception_lines_265_266()
    print("✅ Test passed! ai_systems.py lines 265-266 covered")
