"""
Kubernetes Controllers

Controllers for managing custom resources.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentController:
    """Controller for Agent custom resources"""
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.agents: Dict[str, Dict[str, Any]] = {}
        
    def reconcile(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconcile agent resource
        
        Args:
            agent: Agent resource
            
        Returns:
            Updated agent status
        """
        metadata = agent.get("metadata", {})
        spec = agent.get("spec", {})
        name = metadata.get("name")
        
        logger.info(f"Reconciling agent: {name}")
        
        # Create or update deployment
        deployment = self._create_deployment(name, spec)
        
        # Create or update service
        service = self._create_service(name, spec)
        
        # Create HPA if autoscaling enabled
        if spec.get("autoscaling", {}).get("enabled", False):
            hpa = self._create_hpa(name, spec)
        
        # Update status
        status = self._get_agent_status(name, spec)
        
        return {
            "status": status,
            "resources": {
                "deployment": deployment,
                "service": service,
            }
        }
    
    def _create_deployment(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes deployment for agent"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{name}-agent",
                "namespace": self.namespace,
                "labels": {
                    "app": name,
                    "component": "agent",
                    "managed-by": "controlplane-operator",
                },
            },
            "spec": {
                "replicas": spec.get("replicas", 1),
                "selector": {
                    "matchLabels": {
                        "app": name,
                        "component": "agent",
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name,
                            "component": "agent",
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "agent",
                                "image": spec.get("image", f"controlplane/agent:{spec.get('version', 'latest')}"),
                                "env": [
                                    {"name": "AGENT_TYPE", "value": spec.get("agentType")},
                                    {"name": "AGENT_VERSION", "value": spec.get("version")},
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": spec.get("resources", {}).get("cpu", "100m"),
                                        "memory": spec.get("resources", {}).get("memory", "128Mi"),
                                    },
                                    "limits": {
                                        "cpu": spec.get("resources", {}).get("limits", {}).get("cpu", "500m"),
                                        "memory": spec.get("resources", {}).get("limits", {}).get("memory", "512Mi"),
                                    },
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8080,
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8080,
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ],
                    },
                },
            },
        }
    
    def _create_service(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes service for agent"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{name}-agent",
                "namespace": self.namespace,
                "labels": {
                    "app": name,
                    "component": "agent",
                },
            },
            "spec": {
                "selector": {
                    "app": name,
                    "component": "agent",
                },
                "ports": [
                    {
                        "name": "http",
                        "port": 80,
                        "targetPort": 8080,
                        "protocol": "TCP",
                    }
                ],
                "type": "ClusterIP",
            },
        }
    
    def _create_hpa(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create Horizontal Pod Autoscaler"""
        autoscaling = spec.get("autoscaling", {})
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{name}-agent",
                "namespace": self.namespace,
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"{name}-agent",
                },
                "minReplicas": autoscaling.get("minReplicas", 1),
                "maxReplicas": autoscaling.get("maxReplicas", 10),
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": autoscaling.get("targetCPU", 80),
                            },
                        },
                    }
                ],
            },
        }
    
    def _get_agent_status(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "state": "running",
            "readyReplicas": spec.get("replicas", 1),
            "conditions": [
                {
                    "type": "Ready",
                    "status": "True",
                    "lastTransitionTime": datetime.utcnow().isoformat(),
                    "reason": "AgentReady",
                    "message": "Agent is running and ready",
                }
            ],
        }


class WorkflowController:
    """Controller for Workflow custom resources"""
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.workflows: Dict[str, Dict[str, Any]] = {}
        
    def reconcile(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconcile workflow resource
        
        Args:
            workflow: Workflow resource
            
        Returns:
            Updated workflow status
        """
        metadata = workflow.get("metadata", {})
        spec = workflow.get("spec", {})
        name = metadata.get("name")
        
        logger.info(f"Reconciling workflow: {name}")
        
        # Create CronJob if scheduled
        if spec.get("schedule"):
            cronjob = self._create_cronjob(name, spec)
        else:
            # Create Job for one-time execution
            job = self._create_job(name, spec)
        
        # Update status
        status = self._get_workflow_status(name, spec)
        
        return {
            "status": status,
            "resources": {
                "cronjob": cronjob if spec.get("schedule") else None,
                "job": job if not spec.get("schedule") else None,
            }
        }
    
    def _create_cronjob(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes CronJob for workflow"""
        return {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": f"{name}-workflow",
                "namespace": self.namespace,
                "labels": {
                    "app": name,
                    "component": "workflow",
                    "managed-by": "controlplane-operator",
                },
            },
            "spec": {
                "schedule": spec.get("schedule"),
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": "workflow",
                                        "image": "controlplane/workflow-executor:latest",
                                        "env": [
                                            {"name": "WORKFLOW_TYPE", "value": spec.get("workflowType")},
                                            {"name": "WORKFLOW_STEPS", "value": str(spec.get("steps", []))},
                                        ],
                                    }
                                ],
                                "restartPolicy": "OnFailure",
                            }
                        }
                    }
                },
            },
        }
    
    def _create_job(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes Job for workflow"""
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{name}-workflow",
                "namespace": self.namespace,
                "labels": {
                    "app": name,
                    "component": "workflow",
                },
            },
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "workflow",
                                "image": "controlplane/workflow-executor:latest",
                                "env": [
                                    {"name": "WORKFLOW_TYPE", "value": spec.get("workflowType")},
                                    {"name": "WORKFLOW_STEPS", "value": str(spec.get("steps", []))},
                                ],
                            }
                        ],
                        "restartPolicy": "OnFailure",
                    }
                },
                "backoffLimit": 3,
            },
        }
    
    def _get_workflow_status(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow status"""
        return {
            "state": "scheduled" if spec.get("schedule") else "pending",
            "lastRun": None,
            "nextRun": None,
            "executions": 0,
        }
