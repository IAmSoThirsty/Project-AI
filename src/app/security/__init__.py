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

from .environment_hardening import EnvironmentHardening
from .data_validation import SecureDataParser, DataPoisoningDefense
from .aws_integration import AWSSecurityManager
from .agent_security import AgentEncapsulation
from .database_security import SecureDatabaseManager
from .monitoring import SecurityMonitor

__all__ = [
    "EnvironmentHardening",
    "SecureDataParser",
    "DataPoisoningDefense",
    "AWSSecurityManager",
    "AgentEncapsulation",
    "SecureDatabaseManager",
    "SecurityMonitor",
]
