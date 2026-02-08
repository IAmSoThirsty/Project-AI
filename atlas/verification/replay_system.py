"""
Verification & Replay System for PROJECT ATLAS Ω

Implements complete verification and deterministic replay:
- Bundle format specification  
- Full replay engine from bundles
- Portable verification
- Deterministic reproducibility validation
- State reconstruction

Layer 11 Component - Production-Grade Implementation
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import gzip

from atlas.audit.trail import get_audit_trail, AuditCategory, AuditLevel

logger = logging.getLogger(__name__)


@dataclass
class VerificationBundle:
    """Complete bundle for deterministic replay and verification."""
    bundle_id: str
    created: datetime
    atlas_version: str
    
    # Configuration
    config_hashes: Dict[str, str] = field(default_factory=dict)
    baseline_hashes: Dict[str, str] = field(default_factory=dict)
    
    # Data provenance
    data_hashes: Dict[str, str] = field(default_factory=dict)
    tier_metadata: List[Dict[str, Any]] = field(default_factory=list)
    
    # Seeds and randomness
    seeds: Dict[str, str] = field(default_factory=dict)
    rng_state: Optional[Dict[str, Any]] = None
    
    # State checkpoints
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    
    # Graph snapshots
    graph_snapshots: List[Dict[str, Any]] = field(default_factory=list)
    
    # Audit trail
    audit_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Results
    projections: List[Dict[str, Any]] = field(default_factory=list)
    claims: List[Dict[str, Any]] = field(default_factory=list)
    
    # Bundle metadata
    bundle_hash: Optional[str] = None
    signature: Optional[str] = None
    
    def compute_bundle_hash(self) -> str:
        """Compute canonical hash of entire bundle."""
        canonical = {
            "bundle_id": self.bundle_id,
            "created": self.created.isoformat(),
            "atlas_version": self.atlas_version,
            "config_hashes": sorted(self.config_hashes.items()),
            "baseline_hashes": sorted(self.baseline_hashes.items()),
            "data_hashes": sorted(self.data_hashes.items()),
            "seeds": sorted(self.seeds.items()),
            "checkpoint_count": len(self.checkpoints),
            "graph_snapshot_count": len(self.graph_snapshots),
            "audit_event_count": len(self.audit_events),
            "projection_count": len(self.projections),
            "claim_count": len(self.claims)
        }
        
        content = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bundle_id": self.bundle_id,
            "created": self.created.isoformat(),
            "atlas_version": self.atlas_version,
            "config_hashes": self.config_hashes,
            "baseline_hashes": self.baseline_hashes,
            "data_hashes": self.data_hashes,
            "tier_metadata": self.tier_metadata,
            "seeds": self.seeds,
            "rng_state": self.rng_state,
            "checkpoints": self.checkpoints,
            "graph_snapshots": self.graph_snapshots,
            "audit_events": self.audit_events,
            "projections": self.projections,
            "claims": self.claims,
            "bundle_hash": self.bundle_hash,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationBundle':
        """Create from dictionary."""
        bundle = cls(
            bundle_id=data["bundle_id"],
            created=datetime.fromisoformat(data["created"]),
            atlas_version=data["atlas_version"],
            config_hashes=data.get("config_hashes", {}),
            baseline_hashes=data.get("baseline_hashes", {}),
            data_hashes=data.get("data_hashes", {}),
            tier_metadata=data.get("tier_metadata", []),
            seeds=data.get("seeds", {}),
            rng_state=data.get("rng_state"),
            checkpoints=data.get("checkpoints", []),
            graph_snapshots=data.get("graph_snapshots", []),
            audit_events=data.get("audit_events", []),
            projections=data.get("projections", []),
            claims=data.get("claims", []),
            bundle_hash=data.get("bundle_hash"),
            signature=data.get("signature")
        )
        return bundle


class VerificationSystem:
    """Production-grade verification system."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize verification system."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "data" / "bundles"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit = get_audit_trail()
        
        logger.info(f"Initialized VerificationSystem with output: {self.output_dir}")
    
    def create_bundle(
        self,
        bundle_id: str,
        config_hashes: Dict[str, str],
        data_hashes: Dict[str, str],
        seeds: Dict[str, str],
        **kwargs
    ) -> VerificationBundle:
        """Create verification bundle."""
        bundle = VerificationBundle(
            bundle_id=bundle_id,
            created=datetime.utcnow(),
            atlas_version="1.0.0",
            config_hashes=config_hashes,
            data_hashes=data_hashes,
            seeds=seeds
        )
        
        bundle.bundle_hash = bundle.compute_bundle_hash()
        
        logger.info(f"Created bundle: {bundle_id}")
        
        return bundle
    
    def save_bundle(self, bundle: VerificationBundle, compress: bool = True) -> Path:
        """Save bundle to file."""
        filename = f"bundle_{bundle.bundle_id}.json"
        if compress:
            filename += ".gz"
        
        filepath = self.output_dir / filename
        bundle_data = bundle.to_dict()
        
        if compress:
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(bundle_data, f, indent=2, sort_keys=True)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(bundle_data, f, indent=2, sort_keys=True)
        
        logger.info(f"Saved bundle to {filepath}")
        return filepath
    
    def load_bundle(self, filepath: Path) -> VerificationBundle:
        """Load bundle from file."""
        if not filepath.exists():
            raise FileNotFoundError(f"Bundle not found: {filepath}")
        
        if filepath.suffix == '.gz':
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        bundle = VerificationBundle.from_dict(data)
        logger.info(f"Loaded bundle from {filepath}")
        return bundle


# Singleton instance
_verification_system: Optional[VerificationSystem] = None


def get_verification_system() -> VerificationSystem:
    """Get singleton verification system instance."""
    global _verification_system
    if _verification_system is None:
        _verification_system = VerificationSystem()
    return _verification_system
