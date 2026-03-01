"""
Contract System for Inter-Department Integration
Implements Codex Section 6 (Cross-Department Integration)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import (
    Entity,
    EntityType,
    RelationType,
    get_registry,
)


class FailureMode(Enum):
    """Common failure modes for contracts"""

    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"


@dataclass
class APIEndpoint:
    """
    API endpoint definition (Codex 6.1)
    Typed API with parameters and return type
    """

    path: str
    parameters: Dict[str, str]  # param_name -> type
    return_type: str
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "description": self.description,
        }


@dataclass
class VersionBoundary:
    """Version boundary definition (Codex 6.1)"""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, other: "VersionBoundary") -> bool:
        """Check semantic versioning compatibility"""
        # Breaking changes only on major version
        if self.major != other.major:
            return False
        # Minor and patch versions are backward compatible
        return True

    def to_dict(self) -> Dict:
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "version_string": str(self),
        }


class Contract(Entity):
    """
    Formal contract for inter-department integration (Codex 6.1).
    Departments expose formal contracts: Typed API, Version boundary, Failure modes.
    No implicit coupling.
    """

    def __init__(
        self,
        contract_id: str,
        name: str,
        provider_department_id: str,
        version: VersionBoundary,
    ):
        super().__init__(contract_id, EntityType.CONTRACT, name)
        self.provider_department_id = provider_department_id
        self.version = version
        self.apis: Dict[str, APIEndpoint] = {}
        self.failure_modes: List[FailureMode] = []
        self.consumer_departments: List[str] = []

        # Register contract
        get_registry().register(self)

        # Log creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.entity_id,
            data={
                "entity_type": "contract",
                "provider_department_id": provider_department_id,
                "version": version.to_dict(),
            },
        )

    def add_api(self, endpoint: APIEndpoint):
        """Add an API endpoint to the contract"""
        self.apis[endpoint.path] = endpoint

    def add_failure_mode(self, mode: FailureMode):
        """Add a failure mode to the contract"""
        if mode not in self.failure_modes:
            self.failure_modes.append(mode)

    def add_consumer(self, department_id: str):
        """Register a department as a consumer of this contract"""
        if department_id not in self.consumer_departments:
            self.consumer_departments.append(department_id)

            department = get_registry().get(department_id)
            if department:
                department.declare_relationship(self, RelationType.USES)

    def is_compatible_with(self, other: "Contract") -> bool:
        """Check if this contract version is compatible with another"""
        return self.version.is_compatible_with(other.version)

    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update(
            {
                "provider_department_id": self.provider_department_id,
                "version": self.version.to_dict(),
                "apis": {path: api.to_dict() for path, api in self.apis.items()},
                "failure_modes": [fm.value for fm in self.failure_modes],
                "consumer_departments": self.consumer_departments,
            }
        )
        return base


@dataclass
class InvocationRecord:
    """
    Record of a contract invocation for telemetry (Codex 6.2)
    Elevators record invocation telemetry
    """

    invocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str = ""
    consumer_department_id: str = ""
    api_path: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = True
    error: Optional[str] = None
    latency_ms: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "invocation_id": self.invocation_id,
            "contract_id": self.contract_id,
            "consumer_department_id": self.consumer_department_id,
            "api_path": self.api_path,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


class ElevatorProtocol:
    """
    Elevator Protocol - Service bridges for contracts (Codex 6.2).
    Elevators carry contracts, perform automated compatibility checks,
    and record invocation telemetry.
    """

    def __init__(self):
        self.contracts: Dict[str, Contract] = {}
        self.invocations: List[InvocationRecord] = []

    def register_contract(self, contract: Contract):
        """Register a contract in the elevator system"""
        self.contracts[contract.entity_id] = contract

        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=contract.entity_id,
            data={
                "action": "contract_registered_in_elevator",
                "contract_name": contract.name,
            },
        )

    def check_compatibility(
        self, consumer_department_id: str, contract_id: str
    ) -> bool:
        """
        Perform automated compatibility check (Codex 6.2).
        Elevators perform automated compatibility checks.
        """
        contract = self.contracts.get(contract_id)
        if not contract:
            return False

        # Check if consumer department exists
        consumer = get_registry().get(consumer_department_id)
        if not consumer:
            return False

        # Additional compatibility checks can be added here
        # (e.g., capability matching, security clearance)

        return True

    def invoke_contract(
        self,
        consumer_department_id: str,
        contract_id: str,
        api_path: str,
        parameters: Optional[Dict] = None,
    ) -> InvocationRecord:
        """
        Invoke a contract API and record telemetry (Codex 6.2).
        Returns invocation record.
        """
        start_time = datetime.utcnow()

        contract = self.contracts.get(contract_id)
        if not contract:
            record = InvocationRecord(
                contract_id=contract_id,
                consumer_department_id=consumer_department_id,
                api_path=api_path,
                success=False,
                error="Contract not found",
            )
            self.invocations.append(record)
            return record

        # Check compatibility
        if not self.check_compatibility(consumer_department_id, contract_id):
            record = InvocationRecord(
                contract_id=contract_id,
                consumer_department_id=consumer_department_id,
                api_path=api_path,
                success=False,
                error="Compatibility check failed",
            )
            self.invocations.append(record)
            return record

        # Check API exists
        api = contract.apis.get(api_path)
        if not api:
            record = InvocationRecord(
                contract_id=contract_id,
                consumer_department_id=consumer_department_id,
                api_path=api_path,
                success=False,
                error="API endpoint not found",
            )
            self.invocations.append(record)
            return record

        # Simulate invocation (in real implementation, this would call actual service)
        end_time = datetime.utcnow()
        latency = (end_time - start_time).total_seconds() * 1000

        record = InvocationRecord(
            contract_id=contract_id,
            consumer_department_id=consumer_department_id,
            api_path=api_path,
            success=True,
            latency_ms=latency,
        )
        self.invocations.append(record)

        # Log invocation
        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=consumer_department_id,
            target_id=contract_id,
            data={
                "action": "contract_invoked",
                "invocation_id": record.invocation_id,
                "api_path": api_path,
                "success": record.success,
            },
        )

        return record

    def get_contract_metrics(self, contract_id: str) -> Dict:
        """Get metrics for a contract"""
        relevant_invocations = [
            i for i in self.invocations if i.contract_id == contract_id
        ]

        if not relevant_invocations:
            return {"total_invocations": 0, "success_rate": 0.0, "avg_latency_ms": 0.0}

        total = len(relevant_invocations)
        successes = sum(1 for i in relevant_invocations if i.success)
        avg_latency = sum(i.latency_ms for i in relevant_invocations) / total

        return {
            "total_invocations": total,
            "success_rate": successes / total,
            "avg_latency_ms": avg_latency,
        }


# Global elevator protocol
_elevator_protocol = ElevatorProtocol()


def get_elevator_protocol() -> ElevatorProtocol:
    """Get the global elevator protocol"""
    return _elevator_protocol
