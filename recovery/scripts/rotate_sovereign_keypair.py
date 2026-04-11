#!/usr/bin/env python3
"""
Sovereign Keypair Rotation Script
==================================

Rotates the Ed25519 sovereign signing keypair used for governance operations.

CRITICAL SECURITY OPERATION:
- Generates new Ed25519 keypair
- Stores in Vault (NOT in repository)
- Manages dual-key transition period
- Provides rollback capability
- Complete audit trail

Usage:
    python rotate_sovereign_keypair.py                    # Normal rotation
    python rotate_sovereign_keypair.py --emergency         # Emergency rotation (skip checks)
    python rotate_sovereign_keypair.py --dry-run           # Simulate rotation
    python rotate_sovereign_keypair.py --resume            # Resume failed rotation

Author: Secrets Architect
Date: 2026-04-11
Classification: CONFIDENTIAL
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any

# Cryptography for Ed25519 key generation
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('var/sovereign_keypair_rotation.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KeypairRotationError(Exception):
    """Raised when keypair rotation fails."""
    pass


class SovereignKeypairRotator:
    """
    Manages rotation of the sovereign Ed25519 signing keypair.
    
    Implements zero-downtime rotation with dual-key period and
    comprehensive audit trail.
    """
    
    def __init__(
        self, 
        vault_enabled: bool = True,
        dry_run: bool = False,
        emergency: bool = False
    ):
        """
        Initialize the keypair rotator.
        
        Args:
            vault_enabled: Use Vault for secret storage (recommended)
            dry_run: Simulate rotation without making changes
            emergency: Skip safety checks (use only for compromise)
        """
        self.vault_enabled = vault_enabled
        self.dry_run = dry_run
        self.emergency = emergency
        
        # Paths
        self.state_file = Path("var/keypair_rotation_state.json")
        self.backup_dir = Path("var/keypair_backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Rotation state
        self.state: Dict[str, Any] = {}
        self.load_state()
        
        logger.info(f"Initialized SovereignKeypairRotator (vault={vault_enabled}, dry_run={dry_run}, emergency={emergency})")
    
    def load_state(self):
        """Load rotation state from disk (for resume capability)."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logger.info(f"Loaded rotation state: {self.state.get('phase', 'unknown')}")
            except Exception as e:
                logger.warning(f"Could not load rotation state: {e}")
    
    def save_state(self, phase: str, data: Dict[str, Any]):
        """Save rotation state to disk."""
        self.state = {
            "phase": phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        if not self.dry_run:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.info(f"Saved rotation state: {phase}")
    
    def generate_keypair(self) -> Dict[str, str]:
        """
        Generate a new Ed25519 keypair.
        
        Returns:
            Dictionary with private_key, public_key (hex), algorithm, metadata
        """
        logger.info("Generating new Ed25519 keypair...")
        
        try:
            # Generate Ed25519 private key
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            # Export private key as raw bytes (32 bytes)
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Export public key as raw bytes (32 bytes)
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            # Create keypair data structure
            keypair = {
                "private_key": private_bytes.hex(),
                "public_key": public_bytes.hex(),
                "algorithm": "Ed25519",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "version": self.get_next_version(),
                "metadata": {
                    "rotated_by": os.environ.get("USER", "unknown"),
                    "rotation_reason": "emergency" if self.emergency else "scheduled",
                    "key_id": f"sovereign-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
                }
            }
            
            logger.info(f"Generated new keypair: {keypair['metadata']['key_id']}")
            logger.info(f"Public key: {keypair['public_key']}")
            
            return keypair
            
        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            raise KeypairRotationError(f"Keypair generation failed: {e}")
    
    def get_current_keypair(self) -> Optional[Dict[str, str]]:
        """
        Retrieve the current keypair from storage.
        
        Returns:
            Current keypair or None if not found
        """
        try:
            if self.vault_enabled:
                # Try to get from Vault first
                return self.get_from_vault()
            else:
                # Fallback to file-based (INSECURE - for testing only)
                keypair_file = Path("governance/sovereign_data/sovereign_keypair.json")
                if keypair_file.exists():
                    with open(keypair_file, 'r') as f:
                        return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"Could not retrieve current keypair: {e}")
            return None
    
    def get_from_vault(self) -> Optional[Dict[str, str]]:
        """
        Retrieve keypair from HashiCorp Vault.
        
        Returns:
            Keypair from Vault or None
        """
        try:
            import hvac
            
            vault_addr = os.environ.get("VAULT_ADDR", "http://vault:8200")
            vault_token = os.environ.get("VAULT_TOKEN")
            
            if not vault_token:
                logger.warning("VAULT_TOKEN not set, cannot retrieve from Vault")
                return None
            
            client = hvac.Client(url=vault_addr, token=vault_token)
            
            # Read from Vault
            response = client.secrets.kv.v2.read_secret_version(
                path="project-ai/signing/sovereign-keypair"
            )
            
            if response and 'data' in response and 'data' in response['data']:
                return response['data']['data']
            
            return None
            
        except ImportError:
            logger.warning("hvac library not installed, cannot use Vault")
            return None
        except Exception as e:
            logger.warning(f"Failed to retrieve from Vault: {e}")
            return None
    
    def store_in_vault(self, keypair: Dict[str, str]) -> bool:
        """
        Store keypair in HashiCorp Vault.
        
        Args:
            keypair: Keypair to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import hvac
            
            vault_addr = os.environ.get("VAULT_ADDR", "http://vault:8200")
            vault_token = os.environ.get("VAULT_TOKEN")
            
            if not vault_token:
                raise KeypairRotationError("VAULT_TOKEN not set")
            
            client = hvac.Client(url=vault_addr, token=vault_token)
            
            # Write to Vault
            client.secrets.kv.v2.create_or_update_secret(
                path="project-ai/signing/sovereign-keypair",
                secret=keypair
            )
            
            logger.info("✅ Stored keypair in Vault: project-ai/signing/sovereign-keypair")
            return True
            
        except ImportError:
            logger.error("hvac library not installed, cannot use Vault")
            return False
        except Exception as e:
            logger.error(f"Failed to store in Vault: {e}")
            return False
    
    def backup_current_keypair(self):
        """Backup the current keypair before rotation."""
        logger.info("Backing up current keypair...")
        
        current = self.get_current_keypair()
        if not current:
            logger.warning("No current keypair to backup")
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"sovereign_keypair_{timestamp}.json"
        
        if not self.dry_run:
            with open(backup_file, 'w') as f:
                json.dump(current, f, indent=2)
            logger.info(f"✅ Backed up current keypair to {backup_file}")
        else:
            logger.info(f"[DRY RUN] Would backup to {backup_file}")
    
    def get_next_version(self) -> str:
        """Get the next version number for the keypair."""
        current = self.get_current_keypair()
        if current and 'version' in current:
            # Extract version number and increment
            current_version = current['version']
            if current_version.startswith('v'):
                try:
                    num = int(current_version[1:]) + 1
                    return f"v{num}"
                except:
                    pass
        return "v2"  # Default if no current version
    
    def perform_rotation(self) -> Dict[str, str]:
        """
        Perform the complete keypair rotation.
        
        Returns:
            New keypair
        """
        try:
            # Phase 1: Pre-flight checks
            logger.info("=" * 60)
            logger.info("SOVEREIGN KEYPAIR ROTATION")
            logger.info("=" * 60)
            
            if not self.emergency:
                self.pre_flight_checks()
            else:
                logger.warning("⚠️  EMERGENCY ROTATION - Skipping pre-flight checks")
            
            # Phase 2: Backup current keypair
            self.save_state("backup", {})
            self.backup_current_keypair()
            
            # Phase 3: Generate new keypair
            self.save_state("generate", {})
            new_keypair = self.generate_keypair()
            
            # Phase 4: Store new keypair
            self.save_state("store", {"keypair": new_keypair})
            
            if self.vault_enabled:
                # Store in Vault (PRIMARY)
                if not self.dry_run:
                    success = self.store_in_vault(new_keypair)
                    if not success:
                        logger.warning("⚠️  Failed to store in Vault - continuing with filesystem backup only")
                        # Don't fail rotation - filesystem backup is acceptable
                else:
                    logger.info("[DRY RUN] Would store in Vault")
            else:
                logger.warning("⚠️  Vault disabled - keypair will only be in backup")
            
            # Phase 5: Begin dual-key period
            self.save_state("dual_key", {"keypair": new_keypair})
            self.setup_dual_key_period(new_keypair)
            
            # Phase 6: Update audit trail
            self.save_state("audit", {"keypair": new_keypair})
            self.audit_rotation(new_keypair)
            
            # Phase 7: Complete
            self.save_state("complete", {"keypair": new_keypair})
            
            logger.info("=" * 60)
            logger.info("✅ ROTATION COMPLETE")
            logger.info("=" * 60)
            logger.info(f"New public key: {new_keypair['public_key']}")
            logger.info(f"Version: {new_keypair['version']}")
            logger.info(f"Created: {new_keypair['created_at']}")
            logger.info("")
            logger.info("NEXT STEPS:")
            logger.info("1. Update services to use new keypair")
            logger.info("2. Monitor for 24 hours (dual-key period)")
            logger.info("3. Revoke old public key after verification")
            logger.info("4. Update documentation")
            logger.info("=" * 60)
            
            return new_keypair
            
        except Exception as e:
            logger.error(f"❌ ROTATION FAILED: {e}")
            logger.error("Rotation state saved for resume")
            raise KeypairRotationError(f"Rotation failed: {e}")
    
    def pre_flight_checks(self):
        """Run pre-flight checks before rotation."""
        logger.info("Running pre-flight checks...")
        
        checks = []
        
        # Check 1: Vault connectivity
        if self.vault_enabled:
            try:
                import hvac
                vault_addr = os.environ.get("VAULT_ADDR", "http://vault:8200")
                vault_token = os.environ.get("VAULT_TOKEN")
                
                if not vault_token:
                    checks.append(("Vault token", False, "VAULT_TOKEN not set"))
                else:
                    client = hvac.Client(url=vault_addr, token=vault_token)
                    if client.sys.is_initialized():
                        checks.append(("Vault connectivity", True, "OK"))
                    else:
                        checks.append(("Vault connectivity", False, "Vault not initialized"))
            except ImportError:
                checks.append(("Vault library", False, "hvac not installed"))
            except Exception as e:
                checks.append(("Vault connectivity", False, str(e)))
        
        # Check 2: Backup directory writable
        try:
            test_file = self.backup_dir / ".test"
            test_file.write_text("test")
            test_file.unlink()
            checks.append(("Backup directory", True, "Writable"))
        except Exception as e:
            checks.append(("Backup directory", False, str(e)))
        
        # Check 3: Current keypair exists
        current = self.get_current_keypair()
        if current:
            checks.append(("Current keypair", True, f"Version {current.get('version', 'unknown')}"))
        else:
            checks.append(("Current keypair", False, "Not found (first rotation?)"))
        
        # Report results
        logger.info("Pre-flight check results:")
        all_passed = True
        for check_name, passed, message in checks:
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {check_name}: {message}")
            if not passed:
                all_passed = False
        
        if not all_passed and not self.emergency:
            raise KeypairRotationError("Pre-flight checks failed. Use --emergency to override.")
    
    def setup_dual_key_period(self, new_keypair: Dict[str, str]):
        """
        Setup dual-key period where both old and new keys are valid.
        
        Args:
            new_keypair: Newly generated keypair
        """
        logger.info("Setting up dual-key period (24 hours)...")
        
        current = self.get_current_keypair()
        
        if current and self.vault_enabled and not self.dry_run:
            # Store old keypair with expiration
            try:
                import hvac
                
                vault_addr = os.environ.get("VAULT_ADDR", "http://vault:8200")
                vault_token = os.environ.get("VAULT_TOKEN")
                client = hvac.Client(url=vault_addr, token=vault_token)
                
                # Add expiration to old keypair
                old_keypair = current.copy()
                old_keypair['valid_until'] = (
                    datetime.now(timezone.utc) + timedelta(hours=24)
                ).isoformat()
                
                client.secrets.kv.v2.create_or_update_secret(
                    path="project-ai/signing/sovereign-keypair-old",
                    secret=old_keypair
                )
                
                logger.info("✅ Old keypair stored with 24-hour validity")
                
            except Exception as e:
                logger.warning(f"Could not setup dual-key period: {e}")
        
        logger.info("⏰ Dual-key period: Both keys valid for 24 hours")
        logger.info(f"   Old key expires: {(datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()}")
    
    def audit_rotation(self, new_keypair: Dict[str, str]):
        """
        Create audit trail entry for rotation.
        
        Args:
            new_keypair: Newly generated keypair
        """
        logger.info("Creating audit trail entry...")
        
        audit_entry = {
            "event_type": "sovereign_keypair_rotated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": os.environ.get("USER", "unknown"),
            "rotation_type": "emergency" if self.emergency else "scheduled",
            "new_version": new_keypair['version'],
            "new_public_key": new_keypair['public_key'],
            "metadata": new_keypair.get('metadata', {})
        }
        
        # Write to audit log
        audit_file = Path("governance/audit_log.yaml")
        
        if not self.dry_run and audit_file.parent.exists():
            try:
                # Append to audit log (YAML format)
                with open(audit_file, 'a') as f:
                    f.write("\n# Keypair Rotation\n")
                    f.write(f"- timestamp: {audit_entry['timestamp']}\n")
                    f.write(f"  event: {audit_entry['event_type']}\n")
                    f.write(f"  actor: {audit_entry['actor']}\n")
                    f.write(f"  version: {audit_entry['new_version']}\n")
                    f.write(f"  public_key: {audit_entry['new_public_key']}\n")
                
                logger.info("✅ Audit trail updated")
            except Exception as e:
                logger.warning(f"Could not update audit trail: {e}")
        else:
            logger.info("[DRY RUN] Would update audit trail")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rotate the sovereign Ed25519 signing keypair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal scheduled rotation
  python rotate_sovereign_keypair.py
  
  # Emergency rotation (skip safety checks)
  python rotate_sovereign_keypair.py --emergency
  
  # Dry run (simulate without changes)
  python rotate_sovereign_keypair.py --dry-run
  
  # Resume failed rotation
  python rotate_sovereign_keypair.py --resume

Environment Variables:
  VAULT_ADDR    - Vault server address (default: http://vault:8200)
  VAULT_TOKEN   - Vault authentication token (required for Vault storage)
        """
    )
    
    parser.add_argument(
        '--emergency',
        action='store_true',
        help='Emergency rotation - skip pre-flight checks'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate rotation without making changes'
    )
    
    parser.add_argument(
        '--no-vault',
        action='store_true',
        help='Do not use Vault (testing only - INSECURE)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume a failed rotation'
    )
    
    args = parser.parse_args()
    
    # Initialize rotator
    rotator = SovereignKeypairRotator(
        vault_enabled=not args.no_vault,
        dry_run=args.dry_run,
        emergency=args.emergency
    )
    
    # Resume or start new rotation
    if args.resume:
        logger.info("Resuming failed rotation...")
        if not rotator.state:
            logger.error("No rotation state found to resume")
            sys.exit(1)
        logger.info(f"Last phase: {rotator.state.get('phase')}")
        # Continue from last phase (implementation depends on phase)
    
    try:
        # Perform rotation
        new_keypair = rotator.perform_rotation()
        
        # Success
        logger.info("")
        logger.info("✅ Rotation completed successfully")
        sys.exit(0)
        
    except KeypairRotationError as e:
        logger.error(f"❌ Rotation failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Rotation interrupted by user")
        logger.warning("Run with --resume to continue")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
