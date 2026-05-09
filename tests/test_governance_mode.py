"""tests/test_governance_mode.py — Upgrade 8: Governance Mode."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from app.core.governance_mode import (
    GovernanceMode,
    get_governance_mode,
    set_governance_mode,
)


class TestGovernanceMode:
    def setup_method(self):
        # Reset to single node before each test
        import app.core.governance_mode as gm
        gm._CURRENT_MODE = GovernanceMode.SINGLE_NODE

    def test_default_is_single_node(self):
        assert get_governance_mode() == GovernanceMode.SINGLE_NODE

    def test_set_single_node_works(self):
        set_governance_mode(GovernanceMode.SINGLE_NODE)
        assert get_governance_mode() == GovernanceMode.SINGLE_NODE

    def test_distributed_raises_not_implemented(self):
        with pytest.raises(NotImplementedError) as exc_info:
            set_governance_mode(GovernanceMode.DISTRIBUTED)
        assert "DISTRIBUTED" in str(exc_info.value)
        assert "not yet implemented" in str(exc_info.value).lower()

    def test_bft_raises_not_implemented(self):
        with pytest.raises(NotImplementedError) as exc_info:
            set_governance_mode(GovernanceMode.BFT)
        assert "BFT" in str(exc_info.value)

    def test_error_message_references_roadmap_doc(self):
        try:
            set_governance_mode(GovernanceMode.DISTRIBUTED)
        except NotImplementedError as e:
            assert "GOVERNANCE_MICROKERNEL" in str(e)

    def test_mode_enum_values(self):
        assert GovernanceMode.SINGLE_NODE.value == "SINGLE_NODE"
        assert GovernanceMode.DISTRIBUTED.value == "DISTRIBUTED"
        assert GovernanceMode.BFT.value == "BFT"
