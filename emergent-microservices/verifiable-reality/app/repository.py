"""
Verifiable Reality - Repository
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import RealityProof


class Database:
    def __init__(self):
        self.data: Dict[str, Any] = {"proofs": {}}
        self.connected = False

    async def connect(self):
        self.connected = True
        logger.info("In-memory database initialized for Verifiable Reality")


database = Database()


class RealityRepository:
    def __init__(self):
        self.db = database

    async def get_proof(self, proof_id: UUID) -> Optional[RealityProof]:
        return self.db.data["proofs"].get(str(proof_id))

    async def save_proof(self, proof: RealityProof) -> RealityProof:
        self.db.data["proofs"][str(proof.id)] = proof
        return proof

    async def list_proofs(self, event_type: Optional[str] = None) -> List[RealityProof]:
        proofs = list(self.db.data["proofs"].values())
        if event_type:
            proofs = [p for p in proofs if p.event_type == event_type]
        return proofs
