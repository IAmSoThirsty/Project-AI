"""
Utility functions for the Project AI system.
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any


def hash_data(data: dict[str, Any]) -> str:
    """
    Create a cryptographic hash of data.

    Args:
        data: Dictionary to hash

    Returns:
        SHA256 hex digest
    """
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def get_timestamp() -> float:
    """Get current Unix timestamp."""
    return time.time()


def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to ISO 8601 string.

    Args:
        timestamp: Unix timestamp

    Returns:
        ISO formatted string
    """
    return datetime.fromtimestamp(timestamp).isoformat()


def truncate_hash(hash_str: str, length: int = 8) -> str:
    """
    Truncate hash to specified length.

    Args:
        hash_str: Full hash string
        length: Number of characters to keep

    Returns:
        Truncated hash with ellipsis
    """
    return f"{hash_str[:length]}..." if len(hash_str) > length else hash_str


def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary.

    Args:
        data: Dictionary to query
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value or default
    """
    return data.get(key, default)
