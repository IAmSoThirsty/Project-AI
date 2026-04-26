"""
External Verifiability & Documentation
======================================

REST API for external verification and living documentation generation.
"""

from .documentation_generator import DocumentationGenerator
from .verifiability_api import VerifiabilityAPI

__all__ = [
    "VerifiabilityAPI",
    "DocumentationGenerator",
]
