"""PSIA Ed25519 cryptographic provider."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


@dataclass
class Ed25519KeyPair:
    component: str
    key_id: str
    public_key: Ed25519PublicKey
    private_key: Ed25519PrivateKey
    public_key_hex: str
    created_at: str
    purpose: str = "signing"


class Ed25519Provider:
    @staticmethod
    def generate_keypair(
        component: str,
        key_id: str | None = None,
        purpose: str = "signing",
    ) -> Ed25519KeyPair:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        pub_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        pub_hex = pub_bytes.hex()
        kid = key_id if key_id is not None else f"key_{component}_{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        return Ed25519KeyPair(
            component=component,
            key_id=kid,
            public_key=public_key,
            private_key=private_key,
            public_key_hex=pub_hex,
            created_at=created_at,
            purpose=purpose,
        )

    @staticmethod
    def sign(private_key: Ed25519PrivateKey, data: bytes) -> str:
        return private_key.sign(data).hex()

    @staticmethod
    def verify(public_key: Ed25519PublicKey, signature_hex: str, data: bytes) -> bool:
        try:
            sig_bytes = bytes.fromhex(signature_hex)
            public_key.verify(sig_bytes, data)
            return True
        except Exception:
            return False

    @staticmethod
    def sign_string(private_key: Ed25519PrivateKey, text: str) -> str:
        return Ed25519Provider.sign(private_key, text.encode("utf-8"))

    @staticmethod
    def verify_string(public_key: Ed25519PublicKey, signature_hex: str, text: str) -> bool:
        return Ed25519Provider.verify(public_key, signature_hex, text.encode("utf-8"))

    @staticmethod
    def serialize_public_key(public_key: Ed25519PublicKey) -> str:
        return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    @staticmethod
    def load_public_key(hex_str: str) -> Ed25519PublicKey:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey as _PK
        raw = bytes.fromhex(hex_str)
        return _PK.from_public_bytes(raw)


class KeyStore:
    def __init__(self) -> None:
        self._store: dict[str, Ed25519KeyPair] = {}

    @property
    def components(self) -> list[str]:
        return list(self._store.keys())

    @property
    def count(self) -> int:
        return len(self._store)

    def register(self, kp: Ed25519KeyPair) -> None:
        if kp.component in self._store:
            raise ValueError(f"already registered: {kp.component}")
        self._store[kp.component] = kp

    def get(self, component: str) -> Ed25519KeyPair | None:
        return self._store.get(component)

    def get_private_key(self, component: str) -> Any | None:
        kp = self._store.get(component)
        return kp.private_key if kp else None

    def get_public_key(self, component: str) -> Any | None:
        kp = self._store.get(component)
        return kp.public_key if kp else None

    def sign_as(self, component: str, data: bytes) -> str:
        kp = self._store.get(component)
        if kp is None:
            raise KeyError(f"No key registered: {component}")
        return Ed25519Provider.sign(kp.private_key, data)

    def verify_from(self, component: str, signature_hex: str, data: bytes) -> bool:
        kp = self._store.get(component)
        if kp is None:
            return False
        return Ed25519Provider.verify(kp.public_key, signature_hex, data)

    def public_key_registry(self) -> dict[str, str]:
        return {name: kp.public_key_hex for name, kp in self._store.items()}
