"""Security framework for Project-AI.

This module provides comprehensive security controls including:
- Environment hardening and validation
- Secure data ingestion and parsing
- AWS cloud security integration
- Web service security
- Agent encapsulation and adversarial controls
- Database security
- Monitoring and alerting
"""

# Import core security components (always available)
from .data_validation import DataPoisoningDefense, SecureDataParser
from .environment_hardening import EnvironmentHardening

# Optional imports (graceful degradation if dependencies missing)
try:
    from .agent_security import AgentEncapsulation
except ImportError:
    AgentEncapsulation = None

try:
    from .aws_integration import AWSSecurityManager
except ImportError:
    AWSSecurityManager = None

try:
    from .database_security import SecureDatabaseManager
except ImportError:
    SecureDatabaseManager = None

try:
    from .monitoring import SecurityMonitor
except ImportError:
    SecurityMonitor = None

__all__ = [
    "EnvironmentHardening",
    "SecureDataParser",
    "DataPoisoningDefense",
    "AWSSecurityManager",
    "AgentEncapsulation",
    "SecureDatabaseManager",
    "SecurityMonitor",
]
