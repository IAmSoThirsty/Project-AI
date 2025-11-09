"""CLI tool to preview or apply migration of plaintext passwords to bcrypt hashes.

Usage:
    python tools/migrate_users.py [--users-file path] [--apply]

If --apply is not provided, the script prints what it would change. If --apply
is provided, it will perform the migration and overwrite the users file.
"""
import argparse
import json
import os
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def preview_migration(users_path: str):
    with open(users_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    to_migrate = []
    for uname, udata in data.items():
        if isinstance(udata, dict) and 'password' in udata and 'password_hash' not in udata:
            to_migrate.append(uname)
    return data, to_migrate


def apply_migration(users_path: str):
    data, to_migrate = preview_migration(users_path)
    if not to_migrate:
        print('No plaintext passwords to migrate.')
        return 0
    for uname in to_migrate:
        pw = data[uname].pop('password')
        data[uname]['password_hash'] = pwd.hash(pw)
        print(f"Migrated {uname}")
    # backup
    bak = users_path + '.bak'
    try:
        os.replace(users_path, bak)
    except Exception:
        # fallback to copy
        import shutil
        shutil.copy(users_path, bak)
    with open(users_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Migration applied. Backup saved to {bak}")
    return len(to_migrate)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--users-file', default='src/app/users.json', help='Path to users.json')
    parser.add_argument('--apply', action='store_true', help='Apply the migration')
    args = parser.parse_args()

    if not os.path.exists(args.users_file):
        print('Users file not found:', args.users_file)
        raise SystemExit(1)

    data, to_migrate = preview_migration(args.users_file)
    if not to_migrate:
        print('No users to migrate.')
        raise SystemExit(0)

    print('Users to migrate:')
    for u in to_migrate:
        print(' -', u)

    if args.apply:
        n = apply_migration(args.users_file)
        print(f'Migrated {n} users')
    else:
        print('\nRun with --apply to perform the migration (this will back up the file).')
