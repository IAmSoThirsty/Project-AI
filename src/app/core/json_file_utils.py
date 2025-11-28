"""Utility functions for JSON file operations.

This module provides common functions for loading and saving JSON data files,
consolidating duplicated code across the application.
"""

import json
import os
from typing import Any


def load_json_file(filepath: str, default: Any = None) -> Any:
    """Load JSON data from a file.

    Args:
        filepath: Path to the JSON file.
        default: Default value to return if file doesn't exist or is invalid.
                 If None, returns an empty dict.

    Returns:
        The parsed JSON data, or the default value if loading fails.
    """
    if default is None:
        default = {}
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json_file(filepath: str, data: Any) -> bool:
    """Save data to a JSON file.

    Args:
        filepath: Path to the JSON file.
        data: Data to serialize as JSON.

    Returns:
        True if successful, False otherwise.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except OSError:
        return False


def append_to_json_list(filepath: str, entry: Any) -> bool:
    """Append an entry to a JSON list file.

    If the file doesn't exist or is empty, creates a new list.

    Args:
        filepath: Path to the JSON file containing a list.
        entry: The entry to append to the list.

    Returns:
        True if successful, False otherwise.
    """
    data = load_json_file(filepath, default=[])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    return save_json_file(filepath, data)
