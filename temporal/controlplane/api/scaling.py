"""
Scaling API

Provides horizontal and vertical scaling controls.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class ScalingType(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class AutoscalingMetric(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    REQUESTS = "requests"
    CUSTOM = "custom"


class ScalingPolicy:
    """Autoscaling policy"""
    
    def __init__(
        self,
        name: str,
        target_id: str,
        scaling_type: ScalingType,
        min_replicas: int = 1,
        max_replicas: int = 10,
        target_metric: AutoscalingMetric = AutoscalingMetric.CPU,
        target_value: float = 80.0,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.target_id = target_id
        self.scaling_type = scaling_type
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.target_metric = target_metric
        self.target_value = target_value
        self.enabled = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "target_id": self.target_id,
            "scaling_type": self.scaling_type,
            "min_replicas": self.min_replicas,
            "max_replicas": self.max_replicas,
            "target_metric": self.target_metric,
            "target_value": self.target_value,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ScalingAPI:
    """API for scaling management"""
    
    def __init__(self):
        self.policies: Dict[str, ScalingPolicy] = {}
        self.scaling_history: List[Dict[str, Any]] = []
        
    def scale_horizontal(
        self,
        deployment_id: str,
        replicas: int,
    ) -> Dict[str, Any]:
        """
        Scale deployment horizontally
        
        Args:
            deployment_id: Deployment ID
            replicas: Target replica count
            
        Returns:
            Scaling operation details
        """
        operation = {
            "id": str(uuid.uuid4()),
            "deployment_id": deployment_id,
            "type": ScalingType.HORIZONTAL,
            "target_replicas": replicas,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
        }
        
        self.scaling_history.append(operation)
        return operation
    
    def scale_vertical(
        self,
        deployment_id: str,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scale deployment vertically
        
        Args:
            deployment_id: Deployment ID
            cpu: CPU limit (e.g., "500m")
            memory: Memory limit (e.g., "1Gi")
            
        Returns:
            Scaling operation details
        """
        resources = {}
        if cpu:
            resources["cpu"] = cpu
        if memory:
            resources["memory"] = memory
        
        operation = {
            "id": str(uuid.uuid4()),
            "deployment_id": deployment_id,
            "type": ScalingType.VERTICAL,
            "resources": resources,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
        }
        
        self.scaling_history.append(operation)
        return operation
    
    def create_autoscaling_policy(
        self,
        name: str,
        target_id: str,
        scaling_type: str = "horizontal",
        min_replicas: int = 1,
        max_replicas: int = 10,
        target_metric: str = "cpu",
        target_value: float = 80.0,
    ) -> Dict[str, Any]:
        """
        Create autoscaling policy
        
        Args:
            name: Policy name
            target_id: Target deployment ID
            scaling_type: Horizontal or vertical
            min_replicas: Minimum replicas
            max_replicas: Maximum replicas
            target_metric: Metric to track
            target_value: Target value for metric
            
        Returns:
            Policy details
        """
        policy = ScalingPolicy(
            name=name,
            target_id=target_id,
            scaling_type=ScalingType(scaling_type),
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            target_metric=AutoscalingMetric(target_metric),
            target_value=target_value,
        )
        
        self.policies[policy.id] = policy
        return policy.to_dict()
    
    def get_autoscaling_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get autoscaling policy by ID"""
        policy = self.policies.get(policy_id)
        return policy.to_dict() if policy else None
    
    def list_autoscaling_policies(
        self,
        target_id: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        List autoscaling policies
        
        Args:
            target_id: Filter by target deployment
            enabled: Filter by enabled status
            
        Returns:
            List of policies
        """
        policies = list(self.policies.values())
        
        if target_id:
            policies = [p for p in policies if p.target_id == target_id]
        
        if enabled is not None:
            policies = [p for p in policies if p.enabled == enabled]
        
        return [p.to_dict() for p in policies]
    
    def update_autoscaling_policy(
        self,
        policy_id: str,
        min_replicas: Optional[int] = None,
        max_replicas: Optional[int] = None,
        target_value: Optional[float] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update autoscaling policy"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
        
        if min_replicas is not None:
            policy.min_replicas = min_replicas
        if max_replicas is not None:
            policy.max_replicas = max_replicas
        if target_value is not None:
            policy.target_value = target_value
        if enabled is not None:
            policy.enabled = enabled
        
        policy.updated_at = datetime.utcnow()
        return policy.to_dict()
    
    def delete_autoscaling_policy(self, policy_id: str) -> bool:
        """Delete autoscaling policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            return True
        return False
    
    def get_scaling_history(
        self,
        deployment_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get scaling operation history
        
        Args:
            deployment_id: Filter by deployment
            limit: Maximum number of results
            
        Returns:
            List of scaling operations
        """
        history = self.scaling_history
        
        if deployment_id:
            history = [h for h in history if h["deployment_id"] == deployment_id]
        
        return history[-limit:]
