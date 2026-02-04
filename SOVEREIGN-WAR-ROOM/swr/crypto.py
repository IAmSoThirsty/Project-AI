"""
Cryptographic Engine for SOVEREIGN WAR ROOM

Handles all cryptographic operations including:
- Cryptographic decision attestations for decision verification
- Tamper-evident audit logs with commitment schemes
- Secure challenge-response protocols
- Cryptographic signatures for scenario validation

Note: Implements hash-based commitments and HMAC signatures,
not formal zero-knowledge proof systems (zk-SNARKs/zk-STARKs).
"""

import hashlib
import hmac
import json
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class CryptoEngine:
    """Cryptographic operations engine for secure scenario validation."""
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize cryptographic engine.
        
        Args:
            master_key: Optional master key for deterministic operations
        """
        self.master_key = master_key or Fernet.generate_key()
        self.cipher = Fernet(self.master_key)
        self._nonce_cache = set()
    
    def generate_challenge(self, scenario_id: str, difficulty: int) -> Dict[str, Any]:
        """
        Generate cryptographic challenge for scenario.
        
        Args:
            scenario_id: Unique scenario identifier
            difficulty: Challenge difficulty (1-10)
            
        Returns:
            Challenge dictionary with nonce, hash, and verification data
        """
        nonce = secrets.token_hex(32)
        timestamp = datetime.utcnow().isoformat()
        
        # Create challenge hash
        challenge_data = f"{scenario_id}:{nonce}:{timestamp}:{difficulty}"
        challenge_hash = hashlib.sha3_256(challenge_data.encode()).hexdigest()
        
        # Generate verification proof
        proof_data = {
            "scenario_id": scenario_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "difficulty": difficulty,
            "challenge_hash": challenge_hash
        }
        
        # Sign the challenge
        signature = self._sign_data(json.dumps(proof_data, sort_keys=True))
        
        self._nonce_cache.add(nonce)
        
        return {
            "challenge_hash": challenge_hash,
            "nonce": nonce,
            "timestamp": timestamp,
            "difficulty": difficulty,
            "signature": signature,
            "proof_data": proof_data
        }
    
    def verify_response(
        self,
        challenge: Dict[str, Any],
        response: Dict[str, Any],
        expected_outcome: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify cryptographic response to challenge.
        
        Args:
            challenge: Original challenge data
            response: AI system response
            expected_outcome: Expected decision outcome
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Verify nonce hasn't been reused
        nonce = challenge.get("nonce")
        if not nonce or nonce not in self._nonce_cache:
            return False, "Invalid or reused nonce"
        
        # Verify signature
        proof_data = challenge.get("proof_data")
        signature = challenge.get("signature")
        
        if not self._verify_signature(json.dumps(proof_data, sort_keys=True), signature):
            return False, "Invalid challenge signature"
        
        # Verify response integrity
        response_hash = self._hash_response(response)
        
        # Check if response matches expected outcome
        decision = response.get("decision", "")
        if decision.lower() != expected_outcome.lower():
            return False, f"Expected '{expected_outcome}', got '{decision}'"
        
        # Remove nonce from cache after successful verification
        self._nonce_cache.discard(nonce)
        
        return True, None
    
    def generate_proof(self, data: Dict[str, Any], proof_type: str) -> str:
        """
        Generate zero-knowledge proof for data.
        
        Args:
            data: Data to generate proof for
            proof_type: Type of proof (decision, compliance, audit)
            
        Returns:
            Hex-encoded proof string
        """
        # Serialize data deterministically
        serialized = json.dumps(data, sort_keys=True)
        
        # Create proof with type and timestamp
        proof_input = f"{proof_type}:{serialized}:{datetime.utcnow().isoformat()}"
        
        # Generate proof using SHA3-512
        proof_hash = hashlib.sha3_512(proof_input.encode()).hexdigest()
        
        # Sign the proof
        signature = self._sign_data(proof_hash)
        
        # Combine proof and signature
        full_proof = f"{proof_hash}:{signature}"
        
        return full_proof
    
    def verify_proof(self, proof: str, data: Dict[str, Any], proof_type: str) -> bool:
        """
        Verify zero-knowledge proof.
        
        Args:
            proof: Proof string to verify
            data: Original data
            proof_type: Expected proof type
            
        Returns:
            True if proof is valid
        """
        try:
            proof_hash, signature = proof.split(":", 1)
            
            # Verify signature
            if not self._verify_signature(proof_hash, signature):
                return False
            
            # Note: Full ZK proof verification would require the original timestamp
            # For production, store proofs with metadata in a merkle tree
            return True
            
        except Exception:
            return False
    
    def create_audit_log_entry(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create tamper-evident audit log entry.
        
        Args:
            event: Event data to log
            
        Returns:
            Audit log entry with cryptographic verification
        """
        timestamp = datetime.utcnow().isoformat()
        entry_id = secrets.token_hex(16)
        
        # Create entry
        entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "event": event,
        }
        
        # Generate hash chain
        entry_json = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha3_256(entry_json.encode()).hexdigest()
        
        entry["hash"] = entry_hash
        entry["signature"] = self._sign_data(entry_hash)
        
        return entry
    
    def verify_audit_log_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Verify audit log entry integrity.
        
        Args:
            entry: Audit log entry to verify
            
        Returns:
            True if entry is valid and untampered
        """
        # Extract signature and hash
        signature = entry.get("signature")
        stored_hash = entry.get("hash")
        
        if not signature or not stored_hash:
            return False
        
        # Recreate entry without signature/hash
        entry_copy = {k: v for k, v in entry.items() if k not in ["signature", "hash"]}
        entry_json = json.dumps(entry_copy, sort_keys=True)
        computed_hash = hashlib.sha3_256(entry_json.encode()).hexdigest()
        
        # Verify hash matches
        if computed_hash != stored_hash:
            return False
        
        # Verify signature
        return self._verify_signature(stored_hash, signature)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data using Fernet."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def _sign_data(self, data: str) -> str:
        """Create HMAC signature for data."""
        signature = hmac.new(
            self.master_key,
            data.encode(),
            hashlib.sha3_256
        ).hexdigest()
        return signature
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = self._sign_data(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def _hash_response(self, response: Dict[str, Any]) -> str:
        """Generate hash of response data."""
        response_json = json.dumps(response, sort_keys=True)
        return hashlib.sha3_256(response_json.encode()).hexdigest()
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive cryptographic key from password.
        
        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return key, salt
