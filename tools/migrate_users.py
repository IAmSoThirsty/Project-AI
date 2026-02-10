"""CLI tool to preview or apply migration of plaintext passwords.

Converts plaintext passwords in a users JSON file to bcrypt hashes.

Usage:
    python tools/migrate_users.py [--users-file path] [--apply]

If --apply is not provided, the script prints what it would change. If
--apply is provided, it will perform the migration and overwrite the
users file.
"""

import argparse
import json
import os

from passlib.context import CryptContext

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def preview_migration(users_path: str):
    with open(users_path, encoding="utf-8") as f:
        data = json.load(f)
    to_migrate = []
    for uname, udata in data.items():
        has_password = isinstance(udata, dict) and "password" in udata
        has_hash = "password_hash" in udata if isinstance(udata, dict) else False
        if has_password and not has_hash:
            to_migrate.append(uname)
    return data, to_migrate


def apply_migration(users_path: str):
    data, to_migrate = preview_migration(users_path)
    if not to_migrate:
        print("No plaintext passwords to migrate.")
        return 0
    for uname in to_migrate:
        pw = data[uname].pop("password")
        data[uname]["password_hash"] = pwd.hash(pw)
        print(f"Migrated {uname}")
    # backup
    bak = users_path + ".bak"
    try:
        os.replace(users_path, bak)
    except Exception:
        # fallback to copy
        import shutil

        shutil.copy(users_path, bak)
    with open(users_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Migration applied. Backup saved to {bak}")
    return len(to_migrate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--users-file",
        default="src/app/users.json",
        help="Path to users.json (will try fallback to ./users.json if missing)",
    )
    parser.add_argument("--apply", action="store_true", help="Apply the migration")
    args = parser.parse_args()

    # If provided path doesn't exist, try common fallbacks before failing
    users_path = args.users_file
    if not os.path.exists(users_path):
        alt = os.path.join(os.getcwd(), "users.json")
        if os.path.exists(alt):
            users_path = alt
        else:
            alt2 = os.path.join("src", "app", "users.json")
            if os.path.exists(alt2):
                users_path = alt2
    if not os.path.exists(users_path):
        print("Users file not found. Tried:", args.users_file, users_path)
        raise SystemExit(1)

    data, to_migrate = preview_migration(users_path)
    if not to_migrate:
        print("No users to migrate.")
        raise SystemExit(0)

    print("Users to migrate:")
    for u in to_migrate:
        print(" -", u)

    if args.apply:
        n = apply_migration(users_path)
        print(f"Migrated {n} users")
    else:
        msg = "\nRun with --apply to perform the migration "
        msg += "(this will back up the file)."
        print(msg)
