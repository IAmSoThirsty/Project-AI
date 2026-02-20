"""
SASE - Sovereign Adversarial Signal Engine
L15: Threat Actor Ontology & Classification

Classifies threat actors into behavioral categories.

CLASSES:
- Opportunistic Scanner
- Credential Harvester  
- Cloud VPS Actor
- Botnet Node
- Research Sandbox
- Corporate NAT
- Tor Relay
- Known Cluster Actor

Each defined by probability vector.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger("SASE.L15.ThreatOntology")


class ThreatActorClass(Enum):
    """Threat actor classifications"""

    OPPORTUNISTIC_SCANNER = "opportunistic_scanner"
    CREDENTIAL_HARVESTER = "credential_harvester"
    CLOUD_VPS_ACTOR = "cloud_vps_actor"
    BOTNET_NODE = "botnet_node"
    RESEARCH_SANDBOX = "research_sandbox"
    CORPORATE_NAT = "corporate_nat"
    TOR_RELAY = "tor_relay"
    KNOWN_CLUSTER_ACTOR = "known_cluster_actor"


@dataclass
class ActorProfile:
    """Threat actor behavioral profile"""

    actor_class: ThreatActorClass
    probability_vector: np.ndarray  # Feature probabilities
    description: str
    risk_level: int  # 1-10

    def match_score(self, features: np.ndarray) -> float:
        """Calculate match score with features"""
        # Cosine similarity
        dot = np.dot(self.probability_vector, features)
        norm = np.linalg.norm(self.probability_vector) * np.linalg.norm(features)

        if norm < 1e-10:
            return 0.0

        similarity = dot / norm
        return float(similarity)


class OntologyDatabase:
    """
    Database of threat actor ontologies

    Defines behavioral profiles for each actor class
    """

    def __init__(self):
        self.profiles: Dict[ThreatActorClass, ActorProfile] = {}
        self._initialize_profiles()

        logger.info("Ontology database initialized")

    def _initialize_profiles(self):
        """Initialize threat actor profiles"""

        # Opportunistic Scanner
        self.profiles[ThreatActorClass.OPPORTUNISTIC_SCANNER] = ActorProfile(
            actor_class=ThreatActorClass.OPPORTUNISTIC_SCANNER,
            probability_vector=np.array([0.3, 0.8, 0.2, 0.7, 0.1, 0.6, 0.2, 0.4, 0.3]),
            description="Automated scanning tools, low sophistication",
            risk_level=3,
        )

        # Credential Harvester
        self.profiles[ThreatActorClass.CREDENTIAL_HARVESTER] = ActorProfile(
            actor_class=ThreatActorClass.CREDENTIAL_HARVESTER,
            probability_vector=np.array([0.7, 0.5, 0.9, 0.4, 0.8, 0.4, 0.6, 0.3, 0.5]),
            description="Targeted credential theft, medium-high sophistication",
            risk_level=7,
        )

        # Cloud VPS Actor
        self.profiles[ThreatActorClass.CLOUD_VPS_ACTOR] = ActorProfile(
            actor_class=ThreatActorClass.CLOUD_VPS_ACTOR,
            probability_vector=np.array([0.6, 0.4, 0.5, 0.6, 0.5, 0.7, 0.5, 0.8, 0.6]),
            description="Uses cloud infrastructure, medium sophistication",
            risk_level=5,
        )

        # Botnet Node
        self.profiles[ThreatActorClass.BOTNET_NODE] = ActorProfile(
            actor_class=ThreatActorClass.BOTNET_NODE,
            probability_vector=np.array([0.5, 0.9, 0.3, 0.8, 0.2, 0.8, 0.4, 0.5, 0.9]),
            description="Compromised residential machine, part of botnet",
            risk_level=4,
        )

        # Research Sandbox
        self.profiles[ThreatActorClass.RESEARCH_SANDBOX] = ActorProfile(
            actor_class=ThreatActorClass.RESEARCH_SANDBOX,
            probability_vector=np.array([0.2, 0.3, 0.1, 0.5, 0.1, 0.5, 0.3, 0.2, 0.2]),
            description="Security research, benign analysis",
            risk_level=1,
        )

        # Corporate NAT
        self.profiles[ThreatActorClass.CORPORATE_NAT] = ActorProfile(
            actor_class=ThreatActorClass.CORPORATE_NAT,
            probability_vector=np.array([0.1, 0.2, 0.2, 0.3, 0.2, 0.3, 0.2, 0.1, 0.7]),
            description="Corporate network, likely benign",
            risk_level=2,
        )

        # Tor Relay
        self.profiles[ThreatActorClass.TOR_RELAY] = ActorProfile(
            actor_class=ThreatActorClass.TOR_RELAY,
            probability_vector=np.array([0.8, 0.6, 0.7, 0.5, 0.6, 0.9, 0.7, 0.9, 0.5]),
            description="Tor anonymity network, high risk",
            risk_level=8,
        )

        # Known Cluster Actor
        self.profiles[ThreatActorClass.KNOWN_CLUSTER_ACTOR] = ActorProfile(
            actor_class=ThreatActorClass.KNOWN_CLUSTER_ACTOR,
            probability_vector=np.array([0.9, 0.8, 0.9, 0.7, 0.9, 0.8, 0.9, 0.7, 0.8]),
            description="Known APT or threat cluster, very high risk",
            risk_level=10,
        )

    def get_profile(self, actor_class: ThreatActorClass) -> Optional[ActorProfile]:
        """Get actor profile"""
        return self.profiles.get(actor_class)

    def list_profiles(self) -> List[ActorProfile]:
        """List all profiles"""
        return list(self.profiles.values())


class ThreatActorClassifier:
    """
    L15: Threat Actor Ontology & Classification

    Classifies actors based on behavioral features
    """

    def __init__(self):
        self.ontology = OntologyDatabase()

        logger.info("L15 Threat Actor Classifier initialized")

    def classify(self, feature_vector: Any) -> Dict:
        """
        Classify threat actor

        Args:
            feature_vector: L4 attribution features

        Returns:
            Classification result with probabilities
        """
        from ..intelligence.attribution import FeatureVector

        if not isinstance(feature_vector, FeatureVector):
            raise TypeError("Must provide FeatureVector")

        # Convert to array
        features = np.array(feature_vector.to_array())

        # Calculate match scores for each profile
        scores = {}
        for actor_class, profile in self.ontology.profiles.items():
            score = profile.match_score(features)
            scores[actor_class] = score

        # Find best match
        best_class = max(scores, key=scores.get)
        best_profile = self.ontology.get_profile(best_class)

        result = {
            "actor_class": best_class.value,
            "confidence": scores[best_class],
            "risk_level": best_profile.risk_level,
            "description": best_profile.description,
            "all_scores": {k.value: v for k, v in scores.items()},
        }

        logger.info(f"Actor classified: {best_class.value} (risk={best_profile.risk_level})")

        return result


__all__ = [
    "ThreatActorClass",
    "ActorProfile",
    "OntologyDatabase",
    "ThreatActorClassifier",
]
