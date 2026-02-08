"""
Capsule Engine
==============

Deterministic build capsules with hash trees and cryptographic verification.
Provides reproducible builds and forensic replay capabilities.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BuildCapsule:
    """Represents an immutable build execution capsule."""

    def __init__(
        self,
        capsule_id: str,
        tasks: list[str],
        inputs: dict[str, str],
        outputs: dict[str, str],
        metadata: dict[str, Any]
    ):
        """
        Initialize build capsule.

        Args:
            capsule_id: Unique capsule identifier
            tasks: Executed tasks
            inputs: Input file hashes {path: hash}
            outputs: Output file hashes {path: hash}
            metadata: Build metadata (timestamp, duration, etc.)
        """
        self.capsule_id = capsule_id
        self.tasks = tasks
        self.inputs = inputs
        self.outputs = outputs
        self.metadata = metadata
        self.merkle_root = self._compute_merkle_root()
        self.timestamp = metadata.get("timestamp", datetime.utcnow().isoformat())

    def _compute_merkle_root(self) -> str:
        """Compute Merkle root hash of capsule contents."""
        # Combine all hashes in deterministic order
        all_hashes = []

        # Task hashes
        for task in sorted(self.tasks):
            all_hashes.append(hashlib.sha256(task.encode()).hexdigest())

        # Input hashes
        for path in sorted(self.inputs.keys()):
            all_hashes.append(self.inputs[path])

        # Output hashes
        for path in sorted(self.outputs.keys()):
            all_hashes.append(self.outputs[path])

        # Build Merkle tree
        return self._merkle_tree(all_hashes)

    def _merkle_tree(self, hashes: list[str]) -> str:
        """Build Merkle tree from hash list."""
        if not hashes:
            return hashlib.sha256(b"").hexdigest()

        if len(hashes) == 1:
            return hashes[0]

        # Pair hashes and compute parent level
        next_level = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                combined = hashes[i] + hashes[i + 1]
            else:
                combined = hashes[i] + hashes[i]

            next_level.append(hashlib.sha256(combined.encode()).hexdigest())

        return self._merkle_tree(next_level)

    def to_dict(self) -> dict[str, Any]:
        """Convert capsule to dictionary."""
        return {
            "capsule_id": self.capsule_id,
            "tasks": self.tasks,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
        }

    def verify_integrity(self) -> bool:
        """Verify capsule integrity by recomputing Merkle root."""
        return self._compute_merkle_root() == self.merkle_root


class CapsuleEngine:
    """
    Manages deterministic build capsules with hash tree verification.
    Enables reproducible builds and forensic analysis.
    """

    def __init__(self, capsule_dir: Path | None = None):
        """
        Initialize capsule engine.

        Args:
            capsule_dir: Directory for capsule storage
        """
        self.capsule_dir = capsule_dir or Path("data/build_capsules")
        self.capsule_dir.mkdir(parents=True, exist_ok=True)
        self.capsules: dict[str, BuildCapsule] = {}
        self._load_capsules()
        logger.info(f"Capsule engine initialized: {self.capsule_dir}")

    def create_capsule(
        self,
        tasks: list[str],
        input_files: list[Path],
        output_files: list[Path],
        metadata: dict[str, Any] | None = None
    ) -> BuildCapsule:
        """
        Create a new build capsule.

        Args:
            tasks: Build tasks executed
            input_files: Input files to hash
            output_files: Output files to hash
            metadata: Optional metadata

        Returns:
            Created build capsule
        """
        try:
            # Compute input hashes
            inputs = {}
            for path in input_files:
                if path.exists():
                    inputs[str(path)] = self._hash_file(path)

            # Compute output hashes
            outputs = {}
            for path in output_files:
                if path.exists():
                    outputs[str(path)] = self._hash_file(path)

            # Generate capsule ID
            capsule_id = self._generate_capsule_id(tasks, inputs, outputs)

            # Create capsule
            capsule_metadata = metadata or {}
            capsule_metadata["timestamp"] = datetime.utcnow().isoformat()

            capsule = BuildCapsule(
                capsule_id=capsule_id,
                tasks=tasks,
                inputs=inputs,
                outputs=outputs,
                metadata=capsule_metadata
            )

            # Store capsule
            self.capsules[capsule_id] = capsule
            self._persist_capsule(capsule)

            logger.info(f"Created build capsule: {capsule_id}")
            return capsule

        except Exception as e:
            logger.error(f"Error creating capsule: {e}", exc_info=True)
            raise

    def verify_capsule(self, capsule_id: str) -> tuple[bool, str | None]:
        """
        Verify capsule integrity.

        Args:
            capsule_id: Capsule to verify

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            capsule = self.capsules.get(capsule_id)
            if not capsule:
                return False, f"Capsule not found: {capsule_id}"

            if not capsule.verify_integrity():
                return False, "Merkle root verification failed"

            # Verify against persisted version
            persisted = self._load_capsule(capsule_id)
            if persisted and persisted.merkle_root != capsule.merkle_root:
                return False, "Merkle root mismatch with persisted capsule"

            return True, None

        except Exception as e:
            logger.error(f"Error verifying capsule: {e}", exc_info=True)
            return False, str(e)

    def find_capsules_by_task(self, task: str) -> list[BuildCapsule]:
        """
        Find capsules containing specific task.

        Args:
            task: Task name to search for

        Returns:
            List of matching capsules
        """
        return [
            capsule for capsule in self.capsules.values()
            if task in capsule.tasks
        ]

    def find_capsules_by_input(self, input_path: str) -> list[BuildCapsule]:
        """
        Find capsules that used specific input file.

        Args:
            input_path: Input file path

        Returns:
            List of matching capsules
        """
        return [
            capsule for capsule in self.capsules.values()
            if input_path in capsule.inputs
        ]

    def compute_capsule_diff(
        self,
        capsule_id1: str,
        capsule_id2: str
    ) -> dict[str, Any]:
        """
        Compute difference between two capsules.

        Args:
            capsule_id1: First capsule ID
            capsule_id2: Second capsule ID

        Returns:
            Dictionary describing differences
        """
        try:
            cap1 = self.capsules.get(capsule_id1)
            cap2 = self.capsules.get(capsule_id2)

            if not cap1 or not cap2:
                return {"error": "One or both capsules not found"}

            # Compare tasks
            tasks1 = set(cap1.tasks)
            tasks2 = set(cap2.tasks)

            # Compare inputs
            inputs1 = set(cap1.inputs.keys())
            inputs2 = set(cap2.inputs.keys())

            # Compare outputs
            outputs1 = set(cap1.outputs.keys())
            outputs2 = set(cap2.outputs.keys())

            return {
                "capsule_1": capsule_id1,
                "capsule_2": capsule_id2,
                "tasks": {
                    "added": list(tasks2 - tasks1),
                    "removed": list(tasks1 - tasks2),
                    "common": list(tasks1 & tasks2),
                },
                "inputs": {
                    "added": list(inputs2 - inputs1),
                    "removed": list(inputs1 - inputs2),
                    "modified": self._find_modified_files(cap1.inputs, cap2.inputs),
                },
                "outputs": {
                    "added": list(outputs2 - outputs1),
                    "removed": list(outputs1 - outputs2),
                    "modified": self._find_modified_files(cap1.outputs, cap2.outputs),
                },
            }

        except Exception as e:
            logger.error(f"Error computing capsule diff: {e}", exc_info=True)
            return {"error": str(e)}

    def export_capsule_chain(
        self,
        capsule_ids: list[str],
        output_path: Path
    ) -> None:
        """
        Export capsule chain for forensic analysis.

        Args:
            capsule_ids: List of capsule IDs to export
            output_path: Output file path
        """
        try:
            chain = []
            for capsule_id in capsule_ids:
                capsule = self.capsules.get(capsule_id)
                if capsule:
                    chain.append(capsule.to_dict())

            with open(output_path, "w") as f:
                json.dump(chain, f, indent=2)

            logger.info(f"Exported capsule chain to: {output_path}")

        except Exception as e:
            logger.error(f"Error exporting capsule chain: {e}", exc_info=True)

    def _hash_file(self, path: Path) -> str:
        """Compute SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _generate_capsule_id(
        self,
        tasks: list[str],
        inputs: dict[str, str],
        outputs: dict[str, str]
    ) -> str:
        """Generate unique capsule ID."""
        content = json.dumps({
            "tasks": sorted(tasks),
            "inputs": inputs,
            "outputs": outputs,
            "timestamp": datetime.utcnow().isoformat(),
        }, sort_keys=True)

        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _persist_capsule(self, capsule: BuildCapsule) -> None:
        """Persist capsule to disk."""
        try:
            filepath = self.capsule_dir / f"{capsule.capsule_id}.json"
            with open(filepath, "w") as f:
                json.dump(capsule.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error persisting capsule: {e}", exc_info=True)

    def _load_capsule(self, capsule_id: str) -> BuildCapsule | None:
        """Load capsule from disk."""
        try:
            filepath = self.capsule_dir / f"{capsule_id}.json"
            if not filepath.exists():
                return None

            with open(filepath) as f:
                data = json.load(f)

            return BuildCapsule(
                capsule_id=data["capsule_id"],
                tasks=data["tasks"],
                inputs=data["inputs"],
                outputs=data["outputs"],
                metadata=data["metadata"]
            )
        except Exception as e:
            logger.error(f"Error loading capsule: {e}", exc_info=True)
            return None

    def _load_capsules(self) -> None:
        """Load all capsules from disk."""
        try:
            for filepath in self.capsule_dir.glob("*.json"):
                capsule_id = filepath.stem
                capsule = self._load_capsule(capsule_id)
                if capsule:
                    self.capsules[capsule_id] = capsule

            logger.info(f"Loaded {len(self.capsules)} capsules")
        except Exception as e:
            logger.error(f"Error loading capsules: {e}", exc_info=True)

    def _find_modified_files(
        self,
        files1: dict[str, str],
        files2: dict[str, str]
    ) -> list[str]:
        """Find files with different hashes."""
        modified = []
        for path in files1:
            if path in files2 and files1[path] != files2[path]:
                modified.append(path)
        return modified


__all__ = ["CapsuleEngine", "BuildCapsule"]
