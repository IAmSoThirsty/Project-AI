from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

try:
    import bcrypt
except Exception:
    bcrypt = None


def upgrade_in_db(db_path: Path) -> int:
    if bcrypt is None:
        raise RuntimeError("bcrypt is required to run this upgrade script")
    conn = sqlite3.connect(db_path)
    conn.cursor()
    # This is app-specific: assume overrides stored in a JSON file under overrides/audit.json
    conn.close()
    return 0


def upgrade_in_file(audit_path: Path) -> int:
    if bcrypt is None:
        raise RuntimeError("bcrypt is required to run this upgrade script")
    if not audit_path.exists():
        print("Audit file not found: ", audit_path)
        return 1
    s = audit_path.read_text(encoding="utf-8")
    try:
        data = json.loads(s)
    except Exception:
        print("Could not parse audit JSON")
        return 2

    changed = False
    if isinstance(data, list):
        for entry in data:
            if entry.get("type") == "credentials" and entry.get("password_hash"):
                ph = entry["password_hash"]
                # Detect legacy pbkdf2 format (iterations$salt$hash)
                if isinstance(ph, str) and ph.count("$") == 2:
                    # fallback: we cannot recover original password; require admin to run set_password()
                    # Mark entry to indicate manual migration required
                    entry["migration_required"] = True
                    changed = True
    if changed:
        backup = audit_path.with_suffix(".bak.json")
        audit_path.rename(backup)
        audit_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Migration markers written; backup saved to {backup}")
    else:
        print("No entries requiring migration were found")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgrade CommandOverride password hashes to bcrypt or mark for manual migration")
    parser.add_argument("--audit-file", default="data/overrides/audit.json")
    args = parser.parse_args()
    raise SystemExit(upgrade_in_file(Path(args.audit_file)))
