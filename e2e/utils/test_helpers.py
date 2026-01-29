"""
Test Helper Utilities for E2E Tests

Common helper functions used across E2E test scenarios.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    check_interval: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> bool:
    """Wait for a condition to become true.

    Args:
        condition: Callable that returns True when condition is met
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        error_message: Error message if timeout

    Returns:
        True if condition was met, False if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            if condition():
                return True
        except Exception as e:
            logger.debug(f"Condition check raised exception: {e}")

        time.sleep(check_interval)

    logger.error(error_message)
    return False


def load_json_file(file_path: Path) -> dict[str, Any] | list[Any]:
    """Load and parse a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)


def save_json_file(
    data: dict[str, Any] | list[Any],
    file_path: Path,
    indent: int = 2,
) -> None:
    """Save data to a JSON file.

    Args:
        data: Data to save
        file_path: Path to save to
        indent: JSON indentation level
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent)

    logger.debug(f"Saved JSON data to {file_path}")


def create_test_file(
    directory: Path,
    filename: str,
    content: str,
) -> Path:
    """Create a test file with content.

    Args:
        directory: Directory to create file in
        filename: Name of the file
        content: File content

    Returns:
        Path to created file
    """
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename

    with open(file_path, "w") as f:
        f.write(content)

    logger.debug(f"Created test file: {file_path}")
    return file_path


def cleanup_test_files(*file_paths: Path) -> None:
    """Clean up test files.

    Args:
        *file_paths: Paths to files to delete
    """
    for file_path in file_paths:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
                logger.debug(f"Deleted test file: {file_path}")
            elif file_path.is_dir():
                import shutil

                shutil.rmtree(file_path)
                logger.debug(f"Deleted test directory: {file_path}")


def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure function execution time.

    Args:
        func: Function to measure

    Returns:
        Wrapped function that logs execution time
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
        return result

    return wrapper


def retry_on_failure(
    func: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exceptions: tuple = (Exception,),
) -> Any:
    """Retry a function on failure.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}"
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    raise last_exception


def compare_json_objects(
    obj1: dict[str, Any] | list[Any],
    obj2: dict[str, Any] | list[Any],
    ignore_keys: list[str] | None = None,
) -> tuple[bool, list[str]]:
    """Compare two JSON objects for equality.

    Args:
        obj1: First object
        obj2: Second object
        ignore_keys: Keys to ignore in comparison

    Returns:
        Tuple of (are_equal, differences)
    """
    ignore_keys = ignore_keys or []
    differences = []

    def compare_recursive(o1, o2, path=""):
        if type(o1) != type(o2):
            differences.append(f"{path}: Type mismatch ({type(o1)} vs {type(o2)})")
            return

        if isinstance(o1, dict):
            all_keys = set(o1.keys()) | set(o2.keys())
            for key in all_keys:
                if key in ignore_keys:
                    continue

                new_path = f"{path}.{key}" if path else key

                if key not in o1:
                    differences.append(f"{new_path}: Missing in first object")
                elif key not in o2:
                    differences.append(f"{new_path}: Missing in second object")
                else:
                    compare_recursive(o1[key], o2[key], new_path)

        elif isinstance(o1, list):
            if len(o1) != len(o2):
                differences.append(
                    f"{path}: Length mismatch ({len(o1)} vs {len(o2)})"
                )
            else:
                for i, (item1, item2) in enumerate(zip(o1, o2)):
                    compare_recursive(item1, item2, f"{path}[{i}]")

        else:
            if o1 != o2:
                differences.append(f"{path}: Value mismatch ({o1} vs {o2})")

    compare_recursive(obj1, obj2)
    return len(differences) == 0, differences


def get_timestamp_iso() -> str:
    """Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    from datetime import datetime

    return datetime.now().isoformat()


def parse_iso_timestamp(timestamp_str: str) -> float:
    """Parse ISO timestamp string to epoch seconds.

    Args:
        timestamp_str: ISO formatted timestamp

    Returns:
        Epoch seconds
    """
    from datetime import datetime

    dt = datetime.fromisoformat(timestamp_str)
    return dt.timestamp()
