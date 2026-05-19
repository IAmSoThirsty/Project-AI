import pytest
import tempfile
from pathlib import Path

def test_imports_work():
    '''Verify all main imports work'''
    from src.app.core import ai_systems
    from src.app.core import hydra_50_engine
    from src.app.core import intelligence_engine
    from src.app.core import secure_comms
    from src.security import asymmetric_security
    assert True

def test_four_laws_basic():
    from src.app.core.ai_systems import FourLaws
    laws = FourLaws()
    result = laws.validate_action('test')
    assert result is not None

def test_hydra_scenarios_exist():
    from src.app.core.hydra_50_engine import SCENARIO_REGISTRY
    assert len(SCENARIO_REGISTRY) > 0

def test_security_context_works():
    from src.security.asymmetric_security import SecurityContext
    ctx = SecurityContext('user', 'action')
    assert ctx.user_id == 'user'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
