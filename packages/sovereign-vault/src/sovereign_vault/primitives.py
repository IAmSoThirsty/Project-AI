"""
sovereign_vault.primitives

Low-level crypto only. No policy decisions live here.

Primitive choices are pinned to match the existing CBCC stack (HKDF-SHA-512
for derivation, XChaCha20-Poly1305 for sealing, Ed25519 for signatures) so
this module composes with CBCC rather than introducing a second, divergent
crypto profile.
"""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass

import nacl.bindings as sodium
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

XCHACHA_KEY_LEN = sodium.crypto_aead_xchacha20poly1305_ietf_KEYBYTES  # 32
XCHACHA_NONCE_LEN = sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES  # 24


def hkdf_sha512(key_material: bytes, info: bytes, length: int = 32, salt: bytes = b"") -> bytes:
    """Deterministic subkey derivation. Same (key_material, info) always
    yields the same output — that determinism is required so independent
    branches of the key hierarchy never accidentally collide, and so a
    derivation can be re-verified without storing the derived key."""
    if not key_material:
        raise ValueError("hkdf_sha512: empty key_material")
    if not info:
        raise ValueError(
            "hkdf_sha512: info label is required and must be non-empty "
            "(prevents cross-branch key reuse)"
        )
    return HKDF(
        algorithm=hashes.SHA512(),
        length=length,
        salt=salt or None,
        info=info,
    ).derive(key_material)


def combine_factors(*factors: bytes, info: bytes) -> bytes:
    """
    AND-combine of N independent factors into one 32-byte key.

    This is deliberately NOT k-of-n threshold sharing — every factor listed
    here is mandatory (e.g. USB token share AND TPM-sealed share AND
    operator secret). If you want k-of-n recoverability, that lives at the
    recovery-quorum layer (recovery.py), not here. Conflating the two is
    the exact "USB token as root" mistake this module exists to avoid.
    """
    if len(factors) < 2:
        raise ValueError(
            "combine_factors requires at least 2 independent factors; "
            "a single factor is a root, not a combination"
        )
    for i, f in enumerate(factors):
        if not f or len(f) < 16:
            raise ValueError(
                f"combine_factors: factor {i} missing or too short "
                f"(<16 bytes) to be a real secret/share"
            )
    material = b"\x00".join(factors)  # 0x00 separator: no factor may contain it unescaped in
    # practice this is fine because factors are raw key bytes, not attacker-controlled text
    return hkdf_sha512(material, info=info, length=32)


def seal(key: bytes, plaintext: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    """XChaCha20-Poly1305 AEAD seal. Returns (nonce, ciphertext_with_tag)."""
    if len(key) != XCHACHA_KEY_LEN:
        raise ValueError(f"seal: key must be {XCHACHA_KEY_LEN} bytes, got {len(key)}")
    nonce = os.urandom(XCHACHA_NONCE_LEN)
    ct = sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(plaintext, aad or None, nonce, key)
    return nonce, ct


def unseal(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
    """XChaCha20-Poly1305 AEAD open. Raises on any auth failure — never
    returns partial or best-effort plaintext."""
    if len(key) != XCHACHA_KEY_LEN:
        raise ValueError(f"unseal: key must be {XCHACHA_KEY_LEN} bytes, got {len(key)}")
    if len(nonce) != XCHACHA_NONCE_LEN:
        raise ValueError(f"unseal: nonce must be {XCHACHA_NONCE_LEN} bytes, got {len(nonce)}")
    return sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(ciphertext, aad or None, nonce, key)


@dataclass(frozen=True)
class SigningIdentity:
    """Wraps an Ed25519 keypair used for audit-chain / checkpoint /
    recovery-approver signatures."""

    private_key: Ed25519PrivateKey

    @staticmethod
    def generate() -> SigningIdentity:
        return SigningIdentity(Ed25519PrivateKey.generate())

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self.private_key.public_key()

    def public_bytes(self) -> bytes:
        from cryptography.hazmat.primitives import serialization

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def sign(self, message: bytes) -> bytes:
        return self.private_key.sign(message)


def verify_signature(public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
    """Never raises on a bad signature — returns False. Callers must treat
    False as authoritative denial, not as 'try something else'."""
    try:
        pub = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        pub.verify(signature, message)
        return True
    except (InvalidSignature, ValueError):
        return False


def pack_u64(n: int) -> bytes:
    return struct.pack(">Q", n)
