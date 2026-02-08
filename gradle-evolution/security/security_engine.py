"""
Security Engine
===============

Integrates security_hardening.yaml configuration with build security enforcement.
Provides runtime security controls and agent-based security validation.
"""

import logging
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logger = logging.getLogger(__name__)


class SecurityContext:
    """Security context for build operations."""

    def __init__(
        self,
        agent: str,
        allowed_paths: List[str],
        allowed_operations: List[str],
        credential_ttl_hours: int
    ):
        """
        Initialize security context.

        Args:
            agent: Agent identifier
            allowed_paths: Allowed file paths (glob patterns)
            allowed_operations: Allowed operation types
            credential_ttl_hours: Credential time-to-live in hours
        """
        self.agent = agent
        self.allowed_paths = allowed_paths
        self.allowed_operations = allowed_operations
        self.credential_ttl_hours = credential_ttl_hours


class SecurityEngine:
    """
    Enforces security policies from security_hardening.yaml.
    Implements least privilege, path restrictions, and operation controls.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize security engine.

        Args:
            config_path: Path to security_hardening.yaml (default: config/)
        """
        self.config_path = config_path or Path("config/security_hardening.yaml")
        self.config = self._load_config()
        self.access_log: List[Dict[str, Any]] = []
        self.denied_operations: List[Dict[str, Any]] = []
        logger.info(f"Security engine initialized from: {self.config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Load security configuration from YAML."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config not found: {self.config_path}, using defaults")
                return self._default_config()
            
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            
            logger.info("Security configuration loaded")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults", exc_info=True)
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default security configuration."""
        return {
            "least_privilege": {
                "agents": {
                    "build_agent": {
                        "allowed_paths": ["build/**", "src/**"],
                        "allowed_operations": ["read", "write", "execute"],
                        "credential_ttl_hours": 2,
                    }
                }
            }
        }

    def get_security_context(self, agent: str) -> Optional[SecurityContext]:
        """
        Get security context for an agent.

        Args:
            agent: Agent identifier

        Returns:
            SecurityContext or None if agent not found
        """
        try:
            agents = self.config.get("least_privilege", {}).get("agents", {})
            agent_config = agents.get(agent)
            
            if not agent_config:
                logger.warning(f"No security context for agent: {agent}")
                return None
            
            return SecurityContext(
                agent=agent,
                allowed_paths=agent_config.get("allowed_paths", []),
                allowed_operations=agent_config.get("allowed_operations", []),
                credential_ttl_hours=agent_config.get("credential_ttl_hours", 1)
            )
            
        except Exception as e:
            logger.error(f"Error getting security context: {e}", exc_info=True)
            return None

    def validate_path_access(
        self,
        agent: str,
        path: str,
        operation: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate path access for agent.

        Args:
            agent: Agent requesting access
            path: Path to access
            operation: Operation type (read/write/execute)

        Returns:
            Tuple of (is_allowed, reason)
        """
        try:
            context = self.get_security_context(agent)
            if not context:
                reason = f"No security context for agent: {agent}"
                self._log_denied_operation(agent, path, operation, reason)
                return False, reason
            
            # Check operation allowed
            if operation not in context.allowed_operations:
                reason = f"Operation '{operation}' not allowed for agent '{agent}'"
                self._log_denied_operation(agent, path, operation, reason)
                return False, reason
            
            # Check path allowed (glob matching)
            path_allowed = any(
                fnmatch(path, pattern)
                for pattern in context.allowed_paths
            )
            
            if not path_allowed:
                reason = f"Path '{path}' not in allowed paths for agent '{agent}'"
                self._log_denied_operation(agent, path, operation, reason)
                return False, reason
            
            # Log successful access
            self._log_access(agent, path, operation, allowed=True)
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating path access: {e}", exc_info=True)
            return False, f"Validation error: {str(e)}"

    def validate_batch_operations(
        self,
        agent: str,
        operations: List[tuple[str, str]]
    ) -> Dict[str, tuple[bool, Optional[str]]]:
        """
        Validate multiple operations in batch.

        Args:
            agent: Agent requesting access
            operations: List of (path, operation) tuples

        Returns:
            Dictionary mapping (path, operation) to (is_allowed, reason)
        """
        results = {}
        for path, operation in operations:
            key = f"{path}:{operation}"
            results[key] = self.validate_path_access(agent, path, operation)
        return results

    def get_allowed_paths(self, agent: str) -> List[str]:
        """
        Get allowed paths for agent.

        Args:
            agent: Agent identifier

        Returns:
            List of allowed path patterns
        """
        context = self.get_security_context(agent)
        return context.allowed_paths if context else []

    def get_allowed_operations(self, agent: str) -> List[str]:
        """
        Get allowed operations for agent.

        Args:
            agent: Agent identifier

        Returns:
            List of allowed operations
        """
        context = self.get_security_context(agent)
        return context.allowed_operations if context else []

    def get_credential_ttl(self, agent: str) -> int:
        """
        Get credential TTL for agent.

        Args:
            agent: Agent identifier

        Returns:
            TTL in hours (default: 1)
        """
        context = self.get_security_context(agent)
        return context.credential_ttl_hours if context else 1

    def get_access_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent access log entries.

        Args:
            limit: Maximum number of entries

        Returns:
            List of access log entries
        """
        return self.access_log[-limit:]

    def get_denied_operations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent denied operations.

        Args:
            limit: Maximum number of entries

        Returns:
            List of denied operations
        """
        return self.denied_operations[-limit:]

    def get_security_summary(self) -> Dict[str, Any]:
        """
        Get security summary statistics.

        Returns:
            Summary dictionary
        """
        try:
            total_accesses = len(self.access_log)
            allowed_accesses = sum(1 for log in self.access_log if log.get("allowed"))
            denied_accesses = len(self.denied_operations)
            
            agents = set(log.get("agent") for log in self.access_log)
            
            return {
                "total_accesses": total_accesses,
                "allowed_accesses": allowed_accesses,
                "denied_accesses": denied_accesses,
                "unique_agents": len(agents),
                "agents": list(agents),
                "configured_agents": list(
                    self.config.get("least_privilege", {})
                    .get("agents", {})
                    .keys()
                ),
            }
            
        except Exception as e:
            logger.error(f"Error getting security summary: {e}", exc_info=True)
            return {"error": str(e)}

    def clear_logs(self) -> None:
        """Clear access and denied operation logs."""
        self.access_log.clear()
        self.denied_operations.clear()
        logger.info("Security logs cleared")

    def _log_access(
        self,
        agent: str,
        path: str,
        operation: str,
        allowed: bool
    ) -> None:
        """Log access attempt."""
        from datetime import datetime
        
        self.access_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "path": path,
            "operation": operation,
            "allowed": allowed,
        })
        
        # Keep last 10000 entries
        if len(self.access_log) > 10000:
            self.access_log = self.access_log[-10000:]

    def _log_denied_operation(
        self,
        agent: str,
        path: str,
        operation: str,
        reason: str
    ) -> None:
        """Log denied operation."""
        from datetime import datetime
        
        self.denied_operations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "path": path,
            "operation": operation,
            "reason": reason,
        })
        
        # Keep last 1000 denied operations
        if len(self.denied_operations) > 1000:
            self.denied_operations = self.denied_operations[-1000:]
        
        logger.warning(f"Denied operation: {agent} {operation} {path} - {reason}")


__all__ = ["SecurityEngine", "SecurityContext"]
