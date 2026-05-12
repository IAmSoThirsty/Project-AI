"""
Ed25519 cryptographic anchor for PSIA block sealing (Stage 6).

Signs the block_hash with an Ed25519 private key.  If no key material is
available the anchor runs in "software-only" mode: the signature field is
left empty and a warning is emitted — the pipeline still completes.  This
ensures the pipeline never silently fails due to missing key material while
making the absence clearly visible in the SealedFrame.
"""

from __future__ import annotations

import logging
import os

log = logging.getLogger("psia.crypto.anchor")

_PRIVATE_KEY_ENV = "PSIA_ED25519_PRIVATE_KEY_HEX"


class Ed25519Anchor:
    """
    Ed25519 signing anchor.

    Key loading order:
      1. Hex-encoded 32-byte seed from env var PSIA_ED25519_PRIVATE_KEY_HEX
      2. File path from PSIA_ED25519_KEY_FILE env var
      3. Software-only mode (signature = "")

    Usage:
        anchor = Ed25519Anchor()
        sig_hex = anchor.sign(block_hash_hex)
        ok = Ed25519Anchor.verify(block_hash_hex, sig_hex, public_key_hex)
    """

    def __init__(self) -> None:
        self._private_key = None
        self._public_key_hex = ""
        self._load_key()

    def _load_key(self) -> None:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

            seed_hex = os.environ.get(_PRIVATE_KEY_ENV, "")
            if seed_hex:
                seed = bytes.fromhex(seed_hex)
                self._private_key = Ed25519PrivateKey.from_private_bytes(seed)
                pub = self._private_key.public_key()
                self._public_key_hex = pub.public_bytes(
                    Encoding.Raw, PublicFormat.Raw
                ).hex()
                log.info("PSIA Ed25519 anchor loaded from environment")
                return

            key_file = os.environ.get("PSIA_ED25519_KEY_FILE", "")
            if key_file and os.path.exists(key_file):
                seed = bytes.fromhex(open(key_file).read().strip())
                self._private_key = Ed25519PrivateKey.from_private_bytes(seed)
                pub = self._private_key.public_key()
                self._public_key_hex = pub.public_bytes(
                    Encoding.Raw, PublicFormat.Raw
                ).hex()
                log.info("PSIA Ed25519 anchor loaded from file: %s", key_file)
                return
        except Exception as exc:
            log.warning("PSIA Ed25519 anchor unavailable: %s — running unsigned", exc)

        log.warning(
            "PSIA Ed25519 anchor: no key material found (%s env var not set). "
            "SealedFrame will have empty signature.",
            _PRIVATE_KEY_ENV,
        )

    @property
    def public_key_hex(self) -> str:
        return self._public_key_hex

    @property
    def available(self) -> bool:
        return self._private_key is not None

    def sign(self, data_hex: str) -> str:
        """Sign data_hex (a hex string) and return hex Ed25519 signature, or '' if unavailable."""
        if self._private_key is None:
            return ""
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

            sig = self._private_key.sign(bytes.fromhex(data_hex))
            return sig.hex()
        except Exception as exc:
            log.error("PSIA anchor signing failed: %s", exc)
            return ""

    @staticmethod
    def verify(data_hex: str, signature_hex: str, public_key_hex: str) -> bool:
        """Verify an Ed25519 signature. Returns False if signature or key is empty."""
        if not signature_hex or not public_key_hex:
            return False
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

            pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
            pub.verify(bytes.fromhex(signature_hex), bytes.fromhex(data_hex))
            return True
        except Exception:
            return False
