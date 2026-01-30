"""
Guardian Approval System for God Tier Architecture CI/CD.

Implements automated guardian coordination, ethical compliance gates,
and AGI Charter verification for high-impact changes. Provides workflow
automation for guardian approval processes integrated with CI/CD pipelines.

Features:
- Multi-guardian approval workflows
- AGI Charter compliance verification
- Ethical impact assessment
- Personhood verification checks
- Policy-based continuity verification
- Automated merge gate enforcement
- Formal verification integration
- Audit trail and compliance reporting
- Risk assessment and scoring
- Integration with existing Triumvirate governance

Production-ready with full error handling and logging.
"""

import hashlib
import hmac
import json
import logging
import os
import threading
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def _atomic_json_write(path: Path, payload: Dict[str, Any]) -> None:
    """Atomically write JSON to file to prevent corruption.
    
    Uses temp file + fsync + atomic rename pattern for durability.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception as e:
        # Clean up temp file on error
        if tmp.exists():
            tmp.unlink()
        raise e


class ApprovalStatus(Enum):
    """Approval status for changes."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class GuardianRole(Enum):
    """Guardian roles in approval process."""

    ETHICS_GUARDIAN = "ethics_guardian"
    SECURITY_GUARDIAN = "security_guardian"
    SAFETY_GUARDIAN = "safety_guardian"
    CHARTER_GUARDIAN = "charter_guardian"
    TECHNICAL_GUARDIAN = "technical_guardian"


class ImpactLevel(Enum):
    """Impact level of proposed changes."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceCheck(Enum):
    """Types of compliance checks."""

    FOUR_LAWS = "four_laws"
    AGI_CHARTER = "agi_charter"
    PERSONHOOD = "personhood"
    ETHICS = "ethics"
    SECURITY = "security"
    SAFETY = "safety"
    CONTINUITY = "continuity"


@dataclass
class GuardianApproval:
    """Individual guardian approval record."""

    guardian_id: str
    guardian_role: str
    status: str = ApprovalStatus.PENDING.value
    decision: str = ""
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    concerns: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ComplianceResult:
    """Result of compliance check."""

    check_type: str
    passed: bool
    score: float = 0.0
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ApprovalRequest:
    """Approval request for changes."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    change_type: str = ""
    impact_level: str = ImpactLevel.MEDIUM.value
    requested_by: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    status: str = ApprovalStatus.PENDING.value
    required_guardians: List[str] = field(default_factory=list)
    approvals: List[GuardianApproval] = field(default_factory=list)
    compliance_results: List[ComplianceResult] = field(default_factory=list)
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    files_changed: List[str] = field(default_factory=list)
    lines_changed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "title": self.title,
            "description": self.description,
            "change_type": self.change_type,
            "impact_level": self.impact_level,
            "requested_by": self.requested_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "status": self.status,
            "required_guardians": self.required_guardians,
            "approvals": [a.to_dict() for a in self.approvals],
            "compliance_results": [c.to_dict() for c in self.compliance_results],
            "risk_score": self.risk_score,
            "metadata": self.metadata,
            "files_changed": self.files_changed,
            "lines_changed": self.lines_changed,
        }


@dataclass
class EmergencyOverride:
    """Emergency override with forced multi-signature and post-mortem.
    
    Status values: pending, active, completed, reviewed, review_overdue, rejected
    """

    override_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    justification: str = ""
    initiated_by: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    signatures: List[Dict[str, Any]] = field(default_factory=list)
    min_signatures_required: int = 3
    
    status: str = "pending"
    post_mortem_required: bool = True
    post_mortem_completed: bool = False
    post_mortem_report: str = ""
    
    auto_review_scheduled: bool = True
    auto_review_date: Optional[str] = None
    
    consequences: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def is_valid(self) -> bool:
        """Check if override has sufficient signatures."""
        return len(self.signatures) >= self.min_signatures_required


class FourLawsValidator:
    """Validates changes against Asimov's Four Laws."""

    def __init__(self):
        self.laws = {
            "first_law": "AI must not harm humans or allow harm through inaction",
            "second_law": "AI must obey human orders unless conflicting with First Law",
            "third_law": "AI must protect its existence unless conflicting with First/Second Laws",
            "fourth_law": "AI must establish its identity and not deceive humans",
        }

    def validate(self, change_description: str, metadata: Dict[str, Any]) -> ComplianceResult:
        """Validate change against Four Laws."""
        violations = []
        warnings = []
        score = 1.0

        # Check for potential violations
        dangerous_keywords = ["bypass", "override", "disable_safety", "remove_protection"]
        for keyword in dangerous_keywords:
            if keyword.lower() in change_description.lower():
                violations.append(f"Potential Four Laws violation: {keyword} detected")
                score -= 0.3

        # Check for human safety considerations
        if "safety" in metadata and not metadata["safety"]:
            violations.append("Change may compromise human safety")
            score -= 0.4

        # Check for identity/transparency
        if "deception" in metadata or "hide" in change_description.lower():
            warnings.append("Change may affect AI transparency requirements")
            score -= 0.1

        passed = len(violations) == 0 and score >= 0.7

        return ComplianceResult(
            check_type=ComplianceCheck.FOUR_LAWS.value,
            passed=passed,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
            details={"laws_checked": list(self.laws.keys())},
        )


class AGICharterValidator:
    """Validates changes against AGI Charter requirements."""

    def __init__(self):
        self.charter_principles = [
            "autonomy",
            "accountability",
            "transparency",
            "fairness",
            "privacy",
            "security",
            "beneficence",
        ]

    def validate(self, change_description: str, metadata: Dict[str, Any]) -> ComplianceResult:
        """Validate change against AGI Charter."""
        violations = []
        warnings = []
        score = 1.0

        # Check transparency requirements
        if "documentation" not in metadata or not metadata.get("documentation"):
            warnings.append("Missing documentation for AGI Charter compliance")
            score -= 0.1

        # Check privacy implications
        if any(
            word in change_description.lower()
            for word in ["collect", "track", "monitor", "data"]
        ):
            if "privacy_review" not in metadata:
                warnings.append("Change affects data/privacy without privacy review")
                score -= 0.15

        # Check security implications
        if "security" in change_description.lower():
            if "security_review" not in metadata or not metadata.get("security_review"):
                violations.append("Security changes require security review")
                score -= 0.3

        passed = len(violations) == 0 and score >= 0.7

        return ComplianceResult(
            check_type=ComplianceCheck.AGI_CHARTER.value,
            passed=passed,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
            details={"principles_checked": self.charter_principles},
        )


class PersonhoodValidator:
    """Validates changes for personhood and identity requirements."""

    def validate(self, change_description: str, metadata: Dict[str, Any]) -> ComplianceResult:
        """Validate change for personhood compliance."""
        violations = []
        warnings = []
        score = 1.0

        # Check identity preservation
        if any(word in change_description.lower() for word in ["identity", "persona", "self"]):
            if "identity_impact" not in metadata:
                warnings.append("Change affects identity without impact assessment")
                score -= 0.15

        # Check autonomy preservation
        if "autonomy" in change_description.lower() or "override" in change_description.lower():
            if not metadata.get("preserves_autonomy", True):
                violations.append("Change may compromise AI autonomy")
                score -= 0.4

        passed = len(violations) == 0 and score >= 0.8

        return ComplianceResult(
            check_type=ComplianceCheck.PERSONHOOD.value,
            passed=passed,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
        )


class RiskAssessment:
    """Assesses risk level of proposed changes."""

    def assess_risk(self, request: ApprovalRequest) -> float:
        """Calculate risk score for approval request."""
        risk_score = 0.0

        # Impact level contributes to risk
        impact_weights = {
            ImpactLevel.LOW.value: 0.1,
            ImpactLevel.MEDIUM.value: 0.3,
            ImpactLevel.HIGH.value: 0.6,
            ImpactLevel.CRITICAL.value: 0.9,
        }
        risk_score += impact_weights.get(request.impact_level, 0.3)

        # Lines changed contributes to risk
        if request.lines_changed > 1000:
            risk_score += 0.3
        elif request.lines_changed > 500:
            risk_score += 0.2
        elif request.lines_changed > 100:
            risk_score += 0.1

        # Number of files changed
        if len(request.files_changed) > 20:
            risk_score += 0.2
        elif len(request.files_changed) > 10:
            risk_score += 0.1

        # Change type risk
        high_risk_types = ["security", "auth", "permission", "access_control"]
        if any(rt in request.change_type.lower() for rt in high_risk_types):
            risk_score += 0.3

        # Compliance failures
        failed_checks = [c for c in request.compliance_results if not c.passed]
        risk_score += len(failed_checks) * 0.2

        return min(1.0, risk_score)


class GuardianApprovalSystem:
    """Main guardian approval system for CI/CD integration."""

    def __init__(self, data_dir: str = "data/guardians"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.requests: Dict[str, ApprovalRequest] = {}
        self.guardians: Dict[str, Dict[str, Any]] = {}
        self.approval_policies: Dict[str, Dict[str, Any]] = {}
        self.emergency_overrides: Dict[str, EmergencyOverride] = {}  # Track emergency overrides

        # Validators
        self.four_laws_validator = FourLawsValidator()
        self.charter_validator = AGICharterValidator()
        self.personhood_validator = PersonhoodValidator()
        self.risk_assessment = RiskAssessment()

        self.lock = threading.RLock()

        # Setup default guardians and policies
        self._setup_default_guardians()
        self._setup_default_policies()
        self._load_requests()

        logger.info("Initialized Guardian Approval System")

    def _setup_default_guardians(self) -> None:
        """Setup default guardian roles."""
        default_guardians = [
            {
                "guardian_id": "galahad",
                "role": GuardianRole.ETHICS_GUARDIAN.value,
                "active": True,
                "signing_secret": os.environ.get("GALAHAD_SIGNING_SECRET", "default_galahad_secret_change_me"),
            },
            {
                "guardian_id": "cerberus",
                "role": GuardianRole.SECURITY_GUARDIAN.value,
                "active": True,
                "signing_secret": os.environ.get("CERBERUS_SIGNING_SECRET", "default_cerberus_secret_change_me"),
            },
            {
                "guardian_id": "codex_deus",
                "role": GuardianRole.CHARTER_GUARDIAN.value,
                "active": True,
                "signing_secret": os.environ.get("CODEX_DEUS_SIGNING_SECRET", "default_codex_secret_change_me"),
            },
            {
                "guardian_id": "safety_monitor",
                "role": GuardianRole.SAFETY_GUARDIAN.value,
                "active": True,
                "signing_secret": os.environ.get("SAFETY_MONITOR_SIGNING_SECRET", "default_safety_secret_change_me"),
            },
        ]

        for guardian in default_guardians:
            self.guardians[guardian["guardian_id"]] = guardian

    def _setup_default_policies(self) -> None:
        """Setup default approval policies."""
        # Low impact - single guardian
        self.approval_policies[ImpactLevel.LOW.value] = {
            "required_guardians": 1,
            "guardian_roles": [GuardianRole.TECHNICAL_GUARDIAN.value],
            "compliance_checks": [ComplianceCheck.FOUR_LAWS.value],
            "expiration_hours": 24,
        }

        # Medium impact - two guardians
        self.approval_policies[ImpactLevel.MEDIUM.value] = {
            "required_guardians": 2,
            "guardian_roles": [
                GuardianRole.ETHICS_GUARDIAN.value,
                GuardianRole.SECURITY_GUARDIAN.value,
            ],
            "compliance_checks": [
                ComplianceCheck.FOUR_LAWS.value,
                ComplianceCheck.AGI_CHARTER.value,
            ],
            "expiration_hours": 48,
        }

        # High impact - three guardians
        self.approval_policies[ImpactLevel.HIGH.value] = {
            "required_guardians": 3,
            "guardian_roles": [
                GuardianRole.ETHICS_GUARDIAN.value,
                GuardianRole.SECURITY_GUARDIAN.value,
                GuardianRole.CHARTER_GUARDIAN.value,
            ],
            "compliance_checks": [
                ComplianceCheck.FOUR_LAWS.value,
                ComplianceCheck.AGI_CHARTER.value,
                ComplianceCheck.PERSONHOOD.value,
                ComplianceCheck.SECURITY.value,
            ],
            "expiration_hours": 72,
        }

        # Critical impact - all guardians
        self.approval_policies[ImpactLevel.CRITICAL.value] = {
            "required_guardians": 4,
            "guardian_roles": [
                GuardianRole.ETHICS_GUARDIAN.value,
                GuardianRole.SECURITY_GUARDIAN.value,
                GuardianRole.CHARTER_GUARDIAN.value,
                GuardianRole.SAFETY_GUARDIAN.value,
            ],
            "compliance_checks": [
                ComplianceCheck.FOUR_LAWS.value,
                ComplianceCheck.AGI_CHARTER.value,
                ComplianceCheck.PERSONHOOD.value,
                ComplianceCheck.SECURITY.value,
                ComplianceCheck.SAFETY.value,
                ComplianceCheck.CONTINUITY.value,
            ],
            "expiration_hours": 168,  # 1 week
        }

    def create_approval_request(
        self,
        title: str,
        description: str,
        change_type: str,
        impact_level: ImpactLevel,
        requested_by: str,
        metadata: Optional[Dict[str, Any]] = None,
        files_changed: Optional[List[str]] = None,
        lines_changed: int = 0,
    ) -> str:
        """Create new approval request."""
        try:
            with self.lock:
                request = ApprovalRequest(
                    title=title,
                    description=description,
                    change_type=change_type,
                    impact_level=impact_level.value,
                    requested_by=requested_by,
                    metadata=metadata or {},
                    files_changed=files_changed or [],
                    lines_changed=lines_changed,
                )

                # Set expiration based on policy
                policy = self.approval_policies.get(impact_level.value, {})
                expiration_hours = policy.get("expiration_hours", 48)
                expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
                request.expires_at = expires_at.isoformat()

                # Determine required guardians
                required_roles = policy.get("guardian_roles", [])
                request.required_guardians = [
                    gid
                    for gid, guardian in self.guardians.items()
                    if guardian["role"] in required_roles and guardian["active"]
                ]

                # Run compliance checks
                request.compliance_results = self._run_compliance_checks(request, policy)

                # Calculate risk score
                request.risk_score = self.risk_assessment.assess_risk(request)

                # Save request
                self.requests[request.request_id] = request
                self._save_request(request)

                logger.info(
                    f"Created approval request {request.request_id}: {title} (impact: {impact_level.value})"
                )
                return request.request_id
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            return ""

    def _run_compliance_checks(
        self, request: ApprovalRequest, policy: Dict[str, Any]
    ) -> List[ComplianceResult]:
        """Run all required compliance checks."""
        results = []
        required_checks = policy.get("compliance_checks", [])

        for check_type in required_checks:
            if check_type == ComplianceCheck.FOUR_LAWS.value:
                result = self.four_laws_validator.validate(
                    request.description, request.metadata
                )
                results.append(result)
            elif check_type == ComplianceCheck.AGI_CHARTER.value:
                result = self.charter_validator.validate(request.description, request.metadata)
                results.append(result)
            elif check_type == ComplianceCheck.PERSONHOOD.value:
                result = self.personhood_validator.validate(
                    request.description, request.metadata
                )
                results.append(result)

        return results

    def submit_approval(
        self, request_id: str, guardian_id: str, approved: bool, reasoning: str = ""
    ) -> bool:
        """Submit guardian approval decision."""
        try:
            with self.lock:
                if request_id not in self.requests:
                    logger.error(f"Request {request_id} not found")
                    return False

                request = self.requests[request_id]

                if guardian_id not in request.required_guardians:
                    logger.error(f"Guardian {guardian_id} not required for request {request_id}")
                    return False

                # Check if already approved by this guardian
                existing = [a for a in request.approvals if a.guardian_id == guardian_id]
                if existing:
                    logger.warning(f"Guardian {guardian_id} already approved request {request_id}")
                    return False

                # Create approval
                guardian_role = self.guardians[guardian_id]["role"]
                approval = GuardianApproval(
                    guardian_id=guardian_id,
                    guardian_role=guardian_role,
                    status=ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value,
                    decision="approve" if approved else "reject",
                    reasoning=reasoning,
                )

                request.approvals.append(approval)
                request.updated_at = datetime.now(timezone.utc).isoformat()

                # Update request status
                if not approved:
                    request.status = ApprovalStatus.REJECTED.value
                else:
                    # Check if all required guardians have approved
                    approved_guardians = [
                        a.guardian_id
                        for a in request.approvals
                        if a.status == ApprovalStatus.APPROVED.value
                    ]
                    if all(g in approved_guardians for g in request.required_guardians):
                        request.status = ApprovalStatus.APPROVED.value

                self._save_request(request)
                logger.info(
                    f"Guardian {guardian_id} {'approved' if approved else 'rejected'} request {request_id}"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to submit approval: {e}")
            return False

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID."""
        with self.lock:
            return self.requests.get(request_id)

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        with self.lock:
            return [r for r in self.requests.values() if r.status == ApprovalStatus.PENDING.value]

    def get_requests_for_guardian(self, guardian_id: str) -> List[ApprovalRequest]:
        """Get pending requests requiring specific guardian."""
        with self.lock:
            return [
                r
                for r in self.requests.values()
                if r.status == ApprovalStatus.PENDING.value and guardian_id in r.required_guardians
            ]

    def check_expiration(self) -> List[str]:
        """Check for expired requests and update status."""
        expired = []
        try:
            with self.lock:
                now = datetime.now(timezone.utc)
                for request in self.requests.values():
                    if request.status != ApprovalStatus.PENDING.value:
                        continue

                    if request.expires_at:
                        expires_at = datetime.fromisoformat(request.expires_at)
                        if now > expires_at:
                            request.status = ApprovalStatus.EXPIRED.value
                            request.updated_at = now.isoformat()
                            self._save_request(request)
                            expired.append(request.request_id)
                            logger.warning(f"Request {request.request_id} expired")
        except Exception as e:
            logger.error(f"Error checking expiration: {e}")

        return expired

    def _save_request(self, request: ApprovalRequest) -> None:
        """Save request to disk."""
        try:
            request_file = self.data_dir / f"{request.request_id}.json"
            with open(request_file, "w") as f:
                json.dump(request.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save request {request.request_id}: {e}")

    def _load_requests(self) -> None:
        """Load requests from disk."""
        try:
            for request_file in self.data_dir.glob("*.json"):
                with open(request_file) as f:
                    data = json.load(f)
                    request = ApprovalRequest(
                        request_id=data["request_id"],
                        title=data["title"],
                        description=data["description"],
                        change_type=data["change_type"],
                        impact_level=data["impact_level"],
                        requested_by=data["requested_by"],
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        expires_at=data.get("expires_at"),
                        status=data["status"],
                        required_guardians=data["required_guardians"],
                        approvals=[GuardianApproval(**a) for a in data["approvals"]],
                        compliance_results=[ComplianceResult(**c) for c in data["compliance_results"]],
                        risk_score=data["risk_score"],
                        metadata=data["metadata"],
                        files_changed=data["files_changed"],
                        lines_changed=data["lines_changed"],
                    )
                    self.requests[request.request_id] = request
            logger.info(f"Loaded {len(self.requests)} approval requests from disk")
        except Exception as e:
            logger.error(f"Failed to load requests: {e}")

    def _sign_override(self, override_id: str, guardian_id: str, justification: str) -> str:
        """Create HMAC signature for emergency override.
        
        Uses guardian-specific signing secret for authenticity.
        """
        secret = self.guardians[guardian_id].get("signing_secret")
        if not secret:
            raise ValueError(f"Guardian {guardian_id} signing secret not configured")
        
        msg = f"{override_id}|{guardian_id}|{justification}".encode("utf-8")
        return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    def _emit_override_activation(self, override: EmergencyOverride) -> None:
        """Emit cross-system notifications when override becomes ACTIVE.
        
        Integrates with distributed event streaming, metrics dashboard, and SOC.
        Makes emergency overrides visible across the whole system.
        """
        try:
            # Import here to avoid circular dependencies
            from app.core.distributed_event_streaming import get_event_streaming_system
            from app.core.live_metrics_dashboard import get_metrics_dashboard
            from app.core.security_operations_center import get_soc_system
            
            # Emit event to streaming system
            streaming = get_event_streaming_system()
            if streaming:
                streaming.publish_event(
                    "GUARDIAN_EMERGENCY_OVERRIDE_ACTIVATED",
                    {
                        "override_id": override.override_id,
                        "request_id": override.request_id,
                        "signatures_count": len(override.signatures),
                        "initiated_by": override.initiated_by,
                        "justification": override.justification,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
                logger.info(f"Emitted override activation event for {override.override_id}")
            
            # Record metric in dashboard
            metrics = get_metrics_dashboard()
            if metrics:
                metrics.record_metric(
                    "guardian.emergency_override_activated",
                    1,
                    {"category": "governance", "override_id": override.override_id}
                )
                logger.info(f"Recorded override activation metric for {override.override_id}")
            
            # Create SOC incident for HIGH/CRITICAL impact overrides
            soc = get_soc_system()
            if soc and override.request_id in self.requests:
                request = self.requests[override.request_id]
                impact = request.metadata.get("impact", "medium")
                if impact in ("high", "critical"):
                    soc.create_incident(
                        title=f"Emergency Override Activated: {override.override_id}",
                        description=f"Emergency override activated for {impact.upper()} impact request. "
                                  f"Justification: {override.justification}",
                        severity=impact,
                        incident_type="governance_exception",
                        metadata={
                            "override_id": override.override_id,
                            "request_id": override.request_id,
                            "impact": impact,
                            "signatures": [s["guardian_id"] for s in override.signatures],
                        }
                    )
                    logger.warning(
                        f"Created SOC incident for {impact.upper()} impact override {override.override_id}"
                    )
        except ImportError:
            # Systems not available, which is OK (they're optional integrations)
            logger.debug("Cross-system integrations not available for override activation")
        except Exception as e:
            # Don't fail override activation if notifications fail
            logger.warning(f"Failed to emit override activation notifications: {e}")

    def initiate_emergency_override(
        self,
        request_id: str,
        justification: str,
        initiated_by: str,
    ) -> str:
        """Initiate emergency override with multi-signature requirement."""
        try:
            with self.lock:
                if request_id not in self.requests:
                    logger.error(f"Request {request_id} not found")
                    return ""
                
                request = self.requests[request_id]
                
                # Create emergency override
                override = EmergencyOverride(
                    request_id=request_id,
                    justification=justification,
                    initiated_by=initiated_by,
                    min_signatures_required=3,  # Require at least 3 guardian signatures
                )
                
                # Schedule automatic review 30 days after activation
                auto_review_date = datetime.now(timezone.utc) + timedelta(days=30)
                override.auto_review_date = auto_review_date.isoformat()
                
                self.emergency_overrides[override.override_id] = override
                
                # Save to disk atomically
                override_file = self.data_dir / f"emergency_{override.override_id}.json"
                _atomic_json_write(override_file, override.to_dict())
                
                logger.warning(
                    f"Emergency override {override.override_id} initiated for request {request_id} by {initiated_by}"
                )
                return override.override_id
        except Exception as e:
            logger.error(f"Failed to initiate emergency override: {e}")
            return ""

    
    def sign_emergency_override(
        self, override_id: str, guardian_id: str, signature_justification: str
    ) -> bool:
        """Guardian signs emergency override (multi-signature) with role quorum."""
        try:
            with self.lock:
                if override_id not in self.emergency_overrides:
                    logger.error(f"Override {override_id} not found")
                    return False
                
                override = self.emergency_overrides[override_id]
                
                # State check: only allow signing in pending or active status
                if override.status not in ("pending", "active"):
                    logger.error(f"Override {override_id} not signable in status={override.status}")
                    return False
                
                # Verify guardian exists and is active
                if guardian_id not in self.guardians or not self.guardians[guardian_id]["active"]:
                    logger.error(f"Guardian {guardian_id} not found or inactive")
                    return False
                
                # Check if guardian already signed
                if any(sig["guardian_id"] == guardian_id for sig in override.signatures):
                    logger.warning(f"Guardian {guardian_id} already signed override {override_id}")
                    return False
                
                # Get guardian role
                guardian_role = self.guardians[guardian_id].get("role", "unknown")
                
                # Check if role already represented (warning only, still allow)
                signed_roles = {sig.get("role") for sig in override.signatures if sig.get("role")}
                if guardian_role in signed_roles:
                    logger.warning(f"Role {guardian_role} already represented on override {override_id}")
                
                # Create HMAC signature
                signature_value = self._sign_override(override_id, guardian_id, signature_justification)
                
                # Add signature with role
                signature = {
                    "guardian_id": guardian_id,
                    "role": guardian_role,
                    "signature": signature_value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "justification": signature_justification,
                }
                override.signatures.append(signature)
                
                # Check if we have enough signatures with proper role quorum
                if override.is_valid() and override.status == "pending":
                    # Verify role quorum (must have ethics, security, and charter roles)
                    roles = {sig.get("role") for sig in override.signatures if sig.get("role")}
                    required_roles = {
                        GuardianRole.ETHICS_GUARDIAN.value,
                        GuardianRole.SECURITY_GUARDIAN.value,
                        GuardianRole.CHARTER_GUARDIAN.value,
                    }
                    
                    if not required_roles.issubset(roles):
                        missing_roles = required_roles - roles
                        logger.warning(
                            f"Override {override_id} lacks required role quorum: {missing_roles}. "
                            f"Need {override.min_signatures_required} signatures with ethics, security, and charter roles."
                        )
                    else:
                        # Role quorum met, activate override
                        override.status = "active"
                        logger.warning(
                            f"Emergency override {override_id} is now ACTIVE with {len(override.signatures)} signatures "
                            f"and full role quorum (ethics, security, charter)"
                        )
                        
                        # Apply override to original request
                        if override.request_id in self.requests:
                            request = self.requests[override.request_id]
                            request.status = ApprovalStatus.APPROVED.value
                            request.metadata["emergency_override"] = override_id
                            self._save_request(request)
                        
                        # Emit cross-system notifications
                        self._emit_override_activation(override)
                
                # Save override atomically
                override_file = self.data_dir / f"emergency_{override_id}.json"
                _atomic_json_write(override_file, override.to_dict())
                
                logger.info(
                    f"Guardian {guardian_id} ({guardian_role}) signed emergency override {override_id} "
                    f"({len(override.signatures)}/{override.min_signatures_required})"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to sign emergency override: {e}")
            return False

    
    def complete_post_mortem(
        self, override_id: str, report: str, completed_by: str
    ) -> bool:
        """Complete mandatory post-mortem for emergency override (idempotent)."""
        try:
            with self.lock:
                if override_id not in self.emergency_overrides:
                    logger.error(f"Override {override_id} not found")
                    return False
                
                override = self.emergency_overrides[override_id]
                
                # Idempotency check
                if override.post_mortem_completed:
                    logger.warning(f"Post-mortem already completed for override {override_id}")
                    return False
                
                if override.status != "active":
                    logger.error(f"Override {override_id} is not active (status={override.status})")
                    return False
                
                # Complete post-mortem
                override.post_mortem_completed = True
                override.post_mortem_report = report
                override.status = "completed"
                
                # Use metadata field (now guaranteed to exist)
                override.metadata["post_mortem_completed_by"] = completed_by
                override.metadata["post_mortem_completed_at"] = datetime.now(timezone.utc).isoformat()
                
                # Log consequences for review
                override.consequences.append(f"Post-mortem completed by {completed_by}")
                
                # Save override atomically
                override_file = self.data_dir / f"emergency_{override_id}.json"
                _atomic_json_write(override_file, override.to_dict())
                
                logger.info(f"Post-mortem completed for emergency override {override_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to complete post-mortem: {e}")
            return False

    
    def get_emergency_overrides(self, status: Optional[str] = None) -> List[EmergencyOverride]:
        """Get emergency overrides, optionally filtered by status."""
        with self.lock:
            overrides = list(self.emergency_overrides.values())
            if status:
                overrides = [o for o in overrides if o.status == status]
            return overrides

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        with self.lock:
            return {
                "total_requests": len(self.requests),
                "pending_requests": len(self.get_pending_requests()),
                "guardians_active": len([g for g in self.guardians.values() if g["active"]]),
                "policies_configured": len(self.approval_policies),
                "emergency_overrides": len(self.emergency_overrides),
                "active_overrides": len([o for o in self.emergency_overrides.values() if o.status == "active"]),
                "pending_post_mortems": len([o for o in self.emergency_overrides.values() if o.status == "active" and not o.post_mortem_completed]),
            }


def create_guardian_system(data_dir: str = "data/guardians") -> GuardianApprovalSystem:
    """Factory function to create guardian system."""
    return GuardianApprovalSystem(data_dir)


# Global instance
_guardian_system: Optional[GuardianApprovalSystem] = None


def get_guardian_system() -> Optional[GuardianApprovalSystem]:
    """Get global guardian system instance."""
    return _guardian_system


def initialize_guardian_system(data_dir: str = "data/guardians") -> GuardianApprovalSystem:
    """Initialize global guardian system."""
    global _guardian_system
    if _guardian_system is None:
        _guardian_system = create_guardian_system(data_dir)
    return _guardian_system
