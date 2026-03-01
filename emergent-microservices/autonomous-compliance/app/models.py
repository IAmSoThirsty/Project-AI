from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ComplianceRule(BaseModel):
    """Compliance-as-Code rule definition"""

    model_config = ConfigDict(from_attributes=True)

    id: str  # Rule ID (e.g., PAGL-001)
    name: str
    description: str
    severity: str  # low, medium, high, critical
    logic_expression: str  # Tarl / PAGL expression
    is_active: bool = True


class ComplianceAudit(BaseModel):
    """Record of a compliance check execution"""

    id: UUID = Field(default_factory=uuid4)
    rule_id: str
    target_id: str
    evaluation_result: bool
    details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class PolicyViolation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    audit_id: UUID
    severity: str
    mitigation_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)


class RuleCreate(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    logic_expression: str


class AuditTrigger(BaseModel):
    target_id: str
    data_context: Dict[str, Any]
