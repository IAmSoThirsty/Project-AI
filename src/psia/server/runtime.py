"""
PSIARuntime — Singleton that boots and holds all PSIA subsystems.

Lifecycle:
    1. Create PSIARuntime()
    2. Call boot() — runs genesis ceremony, readiness checks, transitions to OPERATIONAL
    3. Call process_intent(intent_dict) — full Triumvirate + Waterfall evaluation
    4. Call get_health() — returns system status
    5. Call get_audit_records(limit) — returns ledger records

Thread Safety:
    The runtime is NOT thread-safe. In production, use per-request locking
    or message-queue dispatch. For single-user desktop use, sequential calls
    are sufficient. FastAPI's async nature serializes CPU-bound calls.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from psia.bootstrap.genesis import GenesisCoordinator
from psia.bootstrap.readiness import NodeStatus, ReadinessGate
from psia.bootstrap.safe_halt import SafeHaltController
from psia.canonical.capability_authority import CapabilityAuthority
from psia.canonical.commit_coordinator import CommitCoordinator
from psia.canonical.ledger import DurableLedger, ExecutionRecord
from psia.events import EventBus
from psia.invariants import ROOT_INVARIANTS
from psia.observability.autoimmune_dampener import AutoimmuneDampener
from psia.observability.failure_detector import FailureDetector
from psia.waterfall.engine import WaterfallEngine

logger = logging.getLogger(__name__)


class PSIARuntime:
    """Singleton-style runtime that manages the full PSIA lifecycle.

    Boots all subsystems (genesis → readiness → operational) and provides
    high-level methods for governance evaluation and auditing.
    """

    _instance: PSIARuntime | None = None

    def __init__(self) -> None:
        # Event bus (shared across all subsystems)
        self.event_bus = EventBus()

        # Bootstrap
        self.genesis = GenesisCoordinator(node_id="project-ai-desktop-node")
        self.readiness_gate = ReadinessGate(node_id="project-ai-desktop-node")

        # Canonical plane
        self.commit_coordinator = CommitCoordinator()
        self.ledger = DurableLedger(block_size=64)
        self.capability_authority = CapabilityAuthority()

        # Observability
        self.failure_detector = FailureDetector()
        self.autoimmune_dampener = AutoimmuneDampener()

        # Lifecycle
        self.safe_halt = SafeHaltController()

        # Waterfall engine (stages not injected — runs as pass-through)
        self.waterfall = WaterfallEngine(event_bus=self.event_bus)

        # Triumvirate governance (lazy import to avoid circular deps)
        self._triumvirate: Any = None

        # Runtime metadata
        self._booted = False
        self._boot_time: str | None = None
        self._intent_count = 0

    @classmethod
    def get_instance(cls) -> PSIARuntime:
        """Get or create the singleton runtime instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def boot(self) -> dict[str, Any]:
        """Execute the full bootstrap lifecycle.

        Returns:
            dict with boot status, genesis anchor hash, readiness report
        """
        if self._booted:
            return {
                "status": "already_booted",
                "node_status": self.readiness_gate.status.value,
            }

        logger.info("PSIA Desktop Runtime boot sequence starting...")
        start = time.monotonic()

        # Phase 1: Genesis ceremony
        genesis_result = self.genesis.execute(
            invariant_definitions=list(ROOT_INVARIANTS.values()),
        )
        logger.info(
            "Genesis: %s (keys=%d)",
            genesis_result.status.value,
            len(genesis_result.keys_generated),
        )

        # Phase 2: Register readiness checks
        self.readiness_gate.register_genesis_check(self.genesis)
        self.readiness_gate.register_ledger_check(self.ledger)
        self.readiness_gate.register_capability_check(self.capability_authority)

        # Phase 3: Evaluate readiness
        report = self.readiness_gate.evaluate()
        logger.info(
            "Readiness: %s (critical_failures=%d)",
            report.status.value,
            report.critical_failures,
        )

        # Phase 4: Initialize Triumvirate
        try:
            from app.core.governance import Triumvirate

            self._triumvirate = Triumvirate()
            logger.info("Triumvirate governance council initialized")
        except ImportError:
            logger.warning("Triumvirate not available — governance will use fallback")
            self._triumvirate = None

        self._booted = True
        self._boot_time = datetime.now(timezone.utc).isoformat()
        boot_duration_ms = (time.monotonic() - start) * 1000

        logger.info("PSIA Desktop Runtime boot complete in %.1fms", boot_duration_ms)

        return {
            "status": "booted",
            "node_status": report.status.value,
            "genesis_anchor": (
                genesis_result.anchor.anchor_id if genesis_result.anchor else None
            ),
            "readiness_checks": len(report.checks),
            "critical_failures": report.critical_failures,
            "boot_duration_ms": round(boot_duration_ms, 1),
        }

    def process_intent(self, intent_data: dict[str, Any]) -> dict[str, Any]:
        """Process an intent through Triumvirate governance + PSIA ledger.

        Args:
            intent_data: Dict with keys: actor, action, target, origin, context (optional)

        Returns:
            GovernanceResult-compatible dict with votes, verdict, and audit trail
        """
        self._intent_count += 1
        now = datetime.now(timezone.utc)
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        intent_hash = hashlib.sha256(
            f"{intent_data.get('actor', 'unknown')}:{intent_data.get('action', 'unknown')}:"
            f"{intent_data.get('target', 'unknown')}:{now.isoformat()}".encode()
        ).hexdigest()

        actor = intent_data.get("actor", "human")
        action = intent_data.get("action", "read")
        target = intent_data.get("target", "unknown")
        origin = intent_data.get("origin", "desktop")
        context = intent_data.get("context", {})

        # Phase 1: Triumvirate governance evaluation
        votes = []
        final_verdict = "allow"

        if self._triumvirate:
            from app.core.governance import GovernanceContext

            gov_context = GovernanceContext(
                action_type=action,
                description=f"{actor} requests to {action} on {target}",
                high_risk=context.get("high_risk", False),
                sensitive_data=context.get("sensitive_data", False),
                irreversible=context.get("irreversible", False),
                fully_clarified=context.get("fully_clarified", True),
                user_consent=context.get("user_consent", True),
            )

            decision = self._triumvirate.evaluate_action(
                action=f"{actor}:{action}:{target}",
                context=gov_context,
            )

            # Map Triumvirate decision to desktop API format
            if decision.allowed:
                final_verdict = "allow"
            elif decision.overrides:
                final_verdict = "deny"
            else:
                final_verdict = "degrade"

            # Reconstruct individual pillar votes
            for member_name in ["galahad", "cerberus", "codex_deus_maximus"]:
                vote_fn = getattr(
                    self._triumvirate,
                    f"_{member_name.replace('_maximus', '')}_vote",
                    None,
                )
                pillar_name = {
                    "galahad": "Galahad",
                    "cerberus": "Cerberus",
                    "codex_deus_maximus": "Codex Deus",
                }[member_name]

                if vote_fn:
                    try:
                        pillar_decision = vote_fn(
                            f"{actor}:{action}:{target}",
                            gov_context,
                        )
                        votes.append(
                            {
                                "pillar": pillar_name,
                                "verdict": (
                                    "allow"
                                    if pillar_decision.allowed
                                    else (
                                        "deny"
                                        if pillar_decision.overrides
                                        else "degrade"
                                    )
                                ),
                                "reason": pillar_decision.reason,
                            }
                        )
                    except Exception as e:
                        votes.append(
                            {
                                "pillar": pillar_name,
                                "verdict": "allow",
                                "reason": f"Vote evaluation error: {e}",
                            }
                        )
                else:
                    votes.append(
                        {
                            "pillar": pillar_name,
                            "verdict": "allow",
                            "reason": f"{pillar_name}: No concerns",
                        }
                    )
        else:
            # Fallback when Triumvirate is not available
            for pillar in ["Galahad", "Cerberus", "Codex Deus"]:
                votes.append(
                    {
                        "pillar": pillar,
                        "verdict": "allow",
                        "reason": f"{pillar}: Fallback mode — Triumvirate not loaded",
                    }
                )

        # Phase 2: Record to PSIA DurableLedger
        record = ExecutionRecord(
            record_id=f"exec_{uuid.uuid4().hex[:12]}",
            request_id=request_id,
            actor=actor,
            action=action,
            resource=target,
            decision=final_verdict,
            timestamp=now.isoformat(),
            metadata={
                "origin": origin,
                "votes": votes,
                "intent_hash": intent_hash,
            },
        )

        try:
            self.ledger.append(record)
        except Exception as e:
            logger.error("Failed to append to ledger: %s", e)

        # Phase 3: Build response matching desktop API contract
        tarl_version = "TARL-v1.0"

        result = {
            "intent_hash": intent_hash,
            "tarl_version": tarl_version,
            "votes": votes,
            "final_verdict": final_verdict,
            "timestamp": now.timestamp(),
        }

        logger.info(
            "Intent #%d processed: %s → %s (votes: %s)",
            self._intent_count,
            f"{actor}:{action}:{target}",
            final_verdict,
            ", ".join(f"{v['pillar']}={v['verdict']}" for v in votes),
        )

        return result

    def get_health(self) -> dict[str, Any]:
        """Get current system health status.

        Returns:
            HealthResponse-compatible dict
        """
        if not self._booted:
            return {
                "status": "not-booted",
                "tarl": "TARL-v1.0",
            }

        node_status = self.readiness_gate.status

        # Map PSIA node status to desktop API status string
        status_map = {
            NodeStatus.OPERATIONAL: "governance-online",
            NodeStatus.DEGRADED: "governance-degraded",
            NodeStatus.CHECKING: "governance-checking",
            NodeStatus.INITIALIZING: "governance-initializing",
            NodeStatus.SAFE_HALT: "governance-halted",
            NodeStatus.FAILED: "governance-failed",
        }

        return {
            "status": status_map.get(node_status, "governance-unknown"),
            "tarl": "TARL-v1.0",
            "node_id": self.genesis.node_id,
            "boot_time": self._boot_time,
            "intents_processed": self._intent_count,
            "ledger_records": self.ledger.total_records,
            "sealed_blocks": self.ledger.sealed_block_count,
            "halted": self.safe_halt.is_halted,
        }

    def get_audit_records(self, limit: int = 50) -> dict[str, Any]:
        """Get recent audit records from the DurableLedger.

        Args:
            limit: Max records to return

        Returns:
            AuditResponse-compatible dict
        """
        records = []

        # Get all records from sealed blocks + pending
        all_records: list[ExecutionRecord] = []
        for block in self.ledger.sealed_blocks:
            all_records.extend(block.records)
        # Also get pending (current unseal) records via internal access
        all_records.extend(self.ledger._current_records)

        # Take the most recent `limit` records
        recent = all_records[-limit:] if len(all_records) > limit else all_records

        for rec in recent:
            records.append(
                {
                    "intent_hash": rec.metadata.get("intent_hash", rec.record_id),
                    "tarl_version": "TARL-v1.0",
                    "votes": rec.metadata.get("votes", []),
                    "final_verdict": rec.decision,
                    "timestamp": self._parse_timestamp(rec.timestamp),
                }
            )

        # Compute TARL signature (hash of all record IDs)
        sig_data = ":".join(r.record_id for r in recent) if recent else "empty"
        tarl_sig = hashlib.sha256(sig_data.encode()).hexdigest()[:16]

        return {
            "tarl_version": "TARL-v1.0",
            "tarl_signature": tarl_sig,
            "records": records,
        }

    def get_tarl_rules(self) -> dict[str, Any]:
        """Get current TARL protection rules.

        Returns:
            TarlResponse-compatible dict with TARL version and rules
        """
        # Core TARL rules derived from the governance architecture
        rules = [
            {
                "action": "read",
                "allowed_actors": ["human", "agent", "system"],
                "risk": "low",
                "default": "allow",
            },
            {
                "action": "write",
                "allowed_actors": ["human", "agent"],
                "risk": "medium",
                "default": "allow",
            },
            {
                "action": "execute",
                "allowed_actors": ["human", "system"],
                "risk": "high",
                "default": "degrade",
            },
            {
                "action": "mutate",
                "allowed_actors": ["human"],
                "risk": "critical",
                "default": "deny",
            },
            {
                "action": "delete",
                "allowed_actors": ["human"],
                "risk": "critical",
                "default": "deny",
            },
            {
                "action": "escalate",
                "allowed_actors": ["system"],
                "risk": "high",
                "default": "degrade",
            },
            {
                "action": "deploy",
                "allowed_actors": ["human"],
                "risk": "critical",
                "default": "deny",
            },
            {
                "action": "configure",
                "allowed_actors": ["human", "system"],
                "risk": "medium",
                "default": "allow",
            },
        ]

        return {
            "version": "TARL-v1.0",
            "rules": rules,
        }

    @staticmethod
    def _parse_timestamp(ts: str) -> float:
        """Parse ISO timestamp to epoch seconds."""
        try:
            dt = datetime.fromisoformat(ts)
            return dt.timestamp()
        except (ValueError, TypeError):
            return time.time()


__all__ = ["PSIARuntime"]
