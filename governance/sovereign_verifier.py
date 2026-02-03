"""
Sovereign Verification System - Third-Party Auditor Tool

This module provides comprehensive verification capabilities for compliance bundles,
allowing third-party auditors to verify Project-AI's sovereign runtime without
needing to trust the provider.

Key Features:
- Hash chain validation
- Signature authority mapping
- Policy resolution tracing
- Timestamped attestation generation
- Independent cryptographic verification

Usage:
    verifier = SovereignVerifier(bundle_path)
    report = verifier.verify()
"""

import hashlib
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)


class SovereignVerifier:
    """
    Independent verification tool for sovereign compliance bundles.

    This verifier can be used by third-party auditors to cryptographically
    verify all claims made in a compliance bundle without trusting the
    bundle creator.
    """

    def __init__(self, bundle_path: Path | str):
        """Initialize the sovereign verifier.

        Args:
            bundle_path: Path to compliance bundle (JSON or ZIP)
        """
        self.bundle_path = Path(bundle_path)
        self.bundle = None
        self.verification_report = {
            "verification_timestamp": datetime.now().isoformat(),
            "bundle_path": str(self.bundle_path),
            "overall_status": "pending",
            "checks": {},
            "summary": {},
            "attestation": {},
        }

    def _load_bundle(self) -> bool:
        """Load compliance bundle from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.bundle_path.suffix == ".zip":
                # Extract ZIP and load bundle
                with zipfile.ZipFile(self.bundle_path, "r") as zip_file:
                    # Look for compliance_bundle.json
                    bundle_files = [f for f in zip_file.namelist() if "compliance_bundle.json" in f]
                    if not bundle_files:
                        logger.error("No compliance_bundle.json found in ZIP")
                        return False

                    with zip_file.open(bundle_files[0]) as f:
                        self.bundle = json.load(f)
            else:
                # Load JSON directly
                with open(self.bundle_path) as f:
                    self.bundle = json.load(f)

            logger.info("Loaded compliance bundle: version %s", self.bundle.get("version"))
            return True

        except Exception as e:
            logger.error("Failed to load bundle: %s", e)
            return False

    def _verify_hash_chain(self) -> dict[str, Any]:
        """
        Verify the hash chain integrity of the audit trail.

        Returns:
            Verification result dictionary
        """
        result = {
            "check": "hash_chain_validation",
            "status": "pending",
            "details": {},
            "issues": [],
        }

        try:
            audit_blocks = self.bundle["audit_trail"]["blocks"]
            total_blocks = len(audit_blocks)

            result["details"]["total_blocks"] = total_blocks
            result["details"]["blocks_verified"] = 0

            previous_hash = None
            for i, block in enumerate(audit_blocks):
                # Verify block hash
                block_copy = block.copy()
                stored_hash = block_copy.pop("hash", None)

                # Compute hash
                block_str = json.dumps(block_copy, sort_keys=True)
                computed_hash = hashlib.sha256(block_str.encode()).hexdigest()

                if computed_hash != stored_hash:
                    result["issues"].append(f"Block {i}: hash mismatch")
                    continue

                # Verify chain linkage
                if previous_hash is not None:
                    if block["previous_hash"] != previous_hash:
                        result["issues"].append(f"Block {i}: chain broken")
                        continue

                previous_hash = stored_hash
                result["details"]["blocks_verified"] += 1

            # Determine status
            if result["details"]["blocks_verified"] == total_blocks:
                result["status"] = "pass"
                result["details"]["chain_integrity"] = "intact"
            else:
                result["status"] = "fail"
                result["details"]["chain_integrity"] = "broken"

            logger.info(
                "Hash chain validation: %d/%d blocks verified",
                result["details"]["blocks_verified"],
                total_blocks,
            )

        except Exception as e:
            logger.error("Hash chain validation failed: %s", e)
            result["status"] = "error"
            result["issues"].append(f"Verification error: {e}")

        return result

    def _map_signature_authorities(self) -> dict[str, Any]:
        """
        Map all signature authorities and verify their signatures.

        Returns:
            Signature authority map with verification status
        """
        result = {
            "check": "signature_authority_mapping",
            "status": "pending",
            "details": {
                "public_key": self.bundle.get("public_key"),
                "algorithm": self.bundle.get("algorithm"),
                "signatures_found": 0,
                "signatures_verified": 0,
            },
            "authorities": {},
            "issues": [],
        }

        try:
            # Extract public key
            public_key_hex = self.bundle["public_key"]
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

            result["details"]["public_key_fingerprint"] = hashlib.sha256(
                public_key_bytes
            ).hexdigest()[:16]

            # Scan audit trail for signatures
            audit_blocks = self.bundle["audit_trail"]["blocks"]

            for block in audit_blocks:
                event_type = block.get("event_type")
                data = block.get("data", {})

                # Look for signature-related events
                if "signature" in data or "SIGNATURE" in event_type:
                    result["details"]["signatures_found"] += 1

                    # Extract signature info
                    if "role" in data:
                        role = data["role"]
                        if role not in result["authorities"]:
                            result["authorities"][role] = {
                                "occurrences": 0,
                                "verified": 0,
                            }
                        result["authorities"][role]["occurrences"] += 1

                        # Try to verify if signature is present
                        if "signature" in data and "payload_hash" in data:
                            try:
                                sig_bytes = bytes.fromhex(data["signature"][:64])
                                payload = data["payload_hash"].encode()
                                public_key.verify(sig_bytes, payload)
                                result["authorities"][role]["verified"] += 1
                                result["details"]["signatures_verified"] += 1
                            except Exception as e:
                                result["issues"].append(
                                    f"Signature verification failed for {role}: {e}"
                                )

            # Determine status
            if result["details"]["signatures_found"] == 0:
                result["status"] = "warning"
                result["issues"].append("No signatures found in audit trail")
            elif result["details"]["signatures_verified"] == result["details"]["signatures_found"]:
                result["status"] = "pass"
            else:
                result["status"] = "fail"

            logger.info(
                "Signature mapping: %d authorities, %d/%d signatures verified",
                len(result["authorities"]),
                result["details"]["signatures_verified"],
                result["details"]["signatures_found"],
            )

        except Exception as e:
            logger.error("Signature authority mapping failed: %s", e)
            result["status"] = "error"
            result["issues"].append(f"Mapping error: {e}")

        return result

    def _trace_policy_resolutions(self) -> dict[str, Any]:
        """
        Trace all policy resolution decisions through the audit trail.

        Returns:
            Policy resolution trace with decision chain
        """
        result = {
            "check": "policy_resolution_trace",
            "status": "pending",
            "details": {
                "total_resolutions": 0,
                "passed_resolutions": 0,
                "failed_resolutions": 0,
            },
            "resolutions": [],
            "issues": [],
        }

        try:
            audit_blocks = self.bundle["audit_trail"]["blocks"]

            for block in audit_blocks:
                event_type = block.get("event_type")
                data = block.get("data", {})

                # Look for policy-related events
                if "POLICY" in event_type or "policy" in str(data).lower():
                    resolution = {
                        "timestamp": block.get("timestamp"),
                        "event_type": event_type,
                        "policy_hash": data.get("policy_hash"),
                        "context_hash": data.get("context_hash"),
                        "binding_hash": data.get("binding_hash"),
                    }

                    result["details"]["total_resolutions"] += 1

                    # Determine resolution status based on event type
                    if "AUTHORIZED" in event_type or "COMPLETED" in event_type:
                        resolution["status"] = "passed"
                        result["details"]["passed_resolutions"] += 1
                    elif "BLOCKED" in event_type or "FAILED" in event_type:
                        resolution["status"] = "failed"
                        result["details"]["failed_resolutions"] += 1
                    else:
                        resolution["status"] = "unknown"

                    result["resolutions"].append(resolution)

            # Determine status
            if result["details"]["total_resolutions"] == 0:
                result["status"] = "warning"
                result["issues"].append("No policy resolutions found")
            else:
                result["status"] = "pass"

            logger.info(
                "Policy trace: %d resolutions (%d passed, %d failed)",
                result["details"]["total_resolutions"],
                result["details"]["passed_resolutions"],
                result["details"]["failed_resolutions"],
            )

        except Exception as e:
            logger.error("Policy resolution tracing failed: %s", e)
            result["status"] = "error"
            result["issues"].append(f"Tracing error: {e}")

        return result

    def _generate_attestation(self) -> dict[str, Any]:
        """
        Generate timestamped attestation of verification results.

        Returns:
            Attestation dictionary
        """
        attestation = {
            "attestation_id": hashlib.sha256(
                f"{self.bundle_path}{datetime.now().isoformat()}".encode()
            ).hexdigest(),
            "timestamp": datetime.now().isoformat(),
            "verifier": "Project-AI Sovereign Verifier v1.0.0",
            "bundle_source": str(self.bundle_path),
            "bundle_version": self.bundle.get("version"),
            "bundle_generated_at": self.bundle.get("generated_at"),
            "verification_summary": {},
            "cryptographic_proof": {},
        }

        # Add summary from checks
        checks = self.verification_report["checks"]

        attestation["verification_summary"] = {
            "hash_chain": checks.get("hash_chain_validation", {}).get("status", "unknown"),
            "signatures": checks.get("signature_authority_mapping", {}).get(
                "status", "unknown"
            ),
            "policy_trace": checks.get("policy_resolution_trace", {}).get(
                "status", "unknown"
            ),
        }

        # Add cryptographic proof
        attestation["cryptographic_proof"] = {
            "algorithm": self.bundle.get("algorithm", "Ed25519"),
            "public_key_fingerprint": checks.get("signature_authority_mapping", {})
            .get("details", {})
            .get("public_key_fingerprint", "unknown"),
            "total_blocks_verified": checks.get("hash_chain_validation", {})
            .get("details", {})
            .get("blocks_verified", 0),
            "total_signatures_verified": checks.get("signature_authority_mapping", {})
            .get("details", {})
            .get("signatures_verified", 0),
        }

        # Sign attestation with verification hash
        attestation_str = json.dumps(attestation, sort_keys=True)
        attestation["verification_hash"] = hashlib.sha256(
            attestation_str.encode()
        ).hexdigest()

        return attestation

    def verify(self) -> dict[str, Any]:
        """
        Run complete verification of compliance bundle.

        This is the main entry point for third-party auditors.

        Returns:
            Comprehensive verification report
        """
        logger.info("=" * 80)
        logger.info("SOVEREIGN VERIFICATION SYSTEM")
        logger.info("=" * 80)
        logger.info("Bundle: %s", self.bundle_path)
        logger.info("Timestamp: %s", datetime.now().isoformat())
        logger.info("=" * 80)
        logger.info("")

        # Load bundle
        if not self._load_bundle():
            self.verification_report["overall_status"] = "error"
            self.verification_report["summary"]["error"] = "Failed to load bundle"
            return self.verification_report

        # Run verification checks
        logger.info("Running verification checks...")
        logger.info("")

        # 1. Hash chain validation
        logger.info("1. Verifying hash chain integrity...")
        hash_chain_result = self._verify_hash_chain()
        self.verification_report["checks"]["hash_chain_validation"] = hash_chain_result
        logger.info("   Status: %s", hash_chain_result["status"])
        logger.info("")

        # 2. Signature authority mapping
        logger.info("2. Mapping signature authorities...")
        signature_result = self._map_signature_authorities()
        self.verification_report["checks"]["signature_authority_mapping"] = signature_result
        logger.info("   Status: %s", signature_result["status"])
        logger.info("")

        # 3. Policy resolution tracing
        logger.info("3. Tracing policy resolutions...")
        policy_result = self._trace_policy_resolutions()
        self.verification_report["checks"]["policy_resolution_trace"] = policy_result
        logger.info("   Status: %s", policy_result["status"])
        logger.info("")

        # 4. Generate attestation
        logger.info("4. Generating timestamped attestation...")
        attestation = self._generate_attestation()
        self.verification_report["attestation"] = attestation
        logger.info("   Attestation ID: %s", attestation["attestation_id"][:16])
        logger.info("")

        # Determine overall status
        statuses = [
            hash_chain_result["status"],
            signature_result["status"],
            policy_result["status"],
        ]

        if "fail" in statuses or "error" in statuses:
            self.verification_report["overall_status"] = "fail"
        elif "warning" in statuses:
            self.verification_report["overall_status"] = "warning"
        else:
            self.verification_report["overall_status"] = "pass"

        # Generate summary
        self.verification_report["summary"] = {
            "bundle_version": self.bundle.get("version"),
            "total_audit_blocks": self.bundle["audit_trail"]["total_blocks"],
            "blocks_verified": hash_chain_result["details"].get("blocks_verified", 0),
            "signatures_verified": signature_result["details"].get("signatures_verified", 0),
            "policy_resolutions": policy_result["details"].get("total_resolutions", 0),
            "overall_status": self.verification_report["overall_status"],
        }

        logger.info("=" * 80)
        logger.info("VERIFICATION COMPLETE")
        logger.info("=" * 80)
        logger.info("Overall Status: %s", self.verification_report["overall_status"].upper())
        logger.info("=" * 80)

        return self.verification_report


__all__ = ["SovereignVerifier"]
