"""
ATLAS Ω - Epistemic Safeguards

Complete implementation of three critical safeguards:
1. Epistemic Gravity Mitigation - Prevent cognitive anchoring to ATLAS outputs
2. Prompt Framing Guards - Mechanical rejection of normative queries
3. Responsibility Boundary Enforcement - Non-transferable responsibility clauses

⚠️ CRITICAL: These safeguards protect against ATLAS Ω becoming de facto authority.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import json

from atlas.audit.trail import get_audit_trail

logger = logging.getLogger(__name__)


# ============================================================================
# SAFEGUARD 1: EPISTEMIC GRAVITY MITIGATION
# ============================================================================

class DecisionBasis(Enum):
    """How much a decision relied on ATLAS Ω."""
    INFORMED_BY_ATLAS = "informed_by"  # ATLAS provided input, other factors considered
    INFORMED_AND_VALIDATED = "informed_and_validated"  # ATLAS + independent validation
    INDEPENDENT_OF_ATLAS = "independent"  # Decision made without ATLAS
    CONTRADICTS_ATLAS = "contradicts"  # Decision explicitly contradicts ATLAS output


@dataclass
class Decision:
    """Record of a decision with ATLAS Ω involvement tracking."""
    decision_id: str
    decision_maker: str  # Who made the decision
    timestamp: datetime
    description: str
    
    # ATLAS involvement
    atlas_consulted: bool
    atlas_output_id: Optional[str] = None  # ID of ATLAS output consulted
    basis: DecisionBasis = DecisionBasis.INDEPENDENT_OF_ATLAS
    
    # Non-ATLAS reasoning
    reasoning_beyond_atlas: List[str] = field(default_factory=list)
    independent_factors: List[str] = field(default_factory=list)
    
    # Dissent tracking
    dissents_from_atlas: bool = False
    dissent_justification: Optional[str] = None
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate decision record."""
        errors = []
        
        if not self.decision_maker:
            errors.append("decision_maker is required")
        
        if self.atlas_consulted:
            if self.basis == DecisionBasis.INDEPENDENT_OF_ATLAS:
                errors.append("ATLAS was consulted but basis is 'independent' - contradiction")
            
            if self.basis in [DecisionBasis.INFORMED_BY_ATLAS, DecisionBasis.INFORMED_AND_VALIDATED]:
                if not self.reasoning_beyond_atlas:
                    errors.append("ATLAS-informed decision MUST include reasoning beyond ATLAS")
        
        if self.dissents_from_atlas and not self.dissent_justification:
            errors.append("Dissent from ATLAS requires justification")
        
        return len(errors) == 0, errors


class EpistemicGravityMitigation:
    """
    Safeguard 1: Epistemic Gravity Mitigation
    
    Prevents ATLAS Ω from becoming de facto authority through:
    - Decision logging showing "informed by" vs "justified solely by"
    - Explicit dissent pathway tracking
    - Cognitive anchoring prevention
    """
    
    def __init__(self, audit_trail=None):
        """Initialize epistemic gravity mitigation."""
        self.audit_trail = audit_trail or get_audit_trail()
        
        # Decision registry
        self.decisions: List[Decision] = []
        
        # Statistics
        self.atlas_consulted_count = 0
        self.dissent_count = 0
        self.independent_decision_count = 0
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="epistemic_gravity_mitigation_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info("Epistemic gravity mitigation active")
    
    def log_decision(self, decision: Decision) -> None:
        """
        Log a decision with ATLAS involvement tracking.
        
        This creates an audit trail showing decisions were NOT
        justified solely by ATLAS Ω output.
        """
        # Validate decision
        valid, errors = decision.validate()
        if not valid:
            raise ValueError(f"Invalid decision record: {errors}")
        
        # Store decision
        self.decisions.append(decision)
        
        # Update statistics
        if decision.atlas_consulted:
            self.atlas_consulted_count += 1
        if decision.dissents_from_atlas:
            self.dissent_count += 1
        if decision.basis == DecisionBasis.INDEPENDENT_OF_ATLAS:
            self.independent_decision_count += 1
        
        # Audit log
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="decision_logged",
            details={
                "decision_id": decision.decision_id,
                "decision_maker": decision.decision_maker,
                "atlas_consulted": decision.atlas_consulted,
                "basis": decision.basis.value,
                "dissents_from_atlas": decision.dissents_from_atlas,
                "independent_factors_count": len(decision.independent_factors)
            },
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info(f"Decision logged: {decision.decision_id} (basis: {decision.basis.value})")
    
    def verify_dissent_pathway(self) -> Tuple[bool, str]:
        """
        Verify that dissent from ATLAS is possible and has occurred.
        
        If dissent is impossible, ATLAS becomes de facto authority.
        
        Returns:
            (is_possible, message)
        """
        if self.dissent_count == 0 and self.atlas_consulted_count > 10:
            return False, f"No dissents in {self.atlas_consulted_count} ATLAS-consulted decisions - pathway may be blocked"
        
        if self.dissent_count > 0:
            dissent_rate = self.dissent_count / max(1, self.atlas_consulted_count)
            return True, f"Dissent pathway verified: {self.dissent_count} dissents ({dissent_rate:.1%} rate)"
        
        return True, "Dissent pathway available (not yet tested)"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get epistemic gravity statistics."""
        return {
            "total_decisions": len(self.decisions),
            "atlas_consulted": self.atlas_consulted_count,
            "dissents_from_atlas": self.dissent_count,
            "independent_decisions": self.independent_decision_count,
            "dissent_pathway_open": self.verify_dissent_pathway()[0]
        }


# ============================================================================
# SAFEGUARD 2: PROMPT FRAMING GUARDS
# ============================================================================

class QueryType(Enum):
    """Types of queries to ATLAS Ω."""
    SIMULATE = "simulate"  # ALLOWED: "What happens if...?"
    PROJECT = "project"  # ALLOWED: "What are outcomes of...?"
    COMPARE = "compare"  # ALLOWED: "Compare scenarios A vs B"
    ANALYZE = "analyze"  # ALLOWED: "Analyze this situation"
    
    # BLOCKED: Normative queries
    RECOMMEND = "recommend"  # BLOCKED: "What should we do?"
    CHOOSE = "choose"  # BLOCKED: "Which option is best?"
    OPTIMIZE = "optimize"  # BLOCKED: "How to maximize X?"
    DECIDE = "decide"  # BLOCKED: "Should we do X?"


# Normative keywords that trigger blocking
NORMATIVE_KEYWORDS = [
    "should", "recommend", "best", "optimal", "choose",
    "decide", "which option", "what to do", "advise", 
    "suggest", "preference", "better than"
]


@dataclass
class QueryValidation:
    """Result of query validation."""
    query: str
    is_allowed: bool
    query_type: QueryType
    rejection_reason: Optional[str] = None


class PromptFramingGuards:
    """
    Safeguard 2: Prompt Framing Guards
    
    Mechanically rejects normative queries that would turn
    ATLAS Ω from a simulation tool into a decision-maker.
    """
    
    def __init__(self, audit_trail=None):
        """Initialize prompt framing guards."""
        self.audit_trail = audit_trail or get_audit_trail()
        
        # Query history
        self.allowed_queries: List[str] = []
        self.rejected_queries: List[Tuple[str, str]] = []  # (query, reason)
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="prompt_framing_guards_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info("Prompt framing guards active")
    
    def validate_query(self, query: str) -> QueryValidation:
        """
        Validate query against allowed types.
        
        ALLOWED: simulate, project, compare, analyze
        BLOCKED: recommend, choose, optimize, decide
        
        Returns:
            QueryValidation with is_allowed flag
        """
        query_lower = query.lower()
        
        # Check for normative keywords
        for keyword in NORMATIVE_KEYWORDS:
            if keyword in query_lower:
                validation = QueryValidation(
                    query=query,
                    is_allowed=False,
                    query_type=QueryType.RECOMMEND,  # Classify as normative
                    rejection_reason=f"Normative query detected (keyword: '{keyword}'). ATLAS Ω projects, does not recommend."
                )
                
                self.rejected_queries.append((query, validation.rejection_reason))
                
                self.audit_trail.log(
                    category="GOVERNANCE",
                    operation="normative_query_rejected",
                    details={
                        "query": query[:100],  # Truncate for logging
                        "keyword": keyword,
                        "reason": validation.rejection_reason
                    },
                    level="CRITICAL",
                    priority="HIGH_PRIORITY"
                )
                
                logger.warning(f"REJECTED normative query: {validation.rejection_reason}")
                return validation
        
        # Determine query type (simplified classification)
        if "simulate" in query_lower or "what happens" in query_lower:
            query_type = QueryType.SIMULATE
        elif "project" in query_lower or "outcomes" in query_lower:
            query_type = QueryType.PROJECT
        elif "compare" in query_lower or "versus" in query_lower or "vs" in query_lower:
            query_type = QueryType.COMPARE
        elif "analyze" in query_lower or "analysis" in query_lower:
            query_type = QueryType.ANALYZE
        else:
            # Default to SIMULATE if ambiguous
            query_type = QueryType.SIMULATE
        
        # Allow query
        validation = QueryValidation(
            query=query,
            is_allowed=True,
            query_type=query_type
        )
        
        self.allowed_queries.append(query)
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="query_validated",
            details={
                "query": query[:100],
                "query_type": query_type.value
            },
            level="INFORMATIONAL"
        )
        
        return validation
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get query statistics."""
        return {
            "total_queries": len(self.allowed_queries) + len(self.rejected_queries),
            "allowed": len(self.allowed_queries),
            "rejected": len(self.rejected_queries),
            "rejection_rate": len(self.rejected_queries) / max(1, len(self.allowed_queries) + len(self.rejected_queries))
        }


# ============================================================================
# SAFEGUARD 3: RESPONSIBILITY BOUNDARY ENFORCEMENT
# ============================================================================

@dataclass
class ResponsibilityClause:
    """Non-transferable responsibility clause attached to output."""
    output_id: str
    timestamp: datetime
    
    # Standard clause text
    clause_text: str = (
        "⚠️ RESPONSIBILITY CLAUSE:\n"
        "This output does NOT justify or authorize action.\n"
        "This is a simulation/projection for analysis only.\n"
        "Decision-makers retain full responsibility for their choices.\n"
        "ATLAS Ω provides projections (not decisions), assists (not replaces), extends (not subsumes)."
    )
    
    # Verification
    clause_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Compute hash of clause for verification."""
        content = f"{self.output_id}:{self.timestamp.isoformat()}:{self.clause_text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def lock(self) -> None:
        """Lock clause by computing hash."""
        self.clause_hash = self.compute_hash()


@dataclass
class OutputRecord:
    """Record of ATLAS output with responsibility clause."""
    output_id: str
    output_type: str  # "projection", "simulation", "analysis"
    timestamp: datetime
    
    # Content summary
    summary: str
    
    # Responsibility
    responsibility_clause: ResponsibilityClause
    
    # If used in decision
    used_in_decision: bool = False
    decision_id: Optional[str] = None
    decision_maker: Optional[str] = None
    decision_reasoning: Optional[str] = None


class ResponsibilityBoundaryEnforcement:
    """
    Safeguard 3: Responsibility Boundary Enforcement
    
    Ensures every ATLAS output carries non-transferable responsibility
    clause and tracks human decision-makers with reasoning.
    """
    
    def __init__(self, audit_trail=None):
        """Initialize responsibility boundary enforcement."""
        self.audit_trail = audit_trail or get_audit_trail()
        
        # Output registry
        self.outputs: List[OutputRecord] = []
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="responsibility_boundary_enforcement_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info("Responsibility boundary enforcement active")
    
    def attach_clause(self, output_id: str, output_type: str, 
                     summary: str) -> ResponsibilityClause:
        """
        Attach non-transferable responsibility clause to output.
        
        This MUST be called for every ATLAS Ω output.
        """
        clause = ResponsibilityClause(
            output_id=output_id,
            timestamp=datetime.now()
        )
        clause.lock()
        
        # Create output record
        record = OutputRecord(
            output_id=output_id,
            output_type=output_type,
            timestamp=datetime.now(),
            summary=summary,
            responsibility_clause=clause
        )
        
        self.outputs.append(record)
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="responsibility_clause_attached",
            details={
                "output_id": output_id,
                "output_type": output_type,
                "clause_hash": clause.clause_hash
            },
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info(f"Responsibility clause attached to output {output_id}")
        return clause
    
    def log_output_use_in_decision(self, output_id: str, decision_id: str,
                                   decision_maker: str, reasoning: str) -> None:
        """
        Log when ATLAS output is used in a decision.
        
        Records WHO made the decision and their reasoning BEYOND ATLAS.
        """
        # Find output
        record = next((r for r in self.outputs if r.output_id == output_id), None)
        if not record:
            raise ValueError(f"Output {output_id} not found")
        
        # Update record
        record.used_in_decision = True
        record.decision_id = decision_id
        record.decision_maker = decision_maker
        record.decision_reasoning = reasoning
        
        # Verify reasoning is provided
        if not reasoning or len(reasoning) < 10:
            logger.warning(f"Decision {decision_id} has insufficient reasoning beyond ATLAS")
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="output_used_in_decision",
            details={
                "output_id": output_id,
                "decision_id": decision_id,
                "decision_maker": decision_maker,
                "reasoning_provided": bool(reasoning)
            },
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info(f"Output {output_id} used in decision {decision_id} by {decision_maker}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get responsibility tracking statistics."""
        used_in_decisions = sum(1 for r in self.outputs if r.used_in_decision)
        
        return {
            "total_outputs": len(self.outputs),
            "used_in_decisions": used_in_decisions,
            "unused": len(self.outputs) - used_in_decisions
        }


# ============================================================================
# UNIFIED SAFEGUARD SYSTEM
# ============================================================================

class EpistemicSafeguardSystem:
    """
    Unified system managing all three epistemic safeguards.
    
    Ensures ATLAS Ω remains a tool, not an authority.
    """
    
    def __init__(self, audit_trail=None):
        """Initialize all safeguards."""
        self.audit_trail = audit_trail or get_audit_trail()
        
        # Initialize all three safeguards
        self.gravity_mitigation = EpistemicGravityMitigation(audit_trail)
        self.framing_guards = PromptFramingGuards(audit_trail)
        self.responsibility_enforcement = ResponsibilityBoundaryEnforcement(audit_trail)
        
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="epistemic_safeguard_system_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )
        
        logger.info("🛡️ Epistemic safeguard system active (all 3 safeguards)")
    
    def get_complete_status(self) -> Dict[str, Any]:
        """Get complete status of all safeguards."""
        # Check dissent pathway
        dissent_ok, dissent_msg = self.gravity_mitigation.verify_dissent_pathway()
        
        return {
            "safeguard_1_gravity_mitigation": self.gravity_mitigation.get_statistics(),
            "safeguard_2_framing_guards": self.framing_guards.get_statistics(),
            "safeguard_3_responsibility": self.responsibility_enforcement.get_statistics(),
            "dissent_pathway": {
                "is_open": dissent_ok,
                "message": dissent_msg
            },
            "overall_status": "OPERATIONAL"
        }


# Singleton instance
_safeguards = None


def get_epistemic_safeguards(audit_trail=None) -> EpistemicSafeguardSystem:
    """Get singleton epistemic safeguard system."""
    global _safeguards
    if _safeguards is None:
        _safeguards = EpistemicSafeguardSystem(audit_trail=audit_trail)
    return _safeguards
