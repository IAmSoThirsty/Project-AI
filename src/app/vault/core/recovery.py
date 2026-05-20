"""
Vault key recovery using Shamir Secret Sharing.
"""

from __future__ import annotations

from app.security.tseca_ghost_protocol import shamir_reconstruct, shamir_split


class ShamirSecretSharing:
    """k-of-n secret splitting backed by GF(256) Shamir implementation."""

    def __init__(self, threshold: int, total_shares: int) -> None:
        if threshold < 1 or threshold > total_shares:
            raise ValueError(
                f"Invalid parameters: threshold={threshold}, total_shares={total_shares}"
            )
        self.threshold = threshold
        self.total_shares = total_shares

    def split(self, secret: bytes) -> list[tuple[int, bytes]]:
        return shamir_split(secret, self.threshold, self.total_shares)

    def reconstruct(self, shares: list[tuple[int, bytes]]) -> bytes:
        if len(shares) < self.threshold:
            raise ValueError(
                f"Insufficient shares: need {self.threshold}, got {len(shares)}"
            )
        return shamir_reconstruct(shares)


class VaultRecovery:
    """Creates and redeems Shamir-based key escrow bundles."""

    _DEFAULT_THRESHOLD = 2

    def __init__(self, data_dir: str) -> None:
        from pathlib import Path
        self.data_dir = Path(data_dir)

    def create_escrow(
        self, master_key: bytes, guardian_count: int
    ) -> dict[str, object]:
        threshold = min(self._DEFAULT_THRESHOLD, guardian_count)
        sss = ShamirSecretSharing(threshold=threshold, total_shares=guardian_count)
        shares = sss.split(master_key)
        return {
            "threshold": threshold,
            "total": guardian_count,
            "shares": shares,
        }
