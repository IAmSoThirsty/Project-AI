import json
from app.core.user_manager import UserManager


def test_migration_and_authentication(tmp_path):
    # create a users.json with plaintext passwords
    users = {
        "alice": {"password": "alicepw", "persona": "friendly"},
        "bob": {"password": "bobpw", "persona": "friendly"}
    }
    f = tmp_path / "users.json"
    with open(f, 'w', encoding='utf-8') as fh:
        json.dump(users, fh)

    # load via UserManager pointing to tmp file
    um = UserManager(users_file=str(f))

    # after init, plaintext should be migrated to password_hash
    assert 'alice' in um.users
    assert 'password_hash' in um.users['alice']
    assert 'password' not in um.users['alice']

    # authentication should succeed with original password
    assert um.authenticate('alice', 'alicepw') is True
    assert um.authenticate('bob', 'wrongpw') is False

    # set new password and authenticate
    um.set_password('bob', 'newbob')
    assert um.authenticate('bob', 'newbob') is True

    # delete user
    um.delete_user('alice')
    assert 'alice' not in um.users


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
