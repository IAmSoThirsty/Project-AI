"""
Example Workflows for Workflow Orchestration Engine

Demonstrates the engine capabilities with practical examples:
1. Build Pipeline
2. Security Scan
3. Deployment Workflow
"""

__all__ = [
    "create_build_pipeline",
    "create_security_scan_workflow",
    "create_deployment_workflow",
]

from .build_pipeline import create_build_pipeline
from .security_scan import create_security_scan_workflow
from .deployment import create_deployment_workflow
