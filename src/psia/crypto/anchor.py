"""
Ed25519 cryptographic anchor for PSIA block sealing (Stage 6).

Signs the block_hash with an Ed25519 private key.  If no key material is
available the anchor runs in "software-only" mode: the signature field is
left empty and a warning is emitted — the pipeline still completes.  This
ensures the pipeline never silently fails due to missing key material while
making the absence clearly visible in the SealedFrame.

Key Rotation
------------
Call ``anchor.rotate_key(new_seed_hex)`` to install a new signing key.  The
previous key is retired to the key history and can still verify signatures
produced under it.  Each key version gets a monotonically incrementing
``key_id`` (starting at 0).  Rotation events are written to the in-process
rotation log (``anchor.rotation_log``) and optionally to a JSONL file set
via the ``PSIA_ED25519_ROTATION_LOG`` environment variable.

Verification with history
-------------------------
``anchor.verify_with_history(data_hex, sig_hex)`` tries the current public
key first, then all retired public keys in reverse-chronological order.
Returns ``(verified: bool, matched_key_id: int | None)``.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger("psia.crypto.anchor")

_PRIVATE_KEY_ENV = "PSIA_ED25519_PRIVATE_KEY_HEX"
_KEY_FILE_ENV = "PSIA_ED25519_KEY_FILE"
_ROTATION_LOG_ENV = "PSIA_ED25519_ROTATION_LOG"


# ============================================================
# Key Version Record
# ============================================================


@dataclass
class KeyVersion:
    """Immutable snapshot of a single key epoch."""

    key_id: int
    public_key_hex: str
    activated_at: str      # ISO 8601 UTC
    retired_at: str = ""   # ISO 8601 UTC, empty if still active
    rotation_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# Ed25519Anchor
# ============================================================


class Ed25519Anchor:
    """
    Ed25519 signing anchor with key rotation and historical verification.

    Key loading order (initial):
      1. Hex-encoded 32-byte seed from env var PSIA_ED25519_PRIVATE_KEY_HEX
      2. File path from PSIA_ED25519_KEY_FILE env var
      3. Software-only mode (signature = "")

    Rotation:
      anchor.rotate_key(new_seed_hex, reason="scheduled")
        → installs new key as key_id N+1
        → retires current key to history

    Historical verification:
      ok, key_id = anchor.verify_with_history(data_hex, sig_hex)
        → tries active key first, then all retired keys
    """

    def __init__(self) -> None:
        self._private_key = None
        self._current_version: Optional[KeyVersion] = None
        self._key_history: list[KeyVersion] = []       # retired keys, oldest first
        self._next_key_id: int = 0
        self.rotation_log: list[dict] = []             # in-process rotation events

        self._rotation_log_path: Optional[Path] = None
        rlog = os.environ.get(_ROTATION_LOG_ENV, "")
        if rlog:
            self._rotation_log_path = Path(rlog)
            self._rotation_log_path.parent.mkdir(parents=True, exist_ok=True)

        self._load_key()

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    def _make_ed25519_private(self, seed: bytes):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        return Ed25519PrivateKey.from_private_bytes(seed)

    def _pub_hex(self, private_key) -> str:
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        return private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    def _now_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append_rotation_log(self, event: dict) -> None:
        self.rotation_log.append(event)
        if self._rotation_log_path:
            try:
                with open(self._rotation_log_path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(event) + "\n")
            except Exception as exc:
                log.warning("PSIA anchor: rotation log write failed: %s", exc)

    # ----------------------------------------------------------
    # Initial key load
    # ----------------------------------------------------------

    def _load_key(self) -> None:
        try:
            seed_hex = os.environ.get(_PRIVATE_KEY_ENV, "")
            if seed_hex:
                seed = bytes.fromhex(seed_hex)
                priv = self._make_ed25519_private(seed)
                self._install_key(priv, reason="env_var_load")
                log.info("PSIA Ed25519 anchor loaded from environment (key_id=%d)", self._current_version.key_id)
                return

            key_file = os.environ.get(_KEY_FILE_ENV, "")
            if key_file and os.path.exists(key_file):
                seed = bytes.fromhex(open(key_file).read().strip())
                priv = self._make_ed25519_private(seed)
                self._install_key(priv, reason="file_load")
                log.info(
                    "PSIA Ed25519 anchor loaded from file: %s (key_id=%d)",
                    key_file,
                    self._current_version.key_id,
                )
                return

        except Exception as exc:
            log.warning("PSIA Ed25519 anchor unavailable: %s — running unsigned", exc)
            return

        log.warning(
            "PSIA Ed25519 anchor: no key material found (%s env var not set). "
            "SealedFrame will have empty signature.",
            _PRIVATE_KEY_ENV,
        )

    def _install_key(self, private_key, reason: str = "") -> None:
        """Assign private_key as the active key; retire the previous one if any."""
        now = self._now_utc()

        # Retire current key into history
        if self._current_version is not None:
            retired = KeyVersion(
                key_id=self._current_version.key_id,
                public_key_hex=self._current_version.public_key_hex,
                activated_at=self._current_version.activated_at,
                retired_at=now,
                rotation_reason=self._current_version.rotation_reason,
            )
            self._key_history.append(retired)

        # Install new key
        kid = self._next_key_id
        self._next_key_id += 1
        self._private_key = private_key
        self._current_version = KeyVersion(
            key_id=kid,
            public_key_hex=self._pub_hex(private_key),
            activated_at=now,
            rotation_reason=reason,
        )

        event = {
            "event": "key_installed",
            "key_id": kid,
            "public_key_hex": self._current_version.public_key_hex,
            "activated_at": now,
            "reason": reason,
        }
        self._append_rotation_log(event)

    # ----------------------------------------------------------
    # Public API — properties
    # ----------------------------------------------------------

    @property
    def public_key_hex(self) -> str:
        """Hex public key of the currently active signing key, or '' if unavailable."""
        if self._current_version is None:
            return ""
        return self._current_version.public_key_hex

    @property
    def key_id(self) -> int:
        """Integer version counter of the currently active key (0-based)."""
        if self._current_version is None:
            return -1
        return self._current_version.key_id

    @property
    def available(self) -> bool:
        return self._private_key is not None

    @property
    def key_history(self) -> list[dict]:
        """Retired key versions as list of dicts (oldest first)."""
        return [v.to_dict() for v in self._key_history]

    @property
    def current_key_info(self) -> dict:
        """Current active key metadata (no private key material)."""
        if self._current_version is None:
            return {"available": False}
        return {**self._current_version.to_dict(), "available": True}

    # ----------------------------------------------------------
    # Key Rotation
    # ----------------------------------------------------------

    def rotate_key(self, new_seed_hex: str, reason: str = "manual_rotation") -> KeyVersion:
        """
        Rotate to a new Ed25519 signing key.

        Parameters
        ----------
        new_seed_hex : str
            Hex-encoded 32-byte Ed25519 seed for the new key.
        reason : str
            Human-readable reason tag stored in the rotation log.
            Examples: "scheduled_90d", "compromise_response", "hsm_migration".

        Returns
        -------
        KeyVersion
            The newly activated key version record.

        Raises
        ------
        ValueError
            If the seed is not a valid 32-byte Ed25519 seed.
        """
        try:
            seed = bytes.fromhex(new_seed_hex)
            if len(seed) != 32:
                raise ValueError(f"Ed25519 seed must be 32 bytes, got {len(seed)}")
            priv = self._make_ed25519_private(seed)
        except Exception as exc:
            log.error("PSIA anchor: key rotation failed (bad seed): %s", exc)
            raise ValueError(f"Invalid Ed25519 seed: {exc}") from exc

        old_key_id = self._current_version.key_id if self._current_version else None
        self._install_key(priv, reason=reason)
        new_version = self._current_version

        event = {
            "event": "key_rotated",
            "old_key_id": old_key_id,
            "new_key_id": new_version.key_id,
            "new_public_key_hex": new_version.public_key_hex,
            "rotated_at": new_version.activated_at,
            "reason": reason,
        }
        self._append_rotation_log(event)

        log.info(
            "PSIA anchor: key rotated — old key_id=%s → new key_id=%d (%s)",
            old_key_id,
            new_version.key_id,
            reason,
        )
        return new_version

    # ----------------------------------------------------------
    # Signing
    # ----------------------------------------------------------

    def sign(self, data_hex: str) -> str:
        """
        Sign data_hex with the current active key.

        Returns
        -------
        str
            Hex Ed25519 signature, or '' if no key is available.
        """
        if self._private_key is None:
            return ""
        try:
            sig = self._private_key.sign(bytes.fromhex(data_hex))
            return sig.hex()
        except Exception as exc:
            log.error("PSIA anchor signing failed: %s", exc)
            return ""

    # ----------------------------------------------------------
    # Verification
    # ----------------------------------------------------------

    @staticmethod
    def verify(data_hex: str, signature_hex: str, public_key_hex: str) -> bool:
        """
        Verify an Ed25519 signature against a specific public key.
        Returns False if signature or key is empty, or if verification fails.
        """
        if not signature_hex or not public_key_hex:
            return False
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

            pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
            pub.verify(bytes.fromhex(signature_hex), bytes.fromhex(data_hex))
            return True
        except Exception:
            return False

    def verify_with_history(
        self, data_hex: str, signature_hex: str
    ) -> tuple[bool, Optional[int]]:
        """
        Verify a signature against the current key and all retired keys.

        Tries the active key first (O(1) common case), then retired keys in
        reverse-chronological order (most recent retired → oldest).

        Parameters
        ----------
        data_hex : str
            Hex-encoded data that was signed.
        signature_hex : str
            Hex-encoded Ed25519 signature to verify.

        Returns
        -------
        (verified: bool, matched_key_id: int | None)
            If verified is True, matched_key_id is the key_id that produced
            the valid signature.  If False, matched_key_id is None.
        """
        if not signature_hex:
            return False, None

        # Try current active key
        if self._current_version and self.verify(
            data_hex, signature_hex, self._current_version.public_key_hex
        ):
            return True, self._current_version.key_id

        # Try retired keys, most recent first
        for retired in reversed(self._key_history):
            if self.verify(data_hex, signature_hex, retired.public_key_hex):
                return True, retired.key_id

        return False, None
