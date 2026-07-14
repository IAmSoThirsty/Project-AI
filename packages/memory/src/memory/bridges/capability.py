"""Capability bridge: CCMA ``CapabilityChecker`` -> Beginnings ``CapabilityAuthority``.

CCMA keeps authority and capability separate ("Capability without authority is
prohibited. Authority without capability is ineffective."). This module is the
*real* ``CapabilityChecker`` implementation: it verifies a signed HMAC capability
token issued by ``capability.CapabilityAuthority`` (T.A.R.L.) for the exact
``(subject, capability)`` action.

A capability token is a single opaque string scoped to ``(subject, operation,
resource)``. CCMA's ``capability`` string maps onto ``operation``/``resource``;
we encode it as the operation and use the subject as the resource owner so the
token's exact-scope HMAC can be verified without reimplementing crypto here.
"""

from __future__ import annotations

from capability.authority import CapabilityAuthority, ScopeMismatchError

from memory.ccma.interfaces import CapabilityChecker, SafeHaltError


class TARLCapabilityChecker(CapabilityChecker):
    """Verify CCMA capability checks against a real ``CapabilityAuthority``.

    ``capability`` is the T.A.R.L. capability name. We require a token that was
    issued for ``operation=capability`` and ``resource=subject`` so a token is
    bound to both the action and the actor. Any HMAC failure, expiry, replay,
    scope mismatch, or revocation raises ``SafeHaltError`` (fail-closed).
    """

    def __init__(self, authority: CapabilityAuthority) -> None:
        self._authority = authority

    def check_capability(self, subject: str, capability: str) -> bool:
        # The token must be supplied by the caller's environment. CCMA's
        # pipeline only knows ``subject`` + ``capability``; the actual signed
        # token is resolved from the ambient T.A.R.L. session. If no token is
        # present for this subject/capability, we deny by default.
        token = _resolve_token(subject, capability)
        if token is None:
            raise SafeHaltError(
                f"No T.A.R.L. capability token for subject={subject!r} "
                f"capability={capability!r}. Denying by default."
            )
        try:
            self._authority.consume(token, subject=subject, operation=capability, resource=subject)
        except ScopeMismatchError as error:
            raise SafeHaltError(f"Capability scope mismatch: {error}") from error
        except Exception as error:  # any auth failure -> fail closed
            raise SafeHaltError(f"Capability check failed: {error}") from error
        return True


def _resolve_token(subject: str, capability: str) -> str | None:
    """Resolve the ambient T.A.R.L. capability token for ``(subject, capability)``.

    This is the one seam left to the deployment: where the live signed token
    lives (env var, local agent session, sidecar). We never fabricate one. The
    default implementation consults ``$CCMA_CAPABILITY_TOKEN`` so a real token
    issued by ``CapabilityAuthority.issue(...)`` can be injected per request.
    """
    import os

    token = os.environ.get("CCMA_CAPABILITY_TOKEN")
    if not token:
        return None
    return token
