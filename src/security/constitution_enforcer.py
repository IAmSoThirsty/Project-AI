# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / constitution_enforcer.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / constitution_enforcer.py

#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #


# CONSTITUTION ENFORCER
# Global Security Guards for Project-AI

from .thirstys_constitution import enforce, ACTION_HALT, SecurityViolationException
import functools

def constitutional_guard(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract security context from kwargs or defaults
        context = {
            "mutates_state": kwargs.get("mutates_state", False),
            "trust_delta": kwargs.get("trust_delta", 0),
            "affects_human": kwargs.get("affects_human", False),
            "is_agent": kwargs.get("is_agent", True),  # Default to True for service calls
            "audit_span_id": kwargs.get("audit_span_id"),
            "source_tenant": kwargs.get("source_tenant"),
            "target_tenant": kwargs.get("target_tenant"),
            "cross_tenant_auth": kwargs.get("cross_tenant_auth", False),
            "replay_log": kwargs.get("replay_log")
        }
        
        result = enforce(func.__name__, context)
        
        if not result["allowed"]:
            if result["action"] == ACTION_HALT:
                raise SecurityViolationException(f"CONSTITUTIONAL HALT: {result['reason']} (Rule: {result['rule_violated']})")
            # Log or handle other actions (ESCALATE, DEGRADE) as needed
            
        return func(*args, **kwargs)
    return wrapper
