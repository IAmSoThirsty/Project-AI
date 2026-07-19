"""Import-backed liveness adapters for development Compose services."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Final, Literal

from fastapi import FastAPI
from kernel.version import PROJECT_AI_VERSION
from pydantic import BaseModel, ConfigDict

type ServiceRole = Literal["swr", "atlas", "arbiter-rlp"]


@dataclass(frozen=True)
class ServiceDefinition:
    modules: tuple[str, ...]
    status: str


SERVICES: Final[dict[ServiceRole, ServiceDefinition]] = {
    "swr": ServiceDefinition(("swr",), "development"),
    "atlas": ServiceDefinition(("atlas",), "development"),
    "arbiter-rlp": ServiceDefinition(("arbiter", "rlp"), "experimental"),
}


class ServiceResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["live"] = "live"
    service: ServiceRole
    version: str = PROJECT_AI_VERSION
    maturity: str
    modules: tuple[str, ...]
    authority: Literal["none"] = "none"


def create_app(role: str) -> FastAPI:
    if role not in SERVICES:
        raise ValueError(f"Unsupported service role: {role}")
    service_role = role
    definition = SERVICES[service_role]
    for module_name in definition.modules:
        module = importlib.import_module(module_name)
        module_version = getattr(module, "__version__", None)
        if module_version != PROJECT_AI_VERSION:
            raise RuntimeError(
                f"{module_name} version {module_version!r} does not match the "
                f"Project-AI release {PROJECT_AI_VERSION!r}"
            )

    application = FastAPI(
        title=f"Project-AI {service_role} development service",
        version=PROJECT_AI_VERSION,
        docs_url=None,
        redoc_url=None,
    )
    response = ServiceResponse(
        service=service_role,
        maturity=definition.status,
        modules=definition.modules,
    )

    @application.get("/health/live", response_model=ServiceResponse)
    def health_live() -> ServiceResponse:
        return response

    @application.get("/service/info", response_model=ServiceResponse)
    def service_info() -> ServiceResponse:
        return response

    return application


app = create_app(os.getenv("PROJECT_AI_SERVICE", "swr"))
