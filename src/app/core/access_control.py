from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger(__name__)


class AccessControlManager:
    """Simple role-based access control manager with persistent storage.

    - Users stored in `data/access_control.json` as {user: [roles]}
    - Default 'system' user has 'integrator' role to allow automated operations.
    """

    STORAGE = "data/access_control.json"

    def __init__(self) -> None:
        os.makedirs(os.path.dirname(self.STORAGE), exist_ok=True)
        self._users: dict[str, list[str]] = {}
        self._load()
        # Ensure default system user
        if "system" not in self._users:
            self._users["system"] = ["integrator", "expert"]
            self._save()

    def _load(self) -> None:
        try:
            if os.path.exists(self.STORAGE):
                with open(self.STORAGE, encoding="utf-8") as f:
                    self._users = json.load(f)
        except Exception:
            logger.exception("Failed to load access control storage")
            self._users = {}

    def _save(self) -> None:
        try:
            with open(self.STORAGE, "w", encoding="utf-8") as f:
                json.dump(self._users, f, indent=2)
        except Exception:
            logger.exception("Failed to save access control storage")

    def add_user(self, user: str, roles: list[str] | None = None) -> None:
        self._users[user] = roles or []
        self._save()

    def grant_role(self, user: str, role: str) -> None:
        self._users.setdefault(user, [])
        if role not in self._users[user]:
            self._users[user].append(role)
            self._save()

    def revoke_role(self, user: str, role: str) -> None:
        if user in self._users and role in self._users[user]:
            self._users[user].remove(role)
            self._save()

    def has_role(self, user: str, role: str) -> bool:
        return role in self._users.get(user, [])


# singleton
_manager: AccessControlManager | None = None


def get_access_control() -> AccessControlManager:
    global _manager
    if _manager is None:
        _manager = AccessControlManager()
    return _manager
