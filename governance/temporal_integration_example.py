#                                           [2026-03-05 09:35]
#                                          Productivity: Active
"""
Temporal Integration Example - Shows how to use audit ledger with Temporal workflows.

This example demonstrates integrating the temporal audit ledger with Temporal.io
workflows and activities to create court-grade audit trails.
"""

from pathlib import Path
from datetime import timedelta
from typing import Any, Dict

# Note: This is an example - actual Temporal imports would be:
# from temporalio import workflow, activity
# from temporalio.client import Client
# from temporalio.worker import Worker

import sys
sys.path.insert(0, str(Path(__file__).parent))

from temporal_audit_ledger import (
    TemporalAuditLedger,
    AuditEventType,
    create_ledger,
)


class AuditedTemporalWorkflow:
    """
    Example Temporal workflow with integrated audit ledger.
    
    This shows how to audit workflow lifecycle events with cryptographic guarantees.
    """
    
    def __init__(self, ledger_path: Path):
        """Initialize workflow with audit ledger."""
        self.ledger = create_ledger(ledger_path)
    
    # @workflow.defn
    class UserOnboardingWorkflow:
        """Example workflow: User onboarding with full audit trail."""
        
        def __init__(self):
            self.ledger = None  # Set by workflow executor
        
        # @workflow.run
        async def run(self, user_data: Dict[str, Any]) -> str:
            """
            Run user onboarding workflow with audit trail.
            
            Args:
                user_data: User data for onboarding
                
            Returns:
                Workflow result
            """
            # Simulated workflow info
            workflow_id = "wf_12345"
            run_id = "run_67890"
            
            # Audit workflow start
            self.ledger.append(
                event_type=AuditEventType.TEMPORAL_WORKFLOW_START,
                actor=f"workflow_{workflow_id}",
                action="start_user_onboarding",
                resource=f"user_{user_data.get('user_id', 'unknown')}",
                metadata={
                    "workflow_id": workflow_id,
                    "run_id": run_id,
                    "user_email": user_data.get("email", ""),
                    "timestamp": "2026-03-05T09:35:00Z",
                },
                request_tsa_timestamp=True,  # Court-grade timestamp
            )
            
            try:
                # Execute activities with auditing
                
                # Activity 1: Validate user data
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_ACTIVITY_START,
                    actor=f"workflow_{workflow_id}",
                    action="start_validate_user",
                    resource=f"activity_validate",
                    metadata={
                        "workflow_id": workflow_id,
                        "activity_id": "act_validate_001",
                    },
                )
                
                # Simulate activity execution
                validation_result = "valid"
                
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_ACTIVITY_COMPLETE,
                    actor=f"workflow_{workflow_id}",
                    action="complete_validate_user",
                    resource=f"activity_validate",
                    metadata={
                        "workflow_id": workflow_id,
                        "activity_id": "act_validate_001",
                        "result": validation_result,
                    },
                )
                
                # Activity 2: Create user account
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_ACTIVITY_START,
                    actor=f"workflow_{workflow_id}",
                    action="start_create_account",
                    resource=f"activity_create_account",
                    metadata={
                        "workflow_id": workflow_id,
                        "activity_id": "act_create_002",
                    },
                )
                
                account_id = "acc_999"
                
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_ACTIVITY_COMPLETE,
                    actor=f"workflow_{workflow_id}",
                    action="complete_create_account",
                    resource=f"activity_create_account",
                    metadata={
                        "workflow_id": workflow_id,
                        "activity_id": "act_create_002",
                        "account_id": account_id,
                        "result": "success",
                    },
                )
                
                # Activity 3: Send welcome email
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_ACTIVITY_START,
                    actor=f"workflow_{workflow_id}",
                    action="start_send_welcome_email",
                    resource=f"activity_send_email",
                    metadata={
                        "workflow_id": workflow_id,
                        "activity_id": "act_email_003",
                    },
                )
                
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_ACTIVITY_COMPLETE,
                    actor=f"workflow_{workflow_id}",
                    action="complete_send_welcome_email",
                    resource=f"activity_send_email",
                    metadata={
                        "workflow_id": workflow_id,
                        "activity_id": "act_email_003",
                        "email_sent_to": user_data.get("email", ""),
                        "result": "success",
                    },
                )
                
                # Audit workflow completion
                self.ledger.append(
                    event_type=AuditEventType.TEMPORAL_WORKFLOW_COMPLETE,
                    actor=f"workflow_{workflow_id}",
                    action="complete_user_onboarding",
                    resource=f"user_{user_data.get('user_id', 'unknown')}",
                    metadata={
                        "workflow_id": workflow_id,
                        "run_id": run_id,
                        "result": "success",
                        "account_id": account_id,
                    },
                    request_tsa_timestamp=True,  # Court-grade timestamp
                )
                
                # Create Merkle checkpoint after workflow completion
                merkle_root = self.ledger.create_merkle_checkpoint()
                
                return f"success:{account_id}"
                
            except Exception as e:
                # Audit workflow failure
                self.ledger.append(
                    event_type=AuditEventType.SYSTEM_ERROR,
                    actor=f"workflow_{workflow_id}",
                    action="workflow_failed",
                    resource=f"user_{user_data.get('user_id', 'unknown')}",
                    metadata={
                        "workflow_id": workflow_id,
                        "run_id": run_id,
                        "error": str(e),
                    },
                    request_tsa_timestamp=True,
                )
                
                raise


class AuditedGovernanceDecision:
    """
    Example: Governance decision with audit trail.
    
    Shows how to audit governance decisions with cryptographic proofs.
    """
    
    def __init__(self, ledger_path: Path):
        """Initialize with audit ledger."""
        self.ledger = create_ledger(ledger_path)
    
    def make_decision(
        self,
        policy_id: str,
        decision: str,
        reason: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Make governance decision with full audit trail.
        
        Args:
            policy_id: ID of policy being evaluated
            decision: Decision made (approved/denied)
            reason: Reason for decision
            context: Additional context
            
        Returns:
            True if decision made successfully
        """
        # Audit the decision
        self.ledger.append(
            event_type=AuditEventType.GOVERNANCE_DECISION,
            actor="governance_system",
            action=f"decision_{decision}",
            resource=f"policy_{policy_id}",
            metadata={
                "policy_id": policy_id,
                "decision": decision,
                "reason": reason,
                "context": context,
            },
            request_tsa_timestamp=True,  # Critical decisions get timestamps
        )
        
        # Create checkpoint after critical decisions
        if decision in ["approved", "denied"]:
            merkle_root = self.ledger.create_merkle_checkpoint()
            
            # Store Merkle root for external verification
            print(f"Decision checkpoint: {merkle_root}")
        
        return True


class AuditedSecurityEvent:
    """
    Example: Security event auditing.
    
    Shows how to audit authentication, authorization, and security events.
    """
    
    def __init__(self, ledger_path: Path):
        """Initialize with audit ledger."""
        self.ledger = create_ledger(ledger_path)
    
    def audit_authentication(
        self,
        user_id: str,
        auth_method: str,
        success: bool,
        ip_address: str,
    ) -> None:
        """Audit authentication attempt."""
        self.ledger.append(
            event_type=AuditEventType.AUTHENTICATION,
            actor=f"user_{user_id}",
            action="login_attempt" if success else "login_failed",
            resource="auth_system",
            metadata={
                "user_id": user_id,
                "auth_method": auth_method,
                "success": success,
                "ip_address": ip_address,
            },
        )
    
    def audit_authorization(
        self,
        user_id: str,
        resource: str,
        permission: str,
        granted: bool,
    ) -> None:
        """Audit authorization decision."""
        self.ledger.append(
            event_type=AuditEventType.AUTHORIZATION,
            actor=f"user_{user_id}",
            action="access_granted" if granted else "access_denied",
            resource=resource,
            metadata={
                "user_id": user_id,
                "permission": permission,
                "granted": granted,
            },
        )
    
    def audit_data_access(
        self,
        user_id: str,
        data_resource: str,
        operation: str,
    ) -> None:
        """Audit sensitive data access."""
        self.ledger.append(
            event_type=AuditEventType.DATA_ACCESS,
            actor=f"user_{user_id}",
            action=operation,
            resource=data_resource,
            metadata={
                "user_id": user_id,
                "operation": operation,
                "resource": data_resource,
            },
            request_tsa_timestamp=True,  # Sensitive data access gets timestamp
        )


def demo_temporal_integration():
    """Demonstrate Temporal workflow integration."""
    print("=" * 60)
    print("TEMPORAL WORKFLOW INTEGRATION DEMO")
    print("=" * 60)
    print()
    
    # Create workflow with audit ledger
    ledger_path = Path("temporal_workflow_audit.json")
    workflow = AuditedTemporalWorkflow.UserOnboardingWorkflow()
    workflow.ledger = create_ledger(ledger_path)
    
    # Run workflow
    print("Running user onboarding workflow...")
    user_data = {
        "user_id": "user_123",
        "email": "user@example.com",
        "name": "Test User",
    }
    
    # Simulate workflow execution (would be async in real Temporal)
    import asyncio
    result = asyncio.run(workflow.run(user_data))
    
    print(f"✓ Workflow completed: {result}")
    print(f"✓ Audit entries: {len(workflow.ledger.entries)}")
    print()
    
    # Verify integrity
    is_valid, errors = workflow.ledger.verify_chain()
    print(f"Audit chain valid: {is_valid}")
    
    # Detect tampering
    is_tampered, issues = workflow.ledger.detect_tampering()
    print(f"Tampering detected: {is_tampered}")
    print()
    
    return workflow.ledger


def demo_governance_integration():
    """Demonstrate governance decision integration."""
    print("=" * 60)
    print("GOVERNANCE DECISION INTEGRATION DEMO")
    print("=" * 60)
    print()
    
    ledger_path = Path("governance_audit.json")
    governance = AuditedGovernanceDecision(ledger_path)
    
    # Make governance decisions
    print("Making governance decisions...")
    
    governance.make_decision(
        policy_id="pol_001",
        decision="approved",
        reason="Within policy parameters",
        context={
            "requested_by": "user_123",
            "resource": "sensitive_data",
            "timestamp": "2026-03-05T09:35:00Z",
        },
    )
    
    governance.make_decision(
        policy_id="pol_002",
        decision="denied",
        reason="Outside business hours",
        context={
            "requested_by": "user_456",
            "resource": "admin_panel",
            "timestamp": "2026-03-05T23:00:00Z",
        },
    )
    
    print(f"✓ Decisions recorded: {len(governance.ledger.entries)}")
    print()


def demo_security_integration():
    """Demonstrate security event integration."""
    print("=" * 60)
    print("SECURITY EVENT INTEGRATION DEMO")
    print("=" * 60)
    print()
    
    ledger_path = Path("security_audit.json")
    security = AuditedSecurityEvent(ledger_path)
    
    # Audit security events
    print("Auditing security events...")
    
    security.audit_authentication(
        user_id="user_123",
        auth_method="mfa",
        success=True,
        ip_address="192.168.1.100",
    )
    
    security.audit_authorization(
        user_id="user_123",
        resource="sensitive_data",
        permission="read",
        granted=True,
    )
    
    security.audit_data_access(
        user_id="user_123",
        data_resource="patient_records",
        operation="read",
    )
    
    print(f"✓ Security events recorded: {len(security.ledger.entries)}")
    print()


def main():
    """Run all integration demos."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 12 + "TEMPORAL INTEGRATION EXAMPLES" + " " * 17 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Temporal workflow integration
    workflow_ledger = demo_temporal_integration()
    
    # Governance integration
    demo_governance_integration()
    
    # Security integration
    demo_security_integration()
    
    print("=" * 60)
    print("INTEGRATION DEMOS COMPLETE")
    print("=" * 60)
    print()
    print("Files created:")
    print("  - temporal_workflow_audit.json")
    print("  - governance_audit.json")
    print("  - security_audit.json")
    print()
    print("Each ledger provides:")
    print("  ✓ Cryptographic integrity (SHA-256 + Ed25519)")
    print("  ✓ Non-repudiation (digital signatures)")
    print("  ✓ Timestamp proofs (RFC 3161)")
    print("  ✓ Instant tamper detection")
    print("  ✓ Merkle tree verification")
    print()


if __name__ == '__main__':
    main()
