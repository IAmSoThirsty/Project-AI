"""
Autonomous Negotiation Agent - Service Layer
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import AgreedContract, NegotiationOffer, NegotiationSession
from .repository import NegotiationRepository


class NegotiationService:
    """Service for orchestrating secure agent-to-agent bargaining"""

    def __init__(self):
        self.repository = NegotiationRepository()

    async def start_session(
        self, topic: str, initiator: str, participant: str
    ) -> NegotiationSession:
        """Initialize a new bargaining session between two agents"""
        logger.info(
            f"Negotiation: Starting session between {initiator} and {participant} on {topic}"
        )

        session = NegotiationSession(
            initiator_id=initiator,
            participant_id=participant,
            topic=topic,
            current_offer={"status": "initialized"},
            status="active",
        )
        return await self.repository.save_session(session)

    async def submit_offer(
        self, session_id: UUID, offer: NegotiationOffer
    ) -> NegotiationSession:
        """Process a new offer and update session state"""
        session = await self.repository.get_session(session_id)
        if not session:
            raise Exception("Session not found")

        logger.info(
            f"Negotiation: Offer from {offer.sender_id} in session {session_id}"
        )

        session.history.append(session.current_offer)
        session.current_offer = offer.content
        session.updated_at = datetime.now()

        return await self.repository.save_session(session)

    async def finalize_agreement(
        self, session_id: UUID, signatures: Dict[str, str]
    ) -> AgreedContract:
        """Seal a negotiation session with a signed contract"""
        session = await self.repository.get_session(session_id)
        if not session:
            raise Exception("Session not found")

        logger.info(f"Negotiation: Finalizing agreement for session {session_id}")

        contract = AgreedContract(
            session_id=session_id, terms=session.current_offer, signatures=signatures
        )

        session.status = "agreed"
        session.contract_id = contract.id
        await self.repository.save_session(session)

        return await self.repository.save_contract(contract)
