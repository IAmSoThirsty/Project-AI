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

from .agent_security import AgentEncapsulation
from .aws_integration import AWSSecurityManager
from .data_validation import DataPoisoningDefense, SecureDataParser
from .database_security import SecureDatabaseManager
from .environment_hardening import EnvironmentHardening
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
