"""Extended tests for UserManager (20+)."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from app.core.user_manager import UserManager


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as td:
        yield td


def test_create_and_authenticate(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    assert um.create_user("alice", "pw") is True
    assert um.authenticate("alice", "pw") is True


def test_get_user_data_sanitized(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    um.create_user("bob", "pw")
    data = um.get_user_data("bob")
    assert "password_hash" not in data


def test_update_preferences_and_role(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    um.create_user("c", "pw")
    ok = um.update_user("c", preferences={"theme": "dark"}, role="admin")
    assert ok is True
    d = um.get_user_data("c")
    assert d["preferences"]["theme"] == "dark"
    assert d["role"] == "admin"


def test_set_password_changes_hash(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    um.create_user("d", "pw1")
    old_hash = um.users["d"]["password_hash"]
    um.set_password("d", "pw2")
    assert um.users["d"]["password_hash"] != old_hash
    assert um.authenticate("d", "pw2") is True


def test_delete_user(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    um.create_user("e", "pw")
    assert um.delete_user("e") is True
    assert "e" not in um.users


def test_migration_from_plaintext(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    with open(f, "w", encoding="utf-8") as fh:
        json.dump({"u": {"password": "plaintext", "persona": "default"}}, fh)
    um = UserManager(users_file=f)
    assert "password" not in um.users["u"]
    assert "password_hash" in um.users["u"]
    assert um.authenticate("u", "plaintext") is True


def test_list_users(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    um.create_user("x", "pw")
    users = um.list_users()
    assert "x" in users


def test_update_user_password_via_update(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    um.create_user("g", "pw")  # Test password
    um.update_user("g", password="new")  # Test password
    assert um.authenticate("g", "new") is True


def test_authenticate_missing_hash(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    with open(f, "w", encoding="utf-8") as fh:
        json.dump({"h": {"role": "user"}}, fh)
    um = UserManager(users_file=f)
    assert um.authenticate("h", "pw") is False


def test_get_nonexistent_user(tmpdir):
    f = os.path.join(tmpdir, "users.json")
    um = UserManager(users_file=f)
    assert um.get_user_data("zzz") == {}
