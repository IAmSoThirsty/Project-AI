"""
Custom Resource Definitions (CRDs)

Kubernetes custom resources for agents and workflows.
"""

from typing import Dict, Any


class AgentCRD:
    """Agent Custom Resource Definition"""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get Agent CRD definition"""
        return {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": "agents.temporal.controlplane.io",
            },
            "spec": {
                "group": "temporal.controlplane.io",
                "versions": [
                    {
                        "name": "v1",
                        "served": True,
                        "storage": True,
                        "schema": {
                            "openAPIV3Schema": {
                                "type": "object",
                                "properties": {
                                    "spec": {
                                        "type": "object",
                                        "required": ["agentType", "version"],
                                        "properties": {
                                            "agentType": {
                                                "type": "string",
                                                "description": "Type of agent",
                                            },
                                            "version": {
                                                "type": "string",
                                                "description": "Agent version",
                                            },
                                            "replicas": {
                                                "type": "integer",
                                                "minimum": 1,
                                                "default": 1,
                                                "description": "Number of replicas",
                                            },
                                            "image": {
                                                "type": "string",
                                                "description": "Container image",
                                            },
                                            "config": {
                                                "type": "object",
                                                "description": "Agent configuration",
                                                "x-kubernetes-preserve-unknown-fields": True,
                                            },
                                            "resources": {
                                                "type": "object",
                                                "properties": {
                                                    "cpu": {
                                                        "type": "string",
                                                        "default": "100m",
                                                    },
                                                    "memory": {
                                                        "type": "string",
                                                        "default": "128Mi",
                                                    },
                                                    "limits": {
                                                        "type": "object",
                                                        "properties": {
                                                            "cpu": {
                                                                "type": "string",
                                                                "default": "500m",
                                                            },
                                                            "memory": {
                                                                "type": "string",
                                                                "default": "512Mi",
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            "autoscaling": {
                                                "type": "object",
                                                "properties": {
                                                    "enabled": {
                                                        "type": "boolean",
                                                        "default": False,
                                                    },
                                                    "minReplicas": {
                                                        "type": "integer",
                                                        "default": 1,
                                                    },
                                                    "maxReplicas": {
                                                        "type": "integer",
                                                        "default": 10,
                                                    },
                                                    "targetCPU": {
                                                        "type": "integer",
                                                        "default": 80,
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "status": {
                                        "type": "object",
                                        "properties": {
                                            "state": {
                                                "type": "string",
                                                "description": "Current state",
                                            },
                                            "readyReplicas": {
                                                "type": "integer",
                                                "description": "Number of ready replicas",
                                            },
                                            "conditions": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "type": {"type": "string"},
                                                        "status": {"type": "string"},
                                                        "lastTransitionTime": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                        },
                                                        "reason": {"type": "string"},
                                                        "message": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "subresources": {
                            "status": {},
                            "scale": {
                                "specReplicasPath": ".spec.replicas",
                                "statusReplicasPath": ".status.readyReplicas",
                            },
                        },
                    }
                ],
                "scope": "Namespaced",
                "names": {
                    "plural": "agents",
                    "singular": "agent",
                    "kind": "Agent",
                    "shortNames": ["ag"],
                },
            },
        }


class WorkflowCRD:
    """Workflow Custom Resource Definition"""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get Workflow CRD definition"""
        return {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": "workflows.temporal.controlplane.io",
            },
            "spec": {
                "group": "temporal.controlplane.io",
                "versions": [
                    {
                        "name": "v1",
                        "served": True,
                        "storage": True,
                        "schema": {
                            "openAPIV3Schema": {
                                "type": "object",
                                "properties": {
                                    "spec": {
                                        "type": "object",
                                        "required": ["workflowType"],
                                        "properties": {
                                            "workflowType": {
                                                "type": "string",
                                                "description": "Type of workflow",
                                            },
                                            "schedule": {
                                                "type": "string",
                                                "description": "Cron schedule",
                                            },
                                            "steps": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["name", "action"],
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "action": {"type": "string"},
                                                        "params": {
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                    },
                                                },
                                            },
                                            "timeout": {
                                                "type": "string",
                                                "default": "1h",
                                                "description": "Workflow timeout",
                                            },
                                        },
                                    },
                                    "status": {
                                        "type": "object",
                                        "properties": {
                                            "state": {
                                                "type": "string",
                                                "description": "Current state",
                                            },
                                            "lastRun": {
                                                "type": "string",
                                                "format": "date-time",
                                            },
                                            "nextRun": {
                                                "type": "string",
                                                "format": "date-time",
                                            },
                                            "executions": {
                                                "type": "integer",
                                                "description": "Total executions",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "subresources": {
                            "status": {},
                        },
                    }
                ],
                "scope": "Namespaced",
                "names": {
                    "plural": "workflows",
                    "singular": "workflow",
                    "kind": "Workflow",
                    "shortNames": ["wf"],
                },
            },
        }
