"""Authority bridge: CCMA ``AuthorityProvider`` -> Beginnings ``StateRegister``.

CCMA Law II: "Memory Never Grants Authority." The unified graph store and
pipeline never decide authority themselves — they call ``AuthorityProvider``.
This module is the *real* implementation of that interface: it delegates to
``kernel.StateRegister``, which is the constitutional source of truth for
authority in Beginnings (per CCMA's stated seam: "Bridge to STATE_REGISTER /
your Governance authority store").

Nothing here fabricates authority. If the requested scope is not present in the
register (or the register is not wired), it raises ``SafeHaltError`` — deny by
default, exactly like the CCMA fail-closed contract.
"""

from __future__ import annotations

import time

from kernel import StateRegister
from memory.ccma.interfaces import AuthorityProvider, AuthorityToken, SafeHaltError


class StateRegisterAuthorityProvider(AuthorityProvider):
    """Resolve CCMA authority checks against a ``StateRegister``.

    The register's values are treated as the authority record: a key
    ``"authority:<scope>"`` carrying a truthy entry means that scope has been
    constitutionally established. ``protected_override`` is granted only when an
    explicit ``"authority:protected_override:<scope>"`` entry is set — CCMA
    treats unexpiring / blanket protected authority as a red flag, so it must
    be established deliberately, never inferred.
    """

    def __init__(self, register: StateRegister) -> None:
        self._register = register

    def check_authority(self, subject: str, scope: str) -> AuthorityToken:
        values = dict(self._register.snapshot().values)
        grant = values.get(f"authority:{scope}")
        if not grant:
            raise SafeHaltError(
                f"StateRegister denies authority: no grant for scope={scope!r} "
                f"(subject={subject!r}). Authority is always established, never inferred."
            )
        protected_override = bool(values.get(f"authority:protected_override:{scope}"))
        now = time.time()
        # Authority established via the register is granted without an explicit
        # expiry by default; CCMA warns this is a red flag, so callers should
        # prefer scopes that are narrow and re-established.
        return AuthorityToken(
            subject=subject,
            scope=scope,
            granted_by="state_register",
            granted_at=now,
            expires_at=None,
            protected_override=protected_override,
        )
