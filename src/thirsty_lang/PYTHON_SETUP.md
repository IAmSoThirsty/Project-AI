# Python Setup Guide for Thirsty-lang 🐍💧

This guide explains how to set up and use the Python implementation of Thirsty-lang.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- git (for cloning the repository)

## Quick Setup

### Automated Setup (Recommended)

```bash

# Run the automated setup script

./setup_venv.sh
```

This script will:

1. Create a virtual environment in `.venv`
1. Activate the virtual environment
1. Upgrade pip, setuptools, and wheel
1. Install core dependencies
1. Optionally install development dependencies

### Manual Setup

```bash

# Create virtual environment

python3 -m venv .venv

# Activate virtual environment

source .venv/bin/activate  # Linux/macOS

# OR

.venv\Scripts\activate  # Windows

# Upgrade pip

pip install --upgrade pip setuptools wheel

# Install dependencies (if any)

pip install -r requirements.txt
```

## Running Python Implementation

### Run a Thirsty-lang Program

```bash

# Activate virtual environment first

source .venv/bin/activate

# Run a program

python3 src/thirsty_interpreter.py examples/hello.thirsty
```

### Start Python REPL

```bash

# Activate virtual environment

source .venv/bin/activate

# Start REPL

python3 src/thirsty_repl.py
```

## Python Files Overview

### Core Files

1. **thirsty_interpreter.py**
   - Main Python interpreter
   - Handles code parsing and execution
   - Variable management
   - Error handling

1. **thirsty_repl.py**
   - Interactive Python REPL
   - Command history
   - Variable inspection
   - Help system

1. **thirsty_utils.py**
   - Utility functions
   - File handling
   - Error formatting
   - Version checking

## Virtual Environment Management

### Activation

```bash

# Linux/macOS

source .venv/bin/activate

# Windows

.venv\Scripts\activate

# Using helper script

./activate_venv.sh
```

### Deactivation

```bash
deactivate
```

### Verification

```bash

# Check if virtual environment is active

which python  # Should point to .venv/bin/python

# Check Python version

python --version

# List installed packages

pip list
```

## Dependencies

### Core Dependencies (requirements.txt)

The Python implementation uses only Python standard library by default.
No external dependencies required for core functionality.

### Development Dependencies (requirements-dev.txt)

Optional tools for development:

- pytest - Testing framework
- pylint - Code linting
- black - Code formatting
- mypy - Type checking
- sphinx - Documentation generation

### Installing Development Dependencies

```bash

# Activate virtual environment

source .venv/bin/activate

# Install dev dependencies

pip install -r requirements-dev.txt
```

## Testing Python Implementation

### Run a Test Program

```bash

# Activate venv

source .venv/bin/activate

# Test hello world

python3 src/thirsty_interpreter.py examples/hello.thirsty

# Expected output:

# Hello, Thirsty World!

```

### Test REPL

```bash

# Start REPL

python3 src/thirsty_repl.py

# Try these commands:

thirsty> drink message = "Hello from Python!"
thirsty> pour message
thirsty> vars
thirsty> exit
```

## Development Workflow

### 1. Setup Environment

```bash
./setup_venv.sh
source .venv/bin/activate
```

### 2. Make Changes

Edit Python files in `src/` directory:

- `thirsty_interpreter.py`
- `thirsty_repl.py`
- `thirsty_utils.py`

### 3. Test Changes

```bash

# Run interpreter

python3 src/thirsty_interpreter.py examples/hello.thirsty

# Test REPL

python3 src/thirsty_repl.py
```

### 4. Run Linting (Optional)

```bash

# Install dev dependencies first

pip install -r requirements-dev.txt

# Run linters

pylint src/thirsty_*.py
flake8 src/thirsty_*.py
black --check src/thirsty_*.py

# Auto-format

black src/thirsty_*.py
```

### 5. Type Checking (Optional)

```bash

# Install mypy

pip install mypy

# Run type checking

mypy src/thirsty_*.py
```

## Comparing Node.js and Python Implementations

| Feature | Node.js | Python |
|---------|---------|--------|
| **Primary** | ✅ Yes | ❌ No |
| **Speed** | Fast | Fast |
| **Syntax** | JavaScript | Python |
| **REPL** | ✅ Full-featured | ✅ Full-featured |
| **Dependencies** | None | None |
| **Use Case** | Production | Alternative/Learning |

## Common Tasks

### Create New Example

```bash

# Create example file

echo 'drink greeting = "Hello, Python!"' > examples/python_test.thirsty
echo 'pour greeting' >> examples/python_test.thirsty

# Run it

python3 src/thirsty_interpreter.py examples/python_test.thirsty
```

### Batch Process Files

```bash

# Process all example files

for file in examples/*.thirsty; do
    echo "Running $file..."
    python3 src/thirsty_interpreter.py "$file"
done
```

### Integration with Scripts

```python

#!/usr/bin/env python3

from src.thirsty_interpreter import ThirstyInterpreter

# Create interpreter

interpreter = ThirstyInterpreter()

# Run code

code = '''
drink x = 42
pour x
'''
output = interpreter.interpret(code)
print(output)
```

## Troubleshooting

### Python Version Issues

```bash

# Check version

python3 --version

# Should be 3.8 or higher

# If not, install newer Python

```

### Virtual Environment Not Found

```bash

# Remove old venv

rm -rf .venv

# Create new one

python3 -m venv .venv

# Activate

source .venv/bin/activate
```

### Module Import Errors

```bash

# Make sure you're in the right directory

cd /path/to/Thirsty-lang

# Make sure venv is activated

source .venv/bin/activate

# Check Python path

python3 -c "import sys; print(sys.path)"
```

### Permission Denied

```bash

# Make scripts executable

chmod +x setup_venv.sh
chmod +x src/thirsty_interpreter.py
chmod +x src/thirsty_repl.py
```

## Advanced Usage

### Running with Python Debugger

```bash

# Run with pdb

python3 -m pdb src/thirsty_interpreter.py examples/hello.thirsty

# Or use ipdb (install with pip)

pip install ipdb
python3 -m ipdb src/thirsty_interpreter.py examples/hello.thirsty
```

### Profiling Python Implementation

```bash

# Time execution

time python3 src/thirsty_interpreter.py examples/hello.thirsty

# Profile with cProfile

python3 -m cProfile -s cumtime src/thirsty_interpreter.py examples/hello.thirsty
```

### Running in Jupyter Notebook

```python

# Install jupyter

pip install jupyter

# Start notebook

jupyter notebook

# In notebook:

from src.thirsty_interpreter import ThirstyInterpreter
interpreter = ThirstyInterpreter()
output = interpreter.interpret('drink x = 10\npour x')
print(output)
```

## VS Code Integration

### Python Extension Setup

1. Install Python extension in VS Code
1. Select interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
1. Choose `.venv/bin/python`

### Launch Configuration

Add to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Thirsty Interpreter",
      "type": "python",
      "request": "launch",
      "program": "src/thirsty_interpreter.py",
      "args": ["examples/hello.thirsty"],
      "console": "integratedTerminal"
    }
  ]
}
```

## Best Practices

1. **Always use virtual environment** - Isolate dependencies
1. **Keep venv out of git** - Already in .gitignore
1. **Update pip regularly** - `pip install --upgrade pip`
1. **Use requirements.txt** - Track dependencies
1. **Test changes** - Run examples after modifications
1. **Follow PEP 8** - Python style guidelines
1. **Type hints** - Add type annotations
1. **Documentation** - Use docstrings

## FAQ

### Why Python implementation?

- Alternative runtime for Python developers
- Educational purposes
- Cross-platform compatibility
- Easy integration with Python tools

### Is Python version production-ready?

The Python version is fully functional for basic Thirsty-lang features.
For production use, the Node.js version is recommended.

### Can I extend the Python implementation?

Yes! The code is modular and easy to extend:

- Add new language features in `thirsty_interpreter.py`
- Add new commands in `thirsty_repl.py`
- Add utilities in `thirsty_utils.py`

### How do I contribute?

1. Fork the repository
1. Create a virtual environment
1. Make changes to Python files
1. Test thoroughly
1. Submit a pull request

## Resources

- [Python Documentation](https://docs.python.org/)
- [Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [pip Documentation](https://pip.pypa.io/)
- Thirsty-lang main README.md

## Support

For Python-specific issues:

1. Check this guide
1. Verify Python version: `python3 --version`
1. Check virtual environment: `which python`
1. Review error messages
1. Open an issue on GitHub

---

Stay hydrated with Python! 🐍💧✨
