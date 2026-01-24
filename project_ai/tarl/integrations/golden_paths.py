"""
T.A.R.L. Golden Path Recipes

Opinionated, production-ready configuration patterns for common T.A.R.L. use cases.
These recipes provide the "golden path" - best practices that work out of the box.
"""

from typing import Dict, Any, Callable, List
from dataclasses import dataclass, field

from project_ai.tarl.integrations import (
    ExtendedTarlStackBox,
    FullGovernanceStack,
    Capability,
    Policy,
    ResourceQuota,
    TaskQueuePriority,
    ComplianceFramework,
)


@dataclass
class GoldenPathConfig:
    """Base configuration for golden path recipes"""
    name: str
    description: str
    stack_config: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[Capability] = field(default_factory=list)
    policies: List[Policy] = field(default_factory=list)
    setup_steps: List[Callable] = field(default_factory=list)


class GoldenPathRecipes:
    """Collection of opinionated golden path recipes for T.A.R.L."""

    @staticmethod
    def agent_graph_with_governance() -> Dict[str, Any]:
        """
        Golden Path Recipe #1: Agent Graph + HITL + Governance + Provenance
        
        Use case: Multi-agent system with human oversight, compliance tracking,
        and full provenance/audit trail.
        
        Returns:
            dict: Complete configured system ready to use
        """
        # Initialize both stacks
        stack = ExtendedTarlStackBox(config={
            "workers": 4,
            "enable_metrics": True,
            "log_level": "INFO"
        })
        
        governance = FullGovernanceStack()
        
        # Define capabilities for agent actions
        capabilities = [
            Capability(
                name="Agent.Query",
                resource="data",
                constraints={"pii_protected": True, "audit_required": True}
            ),
            Capability(
                name="Agent.Execute",
                resource="workflow",
                constraints={"approval_required": True}
            ),
            Capability(
                name="Agent.Deploy",
                resource="system",
                constraints={"environment": "production", "signed": True}
            )
        ]
        
        for cap in capabilities:
            stack.capabilities.register_capability(cap)
        
        # Define policies
        policies = [
            Policy(
                name="RequireApprovalForExecution",
                capability_name="Agent.Execute",
                constraints={"approval_required": True},
                enforcement_level="strict"
            ),
            Policy(
                name="ProdDeployRequiresSignature",
                capability_name="Agent.Deploy",
                constraints={"environment": "production", "signed": True},
                enforcement_level="strict"
            )
        ]
        
        for policy in policies:
            stack.capabilities.register_policy(policy)
        
        # Configure compliance mapping
        governance.compliance.map_component(
            "agent_graph",
            "workflow",
            ["eu_ai_act_1", "nist_ai_rmf_gov_1", "slsa_l3_1"]
        )
        
        # Register safety guardrails
        def check_pii_protection(action, context):
            """Ensure PII is protected"""
            return not context.get("contains_pii", False)
        
        governance.safety.register_guardrail(
            "pii_protection",
            "PII Protection Check",
            check_pii_protection,
            severity="critical"
        )
        
        # Register provenance for agents
        governance.ai_provenance.register_model(
            "agent_coordinator",
            "Multi-Agent Coordinator",
            "1.0.0",
            "rule_based",
            "python",
            training_dataset_id=None,
            hyperparameters={},
            model_hash="coord_v1",
            performance_metrics={}
        )
        
        return {
            "stack": stack,
            "governance": governance,
            "description": "Agent graph with full governance",
            "usage": """
# Define agent workflows
def query_agent(vm, context):
    # Check capability before querying
    allowed, reason = stack.capabilities.check_capability(
        "Agent.Query", 
        {"pii_protected": True, "audit_required": True}
    )
    if not allowed:
        raise PermissionError(reason)
    
    # Perform query
    return {"data": "query_result"}

def execute_agent(vm, context):
    # Request human approval
    request_id = stack.hitl.request_approval(
        context["workflow_id"],
        "Execute agent action",
        required_approvers=["supervisor"],
        context=context
    )
    
    # Wait for approval (in real system, would be async)
    # stack.hitl.approve(request_id, "supervisor")
    
    # Check if approved
    if stack.hitl.is_approved(request_id):
        return {"executed": True}
    else:
        raise PermissionError("Approval required")

# Create agent graph workflows
stack.create_workflow("query_agent", query_agent, required_caps={"Agent.Query"})
stack.create_workflow("execute_agent", execute_agent, required_caps={"Agent.Execute"})

# Execute with provenance
result = stack.execute_with_provenance("query_agent")

# Generate SBOM for audit
sbom = stack.provenance.generate_sbom("query_agent")
"""
        }

    @staticmethod
    def simple_deterministic_workflow() -> Dict[str, Any]:
        """
        Golden Path Recipe #2: Simple Deterministic Workflow
        
        Use case: Basic deterministic workflow with record/replay for debugging.
        
        Returns:
            dict: Minimal configured system for deterministic execution
        """
        from project_ai.tarl.integrations import TarlStackBox
        
        stack = TarlStackBox(config={
            "vm_data_dir": "data/tarl_vm",
            "enable_recording": True
        })
        
        # Register basic capability
        cap = Capability(
            name="Workflow.Execute",
            resource="compute",
            constraints={}
        )
        stack.capabilities.register_capability(cap)
        
        return {
            "stack": stack,
            "description": "Simple deterministic workflow with replay",
            "usage": """
# Define workflow
def data_processing(vm, context):
    # Record external API call
    stack.recorder.record_external_call(
        "data_processing",
        "api",
        {"endpoint": "/data"},
        {"records": [1, 2, 3]}
    )
    
    # Process data
    result = {"processed": len([1, 2, 3])}
    return result

# Create and execute
stack.create_workflow("data_processing", data_processing, required_caps={"Workflow.Execute"})
result = stack.vm.execute_workflow("data_processing", {})

# Save recording for replay
stack.recorder.save_recording("data/recordings/data_processing.json")

# Later: replay for debugging
stack.recorder.load_recording("data/recordings/data_processing.json")
replayed_result = stack.recorder.replay_workflow("data_processing")
"""
        }

    @staticmethod
    def multi_tenant_deployment() -> Dict[str, Any]:
        """
        Golden Path Recipe #3: Multi-Tenant Deployment
        
        Use case: SaaS platform with tenant isolation, quotas, and fair scheduling.
        
        Returns:
            dict: Multi-tenant configured system with quotas
        """
        stack = ExtendedTarlStackBox(config={
            "workers": 8,
            "enable_multi_tenant": True,
            "fair_scheduling": True
        })
        
        # Define tenant quotas (different tiers)
        tier_quotas = {
            "free": ResourceQuota(
                max_workflows=10,
                max_concurrent_executions=2,
                max_queue_depth=20,
                max_storage_mb=100,
                rate_limit_per_minute=100
            ),
            "pro": ResourceQuota(
                max_workflows=100,
                max_concurrent_executions=10,
                max_queue_depth=200,
                max_storage_mb=1000,
                rate_limit_per_minute=1000
            ),
            "enterprise": ResourceQuota(
                max_workflows=1000,
                max_concurrent_executions=50,
                max_queue_depth=2000,
                max_storage_mb=10000,
                rate_limit_per_minute=10000
            )
        }
        
        return {
            "stack": stack,
            "tier_quotas": tier_quotas,
            "description": "Multi-tenant deployment with tiered quotas",
            "usage": """
# Create tenant namespaces
for tenant_id, tier in [("customer_1", "pro"), ("customer_2", "free")]:
    namespace = stack.multi_tenant.create_namespace(
        tenant_id,
        f"Customer {tenant_id}",
        tier_quotas[tier],
        isolation_level="strict"
    )

# Tenant executes workflow
def tenant_workflow(vm, context):
    tenant_id = context["tenant_id"]
    
    # Consume quota
    stack.multi_tenant.consume_quota(tenant_id, "workflows", amount=1)
    
    try:
        # Execute business logic
        result = {"success": True}
        return result
    finally:
        # Release quota on completion
        stack.multi_tenant.release_quota(tenant_id, "workflows", amount=1)

# Execute per-tenant
stack.create_workflow("tenant_workflow", tenant_workflow)
result = stack.vm.execute_workflow("tenant_workflow", {"tenant_id": "customer_1"})

# Monitor tenant usage
usage = stack.multi_tenant.get_usage("customer_1")
print(f"Customer 1 usage: {usage}")
"""
        }

    @staticmethod
    def compliance_driven_workflow() -> Dict[str, Any]:
        """
        Golden Path Recipe #4: Compliance-Driven Workflow
        
        Use case: Healthcare, finance, or regulated industry workflow with
        comprehensive compliance checking and attestation requirements.
        
        Returns:
            dict: Compliance-configured system with enforcement
        """
        stack = ExtendedTarlStackBox(config={
            "workers": 4,
            "enable_compliance": True,
            "audit_logging": True
        })
        
        governance = FullGovernanceStack()
        
        # Map to multiple compliance frameworks
        compliance_mappings = {
            "patient_data_processor": ["eu_ai_act_1", "gdpr_art_1", "hipaa_1"],
            "financial_model": ["slsa_l3_1", "soc2_cc1_1", "iso27001_a_1"],
            "ai_decision_system": ["nist_ai_rmf_gov_1", "eu_ai_act_1"]
        }
        
        for component, requirements in compliance_mappings.items():
            governance.compliance.map_component(
                component, "workflow", requirements
            )
        
        # Register CI/CD gates for compliance
        def check_data_provenance(component_id, environment):
            """Ensure data provenance is documented"""
            sbom = governance.ai_provenance.generate_ai_sbom(component_id)
            return sbom is not None and "datasets" in sbom
        
        def check_security_scan(component_id, environment):
            """Ensure security scan passed"""
            # In real system, would check scan results
            return True
        
        governance.cicd.register_gate(
            "data_provenance",
            "Data Provenance Required",
            check_data_provenance,
            required=True,
            environment="prod"
        )
        
        governance.cicd.register_gate(
            "security_scan",
            "Security Scan Required",
            check_security_scan,
            required=True,
            environment="prod"
        )
        
        return {
            "stack": stack,
            "governance": governance,
            "compliance_mappings": compliance_mappings,
            "description": "Compliance-driven workflow with attestation requirements",
            "usage": """
# Register component
governance.cicd.register_component(
    "patient_data_processor",
    "workflow",
    "stage",
    metadata={"version": "1.0.0"}
)

# Request promotion to production
request_id = governance.cicd.request_promotion(
    "patient_data_processor",
    from_environment="stage",
    to_environment="prod"
)

# Check promotion status
status = governance.cicd.get_promotion_status(request_id)

if status["status"] == "approved":
    # Verify compliance before execution
    compliance_result = governance.compliance.verify_compliance(
        "patient_data_processor"
    )
    
    # Enforce no-run without attestations
    allowed, reason = governance.compliance.enforce_no_run_without_attestations(
        "patient_data_processor"
    )
    
    if allowed:
        # Execute workflow
        result = stack.vm.execute_workflow("patient_data_processor", {})
    else:
        raise PermissionError(f"Compliance check failed: {reason}")

# Generate compliance report
report = governance.compliance.generate_compliance_report(
    ComplianceFramework.EU_AI_ACT
)
"""
        }

    @staticmethod
    def ai_model_deployment_pipeline() -> Dict[str, Any]:
        """
        Golden Path Recipe #5: AI Model Deployment Pipeline
        
        Use case: Complete ML pipeline from training to production deployment
        with lineage tracking, evaluation, and human approval.
        
        Returns:
            dict: AI/ML configured system with full provenance
        """
        stack = ExtendedTarlStackBox(config={
            "workers": 4,
            "enable_ai_provenance": True
        })
        
        governance = FullGovernanceStack()
        
        # Register dataset
        governance.ai_provenance.register_dataset(
            "training_data_v1",
            "Customer Behavior Dataset",
            "1.0.0",
            "internal_db",
            size_bytes=1024 * 1024 * 500,  # 500MB
            record_count=100000,
            schema_hash="abc123",
            license="proprietary"
        )
        
        # Register model
        governance.ai_provenance.register_model(
            "classifier_v1",
            "Customer Churn Classifier",
            "1.0.0",
            "xgboost",
            "python",
            training_dataset_id="training_data_v1",
            hyperparameters={"max_depth": 6, "learning_rate": 0.1},
            model_hash="def456",
            performance_metrics={"accuracy": 0.89, "f1": 0.87}
        )
        
        # Register evaluation
        governance.ai_provenance.register_evaluation(
            "eval_v1",
            "classifier_v1",
            "training_data_v1",
            metrics={"accuracy": 0.89, "precision": 0.91, "recall": 0.85},
            fairness_metrics={"demographic_parity": 0.92},
            bias_analysis={"gender": "low_bias", "age": "medium_bias"}
        )
        
        # Register safety guardrails
        def check_model_performance(action, context):
            """Ensure model meets minimum performance"""
            accuracy = context.get("accuracy", 0)
            return accuracy >= 0.85
        
        governance.safety.register_guardrail(
            "min_model_performance",
            "Minimum Model Performance",
            check_model_performance,
            severity="critical"
        )
        
        return {
            "stack": stack,
            "governance": governance,
            "description": "AI model deployment pipeline with full lineage",
            "usage": """
# Define deployment workflow
def deploy_model_workflow(vm, context):
    model_id = context["model_id"]
    environment = context["environment"]
    
    # Check guardrails
    allowed, violations = governance.safety.check_guardrails(
        "deploy_model",
        "deploy",
        {"accuracy": 0.89, "environment": environment}
    )
    
    if not allowed:
        raise PermissionError(f"Safety check failed: {violations}")
    
    # Request human approval for production
    if environment == "production":
        request_id = stack.hitl.request_approval(
            context["workflow_id"],
            f"Deploy {model_id} to production",
            required_approvers=["ml_lead", "security_lead"],
            context={"model_id": model_id}
        )
        
        # Wait for approval
        # ... approval process ...
    
    # Record human decision
    decision_id = governance.ai_provenance.record_human_decision(
        context["workflow_id"],
        "ml_lead",
        "deployment_approval",
        f"Approved deployment of {model_id} to {environment}"
    )
    
    # Generate AI-specific SBOM
    ai_sbom = governance.ai_provenance.generate_ai_sbom(model_id)
    
    # Get full lineage
    lineage = governance.ai_provenance.get_lineage(model_id)
    
    return {
        "deployed": True,
        "model_id": model_id,
        "environment": environment,
        "sbom": ai_sbom,
        "lineage": lineage
    }

# Create and execute deployment workflow
stack.create_workflow("deploy_model", deploy_model_workflow)
result = stack.vm.execute_workflow("deploy_model", {
    "model_id": "classifier_v1",
    "environment": "staging"
})

# Promote to production via CI/CD gates
governance.cicd.register_component(
    "classifier_v1",
    "model",
    "staging",
    metadata={"version": "1.0.0"}
)

promotion_id = governance.cicd.request_promotion(
    "classifier_v1",
    from_environment="staging",
    to_environment="production"
)

# Monitor promotion status
status = governance.cicd.get_promotion_status(promotion_id)
"""
        }

    @staticmethod
    def get_all_recipes() -> Dict[str, Dict[str, Any]]:
        """Get all golden path recipes"""
        return {
            "agent_graph_with_governance": GoldenPathRecipes.agent_graph_with_governance(),
            "simple_deterministic_workflow": GoldenPathRecipes.simple_deterministic_workflow(),
            "multi_tenant_deployment": GoldenPathRecipes.multi_tenant_deployment(),
            "compliance_driven_workflow": GoldenPathRecipes.compliance_driven_workflow(),
            "ai_model_deployment_pipeline": GoldenPathRecipes.ai_model_deployment_pipeline()
        }


def print_recipe_guide():
    """Print a guide to all available golden path recipes"""
    print("=" * 80)
    print("T.A.R.L. GOLDEN PATH RECIPES")
    print("=" * 80)
    print()
    print("Opinionated, production-ready patterns for common T.A.R.L. use cases.")
    print()
    
    recipes = [
        ("1", "Agent Graph + HITL + Governance + Provenance",
         "Multi-agent system with human oversight and compliance"),
        ("2", "Simple Deterministic Workflow",
         "Basic deterministic workflow with record/replay"),
        ("3", "Multi-Tenant Deployment",
         "SaaS platform with tenant isolation and quotas"),
        ("4", "Compliance-Driven Workflow",
         "Regulated industry workflow with attestation requirements"),
        ("5", "AI Model Deployment Pipeline",
         "ML pipeline with lineage, evaluation, and approval")
    ]
    
    for num, title, desc in recipes:
        print(f"Recipe #{num}: {title}")
        print(f"   {desc}")
        print()
    
    print("=" * 80)
    print()
    print("Usage:")
    print("    from project_ai.tarl.integrations.golden_paths import GoldenPathRecipes")
    print()
    print("    # Get a specific recipe")
    print("    recipe = GoldenPathRecipes.agent_graph_with_governance()")
    print("    stack = recipe['stack']")
    print("    print(recipe['usage'])")
    print()
    print("    # Get all recipes")
    print("    all_recipes = GoldenPathRecipes.get_all_recipes()")
    print()
    print("=" * 80)


if __name__ == "__main__":
    print_recipe_guide()
