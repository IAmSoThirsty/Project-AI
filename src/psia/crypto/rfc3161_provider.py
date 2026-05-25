"""PSIA RFC 3161 local Timestamping Authority."""
from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from psia.crypto.ed25519_provider import Ed25519Provider


def _canonical_bytes(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, default=str).encode("utf-8")


@dataclass
class TimeStampToken:
    version: int
    policy_oid: str
    hash_algorithm: str
    message_imprint: str
    serial_number: int
    gen_time: str
    tsa_name: str
    signature: str
    nonce: str
    tsa_public_key: str = ""

    def _signable(self) -> bytes:
        d = {
            "version": self.version,
            "policy_oid": self.policy_oid,
            "hash_algorithm": self.hash_algorithm,
            "message_imprint": self.message_imprint,
            "serial_number": self.serial_number,
            "gen_time": self.gen_time,
            "tsa_name": self.tsa_name,
            "nonce": self.nonce,
        }
        return hashlib.sha256(_canonical_bytes(d)).digest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "policy_oid": self.policy_oid,
            "hash_algorithm": self.hash_algorithm,
            "message_imprint": self.message_imprint,
            "serial_number": self.serial_number,
            "gen_time": self.gen_time,
            "tsa_name": self.tsa_name,
            "signature": self.signature,
            "nonce": self.nonce,
            "tsa_public_key": self.tsa_public_key,
        }


@dataclass
class TimeStampResponse:
    status: int
    status_string: str
    token: TimeStampToken | None = None
    failure_info: str | None = None


@dataclass
class TimeStampRequest:
    message_imprint: str
    nonce: str = ""
    policy_oid: str = ""


class LocalTSA:
    _POLICY_OID = "1.3.6.1.4.1.99999.1.1"

    def __init__(self, tsa_name: str = "PSIA-LocalTSA") -> None:
        self._tsa_name = tsa_name
        self._keypair = Ed25519Provider.generate_keypair("tsa")
        self._serial = 0
        self._lock = threading.Lock()
        self._used_nonces: set[str] = set()

    @property
    def tsa_name(self) -> str:
        return self._tsa_name

    @property
    def public_key_hex(self) -> str:
        return self._keypair.public_key_hex

    @property
    def serial_count(self) -> int:
        return self._serial

    @property
    def _serial_counter(self) -> int:
        return self._serial

    def request_timestamp(
        self,
        message_imprint: str,
        nonce: str | None = None,
    ) -> TimeStampResponse:
        if len(message_imprint) != 64:
            return TimeStampResponse(
                status=1,
                status_string="rejection",
                failure_info="message_imprint must be 64 hex chars",
            )

        with self._lock:
            if nonce is not None and nonce in self._used_nonces:
                return TimeStampResponse(
                    status=1,
                    status_string="rejection",
                    failure_info=f"nonce already used: {nonce}",
                )

            effective_nonce = nonce if nonce is not None else uuid.uuid4().hex
            self._serial += 1
            serial = self._serial

            if nonce is not None:
                self._used_nonces.add(nonce)

        gen_time = datetime.now(timezone.utc).isoformat()
        token = TimeStampToken(
            version=1,
            policy_oid=self._POLICY_OID,
            hash_algorithm="SHA-256",
            message_imprint=message_imprint,
            serial_number=serial,
            gen_time=gen_time,
            tsa_name=self._tsa_name,
            signature="",
            nonce=effective_nonce,
            tsa_public_key=self._keypair.public_key_hex,
        )
        token.signature = Ed25519Provider.sign(self._keypair.private_key, token._signable())

        return TimeStampResponse(status=0, status_string="granted", token=token)

    def verify_timestamp(
        self,
        token: TimeStampToken,
        data_hash: str | None = None,
    ) -> bool:
        if data_hash is not None and token.message_imprint != data_hash:
            return False
        return Ed25519Provider.verify(
            self._keypair.public_key,
            token.signature,
            token._signable(),
        )

    @staticmethod
    def verify_with_public_key(token: TimeStampToken, pub_hex: str) -> bool:
        try:
            pub = Ed25519Provider.load_public_key(pub_hex)
            return Ed25519Provider.verify(pub, token.signature, token._signable())
        except Exception:
            return False
