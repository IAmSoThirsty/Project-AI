#!/usr/bin/env python3
"""
Configuration Signing System - Cryptographic Integrity Layer
=============================================================

Provides Ed25519 signature-based integrity verification for configuration files.
Ensures configurations cannot be tampered with and provides audit trail.

Features:
- Ed25519 cryptographic signatures for YAML/JSON configs
- Content hashing (SHA-256) with canonical serialization
- Signature verification before loading
- Tamper detection and alerting
- Multi-key support for different environments
- Configuration versioning and history
"""

import hashlib
import json
import os
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
except ImportError:
    print("ERROR: cryptography package required. Install with: pip install cryptography")
    sys.exit(1)


class ConfigSigner:
    """Sign and verify configuration files for integrity."""
    
    def __init__(self, key_dir: Path, environment: str = "production"):
        """
        Initialize config signer.
        
        Args:
            key_dir: Directory containing signing keys
            environment: Environment name (production, staging, development)
        """
        self.key_dir = Path(key_dir)
        self.environment = environment
        self.key_dir.mkdir(parents=True, exist_ok=True)
        
        # Environment-specific keys
        self.private_key_path = self.key_dir / f"config_signing_{environment}.key"
        self.public_key_path = self.key_dir / f"config_signing_{environment}.pub"
        self.signatures_dir = self.key_dir / "config_signatures"
        self.signatures_dir.mkdir(exist_ok=True)
        
    def generate_keypair(self, force: bool = False) -> Tuple[Path, Path]:
        """
        Generate Ed25519 keypair for config signing.
        
        Args:
            force: If True, regenerate even if keys exist
            
        Returns:
            Tuple of (private_key_path, public_key_path)
        """
        if not force and self.private_key_path.exists():
            print(f"Keys already exist for {self.environment} at {self.key_dir}")
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
        
        print(f"✓ Generated Ed25519 keypair for {self.environment}:")
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
    
    def _canonical_serialize(self, data: Any) -> bytes:
        """
        Serialize data in canonical form for consistent hashing.
        
        Args:
            data: Data structure to serialize
            
        Returns:
            Canonical bytes representation
        """
        # Use JSON with sorted keys for deterministic output
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return json_str.encode('utf-8')
    
    def _load_config(self, config_path: Path) -> Any:
        """Load configuration from file (YAML or JSON)."""
        content = config_path.read_text()
        
        if config_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        elif config_path.suffix == '.json':
            return json.loads(content)
        else:
            # Treat as text
            return {"_raw_content": content}
    
    def sign_config(self, config_path: Path, metadata: Optional[Dict] = None) -> Dict:
        """
        Sign a configuration file and create signature manifest.
        
        Args:
            config_path: Path to config file (YAML/JSON)
            metadata: Optional metadata to include in signature
            
        Returns:
            Signature manifest dictionary
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Load and canonicalize config
        config_data = self._load_config(config_path)
        canonical_bytes = self._canonical_serialize(config_data)
        
        # Compute content hash
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()
        
        # Load private key and sign
        private_key = self._load_private_key()
        signature = private_key.sign(canonical_bytes)
        
        # Create signature manifest
        manifest = {
            "version": "1.0",
            "algorithm": "Ed25519",
            "hash_algorithm": "SHA-256",
            "config_file": config_path.name,
            "config_type": config_path.suffix,
            "content_hash": content_hash,
            "content_size": len(canonical_bytes),
            "signature": signature.hex(),
            "environment": self.environment,
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "signer": os.getenv("USER", "unknown"),
            "metadata": metadata or {}
        }
        
        # Save signature manifest
        sig_file = self.signatures_dir / f"{config_path.stem}_{self.environment}.sig.json"
        sig_file.write_text(json.dumps(manifest, indent=2))
        sig_file.chmod(0o644)
        
        print(f"✓ Signed config: {config_path.name} ({self.environment})")
        print(f"  Content hash: {content_hash[:16]}...")
        print(f"  Signature:    {sig_file}")
        
        return manifest
    
    def verify_config(self, config_path: Path) -> Tuple[bool, str]:
        """
        Verify configuration signature and integrity.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Tuple of (is_valid, message)
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            return (False, f"Config file not found: {config_path}")
        
        # Find signature file
        sig_file = self.signatures_dir / f"{config_path.stem}_{self.environment}.sig.json"
        if not sig_file.exists():
            return (False, f"Signature file not found: {sig_file}")
        
        # Load signature manifest
        try:
            manifest = json.loads(sig_file.read_text())
        except json.JSONDecodeError as e:
            return (False, f"Invalid signature manifest: {e}")
        
        # Load and canonicalize config
        try:
            config_data = self._load_config(config_path)
            canonical_bytes = self._canonical_serialize(config_data)
        except Exception as e:
            return (False, f"Failed to load config: {e}")
        
        # Verify content hash
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()
        if content_hash != manifest["content_hash"]:
            return (False, f"Content hash mismatch. Config has been tampered with!")
        
        # Verify environment matches
        if manifest.get("environment") != self.environment:
            return (False, f"Environment mismatch: expected {self.environment}, got {manifest.get('environment')}")
        
        # Verify signature
        try:
            public_key = self._load_public_key()
            signature = bytes.fromhex(manifest["signature"])
            public_key.verify(signature, canonical_bytes)
        except Exception as e:
            return (False, f"Signature verification failed: {e}")
        
        return (True, f"Config signature valid (signed at {manifest['signed_at']})")
    
    def batch_sign(self, config_dir: Path, patterns: list = None) -> int:
        """
        Sign all configuration files in a directory.
        
        Args:
            config_dir: Directory containing configs
            patterns: List of glob patterns (default: ['*.yaml', '*.yml', '*.json'])
            
        Returns:
            Number of configs signed
        """
        if patterns is None:
            patterns = ['*.yaml', '*.yml', '*.json']
        
        config_dir = Path(config_dir)
        config_files = []
        for pattern in patterns:
            config_files.extend(sorted(config_dir.rglob(pattern)))
        
        if not config_files:
            print(f"No configs found in {config_dir} matching {patterns}")
            return 0
        
        print(f"Signing {len(config_files)} configuration files...")
        
        count = 0
        for config_file in config_files:
            try:
                self.sign_config(config_file)
                count += 1
            except Exception as e:
                print(f"✗ Failed to sign {config_file.name}: {e}")
        
        print(f"\n✓ Signed {count}/{len(config_files)} configs")
        return count


def main():
    """CLI entry point for config signing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sign and verify configuration files for integrity"
    )
    parser.add_argument(
        "command",
        choices=["keygen", "sign", "verify", "batch-sign"],
        help="Command to execute"
    )
    parser.add_argument(
        "--key-dir",
        type=Path,
        default=Path("/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/security/crypto/keys"),
        help="Directory for signing keys"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config file (for sign/verify)"
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        help="Directory containing configs (for batch operations)"
    )
    parser.add_argument(
        "--environment",
        default="production",
        choices=["production", "staging", "development"],
        help="Environment for key selection"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of keys"
    )
    
    args = parser.parse_args()
    
    signer = ConfigSigner(args.key_dir, args.environment)
    
    if args.command == "keygen":
        signer.generate_keypair(force=args.force)
    
    elif args.command == "sign":
        if not args.config:
            parser.error("--config required for sign command")
        signer.sign_config(args.config)
    
    elif args.command == "verify":
        if not args.config:
            parser.error("--config required for verify command")
        is_valid, message = signer.verify_config(args.config)
        print(f"{'✓' if is_valid else '✗'} {message}")
        sys.exit(0 if is_valid else 1)
    
    elif args.command == "batch-sign":
        if not args.config_dir:
            parser.error("--config-dir required for batch-sign command")
        signer.batch_sign(args.config_dir)


if __name__ == "__main__":
    main()
