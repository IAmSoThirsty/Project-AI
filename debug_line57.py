import os
import tempfile

# Remove FERNET_KEY
original_key = os.environ.get("FERNET_KEY")
os.environ.pop("FERNET_KEY", None)

print(f"FERNET_KEY after pop: {os.environ.get('FERNET_KEY')}")

with tempfile.TemporaryDirectory() as tmpdir:
    from app.core.user_manager import UserManager

    users_file = os.path.join(tmpdir, "users.json")
    manager = UserManager(users_file=users_file)

    print(f"Cipher suite created: {manager.cipher_suite is not None}")
    print("Test completed successfully")

# Restore
if original_key:
    os.environ["FERNET_KEY"] = original_key
