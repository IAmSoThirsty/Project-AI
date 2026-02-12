#!/usr/bin/env python3
"""
Persona State Snapshot Signing - Cryptographic Integrity Layer
===============================================================

Provides Ed25519 signature-based integrity verification for AI persona state snapshots.
Ensures persona state cannot be tampered with and provides audit trail.

Features:
- Ed25519 cryptographic signatures for persona state
- State hashing with versioning
- Snapshot verification before restoration
- Tamper detection and alerting
- State lineage tracking
- Automatic snapshot rotation
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
except ImportError:
    print("ERROR: cryptography package required. Install with: pip install cryptography")
    sys.exit(1)


class PersonaSigner:
    """Sign and verify AI persona state snapshots for integrity."""
    
    def __init__(self, key_dir: Path):
        """
        Initialize persona signer.
        
        Args:
            key_dir: Directory containing signing keys
        """
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.key_dir / "persona_signing.key"
        self.public_key_path = self.key_dir / "persona_signing.pub"
        self.signatures_dir = self.key_dir / "persona_signatures"
        self.snapshots_dir = self.key_dir / "persona_snapshots"
        self.signatures_dir.mkdir(exist_ok=True)
        self.snapshots_dir.mkdir(exist_ok=True)
        
    def generate_keypair(self, force: bool = False) -> Tuple[Path, Path]:
        """
        Generate Ed25519 keypair for persona signing.
        
        Args:
            force: If True, regenerate even if keys exist
            
        Returns:
            Tuple of (private_key_path, public_key_path)
        """
        if not force and self.private_key_path.exists():
            print(f"Keys already exist at {self.key_dir}")
            return (self.private_key_path, self.public_key_path)
            
        # Generate new Ed25519 keypair
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Save private key (PEM format)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Save public key (PEM format)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Write keys with restricted permissions
        self.private_key_path.write_bytes(private_pem)
        self.private_key_path.chmod(0o600)  # Owner read/write only
        
        self.public_key_path.write_bytes(public_pem)
        self.public_key_path.chmod(0o644)  # Owner read/write, others read
        
        print(f"✓ Generated Ed25519 keypair for persona signing:")
        print(f"  Private: {self.private_key_path}")
        print(f"  Public:  {self.public_key_path}")
        
        return (self.private_key_path, self.public_key_path)
    
    def _load_private_key(self) -> Ed25519PrivateKey:
        """Load private key from disk."""
        if not self.private_key_path.exists():
            raise FileNotFoundError(
                f"Private key not found at {self.private_key_path}. "
                "Run generate_keypair() first."
            )
        
        pem_data = self.private_key_path.read_bytes()
        return serialization.load_pem_private_key(pem_data, password=None)
    
    def _load_public_key(self) -> Ed25519PublicKey:
        """Load public key from disk."""
        if not self.public_key_path.exists():
            raise FileNotFoundError(
                f"Public key not found at {self.public_key_path}. "
                "Run generate_keypair() first."
            )
        
        pem_data = self.public_key_path.read_bytes()
        return serialization.load_pem_public_key(pem_data)
    
    def _canonical_serialize(self, state: Dict) -> bytes:
        """
        Serialize persona state in canonical form for consistent hashing.
        
        Args:
            state: Persona state dictionary
            
        Returns:
            Canonical bytes representation
        """
        # Use JSON with sorted keys for deterministic output
        json_str = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return json_str.encode('utf-8')
    
    def create_snapshot(
        self, 
        persona_state: Dict, 
        persona_id: str,
        parent_snapshot: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create signed snapshot of persona state.
        
        Args:
            persona_state: Current persona state dictionary
            persona_id: Unique identifier for persona
            parent_snapshot: Hash of previous snapshot (for lineage)
            metadata: Optional metadata to include
            
        Returns:
            Snapshot manifest dictionary
        """
        # Canonicalize state
        canonical_bytes = self._canonical_serialize(persona_state)
        
        # Compute content hash
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()
        
        # Load private key and sign
        private_key = self._load_private_key()
        signature = private_key.sign(canonical_bytes)
        
        # Create snapshot manifest
        snapshot = {
            "version": "1.0",
            "algorithm": "Ed25519",
            "hash_algorithm": "SHA-256",
            "persona_id": persona_id,
            "snapshot_hash": content_hash,
            "parent_snapshot": parent_snapshot,
            "state": persona_state,
            "signature": signature.hex(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "creator": os.getenv("USER", "system"),
            "metadata": metadata or {}
        }
        
        # Save snapshot
        snapshot_file = self.snapshots_dir / f"{persona_id}_{content_hash[:12]}.snapshot.json"
        snapshot_file.write_text(json.dumps(snapshot, indent=2))
        snapshot_file.chmod(0o600)  # Sensitive data
        
        # Save signature manifest separately for quick verification
        sig_manifest = {
            "version": "1.0",
            "algorithm": "Ed25519",
            "hash_algorithm": "SHA-256",
            "persona_id": persona_id,
            "snapshot_hash": content_hash,
            "snapshot_file": snapshot_file.name,
            "signature": signature.hex(),
            "created_at": snapshot["created_at"],
            "parent_snapshot": parent_snapshot,
            "metadata": metadata or {}
        }
        
        sig_file = self.signatures_dir / f"{persona_id}_{content_hash[:12]}.sig.json"
        sig_file.write_text(json.dumps(sig_manifest, indent=2))
        sig_file.chmod(0o644)
        
        print(f"✓ Created persona snapshot: {persona_id}")
        print(f"  Snapshot hash: {content_hash[:16]}...")
        print(f"  File:          {snapshot_file}")
        print(f"  Signature:     {sig_file}")
        
        return snapshot
    
    def verify_snapshot(self, snapshot_file: Path) -> Tuple[bool, str, Optional[Dict]]:
        """
        Verify persona snapshot signature and integrity.
        
        Args:
            snapshot_file: Path to snapshot file
            
        Returns:
            Tuple of (is_valid, message, snapshot_data)
        """
        snapshot_file = Path(snapshot_file)
        
        if not snapshot_file.exists():
            return (False, f"Snapshot file not found: {snapshot_file}", None)
        
        # Load snapshot
        try:
            snapshot = json.loads(snapshot_file.read_text())
        except json.JSONDecodeError as e:
            return (False, f"Invalid snapshot JSON: {e}", None)
        
        # Extract state and compute hash
        state = snapshot.get("state", {})
        canonical_bytes = self._canonical_serialize(state)
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()
        
        # Verify content hash
        if content_hash != snapshot.get("snapshot_hash"):
            return (False, f"Content hash mismatch. Snapshot has been tampered with!", None)
        
        # Verify signature
        try:
            public_key = self._load_public_key()
            signature = bytes.fromhex(snapshot["signature"])
            public_key.verify(signature, canonical_bytes)
        except Exception as e:
            return (False, f"Signature verification failed: {e}", None)
        
        return (True, f"Snapshot valid (created {snapshot['created_at']})", snapshot)
    
    def list_snapshots(self, persona_id: Optional[str] = None) -> List[Dict]:
        """
        List all persona snapshots, optionally filtered by persona_id.
        
        Args:
            persona_id: Optional persona ID to filter
            
        Returns:
            List of snapshot metadata dictionaries
        """
        pattern = f"{persona_id}_*.sig.json" if persona_id else "*.sig.json"
        sig_files = sorted(self.signatures_dir.glob(pattern))
        
        snapshots = []
        for sig_file in sig_files:
            try:
                sig_data = json.loads(sig_file.read_text())
                snapshots.append(sig_data)
            except Exception as e:
                print(f"✗ Failed to load {sig_file.name}: {e}")
        
        return snapshots
    
    def restore_snapshot(self, snapshot_file: Path) -> Tuple[bool, Optional[Dict]]:
        """
        Verify and restore persona state from snapshot.
        
        Args:
            snapshot_file: Path to snapshot file
            
        Returns:
            Tuple of (success, persona_state)
        """
        is_valid, message, snapshot = self.verify_snapshot(snapshot_file)
        
        if not is_valid:
            print(f"✗ Cannot restore: {message}")
            return (False, None)
        
        print(f"✓ Snapshot verified: {message}")
        print(f"✓ Restoring persona state for {snapshot['persona_id']}")
        
        return (True, snapshot["state"])
    
    def get_lineage(self, snapshot_hash: str) -> List[Dict]:
        """
        Get complete lineage of snapshots leading to given snapshot.
        
        Args:
            snapshot_hash: Hash of snapshot to trace
            
        Returns:
            List of snapshots in lineage (oldest to newest)
        """
        # Find snapshot by hash
        sig_files = list(self.signatures_dir.glob(f"*_{snapshot_hash[:12]}.sig.json"))
        
        if not sig_files:
            print(f"Snapshot not found: {snapshot_hash}")
            return []
        
        lineage = []
        current_hash = snapshot_hash
        
        # Walk backwards through parent references
        while current_hash:
            sig_data = None
            for sig_file in self.signatures_dir.glob(f"*_{current_hash[:12]}.sig.json"):
                sig_data = json.loads(sig_file.read_text())
                break
            
            if not sig_data:
                break
            
            lineage.append(sig_data)
            current_hash = sig_data.get("parent_snapshot")
        
        # Return oldest to newest
        return list(reversed(lineage))


def main():
    """CLI entry point for persona signing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sign and verify AI persona state snapshots"
    )
    parser.add_argument(
        "command",
        choices=["keygen", "snapshot", "verify", "list", "restore", "lineage"],
        help="Command to execute"
    )
    parser.add_argument(
        "--key-dir",
        type=Path,
        default=Path("/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/security/crypto/keys"),
        help="Directory for signing keys"
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        help="Path to snapshot file (for verify/restore)"
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        help="Path to persona state JSON (for snapshot creation)"
    )
    parser.add_argument(
        "--persona-id",
        help="Persona ID (for snapshot/list)"
    )
    parser.add_argument(
        "--parent",
        help="Parent snapshot hash (for lineage tracking)"
    )
    parser.add_argument(
        "--hash",
        help="Snapshot hash (for lineage command)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of keys"
    )
    
    args = parser.parse_args()
    
    signer = PersonaSigner(args.key_dir)
    
    if args.command == "keygen":
        signer.generate_keypair(force=args.force)
    
    elif args.command == "snapshot":
        if not args.state_file or not args.persona_id:
            parser.error("--state-file and --persona-id required for snapshot command")
        
        state = json.loads(Path(args.state_file).read_text())
        signer.create_snapshot(state, args.persona_id, parent_snapshot=args.parent)
    
    elif args.command == "verify":
        if not args.snapshot:
            parser.error("--snapshot required for verify command")
        is_valid, message, _ = signer.verify_snapshot(args.snapshot)
        print(f"{'✓' if is_valid else '✗'} {message}")
        sys.exit(0 if is_valid else 1)
    
    elif args.command == "list":
        snapshots = signer.list_snapshots(args.persona_id)
        print(f"Found {len(snapshots)} snapshots:")
        for snap in snapshots:
            print(f"  {snap['snapshot_hash'][:12]} - {snap['persona_id']} - {snap['created_at']}")
    
    elif args.command == "restore":
        if not args.snapshot:
            parser.error("--snapshot required for restore command")
        success, state = signer.restore_snapshot(args.snapshot)
        if success:
            print(json.dumps(state, indent=2))
        sys.exit(0 if success else 1)
    
    elif args.command == "lineage":
        if not args.hash:
            parser.error("--hash required for lineage command")
        lineage = signer.get_lineage(args.hash)
        print(f"Snapshot lineage ({len(lineage)} snapshots):")
        for i, snap in enumerate(lineage, 1):
            print(f"  {i}. {snap['snapshot_hash'][:12]} - {snap['created_at']}")


if __name__ == "__main__":
    main()
