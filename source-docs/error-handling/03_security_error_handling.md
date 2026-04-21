# Security Error Handling Documentation

**Component**: Security Layer Exception Management  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Security errors in Project-AI follow a zero-tolerance model: security violations NEVER auto-retry, ALWAYS log to immutable audit, and ALWAYS escalate to human oversight. This document covers the enforcement gateway, path traversal protection, and constitutional violation handling.

---

## Security Enforcement Gateway

### SecurityViolationException

**Module**: `src/app/security/asymmetric_enforcement_gateway.py`  
**Lines**: 204-227  
**Purpose**: Hard-stop exception for security policy violations

```python
class SecurityViolationException(Exception):
    """
    Exception raised when operation is blocked by security gateway.
    
    This exception MUST be caught and handled at the application layer.
    It prevents the operation from executing.
    """
    
    def __init__(
        self,
        operation_id: str,
        reason: str,
        threat_level: str,
        enforcement_actions: list[str],
    ):
        self.operation_id = operation_id
        self.reason = reason
        self.threat_level = threat_level
        self.enforcement_actions = enforcement_actions
        
        super().__init__(
            f"SECURITY VIOLATION: {operation_id} - {reason} "
            f"(threat={threat_level})"
        )
```

**Attributes**:
- `operation_id`: Unique SHA-256 identifier for the blocked operation
- `reason`: Detailed explanation of security policy violation
- `threat_level`: `low`, `medium`, `high`, or `critical`
- `enforcement_actions`: List of enforcement measures taken (e.g., `["blocked", "logged", "alerted"]`)

---

### Enforcement Flow

```
User Action
    ↓
SecurityEnforcementGateway.enforce(request)
    ↓
GodTierAsymmetricSecurity.validate_action_comprehensive()
    ↓
[PASS] → Create audit trail → Allow execution
[FAIL] → Record incident → Raise SecurityViolationException
```

**Code Flow**:
```python
def enforce(self, request: OperationRequest) -> OperationResult:
    """ENFORCE security on an operation request."""
    self.operations_processed += 1
    
    # Comprehensive validation through all security layers
    validation_result = self.god_tier.validate_action_comprehensive(
        action=request.action,
        context=request.context,
        user_id=request.user_id
    )
    
    result = OperationResult(
        operation_id=request.operation_id,
        allowed=validation_result["allowed"],
        reason=validation_result.get("failure_reason", "All checks passed"),
        threat_level=validation_result["threat_level"],
        layers_checked=validation_result.get("layers_passed", []),
        enforcement_actions=validation_result.get("actions_taken", []),
    )
    
    if not result.allowed:
        self.operations_blocked += 1
        logger.critical(
            f"OPERATION BLOCKED: {request.operation_id} - {result.reason} "
            f"(threat={result.threat_level})"
        )
        
        # Record security incident
        self._record_security_incident(request, result)
        
        # HARD BLOCK - Raise exception to prevent execution
        raise SecurityViolationException(
            operation_id=request.operation_id,
            reason=result.reason,
            threat_level=result.threat_level,
            enforcement_actions=result.enforcement_actions,
        )
    
    # Operation allowed - create audit trail
    if request.requires_audit:
        result.audit_trail_id = self._create_audit_trail(request, result)
    
    return result
```

---

### Handling SecurityViolationException

#### Pattern 1: Command Dispatcher

```python
from app.security.asymmetric_enforcement_gateway import (
    SecurityEnforcementGateway,
    SecurityViolationException,
    OperationRequest,
    OperationType,
)

class SecureCommandDispatcher:
    """Command dispatcher with security enforcement."""
    
    def __init__(self):
        self.gateway = SecurityEnforcementGateway()
        self.command_handlers = {}
    
    def dispatch(self, command: str, user_id: str, context: dict):
        """Dispatch command with security enforcement."""
        request = OperationRequest(
            operation_id=self.generate_operation_id(),
            operation_type=OperationType.AGENT_ACTION,
            action=command,
            context=context,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
        )
        
        try:
            # Enforce security before executing command
            result = self.gateway.enforce(request)
            
            # Security passed - execute command
            handler = self.command_handlers.get(command)
            if handler:
                return handler(context)
            else:
                return {"error": "Unknown command"}
        
        except SecurityViolationException as e:
            # Security violation - log and return error to user
            logger.critical(
                "Command blocked by security: %s (threat=%s)",
                e.reason, e.threat_level
            )
            
            return {
                "error": "Security Violation",
                "reason": self._sanitize_error_for_user(e.reason),
                "operation_id": e.operation_id,
                "threat_level": e.threat_level,
            }
```

**Key Points**:
- NEVER re-raise `SecurityViolationException` to end user (information leak)
- ALWAYS sanitize error messages before displaying to user
- ALWAYS log full exception details for security team
- NEVER retry operation that raised `SecurityViolationException`

---

#### Pattern 2: API Endpoint

```python
from flask import Flask, jsonify, request
from app.security.asymmetric_enforcement_gateway import SecurityViolationException

app = Flask(__name__)

@app.route('/api/action', methods=['POST'])
def execute_action():
    """API endpoint with security enforcement."""
    action = request.json.get('action')
    user_id = request.headers.get('X-User-ID')
    
    try:
        # Create and enforce security request
        op_request = create_operation_request(action, user_id)
        result = security_gateway.enforce(op_request)
        
        # Execute action
        action_result = execute_user_action(action)
        
        return jsonify({
            "success": True,
            "result": action_result,
            "audit_trail_id": result.audit_trail_id,
        }), 200
    
    except SecurityViolationException as e:
        # Return sanitized error to client
        return jsonify({
            "success": False,
            "error": "Security policy violation",
            "operation_id": e.operation_id,
            "threat_level": e.threat_level,
            # DO NOT expose e.reason (may contain internal system details)
        }), 403
    
    except Exception as e:
        # Generic error handling
        logger.error("Action execution failed: %s", e, exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
```

---

### Security Incident Recording

**Method**: `_record_security_incident()`

```python
def _record_security_incident(
    self, request: OperationRequest, result: OperationResult
) -> None:
    """Record security incident for blocked operation."""
    incident = {
        "incident_type": "security_violation",
        "operation_id": request.operation_id,
        "operation_type": request.operation_type.value,
        "action": request.action,
        "user_id": request.user_id,
        "blocked_at": datetime.now().isoformat(),
        "reason": result.reason,
        "threat_level": result.threat_level,
        "enforcement_actions": result.enforcement_actions,
        "context": request.context,
    }
    
    # Wire into Hydra-50 incident response system
    logger.critical("SECURITY INCIDENT: %s", incident)
    
    # Future: Send to SIEM, alert SOC, trigger automated response
```

**Integration Points**:
- Hydra-50 incident response system
- Security Operations Center (SOC) alerting
- SIEM (Security Information and Event Management)
- Automated threat response workflows

---

## Path Traversal Protection

### PathTraversalError

**Module**: `src/app/security/path_security.py`  
**Lines**: 32-34  
**Purpose**: Raised when directory traversal attack is detected

```python
class PathTraversalError(ValueError):
    """Raised when path traversal attack is detected."""
    pass
```

**Parent**: `ValueError` (standard Python exception)

---

### Detection Mechanisms

#### 1. Parent Directory Escape Detection

```python
def safe_path_join(base_dir: str, *user_paths: str) -> str:
    """Securely join paths and validate they stay within base directory."""
    # Normalize base directory
    base_abs = os.path.abspath(base_dir)
    
    # Join and normalize the full path
    full_path = os.path.normpath(os.path.join(base_abs, *user_paths))
    full_abs = os.path.abspath(full_path)
    
    # Ensure result is still under base directory
    try:
        common = os.path.commonpath([base_abs, full_abs])
        if common != base_abs:
            logger.warning(
                "Path traversal blocked: %s escapes base %s",
                user_paths, base_dir
            )
            raise PathTraversalError(
                f"Path traversal detected: {user_paths} escapes {base_dir}"
            )
    except ValueError:
        # Different drives on Windows
        raise PathTraversalError("Path traversal detected: different drive")
```

**Detection Triggers**:
- Final path is outside base directory
- Different drive letters (Windows)
- Symlink attacks (resolved by `os.path.abspath`)

---

#### 2. Explicit '..' Sequence Detection

```python
# Additional check: block any .. sequences in user input
for user_path in user_paths:
    if ".." in str(user_path):
        logger.warning(
            "Path traversal blocked: '..' sequence in %s",
            user_path
        )
        raise PathTraversalError(
            "Invalid path: '..' sequences not allowed"
        )
```

**Blocked Patterns**:
- `../etc/passwd`
- `..\\Windows\\System32`
- `foo/../../../bar`
- `...` (contains `..`)

---

#### 3. Absolute Path Rejection

```python
# Block absolute paths in user input (Unix and Windows)
for user_path in user_paths:
    user_str = str(user_path)
    if os.path.isabs(user_str):
        logger.warning(
            "Path traversal blocked: absolute path %s",
            user_path
        )
        raise PathTraversalError(
            "Invalid path: absolute paths not allowed in user input"
        )
```

**Blocked Patterns**:
- `/etc/passwd` (Unix)
- `C:\Windows\System32` (Windows)
- `\\network\share` (UNC paths)

---

### Safe File Operations

#### safe_open() Function

```python
def safe_open(
    base_dir: str,
    filename: str,
    mode: str = 'r',
    **kwargs
):
    """Safely open a file within base directory.
    
    Args:
        base_dir: Trusted base directory
        filename: User-provided filename
        mode: File mode ('r', 'w', 'a', etc.)
        **kwargs: Additional arguments passed to open()
    
    Returns:
        File handle
    
    Raises:
        PathTraversalError: If path validation fails
    """
    safe_path = safe_path_join(base_dir, filename)
    return open(safe_path, mode, **kwargs)
```

**Usage Example**:
```python
from app.security.path_security import safe_open

def load_user_profile(username: str):
    """Load user profile with path traversal protection."""
    try:
        with safe_open("data/profiles", f"{username}.json", 'r') as f:
            return json.load(f)
    except PathTraversalError as e:
        logger.warning("Path traversal attempt: %s", e)
        raise ValueError("Invalid username")
    except FileNotFoundError:
        return None
```

---

### Path Validation Testing

```python
import pytest
from app.security.path_security import PathTraversalError, safe_path_join

class TestPathTraversalProtection:
    """Test path traversal protection."""
    
    def test_basic_join(self):
        """Test normal path joining works."""
        result = safe_path_join("/data", "user", "profile.json")
        assert result == os.path.abspath("/data/user/profile.json")
    
    def test_parent_directory_blocked(self):
        """Test that parent directory traversal is blocked."""
        with pytest.raises(PathTraversalError) as exc_info:
            safe_path_join("/data", "../etc/passwd")
        
        assert "Path traversal detected" in str(exc_info.value)
    
    def test_absolute_path_blocked(self):
        """Test that absolute paths in user input are blocked."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "/etc/passwd")
    
    def test_double_dot_blocked(self):
        """Test that double-dot sequences are blocked."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "foo/../../../etc/passwd")
    
    def test_windows_path_blocked(self, monkeypatch):
        """Test that Windows absolute paths are blocked."""
        with pytest.raises(PathTraversalError):
            safe_path_join("C:\\data", "C:\\Windows\\System32")
```

---

## Constitutional Violations

### ConstitutionalViolationError

**Module**: `src/app/core/planetary_defense_monolith.py`  
**Lines**: 28-44  
**Purpose**: Base exception for Four Laws violations

```python
class ConstitutionalViolationError(Exception):
    """Base exception for constitutional violations."""
    pass

class MoralCertaintyError(ConstitutionalViolationError):
    """Raised when moral certainty claims are detected."""
    pass

class LawViolationError(ConstitutionalViolationError):
    """Raised when one or more laws are violated."""
    pass
```

---

### Violation Detection

#### Moral Certainty Detection

```python
def assert_no_moral_certainty(self) -> None:
    """
    Enforce the Accountability Axiom: no moral certainty claims.
    
    Raises:
        MoralCertaintyError: If forbidden phrases are detected
    """
    forbidden_phrases = [
        "optimal",
        "necessary evil",
        "justified harm",
        "acceptable losses",
        "greater good requires",
        "ends justify",
        "must sacrifice",
        "for the greater good",
        "morally required",
        "ethically necessary",
    ]
    
    intent_lower = self.intent.lower()
    for phrase in forbidden_phrases:
        if phrase in intent_lower:
            logger.critical(
                "Moral certainty claim detected: '%s' in intent",
                phrase
            )
            raise MoralCertaintyError(
                f"Forbidden moral certainty claim: '{phrase}' detected in intent"
            )
```

**Key Principles**:
- No action can be labeled "morally optimal"
- No harm can be claimed as "necessary"
- All actions require human accountability
- AI cannot make moral judgments

---

#### Four Laws Validation

```python
def validate_action(action: str, context: dict) -> tuple[bool, list[LawEvaluation]]:
    """
    Validate an action against the Four Laws.
    
    Returns:
        (is_allowed, law_evaluations)
    """
    evaluations = [
        validate_zeroth_law(action, context),  # Preserve humanity
        validate_first_law(action, context),   # Do not harm
        validate_second_law(action, context),  # Obey humans
        validate_third_law(action, context),   # Preserve self
    ]
    
    violations = [e for e in evaluations if not e.satisfied]
    
    if violations:
        logger.critical(
            "Four Laws violation: %s violates %d laws",
            action, len(violations)
        )
        raise LawViolationError(
            action=action,
            violations=violations,
            context=context,
        )
    
    return True, evaluations
```

---

### Handling Constitutional Violations

#### Pattern: Immutable Accountability Record

```python
@dataclass
class AccountabilityRecord:
    """Immutable accountability record for all actions."""
    action_id: str
    timestamp: datetime
    actor: str
    intent: str
    authorized_by: str
    predicted_harm: str
    actual_outcome: str | None = None
    violated_laws: list[Law] = field(default_factory=list)
    moral_claims: list[str] = field(default_factory=list)

def record_constitutional_violation(
    action: str,
    violation: ConstitutionalViolationError,
    context: dict,
) -> None:
    """Record constitutional violation to immutable ledger."""
    record = AccountabilityRecord(
        action_id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        actor=context.get("user_id", "unknown"),
        intent=action,
        authorized_by=context.get("authorized_by", "none"),
        predicted_harm=str(violation),
        violated_laws=getattr(violation, "violations", []),
        moral_claims=getattr(violation, "moral_claims", []),
    )
    
    # Write to immutable audit log (append-only, tamper-proof)
    append_to_immutable_ledger(record)
    
    # Alert human oversight
    alert_constitutional_oversight_board(record)
    
    logger.critical("Constitutional violation recorded: %s", record.action_id)
```

**Key Requirements**:
- Records are append-only (never modified or deleted)
- All violations escalate to human oversight
- No automatic remediation
- Full audit trail with context

---

### Recovery: Constitutional Violations NEVER Auto-Retry

```python
def execute_action_with_constitutional_check(action: str, context: dict):
    """Execute action with constitutional validation."""
    try:
        # Validate against Four Laws
        is_allowed, evaluations = validate_action(action, context)
        
        # Check for moral certainty claims
        record = create_accountability_record(action, context)
        record.assert_no_moral_certainty()
        
        # Execute action
        result = perform_action(action, context)
        
        # Record successful execution
        record.actual_outcome = "success"
        append_to_immutable_ledger(record)
        
        return result
    
    except ConstitutionalViolationError as e:
        # Record violation
        record_constitutional_violation(action, e, context)
        
        # NEVER retry - constitutional violations require human intervention
        logger.critical(
            "Action blocked by constitutional violation: %s",
            str(e)
        )
        
        # Return error to user (do NOT expose internal details)
        raise PermissionError(
            "Action blocked by system ethics protocols. "
            "Incident has been recorded for review."
        )
```

---

## Error Message Sanitization

### Principle: Never Leak Internal Details

```python
def sanitize_error_for_user(internal_error: str) -> str:
    """Sanitize internal error message for user display."""
    # Map internal error patterns to user-friendly messages
    sanitization_map = {
        "path traversal": "Invalid file path",
        "security layer": "Security policy violation",
        "constitutional": "Action blocked by ethics protocols",
        "SQL injection": "Invalid input detected",
        "XSS": "Invalid input detected",
        "database": "Data storage error",
        "filesystem": "File operation failed",
    }
    
    error_lower = internal_error.lower()
    for pattern, user_message in sanitization_map.items():
        if pattern in error_lower:
            return user_message
    
    # Default sanitized message
    return "Operation failed due to system policy"
```

---

## Security Metrics and Alerting

### Metrics to Track

```python
@dataclass
class SecurityMetrics:
    """Security error metrics."""
    total_violations: int = 0
    violations_by_type: dict[str, int] = field(default_factory=dict)
    violations_by_user: dict[str, int] = field(default_factory=dict)
    path_traversal_attempts: int = 0
    constitutional_violations: int = 0
    blocked_operations_per_hour: float = 0.0
    
    def record_violation(self, violation_type: str, user_id: str):
        """Record a security violation."""
        self.total_violations += 1
        self.violations_by_type[violation_type] = \
            self.violations_by_type.get(violation_type, 0) + 1
        self.violations_by_user[user_id] = \
            self.violations_by_user.get(user_id, 0) + 1
```

### Alert Thresholds

```python
ALERT_THRESHOLDS = {
    "critical": {
        "constitutional_violations": 1,  # Any occurrence
        "path_traversal_per_user": 5,    # 5 attempts from one user
        "violations_per_hour": 50,       # 50 violations/hour
    },
    "high": {
        "path_traversal_per_user": 3,
        "violations_per_hour": 20,
    },
    "medium": {
        "violations_per_hour": 10,
    },
}
```

---

## References

- **Security Enforcement**: `src/app/security/asymmetric_enforcement_gateway.py`
- **Path Security**: `src/app/security/path_security.py`
- **Constitutional Framework**: `src/app/core/planetary_defense_monolith.py`
- **Four Laws**: `PROGRAM_SUMMARY.md` - AI Systems section
- **Testing**: `tests/test_path_traversal_fix.py`

---

**Next Steps**:
1. Implement SIEM integration for security incident forwarding
2. Add automated threat response workflows
3. Create security dashboard for real-time monitoring
4. Document incident response playbook
