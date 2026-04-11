"""
Network Policy Manager

Creates and manages Kubernetes NetworkPolicy resources for network segmentation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicyRule:
    """Network policy rule"""
    ports: List[Dict[str, Any]] = field(default_factory=list)
    from_selectors: List[Dict[str, Any]] = field(default_factory=list)
    to_selectors: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        rule = {}
        if self.ports:
            rule["ports"] = self.ports
        if self.from_selectors:
            rule["from"] = self.from_selectors
        if self.to_selectors:
            rule["to"] = self.to_selectors
        return rule


@dataclass
class NetworkPolicy:
    """Kubernetes NetworkPolicy"""
    name: str
    namespace: str
    pod_selector: Dict[str, Any]
    policy_types: List[str] = field(default_factory=lambda: ["Ingress", "Egress"])
    ingress_rules: List[PolicyRule] = field(default_factory=list)
    egress_rules: List[PolicyRule] = field(default_factory=list)
    
    def to_manifest(self) -> Dict[str, Any]:
        """Convert to Kubernetes manifest"""
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
            },
            "spec": {
                "podSelector": self.pod_selector,
                "policyTypes": self.policy_types,
            }
        }
        
        if self.ingress_rules:
            manifest["spec"]["ingress"] = [rule.to_dict() for rule in self.ingress_rules]
        
        if self.egress_rules:
            manifest["spec"]["egress"] = [rule.to_dict() for rule in self.egress_rules]
        
        return manifest


class NetworkPolicyManager:
    """
    Manages network policies for zero-trust networking
    
    Features:
    - Default deny all traffic
    - Fine-grained ingress/egress rules
    - Service-to-service communication control
    - Integration with Kubernetes NetworkPolicy
    """
    
    def __init__(self, namespace: str = "temporal"):
        self.namespace = namespace
        self.policies: Dict[str, NetworkPolicy] = {}
    
    def create_default_deny_policy(self) -> NetworkPolicy:
        """
        Create default deny-all policy
        
        This policy denies all ingress and egress traffic by default.
        Specific allow rules should be added separately.
        """
        policy = NetworkPolicy(
            name="default-deny-all",
            namespace=self.namespace,
            pod_selector={},  # Applies to all pods
            policy_types=["Ingress", "Egress"],
            ingress_rules=[],  # Empty = deny all
            egress_rules=[],   # Empty = deny all
        )
        
        self.policies[policy.name] = policy
        logger.info(f"Created default deny-all policy in {self.namespace}")
        
        return policy
    
    def create_temporal_frontend_policy(self) -> NetworkPolicy:
        """
        Create network policy for Temporal frontend service
        
        Allows:
        - Ingress from clients
        - Egress to history service
        - Egress to matching service
        - Egress to DNS
        """
        ingress_rules = [
            PolicyRule(
                ports=[{"protocol": "TCP", "port": 7233}],
                from_selectors=[
                    {"podSelector": {"matchLabels": {"role": "temporal-client"}}},
                    {"namespaceSelector": {}},  # Allow from any namespace
                ],
            ),
        ]
        
        egress_rules = [
            # Allow to history service
            PolicyRule(
                ports=[{"protocol": "TCP", "port": 7234}],
                to_selectors=[
                    {"podSelector": {"matchLabels": {"app": "temporal-history"}}},
                ],
            ),
            # Allow to matching service
            PolicyRule(
                ports=[{"protocol": "TCP", "port": 7235}],
                to_selectors=[
                    {"podSelector": {"matchLabels": {"app": "temporal-matching"}}},
                ],
            ),
            # Allow DNS
            PolicyRule(
                ports=[
                    {"protocol": "UDP", "port": 53},
                    {"protocol": "TCP", "port": 53},
                ],
            ),
        ]
        
        policy = NetworkPolicy(
            name="temporal-frontend",
            namespace=self.namespace,
            pod_selector={"matchLabels": {"app": "temporal-frontend"}},
            policy_types=["Ingress", "Egress"],
            ingress_rules=ingress_rules,
            egress_rules=egress_rules,
        )
        
        self.policies[policy.name] = policy
        logger.info("Created Temporal frontend network policy")
        
        return policy
    
    def create_temporal_worker_policy(self) -> NetworkPolicy:
        """
        Create network policy for Temporal workers
        
        Allows:
        - Egress to frontend service
        - Egress to external services (configurable)
        - Egress to DNS
        """
        egress_rules = [
            # Allow to frontend
            PolicyRule(
                ports=[{"protocol": "TCP", "port": 7233}],
                to_selectors=[
                    {"podSelector": {"matchLabels": {"app": "temporal-frontend"}}},
                ],
            ),
            # Allow DNS
            PolicyRule(
                ports=[
                    {"protocol": "UDP", "port": 53},
                    {"protocol": "TCP", "port": 53},
                ],
            ),
            # Allow to external services (HTTP/HTTPS)
            PolicyRule(
                ports=[
                    {"protocol": "TCP", "port": 80},
                    {"protocol": "TCP", "port": 443},
                ],
            ),
        ]
        
        policy = NetworkPolicy(
            name="temporal-workers",
            namespace=self.namespace,
            pod_selector={"matchLabels": {"app": "temporal-worker"}},
            policy_types=["Egress"],
            egress_rules=egress_rules,
        )
        
        self.policies[policy.name] = policy
        logger.info("Created Temporal worker network policy")
        
        return policy
    
    def create_temporal_internal_policy(self) -> NetworkPolicy:
        """
        Create network policy for internal Temporal services
        (history, matching, worker services)
        
        Allows:
        - Ingress from frontend
        - Egress to database
        - Egress to other Temporal services
        """
        ingress_rules = [
            PolicyRule(
                ports=[
                    {"protocol": "TCP", "port": 7234},  # History
                    {"protocol": "TCP", "port": 7235},  # Matching
                ],
                from_selectors=[
                    {"podSelector": {"matchLabels": {"app": "temporal-frontend"}}},
                    {"podSelector": {"matchLabels": {"component": "temporal-internal"}}},
                ],
            ),
        ]
        
        egress_rules = [
            # Allow to database
            PolicyRule(
                ports=[
                    {"protocol": "TCP", "port": 5432},  # PostgreSQL
                    {"protocol": "TCP", "port": 9042},  # Cassandra
                ],
                to_selectors=[
                    {"podSelector": {"matchLabels": {"app": "temporal-database"}}},
                ],
            ),
            # Allow to other Temporal services
            PolicyRule(
                to_selectors=[
                    {"podSelector": {"matchLabels": {"component": "temporal-internal"}}},
                ],
            ),
            # Allow DNS
            PolicyRule(
                ports=[
                    {"protocol": "UDP", "port": 53},
                    {"protocol": "TCP", "port": 53},
                ],
            ),
        ]
        
        policy = NetworkPolicy(
            name="temporal-internal",
            namespace=self.namespace,
            pod_selector={"matchLabels": {"component": "temporal-internal"}},
            policy_types=["Ingress", "Egress"],
            ingress_rules=ingress_rules,
            egress_rules=egress_rules,
        )
        
        self.policies[policy.name] = policy
        logger.info("Created Temporal internal services network policy")
        
        return policy
    
    def export_policy(self, policy_name: str, file_path: str):
        """Export policy to YAML file"""
        if policy_name not in self.policies:
            raise ValueError(f"Policy {policy_name} not found")
        
        policy = self.policies[policy_name]
        manifest = policy.to_manifest()
        
        with open(file_path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        logger.info(f"Exported policy {policy_name} to {file_path}")
    
    def export_all_policies(self, directory: str):
        """Export all policies to directory"""
        import os
        os.makedirs(directory, exist_ok=True)
        
        for policy_name, policy in self.policies.items():
            file_path = os.path.join(directory, f"{policy_name}.yaml")
            self.export_policy(policy_name, file_path)
        
        logger.info(f"Exported {len(self.policies)} policies to {directory}")
    
    def create_all_temporal_policies(self):
        """Create all standard Temporal policies"""
        self.create_default_deny_policy()
        self.create_temporal_frontend_policy()
        self.create_temporal_worker_policy()
        self.create_temporal_internal_policy()
        
        logger.info("Created all Temporal network policies")
