"""
T-SECA / GHOST Threshold Cryptography over GF(257).

T-SECA: Threshold Secret with Ed25519 Commitment Anchor
GHOST:  Governance Hash Over Shared Threshold

Implements Shamir's Secret Sharing over GF(257) — the smallest prime field
larger than 256, allowing secret bytes (0–255) to be represented as field
elements without ambiguity.  Each byte is split independently; multi-byte
secrets are split byte-by-byte and reassembled symmetrically.

GHOST extends T-SECA by anchoring the threshold commitment with a SHA-256
digest and an Ed25519 signature, creating an auditable governance record.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# GF(257) — Prime field of order 257
# ---------------------------------------------------------------------------

class GF257:
    """
    Arithmetic in GF(257), the prime field of order p = 257.

    257 is the smallest prime strictly greater than 256, so every byte value
    0–255 is a valid non-zero element (0 is the additive identity).  The field
    supports all standard operations required for polynomial evaluation and
    Lagrange interpolation in Shamir's Secret Sharing.
    """

    P: int = 257

    # ---- class-level helpers (all arithmetic is modular) ------------------

    @classmethod
    def add(cls, a: int, b: int) -> int:
        """Addition in GF(257)."""
        return (a + b) % cls.P

    @classmethod
    def sub(cls, a: int, b: int) -> int:
        """Subtraction in GF(257)."""
        return (a - b) % cls.P

    @classmethod
    def mul(cls, a: int, b: int) -> int:
        """Multiplication in GF(257)."""
        return (a * b) % cls.P

    @classmethod
    def pow(cls, base: int, exp: int) -> int:
        """Modular exponentiation in GF(257)."""
        return builtins_pow(base, exp, cls.P)

    @classmethod
    def inv(cls, a: int) -> int:
        """
        Multiplicative inverse via Fermat's Little Theorem: a^{p-2} mod p.

        Raises ZeroDivisionError for a == 0.
        """
        if a % cls.P == 0:
            raise ZeroDivisionError("GF(257): no multiplicative inverse for 0")
        return builtins_pow(a, cls.P - 2, cls.P)

    @classmethod
    def div(cls, a: int, b: int) -> int:
        """Division in GF(257): a * b^{-1} mod p."""
        return cls.mul(a, cls.inv(b))


# Use the built-in pow to avoid shadowing after class definition
builtins_pow = pow


# ---------------------------------------------------------------------------
# ShamirShare
# ---------------------------------------------------------------------------

@dataclass
class ShamirShare:
    """
    A single Shamir share: the point (x, y) on the secret polynomial over GF(257).

    x is the share index (1-based); y is the polynomial evaluation f(x).
    Both are elements of GF(257), i.e., integers in [0, 256].
    """

    x: int  # evaluation point (1 ≤ x ≤ 256)
    y: int  # f(x) in GF(257)

    def __post_init__(self) -> None:
        if not (0 <= self.x <= 256):
            raise ValueError(f"ShamirShare.x must be in [0, 256], got {self.x}")
        if not (0 <= self.y <= 256):
            raise ValueError(f"ShamirShare.y must be in [0, 256], got {self.y}")

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, d: dict) -> "ShamirShare":
        return cls(x=int(d["x"]), y=int(d["y"]))


# ---------------------------------------------------------------------------
# ThresholdSecret — Shamir k-of-n over GF(257)
# ---------------------------------------------------------------------------

class ThresholdSecret:
    """
    Shamir Secret Sharing over GF(257).

    Every secret byte b (0 ≤ b ≤ 255) is embedded directly as a field
    element and placed at f(0) of a random degree-(k-1) polynomial.
    """

    # ------------------------------------------------------------------
    # Single-byte operations
    # ------------------------------------------------------------------

    @staticmethod
    def _random_nonzero_field_element() -> int:
        """Return a cryptographically random element of GF(257) \ {0}."""
        # 257 is prime; rejection-sample from [1, 256]
        while True:
            b = secrets.randbelow(257)
            if b != 0:
                return b

    @classmethod
    def split(cls, secret_byte: int, n: int, k: int) -> List[ShamirShare]:
        """
        Split a single secret byte into n shares with threshold k.

        Parameters
        ----------
        secret_byte : int
            The secret value, must be in [0, 255].
        n : int
            Total number of shares to generate.
        k : int
            Minimum number of shares required for reconstruction.

        Returns
        -------
        list[ShamirShare]
            n shares [(1, f(1)), (2, f(2)), ..., (n, f(n))].

        Notes
        -----
        The polynomial is:
            f(x) = secret_byte + a_1*x + a_2*x^2 + ... + a_{k-1}*x^{k-1}  (mod 257)
        Coefficients a_1 ... a_{k-1} are chosen uniformly at random from GF(257).
        """
        if not (0 <= secret_byte <= 255):
            raise ValueError(f"secret_byte must be in [0, 255], got {secret_byte}")
        if k < 1:
            raise ValueError("threshold k must be at least 1")
        if n < k:
            raise ValueError(f"n ({n}) must be >= k ({k})")
        if n > 256:
            raise ValueError("n cannot exceed 256 (GF(257) only has 256 non-zero elements)")

        P = GF257.P

        # Build polynomial coefficients [secret_byte, a_1, ..., a_{k-1}]
        coeffs = [secret_byte % P]
        for _ in range(k - 1):
            coeffs.append(secrets.randbelow(P))

        shares = []
        for x in range(1, n + 1):
            # Evaluate polynomial at x using Horner's method
            y = 0
            for coeff in reversed(coeffs):
                y = GF257.add(GF257.mul(y, x), coeff)
            shares.append(ShamirShare(x=x, y=y))
        return shares

    @classmethod
    def reconstruct(cls, shares: List[ShamirShare], k: int) -> int:
        """
        Reconstruct the secret byte from any k shares using Lagrange interpolation.

        Parameters
        ----------
        shares : list[ShamirShare]
            Exactly k (or more) shares; only the first k are used.
        k : int
            The threshold used during splitting.

        Returns
        -------
        int
            The reconstructed secret byte in [0, 256].
        """
        if len(shares) < k:
            raise ValueError(f"Need at least {k} shares, got {len(shares)}")

        # Use the first k shares
        working = shares[:k]
        xs = [s.x for s in working]
        ys = [s.y for s in working]

        # Lagrange interpolation at x = 0
        secret = 0
        P = GF257.P
        for i in range(k):
            # Compute the i-th Lagrange basis polynomial evaluated at 0:
            # L_i(0) = product_{j != i} (0 - x_j) / (x_i - x_j)  in GF(257)
            numerator = 1
            denominator = 1
            for j in range(k):
                if i == j:
                    continue
                # (0 - x_j) mod P  =  (-x_j) mod P  =  (P - x_j) mod P
                numerator = GF257.mul(numerator, (P - xs[j]) % P)
                # (x_i - x_j) mod P
                denominator = GF257.mul(denominator, (xs[i] - xs[j]) % P)

            basis = GF257.mul(numerator, GF257.inv(denominator))
            term = GF257.mul(ys[i], basis)
            secret = GF257.add(secret, term)

        return secret

    # ------------------------------------------------------------------
    # Multi-byte operations
    # ------------------------------------------------------------------

    @classmethod
    def split_bytes(cls, data: bytes, n: int, k: int) -> List[List[ShamirShare]]:
        """
        Split each byte of data independently.

        Returns
        -------
        list[list[ShamirShare]]
            A list of n inner lists, one per participant.  Each inner list
            contains one ShamirShare per byte of data.
            Result shape: [participant_0_shares, ..., participant_{n-1}_shares]
            where participant_i_shares[j] is the share for byte j held by participant i.
        """
        if not data:
            raise ValueError("data must be non-empty")

        # byte_shares[j] = list of n shares for byte j
        byte_shares: List[List[ShamirShare]] = [
            cls.split(b, n, k) for b in data
        ]

        # Transpose: participant_shares[i] = shares from all bytes for participant i
        participant_shares: List[List[ShamirShare]] = [
            [byte_shares[j][i] for j in range(len(data))]
            for i in range(n)
        ]
        return participant_shares

    @classmethod
    def reconstruct_bytes(cls, share_sets: List[List[ShamirShare]], k: int) -> bytes:
        """
        Reconstruct the original bytes from k participants' share sets.

        Parameters
        ----------
        share_sets : list[list[ShamirShare]]
            Exactly k (or more) participants' share sets.  Each element is the
            list of per-byte shares for that participant.
        k : int
            The threshold used during splitting.

        Returns
        -------
        bytes
            The reconstructed original data.
        """
        if len(share_sets) < k:
            raise ValueError(f"Need at least {k} share sets, got {len(share_sets)}")

        # Use the first k participant share sets
        working = share_sets[:k]
        num_bytes = len(working[0])
        for ps in working:
            if len(ps) != num_bytes:
                raise ValueError("All share sets must have the same number of shares")

        result = bytearray()
        for j in range(num_bytes):
            # Collect the j-th share from each of the k participants
            byte_shares = [ps[j] for ps in working]
            byte_val = cls.reconstruct(byte_shares, k)
            # byte_val should be in [0, 255]; 256 would be a field element not valid as a byte
            if byte_val > 255:
                raise ValueError(
                    f"Reconstructed value {byte_val} at byte {j} is out of range [0, 255]. "
                    "Data corruption or wrong shares."
                )
            result.append(byte_val)
        return bytes(result)


# ---------------------------------------------------------------------------
# GHOSTRecord
# ---------------------------------------------------------------------------

@dataclass
class GHOSTRecord:
    """
    Governance Hash Over Shared Threshold — commitment record.

    Attributes
    ----------
    shares : list[list[ShamirShare]]
        n participant share sets (one per participant, each a list of per-byte shares).
    commitment_hex : str
        SHA-256 hex digest of the original plaintext data.
    signature_hex : str
        Ed25519 hex signature of commitment_hex (or "" if anchor unavailable).
    n : int
        Total number of shares.
    k : int
        Reconstruction threshold.
    timestamp : float
        Unix timestamp of record creation.
    """

    shares: List[List[ShamirShare]]
    commitment_hex: str
    signature_hex: str
    n: int
    k: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "shares": [
                [s.to_dict() for s in participant_shares]
                for participant_shares in self.shares
            ],
            "commitment_hex": self.commitment_hex,
            "signature_hex": self.signature_hex,
            "n": self.n,
            "k": self.k,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GHOSTRecord":
        shares = [
            [ShamirShare.from_dict(s) for s in participant_shares]
            for participant_shares in d["shares"]
        ]
        return cls(
            shares=shares,
            commitment_hex=d["commitment_hex"],
            signature_hex=d["signature_hex"],
            n=int(d["n"]),
            k=int(d["k"]),
            timestamp=float(d["timestamp"]),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str) -> "GHOSTRecord":
        return cls.from_dict(json.loads(s))


# ---------------------------------------------------------------------------
# GHOSTCommitment
# ---------------------------------------------------------------------------

class GHOSTCommitment:
    """
    Governance Hash Over Shared Threshold.

    Combines Shamir threshold secret sharing with Ed25519 commitment anchoring.
    The commitment (SHA-256 of original data) is signed with the Ed25519 anchor
    to create a non-repudiable governance record.  Reconstruction verifies both
    the SHA-256 commitment and the Ed25519 signature before returning data.
    """

    def commit(
        self,
        data: bytes,
        n: int,
        k: int,
        anchor: "Ed25519Anchor",
    ) -> GHOSTRecord:
        """
        Split data into n threshold shares and anchor the commitment.

        Steps
        -----
        1. Split data byte-by-byte using Shamir k-of-n over GF(257).
        2. Compute SHA-256 commitment of original data.
        3. Sign commitment_hex with the Ed25519 anchor.
        4. Return GHOSTRecord.

        Parameters
        ----------
        data : bytes
            The plaintext to protect.
        n : int
            Total number of shares.
        k : int
            Reconstruction threshold (k ≤ n).
        anchor : Ed25519Anchor
            Signing key.  If the anchor has no key material, signature_hex
            will be "" and a warning will be visible in the record.

        Returns
        -------
        GHOSTRecord
        """
        if not data:
            raise ValueError("data must be non-empty")

        # 1. Threshold split
        shares = ThresholdSecret.split_bytes(data, n, k)

        # 2. SHA-256 commitment
        commitment = hashlib.sha256(data).hexdigest()

        # 3. Ed25519 signature over the commitment hex
        signature = anchor.sign(commitment)

        return GHOSTRecord(
            shares=shares,
            commitment_hex=commitment,
            signature_hex=signature,
            n=n,
            k=k,
        )

    def verify_and_reconstruct(
        self,
        record: GHOSTRecord,
        share_indices: List[int],
        anchor_pub_hex: str,
    ) -> bytes:
        """
        Reconstruct data from selected participant shares, verifying integrity.

        Steps
        -----
        1. Select participants by index from record.shares.
        2. Reconstruct plaintext using ThresholdSecret.reconstruct_bytes.
        3. Verify SHA-256 commitment of reconstructed data matches record.commitment_hex.
        4. Verify Ed25519 signature on commitment_hex using anchor_pub_hex.
        5. Return reconstructed bytes if all checks pass; raise on any failure.

        Parameters
        ----------
        record : GHOSTRecord
            The GHOST record produced by commit().
        share_indices : list[int]
            Indices into record.shares of the participating parties (0-based).
            Must provide at least record.k indices.
        anchor_pub_hex : str
            Hex-encoded Ed25519 public key for signature verification.

        Returns
        -------
        bytes
            The reconstructed plaintext.

        Raises
        ------
        ValueError
            If fewer than k indices are provided.
        RuntimeError
            If the SHA-256 commitment or Ed25519 signature verification fails.
        """
        if len(share_indices) < record.k:
            raise ValueError(
                f"Need at least {record.k} share indices, got {len(share_indices)}"
            )

        # 1. Select participant share sets
        selected: List[List[ShamirShare]] = []
        for idx in share_indices:
            if not (0 <= idx < len(record.shares)):
                raise ValueError(
                    f"share index {idx} is out of range [0, {len(record.shares) - 1}]"
                )
            selected.append(record.shares[idx])

        # 2. Reconstruct plaintext
        reconstructed = ThresholdSecret.reconstruct_bytes(selected, record.k)

        # 3. Verify SHA-256 commitment
        actual_commitment = hashlib.sha256(reconstructed).hexdigest()
        if actual_commitment != record.commitment_hex:
            raise RuntimeError(
                f"GHOST commitment mismatch: expected {record.commitment_hex}, "
                f"got {actual_commitment}. Data may be corrupted or tampered."
            )

        # 4. Verify Ed25519 signature
        from .anchor import Ed25519Anchor
        if not Ed25519Anchor.verify(record.commitment_hex, record.signature_hex, anchor_pub_hex):
            raise RuntimeError(
                "GHOST signature verification failed: Ed25519 signature on commitment "
                "does not match the provided public key. Record may have been tampered."
            )

        return reconstructed


__all__ = [
    "GF257",
    "ShamirShare",
    "ThresholdSecret",
    "GHOSTCommitment",
    "GHOSTRecord",
]
