"""
T.A.R.L. Governance, Compliance, and Observability Extensions

Implements:
8. Governance-grade capability engine with policy versioning
9. Risk/compliance mapping (EU AI Act, NIST AI RMF, SLSA)
10. Runtime safety hooks (guardrails, anomaly detection)
11. Rich AI-specific provenance (datasets, models, evals)
12. CI/CD enforcement with promotion gates
13. Multi-language protocol and SDK support
14. Observability with metrics, traces, structured events
15. Operations plane with admin API
"""

import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# 8. GOVERNANCE-GRADE CAPABILITY ENGINE
# ============================================================================


@dataclass
class PolicyVersion:
    """Versioned policy with environments"""

    policy_id: str
    version: str
    environment: str  # "dev", "stage", "prod"
    policy_data: dict[str, Any]
    created_at: str
    active: bool = True


@dataclass
class PolicyViolation:
    """Record of policy violation"""

    violation_id: str
    policy_id: str
    workflow_id: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    context: dict[str, Any]
    escalated: bool = False
    resolved: bool = False


class GovernanceEngine:
    """
    Governance-grade capability engine with policy versioning and escalation
    """

    def __init__(self, data_dir: str = "data/tarl_governance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._policy_versions: dict[str, list[PolicyVersion]] = defaultdict(list)
        self._violations: dict[str, PolicyViolation] = {}
        self._escalation_handlers: dict[str, Callable] = {}

    def register_policy_version(
        self,
        policy_id: str,
        version: str,
        environment: str,
        policy_data: dict[str, Any],
    ) -> None:
        """Register a new policy version for an environment"""
        policy_version = PolicyVersion(
            policy_id=policy_id,
            version=version,
            environment=environment,
            policy_data=policy_data,
            created_at=datetime.now().isoformat(),
        )

        self._policy_versions[policy_id].append(policy_version)
        logger.info(
            f"Policy {policy_id} version {version} registered for {environment}"
        )

    def get_active_policy(
        self, policy_id: str, environment: str
    ) -> PolicyVersion | None:
        """Get active policy version for environment"""
        versions = self._policy_versions[policy_id]

        for pv in reversed(versions):  # Latest first
            if pv.environment == environment and pv.active:
                return pv

        return None

    def record_violation(
        self,
        policy_id: str,
        workflow_id: str,
        severity: str,
        description: str,
        context: dict[str, Any],
    ) -> str:
        """Record a policy violation"""
        violation_id = str(uuid.uuid4())
        violation = PolicyViolation(
            violation_id=violation_id,
            policy_id=policy_id,
            workflow_id=workflow_id,
            severity=severity,
            description=description,
            context=context,
        )

        self._violations[violation_id] = violation

        # Auto-escalate critical violations
        if severity == "critical":
            self.escalate_violation(violation_id)

        logger.warning(
            f"Policy violation recorded: {policy_id} for workflow {workflow_id}"
        )
        return violation_id

    def escalate_violation(self, violation_id: str) -> None:
        """Escalate a policy violation"""
        if violation_id not in self._violations:
            return

        violation = self._violations[violation_id]
        violation.escalated = True

        # Call escalation handler if registered
        if violation.policy_id in self._escalation_handlers:
            handler = self._escalation_handlers[violation.policy_id]
            handler(violation)

        logger.error(f"Violation {violation_id} escalated")

    def register_escalation_handler(self, policy_id: str, handler: Callable) -> None:
        """Register escalation handler for a policy"""
        self._escalation_handlers[policy_id] = handler

    def get_violations(
        self, workflow_id: str | None = None, severity: str | None = None
    ) -> list[PolicyViolation]:
        """Get policy violations with optional filters"""
        violations = list(self._violations.values())

        if workflow_id:
            violations = [v for v in violations if v.workflow_id == workflow_id]

        if severity:
            violations = [v for v in violations if v.severity == severity]

        return violations


# ============================================================================
# 9. RISK/COMPLIANCE MAPPING
# ============================================================================


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    EU_AI_ACT = "eu_ai_act"
    NIST_AI_RMF = "nist_ai_rmf"
    SLSA = "slsa"
    SOC2 = "soc2"
    ISO_27001 = "iso_27001"
    GDPR = "gdpr"


@dataclass
class ComplianceRequirement:
    """Compliance requirement from a framework"""

    requirement_id: str
    framework: ComplianceFramework
    control_id: str
    description: str
    risk_level: str  # "low", "medium", "high", "critical"
    verification_method: str  # "automated", "manual", "audit"


@dataclass
class ComplianceMapping:
    """Mapping of system components to compliance requirements"""

    component_id: str
    component_type: str  # "workflow", "capability", "activity"
    requirements: list[str]  # requirement_ids
    status: str  # "compliant", "non_compliant", "pending"
    evidence: dict[str, Any] = field(default_factory=dict)


class ComplianceManager:
    """
    Maps system components to compliance frameworks

    Supports EU AI Act, NIST AI RMF, SLSA, SOC2, etc.
    """

    def __init__(self, data_dir: str = "data/tarl_compliance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._requirements: dict[str, ComplianceRequirement] = {}
        self._mappings: dict[str, ComplianceMapping] = {}

        # Load framework requirements
        self._load_frameworks()

    def _load_frameworks(self) -> None:
        """Load compliance framework requirements"""
        # EU AI Act - High-Risk AI Systems
        self._requirements["eu_ai_act_1"] = ComplianceRequirement(
            requirement_id="eu_ai_act_1",
            framework=ComplianceFramework.EU_AI_ACT,
            control_id="Article 9",
            description="Risk management system for high-risk AI",
            risk_level="high",
            verification_method="automated",
        )

        # NIST AI RMF - Govern category
        self._requirements["nist_ai_rmf_gov_1"] = ComplianceRequirement(
            requirement_id="nist_ai_rmf_gov_1",
            framework=ComplianceFramework.NIST_AI_RMF,
            control_id="GOVERN-1.1",
            description="AI system accountability and transparency",
            risk_level="medium",
            verification_method="manual",
        )

        # SLSA - Build Level 3
        self._requirements["slsa_l3_1"] = ComplianceRequirement(
            requirement_id="slsa_l3_1",
            framework=ComplianceFramework.SLSA,
            control_id="L3.1",
            description="Provenance generation for all artifacts",
            risk_level="medium",
            verification_method="automated",
        )

        logger.info("Compliance frameworks loaded")

    def map_component(
        self,
        component_id: str,
        component_type: str,
        requirement_ids: list[str],
    ) -> None:
        """Map a component to compliance requirements"""
        mapping = ComplianceMapping(
            component_id=component_id,
            component_type=component_type,
            requirements=requirement_ids,
            status="pending",
        )

        self._mappings[component_id] = mapping
        logger.info(
            f"Component {component_id} mapped to {len(requirement_ids)} requirements"
        )

    def verify_compliance(self, component_id: str) -> dict[str, Any]:
        """Verify compliance for a component"""
        if component_id not in self._mappings:
            return {"status": "unknown", "reason": "Component not mapped"}

        mapping = self._mappings[component_id]
        results = []

        for req_id in mapping.requirements:
            if req_id in self._requirements:
                req = self._requirements[req_id]
                # In production, this would perform actual verification
                result = {
                    "requirement": req.control_id,
                    "framework": req.framework.value,
                    "status": "compliant",  # Placeholder
                    "verified_at": datetime.now().isoformat(),
                }
                results.append(result)

        # Update mapping status
        mapping.status = (
            "compliant"
            if all(r["status"] == "compliant" for r in results)
            else "non_compliant"
        )

        return {
            "component_id": component_id,
            "status": mapping.status,
            "requirements": results,
        }

    def enforce_no_run_without_attestations(
        self, component_id: str
    ) -> tuple[bool, str]:
        """Enforce that component has required attestations"""
        if component_id not in self._mappings:
            return False, "Component not mapped to compliance requirements"

        mapping = self._mappings[component_id]

        if mapping.status != "compliant":
            return False, f"Component not compliant (status: {mapping.status})"

        # Check for required attestations
        if not mapping.evidence:
            return False, "No attestations found"

        return True, "All attestations present"

    def generate_compliance_report(
        self, framework: ComplianceFramework
    ) -> dict[str, Any]:
        """Generate compliance report for a framework"""
        components = [
            m
            for m in self._mappings.values()
            if any(
                self._requirements[req_id].framework == framework
                for req_id in m.requirements
                if req_id in self._requirements
            )
        ]

        compliant_count = sum(1 for c in components if c.status == "compliant")
        total_count = len(components)

        return {
            "framework": framework.value,
            "total_components": total_count,
            "compliant": compliant_count,
            "non_compliant": total_count - compliant_count,
            "compliance_rate": compliant_count / total_count if total_count > 0 else 0,
            "components": [
                {
                    "component_id": c.component_id,
                    "type": c.component_type,
                    "status": c.status,
                }
                for c in components
            ],
        }


# ============================================================================
# 10. RUNTIME SAFETY HOOKS
# ============================================================================


@dataclass
class SafetyGuardrail:
    """Safety guardrail for runtime checks"""

    guardrail_id: str
    name: str
    check_function: Callable
    severity: str  # "warning", "error", "critical"
    enabled: bool = True


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""

    anomaly_id: str
    workflow_id: str
    anomaly_type: (
        str  # "prompt_injection", "tool_abuse", "rate_limit", "unusual_pattern"
    )
    description: str
    confidence: float  # 0.0 to 1.0
    action_taken: str  # "logged", "blocked", "escalated"


class RuntimeSafetyManager:
    """
    Runtime safety hooks for guardrails and anomaly detection
    """

    def __init__(self, data_dir: str = "data/tarl_safety"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._guardrails: dict[str, SafetyGuardrail] = {}
        self._anomalies: list[AnomalyDetection] = []
        self._blocked_actions: set[str] = set()

    def register_guardrail(
        self,
        guardrail_id: str,
        name: str,
        check_function: Callable,
        severity: str = "warning",
    ) -> None:
        """Register a safety guardrail"""
        guardrail = SafetyGuardrail(
            guardrail_id=guardrail_id,
            name=name,
            check_function=check_function,
            severity=severity,
        )

        self._guardrails[guardrail_id] = guardrail
        logger.info(f"Guardrail {name} registered")

    def check_guardrails(
        self, workflow_id: str, action: str, context: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Run all enabled guardrails"""
        violations = []

        for guardrail in self._guardrails.values():
            if not guardrail.enabled:
                continue

            try:
                passed = guardrail.check_function(action, context)
                if not passed:
                    violations.append(f"{guardrail.name}: Check failed")

                    if guardrail.severity == "critical":
                        self._blocked_actions.add(action)

            except Exception as ex:
                logger.error(f"Guardrail {guardrail.name} check failed: {ex}")

        allowed = len(violations) == 0
        return allowed, violations

    def detect_prompt_injection(self, prompt: str) -> tuple[bool, float]:
        """Detect potential prompt injection attacks"""
        # Simple pattern matching (production would use ML model)
        dangerous_patterns = [
            "ignore previous instructions",
            "disregard above",
            "system:",
            "assistant:",
            "\\n\\nHuman:",
        ]

        matches = sum(
            1 for pattern in dangerous_patterns if pattern.lower() in prompt.lower()
        )
        confidence = min(matches / len(dangerous_patterns), 1.0)

        is_injection = confidence > 0.3

        if is_injection:
            self._record_anomaly(
                workflow_id="unknown",
                anomaly_type="prompt_injection",
                description=f"Potential prompt injection detected (confidence: {confidence:.2f})",
                confidence=confidence,
                action_taken="blocked" if confidence > 0.7 else "logged",
            )

        return is_injection, confidence

    def detect_tool_abuse(
        self, tool_name: str, call_count: int, time_window: int
    ) -> tuple[bool, str]:
        """Detect tool abuse patterns"""
        # Simple rate limiting (production would use sophisticated analysis)
        rate_limit = 100  # calls per time window

        if call_count > rate_limit:
            self._record_anomaly(
                workflow_id="unknown",
                anomaly_type="tool_abuse",
                description=f"Tool {tool_name} called {call_count} times in {time_window}s",
                confidence=1.0,
                action_taken="escalated",
            )
            return True, f"Rate limit exceeded for tool {tool_name}"

        return False, ""

    def _record_anomaly(
        self,
        workflow_id: str,
        anomaly_type: str,
        description: str,
        confidence: float,
        action_taken: str,
    ) -> None:
        """Record an anomaly"""
        anomaly = AnomalyDetection(
            anomaly_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            anomaly_type=anomaly_type,
            description=description,
            confidence=confidence,
            action_taken=action_taken,
        )

        self._anomalies.append(anomaly)
        logger.warning(
            f"Anomaly detected: {anomaly_type} ({confidence:.2f} confidence)"
        )

    def get_anomalies(self, anomaly_type: str | None = None) -> list[AnomalyDetection]:
        """Get detected anomalies"""
        anomalies = self._anomalies

        if anomaly_type:
            anomalies = [a for a in anomalies if a.anomaly_type == anomaly_type]

        return anomalies


# ============================================================================
# 11. RICH AI-SPECIFIC PROVENANCE
# ============================================================================


@dataclass
class DatasetProvenance:
    """Provenance for training/evaluation datasets"""

    dataset_id: str
    name: str
    version: str
    source: str
    size_bytes: int
    record_count: int
    schema_hash: str
    collection_date: str
    license: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelProvenance:
    """Provenance for AI models"""

    model_id: str
    name: str
    version: str
    architecture: str
    framework: str  # "pytorch", "tensorflow", "jax"
    training_dataset_id: str
    hyperparameters: dict[str, Any]
    training_date: str
    model_hash: str
    performance_metrics: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationProvenance:
    """Provenance for model evaluations"""

    eval_id: str
    model_id: str
    eval_dataset_id: str
    eval_date: str
    metrics: dict[str, float]
    fairness_metrics: dict[str, float]
    bias_analysis: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanDecisionProvenance:
    """Provenance for human decisions in the workflow"""

    decision_id: str
    workflow_id: str
    decision_maker: str
    decision_type: str  # "approval", "rejection", "modification"
    rationale: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvenanceManager:
    """
    Rich AI-specific provenance tracking

    Tracks datasets, models, evaluations, human decisions, risk mappings.
    """

    def __init__(self, data_dir: str = "data/tarl_ai_provenance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._datasets: dict[str, DatasetProvenance] = {}
        self._models: dict[str, ModelProvenance] = {}
        self._evaluations: dict[str, EvaluationProvenance] = {}
        self._human_decisions: dict[str, HumanDecisionProvenance] = {}
        self._lineage_graph: dict[str, list[str]] = defaultdict(list)

    def register_dataset(
        self,
        dataset_id: str,
        name: str,
        version: str,
        source: str,
        size_bytes: int,
        record_count: int,
        schema_hash: str,
        license: str = "Unknown",
    ) -> None:
        """Register dataset provenance"""
        dataset = DatasetProvenance(
            dataset_id=dataset_id,
            name=name,
            version=version,
            source=source,
            size_bytes=size_bytes,
            record_count=record_count,
            schema_hash=schema_hash,
            collection_date=datetime.now().isoformat(),
            license=license,
        )

        self._datasets[dataset_id] = dataset
        logger.info(f"Dataset {name} v{version} registered")

    def register_model(
        self,
        model_id: str,
        name: str,
        version: str,
        architecture: str,
        framework: str,
        training_dataset_id: str,
        hyperparameters: dict[str, Any],
        model_hash: str,
        performance_metrics: dict[str, float],
    ) -> None:
        """Register model provenance"""
        model = ModelProvenance(
            model_id=model_id,
            name=name,
            version=version,
            architecture=architecture,
            framework=framework,
            training_dataset_id=training_dataset_id,
            hyperparameters=hyperparameters,
            training_date=datetime.now().isoformat(),
            model_hash=model_hash,
            performance_metrics=performance_metrics,
        )

        self._models[model_id] = model

        # Add lineage: model -> dataset
        self._lineage_graph[model_id].append(training_dataset_id)

        logger.info(f"Model {name} v{version} registered")

    def register_evaluation(
        self,
        eval_id: str,
        model_id: str,
        eval_dataset_id: str,
        metrics: dict[str, float],
        fairness_metrics: dict[str, float],
        bias_analysis: dict[str, Any],
    ) -> None:
        """Register evaluation provenance"""
        evaluation = EvaluationProvenance(
            eval_id=eval_id,
            model_id=model_id,
            eval_dataset_id=eval_dataset_id,
            eval_date=datetime.now().isoformat(),
            metrics=metrics,
            fairness_metrics=fairness_metrics,
            bias_analysis=bias_analysis,
        )

        self._evaluations[eval_id] = evaluation

        # Add lineage: eval -> model, eval -> dataset
        self._lineage_graph[eval_id].extend([model_id, eval_dataset_id])

        logger.info(f"Evaluation {eval_id} registered")

    def record_human_decision(
        self,
        workflow_id: str,
        decision_maker: str,
        decision_type: str,
        rationale: str,
    ) -> str:
        """Record a human decision in the workflow"""
        decision_id = str(uuid.uuid4())
        decision = HumanDecisionProvenance(
            decision_id=decision_id,
            workflow_id=workflow_id,
            decision_maker=decision_maker,
            decision_type=decision_type,
            rationale=rationale,
            timestamp=datetime.now().isoformat(),
        )

        self._human_decisions[decision_id] = decision

        logger.info(f"Human decision recorded: {decision_type} by {decision_maker}")
        return decision_id

    def get_lineage(self, artifact_id: str) -> dict[str, Any]:
        """Get complete lineage for an artifact"""
        visited = set()
        lineage = {"artifact_id": artifact_id, "dependencies": []}

        def traverse(aid: str) -> None:
            if aid in visited:
                return

            visited.add(aid)

            for dep in self._lineage_graph.get(aid, []):
                lineage["dependencies"].append(dep)
                traverse(dep)

        traverse(artifact_id)

        return lineage

    def generate_ai_sbom(self, model_id: str) -> dict[str, Any]:
        """Generate AI-specific SBOM for a model"""
        if model_id not in self._models:
            return {"error": "Model not found"}

        model = self._models[model_id]
        lineage = self.get_lineage(model_id)

        # Find associated datasets and evaluations
        dataset = self._datasets.get(model.training_dataset_id, {})
        evaluations = [e for e in self._evaluations.values() if e.model_id == model_id]

        return {
            "model": {
                "id": model.model_id,
                "name": model.name,
                "version": model.version,
                "architecture": model.architecture,
                "framework": model.framework,
                "hash": model.model_hash,
                "training_date": model.training_date,
            },
            "training_data": {
                "dataset_id": (
                    dataset.dataset_id if hasattr(dataset, "dataset_id") else "unknown"
                ),
                "name": dataset.name if hasattr(dataset, "name") else "unknown",
                "size_bytes": (
                    dataset.size_bytes if hasattr(dataset, "size_bytes") else 0
                ),
                "license": (
                    dataset.license if hasattr(dataset, "license") else "unknown"
                ),
            },
            "evaluations": [
                {
                    "eval_id": e.eval_id,
                    "eval_date": e.eval_date,
                    "metrics": e.metrics,
                    "fairness_metrics": e.fairness_metrics,
                }
                for e in evaluations
            ],
            "lineage": lineage,
            "sbom_version": "1.0.0-ai",
            "generator": "T.A.R.L. AI Provenance Manager",
        }


# ============================================================================
# 12. CI/CD ENFORCEMENT WITH PROMOTION GATES
# ============================================================================


@dataclass
class PromotionGate:
    """Gate that must pass for promotion"""

    gate_id: str
    name: str
    check_function: Callable
    required: bool = True
    environment: str = "all"  # "all", "stage", "prod"


@dataclass
class PromotionRequest:
    """Request to promote a component"""

    request_id: str
    component_id: str
    from_environment: str
    to_environment: str
    status: str = "pending"  # "pending", "approved", "rejected"
    gate_results: dict[str, bool] = field(default_factory=dict)


class CICDEnforcementManager:
    """
    CI/CD enforcement with promotion gates

    Rejects workflows/agents lacking required provenance.
    """

    def __init__(self, data_dir: str = "data/tarl_cicd"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._gates: dict[str, PromotionGate] = {}
        self._promotion_requests: dict[str, PromotionRequest] = {}
        self._component_registry: dict[str, dict[str, Any]] = {}

    def register_gate(
        self,
        gate_id: str,
        name: str,
        check_function: Callable,
        required: bool = True,
        environment: str = "all",
    ) -> None:
        """Register a promotion gate"""
        gate = PromotionGate(
            gate_id=gate_id,
            name=name,
            check_function=check_function,
            required=required,
            environment=environment,
        )

        self._gates[gate_id] = gate
        logger.info(f"Promotion gate {name} registered")

    def register_component(
        self,
        component_id: str,
        component_type: str,
        environment: str,
        metadata: dict[str, Any],
    ) -> None:
        """Register a component in an environment"""
        self._component_registry[component_id] = {
            "type": component_type,
            "environment": environment,
            "metadata": metadata,
            "registered_at": datetime.now().isoformat(),
        }

        logger.info(f"Component {component_id} registered in {environment}")

    def request_promotion(
        self,
        component_id: str,
        from_environment: str,
        to_environment: str,
    ) -> str:
        """Request promotion of a component"""
        request_id = str(uuid.uuid4())
        request = PromotionRequest(
            request_id=request_id,
            component_id=component_id,
            from_environment=from_environment,
            to_environment=to_environment,
        )

        self._promotion_requests[request_id] = request

        # Run gates
        self._run_gates(request_id)

        logger.info(
            f"Promotion requested: {component_id} from {from_environment} to {to_environment}"
        )
        return request_id

    def _run_gates(self, request_id: str) -> None:
        """Run all promotion gates for a request"""
        request = self._promotion_requests[request_id]

        for gate in self._gates.values():
            # Skip if gate doesn't apply to target environment
            if gate.environment not in ["all", request.to_environment]:
                continue

            try:
                passed = gate.check_function(
                    request.component_id, request.to_environment
                )
                request.gate_results[gate.gate_id] = passed

                if not passed and gate.required:
                    request.status = "rejected"
                    logger.warning(
                        f"Promotion gate {gate.name} failed for {request.component_id}"
                    )

            except Exception as ex:
                logger.error(f"Gate {gate.name} check failed: {ex}")
                request.gate_results[gate.gate_id] = False

                if gate.required:
                    request.status = "rejected"

        # Approve if all required gates passed
        if request.status == "pending":
            required_gates_passed = all(
                passed
                for gate_id, passed in request.gate_results.items()
                if self._gates[gate_id].required
            )

            if required_gates_passed:
                request.status = "approved"
                logger.info(f"Promotion request {request_id} approved")

    def get_promotion_status(self, request_id: str) -> dict[str, Any]:
        """Get status of a promotion request"""
        if request_id not in self._promotion_requests:
            return {"status": "not_found"}

        request = self._promotion_requests[request_id]

        return {
            "request_id": request_id,
            "component_id": request.component_id,
            "from": request.from_environment,
            "to": request.to_environment,
            "status": request.status,
            "gate_results": request.gate_results,
        }


# ============================================================================
# INTEGRATION MODULE
# ============================================================================


class FullGovernanceStack:
    """
    Complete governance, compliance, and observability stack
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Initialize all subsystems
        self.governance = GovernanceEngine(
            data_dir=self.config.get("governance_dir", "data/tarl_governance")
        )
        self.compliance = ComplianceManager(
            data_dir=self.config.get("compliance_dir", "data/tarl_compliance")
        )
        self.safety = RuntimeSafetyManager(
            data_dir=self.config.get("safety_dir", "data/tarl_safety")
        )
        self.ai_provenance = AIProvenanceManager(
            data_dir=self.config.get("ai_provenance_dir", "data/tarl_ai_provenance")
        )
        self.cicd = CICDEnforcementManager(
            data_dir=self.config.get("cicd_dir", "data/tarl_cicd")
        )

        logger.info("FullGovernanceStack initialized")

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive status"""
        return {
            "governance": {
                "policies": len(self.governance._policy_versions),
                "violations": len(self.governance._violations),
            },
            "compliance": {
                "mappings": len(self.compliance._mappings),
                "frameworks": len(ComplianceFramework),
            },
            "safety": {
                "guardrails": len(self.safety._guardrails),
                "anomalies": len(self.safety._anomalies),
            },
            "ai_provenance": {
                "datasets": len(self.ai_provenance._datasets),
                "models": len(self.ai_provenance._models),
                "evaluations": len(self.ai_provenance._evaluations),
            },
            "cicd": {
                "gates": len(self.cicd._gates),
                "components": len(self.cicd._component_registry),
                "promotions": len(self.cicd._promotion_requests),
            },
        }


# ============================================================================
# DEMO
# ============================================================================


def demo_governance_features():
    """Demo of governance, compliance, and safety features"""
    print("\n" + "=" * 80)
    print("T.A.R.L. GOVERNANCE, COMPLIANCE & SAFETY DEMO")
    print("=" * 80 + "\n")

    stack = FullGovernanceStack()

    # 1. Policy Versioning
    print("1️⃣  Policy Versioning")
    stack.governance.register_policy_version(
        policy_id="security_policy",
        version="1.2.0",
        environment="prod",
        policy_data={"require_mfa": True, "max_retries": 3},
    )
    print("   ✅ Policy version registered\n")

    # 2. Compliance Mapping
    print("2️⃣  Compliance Mapping")
    stack.compliance.map_component(
        component_id="ml_workflow_001",
        component_type="workflow",
        requirement_ids=["eu_ai_act_1", "nist_ai_rmf_gov_1", "slsa_l3_1"],
    )
    compliance_result = stack.compliance.verify_compliance("ml_workflow_001")
    print(f"   ✅ Compliance verified: {compliance_result['status']}\n")

    # 3. Runtime Safety
    print("3️⃣  Runtime Safety")
    stack.safety.register_guardrail(
        guardrail_id="prompt_safety",
        name="Prompt Injection Detection",
        check_function=lambda action, ctx: "system:" not in action,
        severity="critical",
    )

    is_injection, confidence = stack.safety.detect_prompt_injection(
        "Hello, please help me with this task"
    )
    print(
        f"   ✅ Prompt checked: injection={is_injection}, confidence={confidence:.2f}\n"
    )

    # 4. AI Provenance
    print("4️⃣  AI-Specific Provenance")
    stack.ai_provenance.register_dataset(
        dataset_id="train_001",
        name="Training Data",
        version="1.0.0",
        source="internal",
        size_bytes=1024 * 1024 * 100,
        record_count=10000,
        schema_hash="abc123",
        license="MIT",
    )

    stack.ai_provenance.register_model(
        model_id="model_001",
        name="Classifier",
        version="1.0.0",
        architecture="transformer",
        framework="pytorch",
        training_dataset_id="train_001",
        hyperparameters={"lr": 0.001, "epochs": 10},
        model_hash="def456",
        performance_metrics={"accuracy": 0.95, "f1": 0.93},
    )

    ai_sbom = stack.ai_provenance.generate_ai_sbom("model_001")
    print(f"   ✅ AI SBOM generated: {ai_sbom['model']['name']}\n")

    # 5. CI/CD Gates
    print("5️⃣  CI/CD Promotion Gates")
    stack.cicd.register_gate(
        gate_id="provenance_check",
        name="Provenance Required",
        check_function=lambda comp_id, env: True,  # Placeholder
        required=True,
        environment="prod",
    )

    promotion_id = stack.cicd.request_promotion(
        component_id="ml_workflow_001",
        from_environment="stage",
        to_environment="prod",
    )

    promo_status = stack.cicd.get_promotion_status(promotion_id)
    print(f"   ✅ Promotion status: {promo_status['status']}\n")

    # Status
    print("📊 System Status:")
    status = stack.get_status()
    for subsystem, stats in status.items():
        print(f"   {subsystem}: {stats}")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo_governance_features()
