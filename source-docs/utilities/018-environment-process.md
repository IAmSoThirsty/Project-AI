# Environment & Process Utilities

## Overview

Utilities for environment variable management, process control, system information, and runtime environment detection for Project-AI.

**Purpose**: Environment management, process control, system detection  
**Dependencies**: os, sys, subprocess, platform, psutil (optional)

---

## Environment Variables

### 1. Environment Access

#### get_env()
```python
import os

def get_env(
    key: str,
    default: Any = None,
    required: bool = False,
    cast: type = str
) -> Any:
    """
    Get environment variable with type casting.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: Raise error if not set
        cast: Type to cast to (str, int, float, bool)
    
    Returns:
        Environment variable value
    
    Raises:
        ValueError: If required and not set
    """
    value = os.getenv(key)
    
    if value is None:
        if required:
            raise ValueError(f"Required environment variable not set: {key}")
        return default
    
    # Type casting
    if cast == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast == int:
        return int(value)
    elif cast == float:
        return float(value)
    else:
        return value

# Usage
api_key = get_env("API_KEY", required=True)
debug_mode = get_env("DEBUG", default=False, cast=bool)
timeout = get_env("TIMEOUT", default=30, cast=int)
```

---

#### load_env_file()
```python
def load_env_file(filepath: str = ".env") -> dict[str, str]:
    """
    Load environment variables from .env file.
    
    Args:
        filepath: Path to .env file
    
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    if not os.path.exists(filepath):
        logger.warning(f".env file not found: {filepath}")
        return env_vars
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                env_vars[key] = value
                os.environ[key] = value
    
    return env_vars

# Usage
load_env_file(".env")
api_key = os.getenv("API_KEY")
```

---

### 2. Environment Detection

#### is_production()
```python
def is_production() -> bool:
    """Check if running in production environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env in ("production", "prod")

def is_development() -> bool:
    """Check if running in development environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env in ("development", "dev")

def is_testing() -> bool:
    """Check if running in test environment."""
    return os.getenv("TESTING", "false").lower() == "true"

# Usage
if is_production():
    # Strict error handling
    pass
elif is_development():
    # Verbose logging
    pass
```

---

## Process Management

### 1. Process Execution

#### run_command()
```python
import subprocess

def run_command(
    command: list[str],
    timeout: int | None = None,
    capture_output: bool = True,
    check: bool = True
) -> subprocess.CompletedProcess:
    """
    Run shell command safely.
    
    Args:
        command: Command as list of strings
        timeout: Timeout in seconds
        capture_output: Capture stdout/stderr
        check: Raise error on non-zero exit
    
    Returns:
        CompletedProcess object
    
    Raises:
        subprocess.CalledProcessError: If command fails and check=True
        subprocess.TimeoutExpired: If timeout exceeded
    """
    try:
        result = subprocess.run(
            command,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.cmd}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Output: {e.output}")
        raise
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {e.cmd}")
        raise

# Usage
result = run_command(["git", "status"], timeout=10)
print(result.stdout)

# With error handling
try:
    run_command(["invalid-command"])
except subprocess.CalledProcessError:
    print("Command failed")
```

---

#### run_command_async()
```python
async def run_command_async(
    command: list[str],
    timeout: int | None = None
) -> tuple[str, str, int]:
    """
    Run command asynchronously.
    
    Returns:
        (stdout, stderr, returncode)
    """
    import asyncio
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        return (
            stdout.decode(),
            stderr.decode(),
            process.returncode
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise

# Usage
stdout, stderr, code = await run_command_async(["ls", "-la"], timeout=10)
```

---

### 2. Process Information

#### get_process_info()
```python
def get_process_info() -> dict:
    """
    Get current process information.
    
    Returns:
        Dictionary with process info
    """
    import psutil  # Optional dependency
    
    process = psutil.Process()
    
    return {
        "pid": process.pid,
        "name": process.name(),
        "status": process.status(),
        "cpu_percent": process.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "num_threads": process.num_threads(),
        "create_time": process.create_time(),
        "username": process.username()
    }

# Usage
info = get_process_info()
print(f"PID: {info['pid']}")
print(f"Memory: {info['memory_mb']:.2f} MB")
```

---

## System Information

### 1. System Detection

#### get_system_info()
```python
import platform

def get_system_info() -> dict:
    """
    Get system information.
    
    Returns:
        Dictionary with system info
    """
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }

# Usage
info = get_system_info()
print(f"OS: {info['os']}")
print(f"Python: {info['python_version']}")
```

---

#### is_windows()
```python
def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"

def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")

def is_mac() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"

# Usage
if is_windows():
    # Windows-specific code
    pass
elif is_linux():
    # Linux-specific code
    pass
```

---

### 2. Resource Information

#### get_memory_info()
```python
def get_memory_info() -> dict:
    """
    Get system memory information.
    
    Returns:
        Dictionary with memory info (requires psutil)
    """
    import psutil
    
    mem = psutil.virtual_memory()
    
    return {
        "total_gb": mem.total / (1024 ** 3),
        "available_gb": mem.available / (1024 ** 3),
        "used_gb": mem.used / (1024 ** 3),
        "percent_used": mem.percent
    }

# Usage
mem = get_memory_info()
print(f"Memory: {mem['used_gb']:.2f} GB / {mem['total_gb']:.2f} GB")
print(f"Usage: {mem['percent_used']}%")
```

---

#### get_disk_info()
```python
def get_disk_info(path: str = "/") -> dict:
    """
    Get disk information.
    
    Args:
        path: Path to check
    
    Returns:
        Dictionary with disk info
    """
    import psutil
    
    disk = psutil.disk_usage(path)
    
    return {
        "total_gb": disk.total / (1024 ** 3),
        "used_gb": disk.used / (1024 ** 3),
        "free_gb": disk.free / (1024 ** 3),
        "percent_used": disk.percent
    }

# Usage
disk = get_disk_info()
print(f"Disk: {disk['free_gb']:.2f} GB free")
```

---

## Advanced Utilities

### 1. Environment Configuration Class

```python
class EnvironmentConfig:
    """Centralized environment configuration."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = get_env("DEBUG", default=False, cast=bool)
        
        # API Configuration
        self.api_key = get_env("API_KEY", required=True)
        self.api_url = get_env("API_URL", default="https://api.example.com")
        self.api_timeout = get_env("API_TIMEOUT", default=30, cast=int)
        
        # Database Configuration
        self.db_host = get_env("DB_HOST", default="localhost")
        self.db_port = get_env("DB_PORT", default=5432, cast=int)
        self.db_name = get_env("DB_NAME", default="projectai")
        
        # Feature Flags
        self.enable_caching = get_env("ENABLE_CACHING", default=True, cast=bool)
        self.enable_metrics = get_env("ENABLE_METRICS", default=False, cast=bool)
    
    def is_production(self) -> bool:
        """Check if production environment."""
        return self.environment == "production"
    
    def validate(self) -> None:
        """Validate configuration."""
        if self.is_production() and self.debug:
            raise ValueError("Debug mode cannot be enabled in production")
        
        if self.api_timeout <= 0:
            raise ValueError("API timeout must be positive")

# Usage
config = EnvironmentConfig()
config.validate()

if config.is_production():
    setup_production_logging()
```

---

### 2. Process Pool Manager

```python
class ManagedProcess:
    """Managed subprocess."""
    
    def __init__(self, command: list[str]):
        self.command = command
        self.process = None
    
    def start(self) -> None:
        """Start process."""
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Started process {self.process.pid}: {' '.join(self.command)}")
    
    def stop(self, timeout: int = 10) -> None:
        """Stop process gracefully."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate, killing...")
                self.process.kill()
                self.process.wait()
    
    def is_running(self) -> bool:
        """Check if process is running."""
        return self.process is not None and self.process.poll() is None
    
    def get_output(self) -> tuple[str, str]:
        """Get stdout and stderr."""
        if self.process:
            stdout, stderr = self.process.communicate()
            return stdout, stderr
        return "", ""

# Usage
proc = ManagedProcess(["python", "worker.py"])
proc.start()

# ... do other work ...

proc.stop()
```

---

## Best Practices

### DO ✅

- Load .env files in development
- Validate required environment variables at startup
- Use environment-specific configurations
- Sanitize command inputs
- Set timeouts for subprocesses
- Handle process cleanup properly

### DON'T ❌

- Hard-code configuration values
- Store secrets in environment variables (use secret management)
- Use shell=True in subprocess (security risk)
- Forget to close subprocesses
- Ignore subprocess errors
- Run untrusted commands

---

## Testing

```python
import unittest

class TestEnvironment(unittest.TestCase):
    def test_get_env_with_default(self):
        value = get_env("NONEXISTENT_VAR", default="default")
        self.assertEqual(value, "default")
    
    def test_get_env_cast_bool(self):
        os.environ["TEST_BOOL"] = "true"
        value = get_env("TEST_BOOL", cast=bool)
        self.assertTrue(value)
```

---

## Related Documentation

- **Configuration Management**: `source-docs/utilities/008-configuration-management.md`
- **Async Utilities**: `source-docs/utilities/017-async-concurrency.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Infrastructure Team
