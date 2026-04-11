"""
Network Policy Management

Manages Kubernetes NetworkPolicy and Calico policies for network segmentation
and zero-trust networking.
"""

from .policy_manager import NetworkPolicyManager, NetworkPolicy, PolicyRule
from .calico_integration import CalicoPolicy

__all__ = [
    "NetworkPolicyManager",
    "NetworkPolicy",
    "PolicyRule",
    "CalicoPolicy",
]
