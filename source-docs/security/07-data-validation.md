# Data Validation and Secure Parsing

## Overview

Secure data ingestion and parsing with comprehensive defenses against XXE, CSV injection, SQL injection, path traversal, and data poisoning attacks. Supports XML, CSV, and JSON with schema validation.

**Location:** `src/app/security/data_validation.py` (556 lines)

**Core Philosophy:** Validate everything, trust nothing, sanitize by default.

---

## Architecture

### Components

1. **SecureDataParser** - Multi-format parsing (XML, CSV, JSON)
2. **DataPoisoningDefense** - Attack pattern detection and sanitization
3. **Utility Functions** - `sanitize_input()`, `validate_email()`, `validate_length()`

### Data Structure

```python
@dataclass
class ParsedData:
    """Container for parsed data with metadata"""
    data: Any               # Parsed content
    data_type: str          # 'xml', 'csv', or 'json'
    hash: str               # SHA-256 hash of input
    validated: bool         # Passed schema validation
    issues: list[str]       # List of validation issues
```

---

## API Reference

### Secure XML Parsing

```python
from app.security.data_validation import SecureDataParser

parser = SecureDataParser()

# Parse XML with security controls
xml_data = """
<user>
    <username>alice</username>
    <email>alice@example.com</email>
    <role>admin</role>
</user>
"""

result = parser.parse_xml(xml_data)

if result.validated:
    print(f"Data: {result.data}")
    print(f"Hash: {result.hash}")
else:
    print(f"Issues: {result.issues}")

# With schema validation
schema = {
    "required": ["username", "email", "role"],
    "properties": {
        "username": {"type": "string"},
        "email": {"type": "string"},
        "role": {"type": "string"}
    }
}

result = parser.parse_xml(xml_data, schema=schema)
```

**Security Features:**
- Uses `defusedxml` to prevent XXE attacks
- Blocks DTD/Entity declarations
- Detects XXE attack patterns
- Schema validation

**Blocked Patterns:**
```xml
<!-- XXE Attack - BLOCKED -->
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user>&xxe;</user>

<!-- External Entity - BLOCKED -->
<!ENTITY remote SYSTEM "http://malicious.com/data">
```

### Secure CSV Parsing

```python
csv_data = """
username,email,role
alice,alice@example.com,admin
bob,bob@example.com,user
charlie,charlie@example.com,user
"""

# Parse with validation
schema = {
    "username": "string",
    "email": "string",
    "role": "string"
}

result = parser.parse_csv(csv_data, schema=schema)

if result.validated:
    for row in result.data:
        print(f"{row['username']}: {row['email']} ({row['role']})")
else:
    print(f"Issues: {result.issues}")

# Custom delimiter
tsv_data = "name\tage\tCity\nAlice\t30\tNY"
result = parser.parse_csv(tsv_data, delimiter="\t")
```

**Security Features:**
- Detects CSV injection (formula injection)
- Schema validation with type checking
- Blocks dangerous prefixes (`=`, `+`, `-`, `@`)

**Blocked Patterns:**
```csv
# CSV Injection - BLOCKED
=cmd|'/c calc'
+cmd|'/c calc'
-cmd|'/c calc'
@SUM(A1:A1000)
```

### Secure JSON Parsing

```python
json_data = """
{
    "username": "alice",
    "email": "alice@example.com",
    "role": "admin",
    "permissions": ["read", "write", "delete"]
}
"""

# Parse with schema
schema = {
    "required": ["username", "email", "role"],
    "properties": {
        "username": {"type": "string"},
        "email": {"type": "string"},
        "role": {"type": "string"},
        "permissions": {"type": "array"}
    }
}

result = parser.parse_json(json_data, schema=schema)

if result.validated:
    print(f"User: {result.data['username']}")
    print(f"Permissions: {result.data['permissions']}")
else:
    print(f"Issues: {result.issues}")
```

**Security Features:**
- Size limits (max 100MB)
- Schema validation
- Hash computation for integrity

---

## Data Poisoning Defense

### Attack Pattern Detection

```python
from app.security.data_validation import DataPoisoningDefense

defense = DataPoisoningDefense()

# Check for poison patterns
data = "<script>alert('XSS')</script>"
is_poisoned, detected = defense.check_for_poison(data)

if is_poisoned:
    print(f"ATTACK DETECTED: {detected}")
    # ['Poison pattern: <script.*?>.*?</script>']

# Add known poison signature
defense.add_poison_signature(data)

# Later checks will detect same content by hash
is_poisoned, detected = defense.check_for_poison(data)
# True, ['Known poison hash detected']
```

**Detected Attack Patterns:**
- **XSS:** `<script>`, `javascript:`, `onerror=`, `onclick=`
- **SQL Injection:** `'; DROP TABLE`, `UNION SELECT`
- **Path Traversal:** `../../`, `../..`
- **Log4Shell:** `${jndi:ldap://`, `${jndi:rmi://`
- **Template Injection:** `{{...}}`
- **CRLF Injection:** `%0d%0a`

### Input Sanitization

```python
# Sanitize dangerous input
dirty_input = "<script>alert('XSS')</script>Hello World<img onerror='alert(1)'>"
clean_input = defense.sanitize_input(dirty_input)

print(clean_input)
# Output: "Hello World"
# Script tags and event handlers removed
```

**Sanitization Rules:**
- Remove `<script>` tags
- Remove event handlers (`onclick=`, `onerror=`, etc.)
- Remove `javascript:` URLs
- SQL injection pattern removal

---

## Utility Functions

### Input Sanitization

```python
from app.security.data_validation import sanitize_input

# Sanitize user input
user_input = "<script>alert('XSS')</script>Hello'; DROP TABLE users;--"
safe_input = sanitize_input(user_input, max_length=100)

print(safe_input)
# Output: "Hello TABLE users"
# Script tags, SQL injection patterns, and XSS removed
```

**Removed Patterns:**
- Script tags and XSS
- Event handlers
- SQL injection patterns
- Path traversal sequences
- Null bytes

### Length Validation

```python
from app.security.data_validation import validate_length

# Validate string length
is_valid = validate_length("password123", min_len=8, max_len=100)  # True
is_valid = validate_length("abc", min_len=8, max_len=100)  # False (too short)
is_valid = validate_length("x" * 1000, min_len=8, max_len=100)  # False (too long)
```

### Email Validation

```python
from app.security.data_validation import validate_email

# Validate email format
is_valid = validate_email("alice@example.com")  # True
is_valid = validate_email("invalid.email")  # False
is_valid = validate_email("test@domain")  # False (no TLD)
```

---

## Integration Patterns

### Flask Application Integration

```python
from flask import Flask, request, jsonify
from app.security.data_validation import sanitize_input, validate_email, SecureDataParser

app = Flask(__name__)
parser = SecureDataParser()

@app.route('/register', methods=['POST'])
def register():
    # Get user input
    username = sanitize_input(request.form.get('username', ''), max_length=50)
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    # Validate email
    if not validate_email(email):
        return jsonify({"error": "Invalid email"}), 400
    
    # Validate password length
    if not validate_length(password, min_len=8, max_len=100):
        return jsonify({"error": "Password must be 8-100 characters"}), 400
    
    # Create user
    create_user(username, email, password)
    return jsonify({"success": True})

@app.route('/upload/csv', methods=['POST'])
def upload_csv():
    # Get CSV data
    csv_data = request.data.decode('utf-8')
    
    # Parse with validation
    result = parser.parse_csv(csv_data)
    
    if not result.validated:
        return jsonify({
            "error": "CSV validation failed",
            "issues": result.issues
        }), 400
    
    # Process validated data
    process_csv_data(result.data)
    return jsonify({"success": True, "rows": len(result.data)})
```

### File Upload Validation

```python
from app.security.data_validation import SecureDataParser, DataPoisoningDefense

parser = SecureDataParser()
defense = DataPoisoningDefense()

def process_uploaded_file(file_path, file_type):
    """Validate and parse uploaded file"""
    
    # Read file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for data poisoning
    is_poisoned, patterns = defense.check_for_poison(content)
    if is_poisoned:
        raise SecurityError(f"Data poisoning detected: {patterns}")
    
    # Parse based on type
    if file_type == 'xml':
        result = parser.parse_xml(content)
    elif file_type == 'csv':
        result = parser.parse_csv(content)
    elif file_type == 'json':
        result = parser.parse_json(content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # Check validation
    if not result.validated:
        raise ValidationError(f"Validation failed: {result.issues}")
    
    return result.data
```

### API Input Validation

```python
from app.security.data_validation import sanitize_input, validate_length

def validate_api_input(data):
    """Validate all API inputs"""
    
    validated = {}
    errors = []
    
    # Validate username
    if 'username' in data:
        username = sanitize_input(data['username'], max_length=50)
        if not validate_length(username, min_len=3, max_len=50):
            errors.append("Username must be 3-50 characters")
        else:
            validated['username'] = username
    
    # Validate email
    if 'email' in data:
        if not validate_email(data['email']):
            errors.append("Invalid email format")
        else:
            validated['email'] = data['email']
    
    # Validate description (longer field)
    if 'description' in data:
        description = sanitize_input(data['description'], max_length=1000)
        validated['description'] = description
    
    if errors:
        raise ValidationError(errors)
    
    return validated
```

---

## Security Patterns

### 1. Defense in Depth

```python
def secure_data_pipeline(raw_data, data_type):
    """Multi-layer validation pipeline"""
    
    # Layer 1: Data poisoning check
    is_poisoned, patterns = defense.check_for_poison(raw_data)
    if is_poisoned:
        raise SecurityError(f"Poison detected: {patterns}")
    
    # Layer 2: Parse with security controls
    if data_type == 'xml':
        result = parser.parse_xml(raw_data)
    elif data_type == 'csv':
        result = parser.parse_csv(raw_data)
    elif data_type == 'json':
        result = parser.parse_json(raw_data)
    
    # Layer 3: Schema validation
    if not result.validated:
        raise ValidationError(result.issues)
    
    # Layer 4: Business logic validation
    validate_business_rules(result.data)
    
    # Layer 5: Sanitize output
    sanitized = sanitize_output(result.data)
    
    return sanitized
```

### 2. Fail Closed

```python
def safe_parse(data, parser_func, default=None):
    """Parse with fail-closed error handling"""
    try:
        result = parser_func(data)
        
        if not result.validated:
            logger.warning(f"Validation failed: {result.issues}")
            return default
        
        return result.data
        
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return default  # Fail closed, not open

# Usage
data = safe_parse(xml_string, parser.parse_xml, default={})
```

### 3. Hash-Based Blacklisting

```python
# Maintain blacklist of known bad content
POISON_HASHES = set()

def check_and_blacklist(data):
    """Check hash, add to blacklist if poisoned"""
    data_hash = hashlib.sha256(data.encode()).hexdigest()
    
    # Check blacklist
    if data_hash in POISON_HASHES:
        raise SecurityError("Known malicious content")
    
    # Check for poison
    is_poisoned, patterns = defense.check_for_poison(data)
    
    if is_poisoned:
        # Add to blacklist
        POISON_HASHES.add(data_hash)
        defense.add_poison_signature(data)
        raise SecurityError(f"Poison detected: {patterns}")
    
    return data
```

---

## Performance Considerations

### Parsing Performance

- **XML:** ~10 MB/s (depends on complexity)
- **CSV:** ~50 MB/s (text splitting)
- **JSON:** ~30 MB/s (native JSON parsing)

### Optimization Tips

```python
# 1. Use streaming for large files
def parse_large_csv(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Validate row-by-row
            validate_row(row)
            yield row

# 2. Cache poison pattern compilation
poison_patterns = [re.compile(p) for p in POISON_PATTERNS]

# 3. Batch hash computation
def batch_check_hashes(data_list):
    hashes = [hashlib.sha256(d.encode()).hexdigest() for d in data_list]
    return [h in POISON_HASHES for h in hashes]
```

---

## Testing

### Unit Tests

```bash
pytest tests/test_data_validation.py -v
```

**Coverage:**
- XML parsing (valid, XXE, DTD)
- CSV parsing (valid, injection, schema)
- JSON parsing (valid, schema)
- Data poisoning detection
- Input sanitization
- Email validation
- Length validation

### Integration Tests

```python
def test_full_pipeline():
    """Test complete validation pipeline"""
    
    # Test data with multiple issues
    data = """<user>
        <username>alice'; DROP TABLE users;--</username>
        <email>invalid.email</email>
        <script>alert('xss')</script>
    </user>"""
    
    result = parser.parse_xml(data)
    
    # Should detect issues
    assert not result.validated
    assert len(result.issues) > 0
```

---

## Best Practices

1. **Always Sanitize:** Sanitize ALL user input before processing
2. **Use defusedxml:** Never use standard `xml.etree` for untrusted XML
3. **Schema Validation:** Define and enforce schemas for all data formats
4. **Hash Blacklists:** Maintain hash blacklists for known malicious content
5. **Log Attempts:** Log all validation failures for security monitoring
6. **Fail Closed:** Return safe defaults on validation failure
7. **Test Edge Cases:** Test with actual attack payloads during development
8. **Regular Updates:** Update poison patterns weekly from threat feeds

---


---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]

---
## Related Documentation

- [05-security-monitoring.md](05-security-monitoring.md) - Log validation failures
- [06-agent-security.md](06-agent-security.md) - Agent input validation
- [08-contrarian-firewall.md](08-contrarian-firewall.md) - System-level filtering

---

## See Also

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [XML External Entity (XXE) Prevention](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [CSV Injection Guide](https://owasp.org/www-community/attacks/CSV_Injection)
