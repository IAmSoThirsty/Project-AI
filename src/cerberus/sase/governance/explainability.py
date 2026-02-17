"""
SASE Explainability Module

Provides SOC-facing explanations for confidence scores.

CRITICAL: SOC trust collapses if scores are opaque.

OUTPUT:
- Top 3 feature contributions
- HMM state path
- Bayesian posterior breakdown
- Threat classification rationale
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class FeatureContribution:
    """Individual feature contribution to confidence score"""

    feature_name: str
    value: Any
    weight: float
    contribution_percentage: float
    interpretation: str


@dataclass
class ExplainabilityReport:
    """
    Complete explanation of threat detection decision

    SOC-facing output for human review
    """

    event_id: str
    final_confidence: float
    verdict: str  # "CONTAINED", "MONITORED", "ALLOWED"

    # Feature contributions (sorted by impact)
    top_features: List[FeatureContribution]

    # HMM state sequence
    hmm_state_path: List[str]

    # Bayesian breakdown
    prior_confidence: float
    likelihood_boost: float
    posterior_confidence: float

    # Threat classification
    actor_class: str
    actor_probability: float

    # Summary for SOC
    human_summary: str


class ExplainabilityEngine:
    """
    Generates explainability reports for SOC operators

    Translates technical scores into actionable intelligence
    """

    def __init__(self):
        # Feature importance weights (learned from training data)
        self.feature_weights = {
            "Tor_flag": 0.25,
            "Token_sensitivity": 0.20,
            "VPS_flag": 0.15,
            "ASN_risk": 0.12,
            "Historical_reuse_count": 0.10,
            "Geo_anomaly_score": 0.08,
            "Infrastructure_entropy": 0.05,
            "Time_of_day_deviation": 0.03,
            "NAT_density_estimate": 0.02,
        }

    def explain(
        self,
        event_id: str,
        feature_vector: Dict[str, Any],
        confidence_assessment: Dict[str, Any],
        hmm_state: str,
        threat_class: Dict[str, Any],
    ) -> ExplainabilityReport:
        """
        Generate comprehensive explainability report

        Args:
            event_id: Event identifier
            feature_vector: Attribution features
            confidence_assessment: Bayesian confidence output
            hmm_state: Current behavioral state
            threat_class: Threat actor classification

        Returns:
            ExplainabilityReport for SOC review
        """
        # 1. Calculate feature contributions
        top_features = self._rank_feature_contributions(
            feature_vector, confidence_assessment["confidence_score"]
        )

        # 2. Extract HMM state path (simplified - in production, track full sequence)
        hmm_state_path = [hmm_state]

        # 3. Bayesian breakdown
        prior = confidence_assessment.get("prior_confidence", 0.5)
        posterior = confidence_assessment["confidence_score"]
        likelihood_boost = posterior - prior

        # 4. Verdict determination
        confidence_pct = confidence_assessment["confidence_percentage"]
        if confidence_pct >= 50:
            verdict = "CONTAINED"
        elif confidence_pct >= 30:
            verdict = "MONITORED"
        else:
            verdict = "ALLOWED"

        # 5. Generate human summary
        human_summary = self._generate_summary(
            confidence_pct, top_features, hmm_state, threat_class
        )

        return ExplainabilityReport(
            event_id=event_id,
            final_confidence=posterior,
            verdict=verdict,
            top_features=top_features[:3],  # Top 3 only
            hmm_state_path=hmm_state_path,
            prior_confidence=prior,
            likelihood_boost=likelihood_boost,
            posterior_confidence=posterior,
            actor_class=threat_class.get("primary_class", "UNKNOWN"),
            actor_probability=threat_class.get("confidence", 0.0),
            human_summary=human_summary,
        )

    def _rank_feature_contributions(
        self, feature_vector: Dict[str, Any], final_confidence: float
    ) -> List[FeatureContribution]:
        """
        Rank features by contribution to final confidence

        Uses feature weights and activation values
        """
        contributions = []

        for feature_name, value in feature_vector.items():
            weight = self.feature_weights.get(feature_name, 0.0)

            # Calculate contribution (simplified SHAP-like approach)
            if isinstance(value, bool):
                activation = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                activation = min(float(value), 1.0)
            else:
                activation = 0.0

            contribution = weight * activation * final_confidence
            contribution_pct = (
                (contribution / final_confidence * 100) if final_confidence > 0 else 0.0
            )

            interpretation = self._interpret_feature(feature_name, value)

            contributions.append(
                FeatureContribution(
                    feature_name=feature_name,
                    value=value,
                    weight=weight,
                    contribution_percentage=contribution_pct,
                    interpretation=interpretation,
                )
            )

        # Sort by contribution (descending)
        contributions.sort(key=lambda x: x.contribution_percentage, reverse=True)

        return contributions

    def _interpret_feature(self, feature_name: str, value: Any) -> str:
        """Generate human-readable interpretation of feature value"""

        interpretations = {
            "Tor_flag": {True: "🔴 Tor exit node detected", False: "✓ Not using Tor"},
            "VPS_flag": {
                True: "⚠️  Cloud/VPS infrastructure",
                False: "✓ Residential/corporate IP",
            },
            "Token_sensitivity": lambda v: f"🔑 Token reuse: {v*100:.0f}% suspicious",
            "ASN_risk": lambda v: f"🌐 ASN risk: {v*100:.0f}%",
            "Geo_anomaly_score": lambda v: f"🌍 Geographic anomaly: {v*100:.0f}%",
            "Historical_reuse_count": lambda v: f"📊 Seen {v} times before",
        }

        interp = interpretations.get(feature_name)

        if isinstance(interp, dict):
            return interp.get(value, f"{feature_name}: {value}")
        elif callable(interp):
            return interp(value)
        else:
            return f"{feature_name}: {value}"

    def _generate_summary(
        self,
        confidence_pct: float,
        top_features: List[FeatureContribution],
        hmm_state: str,
        threat_class: Dict[str, Any],
    ) -> str:
        """
        Generate human-readable summary for SOC

        Example:
        "HIGH confidence (85%) adversarial activity detected. Primary indicators:
        Tor exit node, high token reuse (90%), unusual geographic pattern.
        Behavioral state: EXPLOITATION. Classified as CREDENTIAL_HARVESTING_BOT."
        """
        # Confidence level
        if confidence_pct >= 75:
            conf_level = "HIGH"
        elif confidence_pct >= 50:
            conf_level = "MEDIUM"
        elif confidence_pct >= 30:
            conf_level = "LOW"
        else:
            conf_level = "MINIMAL"

        # Top indicators
        indicators = []
        for feat in top_features[:3]:
            if feat.contribution_percentage > 5.0:  # Only meaningful contributors
                indicators.append(feat.interpretation)

        indicators_str = ", ".join(indicators) if indicators else "No strong indicators"

        # Actor class
        actor = threat_class.get("primary_class", "UNKNOWN")

        summary = (
            f"{conf_level} confidence ({confidence_pct:.0f}%) adversarial activity detected. "
            f"Primary indicators: {indicators_str}. "
            f"Behavioral state: {hmm_state}. "
            f"Classified as {actor}."
        )

        return summary

    def format_for_soc(self, report: ExplainabilityReport) -> str:
        """
        Format report for SOC dashboard display

        Returns multi-line string suitable for logging/display
        """
        lines = [
            f"=" * 60,
            f"THREAT DETECTION EXPLANATION - {report.event_id}",
            f"=" * 60,
            f"VERDICT: {report.verdict}",
            f"CONFIDENCE: {report.final_confidence * 100:.1f}%",
            f"",
            f"SUMMARY:",
            f"{report.human_summary}",
            f"",
            f"TOP CONTRIBUTING FACTORS:",
        ]

        for i, feat in enumerate(report.top_features, 1):
            lines.append(
                f"  {i}. {feat.feature_name}: {feat.interpretation} "
                f"({feat.contribution_percentage:.1f}% contribution)"
            )

        lines.extend(
            [
                f"",
                f"BAYESIAN ANALYSIS:",
                f"  Prior: {report.prior_confidence * 100:.1f}%",
                f"  Likelihood boost: +{report.likelihood_boost * 100:.1f}%",
                f"  Posterior: {report.posterior_confidence * 100:.1f}%",
                f"",
                f"THREAT CLASSIFICATION:",
                f"  Actor class: {report.actor_class}",
                f"  Probability: {report.actor_probability * 100:.1f}%",
                f"",
                f"BEHAVIORAL STATE PATH:",
                f"  {' → '.join(report.hmm_state_path)}",
                f"=" * 60,
            ]
        )

        return "\n".join(lines)


__all__ = ["FeatureContribution", "ExplainabilityReport", "ExplainabilityEngine"]
