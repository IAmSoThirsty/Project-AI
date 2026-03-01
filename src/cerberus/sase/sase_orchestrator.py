"""
SASE - Sovereign Adversarial Signal Engine
Main Orchestrator

Integrates all 16 layers into unified adversarial detection pipeline.
"""

import logging
import time
from typing import Any

from .advanced.model_drift import DriftDetector, RetrainingTrigger
from .advanced.raft_consensus import RaftNode
from .advanced.threat_ontology import ThreatActorClassifier
from .audit.evidence_vault import EvidenceVault
from .core.ingestion_gateway import TelemetryGateway
from .core.network_enforcement import EdgeEnforcementPlane
from .core.normalization import EventEnrichmentPipeline

# Layer imports
from .core.substrate import DeploymentTopology, SubstrateManager
from .governance.key_management import KeyManagementCeremony
from .governance.observability import ObservabilityFabric
from .governance.rbac import RBACEngine
from .intelligence.attribution import AttributionEngine
from .intelligence.bayesian_scoring import ConfidenceAggregator
from .intelligence.behavioral_model import BehavioralModelEngine
from .policy.adaptive_policy import AdaptivePolicyEngine
from .policy.containment import ContainmentOrchestrator

logger = logging.getLogger("SASE.Orchestrator")


class SASEOrchestrator:
    """
    SASE Main Orchestrator

    Coordinates all 16 layers for end-to-end adversarial signal processing.

    PIPELINE:
    1. Edge enforcement (L1)
    2. Telemetry ingestion (L2)
    3. Event enrichment (L3)
    4. Feature attribution (L4)
    5. Behavioral modeling (L5)
    6. Bayesian scoring (L6)
    7. Policy enforcement (L7)
    8. Containment orchestration (L8)
    9. Evidence vault (L9)
    10. Observability tracking (L11)
    11. Threat classification (L15)
    """

    def __init__(
        self,
        deployment: DeploymentTopology = DeploymentTopology.SINGLE_NODE,
        node_id: str = "sase-node-1",
        cluster_nodes: list = None,
    ):

        logger.critical("=" * 60)
        logger.critical("INITIALIZING SOVEREIGN ADVERSARIAL SIGNAL ENGINE (SASE)")
        logger.critical("=" * 60)

        # L0: Substrate
        self.substrate = SubstrateManager(deployment)

        # L1: Network enforcement
        self.edge_enforcement = EdgeEnforcementPlane()

        # L2: Telemetry gateway
        self.telemetry_gateway = TelemetryGateway()

        # L3: Enrichment
        self.enrichment_pipeline = EventEnrichmentPipeline()

        # L4: Attribution
        self.attribution_engine = AttributionEngine()

        # L5: Behavioral model
        self.behavioral_model = BehavioralModelEngine()

        # L6: Bayesian scoring
        self.confidence_aggregator = ConfidenceAggregator()

        # L7: Adaptive policy
        self.policy_engine = AdaptivePolicyEngine()

        # L8: Containment
        self.containment_orchestrator = ContainmentOrchestrator()

        # L9: Evidence vault
        self.evidence_vault = EvidenceVault()

        # L10: RBAC
        self.rbac = RBACEngine()

        # L11: Observability
        self.observability = ObservabilityFabric()

        # L12: Key management
        self.key_mgmt = KeyManagementCeremony()

        # L13: Drift detection
        self.drift_detector = DriftDetector()
        self.retrain_trigger = RetrainingTrigger()

        # L14: Raft consensus (if multi-node)
        self.raft_node = None
        if deployment in [
            DeploymentTopology.HA_CLUSTER,
            DeploymentTopology.MULTI_REGION,
        ]:
            self.raft_node = RaftNode(node_id, cluster_nodes or [node_id])

        # L15: Threat ontology
        self.threat_classifier = ThreatActorClassifier()

        logger.critical("SASE INITIALIZED - ALL 16 LAYERS ACTIVE")
        logger.critical("=" * 60)

    def process_telemetry(self, raw_telemetry: dict[str, Any]) -> dict[str, Any]:
        """
        Process telemetry event through full SASE pipeline

        Returns comprehensive analysis result
        """
        start_time = time.time()

        logger.info("=" * 40)
        logger.info("PROCESSING TELEMETRY EVENT")
        logger.info("=" * 40)

        try:
            # Import invariant guards
            from .governance.invariants import (
                ClassificationDecouplingGuard,
                FeatureDoubleWeightingDetector,
                PosteriorImmutabilityGuard,
            )

            posterior_guard = PosteriorImmutabilityGuard()

            # L1: Edge enforcement
            enforcement_action, enforcement_ctx = self.edge_enforcement.enforce(
                raw_telemetry
            )

            if enforcement_action.value not in ["allow"]:
                logger.warning(f"Event blocked by edge: {enforcement_action.value}")
                return {"blocked": True, "reason": enforcement_action.value}

            # L2: Ingest telemetry
            event = self.telemetry_gateway.ingest(raw_telemetry)
            self.observability.record_event_ingested(event.artifact_type.value)

            # L3: Enrich event
            enrichment = self.enrichment_pipeline.enrich(event)
            event.enrichment = enrichment.to_dict()

            # L4: Extract features
            feature_vector = self.attribution_engine.attribute(event, enrichment)

            # L5: Behavioral modeling
            behavior_state = self.behavioral_model.process_event(event)

            # L6: Bayesian scoring
            confidence_assessment = self.confidence_aggregator.aggregate(
                event, feature_vector, behavior_state
            )

            # === CRITICAL INVARIANT: LOCK POSTERIOR ===
            # After L6, posterior MUST NOT be mutated
            posterior_hash = posterior_guard.lock_posterior(
                event.event_id, confidence_assessment
            )
            logger.info(
                f"✓ Posterior locked: {confidence_assessment['confidence_percentage']}% (hash={posterior_hash[:8]})"
            )

            # L15: Threat classification
            # IMPORTANT: Classification CANNOT modify confidence
            threat_class = self.threat_classifier.classify(feature_vector)

            # === INVARIANT CHECK: L15 OUTPUT VALIDATION ===
            ClassificationDecouplingGuard.validate_classification_output(threat_class)

            # === INVARIANT CHECK: FEATURE DOUBLE-WEIGHTING ===
            FeatureDoubleWeightingDetector.check_for_double_weighting(
                feature_vector, confidence_assessment, threat_class
            )

            # === INVARIANT CHECK: VERIFY POSTERIOR IMMUTABILITY ===
            posterior_guard.verify_immutability(event.event_id, confidence_assessment)
            logger.info("✓ Posterior immutability verified - no mutations detected")

            # L7: Policy enforcement
            # Policy uses posterior for severity, actor class for response type
            if confidence_assessment["confidence_percentage"] >= 30:
                policy_executions = self.policy_engine.enforce(confidence_assessment)

                # L8: Containment orchestration
                if confidence_assessment["confidence_percentage"] >= 50:
                    from .policy.containment import ContainmentRequest

                    containment_req = ContainmentRequest(
                        event_id=event.event_id,
                        source_ip=event.source_ip,
                        confidence_score=confidence_assessment["confidence_score"],
                        actions=[e.action for e in policy_executions],
                        model_version=event.model_version,
                        requestor="SASE_ORCHESTRATOR",
                    )

                    containment_result = self.containment_orchestrator.orchestrate(
                        containment_req,
                        feature_vector,
                        confidence_assessment,
                        event.raw_payload_hash,
                    )

                    # Record containment
                    for exec in policy_executions:
                        self.observability.record_containment_action(exec.action.value)

            # L11: Observability
            detection_time = time.time() - start_time
            self.observability.record_detection(detection_time)

            # L9: Evidence vault (store event)
            # In production, would batch daily for Merkle tree

            result = {
                "success": True,
                "event_id": event.event_id,
                "confidence": confidence_assessment,
                "threat_class": threat_class,
                "behavior_state": behavior_state.value if behavior_state else None,
                "detection_time_ms": int(detection_time * 1000),
                "posterior_hash": posterior_hash,  # Include for audit trail
                "invariants_verified": True,
            }

            logger.info(
                f"TELEMETRY PROCESSED: confidence={confidence_assessment['confidence_percentage']}%"
            )
            logger.info("=" * 40)

            return result

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {"success": False, "error": str(e)}

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "substrate": self.substrate.get_health_status(),
            "events_processed": self.telemetry_gateway.store.event_count,
            "metrics": self.observability.export_metrics(),
            "raft_state": self.raft_node.state.value if self.raft_node else "N/A",
        }


__all__ = ["SASEOrchestrator"]
