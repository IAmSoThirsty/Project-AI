# Path Traversal Security - Developer Quick Reference

## Quick Start

```python
from app.security.path_security import safe_path_join, safe_open, sanitize_filename

# ✅ DO: Use safe_path_join for all path operations
user_file = safe_path_join(data_dir, user_input)

# ✅ DO: Use safe_open for file operations
with safe_open(data_dir, filename, 'r') as f:
    content = f.read()

# ✅ DO: Sanitize user input in filenames
safe_name = sanitize_filename(username)
file_path = safe_path_join(data_dir, f"{safe_name}_profile.json")

# ❌ DON'T: Use os.path.join with user input
dangerous = os.path.join(data_dir, user_input)  # VULNERABLE!

# ❌ DON'T: Open files without validation
with open(f"{data_dir}/{user_input}") as f:  # VULNERABLE!
    content = f.read()
```

## Common Patterns

### Pattern 1: User Data Files
```python
class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_user_data(self, username, data):
        # Sanitize username for filename
        safe_username = sanitize_filename(username)
        filepath = safe_path_join(self.data_dir, f"{safe_username}.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
```

### Pattern 2: File Upload
```python
def handle_upload(uploaded_file, user_id):
    # Sanitize filename
    safe_name = sanitize_filename(uploaded_file.filename)
    
    # Ensure in user's directory
    user_dir = safe_path_join("uploads", user_id)
    os.makedirs(user_dir, exist_ok=True)
    
    # Save securely
    filepath = safe_path_join(user_dir, safe_name)
    uploaded_file.save(filepath)
```

### Pattern 3: Configuration Files
```python
class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
    
    def load_config(self, config_name):
        # Validate filename
        validate_filename(config_name)
        
        # Load securely
        with safe_open(self.config_dir, config_name, 'r') as f:
            return json.load(f)
```

## Attack Vectors to Block

| Attack | Example | Protection |
|--------|---------|------------|
| Parent directory | `../../../etc/passwd` | `safe_path_join` blocks `..` |
| Absolute path | `/etc/passwd` | `safe_path_join` blocks `/` prefix |
| Windows drive | `C:\\Windows\\` | `safe_path_join` blocks drive letters |
| Null byte | `file\x00.txt` | `validate_filename` blocks null bytes |
| Hidden files | `.bashrc` | `validate_filename` blocks leading `.` |
| Reserved names | `CON.txt` | `validate_filename` blocks Windows reserved |

## Migration Guide

### Before (Vulnerable):
```python
def save_file(self, filename):
    path = os.path.join("data", filename)
    with open(path, 'w') as f:
        f.write(content)
```

### After (Secure):
```python
def save_file(self, filename):
    path = safe_path_join("data", filename)
    with open(path, 'w') as f:
        f.write(content)
```

Or even better:
```python
def save_file(self, filename):
    with safe_open("data", filename, 'w') as f:
        f.write(content)
```

## Testing Your Code

```python
def test_path_security():
    # Test path traversal is blocked
    with pytest.raises(PathTraversalError):
        safe_path_join("/data", "../../../etc/passwd")
    
    # Test normal paths work
    result = safe_path_join("/data", "user", "file.txt")
    assert "/data/user/file.txt" in result
```

## Error Handling

```python
from app.security.path_security import PathTraversalError

try:
    filepath = safe_path_join(data_dir, user_input)
    with open(filepath, 'r') as f:
        data = f.read()
except PathTraversalError as e:
    logger.warning(f"Path traversal blocked: {e}")
    return {"error": "Invalid file path"}
except FileNotFoundError:
    return {"error": "File not found"}
```

## FAQ

**Q: What if I need to access files outside data_dir?**  
A: Use a different base_dir for that category of files. Never use user input to specify the base directory.

```python
# ✅ DO: Separate base directories
config_path = safe_path_join("config", user_file)
data_path = safe_path_join("data", user_file)

# ❌ DON'T: User-controlled base directory
path = safe_path_join(user_base_dir, filename)  # Still vulnerable!
```

**Q: What about symlinks?**  
A: Use `is_safe_symlink()` to validate symlink targets stay within base_dir.

```python
if os.path.islink(filepath):
    if not is_safe_symlink(filepath, base_dir):
        raise PathTraversalError("Symlink escapes base directory")
```

**Q: Should I sanitize or validate?**  
A: Both! Validate for security-critical operations, sanitize for user-facing features.

```python
# Critical: Authentication, system files
validate_filename(filename)  # Raises exception if invalid

# User-facing: Display names, logs
safe_name = sanitize_filename(username)  # Cleans dangerous chars
```

**Q: What about URL paths in web apps?**  
A: Same principles apply. Never trust user input.

```python
@app.route('/files/<path:filename>')
def serve_file(filename):
    # Validate before serving
    safe_file = safe_path_join("public", filename)
    return send_file(safe_file)
```

## Security Checklist

When writing file operations, ask:

- [ ] Is any part of the path user-controlled?
- [ ] Am I using `safe_path_join` instead of `os.path.join`?
- [ ] Have I validated filenames with `validate_filename`?
- [ ] Are user inputs sanitized with `sanitize_filename`?
- [ ] Is the base directory hard-coded (never user input)?
- [ ] Do I handle `PathTraversalError` appropriately?
- [ ] Have I tested with `../../../etc/passwd`?

## Complete Example

```python
from app.security.path_security import (
    safe_path_join,
    safe_open,
    sanitize_filename,
    validate_filename,
    PathTraversalError,
)

class SecureFileManager:
    """Example of secure file management."""
    
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def save_user_file(self, username, filename, content):
        """Save a file for a user."""
        try:
            # Sanitize inputs
            safe_username = sanitize_filename(username)
            safe_filename = sanitize_filename(filename)
            
            # Build path securely
            user_dir = safe_path_join(self.base_dir, safe_username)
            os.makedirs(user_dir, exist_ok=True)
            
            # Save file
            with safe_open(user_dir, safe_filename, 'w') as f:
                f.write(content)
            
            return {"success": True, "path": safe_filename}
            
        except PathTraversalError as e:
            logger.warning(f"Path traversal blocked: {e}")
            return {"success": False, "error": "Invalid path"}
    
    def load_user_file(self, username, filename):
        """Load a file for a user."""
        try:
            # Validate filename
            validate_filename(filename)
            
            # Build path securely
            safe_username = sanitize_filename(username)
            user_dir = safe_path_join(self.base_dir, safe_username)
            
            # Load file
            with safe_open(user_dir, filename, 'r') as f:
                return {"success": True, "content": f.read()}
                
        except PathTraversalError as e:
            logger.warning(f"Path traversal blocked: {e}")
            return {"success": False, "error": "Invalid path"}
        except FileNotFoundError:
            return {"success": False, "error": "File not found"}
```

## Remember

🔒 **Never trust user input**  
✅ **Always validate paths**  
🛡️ **Use the security utilities**  
📝 **Log security events**  
🧪 **Test with malicious input**  

---

For detailed documentation, see: `src/app/security/path_security.py`  
For test examples, see: `tests/test_path_security.py`  
For full report, see: `PATH_TRAVERSAL_FIX_REPORT.md`
