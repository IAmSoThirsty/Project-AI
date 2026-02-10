#!/usr/bin/env python3
"""
Triumvirate HTTP Client - Legion Phase 2
Handles governance decisions via Project-AI API
"""

import asyncio
from datetime import datetime
from typing import Any

import aiohttp
from pydantic import BaseModel


class TriumvirateVote(BaseModel):
    """Single Triumvirate pillar vote"""

    pillar: str  # "Galahad", "Cerberus", "CodexDeus"
    verdict: str  # "allow", "deny", "escalate"
    reasoning: str
    confidence: float = 1.0


class GovernanceDecision(BaseModel):
    """Complete Triumvirate decision"""

    final_verdict: str  # "allow", "deny", "escalate"
    votes: list[TriumvirateVote]
    timestamp: datetime
    audit_id: str
    consensus: bool = True
    metadata: dict[str, Any] = {}


class Intent(BaseModel):
    """Structured intent for Triumvirate evaluation"""

    actor: str  # "human", "agent", "system"
    action: str  # "read", "write", "execute", "mutate"
    target: str
    context: dict[str, Any]
    origin: str
    risk_level: str = "unknown"


class TriumvirateClient:
    """
    HTTP client for Project-AI Triumvirate governance

    Submits intents to /intent endpoint and receives
    governance decisions from Galahad, Cerberus, and CodexDeus
    """

    def __init__(self, api_url: str = "http://localhost:8001"):
        """
        Initialize Triumvirate client

        Args:
            api_url: Base URL for Project-AI API
        """
        self.api_url = api_url.rstrip("/")
        self.intent_endpoint = f"{self.api_url}/intent"
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def submit_intent(
        self, intent: Intent, timeout: int = 30
    ) -> GovernanceDecision:
        """
        Submit intent to Triumvirate for governance decision

        Args:
            intent: Structured intent to evaluate
            timeout: Request timeout in seconds

        Returns:
            GovernanceDecision: Decision from all three pillars

        Raises:
            TriumvirateError: If governance request fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        payload = {
            "actor": intent.actor,
            "action": intent.action,
            "target": intent.target,
            "context": intent.context,
            "origin": intent.origin,
            "risk_level": intent.risk_level,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            async with self.session.post(
                self.intent_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise TriumvirateError(
                        f"Triumvirate request failed: {response.status} - {error_text}"
                    )

                data = await response.json()
                return self._parse_decision(data)

        except aiohttp.ClientError as e:
            raise TriumvirateError(f"Network error contacting Triumvirate: {str(e)}")
        except TimeoutError:
            raise TriumvirateError(f"Triumvirate decision timed out after {timeout}s")

    def _parse_decision(self, data: dict[str, Any]) -> GovernanceDecision:
        """Parse Triumvirate response into decision object"""
        votes = [
            TriumvirateVote(
                pillar=vote.get("pillar", "unknown"),
                verdict=vote.get("verdict", "deny"),
                reasoning=vote.get("reasoning", ""),
                confidence=vote.get("confidence", 1.0),
            )
            for vote in data.get("votes", [])
        ]

        return GovernanceDecision(
            final_verdict=data.get("final_verdict", "deny"),
            votes=votes,
            timestamp=datetime.fromisoformat(
                data.get("timestamp", datetime.now().isoformat())
            ),
            audit_id=data.get("audit_id", ""),
            consensus=data.get("consensus", True),
            metadata=data.get("metadata", {}),
        )

    async def check_health(self) -> bool:
        """
        Check if Triumvirate endpoint is healthy

        Returns:
            bool: True if endpoint is responsive
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            health_url = f"{self.api_url}/health"
            async with self.session.get(
                health_url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except:
            return False

    async def get_decision_history(self, limit: int = 10) -> list[GovernanceDecision]:
        """
        Retrieve recent governance decisions (if endpoint exists)

        Args:
            limit: Number of recent decisions to fetch

        Returns:
            List of recent governance decisions
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            history_url = f"{self.api_url}/intent/history?limit={limit}"
            async with self.session.get(history_url) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                return [self._parse_decision(d) for d in data.get("decisions", [])]
        except:
            return []


class TriumvirateError(Exception):
    """Exception raised for Triumvirate client errors"""

    pass


# CLI test interface
async def test_triumvirate_client():
    """Test Triumvirate client locally"""
    print("\n" + "=" * 60)
    print("Triumvirate Client - Test Mode")
    print("=" * 60 + "\n")

    async with TriumvirateClient() as client:
        # Check health
        healthy = await client.check_health()
        print(f"Triumvirate Health: {'✓ Healthy' if healthy else '✗ Unavailable'}\n")

        if not healthy:
            print("Note: Start Project-AI API with 'python start_api.py'")
            return

        # Test intent
        test_intent = Intent(
            actor="human",
            action="read",
            target="user_conversation",
            context={"message": "What is your status?"},
            origin="legion_test",
            risk_level="low",
        )

        print("Submitting test intent...")
        print(f"  Actor: {test_intent.actor}")
        print(f"  Action: {test_intent.action}")
        print(f"  Target: {test_intent.target}\n")

        try:
            decision = await client.submit_intent(test_intent)

            print(f"Triumvirate Decision: {decision.final_verdict.upper()}")
            print(f"Consensus: {decision.consensus}")
            print(f"Audit ID: {decision.audit_id}\n")

            print("Individual Votes:")
            for vote in decision.votes:
                print(f"  {vote.pillar}: {vote.verdict}")
                print(f"    Reasoning: {vote.reasoning}")
                print(f"    Confidence: {vote.confidence:.2f}")

        except TriumvirateError as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_triumvirate_client())
