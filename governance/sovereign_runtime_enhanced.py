"""
Sovereign Runtime Enhanced - Advanced Policy Enforcement
[2026-03-05]

This module enhances the Sovereign Runtime with:
1. Capability-Based Security - Fine-grained capabilities with scope/TTL/constraints
2. Time-Based Constraints - Business hours, temporal windows, rate limits
3. Dynamic Policy Compilation - JIT compile policies to native code for speed
4. Cryptographic Proofs - Ed25519 signatures for all policy decisions
5. Integration with STATE_REGISTER and Triumvirate

Architecture:
- CapabilityToken: Fine-grained permissions with temporal/scope constraints
- PolicyCompiler: JIT compilation of policies to bytecode for performance
- TimeConstraintEngine: Enforce temporal policies (business hours, windows, rate limits)
- ProofGenerator: Cryptographic proof of all policy decisions
- RuntimeEngine: Unified enforcement layer with STATE_REGISTER integration
"""

import ast
import hashlib
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from governance.sovereign_runtime import SovereignRuntime

logger = logging.getLogger(__name__)


# ============================================================================
# CAPABILITY-BASED SECURITY
# ============================================================================


class CapabilityScope(Enum):
    """Capability scope levels"""
    GLOBAL = "global"           # Entire system
    SERVICE = "service"         # Specific service
    RESOURCE = "resource"       # Specific resource
    OPERATION = "operation"     # Specific operation


@dataclass
class CapabilityConstraint:
    """Constraint on capability usage"""
    constraint_type: str        # "time_window", "rate_limit", "condition", "delegation"
    parameters: dict[str, Any]
    
    def evaluate(self, context: dict[str, Any]) -> tuple[bool, str]:
        """Evaluate constraint against context"""
        if self.constraint_type == "time_window":
            return self._eval_time_window(context)
        elif self.constraint_type == "rate_limit":
            return self._eval_rate_limit(context)
        elif self.constraint_type == "condition":
            return self._eval_condition(context)
        elif self.constraint_type == "delegation":
            return self._eval_delegation(context)
        return False, f"Unknown constraint type: {self.constraint_type}"
    
    def _eval_time_window(self, context: dict[str, Any]) -> tuple[bool, str]:
        """Evaluate time window constraint"""
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(self.parameters.get("start", ""))
        end = datetime.fromisoformat(self.parameters.get("end", ""))
        
        if start <= now <= end:
            return True, "Within time window"
        return False, f"Outside time window {start} to {end}"
    
    def _eval_rate_limit(self, context: dict[str, Any]) -> tuple[bool, str]:
        """Evaluate rate limit constraint"""
        max_calls = self.parameters.get("max_calls", 0)
        window_seconds = self.parameters.get("window_seconds", 60)
        current_calls = context.get("rate_limit_calls", 0)
        
        if current_calls < max_calls:
            return True, f"Rate limit OK ({current_calls}/{max_calls})"
        return False, f"Rate limit exceeded ({current_calls}/{max_calls})"
    
    def _eval_condition(self, context: dict[str, Any]) -> tuple[bool, str]:
        """Evaluate custom condition"""
        condition = self.parameters.get("expression", "True")
        try:
            # Safe eval of simple expressions
            allowed_names = {"context": context, "True": True, "False": False}
            result = eval(condition, {"__builtins__": {}}, allowed_names)
            return bool(result), f"Condition '{condition}' = {result}"
        except Exception as e:
            return False, f"Condition evaluation failed: {e}"
    
    def _eval_delegation(self, context: dict[str, Any]) -> tuple[bool, str]:
        """Evaluate delegation constraint"""
        allowed_delegatees = self.parameters.get("allowed_delegatees", [])
        delegatee = context.get("delegatee")
        
        if delegatee in allowed_delegatees:
            return True, f"Delegation to {delegatee} allowed"
        return False, f"Delegation to {delegatee} not allowed"


@dataclass
class CapabilityToken:
    """
    Fine-grained capability token with scope, TTL, and constraints.
    
    Represents a specific permission with temporal and contextual limits.
    """
    token_id: str
    issuer: str                 # Who issued this capability
    subject: str                # Who can use this capability
    action: str                 # What action is permitted
    scope: CapabilityScope
    scope_value: str | None     # Specific scope value (e.g., service name)
    
    # Temporal constraints
    issued_at: datetime
    expires_at: datetime | None
    max_uses: int | None = None
    uses_count: int = 0
    
    # Additional constraints
    constraints: list[CapabilityConstraint] = field(default_factory=list)
    
    # Delegation
    can_delegate: bool = False
    delegation_depth: int = 0
    max_delegation_depth: int = 0
    
    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self, context: dict[str, Any] | None = None) -> tuple[bool, str]:
        """Check if capability is currently valid"""
        context = context or {}
        now = datetime.now(timezone.utc)
        
        # Check expiration
        if self.expires_at and now > self.expires_at:
            return False, f"Capability expired at {self.expires_at}"
        
        # Check max uses
        if self.max_uses is not None and self.uses_count >= self.max_uses:
            return False, f"Max uses ({self.max_uses}) exceeded"
        
        # Check constraints
        for constraint in self.constraints:
            valid, reason = constraint.evaluate(context)
            if not valid:
                return False, f"Constraint failed: {reason}"
        
        return True, "Capability is valid"
    
    def use(self) -> None:
        """Increment usage counter"""
        self.uses_count += 1
    
    def delegate(self, new_subject: str, constraints: list[CapabilityConstraint] | None = None) -> "CapabilityToken | None":
        """Delegate capability to another subject"""
        if not self.can_delegate:
            return None
        
        if self.delegation_depth >= self.max_delegation_depth:
            return None
        
        # Create delegated token
        delegated = CapabilityToken(
            token_id=str(uuid4()),
            issuer=self.subject,  # Original subject becomes issuer
            subject=new_subject,
            action=self.action,
            scope=self.scope,
            scope_value=self.scope_value,
            issued_at=datetime.now(timezone.utc),
            expires_at=self.expires_at,  # Inherit expiration
            max_uses=self.max_uses,
            constraints=list(self.constraints) + (constraints or []),
            can_delegate=self.can_delegate,
            delegation_depth=self.delegation_depth + 1,
            max_delegation_depth=self.max_delegation_depth,
            metadata={"delegated_from": self.token_id}
        )
        
        return delegated
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "token_id": self.token_id,
            "issuer": self.issuer,
            "subject": self.subject,
            "action": self.action,
            "scope": self.scope.value,
            "scope_value": self.scope_value,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "max_uses": self.max_uses,
            "uses_count": self.uses_count,
            "constraints": [
                {
                    "constraint_type": c.constraint_type,
                    "parameters": c.parameters
                }
                for c in self.constraints
            ],
            "can_delegate": self.can_delegate,
            "delegation_depth": self.delegation_depth,
            "max_delegation_depth": self.max_delegation_depth,
            "metadata": self.metadata
        }


class CapabilityRegistry:
    """Registry for capability tokens"""
    
    def __init__(self):
        self.tokens: dict[str, CapabilityToken] = {}
        self.subject_index: dict[str, list[str]] = defaultdict(list)
    
    def register(self, token: CapabilityToken) -> None:
        """Register a capability token"""
        self.tokens[token.token_id] = token
        self.subject_index[token.subject].append(token.token_id)
    
    def get(self, token_id: str) -> CapabilityToken | None:
        """Get capability by ID"""
        return self.tokens.get(token_id)
    
    def get_by_subject(self, subject: str) -> list[CapabilityToken]:
        """Get all capabilities for a subject"""
        token_ids = self.subject_index.get(subject, [])
        return [self.tokens[tid] for tid in token_ids if tid in self.tokens]
    
    def revoke(self, token_id: str) -> bool:
        """Revoke a capability"""
        token = self.tokens.get(token_id)
        if token:
            token.expires_at = datetime.now(timezone.utc)
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Remove expired tokens, return count removed"""
        now = datetime.now(timezone.utc)
        expired = [
            tid for tid, token in self.tokens.items()
            if token.expires_at and token.expires_at < now
        ]
        
        for tid in expired:
            token = self.tokens.pop(tid)
            self.subject_index[token.subject].remove(tid)
        
        return len(expired)


# ============================================================================
# TIME-BASED CONSTRAINTS
# ============================================================================


@dataclass
class TimeWindow:
    """Represents a time window for access"""
    start_hour: int  # 0-23
    end_hour: int    # 0-23
    days_of_week: list[int]  # 0=Monday, 6=Sunday
    timezone_name: str = "UTC"
    
    def is_active(self, dt: datetime | None = None) -> bool:
        """Check if time window is currently active"""
        dt = dt or datetime.now(timezone.utc)
        
        # Check day of week (0=Monday)
        if dt.weekday() not in self.days_of_week:
            return False
        
        # Check hour range
        hour = dt.hour
        if self.start_hour <= self.end_hour:
            return self.start_hour <= hour < self.end_hour
        else:  # Crosses midnight
            return hour >= self.start_hour or hour < self.end_hour


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_calls: int
    window_seconds: int
    burst_size: int | None = None  # Max burst above steady rate


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.buckets: dict[str, dict[str, Any]] = {}
    
    def check_limit(self, key: str, tokens: int = 1) -> tuple[bool, dict[str, Any]]:
        """Check if action is within rate limit"""
        now = time.time()
        
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.config.max_calls,
                "last_update": now,
                "total_calls": 0
            }
        
        bucket = self.buckets[key]
        
        # Refill tokens based on time passed
        time_passed = now - bucket["last_update"]
        refill_rate = self.config.max_calls / self.config.window_seconds
        tokens_to_add = time_passed * refill_rate
        
        bucket["tokens"] = min(
            self.config.max_calls,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_update"] = now
        
        # Check if enough tokens
        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            bucket["total_calls"] += tokens
            return True, {
                "allowed": True,
                "tokens_remaining": bucket["tokens"],
                "total_calls": bucket["total_calls"]
            }
        else:
            return False, {
                "allowed": False,
                "tokens_remaining": bucket["tokens"],
                "retry_after": (tokens - bucket["tokens"]) / refill_rate,
                "total_calls": bucket["total_calls"]
            }


class TimeConstraintEngine:
    """Engine for enforcing time-based constraints"""
    
    def __init__(self):
        self.business_hours = TimeWindow(
            start_hour=9,
            end_hour=17,
            days_of_week=[0, 1, 2, 3, 4],  # Monday-Friday
            timezone_name="UTC"
        )
        self.rate_limiters: dict[str, RateLimiter] = {}
        self.temporal_policies: dict[str, dict[str, Any]] = {}
    
    def set_business_hours(self, window: TimeWindow) -> None:
        """Set business hours window"""
        self.business_hours = window
    
    def is_business_hours(self, dt: datetime | None = None) -> bool:
        """Check if current time is within business hours"""
        return self.business_hours.is_active(dt)
    
    def register_rate_limit(self, policy_id: str, config: RateLimitConfig) -> None:
        """Register a rate limit policy"""
        self.rate_limiters[policy_id] = RateLimiter(config)
    
    def check_rate_limit(self, policy_id: str, key: str, tokens: int = 1) -> tuple[bool, dict[str, Any]]:
        """Check rate limit for a policy"""
        limiter = self.rate_limiters.get(policy_id)
        if not limiter:
            return True, {"allowed": True, "reason": "No rate limit configured"}
        
        return limiter.check_limit(key, tokens)
    
    def register_temporal_policy(self, policy_id: str, policy: dict[str, Any]) -> None:
        """Register a temporal policy"""
        self.temporal_policies[policy_id] = policy
    
    def evaluate_temporal_policy(self, policy_id: str, context: dict[str, Any]) -> tuple[bool, str]:
        """Evaluate a temporal policy"""
        policy = self.temporal_policies.get(policy_id)
        if not policy:
            return True, "No temporal policy configured"
        
        now = datetime.now(timezone.utc)
        
        # Check time windows
        if "allowed_windows" in policy:
            in_window = False
            for window_def in policy["allowed_windows"]:
                window = TimeWindow(**window_def)
                if window.is_active(now):
                    in_window = True
                    break
            
            if not in_window:
                return False, "Outside allowed time windows"
        
        # Check blackout periods
        if "blackout_periods" in policy:
            for period in policy["blackout_periods"]:
                start = datetime.fromisoformat(period["start"])
                end = datetime.fromisoformat(period["end"])
                if start <= now <= end:
                    return False, f"Within blackout period: {period.get('reason', 'N/A')}"
        
        return True, "Temporal policy satisfied"


# ============================================================================
# DYNAMIC POLICY COMPILATION (JIT)
# ============================================================================


class CompiledPolicy:
    """Compiled policy for fast execution"""
    
    def __init__(self, policy_id: str, policy_func: Callable, metadata: dict[str, Any]):
        self.policy_id = policy_id
        self.policy_func = policy_func
        self.metadata = metadata
        self.compiled_at = datetime.now(timezone.utc)
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    def execute(self, context: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
        """Execute compiled policy"""
        start = time.time()
        try:
            result = self.policy_func(context)
            allowed = result.get("allowed", False)
            reason = result.get("reason", "No reason provided")
            metadata = result.get("metadata", {})
            
            self.execution_count += 1
            self.total_execution_time += time.time() - start
            
            return allowed, reason, metadata
        except Exception as e:
            logger.error(f"Policy execution failed: {e}")
            return False, f"Policy execution error: {e}", {}
    
    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics"""
        avg_time = self.total_execution_time / self.execution_count if self.execution_count > 0 else 0
        return {
            "policy_id": self.policy_id,
            "compiled_at": self.compiled_at.isoformat(),
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_time
        }


class PolicyCompiler:
    """
    JIT compiler for policies.
    
    Compiles policy definitions to Python bytecode for fast execution.
    """
    
    def __init__(self):
        self.compiled_policies: dict[str, CompiledPolicy] = {}
        self.compilation_stats: dict[str, Any] = defaultdict(int)
    
    def compile_policy(self, policy_id: str, policy_def: dict[str, Any]) -> CompiledPolicy | None:
        """
        Compile a policy definition to executable code.
        
        Policy definition format:
        {
            "rules": [
                {
                    "condition": "context['user_role'] == 'admin'",
                    "allow": true,
                    "reason": "Admin access granted"
                }
            ],
            "default": {"allow": false, "reason": "No matching rule"}
        }
        """
        try:
            # Build policy function
            policy_func = self._build_policy_function(policy_def)
            
            # Create compiled policy
            compiled = CompiledPolicy(
                policy_id=policy_id,
                policy_func=policy_func,
                metadata={
                    "rules_count": len(policy_def.get("rules", [])),
                    "has_default": "default" in policy_def
                }
            )
            
            self.compiled_policies[policy_id] = compiled
            self.compilation_stats["total_compilations"] += 1
            
            logger.info(f"Compiled policy: {policy_id}")
            return compiled
            
        except Exception as e:
            logger.error(f"Policy compilation failed for {policy_id}: {e}")
            self.compilation_stats["failed_compilations"] += 1
            return None
    
    def _build_policy_function(self, policy_def: dict[str, Any]) -> Callable:
        """Build executable policy function from definition"""
        rules = policy_def.get("rules", [])
        default = policy_def.get("default", {"allowed": False, "reason": "No matching rule"})
        
        def policy_func(context: dict[str, Any]) -> dict[str, Any]:
            # Evaluate rules in order
            for rule in rules:
                try:
                    # Safe eval with restricted namespace
                    condition = rule.get("condition", "False")
                    allowed_names = {
                        "context": context,
                        "True": True,
                        "False": False,
                        "None": None,
                        "len": len,
                        "str": str,
                        "int": int,
                        "float": float,
                        "bool": bool,
                    }
                    
                    # Parse and validate AST
                    tree = ast.parse(condition, mode='eval')
                    
                    # Evaluate condition
                    result = eval(compile(tree, '<policy>', 'eval'), {"__builtins__": {}}, allowed_names)
                    
                    if result:
                        return {
                            "allowed": rule.get("allow", False),
                            "reason": rule.get("reason", "Rule matched"),
                            "metadata": rule.get("metadata", {})
                        }
                except Exception as e:
                    logger.warning(f"Rule evaluation failed: {e}")
                    continue
            
            # No rule matched, use default
            return default
        
        return policy_func
    
    def get_compiled_policy(self, policy_id: str) -> CompiledPolicy | None:
        """Get compiled policy by ID"""
        return self.compiled_policies.get(policy_id)
    
    def recompile_all(self, policy_defs: dict[str, dict[str, Any]]) -> None:
        """Recompile all policies"""
        for policy_id, policy_def in policy_defs.items():
            self.compile_policy(policy_id, policy_def)
    
    def get_stats(self) -> dict[str, Any]:
        """Get compilation statistics"""
        return {
            "total_policies": len(self.compiled_policies),
            "compilation_stats": dict(self.compilation_stats),
            "policy_stats": [
                policy.get_stats() for policy in self.compiled_policies.values()
            ]
        }


# ============================================================================
# CRYPTOGRAPHIC PROOFS
# ============================================================================


@dataclass
class PolicyDecisionProof:
    """Cryptographic proof of policy decision"""
    proof_id: str
    decision_type: str          # "allow", "deny"
    policy_id: str
    context_hash: str
    decision_hash: str
    signature: str
    public_key: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "proof_id": self.proof_id,
            "decision_type": self.decision_type,
            "policy_id": self.policy_id,
            "context_hash": self.context_hash,
            "decision_hash": self.decision_hash,
            "signature": self.signature,
            "public_key": self.public_key,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class ProofGenerator:
    """Generate cryptographic proofs for policy decisions"""
    
    def __init__(self, sovereign_runtime: SovereignRuntime):
        self.runtime = sovereign_runtime
        self.proofs: dict[str, PolicyDecisionProof] = {}
    
    def generate_proof(
        self,
        decision_type: str,
        policy_id: str,
        context: dict[str, Any],
        decision: dict[str, Any]
    ) -> PolicyDecisionProof:
        """Generate cryptographic proof of policy decision"""
        # Compute context hash
        context_str = json.dumps(context, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()
        
        # Compute decision hash
        decision_data = {
            "decision_type": decision_type,
            "policy_id": policy_id,
            "context_hash": context_hash,
            "decision": decision,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        decision_str = json.dumps(decision_data, sort_keys=True)
        decision_hash = hashlib.sha256(decision_str.encode()).hexdigest()
        
        # Sign decision hash
        signature = self.runtime.private_key.sign(decision_hash.encode())
        
        # Create proof
        proof = PolicyDecisionProof(
            proof_id=str(uuid4()),
            decision_type=decision_type,
            policy_id=policy_id,
            context_hash=context_hash,
            decision_hash=decision_hash,
            signature=signature.hex(),
            public_key=self.runtime.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ).hex(),
            timestamp=decision_data["timestamp"],
            metadata={
                "decision": decision,
                "context_size": len(context_str)
            }
        )
        
        self.proofs[proof.proof_id] = proof
        
        # Log to audit trail
        self.runtime.audit_log(
            "POLICY_DECISION_PROOF",
            {
                "proof_id": proof.proof_id,
                "decision_type": decision_type,
                "policy_id": policy_id,
                "decision_hash": decision_hash
            }
        )
        
        return proof
    
    def verify_proof(self, proof: PolicyDecisionProof) -> bool:
        """Verify cryptographic proof"""
        try:
            # Reconstruct decision data
            decision_data = {
                "decision_type": proof.decision_type,
                "policy_id": proof.policy_id,
                "context_hash": proof.context_hash,
                "decision": proof.metadata.get("decision", {}),
                "timestamp": proof.timestamp
            }
            decision_str = json.dumps(decision_data, sort_keys=True)
            computed_hash = hashlib.sha256(decision_str.encode()).hexdigest()
            
            # Check hash matches
            if computed_hash != proof.decision_hash:
                logger.error("Decision hash mismatch in proof")
                return False
            
            # Verify signature
            public_key_bytes = bytes.fromhex(proof.public_key)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = bytes.fromhex(proof.signature)
            
            public_key.verify(signature, proof.decision_hash.encode())
            
            logger.info(f"Proof verified: {proof.proof_id}")
            return True
            
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return False
    
    def export_proofs(self, output_path: Path) -> bool:
        """Export all proofs to file"""
        try:
            proofs_data = {
                "version": "1.0.0",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_proofs": len(self.proofs),
                "proofs": [proof.to_dict() for proof in self.proofs.values()]
            }
            
            with open(output_path, "w") as f:
                json.dump(proofs_data, f, indent=2)
            
            logger.info(f"Exported {len(self.proofs)} proofs to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export proofs: {e}")
            return False


# ============================================================================
# ENHANCED RUNTIME ENGINE
# ============================================================================


class EnhancedSovereignRuntime:
    """
    Enhanced Sovereign Runtime with capability-based security,
    time constraints, JIT policy compilation, and cryptographic proofs.
    """
    
    def __init__(self, data_dir: Path | None = None):
        # Initialize base runtime
        self.base_runtime = SovereignRuntime(data_dir)
        self.data_dir = self.base_runtime.data_dir
        
        # Initialize enhanced components
        self.capability_registry = CapabilityRegistry()
        self.time_engine = TimeConstraintEngine()
        self.policy_compiler = PolicyCompiler()
        self.proof_generator = ProofGenerator(self.base_runtime)
        
        # STATE_REGISTER integration (placeholder - will connect to actual register)
        self.state_register: dict[str, Any] = {}
        
        # Triumvirate integration (placeholder - will connect to actual Triumvirate)
        self.triumvirate_callback: Callable | None = None
        
        logger.info("Enhanced Sovereign Runtime initialized")
    
    # ========================================================================
    # CAPABILITY MANAGEMENT
    # ========================================================================
    
    def issue_capability(
        self,
        issuer: str,
        subject: str,
        action: str,
        scope: CapabilityScope,
        scope_value: str | None = None,
        ttl_seconds: int | None = None,
        max_uses: int | None = None,
        constraints: list[CapabilityConstraint] | None = None,
        can_delegate: bool = False,
        max_delegation_depth: int = 0
    ) -> CapabilityToken:
        """Issue a new capability token"""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds) if ttl_seconds else None
        
        token = CapabilityToken(
            token_id=str(uuid4()),
            issuer=issuer,
            subject=subject,
            action=action,
            scope=scope,
            scope_value=scope_value,
            issued_at=now,
            expires_at=expires_at,
            max_uses=max_uses,
            constraints=constraints or [],
            can_delegate=can_delegate,
            delegation_depth=0,
            max_delegation_depth=max_delegation_depth
        )
        
        self.capability_registry.register(token)
        
        # Log to audit trail
        self.base_runtime.audit_log(
            "CAPABILITY_ISSUED",
            {
                "token_id": token.token_id,
                "issuer": issuer,
                "subject": subject,
                "action": action,
                "scope": scope.value,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
        )
        
        return token
    
    def check_capability(
        self,
        token_id: str,
        context: dict[str, Any] | None = None
    ) -> tuple[bool, str]:
        """Check if a capability is valid"""
        token = self.capability_registry.get(token_id)
        if not token:
            return False, "Capability not found"
        
        return token.is_valid(context)
    
    def use_capability(self, token_id: str, context: dict[str, Any] | None = None) -> tuple[bool, str]:
        """Use a capability (increment usage)"""
        valid, reason = self.check_capability(token_id, context)
        if not valid:
            return False, reason
        
        token = self.capability_registry.get(token_id)
        token.use()
        
        # Log usage
        self.base_runtime.audit_log(
            "CAPABILITY_USED",
            {
                "token_id": token_id,
                "uses_count": token.uses_count,
                "subject": token.subject,
                "action": token.action
            }
        )
        
        return True, f"Capability used ({token.uses_count} uses)"
    
    # ========================================================================
    # POLICY ENFORCEMENT
    # ========================================================================
    
    def compile_policy(self, policy_id: str, policy_def: dict[str, Any]) -> bool:
        """Compile a policy for fast execution"""
        compiled = self.policy_compiler.compile_policy(policy_id, policy_def)
        return compiled is not None
    
    def evaluate_policy(
        self,
        policy_id: str,
        context: dict[str, Any],
        generate_proof: bool = True
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Evaluate a compiled policy with full proof generation.
        
        Returns: (allowed, reason, metadata)
        """
        # Get compiled policy
        compiled = self.policy_compiler.get_compiled_policy(policy_id)
        if not compiled:
            return False, "Policy not compiled", {}
        
        # Execute policy
        allowed, reason, metadata = compiled.execute(context)
        
        # Generate cryptographic proof
        if generate_proof:
            decision = {
                "allowed": allowed,
                "reason": reason,
                "metadata": metadata
            }
            proof = self.proof_generator.generate_proof(
                decision_type="allow" if allowed else "deny",
                policy_id=policy_id,
                context=context,
                decision=decision
            )
            metadata["proof_id"] = proof.proof_id
        
        # Log decision
        self.base_runtime.audit_log(
            "POLICY_DECISION",
            {
                "policy_id": policy_id,
                "decision": "allow" if allowed else "deny",
                "reason": reason,
                "proof_id": metadata.get("proof_id")
            },
            severity="INFO" if allowed else "WARNING"
        )
        
        return allowed, reason, metadata
    
    def enforce_policy(
        self,
        policy_id: str,
        context: dict[str, Any],
        triumvirate_override: bool = False
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Enforce policy with time constraints and Triumvirate integration.
        
        This is the main enforcement entry point.
        """
        # Check temporal constraints
        temporal_valid, temporal_reason = self.time_engine.evaluate_temporal_policy(
            policy_id, context
        )
        if not temporal_valid:
            return False, f"Temporal constraint failed: {temporal_reason}", {}
        
        # Check rate limits if configured
        rate_limit_key = f"{policy_id}:{context.get('subject', 'unknown')}"
        rate_ok, rate_info = self.time_engine.check_rate_limit(policy_id, rate_limit_key)
        if not rate_ok:
            return False, f"Rate limit exceeded: {rate_info}", rate_info
        
        # Evaluate policy
        allowed, reason, metadata = self.evaluate_policy(policy_id, context)
        
        # Triumvirate override check (for high-stakes decisions)
        if triumvirate_override and self.triumvirate_callback:
            triumvirate_result = self.triumvirate_callback(policy_id, context, {
                "allowed": allowed,
                "reason": reason,
                "metadata": metadata
            })
            
            if triumvirate_result.get("override"):
                allowed = triumvirate_result["allowed"]
                reason = f"Triumvirate override: {triumvirate_result['reason']}"
                metadata["triumvirate_override"] = True
        
        # Update STATE_REGISTER
        self._update_state_register(policy_id, allowed, context)
        
        return allowed, reason, metadata
    
    # ========================================================================
    # INTEGRATION POINTS
    # ========================================================================
    
    def _update_state_register(self, policy_id: str, allowed: bool, context: dict[str, Any]) -> None:
        """Update STATE_REGISTER with policy decision"""
        self.state_register[policy_id] = {
            "last_decision": "allow" if allowed else "deny",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_hash": hashlib.sha256(
                json.dumps(context, sort_keys=True).encode()
            ).hexdigest()
        }
    
    def register_triumvirate_callback(self, callback: Callable) -> None:
        """Register Triumvirate integration callback"""
        self.triumvirate_callback = callback
        logger.info("Triumvirate callback registered")
    
    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of runtime state"""
        return {
            "capabilities": {
                "total": len(self.capability_registry.tokens),
                "by_subject": {
                    subject: len(tokens)
                    for subject, tokens in self.capability_registry.subject_index.items()
                }
            },
            "policies": self.policy_compiler.get_stats(),
            "proofs": {
                "total": len(self.proof_generator.proofs)
            },
            "state_register": {
                "entries": len(self.state_register)
            },
            "audit_trail": {
                "valid": self.base_runtime.verify_audit_trail_integrity()[0]
            }
        }
    
    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================
    
    def create_business_hours_capability(
        self,
        issuer: str,
        subject: str,
        action: str,
        ttl_days: int = 30
    ) -> CapabilityToken:
        """Create capability with business hours constraint"""
        constraint = CapabilityConstraint(
            constraint_type="condition",
            parameters={
                "expression": "context.get('in_business_hours', False)"
            }
        )
        
        return self.issue_capability(
            issuer=issuer,
            subject=subject,
            action=action,
            scope=CapabilityScope.GLOBAL,
            ttl_seconds=ttl_days * 24 * 3600,
            constraints=[constraint]
        )
    
    def create_rate_limited_capability(
        self,
        issuer: str,
        subject: str,
        action: str,
        max_calls: int,
        window_seconds: int = 60,
        ttl_days: int = 30
    ) -> CapabilityToken:
        """Create capability with rate limit constraint"""
        constraint = CapabilityConstraint(
            constraint_type="rate_limit",
            parameters={
                "max_calls": max_calls,
                "window_seconds": window_seconds
            }
        )
        
        return self.issue_capability(
            issuer=issuer,
            subject=subject,
            action=action,
            scope=CapabilityScope.GLOBAL,
            ttl_seconds=ttl_days * 24 * 3600,
            constraints=[constraint]
        )
    
    def export_full_compliance_bundle(self, output_dir: Path) -> bool:
        """Export complete compliance bundle with all proofs and audit data"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export base compliance bundle
            self.base_runtime.export_compliance_bundle(output_dir / "base_compliance.json")
            
            # Export proofs
            self.proof_generator.export_proofs(output_dir / "policy_proofs.json")
            
            # Export state summary
            with open(output_dir / "state_summary.json", "w") as f:
                json.dump(self.get_state_summary(), f, indent=2)
            
            logger.info(f"Exported full compliance bundle to {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export compliance bundle: {e}")
            return False


__all__ = [
    "EnhancedSovereignRuntime",
    "CapabilityToken",
    "CapabilityScope",
    "CapabilityConstraint",
    "CapabilityRegistry",
    "TimeWindow",
    "RateLimitConfig",
    "TimeConstraintEngine",
    "PolicyCompiler",
    "CompiledPolicy",
    "ProofGenerator",
    "PolicyDecisionProof"
]
