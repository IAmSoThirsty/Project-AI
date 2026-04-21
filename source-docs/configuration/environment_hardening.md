# Environment Hardening Module

**Module**: `src/app/security/environment_hardening.py` [[src/app/security/environment_hardening.py]]  
**Purpose**: Environment validation and security hardening for secure AI deployment  
**Classification**: Security Configuration  
**Priority**: P0 - Critical Security

---

## Overview

The Environment Hardening Module provides comprehensive environment security validation including virtualenv checking, sys.path hardening, ASLR/SSP verification, directory permission validation, and data structure initialization. It ensures the application runs in a secure, properly configured environment.

### Key Characteristics

- **Virtualenv Validation**: Ensures application runs in isolated environment
- **Path Hardening**: Removes dangerous sys.path entries
- **ASLR/SSP Verification**: Checks memory protection features
- **Permission Enforcement**: Unix 0600/0700 permissions on sensitive directories
- **Data Structure Validation**: Ensures required JSON files exist with proper structure

---

## Architecture

### Class Structure

```python
class EnvironmentHardening:
    """Environment security validation and hardening utilities."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir: Path
        self.required_dirs: list[str]
        self.validation_results: dict
```

### Required Directories

```python
required_dirs = [
    "data",
    "data/ai_persona",
    "data/memory",
    "data/learning_requests",
    "data/black_vault_secure",
    "data/audit_logs",
    "data/secure_backups"
]
```

---

## Core API

### Validation

```python
def validate_environment(self) -> tuple[bool, list[str]]:
    """Run comprehensive environment validation.
    
    Returns:
        (is_valid, list_of_issues)
    
    Validation Steps:
        1. Check virtualenv
        2. Validate sys.path
        3. Check ASLR/SSP
        4. Validate directory permissions
        5. Validate data structures
    
    Example:
        >>> hardening = EnvironmentHardening()
        >>> is_valid, issues = hardening.validate_environment()
        >>> if not is_valid:
        ...     for issue in issues:
        ...         logger.error("Security issue: %s", issue)
    """
```

### Virtualenv Checking

```python
def _check_virtualenv(self) -> bool:
    """Check if running in a virtual environment.
    
    Returns:
        True if in virtualenv, False otherwise
    
    Checks:
        - hasattr(sys, 'real_prefix')
        - sys.base_prefix != sys.prefix
        - VIRTUAL_ENV environment variable
    
    Security Impact:
        Running outside virtualenv risks:
        - System-wide package pollution
        - Privilege escalation
        - Dependency conflicts
    """
```

### Sys.path Validation

```python
def _validate_sys_path(self) -> list[str]:
    """Validate sys.path for security issues.
    
    Returns:
        List of path validation issues
    
    Checks:
        - Current directory ("" or ".") in sys.path
        - World-writable directories in sys.path
    
    Security Risks:
        - Current directory: Code injection via relative imports
        - World-writable paths: Untrusted code execution
    """
```

### ASLR/SSP Verification

```python
def _check_aslr_ssp(self) -> bool:
    """Check for ASLR and SSP security features.
    
    Returns:
        True if security features are enabled
    
    Platform-Specific Checks:
        - Linux: /proc/sys/kernel/randomize_va_space >= 2
        - Windows: Assumed enabled (DEP/ASLR by default)
        - macOS: ASLR enabled by default
    
    Security Features:
        - ASLR: Address Space Layout Randomization
        - SSP: Stack Smashing Protection
        - DEP: Data Execution Prevention (Windows)
    """
```

### Directory Permissions

```python
def _validate_directory_permissions(self) -> list[str]:
    """Validate directory permissions for security.
    
    Returns:
        List of permission issues
    
    Actions:
        - Creates missing directories with 0700 (owner only)
        - Checks existing directories for insecure permissions
        - Fixes permissions on directories with group/other access
    
    Unix Permissions:
        - 0700: drwx------ (owner read/write/execute only)
        - 0600: -rw------- (owner read/write only)
    
    Windows:
        - Permission checks skipped (different security model)
    """
```

### Data Structure Validation

```python
def _validate_data_structures(self) -> list[str]:
    """Validate initial data structures.
    
    Returns:
        List of data structure issues
    
    Required Files:
        - data/ai_persona/state.json
        - data/memory/knowledge.json
        - data/learning_requests/requests.json
    
    Actions:
        - Creates missing files with default structure
        - Sets 0600 permissions on Unix systems
    """
```

### Hardening Operations

```python
def harden_sys_path(self) -> None:
    """Remove potentially dangerous entries from sys.path.
    
    Removes:
        - "" (current directory)
        - "." (current directory)
    
    Side Effects:
        - Modifies sys.path in-place
        - Logs removed entries
    """

def secure_directory_structure(self) -> None:
    """Create and secure all required directories.
    
    Actions:
        - Creates all required directories
        - Sets 0700 permissions on Unix
        - Logs secured directories
    """
```

### Reporting

```python
def get_validation_report(self) -> dict:
    """Get detailed validation report.
    
    Returns:
        {
            "virtualenv": bool,
            "sys_path_issues": list[str],
            "aslr_ssp_enabled": bool,
            "directory_issues": list[str],
            "data_structure_issues": list[str],
            "platform": str,
            "python_version": str
        }
    """
```

---

## Validation Details

### Virtualenv Detection

**Indicators**:
```python
# Python 2 virtualenv
hasattr(sys, 'real_prefix')

# Python 3 venv
sys.base_prefix != sys.prefix

# Environment variable
os.getenv('VIRTUAL_ENV') is not None
```

**Valid Virtualenv**:
```
sys.prefix: /home/user/.venv
sys.base_prefix: /usr
VIRTUAL_ENV: /home/user/.venv
```

### Sys.path Security

**Dangerous Patterns**:
```python
# Current directory in path (code injection risk)
sys.path = ['', '/usr/lib/python3.11', ...]  # ❌

# World-writable directory
stat.S_IWOTH & os.stat('/tmp/python').st_mode  # ❌
```

**Safe Pattern**:
```python
# No current directory, restrictive permissions
sys.path = ['/home/user/.venv/lib/python3.11', ...]  # ✅
```

### ASLR Verification

**Linux** (`/proc/sys/kernel/randomize_va_space`):
- `0`: Disabled
- `1`: Partial (stack randomization)
- `2`: Full (stack + heap + mmap) ✅

**Windows**:
- ASLR enabled by default since Vista
- DEP enabled by default

**macOS**:
- ASLR enabled by default since 10.5

---

## Usage Patterns

### Pattern 1: Startup Validation

```python
from src.app.security.environment_hardening import EnvironmentHardening
import logging
import sys

def main():
    # Initialize hardening
    hardening = EnvironmentHardening()
    
    # Validate environment
    is_valid, issues = hardening.validate_environment()
    
    if not is_valid:
        logging.error("Environment validation failed:")
        for issue in issues:
            logging.error("  - %s", issue)
        sys.exit(1)
    
    # Continue with application startup
    logging.info("Environment validation passed")
```

### Pattern 2: Proactive Hardening

```python
def harden_environment():
    hardening = EnvironmentHardening()
    
    # Harden sys.path
    hardening.harden_sys_path()
    
    # Secure directory structure
    hardening.secure_directory_structure()
    
    # Validate after hardening
    is_valid, issues = hardening.validate_environment()
    
    if not is_valid:
        logging.warning("Hardening incomplete: %s", issues)
    
    return is_valid
```

### Pattern 3: Detailed Reporting

```python
def generate_security_report():
    hardening = EnvironmentHardening()
    report = hardening.get_validation_report()
    
    logging.info("Security Report:")
    logging.info("  Platform: %s", report["platform"])
    logging.info("  Python: %s", report["python_version"])
    logging.info("  Virtualenv: %s", report["virtualenv"])
    logging.info("  ASLR/SSP: %s", report["aslr_ssp_enabled"])
    
    if report["sys_path_issues"]:
        logging.warning("  Sys.path issues: %s", report["sys_path_issues"])
    
    if report["directory_issues"]:
        logging.warning("  Directory issues: %s", report["directory_issues"])
    
    return report
```

### Pattern 4: Conditional Hardening

```python
def smart_harden():
    hardening = EnvironmentHardening()
    is_valid, issues = hardening.validate_environment()
    
    if not is_valid:
        # Try to fix issues
        if "virtualenv" in str(issues):
            logging.error("Not in virtualenv - cannot auto-fix")
            return False
        
        if "sys.path" in str(issues):
            hardening.harden_sys_path()
        
        if "permission" in str(issues):
            hardening.secure_directory_structure()
        
        # Re-validate
        is_valid, remaining_issues = hardening.validate_environment()
    
    return is_valid
```

---

## Security Considerations

### 1. Virtualenv Enforcement

**Risk**: Running outside virtualenv
- System-wide package installation
- Privilege escalation
- Dependency conflicts

**Mitigation**:
```python
if not hardening._check_virtualenv():
    raise SecurityError("Must run in virtualenv")
```

### 2. Sys.path Injection

**Risk**: Current directory in sys.path
- Attacker places malicious module in current directory
- Application imports it via relative import

**Mitigation**:
```python
hardening.harden_sys_path()  # Remove "" and "."
```

### 3. Directory Permissions

**Risk**: World-readable/writable data directories
- Data exfiltration
- Data tampering
- Unauthorized access

**Mitigation**:
```python
# Unix only - enforce 0700/0600
if platform.system() != "Windows":
    os.chmod(data_dir, 0o700)
```

### 4. Memory Protection

**Risk**: ASLR/SSP disabled
- Buffer overflow attacks
- Return-to-libc attacks
- ROP (Return-Oriented Programming)

**Mitigation**:
```python
if not hardening._check_aslr_ssp():
    logging.warning("ASLR/SSP not enabled - memory attacks possible")
```

### 5. Data Structure Integrity

**Risk**: Missing or corrupted JSON files
- Application crashes
- Data loss
- Inconsistent state

**Mitigation**:
```python
# Auto-create with defaults
hardening._validate_data_structures()
```

---

## Platform-Specific Behavior

### Linux

**Permissions**: Enforced (0700/0600)
**ASLR Check**: `/proc/sys/kernel/randomize_va_space`
**Sys.path**: Full validation

```python
# Enable ASLR (requires root)
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
```

### Windows

**Permissions**: Not enforced (different model)
**ASLR Check**: Assumed enabled
**Sys.path**: Checks dangerous entries only

```python
# ASLR enabled by default in modern Windows
```

### macOS

**Permissions**: Enforced (0700/0600)
**ASLR Check**: Assumed enabled
**Sys.path**: Full validation

```python
# ASLR enabled by default since OS X 10.5
```

---

## Testing

### Unit Testing

```python
import pytest
from src.app.security.environment_hardening import EnvironmentHardening
import sys
import os

def test_virtualenv_detection():
    hardening = EnvironmentHardening()
    assert hardening._check_virtualenv() is True

def test_sys_path_validation(monkeypatch):
    hardening = EnvironmentHardening()
    
    # Add dangerous entry
    sys.path.insert(0, "")
    issues = hardening._validate_sys_path()
    assert any("current directory" in issue for issue in issues)
    
    # Clean up
    sys.path.remove("")

def test_harden_sys_path():
    hardening = EnvironmentHardening()
    sys.path.insert(0, "")
    sys.path.insert(0, ".")
    
    hardening.harden_sys_path()
    
    assert "" not in sys.path
    assert "." not in sys.path

def test_directory_creation(tmp_path):
    hardening = EnvironmentHardening(data_dir=str(tmp_path))
    hardening.secure_directory_structure()
    
    assert (tmp_path / "data").exists()
    assert (tmp_path / "data/ai_persona").exists()
```

---

## Troubleshooting

### Issue: Not in Virtualenv

**Symptom**: `validate_environment()` reports virtualenv issue

**Solutions**:
```bash
# Create virtualenv
python -m venv .venv

# Activate (Unix)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: Permission Denied

**Symptom**: Cannot set directory permissions

**Solutions**:
```bash
# Ensure ownership
sudo chown -R $USER:$USER data/

# Manual permission fix
chmod 700 data/
chmod 700 data/*/
```

### Issue: ASLR Not Enabled

**Symptom**: `_check_aslr_ssp()` returns False

**Solutions (Linux)**:
```bash
# Check current setting
cat /proc/sys/kernel/randomize_va_space

# Enable temporarily (requires root)
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space

# Enable permanently
echo "kernel.randomize_va_space=2" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Best Practices

1. **Run Validation Early**: Call `validate_environment()` at application startup
2. **Fail Fast**: Exit with error if validation fails in production
3. **Warn in Development**: Allow bypassing validation in development mode
4. **Log Everything**: Log all validation results and hardening actions
5. **Platform Awareness**: Skip platform-specific checks appropriately
6. **Automated Fix**: Auto-fix permission issues when possible
7. **Monitor Continuously**: Re-validate periodically in long-running processes
8. **Document Requirements**: Document environment requirements in README
9. **CI/CD Integration**: Run validation in CI/CD pipeline
10. **Security Reviews**: Regular security audits of hardening logic

---

## Related Modules

- **Settings Manager**: `config/settings_manager.py` - Configuration with encryption
- **Security Module**: `src/app/security/__init__.py` [[src/app/security/__init__.py]] - Security utilities
- **Command Override**: `src/app/core/command_override.py` [[src/app/core/command_override.py]] - Secure command execution
- **User Manager**: `src/app/core/user_manager.py` [[src/app/core/user_manager.py]] - User authentication

---

## Future Enhancements

1. **Windows ACL Support**: Implement Windows ACL checking
2. **SELinux Integration**: Validate SELinux contexts
3. **AppArmor Profiles**: Check AppArmor profiles
4. **Container Detection**: Detect and validate container environments
5. **Capability Checking**: Verify Linux capabilities
6. **Seccomp Filters**: Validate seccomp-bpf filters
7. **Namespace Isolation**: Check namespace isolation
8. **Resource Limits**: Validate ulimits
9. **Network Policies**: Check network policy enforcement
10. **Audit Logging**: Integrate with system audit logs


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/security/environment_hardening.py]]
