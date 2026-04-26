# Validation & Sanitization Utilities

## Overview

Comprehensive validation and input sanitization utilities for ensuring data integrity, security, and consistency across Project-AI.

**Purpose**: Input validation, data sanitization, security checks  
**Dependencies**: re, typing, validators (optional)

---

## Core Validation

### 1. String Validation

#### validate_not_empty()
```python
def validate_not_empty(
    value: str,
    field_name: str = "Value"
) -> tuple[bool, str]:
    """
    Validate string is not empty.
    
    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty"
    return True, ""
```

---

#### validate_length()
```python
def validate_length(
    value: str,
    min_length: int | None = None,
    max_length: int | None = None,
    field_name: str = "Value"
) -> tuple[bool, str]:
    """
    Validate string length constraints.
    
    Args:
        value: String to validate
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)
        field_name: Field name for error messages
    
    Returns:
        (is_valid, error_message)
    """
    length = len(value)
    
    if min_length is not None and length < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    
    if max_length is not None and length > max_length:
        return False, f"{field_name} must be at most {max_length} characters"
    
    return True, ""

# Usage
is_valid, error = validate_length("password", min_length=8, max_length=128)
```

---

#### validate_pattern()
```python
import re

def validate_pattern(
    value: str,
    pattern: str,
    field_name: str = "Value",
    error_message: str | None = None
) -> tuple[bool, str]:
    """
    Validate string matches regex pattern.
    
    Args:
        value: String to validate
        pattern: Regex pattern
        field_name: Field name
        error_message: Custom error message
    
    Returns:
        (is_valid, error_message)
    """
    if not re.match(pattern, value):
        if error_message is None:
            error_message = f"{field_name} format is invalid"
        return False, error_message
    
    return True, ""

# Usage
is_valid, error = validate_pattern(
    "user_123",
    pattern=r'^[a-z_][a-z0-9_]*$',
    field_name="Username",
    error_message="Username must start with letter or underscore"
)
```

---

### 2. Email & URL Validation

#### validate_email()
```python
def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email address format.
    
    Returns:
        (is_valid, error_message)
    """
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email:
        return False, "Email cannot be empty"
    
    if len(email) > 254:  # RFC 5321
        return False, "Email address too long"
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Check for consecutive dots
    if ".." in email:
        return False, "Email cannot contain consecutive dots"
    
    return True, ""

# Usage
is_valid, error = validate_email("user@example.com")
if not is_valid:
    print(f"Invalid email: {error}")
```

---

#### validate_url()
```python
def validate_url(url: str, require_https: bool = False) -> tuple[bool, str]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        require_https: Require HTTPS protocol
    
    Returns:
        (is_valid, error_message)
    """
    url_pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
    
    if not url:
        return False, "URL cannot be empty"
    
    if not re.match(url_pattern, url):
        return False, "Invalid URL format"
    
    if require_https and not url.startswith("https://"):
        return False, "HTTPS required"
    
    return True, ""
```

---

### 3. Numeric Validation

#### validate_integer()
```python
def validate_integer(
    value: Any,
    min_value: int | None = None,
    max_value: int | None = None,
    field_name: str = "Value"
) -> tuple[bool, str]:
    """
    Validate integer with range check.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be an integer"
    
    if min_value is not None and int_value < min_value:
        return False, f"{field_name} must be at least {min_value}"
    
    if max_value is not None and int_value > max_value:
        return False, f"{field_name} must be at most {max_value}"
    
    return True, ""

# Usage
is_valid, error = validate_integer("25", min_value=18, max_value=100, field_name="Age")
```

---

#### validate_float()
```python
def validate_float(
    value: Any,
    min_value: float | None = None,
    max_value: float | None = None,
    field_name: str = "Value"
) -> tuple[bool, str]:
    """
    Validate float with range check.
    """
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    
    if min_value is not None and float_value < min_value:
        return False, f"{field_name} must be at least {min_value}"
    
    if max_value is not None and float_value > max_value:
        return False, f"{field_name} must be at most {max_value}"
    
    return True, ""
```

---

### 4. Collection Validation

#### validate_list()
```python
def validate_list(
    value: Any,
    min_items: int | None = None,
    max_items: int | None = None,
    item_validator: Callable | None = None,
    field_name: str = "List"
) -> tuple[bool, str]:
    """
    Validate list with size and item constraints.
    
    Args:
        value: List to validate
        min_items: Minimum number of items
        max_items: Maximum number of items
        item_validator: Function to validate each item
        field_name: Field name
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(value, list):
        return False, f"{field_name} must be a list"
    
    if min_items is not None and len(value) < min_items:
        return False, f"{field_name} must have at least {min_items} items"
    
    if max_items is not None and len(value) > max_items:
        return False, f"{field_name} must have at most {max_items} items"
    
    if item_validator:
        for i, item in enumerate(value):
            is_valid, error = item_validator(item)
            if not is_valid:
                return False, f"{field_name}[{i}]: {error}"
    
    return True, ""

# Usage
is_valid, error = validate_list(
    ["alice", "bob"],
    min_items=1,
    max_items=10,
    item_validator=lambda x: validate_pattern(x, r'^[a-z]+$')[0],
    field_name="Usernames"
)
```

---

### 5. Security Validation

#### validate_password_strength()
```python
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain special character"
    
    return True, ""

# Usage
is_valid, error = validate_password_strength("MyP@ssw0rd")
```

---

#### validate_safe_filename()
```python
def validate_safe_filename(filename: str) -> tuple[bool, str]:
    """
    Validate filename is safe (no directory traversal).
    
    Returns:
        (is_valid, error_message)
    """
    # Forbidden characters
    forbidden_chars = ['/', '\\', '..', '\0']
    
    for char in forbidden_chars:
        if char in filename:
            return False, f"Filename contains forbidden character: {char}"
    
    # Forbidden names (Windows)
    forbidden_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']
    if filename.upper() in forbidden_names:
        return False, f"Filename is reserved: {filename}"
    
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"
    
    return True, ""
```

---

## Sanitization

### 1. String Sanitization

#### sanitize_html()
```python
def sanitize_html(html: str) -> str:
    """
    Remove HTML tags from string.
    
    Returns:
        Plain text (HTML tags removed)
    """
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

# Usage
dirty = "<script>alert('XSS')</script><p>Hello</p>"
clean = sanitize_html(dirty)  # "alert('XSS')Hello"
```

---

#### sanitize_sql()
```python
def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifier (table/column name).
    
    Returns:
        Sanitized identifier
    
    Raises:
        ValueError: If identifier contains dangerous characters
    """
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")
    
    return identifier

# Usage
table_name = sanitize_sql_identifier("users")  # OK
# sanitize_sql_identifier("users; DROP TABLE")  # Raises ValueError
```

---

### 2. Path Sanitization

#### sanitize_path()
```python
from pathlib import Path

def sanitize_path(path: str, base_dir: Path) -> Path:
    """
    Sanitize file path to prevent directory traversal.
    
    Args:
        path: User-provided path
        base_dir: Base directory to restrict to
    
    Returns:
        Safe path within base_dir
    
    Raises:
        ValueError: If path escapes base_dir
    """
    # Resolve to absolute path
    base_dir = base_dir.resolve()
    safe_path = (base_dir / path).resolve()
    
    # Check if within base directory
    try:
        safe_path.relative_to(base_dir)
    except ValueError:
        raise ValueError(f"Path escapes base directory: {path}")
    
    return safe_path

# Usage
base = Path("/data/uploads")
user_path = "../../etc/passwd"  # Malicious

try:
    safe = sanitize_path(user_path, base)
except ValueError as e:
    print(f"Blocked: {e}")
```

---

## Validation Chains

### ValidatorChain Class

```python
class ValidationError(Exception):
    """Validation error exception."""
    pass

class ValidatorChain:
    """Chain multiple validators together."""
    
    def __init__(self):
        self.validators = []
    
    def add(
        self,
        validator: Callable[[Any], tuple[bool, str]],
        required: bool = True
    ):
        """Add validator to chain."""
        self.validators.append((validator, required))
        return self
    
    def validate(self, value: Any) -> tuple[bool, list[str]]:
        """
        Run all validators.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        for validator, required in self.validators:
            is_valid, error = validator(value)
            
            if not is_valid:
                errors.append(error)
                if required:
                    # Stop on first required validation failure
                    return False, errors
        
        return len(errors) == 0, errors
    
    def validate_or_raise(self, value: Any) -> None:
        """
        Validate and raise exception on error.
        
        Raises:
            ValidationError: If validation fails
        """
        is_valid, errors = self.validate(value)
        
        if not is_valid:
            raise ValidationError("; ".join(errors))

# Usage
username_validator = ValidatorChain()
username_validator.add(lambda x: validate_not_empty(x, "Username"))
username_validator.add(lambda x: validate_length(x, 3, 50, "Username"))
username_validator.add(lambda x: validate_pattern(x, r'^[a-zA-Z0-9_]+$', "Username"))

try:
    username_validator.validate_or_raise("user_123")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Form Validation

### FormValidator Class

```python
class FormValidator:
    """Validate form data."""
    
    def __init__(self):
        self.field_validators = {}
        self.errors = {}
    
    def field(
        self,
        field_name: str,
        *validators: Callable[[Any], tuple[bool, str]]
    ):
        """Register validators for field."""
        self.field_validators[field_name] = validators
        return self
    
    def validate(self, data: dict) -> bool:
        """
        Validate form data.
        
        Args:
            data: Form data dictionary
        
        Returns:
            True if valid, False otherwise
        """
        self.errors = {}
        
        for field_name, validators in self.field_validators.items():
            value = data.get(field_name)
            
            for validator in validators:
                is_valid, error = validator(value)
                if not is_valid:
                    self.errors[field_name] = error
                    break  # Stop at first error for this field
        
        return len(self.errors) == 0
    
    def get_errors(self) -> dict[str, str]:
        """Get validation errors."""
        return self.errors

# Usage
validator = FormValidator()

validator.field(
    "username",
    lambda x: validate_not_empty(x, "Username"),
    lambda x: validate_length(x, 3, 50, "Username")
)

validator.field(
    "email",
    lambda x: validate_not_empty(x, "Email"),
    validate_email
)

validator.field(
    "age",
    lambda x: validate_integer(x, 18, 120, "Age")
)

form_data = {
    "username": "ab",  # Too short
    "email": "invalid-email",
    "age": 25
}

if not validator.validate(form_data):
    print("Validation errors:", validator.get_errors())
    # {"username": "Username must be at least 3 characters", "email": "Invalid email format"}
```

---

## Testing

```python
import unittest

class TestValidation(unittest.TestCase):
    def test_validate_email(self):
        # Valid emails
        self.assertTrue(validate_email("user@example.com")[0])
        self.assertTrue(validate_email("user.name@example.co.uk")[0])
        
        # Invalid emails
        self.assertFalse(validate_email("invalid")[0])
        self.assertFalse(validate_email("@example.com")[0])
        self.assertFalse(validate_email("user..name@example.com")[0])
    
    def test_validate_password_strength(self):
        # Valid password
        self.assertTrue(validate_password_strength("MyP@ssw0rd")[0])
        
        # Too short
        self.assertFalse(validate_password_strength("Pass1!")[0])
        
        # Missing special char
        self.assertFalse(validate_password_strength("Password123")[0])
```

---

## Best Practices

### DO ✅

- Validate all user input
- Sanitize before displaying
- Use whitelisting over blacklisting
- Provide clear error messages
- Chain validators for complex validation
- Test edge cases

### DON'T ❌

- Trust client-side validation alone
- Use regex for complex parsing (HTML, URLs)
- Ignore encoding issues
- Reveal sensitive info in errors
- Skip sanitization for "trusted" input
- Use blacklists for security

---

## Related Documentation

- **String Utilities**: `source-docs/utilities/011-string-text-utils.md`
- **Path Utilities**: `source-docs/utilities/012-path-file-utils.md`
- **Dashboard Utils**: `source-docs/utilities/001-dashboard-utils.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Security & Utilities Team
