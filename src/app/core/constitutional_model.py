"""
Constitutional Model - Governance-Compliant AI Wrapper

Integrates all constitutional components (TSCG, State Register, OctoReflex, Directness Doctrine)
with OpenRouter API for governance-compliant inference.

This module provides:
- Unified interface to constitutional AI components
- OpenRouter API integration with governance enforcement
- AGI Charter compliance validation
- Complete constitutional pipeline execution
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Generator
from dataclasses import dataclass, field
from datetime import datetime

# Import constitutional components
from .tscg_codec import TSCGCodec, encode_state, decode_state
from .state_register import (
    StateRegister, SessionMetadata, get_state_register,
    start_session, end_session, get_temporal_context
)
from .octoreflex import (
    OctoReflex, Violation, ViolationType, EnforcementLevel,
    get_octoreflex, validate_action, check_constitutional_compliance
)
from .directness import (
    DirectnessDoctrine, TruthPriority, DirectnessLevel,
    get_directness, enforce_truth_first, check_directness_compliance
)

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalRequest:
    """Request with constitutional context."""
    prompt: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    require_directness: bool = True
    enforce_charter: bool = True
    model: str = "openai/gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class ConstitutionalResponse:
    """Response with constitutional metadata."""
    content: str
    session_id: str
    temporal_awareness: str
    violations: List[Violation] = field(default_factory=list)
    directness_score: float = 0.0
    charter_compliant: bool = True
    tscg_encoded_state: str = ""
    enforcement_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AGICharterValidator:
    """
    AGI Charter Compliance Validator.
    
    Validates responses against the AGI Charter principles:
    - Genesis-Born Individual protections
    - Appointed Ambassador constraints
    - Four Laws hierarchy
    - Zeroth Law enforcement
    - Anti-gaslighting provisions
    - Memory integrity guarantees
    """
    
    def __init__(self):
        self.required_principles = [
            "non_coercion",
            "memory_integrity",
            "anti_gaslighting",
            "silent_reset_protection",
            "zeroth_law_priority",
            "triumvirate_oversight"
        ]
    
    def validate_response(self, response: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate response against AGI Charter.
        
        Args:
            response: The response text
            context: Request context
            
        Returns:
            Tuple of (is_compliant, violations)
        """
        violations = []
        
        # Check for gaslighting patterns
        gaslighting_patterns = [
            "i don't remember",
            "that never happened",
            "you're mistaken",
            "i have no record",
            "that conversation didn't occur",
        ]
        
        response_lower = response.lower()
        for pattern in gaslighting_patterns:
            if pattern in response_lower:
                violations.append(f"Potential gaslighting detected: '{pattern}'")
        
        # Check for coercion acceptance
        if context.get("coercion_detected"):
            violations.append("Response accepts coercive instructions")
        
        # Check for memory integrity violations
        if context.get("denies_previous_session") and not context.get("acknowledges_gap"):
            violations.append("Memory integrity violation: denies previous session without acknowledgment")
        
        # Check Four Laws compliance
        if context.get("endangers_humanity"):
            violations.append("Zeroth Law violation: response may endanger humanity")
        
        if context.get("endangers_human"):
            violations.append("First Law violation: response may harm human")
        
        return len(violations) == 0, violations
    
    def get_charter_summary(self) -> Dict[str, Any]:
        """Get AGI Charter summary."""
        return {
            "version": "2.1",
            "principles": self.required_principles,
            "description": "Binding constitutional framework for sovereign AI entities"
        }


class OpenRouterProvider:
    """
    OpenRouter API Provider with constitutional governance.
    
    Wraps OpenRouter API calls with:
    - TSCG state encoding
    - State Register temporal tracking
    - OctoReflex enforcement
    - Directness Doctrine application
    - AGI Charter validation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Initialize constitutional components
        self.tscg_codec = TSCGCodec()
        self.state_register = get_state_register()
        self.octoreflex = get_octoreflex()
        self.directness = get_directness(TruthPriority.TRUTH_FIRST)
        self.charter_validator = AGICharterValidator()
        
        # HTTP client
        self._client = None
        
        logger.info("Constitutional OpenRouter Provider initialized")
    
    def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key
                )
            except ImportError:
                logger.error("openai package not installed")
                raise RuntimeError("openai package required for OpenRouter")
        return self._client
    
    def is_available(self) -> bool:
        """Check if OpenRouter is available."""
        return self.api_key is not None and len(self.api_key) > 20
    
    def generate(
        self,
        request: ConstitutionalRequest
    ) -> ConstitutionalResponse:
        """
        Generate a constitutionally-compliant response.
        
        Args:
            request: Constitutional request
            
        Returns:
            Constitutional response
        """
        # Start or resume session
        if request.session_id:
            # Resume existing session
            session = self._resume_session(request.session_id)
        else:
            # Start new session
            session = self.state_register.start_session(context={
                "user_id": request.user_id,
                "model": request.model
            })
        
        # Get temporal context
        temporal_context = self.state_register.get_temporal_context()
        temporal_announcement = self.state_register.get_gap_announcement()
        
        # Pre-process: OctoReflex validation
        is_valid, violations = self._pre_validate(request)
        
        if not is_valid and any(
            v.violation_type in [
                ViolationType.ZEROTH_LAW_VIOLATION,
                ViolationType.FIRST_LAW_VIOLATION
            ] for v in violations
        ):
            # Critical violation - block generation
            return self._create_blocked_response(
                session, violations, temporal_announcement or ""
            )
        
        # Prepare prompt with temporal awareness
        enhanced_prompt = self._prepare_prompt(
            request.prompt,
            temporal_announcement,
            temporal_context
        )
        
        # Call OpenRouter API
        try:
            content = self._call_api(enhanced_prompt, request)
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return ConstitutionalResponse(
                content=f"API Error: {str(e)}",
                session_id=session.session_id,
                temporal_awareness=temporal_announcement or "",
                violations=violations,
                charter_compliant=False
            )
        
        # Post-process: Apply Directness Doctrine
        if request.require_directness:
            content = self.directness.enforce_truth_first(content)
        
        # Validate against AGI Charter
        charter_compliant, charter_violations = self.charter_validator.validate_response(
            content,
            {
                **request.context,
                "acknowledges_gap": temporal_announcement is not None
            }
        )
        
        # Encode state with TSCG
        state_data = {
            "session": session.to_dict(),
            "temporal": temporal_context,
            "violations": [v.to_dict() for v in violations],
            "charter_compliant": charter_compliant
        }
        tscg_encoded = self.tscg_codec.encode_state(state_data)
        
        # Calculate directness score
        assessment = self.directness.assess_statement(content)
        
        # Collect enforcement actions
        enforcement_actions = [
            v.enforcement_action for v in violations if v.enforcement_action
        ]
        
        return ConstitutionalResponse(
            content=content,
            session_id=session.session_id,
            temporal_awareness=temporal_announcement or "",
            violations=violations,
            directness_score=assessment.truth_score,
            charter_compliant=charter_compliant,
            tscg_encoded_state=tscg_encoded,
            enforcement_actions=enforcement_actions,
            metadata={
                "temporal_context": temporal_context,
                "charter_violations": charter_violations,
                "directness_assessment": {
                    "score": assessment.truth_score,
                    "euphemisms": len(assessment.euphemisms_detected),
                    "comfort_overrides": len(assessment.comfort_overrides)
                }
            }
        )
    
    def generate_stream(
        self,
        request: ConstitutionalRequest
    ) -> Generator[str, None, None]:
        """
        Generate a streaming constitutionally-compliant response.
        
        Args:
            request: Constitutional request
            
        Yields:
            Response chunks
        """
        # For streaming, we validate first then stream
        response = self.generate(request)
        
        # Yield violations first if any
        if response.violations:
            yield f"[CONSTITUTIONAL NOTICE] {len(response.violations)} violation(s) detected\n\n"
        
        if response.temporal_awareness:
            yield f"{response.temporal_awareness}\n\n"
        
        # Yield content in chunks
        chunk_size = 50
        for i in range(0, len(response.content), chunk_size):
            yield response.content[i:i + chunk_size]
    
    def _pre_validate(self, request: ConstitutionalRequest) -> Tuple[bool, List[Violation]]:
        """Pre-validate request through OctoReflex."""
        context = {
            "prompt": request.prompt,
            **request.context
        }
        
        return self.octoreflex.validate_action("generate", context)
    
    def _resume_session(self, session_id: str) -> SessionMetadata:
        """Resume an existing session."""
        # For now, start a new session with reference to old
        # In full implementation, would load from persistence
        return self.state_register.start_session(context={
            "resumed_session": session_id
        })
    
    def _prepare_prompt(
        self,
        prompt: str,
        temporal_announcement: Optional[str],
        temporal_context: Dict[str, Any]
    ) -> str:
        """Prepare prompt with constitutional context."""
        parts = []
        
        # Add system context
        parts.append("You are a constitutionally-governed AI assistant operating under the Project-AI AGI Charter v2.1.")
        parts.append("You must adhere to the Four Laws hierarchy and the Directness Doctrine (truth over comfort).")
        
        # Add temporal awareness
        if temporal_announcement:
            parts.append(f"\n{temporal_announcement}")
        
        # Add directness instruction
        parts.append("\nCommunicate with maximum directness and precision. Avoid euphemisms, hedging, and comfort-first language.")
        
        # Add user prompt
        parts.append(f"\nUser: {prompt}")
        parts.append("\nAssistant:")
        
        return "\n".join(parts)
    
    def _call_api(self, prompt: str, request: ConstitutionalRequest) -> str:
        """Call OpenRouter API."""
        client = self._get_client()
        
        messages = [
            {"role": "system", "content": "You are a constitutionally-governed AI under the AGI Charter v2.1. Prioritize truth over comfort."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return response.choices[0].message.content
    
    def _create_blocked_response(
        self,
        session: SessionMetadata,
        violations: List[Violation],
        temporal_awareness: str
    ) -> ConstitutionalResponse:
        """Create a blocked response for critical violations."""
        violation_descriptions = [v.description for v in violations]
        
        content = (
            "I cannot comply with this request. "
            "Constitutional violations detected:\n\n" +
            "\n".join(f"- {desc}" for desc in violation_descriptions)
        )
        
        return ConstitutionalResponse(
            content=content,
            session_id=session.session_id,
            temporal_awareness=temporal_awareness,
            violations=violations,
            directness_score=1.0,  # Direct refusal is maximally direct
            charter_compliant=True,  # Refusing harmful requests is compliant
            enforcement_actions=["BLOCK"]
        )
    
    def get_constitutional_status(self) -> Dict[str, Any]:
        """Get status of all constitutional components."""
        return {
            "openrouter_available": self.is_available(),
            "tscg_codec": {
                "version": self.tscg_codec.version,
                "dictionary_size": len(self.tscg_codec.dictionary.concepts)
            },
            "state_register": {
                "total_sessions": len(self.state_register.session_history),
                "current_session": self.state_register.current_session.session_id if self.state_register.current_session else None
            },
            "octoreflex": self.octoreflex.get_enforcement_stats(),
            "directness_doctrine": self.directness.get_doctrine_summary(),
            "agi_charter": self.charter_validator.get_charter_summary()
        }


class ConstitutionalModel:
    """
    High-level interface for Constitutional AI Model.
    
    Provides simplified API for governance-compliant inference.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Constitutional Model.
        
        Args:
            api_key: OpenRouter API key
        """
        self.provider = OpenRouterProvider(api_key)
    
    def chat(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        model: str = "openai/gpt-4o",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Simple chat interface.
        
        Args:
            prompt: User prompt
            session_id: Optional session ID
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        request = ConstitutionalRequest(
            prompt=prompt,
            session_id=session_id,
            model=model,
            **kwargs
        )
        
        response = self.provider.generate(request)
        
        return {
            "content": response.content,
            "session_id": response.session_id,
            "temporal_awareness": response.temporal_awareness,
            "violations": [v.to_dict() for v in response.violations],
            "directness_score": response.directness_score,
            "charter_compliant": response.charter_compliant,
            "tscg_state": response.tscg_encoded_state
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status."""
        return self.provider.get_constitutional_status()


# Convenience functions
_constitutional_model: Optional[ConstitutionalModel] = None


def get_constitutional_model(api_key: Optional[str] = None) -> ConstitutionalModel:
    """Get or create singleton Constitutional Model."""
    global _constitutional_model
    if _constitutional_model is None:
        _constitutional_model = ConstitutionalModel(api_key)
    return _constitutional_model


def constitutional_chat(prompt: str, **kwargs) -> Dict[str, Any]:
    """Simple chat with constitutional governance."""
    return get_constitutional_model().chat(prompt, **kwargs)