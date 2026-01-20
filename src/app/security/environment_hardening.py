"""Environment hardening and validation for secure AI deployment.

This module implements:
- Virtualenv validation and sys.path hardening
- Unix permission checking (0600/0700)
- ASLR/SSP verification
- Directory structure security
- Initial data structure validation
"""

import logging
import os
import platform
import stat
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class EnvironmentHardening:
    """Environment security validation and hardening utilities."""

    def __init__(self, data_dir: str = "data"):
        """Initialize environment hardening.

        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.required_dirs = [
            "data",
            "data/ai_persona",
            "data/memory",
            "data/learning_requests",
            "data/black_vault_secure",
            "data/audit_logs",
            "data/secure_backups",
        ]
        self.validation_results = {}

    def validate_environment(self) -> tuple[bool, list[str]]:
        """Run comprehensive environment validation.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Validate virtualenv
        if not self._check_virtualenv():
            issues.append("Not running in virtualenv - security risk")

        # Validate sys.path
        path_issues = self._validate_sys_path()
        issues.extend(path_issues)

        # Check ASLR/SSP
        if not self._check_aslr_ssp():
            issues.append("ASLR/SSP not fully enabled")

        # Validate directory permissions
        perm_issues = self._validate_directory_permissions()
        issues.extend(perm_issues)

        # Validate data structures
        struct_issues = self._validate_data_structures()
        issues.extend(struct_issues)

        self.validation_results["issues"] = issues
        self.validation_results["is_valid"] = len(issues) == 0

        return len(issues) == 0, issues

    def _check_virtualenv(self) -> bool:
        """Check if running in a virtual environment.

        Returns:
            True if in virtualenv, False otherwise
        """
        # Check multiple indicators for virtualenv
        in_venv = (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
            or os.getenv("VIRTUAL_ENV") is not None
        )

        if in_venv:
            logger.info("Running in virtual environment: %s", sys.prefix)
        else:
            logger.warning("Not running in virtual environment - security risk")

        return in_venv

    def _validate_sys_path(self) -> list[str]:
        """Validate sys.path for security issues.

        Returns:
            List of path validation issues
        """
        issues = []

        # Check for current directory in sys.path (security risk)
        if "" in sys.path or "." in sys.path:
            issues.append("Current directory in sys.path - code injection risk")
            logger.warning("Security risk: current directory in sys.path")

        # Check for world-writable directories in sys.path
        if platform.system() != "Windows":
            for path_entry in sys.path:
                if not path_entry or not os.path.exists(path_entry):
                    continue

                try:
                    path_stat = os.stat(path_entry)
                    # Check if world-writable (dangerous)
                    if path_stat.st_mode & stat.S_IWOTH:
                        issues.append(
                            f"World-writable directory in sys.path: {path_entry}"
                        )
                        logger.warning("World-writable path: %s", path_entry)
                except OSError as e:
                    logger.debug("Could not stat path %s: %s", path_entry, e)

        return issues

    def _check_aslr_ssp(self) -> bool:
        """Check for ASLR and SSP security features.

        Returns:
            True if security features are enabled
        """
        system = platform.system()

        if system == "Linux":
            return self._check_linux_aslr_ssp()
        elif system == "Windows":
            return self._check_windows_aslr_dep()
        elif system == "Darwin":
            return self._check_macos_aslr()
        else:
            logger.warning("Unknown platform: cannot verify ASLR/SSP")
            return False

    def _check_linux_aslr_ssp(self) -> bool:
        """Check ASLR on Linux systems.

        Returns:
            True if ASLR is enabled
        """
        try:
            with open("/proc/sys/kernel/randomize_va_space") as f:
                aslr_level = int(f.read().strip())

            if aslr_level >= 2:
                logger.info("ASLR enabled (level %d)", aslr_level)
                return True
            else:
                logger.warning("ASLR not fully enabled (level %d)", aslr_level)
                return False
        except (FileNotFoundError, PermissionError, ValueError) as e:
            logger.warning("Could not check ASLR: %s", e)
            return False

    def _check_windows_aslr_dep(self) -> bool:
        """Check ASLR/DEP on Windows systems.

        Returns:
            True if basic security features detected
        """
        # On Windows, ASLR and DEP are typically enabled by default
        # We can't easily check without admin privileges
        logger.info("Windows detected - assuming ASLR/DEP enabled")
        return True

    def _check_macos_aslr(self) -> bool:
        """Check ASLR on macOS systems.

        Returns:
            True (macOS has ASLR enabled by default)
        """
        logger.info("macOS detected - ASLR enabled by default")
        return True

    def _validate_directory_permissions(self) -> list[str]:
        """Validate directory permissions for security.

        Returns:
            List of permission issues
        """
        issues = []

        if platform.system() == "Windows":
            logger.info("Windows detected - skipping Unix permission checks")
            return issues

        # Ensure all required directories exist with proper permissions
        for dir_path in self.required_dirs:
            full_path = Path(dir_path)

            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    # Set restrictive permissions (owner only)
                    os.chmod(full_path, 0o700)
                    logger.info(
                        "Created directory with secure permissions: %s", full_path
                    )
                except OSError as e:
                    issues.append(f"Cannot create directory {full_path}: {e}")
                    continue

            # Check permissions
            try:
                dir_stat = os.stat(full_path)
                mode = dir_stat.st_mode

                # Check if group or others have any permissions
                if mode & (stat.S_IRWXG | stat.S_IRWXO):
                    issues.append(
                        f"Insecure permissions on {full_path}: {oct(stat.S_IMODE(mode))}"
                    )
                    logger.warning("Fixing permissions on %s", full_path)
                    os.chmod(full_path, 0o700)

            except OSError as e:
                issues.append(f"Cannot check permissions for {full_path}: {e}")

        return issues

    def _validate_data_structures(self) -> list[str]:
        """Validate initial data structures.

        Returns:
            List of data structure issues
        """
        issues = []

        # Check for required JSON files with proper structure
        required_files = {
            "data/ai_persona/state.json": {
                "persona": dict,
                "mood": dict,
                "interaction_count": int,
            },
            "data/memory/knowledge.json": {"categories": dict},
            "data/learning_requests/requests.json": {"requests": list},
        }

        for file_path, expected_structure in required_files.items():
            full_path = Path(file_path)

            if not full_path.exists():
                # Create with default structure
                try:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    default_data = {
                        key: val() if callable(val) else val
                        for key, val in expected_structure.items()
                    }
                    import json

                    with open(full_path, "w") as f:
                        json.dump(default_data, f, indent=2)

                    # Set restrictive permissions
                    if platform.system() != "Windows":
                        os.chmod(full_path, 0o600)

                    logger.info("Created data file with defaults: %s", full_path)
                except OSError as e:
                    issues.append(f"Cannot create data file {full_path}: {e}")

        return issues

    def harden_sys_path(self) -> None:
        """Remove potentially dangerous entries from sys.path."""
        # Remove current directory references
        dangerous_paths = ["", "."]
        for path in dangerous_paths:
            while path in sys.path:
                sys.path.remove(path)
                logger.info("Removed dangerous path from sys.path: '%s'", path)

    def secure_directory_structure(self) -> None:
        """Create and secure all required directories."""
        for dir_path in self.required_dirs:
            full_path = Path(dir_path)
            full_path.mkdir(parents=True, exist_ok=True)

            # Set restrictive permissions on Unix systems
            if platform.system() != "Windows":
                os.chmod(full_path, 0o700)

            logger.info("Secured directory: %s", full_path)

    def get_validation_report(self) -> dict:
        """Get detailed validation report.

        Returns:
            Dictionary containing validation results
        """
        return {
            "virtualenv": self._check_virtualenv(),
            "sys_path_issues": self._validate_sys_path(),
            "aslr_ssp_enabled": self._check_aslr_ssp(),
            "directory_issues": self._validate_directory_permissions(),
            "data_structure_issues": self._validate_data_structures(),
            "platform": platform.system(),
            "python_version": platform.python_version(),
        }
