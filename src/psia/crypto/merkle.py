"""
Merkle tree implementation for PSIA stage 6 block sealing.

A canonical Merkle tree over SHA-256 hashes of log entries.
Leaf nodes: SHA-256(entry_hash).
Internal nodes: SHA-256(left_child + right_child).
Odd-length levels: last node is duplicated.

This is a true Merkle tree — not a SHA-256 chain labeled as Merkle.
"""

from __future__ import annotations

import hashlib
from typing import Sequence


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class MerkleTree:
    """
    Builds a Merkle tree from a list of hex-string leaf hashes.

    Usage:
        tree = MerkleTree(["aabbcc...", "ddeeff...", ...])
        root = tree.root  # hex string
    """

    def __init__(self, leaves: Sequence[str]) -> None:
        if not leaves:
            self._root = "0" * 64
            self._layers: list[list[str]] = [[]]
            return
        layer = [_sha256(h.encode("utf-8")) for h in leaves]
        self._layers = [layer]
        while len(layer) > 1:
            layer = self._build_layer(layer)
            self._layers.append(layer)
        self._root = self._layers[-1][0]

    @staticmethod
    def _build_layer(nodes: list[str]) -> list[str]:
        result: list[str] = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]  # duplicate last
            result.append(_sha256((left + right).encode("utf-8")))
        return result

    @property
    def root(self) -> str:
        return self._root

    def proof(self, index: int) -> list[dict]:
        """
        Return a Merkle inclusion proof for the leaf at `index`.
        Each element: {"direction": "left"|"right", "hash": "<hex>"}
        """
        proof: list[dict] = []
        for layer in self._layers[:-1]:
            sibling_idx = index ^ 1  # XOR to get sibling
            if sibling_idx < len(layer):
                sibling = layer[sibling_idx]
            else:
                sibling = layer[index]  # duplicate case
            direction = "right" if index % 2 == 0 else "left"
            proof.append({"direction": direction, "hash": sibling})
            index //= 2
        return proof

    @staticmethod
    def verify(leaf_hash: str, proof: list[dict], expected_root: str) -> bool:
        """Verify a Merkle inclusion proof."""
        current = _sha256(leaf_hash.encode("utf-8"))
        for step in proof:
            if step["direction"] == "right":
                current = _sha256((current + step["hash"]).encode("utf-8"))
            else:
                current = _sha256((step["hash"] + current).encode("utf-8"))
        return current == expected_root
