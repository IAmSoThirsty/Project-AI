# String & Text Utilities

## Overview

Common string manipulation, text processing, and formatting utilities used throughout Project-AI for consistent text handling across modules.

**Purpose**: Centralized string operations, sanitization, formatting  
**Dependencies**: Python stdlib (re, string, unicodedata)

---

## Core Utilities

### 1. String Sanitization

#### sanitize_string()
```python
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing control characters.
    
    Args:
        value: Input string
        max_length: Maximum length (default: 1000)
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove control characters (except newline)
    cleaned = "".join(char for char in value if ord(char) >= 32 or char == "\n")
    
    # Limit length
    return cleaned[:max_length]
```

**Usage**:
```python
# Remove control characters from user input
user_input = "Hello\x00World\x1F!"
clean = sanitize_string(user_input)  # "HelloWorld!"

# Limit length
long_text = "a" * 2000
clean = sanitize_string(long_text, max_length=500)  # 500 chars
```

---

#### strip_html()
```python
import re

def strip_html(html: str) -> str:
    """Remove HTML tags from string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)
```

**Usage**:
```python
html = "<p>Hello <strong>World</strong>!</p>"
text = strip_html(html)  # "Hello World!"
```

---

### 2. String Validation

#### is_valid_username()
```python
import re

def is_valid_username(username: str) -> bool:
    """
    Validate username format.
    
    Rules:
    - 3-50 characters
    - Alphanumeric, underscore, hyphen only
    - Must start with letter
    """
    if not username or len(username) < 3 or len(username) > 50:
        return False
    
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
    return bool(re.match(pattern, username))
```

---

#### is_valid_email()
```python
import re

def is_valid_email(email: str) -> bool:
    """Validate email format (basic check)."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

---

### 3. Text Formatting

#### truncate_string()
```python
def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix.
    
    Args:
        text: Input text
        max_length: Maximum length (including suffix)
        suffix: Suffix to append (default: "...")
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
```

**Usage**:
```python
text = "This is a very long string that needs truncation"
short = truncate_string(text, 30)  # "This is a very long stri..."
```

---

#### format_file_size()
```python
def format_file_size(size_bytes: int) -> str:
    """
    Format bytes as human-readable file size.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"
```

**Usage**:
```python
print(format_file_size(1024))        # "1.0 KB"
print(format_file_size(1536))        # "1.5 KB"
print(format_file_size(1048576))     # "1.0 MB"
print(format_file_size(1073741824))  # "1.0 GB"
```

---

#### format_duration()
```python
def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2h 30m 45s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    return f"{hours}h {minutes}m {seconds}s"
```

---

### 4. Case Conversion

#### to_snake_case()
```python
import re

def to_snake_case(text: str) -> str:
    """Convert string to snake_case."""
    # Insert underscore before uppercase letters
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
    return text.lower()
```

**Usage**:
```python
print(to_snake_case("CamelCase"))        # "camel_case"
print(to_snake_case("HTTPResponse"))     # "http_response"
print(to_snake_case("userID"))           # "user_id"
```

---

#### to_camel_case()
```python
def to_camel_case(text: str) -> str:
    """Convert string to camelCase."""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
```

**Usage**:
```python
print(to_camel_case("snake_case"))       # "snakeCase"
print(to_camel_case("http_response"))    # "httpResponse"
```

---

### 5. Text Extraction

#### extract_urls()
```python
import re

def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)
```

**Usage**:
```python
text = "Visit https://example.com and http://test.org for more info"
urls = extract_urls(text)
# ['https://example.com', 'http://test.org']
```

---

#### extract_emails()
```python
import re

def extract_emails(text: str) -> list[str]:
    """Extract all email addresses from text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)
```

---

### 6. Text Normalization

#### normalize_whitespace()
```python
def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()
```

**Usage**:
```python
text = "Hello    World\n\n  Test  "
clean = normalize_whitespace(text)  # "Hello World Test"
```

---

#### remove_accents()
```python
import unicodedata

def remove_accents(text: str) -> str:
    """Remove accents from text."""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
```

**Usage**:
```python
text = "café résumé naïve"
clean = remove_accents(text)  # "cafe resume naive"
```

---

### 7. String Comparison

#### fuzzy_match()
```python
def fuzzy_match(str1: str, str2: str, threshold: float = 0.8) -> bool:
    """
    Check if strings match with fuzzy matching.
    
    Uses Levenshtein distance.
    """
    from difflib import SequenceMatcher
    
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold
```

**Usage**:
```python
fuzzy_match("hello", "helo")      # True (typo tolerance)
fuzzy_match("test", "testing")    # False (too different)
```

---

### 8. Template Rendering

#### simple_template()
```python
def simple_template(template: str, **kwargs) -> str:
    """
    Simple template rendering with {{variable}} syntax.
    
    Args:
        template: Template string with {{var}} placeholders
        **kwargs: Variables to substitute
    
    Returns:
        Rendered string
    """
    result = template
    for key, value in kwargs.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result
```

**Usage**:
```python
template = "Hello {{name}}, you have {{count}} messages."
output = simple_template(
    template,
    name="Alice",
    count=5
)
# "Hello Alice, you have 5 messages."
```

---

## Advanced Patterns

### 1. Text Pipeline

```python
class TextPipeline:
    """Pipeline for text processing."""
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, func: Callable[[str], str]):
        """Add processing step."""
        self.steps.append(func)
        return self
    
    def process(self, text: str) -> str:
        """Process text through pipeline."""
        result = text
        for step in self.steps:
            result = step(result)
        return result

# Usage
pipeline = TextPipeline()
pipeline.add_step(strip_html)
pipeline.add_step(normalize_whitespace)
pipeline.add_step(lambda t: truncate_string(t, 100))

clean_text = pipeline.process(dirty_html)
```

---

### 2. String Builder

```python
class StringBuilder:
    """Efficient string building."""
    
    def __init__(self):
        self._parts = []
    
    def append(self, text: str):
        """Append text."""
        self._parts.append(text)
        return self
    
    def appendline(self, text: str = ""):
        """Append text with newline."""
        self._parts.append(text)
        self._parts.append("\n")
        return self
    
    def build(self) -> str:
        """Build final string."""
        return "".join(self._parts)

# Usage
builder = StringBuilder()
builder.appendline("# Header")
builder.appendline()
builder.append("Content line 1\n")
builder.append("Content line 2\n")

result = builder.build()
```

---

### 3. Text Chunker

```python
def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int = 0
) -> list[str]:
    """
    Split text into chunks with optional overlap.
    
    Args:
        text: Input text
        chunk_size: Size of each chunk
        overlap: Number of overlapping characters
    
    Returns:
        List of text chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks

# Usage
text = "A" * 1000
chunks = chunk_text(text, chunk_size=100, overlap=10)
# 11 chunks with 10-char overlap
```

---

## Testing

```python
import unittest

class TestStringUtils(unittest.TestCase):
    def test_sanitize_string(self):
        # Remove control characters
        self.assertEqual(
            sanitize_string("Hello\x00World"),
            "HelloWorld"
        )
        
        # Preserve newlines
        self.assertEqual(
            sanitize_string("Line1\nLine2"),
            "Line1\nLine2"
        )
        
        # Limit length
        self.assertEqual(
            len(sanitize_string("a" * 2000, max_length=100)),
            100
        )
    
    def test_truncate_string(self):
        text = "Hello World"
        self.assertEqual(truncate_string(text, 20), "Hello World")
        self.assertEqual(truncate_string(text, 8), "Hello...")
    
    def test_format_file_size(self):
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1048576), "1.0 MB")
```

---

## Best Practices

### DO ✅

- Sanitize all user input
- Validate before processing
- Use consistent encoding (UTF-8)
- Handle empty strings gracefully
- Test edge cases (empty, very long, special chars)

### DON'T ❌

- Trust user input
- Use `eval()` on strings
- Assume ASCII-only text
- Concatenate in loops (use StringBuilder or join)
- Ignore encoding errors

---

## Related Documentation

- **Dashboard Utils**: `source-docs/utilities/001-dashboard-utils.md`
- **Configuration Management**: `source-docs/utilities/008-configuration-management.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Utilities Team
