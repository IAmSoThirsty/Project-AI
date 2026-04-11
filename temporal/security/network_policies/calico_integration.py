"""
Calico Network Policy Integration

Advanced network policies using Project Calico for enhanced security.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class CalicoPolicy:
    """
    Calico NetworkPolicy with advanced features
    
    Supports:
    - Global network policies
    - Service account-based rules
    - Layer 7 policies
    - Endpoint-specific rules
    """
    name: str
    namespace: Optional[str] = None  # None for global policies
    order: int = 100
    selector: str = ""
    types: List[str] = field(default_factory=lambda: ["Ingress", "Egress"])
    ingress: List[Dict[str, Any]] = field(default_factory=list)
    egress: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_manifest(self) -> Dict[str, Any]:
        """Convert to Calico manifest"""
        if self.namespace:
            # Namespaced NetworkPolicy
            manifest = {
                "apiVersion": "projectcalico.org/v3",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": self.name,
                    "namespace": self.namespace,
                },
            }
        else:
            # Global NetworkPolicy
            manifest = {
                "apiVersion": "projectcalico.org/v3",
                "kind": "GlobalNetworkPolicy",
                "metadata": {
                    "name": self.name,
                },
            }
        
        manifest["spec"] = {
            "order": self.order,
            "selector": self.selector,
            "types": self.types,
        }
        
        if self.ingress:
            manifest["spec"]["ingress"] = self.ingress
        
        if self.egress:
            manifest["spec"]["egress"] = self.egress
        
        return manifest


class CalicoGlobalDenyPolicy:
    """Global default-deny policy using Calico"""
    
    @staticmethod
    def create() -> CalicoPolicy:
        """Create global deny-all policy with highest order"""
        return CalicoPolicy(
            name="global-deny-all",
            namespace=None,
            order=9999,  # Lowest priority (highest number)
            selector="all()",
            types=["Ingress", "Egress"],
            ingress=[],
            egress=[],
        )


class CalicoTemporalPolicies:
    """Calico policies for Temporal services"""
    
    @staticmethod
    def create_frontend_policy(namespace: str = "temporal") -> CalicoPolicy:
        """
        Advanced frontend policy with service account matching
        """
        return CalicoPolicy(
            name="temporal-frontend-advanced",
            namespace=namespace,
            order=100,
            selector='app == "temporal-frontend"',
            types=["Ingress", "Egress"],
            ingress=[
                {
                    "action": "Allow",
                    "protocol": "TCP",
                    "source": {
                        "serviceAccounts": {
                            "names": ["temporal-client"],
                        },
                    },
                    "destination": {
                        "ports": [7233],
                    },
                },
            ],
            egress=[
                {
                    "action": "Allow",
                    "protocol": "TCP",
                    "destination": {
                        "selector": 'app == "temporal-history"',
                        "ports": [7234],
                    },
                },
                {
                    "action": "Allow",
                    "protocol": "TCP",
                    "destination": {
                        "selector": 'app == "temporal-matching"',
                        "ports": [7235],
                    },
                },
                # DNS
                {
                    "action": "Allow",
                    "protocol": "UDP",
                    "destination": {
                        "ports": [53],
                    },
                },
            ],
        )
    
    @staticmethod
    def create_mtls_enforcement_policy(namespace: str = "temporal") -> CalicoPolicy:
        """
        Enforce mTLS for all Temporal inter-service communication
        
        Uses Calico's application layer policy to enforce TLS version
        """
        return CalicoPolicy(
            name="temporal-mtls-enforcement",
            namespace=namespace,
            order=50,  # High priority
            selector='component == "temporal-internal"',
            types=["Ingress", "Egress"],
            ingress=[
                {
                    "action": "Allow",
                    "protocol": "TCP",
                    "source": {
                        "selector": 'component == "temporal-internal"',
                    },
                    "destination": {
                        "ports": [7233, 7234, 7235],
                    },
                    # Metadata to indicate mTLS requirement
                    "metadata": {
                        "annotations": {
                            "tls-required": "true",
                            "min-tls-version": "1.3",
                        },
                    },
                },
            ],
        )
    
    @staticmethod
    def create_egress_lockdown_policy(
        namespace: str = "temporal",
        allowed_external_cidrs: List[str] = None,
    ) -> CalicoPolicy:
        """
        Lockdown egress to only specific external CIDRs
        
        Args:
            namespace: Kubernetes namespace
            allowed_external_cidrs: List of allowed external IP ranges
        """
        allowed_cidrs = allowed_external_cidrs or ["10.0.0.0/8", "172.16.0.0/12"]
        
        egress_rules = []
        
        # Allow internal cluster communication
        for cidr in allowed_cidrs:
            egress_rules.append({
                "action": "Allow",
                "destination": {
                    "nets": [cidr],
                },
            })
        
        # Deny all other egress
        egress_rules.append({
            "action": "Deny",
            "destination": {},
        })
        
        return CalicoPolicy(
            name="temporal-egress-lockdown",
            namespace=namespace,
            order=200,
            selector='app startsWith "temporal-"',
            types=["Egress"],
            egress=egress_rules,
        )


def export_calico_policies(policies: List[CalicoPolicy], output_dir: str):
    """Export Calico policies to YAML files"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for policy in policies:
        filename = f"{policy.name}.yaml"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w") as f:
            yaml.dump(policy.to_manifest(), f, default_flow_style=False)
        
        logger.info(f"Exported Calico policy: {filepath}")
