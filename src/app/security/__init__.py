"""Security framework for Project-AI.

This module provides comprehensive security controls including:
- Environment hardening and validation
- Secure data ingestion and parsing
- AWS cloud security integration
- Web service security
- Agent encapsulation and adversarial controls
- Database security
- Monitoring and alerting
- Path traversal protection
"""

# Import path security (always available, no dependencies)
from .path_security import (
    PathTraversalError as PathTraversalError,
)
from .path_security import (
    is_safe_symlink as is_safe_symlink,
)
from .path_security import (
    safe_open as safe_open,
)
from .path_security import (
    safe_path_join as safe_path_join,
)
from .path_security import (
    sanitize_filename as sanitize_filename,
)
from .path_security import (
    validate_filename as validate_filename,
)

# Import core security components (with graceful degradation)
try:
    from .data_validation import DataPoisoningDefense, SecureDataParser
except ImportError:
    DataPoisoningDefense = None
    SecureDataParser = None

try:
    from .environment_hardening import EnvironmentHardening
except ImportError:
    EnvironmentHardening = None

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
    "PathTraversalError",
    "is_safe_symlink",
    "safe_open",
    "safe_path_join",
    "sanitize_filename",
    "validate_filename",
]
