"""Project-AI development service adapters."""

from kernel.version import distribution_version

from project_ai_services.app import ServiceResponse, create_app

__version__ = distribution_version("project-ai-service-host")

__all__ = ["ServiceResponse", "create_app"]
