import json

from app.core.command_override import CommandOverrideSystem


def test_sha256_to_bcrypt_migration(tmp_path):
    # create data dir
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create legacy config with sha256 password for migration testing
    # NOTE: "s3cret!" is a test password only - not used in production
    password = "s3cret!"
    # Precomputed legacy SHA-256 of "s3cret!", do not compute password hashes with SHA256 in new code
    legacy_hash = "98830ed5c6d7d22ef9dcf6a236aa93a3c81f57ea5483cfa0409643bd5be5b92e"
    config = {"master_password_hash": legacy_hash, "safety_protocols": {}}
    cfg_file = data_dir / "command_override_config.json"
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(config, f)

    # instantiate system pointing to tmp data dir
    sys = CommandOverrideSystem(data_dir=str(data_dir))

    # authenticate using legacy password
    assert sys.authenticate(password) is True
    # after authentication, stored hash should no longer be the legacy hex
    with open(cfg_file, encoding="utf-8") as f:
        new_cfg = json.load(f)
    new_hash = new_cfg.get("master_password_hash")
    assert new_hash is not None
    assert new_hash != legacy_hash
    # subsequent authenticate should still work
    assert sys.authenticate(password) is True


def test_set_and_verify_bcrypt(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    sys = CommandOverrideSystem(data_dir=str(data_dir))
    assert sys.set_master_password("mystrongpassword") is True
    assert sys.authenticate("mystrongpassword") is True
    assert sys.authenticate("wrong") is False
