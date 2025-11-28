"""Tests for json_file_utils module."""

import os
from app.core.json_file_utils import load_json_file, save_json_file, append_to_json_list


def test_load_json_file_nonexistent(tmp_path):
    """Test loading a file that doesn't exist returns default."""
    filepath = str(tmp_path / "nonexistent.json")
    result = load_json_file(filepath)
    assert result == {}

    result = load_json_file(filepath, default=[])
    assert result == []


def test_load_json_file_invalid(tmp_path):
    """Test loading an invalid JSON file returns default."""
    filepath = str(tmp_path / "invalid.json")
    with open(filepath, 'w') as f:
        f.write("not valid json {{{")
    result = load_json_file(filepath)
    assert result == {}


def test_save_and_load_json_file(tmp_path):
    """Test saving and loading JSON data."""
    filepath = str(tmp_path / "test.json")
    data = {"key": "value", "nested": {"a": 1}}

    success = save_json_file(filepath, data)
    assert success is True
    assert os.path.exists(filepath)

    loaded = load_json_file(filepath)
    assert loaded == data


def test_append_to_json_list(tmp_path):
    """Test appending to a JSON list file."""
    filepath = str(tmp_path / "list.json")

    # Append to non-existent file
    success = append_to_json_list(filepath, {"id": 1})
    assert success is True

    # Verify content
    loaded = load_json_file(filepath, default=[])
    assert loaded == [{"id": 1}]

    # Append another item
    success = append_to_json_list(filepath, {"id": 2})
    assert success is True

    loaded = load_json_file(filepath, default=[])
    assert loaded == [{"id": 1}, {"id": 2}]


def test_append_to_json_list_overwrites_non_list(tmp_path):
    """Test appending to a file that doesn't contain a list."""
    filepath = str(tmp_path / "notlist.json")
    save_json_file(filepath, {"not": "a list"})

    success = append_to_json_list(filepath, {"id": 1})
    assert success is True

    loaded = load_json_file(filepath, default=[])
    assert loaded == [{"id": 1}]


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
