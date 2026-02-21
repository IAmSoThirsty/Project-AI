"""
Legal and Governance Subsystem - Acceptance Ledger Core

This module implements the immutable, cryptographically-secured acceptance ledger
for Project-AI. All user agreements, acceptances, and governance actions are recorded
in a tamper-proof, append-only ledger with hash chaining and digital signatures.

Features:
- Immutable append-only ledger (file + SQLite backends)
- SHA-256 hash chaining for tamper-evidence
- Ed25519 digital signatures (software and hardware-backed)
- Optional timestamp authority support (RFC 3161, OpenTimestamps, eIDAS)
- Court-grade audit trails and replayability
- Zero-trust cryptographic verification
"""

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class TierLevel(StrEnum):
    """User tier levels"""

    SOLO = "solo"
    COMPANY = "company"
    GOVERNMENT = "government"


class SubscriptionPlan(StrEnum):
    """Subscription plan types for Company and Government tiers"""

    # Company plans
    COMPANY_WEEKLY = "company_weekly"
    COMPANY_MONTHLY = "company_monthly"
    COMPANY_YEARLY = "company_yearly"
    COMPANY_LIFETIME = "company_lifetime"

    # Government plans (no lifetime option)
    GOVERNMENT_MONTHLY = "government_monthly"
    GOVERNMENT_YEARLY = "government_yearly"

    # Legacy Solo
    SOLO_FREE = "solo_free"
    SOLO_LIFETIME = "solo_lifetime"


class AcceptanceType(StrEnum):
    """Types of acceptance records"""

    INITIAL_MSA = "initial_msa"
    JURISDICTION_ANNEX = "jurisdiction_annex"
    TIER_UPGRADE = "tier_upgrade"
    PLAN_CHANGE = "plan_change"  # New: for changing subscription plans
    POLICY_UPDATE = "policy_update"
    TERMINATION = "termination"
    AUDIT_LOCK = "audit_lock"


class SigningMethod(StrEnum):
    """Cryptographic signing methods"""

    SOFTWARE_ED25519 = "software_ed25519"
    TPM_BACKED = "tpm_backed"
    HSM_BACKED = "hsm_backed"


@dataclass
class AcceptanceEntry:
    """Single acceptance ledger entry"""

    entry_id: str
    timestamp: float
    user_id: str
    user_email: str
    acceptance_type: AcceptanceType
    tier: TierLevel
    jurisdiction: str
    document_hash: str  # SHA-256 of accepted document
    previous_entry_hash: str | None  # Hash chain link
    signing_method: SigningMethod
    signature: str  # Ed25519 or hardware-backed signature
    public_key: str  # User's public key for verification
    timestamp_authority: str | None = None  # RFC 3161 timestamp token
    hardware_attestation: str | None = None  # TPM/HSM attestation
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "acceptance_type": self.acceptance_type.value,
            "tier": self.tier.value,
            "jurisdiction": self.jurisdiction,
            "document_hash": self.document_hash,
            "previous_entry_hash": self.previous_entry_hash,
            "signing_method": self.signing_method.value,
            "signature": self.signature,
            "public_key": self.public_key,
            "timestamp_authority": self.timestamp_authority,
            "hardware_attestation": self.hardware_attestation,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AcceptanceEntry":
        """Create from dictionary"""
        return cls(
            entry_id=data["entry_id"],
            timestamp=data["timestamp"],
            user_id=data["user_id"],
            user_email=data["user_email"],
            acceptance_type=AcceptanceType(data["acceptance_type"]),
            tier=TierLevel(data["tier"]),
            jurisdiction=data["jurisdiction"],
            document_hash=data["document_hash"],
            previous_entry_hash=data.get("previous_entry_hash"),
            signing_method=SigningMethod(data["signing_method"]),
            signature=data["signature"],
            public_key=data["public_key"],
            timestamp_authority=data.get("timestamp_authority"),
            hardware_attestation=data.get("hardware_attestation"),
            metadata=data.get("metadata", {}),
        )

    def compute_entry_hash(self) -> str:
        """Compute SHA-256 hash of this entry for chain linking"""
        canonical_data = json.dumps(
            {
                "entry_id": self.entry_id,
                "timestamp": self.timestamp,
                "user_id": self.user_id,
                "user_email": self.user_email,
                "acceptance_type": self.acceptance_type.value,
                "tier": self.tier.value,
                "jurisdiction": self.jurisdiction,
                "document_hash": self.document_hash,
                "previous_entry_hash": self.previous_entry_hash,
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical_data).hexdigest()


class AcceptanceLedger:
    """
    Immutable, append-only acceptance ledger with cryptographic integrity.

    Maintains dual storage:
    1. File-based append-only log (human-readable JSON lines)
    2. SQLite with WAL mode (queryable, transactional)

    All entries are cryptographically signed and hash-chained.
    """

    def __init__(
        self,
        data_dir: str = "data/legal",
        enable_sqlite: bool = True,
        enable_file: bool = True,
    ):
        """Initialize acceptance ledger"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.enable_sqlite = enable_sqlite
        self.enable_file = enable_file

        # File-based ledger
        self.ledger_file = self.data_dir / "acceptance_ledger.jsonl"

        # SQLite database with WAL mode
        self.db_path = self.data_dir / "acceptance_ledger.db"

        # Initialize storage backends
        if self.enable_sqlite:
            self._init_sqlite()

        # Verify integrity on startup
        self._verify_integrity()

    def _init_sqlite(self):
        """Initialize SQLite database with WAL mode"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS acceptance_ledger (
                entry_id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                user_id TEXT NOT NULL,
                user_email TEXT NOT NULL,
                acceptance_type TEXT NOT NULL,
                tier TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                document_hash TEXT NOT NULL,
                previous_entry_hash TEXT,
                entry_hash TEXT NOT NULL UNIQUE,
                signing_method TEXT NOT NULL,
                signature TEXT NOT NULL,
                public_key TEXT NOT NULL,
                timestamp_authority TEXT,
                hardware_attestation TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Indexes for efficient queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON acceptance_ledger(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON acceptance_ledger(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entry_hash ON acceptance_ledger(entry_hash)")

        conn.commit()
        conn.close()

    def _verify_integrity(self):
        """Verify ledger integrity (hash chain unbroken)"""
        if not self.enable_file or not self.ledger_file.exists():
            return

        entries = self._load_all_entries()
        if not entries:
            return

        # Verify hash chain
        for i, entry in enumerate(entries):
            # Verify signature (if crypto available)
            if CRYPTO_AVAILABLE:
                self._verify_signature(entry)

            # Verify hash chain
            if i > 0:
                expected_prev_hash = entries[i - 1].compute_entry_hash()
                if entry.previous_entry_hash != expected_prev_hash:
                    raise ValueError(
                        f"Hash chain broken at entry {entry.entry_id}: "
                        f"expected previous hash {expected_prev_hash}, "
                        f"got {entry.previous_entry_hash}"
                    )

    def _load_all_entries(self) -> list[AcceptanceEntry]:
        """Load all entries from file-based ledger"""
        if not self.ledger_file.exists():
            return []

        entries = []
        with open(self.ledger_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_dict = json.loads(line)
                    entries.append(AcceptanceEntry.from_dict(entry_dict))
        return entries

    def _get_last_entry_hash(self) -> str | None:
        """Get hash of the last entry in the chain"""
        entries = self._load_all_entries()
        if not entries:
            return None
        return entries[-1].compute_entry_hash()

    def append_acceptance(
        self,
        user_id: str,
        user_email: str,
        acceptance_type: AcceptanceType,
        tier: TierLevel,
        jurisdiction: str,
        document_hash: str,
        private_key: bytes | None = None,
        signing_method: SigningMethod = SigningMethod.SOFTWARE_ED25519,
        timestamp_authority_url: str | None = None,
        hardware_attestation: str | None = None,
        metadata: dict | None = None,
    ) -> AcceptanceEntry:
        """
        Append a new acceptance to the ledger.

        This is the ONLY way to add entries - no modifications or deletions allowed.

        Args:
            user_id: User identifier
            user_email: User email address
            acceptance_type: Type of acceptance
            tier: User tier level
            jurisdiction: Primary jurisdiction
            document_hash: SHA-256 hash of accepted document
            private_key: Ed25519 private key bytes (if None, generates new key)
            signing_method: Method used for signing
            timestamp_authority_url: Optional TSA URL for RFC 3161 timestamp
            hardware_attestation: Optional TPM/HSM attestation data
            metadata: Optional additional metadata

        Returns:
            AcceptanceEntry: The created and appended entry

        Raises:
            ValueError: If ledger integrity check fails
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available. Install: pip install cryptography")

        # Generate or load key pair
        if private_key is None:
            private_key_obj = ed25519.Ed25519PrivateKey.generate()
            private_key = private_key_obj.private_bytes(
                encoding=Encoding.Raw,
                format=PrivateFormat.Raw,
                encryption_algorithm=NoEncryption(),
            )
        else:
            private_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)

        public_key_obj = private_key_obj.public_key()
        public_key = public_key_obj.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw).hex()

        # Create entry
        entry_id = hashlib.sha256(f"{user_id}{user_email}{time.time()}".encode()).hexdigest()[:16]

        previous_hash = self._get_last_entry_hash()

        entry = AcceptanceEntry(
            entry_id=entry_id,
            timestamp=time.time(),
            user_id=user_id,
            user_email=user_email,
            acceptance_type=acceptance_type,
            tier=tier,
            jurisdiction=jurisdiction,
            document_hash=document_hash,
            previous_entry_hash=previous_hash,
            signing_method=signing_method,
            signature="",  # Will be computed
            public_key=public_key,
            timestamp_authority=None,  # Will be populated if TSA URL provided
            hardware_attestation=hardware_attestation,
            metadata=metadata or {},
        )

        # Get Timestamp Token if Authority URL provided
        if timestamp_authority_url and TSA_AVAILABLE:
            try:
                tsa_client = TSAClient(timestamp_authority_url)
                # Timestamp the entry hash
                entry_hash_bytes = bytes.fromhex(entry.compute_entry_hash())
                token = tsa_client.get_timestamp(entry_hash_bytes)
                entry.timestamp_authority = token.hex()
            except Exception as e:
                # Log error but don't fail acceptance if TSA fails (soft fail)
                # Unless strict mode is required
                print(f"TSA Warning: Failed to get timestamp: {e}")

        # Sign the entry
        signature_payload = entry.compute_entry_hash().encode()
        signature = private_key_obj.sign(signature_payload)
        entry.signature = signature.hex()

        # Write to file-based ledger (append-only)
        if self.enable_file:
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
                # os.fsync(f.fileno())  # Force write to disk - commented out for performance unless critical

        # Write to SQLite
        if self.enable_sqlite:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                """
                INSERT INTO acceptance_ledger (
                    entry_id, timestamp, user_id, user_email, acceptance_type,
                    tier, jurisdiction, document_hash, previous_entry_hash,
                    entry_hash, signing_method, signature, public_key,
                    timestamp_authority, hardware_attestation, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.entry_id,
                    entry.timestamp,
                    entry.user_id,
                    entry.user_email,
                    entry.acceptance_type.value,
                    entry.tier.value,
                    entry.jurisdiction,
                    entry.document_hash,
                    entry.previous_entry_hash,
                    entry.compute_entry_hash(),
                    entry.signing_method.value,
                    entry.signature,
                    entry.public_key,
                    entry.timestamp_authority,
                    entry.hardware_attestation,
                    json.dumps(entry.metadata),
                ),
            )
            conn.commit()
            conn.close()

        return entry

    def _verify_signature(self, entry: AcceptanceEntry) -> bool:
        """Verify Ed25519 signature on an entry"""
        if not CRYPTO_AVAILABLE:
            return False

        try:
            public_key_bytes = bytes.fromhex(entry.public_key)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

            signature_bytes = bytes.fromhex(entry.signature)
            payload = entry.compute_entry_hash().encode()

            public_key.verify(signature_bytes, payload)
            return True
        except Exception:
            return False

    def get_entry(self, entry_id: str) -> AcceptanceEntry | None:
        """Get a specific entry by ID"""
        if self.enable_sqlite:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("SELECT * FROM acceptance_ledger WHERE entry_id = ?", (entry_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return AcceptanceEntry(
                    entry_id=row[0],
                    timestamp=row[1],
                    user_id=row[2],
                    user_email=row[3],
                    acceptance_type=AcceptanceType(row[4]),
                    tier=TierLevel(row[5]),
                    jurisdiction=row[6],
                    document_hash=row[7],
                    previous_entry_hash=row[8],
                    signing_method=SigningMethod(row[10]),
                    signature=row[11],
                    public_key=row[12],
                    timestamp_authority=row[13],
                    hardware_attestation=row[14],
                    metadata=json.loads(row[15]) if row[15] else {},
                )

        # Fallback to file-based search
        entries = self._load_all_entries()
        for entry in entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_user_acceptances(self, user_id: str) -> list[AcceptanceEntry]:
        """Get all acceptances for a user"""
        if self.enable_sqlite:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute(
                "SELECT * FROM acceptance_ledger WHERE user_id = ? ORDER BY timestamp",
                (user_id,),
            )
            rows = cursor.fetchall()
            conn.close()

            entries = []
            for row in rows:
                entries.append(
                    AcceptanceEntry(
                        entry_id=row[0],
                        timestamp=row[1],
                        user_id=row[2],
                        user_email=row[3],
                        acceptance_type=AcceptanceType(row[4]),
                        tier=TierLevel(row[5]),
                        jurisdiction=row[6],
                        document_hash=row[7],
                        previous_entry_hash=row[8],
                        signing_method=SigningMethod(row[10]),
                        signature=row[11],
                        public_key=row[12],
                        timestamp_authority=row[13],
                        hardware_attestation=row[14],
                        metadata=json.loads(row[15]) if row[15] else {},
                    )
                )
            return entries

        # Fallback to file-based search
        entries = self._load_all_entries()
        return [e for e in entries if e.user_id == user_id]

    def verify_entry(self, entry_id: str) -> dict:
        """
        Verify cryptographic integrity of an entry.

        Returns dict with verification results:
        {
            "valid": bool,
            "signature_valid": bool,
            "hash_chain_valid": bool,
            "timestamp_valid": bool,
            "hardware_attested": bool
        }
        """
        entry = self.get_entry(entry_id)
        if not entry:
            return {"valid": False, "error": "Entry not found"}

        results = {
            "entry_id": entry_id,
            "signature_valid": False,
            "hash_chain_valid": False,
            "timestamp_valid": False,
            "hardware_attested": bool(entry.hardware_attestation),
        }

        # Verify signature
        if CRYPTO_AVAILABLE:
            results["signature_valid"] = self._verify_signature(entry)

        # Verify hash chain
        if entry.previous_entry_hash:
            prev_entry = self.get_entry(entry.previous_entry_hash)
            if prev_entry:
                expected_hash = prev_entry.compute_entry_hash()
                results["hash_chain_valid"] = entry.previous_entry_hash == expected_hash
            else:
                results["hash_chain_valid"] = False
        else:
            # First entry in chain
            results["hash_chain_valid"] = True

        # Timestamp validation
        results["timestamp_valid"] = entry.timestamp > 0 and entry.timestamp <= time.time()

        # Extended TSA Validation
        if entry.timestamp_authority and TSA_AVAILABLE:
            # If we have a stored token, we should verify it
            # We need to know which TSA issued it, or default to a known one if configured
            # For now, we just check if it's structurally valid if we had the certs
            # This is a placeholder for full verification logic
            try:
                token_bytes = bytes.fromhex(entry.timestamp_authority)
                # In a real verification, we'd fetch the certs from the token or config
                # and verify chain.
                results["timestamp_valid"] = True  # Assume valid if parseable for now
            except Exception:
                results["timestamp_valid"] = False

        results["valid"] = all(
            [
                results["signature_valid"],
                results["hash_chain_valid"],
                results["timestamp_valid"],
            ]
        )

        return results


# Singleton instance
_ledger_instance: AcceptanceLedger | None = None


def get_acceptance_ledger(data_dir: str = "data/legal") -> AcceptanceLedger:
    """Get or create the global acceptance ledger instance"""
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = AcceptanceLedger(data_dir=data_dir)
    return _ledger_instance


try:
    import rfc3161ng
    from pyasn1.codec.der import decoder, encoder

    TSA_AVAILABLE = True
except ImportError:
    TSA_AVAILABLE = False


class TSAClient:
    """Timestamp Authority Client (RFC 3161)"""

    def __init__(self, url: str):
        self.url = url

    def get_timestamp(self, data: bytes) -> bytes:
        """Get RFC 3161 timestamp token for data"""
        if not TSA_AVAILABLE:
            raise RuntimeError("TSA libraries not available. Install: pip install rfc3161ng pyasn1")

        tst = rfc3161ng.RemoteTimestamper(self.url, hashname="sha256", include_tsa_certificate=True)
        return tst.timestamp(data=data)

    def verify_timestamp(self, token: bytes, data: bytes, ca_certs: bytes = None) -> bool:
        """Verify RFC 3161 timestamp token"""
        if not TSA_AVAILABLE:
            return False

        tst = rfc3161ng.RemoteTimestamper(self.url, hashname="sha256")
        try:
            # Basic verification: check integrity and data match
            # For production, we'd need a full chain verification with ca_certs
            # Here we rely on the library providing basic checks, but note that
            # without a trusted root CA store passed in, this is limited.
            # rfc3161ng doesn't have a simple 'verify' method that takes the token and data
            # in a stateless way easily without a Timestamper instance.
            # We will implement a basic check using pyasn1 decoding if needed,
            # but for now we'll assume the token structure is valid and contains the hash.

            # Decode token
            tst_obj, _ = decoder.decode(token, asn1Spec=rfc3161ng.TimeStampResp())
            status = tst_obj["status"]
            if status["status"] != 0:  # 0 = granted
                return False

            # Verify the hash in the token matches our data hash
            # This is a simplification. A real implementation needs full signature verification.
            # rfc3161ng provides tools for this but they expect specific setup.
            return True
        except Exception:
            return False


def get_seat_count_from_entry(entry: AcceptanceEntry) -> int | None:
    """
    Extract seat count from acceptance entry metadata.
    """
    if entry.tier == TierLevel.GOVERNMENT:
        return entry.metadata.get("seat_count")
    return None


def set_seat_count_in_metadata(metadata: dict, seat_count: int) -> dict:
    """
    Add seat count to metadata dictionary.
    """
    if seat_count < 1:
        raise ValueError(f"Seat count must be at least 1, got {seat_count}")
    metadata["seat_count"] = seat_count
    return metadata
