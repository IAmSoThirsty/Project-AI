"""Tests for cerberus.security.modules.encryption.

Honest scope: covers key generation/persistence/rotation, encrypt/decrypt
round-trips (bytes, string, JSON, file, multi-key), the naive-timestamp
coercion for upstream-written key files, and error paths (no active key,
unknown key id). Cryptographic strength of Fernet/PBKDF2 is assumed, not
benchmarked; POSIX file-permission bits are not asserted (suite runs on
Windows).
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from cerberus.security import EncryptionKey, EncryptionManager, KeyManager


@pytest.fixture
def key_manager(tmp_path: Path) -> KeyManager:
    return KeyManager(key_dir=tmp_path / "keys")


@pytest.fixture
def manager(key_manager: KeyManager) -> EncryptionManager:
    return EncryptionManager(key_manager)


class TestKeyManager:
    def test_construction_guarantees_active_key(self, key_manager: KeyManager) -> None:
        active = key_manager.get_active_key()
        assert active is not None
        assert active.is_active
        assert active.created_at.tzinfo is not None

    def test_keys_persist_across_instances(self, tmp_path: Path) -> None:
        first = KeyManager(key_dir=tmp_path / "keys")
        active = first.get_active_key()
        assert active is not None

        second = KeyManager(key_dir=tmp_path / "keys")
        reloaded = second.get_key(active.key_id)
        assert reloaded is not None
        assert reloaded.key_data == active.key_data
        assert reloaded.created_at == active.created_at

    def test_rotation_deactivates_old_keys_but_keeps_them(self, key_manager: KeyManager) -> None:
        old = key_manager.get_active_key()
        assert old is not None

        new = key_manager.rotate_keys()
        assert new.key_id != old.key_id
        assert key_manager.get_active_key() is not None
        active = key_manager.get_active_key()
        assert active is not None and active.key_id == new.key_id

        retained = key_manager.get_key(old.key_id)
        assert retained is not None
        assert not retained.is_active
        assert len(key_manager.get_all_keys()) == 2

    def test_check_rotation_needed_false_for_fresh_key(self, key_manager: KeyManager) -> None:
        assert key_manager.check_rotation_needed() is False

    def test_check_rotation_needed_true_when_expired(self, tmp_path: Path) -> None:
        km = KeyManager(key_dir=tmp_path / "keys", rotation_days=0)
        assert km.check_rotation_needed() is True

    def test_naive_upstream_timestamps_coerced_to_utc(self, tmp_path: Path) -> None:
        key_dir = tmp_path / "keys"
        km = KeyManager(key_dir=key_dir)
        active = km.get_active_key()
        assert active is not None

        # Rewrite the key file with naive timestamps, as upstream writes them.
        key_file = key_dir / "keys.json"
        data = json.loads(key_file.read_text(encoding="utf-8"))
        for entry in data["keys"]:
            entry["created_at"] = "2026-01-01T00:00:00"
            entry["expires_at"] = "2099-01-01T00:00:00"
        key_file.write_text(json.dumps(data), encoding="utf-8")

        reloaded = KeyManager(key_dir=key_dir)
        key = reloaded.get_key(active.key_id)
        assert key is not None
        assert key.created_at == datetime(2026, 1, 1, tzinfo=UTC)
        # Aware comparison must not raise (naive would).
        assert reloaded.check_rotation_needed() is False

    def test_derive_key_deterministic_for_same_salt(self, key_manager: KeyManager) -> None:
        salt = b"\x01" * 16
        first = key_manager.derive_key_from_password("correct horse", salt=salt)
        second = key_manager.derive_key_from_password("correct horse", salt=salt)
        assert first == second
        assert first != key_manager.derive_key_from_password("battery staple", salt=salt)


class TestEncryptionManager:
    def test_bytes_round_trip(self, manager: EncryptionManager) -> None:
        payload = manager.encrypt(b"secret bytes")
        assert set(payload) == {"key_id", "data"}
        assert manager.decrypt(payload) == b"secret bytes"

    def test_string_and_json_round_trip(self, manager: EncryptionManager) -> None:
        assert manager.decrypt_string(manager.encrypt_string("héllo")) == "héllo"
        doc = {"verdict": "ALLOW", "n": 3}
        assert manager.decrypt_json(manager.encrypt_json(doc)) == doc

    def test_file_round_trip(self, manager: EncryptionManager, tmp_path: Path) -> None:
        source = tmp_path / "plain.bin"
        source.write_bytes(b"\x00\x01file-content\xff")
        envelope = tmp_path / "cipher.json"
        restored = tmp_path / "restored.bin"

        manager.encrypt_file(source, envelope)
        assert json.loads(envelope.read_text(encoding="utf-8"))["key_id"]
        manager.decrypt_file(envelope, restored)
        assert restored.read_bytes() == source.read_bytes()

    def test_unknown_key_id_rejected(self, manager: EncryptionManager) -> None:
        with pytest.raises(ValueError, match="Encryption key not found"):
            manager.decrypt({"key_id": "no-such-key", "data": ""})

    def test_no_active_key_rejected(self, manager: EncryptionManager) -> None:
        for key in manager.key_manager.get_all_keys():
            key.is_active = False
        with pytest.raises(ValueError, match="No active encryption key"):
            manager.encrypt(b"data")

    def test_old_data_decryptable_after_rotation(self, manager: EncryptionManager) -> None:
        payload = manager.encrypt(b"pre-rotation")
        manager.key_manager.rotate_keys()
        assert manager.decrypt(payload) == b"pre-rotation"

        rotated = manager.rotate_encrypted_data(payload)
        assert rotated["key_id"] != payload["key_id"]
        assert manager.decrypt(rotated) == b"pre-rotation"

    def test_multi_key_encrypt_decryptable_with_active_key(
        self, manager: EncryptionManager
    ) -> None:
        manager.key_manager.rotate_keys()
        payload = manager.encrypt_with_multi_key(b"multi")
        assert len(payload["key_ids"]) == 2
        # MultiFernet encrypts with the first key; round-trip via single-key path.
        first_key = manager.key_manager.get_all_keys()[0]
        assert manager.decrypt({"key_id": first_key.key_id, "data": payload["data"]}) == b"multi"


def test_encryption_key_dataclass_defaults() -> None:
    key = EncryptionKey(key_id="k", key_data=b"d", created_at=datetime.now(UTC))
    assert key.expires_at is None
    assert key.is_active
