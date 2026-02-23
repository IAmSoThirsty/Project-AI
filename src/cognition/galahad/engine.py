"""
Galahad Engine - Reasoning and Arbitration

Provides reasoning abstraction with:
- Logical inference and decision-making
- Arbitration between conflicting inputs
- Curiosity metrics for exploration
- Explanation generation
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GalahadConfig:
    """Configuration for Galahad engine."""

    reasoning_depth: int = 3
    enable_curiosity: bool = True
    curiosity_threshold: float = 0.5
    arbitration_strategy: str = "weighted"  # 'weighted', 'unanimous', 'majority'


class GalahadEngine:
    """
    Reasoning and arbitration engine.

    Handles:
    - Multi-step reasoning chains
    - Conflict resolution between sources
    - Curiosity-driven exploration
    - Explanation generation
    """

    def __init__(
        self,
        config: GalahadConfig | None = None,
        reasoning_matrix=None,
    ):
        """
        Initialize Galahad engine.

        Args:
            config: Engine configuration
            reasoning_matrix: Optional ReasoningMatrix for formalized
                reasoning traces.
        """
        self.config = config or GalahadConfig()
        self.curiosity_score = 0.0
        self.reasoning_history: list[dict] = []
        self._matrix = reasoning_matrix

        logger.info("Galahad engine initialized")
        logger.info("Config: %s", self.config)

    def reason(self, inputs: list[Any], context: dict | None = None) -> dict:
        """
        Perform reasoning over multiple inputs.

        Args:
            inputs: List of input data to reason over
            context: Optional context dictionary

        Returns:
            Reasoning result with explanation
        """
        logger.info("Reasoning over %s inputs", len(inputs))

        # Begin reasoning trace
        rm_entry_id = None
        if self._matrix:
            rm_entry_id = self._matrix.begin_reasoning(
                "galahad_reasoning",
                {"input_count": len(inputs), "depth": self.config.reasoning_depth},
            )

        try:
            # Step 1: Analyze inputs
            analyses = self._analyze_inputs(inputs, context)

            # Record each analysis as a factor
            if self._matrix and rm_entry_id:
                for analysis in analyses:
                    conf = analysis["confidence"]
                    self._matrix.add_factor(
                        rm_entry_id,
                        f"input_{analysis['index']}_analysis",
                        analysis["type"],
                        weight=conf,
                        score=conf,
                        source="galahad",
                        rationale=f"Input {analysis['index']} analyzed with confidence {conf:.2f}",
                    )

            # Step 2: Detect contradictions
            contradictions = self._detect_contradictions(analyses)

            # Record contradictions as factors
            if self._matrix and rm_entry_id and contradictions:
                self._matrix.add_factor(
                    rm_entry_id,
                    "contradictions_detected",
                    len(contradictions),
                    weight=0.8,
                    score=max(0.0, 1.0 - len(contradictions) * 0.3),
                    source="galahad",
                    rationale=f"{len(contradictions)} contradiction(s) detected between inputs",
                )

            # Step 3: Arbitrate if needed
            if contradictions:
                result = self._arbitrate(analyses, contradictions)
                strategy_used = self.config.arbitration_strategy
            else:
                result = self._synthesize(analyses)
                strategy_used = "synthesis"

            # Record strategy as factor
            if self._matrix and rm_entry_id:
                self._matrix.add_factor(
                    rm_entry_id,
                    "resolution_strategy",
                    strategy_used,
                    weight=0.6,
                    score=0.8 if not contradictions else 0.6,
                    source="galahad",
                    rationale=f"Used '{strategy_used}' to {'resolve conflicts' if contradictions else 'synthesize'}",
                )

            # Step 4: Update curiosity
            if self.config.enable_curiosity:
                self._update_curiosity(result)
                # Record curiosity as factor
                if self._matrix and rm_entry_id:
                    self._matrix.add_factor(
                        rm_entry_id,
                        "curiosity_signal",
                        self.curiosity_score,
                        weight=0.3,
                        score=self.curiosity_score,
                        source="galahad",
                        rationale=f"Curiosity {'high — exploration recommended' if self.curiosity_score >= self.config.curiosity_threshold else 'normal'}",
                    )

            # Step 5: Generate explanation
            explanation = self._generate_explanation(result, contradictions)

            # Render verdict
            confidence = 0.7
            if analyses:
                confidence = max(a["confidence"] for a in analyses)
            if self._matrix and rm_entry_id:
                self._matrix.render_verdict(
                    rm_entry_id,
                    decision="synthesized" if not contradictions else "arbitrated",
                    confidence=confidence,
                    explanation=explanation,
                )

            # Record in history
            reasoning_record = {
                "inputs": inputs,
                "analyses": analyses,
                "contradictions": contradictions,
                "result": result,
                "explanation": explanation,
                "context": context or {},
                "reasoning_entry_id": rm_entry_id,
            }
            self.reasoning_history.append(reasoning_record)

            return {
                "success": True,
                "conclusion": result,
                "explanation": explanation,
                "contradictions": contradictions,
                "curiosity_score": self.curiosity_score,
                "confidence": confidence,
                "reasoning_entry_id": rm_entry_id,
                "metadata": {
                    "depth": self.config.reasoning_depth,
                    "context": context or {},
                },
            }

        except Exception as e:
            logger.error("Reasoning error: %s", e)
            if self._matrix and rm_entry_id:
                try:
                    self._matrix.render_verdict(
                        rm_entry_id,
                        decision="error",
                        confidence=0.0,
                        explanation=f"Reasoning failed: {e}",
                    )
                except ValueError:
                    pass
            return {
                "success": False,
                "error": str(e),
                "conclusion": None,
                "explanation": f"Reasoning failed: {e}",
            }

    def arbitrate(self, conflicting_inputs: list[dict]) -> dict:
        """
        Arbitrate between conflicting inputs.

        Args:
            conflicting_inputs: List of conflicting input dictionaries

        Returns:
            Arbitration decision
        """
        logger.info("Arbitrating %s conflicting inputs", len(conflicting_inputs))

        if not conflicting_inputs:
            return {"decision": None, "reason": "No inputs to arbitrate"}

        strategy = self.config.arbitration_strategy

        if strategy == "weighted":
            return self._weighted_arbitration(conflicting_inputs)
        elif strategy == "majority":
            return self._majority_arbitration(conflicting_inputs)
        elif strategy == "unanimous":
            return self._unanimous_arbitration(conflicting_inputs)
        else:
            return self._weighted_arbitration(conflicting_inputs)

    def get_curiosity_metrics(self) -> dict:
        """Get current curiosity metrics."""
        return {
            "current_score": self.curiosity_score,
            "enabled": self.config.enable_curiosity,
            "threshold": self.config.curiosity_threshold,
            "should_explore": self.curiosity_score >= self.config.curiosity_threshold,
        }

    def get_reasoning_history(self, limit: int = 10) -> list[dict]:
        """Get recent reasoning history."""
        return self.reasoning_history[-limit:]

    def clear_history(self):
        """Clear reasoning history."""
        self.reasoning_history = []
        logger.info("Reasoning history cleared")

    # Private methods

    def _analyze_inputs(self, inputs: list[Any], context: dict | None) -> list[dict]:
        """Analyze each input."""
        analyses = []
        for i, inp in enumerate(inputs):
            analysis = {
                "index": i,
                "input": inp,
                "type": type(inp).__name__,
                "confidence": self._estimate_confidence(inp),
                "context": context or {},
            }
            analyses.append(analysis)
        return analyses

    def _detect_contradictions(self, analyses: list[dict]) -> list[dict]:
        """Detect contradictions between analyses."""
        contradictions = []

        # Simple contradiction detection: compare pairwise
        for i in range(len(analyses)):
            for j in range(i + 1, len(analyses)):
                if self._are_contradictory(analyses[i], analyses[j]):
                    contradictions.append(
                        {
                            "index1": i,
                            "index2": j,
                            "description": f"Contradiction between input {i} and {j}",
                        }
                    )

        if contradictions:
            logger.warning("Detected %s contradictions", len(contradictions))

        return contradictions

    def _are_contradictory(self, analysis1: dict, analysis2: dict) -> bool:
        """Check if two analyses are contradictory."""
        # Simplified: check if inputs are opposite or incompatible
        inp1 = str(analysis1["input"]).lower()
        inp2 = str(analysis2["input"]).lower()

        # Look for opposite keywords
        opposites = [
            ("yes", "no"),
            ("true", "false"),
            ("allow", "deny"),
            ("safe", "unsafe"),
        ]

        for pos, neg in opposites:
            if (pos in inp1 and neg in inp2) or (neg in inp1 and pos in inp2):
                return True

        return False

    def _arbitrate(self, analyses: list[dict], contradictions: list[dict]) -> Any:
        """Arbitrate when contradictions exist."""
        logger.info("Performing arbitration")
        return self.arbitrate([a["input"] for a in analyses])["decision"]

    def _synthesize(self, analyses: list[dict]) -> Any:
        """Synthesize when no contradictions exist."""
        # Simple synthesis: return most confident input
        if not analyses:
            return None

        most_confident = max(analyses, key=lambda a: a["confidence"])
        return most_confident["input"]

    def _weighted_arbitration(self, inputs: list[dict]) -> dict:
        """Weighted arbitration based on confidence."""
        if not inputs:
            return {"decision": None, "reason": "No inputs"}

        # Assign weights based on confidence or order
        weights = [
            inp.get("confidence", 1.0) if isinstance(inp, dict) else 1.0
            for inp in inputs
        ]

        total_weight = sum(weights)
        if total_weight == 0:
            return {"decision": inputs[0], "reason": "All weights zero, using first"}

        # Select input with highest weight
        max_idx = weights.index(max(weights))
        return {
            "decision": inputs[max_idx],
            "reason": f"Highest weight ({weights[max_idx]}/{total_weight})",
        }

    def _majority_arbitration(self, inputs: list[dict]) -> dict:
        """Majority voting arbitration."""
        from collections import Counter

        if not inputs:
            return {"decision": None, "reason": "No inputs"}

        # Count occurrences
        str_inputs = [str(inp) for inp in inputs]
        counter = Counter(str_inputs)
        most_common = counter.most_common(1)[0]

        return {
            "decision": most_common[0],
            "reason": f"Majority vote ({most_common[1]}/{len(inputs)})",
        }

    def _unanimous_arbitration(self, inputs: list[dict]) -> dict:
        """Unanimous arbitration (all must agree)."""
        if not inputs:
            return {"decision": None, "reason": "No inputs"}

        # Check if all are the same
        first = str(inputs[0])
        if all(str(inp) == first for inp in inputs):
            return {"decision": inputs[0], "reason": "Unanimous agreement"}

        return {"decision": None, "reason": "No unanimous agreement"}

    def _estimate_confidence(self, input_data: Any) -> float:
        """Estimate confidence in input."""
        # Simplified: base on input characteristics
        if isinstance(input_data, dict) and "confidence" in input_data:
            return float(input_data["confidence"])
        return 0.7  # Default moderate confidence

    def _update_curiosity(self, result: Any):
        """Update curiosity score based on result."""
        # Increase curiosity for novel or uncertain results
        if result is None or str(result).lower() in ["unknown", "uncertain"]:
            self.curiosity_score = min(1.0, self.curiosity_score + 0.1)
        else:
            # Decay curiosity slightly
            self.curiosity_score = max(0.0, self.curiosity_score - 0.05)

    def _generate_explanation(self, result: Any, contradictions: list[dict]) -> str:
        """Generate human-readable explanation."""
        if contradictions:
            return (
                f"Resolved {len(contradictions)} contradiction(s) "
                f"using {self.config.arbitration_strategy} strategy. "
                f"Conclusion: {result}"
            )
        else:
            return f"No contradictions detected. Synthesized conclusion: {result}"
