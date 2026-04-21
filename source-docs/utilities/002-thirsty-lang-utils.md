# Thirsty-Lang Python Utilities

## Overview

The Thirsty-Lang Utilities module (`src/thirsty_lang/src/thirsty_utils.py`) provides common utility functions for the Thirsty-Lang Python implementation, including file operations, validation, error formatting, and CLI utilities.

**Location**: `src/thirsty_lang/src/thirsty_utils.py`  
**Lines of Code**: 122  
**Dependencies**: Python stdlib (os, sys)  
**Purpose**: Support Thirsty-Lang compiler/interpreter operations

## What is Thirsty-Lang?

Thirsty-Lang is a custom programming language with multiple dialect levels:
- `.thirsty` - Basic dialect
- `.thirstyplus` - Enhanced features
- `.thirstyplusplus` - Advanced features
- `.thirstofgods` - God-tier dialect

This utilities module supports all dialects.

---

## Core Functions

### 1. File Operations

#### read_file()
```python
def read_file(filename: str) -> str
```

**Purpose**: Reads a Thirsty-Lang source file with UTF-8 encoding.

**Parameters**:
- `filename`: Path to the source file

**Returns**: File contents as string

**Raises**:
- `FileNotFoundError`: If file doesn't exist

**Example**:
```python
source_code = read_file("hello.thirsty")
print(source_code)
# Output: "HYDRATE x WITH 42"
```

**Design Notes**:
- Uses UTF-8 encoding for Unicode support
- Context manager ensures file is properly closed
- No caching - reads from disk each time

---

#### get_file_extension()
```python
def get_file_extension(filename: str) -> str
```

**Purpose**: Extracts file extension from path.

**Parameters**:
- `filename`: File path (relative or absolute)

**Returns**: Extension including dot (e.g., `.thirsty`)

**Example**:
```python
ext = get_file_extension("src/main.thirstyplus")
print(ext)  # ".thirstyplus"

ext = get_file_extension("noext")
print(ext)  # ""
```

**Implementation**: Uses `os.path.splitext()` for cross-platform compatibility.

---

#### is_thirsty_file()
```python
def is_thirsty_file(filename: str) -> bool
```

**Purpose**: Validates if a file is a Thirsty-Lang source file.

**Recognized Extensions**:
- `.thirsty` - Basic dialect
- `.thirstyplus` - Plus dialect
- `.thirstyplusplus` - PlusPlus dialect
- `.thirstofgods` - God-tier dialect

**Returns**: `True` if file has valid Thirsty-Lang extension

**Example**:
```python
is_thirsty_file("main.thirsty")        # True
is_thirsty_file("main.thirstofgods")   # True
is_thirsty_file("main.py")              # False
is_thirsty_file("main.THIRSTY")         # True (case-insensitive)
```

**Design Notes**:
- Case-insensitive check (`.lower()`)
- Returns `False` for empty extensions
- No content validation - only checks extension

---

#### find_thirsty_files()
```python
def find_thirsty_files(directory: str) -> list[str]
```

**Purpose**: Recursively finds all Thirsty-Lang files in a directory tree.

**Parameters**:
- `directory`: Root directory to search

**Returns**: List of absolute file paths

**Example**:
```python
files = find_thirsty_files("./src")
print(files)
# [
#   "/abs/path/to/src/main.thirsty",
#   "/abs/path/to/src/lib/utils.thirstyplus",
#   "/abs/path/to/src/core/engine.thirstofgods"
# ]
```

**Use Cases**:
- Project-wide compilation
- Static analysis
- Code search/indexing
- Dependency resolution

**Performance**: Uses `os.walk()` which is efficient for large directory trees.

---

### 2. Error Handling

#### format_error()
```python
def format_error(message: str, line_num: int | None = None) -> str
```

**Purpose**: Creates consistent error messages for compiler/interpreter.

**Parameters**:
- `message`: Error description
- `line_num`: Optional source line number

**Returns**: Formatted error string

**Example**:
```python
error = format_error("Undefined variable 'x'", line_num=42)
print(error)
# "Error on line 42: Undefined variable 'x'"

error = format_error("Syntax error")
print(error)
# "Error: Syntax error"
```

**Integration**:
```python
class ThirstyCompiler:
    def compile_line(self, line, line_num):
        try:
            return self.parse(line)
        except ParseError as e:
            raise CompilerError(format_error(str(e), line_num))
```

---

### 3. CLI Utilities

#### print_banner()
```python
def print_banner(title: str)
```

**Purpose**: Prints a formatted ASCII banner for CLI tools.

**Parameters**:
- `title`: Banner title text

**Output Format**:
```
╔══════════════════════════════════════════════════════════╗
║                 Thirsty-lang Python                      ║
╚══════════════════════════════════════════════════════════╝
```

**Example Usage**:
```python
if __name__ == "__main__":
    print_banner("Thirsty-Lang Compiler v1.0")
    # Compiler logic...
```

**Design**:
- Fixed width: 60 characters
- Box-drawing characters (Unicode U+2550, U+2551)
- Auto-centers title with padding

**Customization**:
```python
# For different width
def print_banner(title: str, width: int = 80):
    border = "═" * (width - 2)
    print(f"╔{border}╗")
    padding = (width - len(title) - 2) // 2
    print(f"║{' ' * padding}{title}{' ' * (width - len(title) - padding - 2)}║")
    print(f"╚{border}╝")
```

---

#### check_version()
```python
def check_version() -> str
```

**Purpose**: Returns version information for Python runtime and Thirsty-Lang.

**Returns**: Version string in format:
```
"Python 3.11.5 | Thirsty-lang 1.0.0"
```

**Example**:
```python
version_info = check_version()
print(version_info)
# "Python 3.12.0 | Thirsty-lang 1.0.0"
```

**Use Cases**:
- `--version` flag in CLI
- Debug output
- Compatibility checks
- Bug reports

**Implementation**:
```python
def check_version() -> str:
    python_version = (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )
    # TODO: Load Thirsty-Lang version from package metadata
    return f"Python {python_version} | Thirsty-lang 1.0.0"
```

---

## Usage Patterns

### Pattern 1: Compiler Entry Point

```python
#!/usr/bin/env python3
import sys
from thirsty_utils import (
    print_banner,
    check_version,
    is_thirsty_file,
    read_file,
    format_error,
)

def main():
    print_banner("Thirsty-Lang Compiler")
    print(f"{check_version()}\n")
    
    if len(sys.argv) < 2:
        print("Usage: thirsty <file.thirsty>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    
    if not is_thirsty_file(source_file):
        print(format_error(f"Invalid file extension: {source_file}"))
        sys.exit(1)
    
    try:
        source_code = read_file(source_file)
        compile(source_code)
    except FileNotFoundError:
        print(format_error(f"File not found: {source_file}"))
        sys.exit(1)
    except CompileError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

### Pattern 2: Project-Wide Analysis

```python
from thirsty_utils import find_thirsty_files, read_file

def analyze_project(project_dir: str):
    """Analyze all Thirsty-Lang files in a project."""
    files = find_thirsty_files(project_dir)
    
    stats = {
        "total_files": len(files),
        "total_lines": 0,
        "by_dialect": {
            ".thirsty": 0,
            ".thirstyplus": 0,
            ".thirstyplusplus": 0,
            ".thirstofgods": 0,
        }
    }
    
    for filepath in files:
        source = read_file(filepath)
        lines = source.count('\n') + 1
        stats["total_lines"] += lines
        
        ext = get_file_extension(filepath)
        if ext in stats["by_dialect"]:
            stats["by_dialect"][ext] += 1
    
    return stats
```

---

### Pattern 3: Error Reporting Chain

```python
class ThirstyLexer:
    def tokenize(self, source: str):
        for line_num, line in enumerate(source.split('\n'), start=1):
            try:
                tokens = self.lex_line(line)
                yield tokens
            except LexError as e:
                raise LexError(format_error(str(e), line_num)) from e

class ThirstyParser:
    def parse(self, tokens):
        # If lexer error occurs, it already has line number
        for token_list in tokens:
            try:
                ast_node = self.parse_tokens(token_list)
                yield ast_node
            except ParseError as e:
                # Re-raise with context
                raise
```

---

## Testing Strategies

### Unit Tests

```python
import tempfile
import unittest
from pathlib import Path
from thirsty_utils import *

class TestThirstyUtils(unittest.TestCase):
    
    def test_is_thirsty_file(self):
        self.assertTrue(is_thirsty_file("test.thirsty"))
        self.assertTrue(is_thirsty_file("test.thirstyplus"))
        self.assertTrue(is_thirsty_file("test.thirstyplusplus"))
        self.assertTrue(is_thirsty_file("test.thirstofgods"))
        self.assertTrue(is_thirsty_file("TEST.THIRSTY"))  # Case-insensitive
        
        self.assertFalse(is_thirsty_file("test.py"))
        self.assertFalse(is_thirsty_file("test.txt"))
        self.assertFalse(is_thirsty_file("noext"))
    
    def test_read_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.thirsty', delete=False) as f:
            f.write("HYDRATE x WITH 42")
            temp_path = f.name
        
        try:
            content = read_file(temp_path)
            self.assertEqual(content, "HYDRATE x WITH 42")
        finally:
            Path(temp_path).unlink()
    
    def test_format_error(self):
        error = format_error("Test error")
        self.assertEqual(error, "Error: Test error")
        
        error = format_error("Test error", line_num=10)
        self.assertEqual(error, "Error on line 10: Test error")
    
    def test_find_thirsty_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "main.thirsty").touch()
            Path(tmpdir, "test.py").touch()
            subdir = Path(tmpdir, "lib")
            subdir.mkdir()
            Path(subdir, "utils.thirstyplus").touch()
            
            files = find_thirsty_files(tmpdir)
            
            self.assertEqual(len(files), 2)
            self.assertTrue(any("main.thirsty" in f for f in files))
            self.assertTrue(any("utils.thirstyplus" in f for f in files))
            self.assertFalse(any("test.py" in f for f in files))
```

---

## Integration with Thirsty-Lang Ecosystem

### Compiler Integration

```python
# thirsty_compiler.py
from thirsty_utils import read_file, format_error

class Compiler:
    def compile_file(self, filepath: str):
        source = read_file(filepath)
        return self.compile_source(source, filepath)
```

### Interpreter Integration

```python
# thirsty_repl.py
from thirsty_utils import print_banner, check_version

def repl():
    print_banner("Thirsty-Lang REPL")
    print(check_version())
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            line = input(">>> ")
            if line == "exit":
                break
            result = interpret(line)
            print(result)
        except Exception as e:
            print(format_error(str(e)))
```

### Linter Integration

```python
# thirsty_lint.py
from thirsty_utils import find_thirsty_files, read_file, format_error

def lint_project(project_dir: str):
    files = find_thirsty_files(project_dir)
    issues = []
    
    for filepath in files:
        source = read_file(filepath)
        file_issues = lint_source(source)
        
        for line_num, issue in file_issues:
            issues.append(format_error(issue, line_num))
    
    return issues
```

---

## Performance Considerations

### File Reading

**Current Implementation**:
- No caching
- Reads entire file into memory
- UTF-8 decoding

**For Large Files** (>100MB):
```python
def read_file_lazy(filename: str):
    """Lazy line-by-line reading for large files."""
    with open(filename, encoding="utf-8") as f:
        for line in f:
            yield line
```

### Directory Traversal

**Current**: `os.walk()` - efficient for most cases

**For Huge Projects** (>10,000 files):
```python
def find_thirsty_files_fast(directory: str, max_depth: int = 5):
    """Fast file finding with depth limit."""
    from pathlib import Path
    
    valid_extensions = {".thirsty", ".thirstyplus", ".thirstyplusplus", ".thirstofgods"}
    
    def scan(path: Path, depth: int):
        if depth > max_depth:
            return
        
        for item in path.iterdir():
            if item.is_file() and item.suffix.lower() in valid_extensions:
                yield str(item)
            elif item.is_dir():
                yield from scan(item, depth + 1)
    
    return list(scan(Path(directory), 0))
```

---

## Known Limitations

1. **Unicode Handling**:
   - Assumes UTF-8 encoding
   - No BOM detection
   - No encoding auto-detection

2. **Error Messages**:
   - No internationalization (i18n)
   - No error codes
   - No structured error objects

3. **Banner Display**:
   - Fixed width (60 chars)
   - Assumes terminal supports Unicode box-drawing
   - No color support

4. **Version Management**:
   - Hardcoded version string
   - No semantic versioning parsing
   - No version comparison utilities

---

## Future Enhancements

### Planned Features

```python
# Enhanced error with code context
def format_error_with_context(
    message: str,
    source: str,
    line_num: int,
    col_num: int | None = None,
) -> str:
    """Format error with source code context."""
    lines = source.split('\n')
    error_line = lines[line_num - 1] if line_num <= len(lines) else ""
    
    output = [f"Error on line {line_num}: {message}"]
    output.append(f"  {error_line}")
    
    if col_num:
        output.append(f"  {' ' * (col_num - 1)}^")
    
    return '\n'.join(output)
```

```python
# Config file support
def load_thirsty_config(directory: str) -> dict:
    """Load .thirstyrc configuration file."""
    config_path = Path(directory) / ".thirstyrc"
    if config_path.exists():
        import json
        with open(config_path) as f:
            return json.load(f)
    return {}
```

---

## Related Documentation

- **Thirsty-Lang Language Spec**: `docs/thirsty-lang-spec.md`
- **Compiler Architecture**: `docs/compiler-architecture.md`
- **CLI Reference**: `docs/cli-reference.md`

---

## Version History

- **v1.0.0** (Current): Initial stable release
- **v0.5.0**: Added `find_thirsty_files()` recursive search
- **v0.3.0**: Added `.thirstofgods` dialect support
- **v0.1.0**: Initial utilities (read, validate, format)

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: Thirsty-Lang Core Team
