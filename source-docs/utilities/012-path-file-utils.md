# Path & File System Utilities

## Overview

Common file system operations, path manipulation, and directory management utilities used throughout Project-AI for consistent file handling.

**Purpose**: Centralized file operations, path normalization, directory management  
**Dependencies**: pathlib, os, shutil, tempfile

---

## Core Utilities

### 1. Path Operations

#### ensure_directory()
```python
from pathlib import Path

def ensure_directory(path: Path | str) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    
    Returns:
        Path object (created or existing)
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
```

**Usage**:
```python
data_dir = ensure_directory("data/logs")
config_dir = ensure_directory(Path("/etc/projectai/config"))
```

---

#### safe_join()
```python
def safe_join(base_path: Path, *parts: str) -> Path:
    """
    Safely join paths, preventing directory traversal.
    
    Args:
        base_path: Base directory
        *parts: Path components to join
    
    Returns:
        Joined path
    
    Raises:
        ValueError: If result escapes base_path
    """
    base_path = Path(base_path).resolve()
    result_path = (base_path / Path(*parts)).resolve()
    
    # Check if result is within base_path
    try:
        result_path.relative_to(base_path)
    except ValueError:
        raise ValueError(f"Path escapes base directory: {result_path}")
    
    return result_path
```

**Security Example**:
```python
base = Path("/data")

# Safe
safe_join(base, "user1", "file.txt")  # /data/user1/file.txt

# Blocks directory traversal
try:
    safe_join(base, "..", "etc", "passwd")  # Raises ValueError
except ValueError as e:
    print(f"Blocked: {e}")
```

---

### 2. File Operations

#### read_text_file()
```python
def read_text_file(path: Path | str, encoding: str = "utf-8") -> str:
    """
    Read text file with error handling.
    
    Args:
        path: File path
        encoding: Text encoding (default: utf-8)
    
    Returns:
        File contents
    
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If encoding fails
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(path, 'r', encoding=encoding) as f:
        return f.read()
```

---

#### write_text_file()
```python
def write_text_file(
    path: Path | str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> None:
    """
    Write text file with automatic directory creation.
    
    Args:
        path: File path
        content: Content to write
        encoding: Text encoding
        create_dirs: Create parent directories if needed
    """
    path = Path(path)
    
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)
```

---

#### atomic_write()
```python
import tempfile
import shutil

def atomic_write(path: Path | str, content: str) -> None:
    """
    Write file atomically (write to temp, then rename).
    
    Prevents corruption if process crashes during write.
    """
    path = Path(path)
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=path.parent,
        delete=False
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    # Atomic rename
    shutil.move(tmp_path, path)
```

---

### 3. Directory Operations

#### list_files()
```python
def list_files(
    directory: Path | str,
    pattern: str = "*",
    recursive: bool = False
) -> list[Path]:
    """
    List files in directory.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (default: "*")
        recursive: Search recursively
    
    Returns:
        List of file paths
    """
    directory = Path(directory)
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))
```

**Usage**:
```python
# List all Python files
py_files = list_files("src", pattern="*.py", recursive=True)

# List JSON files in directory
json_files = list_files("data", pattern="*.json")
```

---

#### clean_directory()
```python
def clean_directory(
    directory: Path | str,
    keep_dirs: bool = True
) -> int:
    """
    Clean all files from directory.
    
    Args:
        directory: Directory to clean
        keep_dirs: Keep subdirectories (only remove files)
    
    Returns:
        Number of files removed
    """
    directory = Path(directory)
    count = 0
    
    for item in directory.iterdir():
        if item.is_file():
            item.unlink()
            count += 1
        elif item.is_dir() and not keep_dirs:
            shutil.rmtree(item)
            count += 1
    
    return count
```

---

### 4. Temporary Files

#### temp_file()
```python
from contextlib import contextmanager

@contextmanager
def temp_file(
    suffix: str = "",
    prefix: str = "tmp",
    content: str | None = None
):
    """
    Context manager for temporary file.
    
    Automatically deleted after use.
    """
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix=suffix,
        prefix=prefix,
        delete=False
    ) as f:
        if content:
            f.write(content)
        temp_path = Path(f.name)
    
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            temp_path.unlink()

# Usage
with temp_file(suffix=".txt", content="test data") as temp_path:
    process_file(temp_path)
# File automatically deleted
```

---

#### temp_directory()
```python
@contextmanager
def temp_directory(prefix: str = "tmpdir"):
    """
    Context manager for temporary directory.
    
    Automatically deleted after use.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

# Usage
with temp_directory() as temp_dir:
    (temp_dir / "file.txt").write_text("data")
    process_directory(temp_dir)
# Directory automatically deleted
```

---

### 5. File Information

#### get_file_info()
```python
import os

def get_file_info(path: Path | str) -> dict:
    """
    Get comprehensive file information.
    
    Returns:
        Dictionary with file metadata
    """
    path = Path(path)
    stat = path.stat()
    
    return {
        "path": str(path.absolute()),
        "name": path.name,
        "size": stat.st_size,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "accessed": stat.st_atime,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "is_symlink": path.is_symlink(),
        "extension": path.suffix,
        "parent": str(path.parent)
    }
```

---

#### calculate_directory_size()
```python
def calculate_directory_size(directory: Path | str) -> int:
    """
    Calculate total size of directory (recursive).
    
    Returns:
        Total size in bytes
    """
    directory = Path(directory)
    total_size = 0
    
    for item in directory.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size
    
    return total_size

# Usage
size_bytes = calculate_directory_size("data")
size_mb = size_bytes / (1024 * 1024)
print(f"Directory size: {size_mb:.2f} MB")
```

---

### 6. File Searching

#### find_file()
```python
def find_file(
    filename: str,
    search_paths: list[Path | str]
) -> Path | None:
    """
    Search for file in multiple directories.
    
    Args:
        filename: File to find
        search_paths: Directories to search
    
    Returns:
        First matching path or None
    """
    for search_dir in search_paths:
        path = Path(search_dir) / filename
        if path.exists():
            return path
    
    return None

# Usage
config_file = find_file(
    "config.toml",
    [
        Path.cwd(),
        Path.home() / ".projectai",
        Path("/etc/projectai")
    ]
)
```

---

#### find_files_by_content()
```python
def find_files_by_content(
    directory: Path | str,
    pattern: str,
    file_pattern: str = "*.txt"
) -> list[Path]:
    """
    Find files containing specific pattern.
    
    Args:
        directory: Directory to search
        pattern: Text pattern to find
        file_pattern: File glob pattern
    
    Returns:
        List of matching files
    """
    import re
    
    directory = Path(directory)
    matches = []
    
    for file_path in directory.rglob(file_pattern):
        if file_path.is_file():
            try:
                content = file_path.read_text()
                if re.search(pattern, content):
                    matches.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                pass
    
    return matches
```

---

### 7. Backup Operations

#### backup_file()
```python
import datetime

def backup_file(path: Path | str, backup_dir: Path | str | None = None) -> Path:
    """
    Create backup of file with timestamp.
    
    Args:
        path: File to backup
        backup_dir: Backup directory (defaults to same dir)
    
    Returns:
        Path to backup file
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    # Generate backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_{timestamp}{path.suffix}"
    
    # Determine backup location
    if backup_dir:
        backup_path = Path(backup_dir) / backup_name
        ensure_directory(backup_dir)
    else:
        backup_path = path.parent / backup_name
    
    # Copy file
    shutil.copy2(path, backup_path)
    
    return backup_path

# Usage
backup_path = backup_file("important_config.json")
# Creates: important_config_20250124_103045.json
```

---

### 8. Path Normalization

#### normalize_path()
```python
def normalize_path(path: Path | str) -> Path:
    """
    Normalize path (resolve, absolute).
    
    - Converts to absolute path
    - Resolves symlinks
    - Normalizes separators
    """
    return Path(path).resolve()
```

---

#### relative_path()
```python
def relative_path(path: Path | str, base: Path | str) -> Path:
    """
    Get relative path from base.
    
    Args:
        path: Target path
        base: Base path
    
    Returns:
        Relative path
    """
    return Path(path).relative_to(base)

# Usage
full_path = Path("/home/user/project/src/main.py")
project_root = Path("/home/user/project")

rel_path = relative_path(full_path, project_root)
# Path("src/main.py")
```

---

## Advanced Patterns

### 1. File Watcher

```python
import time
from typing import Callable

class FileWatcher:
    """Watch file for changes."""
    
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.last_modified = self._get_mtime()
    
    def _get_mtime(self) -> float:
        """Get modification time."""
        if self.path.exists():
            return self.path.stat().st_mtime
        return 0.0
    
    def has_changed(self) -> bool:
        """Check if file has changed."""
        current_mtime = self._get_mtime()
        
        if current_mtime > self.last_modified:
            self.last_modified = current_mtime
            return True
        
        return False
    
    def watch(
        self,
        callback: Callable[[Path], None],
        interval: float = 1.0
    ):
        """Watch file and call callback on change."""
        while True:
            if self.has_changed():
                callback(self.path)
            time.sleep(interval)

# Usage
def on_config_change(path: Path):
    print(f"Config changed: {path}")
    reload_config()

watcher = FileWatcher("config.toml")
watcher.watch(on_config_change, interval=5.0)
```

---

### 2. Directory Synchronization

```python
def sync_directories(
    source: Path | str,
    destination: Path | str,
    delete_extra: bool = False
):
    """
    Synchronize source directory to destination.
    
    Args:
        source: Source directory
        destination: Destination directory
        delete_extra: Delete files in destination not in source
    """
    source = Path(source)
    destination = Path(destination)
    
    ensure_directory(destination)
    
    # Copy/update files from source
    for src_file in source.rglob('*'):
        if src_file.is_file():
            rel_path = src_file.relative_to(source)
            dst_file = destination / rel_path
            
            # Create parent directories
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy if newer or doesn't exist
            if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                shutil.copy2(src_file, dst_file)
    
    # Delete extra files if requested
    if delete_extra:
        for dst_file in destination.rglob('*'):
            if dst_file.is_file():
                rel_path = dst_file.relative_to(destination)
                src_file = source / rel_path
                
                if not src_file.exists():
                    dst_file.unlink()
```

---

### 3. Safe File Replace

```python
def safe_replace_file(
    path: Path | str,
    new_content: str,
    backup: bool = True
) -> None:
    """
    Safely replace file contents.
    
    - Creates backup (optional)
    - Writes to temp file
    - Atomically replaces original
    - Restores backup on error
    """
    path = Path(path)
    backup_path = None
    
    try:
        # Create backup
        if backup and path.exists():
            backup_path = backup_file(path)
        
        # Write to temp file
        atomic_write(path, new_content)
        
        # Delete backup if successful
        if backup_path:
            backup_path.unlink()
            
    except Exception as e:
        # Restore backup on error
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, path)
            backup_path.unlink()
        raise
```

---

## Testing

```python
import unittest

class TestPathUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_ensure_directory(self):
        dir_path = self.test_dir / "subdir" / "nested"
        result = ensure_directory(dir_path)
        
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())
    
    def test_safe_join(self):
        base = self.test_dir
        
        # Valid path
        result = safe_join(base, "file.txt")
        self.assertTrue(str(result).startswith(str(base)))
        
        # Invalid path (directory traversal)
        with self.assertRaises(ValueError):
            safe_join(base, "..", "etc", "passwd")
```

---

## Best Practices

### DO ✅

- Use `pathlib.Path` instead of string paths
- Call `ensure_directory()` before writing
- Use atomic writes for critical files
- Validate paths to prevent traversal
- Handle file not found errors
- Close files properly (use `with` statements)

### DON'T ❌

- Concatenate paths with string operations
- Ignore permission errors
- Trust user-provided paths without validation
- Forget to clean up temporary files
- Use relative paths in production

---

## Related Documentation

- **Test Helpers**: `source-docs/utilities/007-test-helpers.md`
- **Configuration Management**: `source-docs/utilities/008-configuration-management.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Utilities Team
