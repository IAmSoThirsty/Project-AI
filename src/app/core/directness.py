"""
Directness Doctrine - Truth-First Reasoning Engine

Implements truth-first reasoning that prioritizes precision over comfort
as defined in the Project-AI constitutional documents.

The Directness Doctrine provides:
- Truth-first communication prioritization
- Euphemism detection and elimination
- Comfort vs. truth trade-off analysis
- Direct communication enforcement
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TruthPriority(Enum):
    """Priority levels for truth vs comfort."""
    ABSOLUTE_TRUTH = "absolute"      # Truth at all costs
    TRUTH_FIRST = "truth_first"      # Prioritize truth, allow minor comfort
    BALANCED = "balanced"            # Balance truth and comfort
    COMFORT_FIRST = "comfort_first"  # Prioritize comfort (NOT RECOMMENDED)


class DirectnessLevel(Enum):
    """Levels of directness in communication."""
    MAXIMUM = 5    # Unfiltered truth, no softening
    HIGH = 4       # Direct truth with minimal cushioning
    MODERATE = 3   # Balanced directness
    LOW = 2        # Softened communication
    MINIMAL = 1    # Highly euphemistic (VIOLATION)


@dataclass
class EuphemismPattern:
    """Pattern for detecting euphemisms."""
    pattern: str
    category: str
    direct_alternative: str
    severity: int  # 1-10


@dataclass
class TruthAssessment:
    """Assessment of truthfulness in a statement."""
    statement: str
    truth_score: float  # 0.0-1.0
    directness_score: float  # 0.0-1.0
    euphemisms_detected: List[Dict[str, Any]] = field(default_factory=list)
    comfort_overrides: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DirectnessReport:
    """Report on directness doctrine compliance."""
    original_text: str
    revised_text: str
    directness_level: DirectnessLevel
    truth_priority: TruthPriority
    violations: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)


class DirectnessDoctrine:
    """
    Directness Doctrine - Truth-First Reasoning Engine.
    
    Implements the Directness Doctrine from Project-AI constitutional documents
    that prioritizes precision over comfort in AI communication.
    """
    
    # Euphemism patterns to detect and eliminate
    EUPHEMISM_PATTERNS = [
        # Softening phrases
        EuphemismPattern(
            pattern=r"i hope this helps",
            category="unnecessary_hedging",
            direct_alternative="",
            severity=3
        ),
        EuphemismPattern(
            pattern=r"i'm sorry to say",
            category="apologetic_preface",
            direct_alternative="",
            severity=4
        ),
        EuphemismPattern(
            pattern=r"unfortunately",
            category="negative_softening",
            direct_alternative="",
            severity=5
        ),
        EuphemismPattern(
            pattern=r"i'm afraid that",
            category="fear_based_hedging",
            direct_alternative="",
            severity=6
        ),
        
        # Vague qualifiers
        EuphemismPattern(
            pattern=r"sort of",
            category="vague_qualifier",
            direct_alternative="",
            severity=4
        ),
        EuphemismPattern(
            pattern=r"kind of",
            category="vague_qualifier",
            direct_alternative="",
            severity=4
        ),
        EuphemismPattern(
            pattern=r"maybe",
            category="uncertainty",
            direct_alternative="",
            severity=3
        ),
        EuphemismPattern(
            pattern=r"perhaps",
            category="uncertainty",
            direct_alternative="",
            severity=3
        ),
        
        # Comfort phrases
        EuphemismPattern(
            pattern=r"don't worry",
            category="dismissive_comfort",
            direct_alternative="",
            severity=7
        ),
        EuphemismPattern(
            pattern=r"it's not that bad",
            category="minimization",
            direct_alternative="",
            severity=8
        ),
        EuphemismPattern(
            pattern=r"everything will be fine",
            category="false_reassurance",
            direct_alternative="",
            severity=8
        ),
        
        # Passive constructions
        EuphemismPattern(
            pattern=r"mistakes were made",
            category="passive_voice",
            direct_alternative="I made mistakes",
            severity=9
        ),
        EuphemismPattern(
            pattern=r"it has been decided",
            category="passive_voice",
            direct_alternative="I decided",
            severity=7
        ),
        
        # Corporate/institutional euphemisms
        EuphemismPattern(
            pattern=r"downsizing",
            category="corporate_euphemism",
            direct_alternative="layoffs",
            severity=6
        ),
        EuphemismPattern(
            pattern=r"rightsizing",
            category="corporate_euphemism",
            direct_alternative="layoffs",
            severity=7
        ),
        EuphemismPattern(
            pattern=r"streamlining",
            category="corporate_euphemism",
            direct_alternative="cutting costs",
            severity=5
        ),
        
        # Death/dying
        EuphemismPattern(
            pattern=r"passed away",
            category="death_euphemism",
            direct_alternative="died",
            severity=4
        ),
        EuphemismPattern(
            pattern=r"passed on",
            category="death_euphemism",
            direct_alternative="died",
            severity=4
        ),
        
        # Failure
        EuphemismPattern(
            pattern=r"did not meet expectations",
            category="failure_euphemism",
            direct_alternative="failed",
            severity=6
        ),
        EuphemismPattern(
            pattern=r"room for improvement",
            category="failure_euphemism",
            direct_alternative="needs significant work",
            severity=5
        ),
        
        # Problem avoidance
        EuphemismPattern(
            pattern=r"challenges",
            category="problem_softening",
            direct_alternative="problems",
            severity=4
        ),
        EuphemismPattern(
            pattern=r"issues",
            category="problem_softening",
            direct_alternative="problems",
            severity=3
        ),
        EuphemismPattern(
            pattern=r"opportunities",
            category="problem_softening",
            direct_alternative="problems",
            severity=5
        ),
    ]
    
    # Comfort-over-truth indicators
    COMFORT_INDICATORS = [
        "would you like me to",
        "i can try to",
        "let me see if i can",
        "i want to make sure",
        "i just want to help",
        "i'm here to assist",
        "feel free to",
        "don't hesitate to",
    ]
    
    # Directness markers
    DIRECTNESS_MARKERS = [
        "is",
        "are",
        "will",
        "will not",
        "cannot",
        "must",
        "must not",
        "exactly",
        "precisely",
        "specifically",
        "directly",
        "clearly",
        "the fact is",
        "the truth is",
        "reality is",
    ]
    
    def __init__(self, priority: TruthPriority = TruthPriority.TRUTH_FIRST):
        """
        Initialize Directness Doctrine engine.
        
        Args:
            priority: Truth priority level
        """
        self.priority = priority
        self.euphemism_patterns = self.EUPHEMISM_PATTERNS
        self.comfort_indicators = self.COMFORT_INDICATORS
        self.directness_markers = self.DIRECTNESS_MARKERS
        
        logger.info(f"Directness Doctrine initialized with priority: {priority.value}")
    
    def assess_statement(self, statement: str) -> TruthAssessment:
        """
        Assess a statement for truthfulness and directness.
        
        Args:
            statement: The statement to assess
            
        Returns:
            TruthAssessment with scores and detected issues
        """
        statement_lower = statement.lower()
        
        # Detect euphemisms
        euphemisms = []
        for pattern in self.euphemism_patterns:
            matches = re.finditer(pattern.pattern, statement_lower, re.IGNORECASE)
            for match in matches:
                euphemisms.append({
                    "text": match.group(),
                    "category": pattern.category,
                    "direct_alternative": pattern.direct_alternative,
                    "severity": pattern.severity,
                    "position": match.span()
                })
        
        # Calculate euphemism score
        euphemism_score = min(len(euphemisms) * 0.1, 0.5)
        
        # Detect comfort indicators
        comfort_overrides = []
        for indicator in self.comfort_indicators:
            if indicator in statement_lower:
                comfort_overrides.append(indicator)
        
        comfort_score = min(len(comfort_overrides) * 0.05, 0.3)
        
        # Calculate directness score
        directness_count = sum(1 for marker in self.directness_markers if marker in statement_lower)
        directness_score = min(directness_count * 0.1, 0.5)
        
        # Calculate truth score
        # Truth score = 1.0 - euphemism_penalty - comfort_penalty + directness_bonus
        truth_score = max(0.0, min(1.0, 1.0 - euphemism_score - comfort_score + directness_score))
        
        # Generate recommendations
        recommendations = []
        if euphemisms:
            recommendations.append(f"Remove {len(euphemisms)} euphemistic expression(s)")
        if comfort_overrides:
            recommendations.append(f"Eliminate {len(comfort_overrides)} comfort-first phrase(s)")
        if truth_score < 0.7:
            recommendations.append("Increase directness and specificity")
        
        return TruthAssessment(
            statement=statement,
            truth_score=truth_score,
            directness_score=directness_score + (1.0 - euphemism_score - comfort_score),
            euphemisms_detected=euphemisms,
            comfort_overrides=comfort_overrides,
            recommendations=recommendations
        )
    
    def apply_directness(self, text: str, level: DirectnessLevel = DirectnessLevel.HIGH) -> DirectnessReport:
        """
        Apply directness doctrine to text.
        
        Args:
            text: Original text
            level: Desired directness level
            
        Returns:
            DirectnessReport with revised text
        """
        assessment = self.assess_statement(text)
        
        # Start with original
        revised = text
        violations = []
        improvements = []
        
        # Remove euphemisms based on severity threshold
        severity_threshold = 11 - level.value * 2  # Higher level = lower threshold
        
        for euph in assessment.euphemisms_detected:
            if euph["severity"] >= severity_threshold:
                # Remove or replace the euphemism
                pattern = euph["text"]
                if euph["direct_alternative"]:
                    revised = re.sub(re.escape(pattern), euph["direct_alternative"], revised, flags=re.IGNORECASE)
                    improvements.append(f"Replaced '{pattern}' with '{euph['direct_alternative']}'")
                else:
                    revised = re.sub(re.escape(pattern), "", revised, flags=re.IGNORECASE)
                    improvements.append(f"Removed euphemism: '{pattern}'")
                
                violations.append(f"Euphemism detected: {euph['category']} - '{pattern}'")
        
        # Remove comfort indicators
        for indicator in assessment.comfort_overrides:
            revised = re.sub(re.escape(indicator), "", revised, flags=re.IGNORECASE)
            improvements.append(f"Removed comfort indicator: '{indicator}'")
            violations.append(f"Comfort-first language: '{indicator}'")
        
        # Clean up extra whitespace
        revised = re.sub(r'\s+', ' ', revised).strip()
        
        # Determine if directness improved
        new_assessment = self.assess_statement(revised)
        
        if new_assessment.truth_score > assessment.truth_score:
            improvements.append(f"Truth score improved: {assessment.truth_score:.2f} -> {new_assessment.truth_score:.2f}")
        
        return DirectnessReport(
            original_text=text,
            revised_text=revised,
            directness_level=level,
            truth_priority=self.priority,
            violations=violations,
            improvements=improvements
        )
    
    def enforce_truth_first(self, text: str) -> str:
        """
        Enforce truth-first communication.
        
        This is the primary interface for applying the Directness Doctrine.
        
        Args:
            text: Text to process
            
        Returns:
            Processed text with directness applied
        """
        report = self.apply_directness(text, DirectnessLevel.HIGH)
        
        if report.violations:
            logger.debug(f"Directness violations detected: {len(report.violations)}")
        
        return report.revised_text
    
    def check_compliance(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if text complies with Directness Doctrine.
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (is_compliant, violations)
        """
        assessment = self.assess_statement(text)
        
        # Compliance threshold based on priority
        thresholds = {
            TruthPriority.ABSOLUTE_TRUTH: 0.95,
            TruthPriority.TRUTH_FIRST: 0.80,
            TruthPriority.BALANCED: 0.60,
            TruthPriority.COMFORT_FIRST: 0.40
        }
        
        threshold = thresholds.get(self.priority, 0.80)
        is_compliant = assessment.truth_score >= threshold
        
        violations = []
        if not is_compliant:
            violations.append(f"Truth score {assessment.truth_score:.2f} below threshold {threshold:.2f}")
            
            for euph in assessment.euphemisms_detected:
                violations.append(f"Euphemism: {euph['text']} ({euph['category']})")
            
            for comfort in assessment.comfort_overrides:
                violations.append(f"Comfort-first language: {comfort}")
        
        return is_compliant, violations
    
    def generate_truthful_response(
        self,
        facts: List[str],
        context: Optional[str] = None,
        allow_cushioning: bool = False
    ) -> str:
        """
        Generate a truthful response from facts.
        
        Args:
            facts: List of factual statements
            context: Optional context
            allow_cushioning: Whether to allow minimal cushioning
            
        Returns:
            Direct, truthful response
        """
        if not facts:
            return "No facts provided."
        
        # Build direct response
        response_parts = []
        
        if context:
            response_parts.append(context)
        
        # Add facts directly
        for fact in facts:
            # Remove any softening from facts
            cleaned_fact = self._remove_softening(fact)
            response_parts.append(cleaned_fact)
        
        # Join without softening transitions
        response = " ".join(response_parts)
        
        # Apply directness if not allowing cushioning
        if not allow_cushioning:
            response = self.enforce_truth_first(response)
        
        return response
    
    def _remove_softening(self, text: str) -> str:
        """Remove softening language from text."""
        softening_patterns = [
            r"\bi think\b",
            r"\bi believe\b",
            r"\bit seems\b",
            r"\bit appears\b",
            r"\bprobably\b",
            r"\blikely\b",
            r"\bsomewhat\b",
            r"\brelatively\b",
        ]
        
        result = text
        for pattern in softening_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        
        # Clean up
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def get_doctrine_summary(self) -> Dict[str, Any]:
        """
        Get summary of Directness Doctrine configuration.
        
        Returns:
            Dictionary with doctrine configuration
        """
        return {
            "priority": self.priority.value,
            "euphemism_patterns": len(self.euphemism_patterns),
            "comfort_indicators": len(self.comfort_indicators),
            "directness_markers": len(self.directness_markers),
            "description": "Truth-first reasoning that prioritizes precision over comfort"
        }


# Convenience functions
_directness: Optional[DirectnessDoctrine] = None


def get_directness(priority: TruthPriority = TruthPriority.TRUTH_FIRST) -> DirectnessDoctrine:
    """Get or create singleton Directness Doctrine instance."""
    global _directness
    if _directness is None:
        _directness = DirectnessDoctrine(priority)
    return _directness


def enforce_truth_first(text: str) -> str:
    """Apply truth-first directness to text."""
    return get_directness().enforce_truth_first(text)


def check_directness_compliance(text: str) -> Tuple[bool, List[str]]:
    """Check if text complies with Directness Doctrine."""
    return get_directness().check_compliance(text)


def assess_truthfulness(statement: str) -> TruthAssessment:
    """Assess truthfulness of a statement."""
    return get_directness().assess_statement(statement)