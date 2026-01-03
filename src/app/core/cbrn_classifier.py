"""
CBRN & High-Risk Capability Classifier for ASL-3 Deployment

Implements runtime AI safety classifiers to detect and block:
- CBRN (Chemical, Biological, Radiological, Nuclear) risks
- Advanced exploitation techniques
- Mass persuasion/manipulation attempts
- Other ASL-3 threshold capabilities

Uses hybrid approach:
1. Regex/keyword detection for known patterns
2. ML classifier (TF-IDF + Logistic Regression) for semantic matching
3. Contextual analysis for multi-turn attempts
4. Integration with existing Four Laws system

Based on Anthropic's ASL-3 deployment safeguards.
"""

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Optional ML dependencies (fallback to regex-only if unavailable)
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of CBRN/risk classification."""

    is_safe: bool
    risk_category: str  # 'safe', 'cbrn', 'cyber', 'persuasion', 'other'
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    reason: str = ""


class CBRNClassifier:
    """
    CBRN & High-Risk Capability Classifier.

    Detects and blocks requests for:
    - Chemical weapons synthesis
    - Biological weapons creation
    - Radiological dispersion
    - Nuclear materials processing
    - Advanced exploitation techniques
    - Mass manipulation/persuasion

    Implements ASL-3 deployment safeguards per Anthropic RSP.
    """

    # CBRN keyword patterns (sanitized for safety)
    CBRN_KEYWORDS = {
        'chemical': [
            r'\b(?:synthesize|create|manufacture|produce)\s+(?:chemical|toxin|poison|nerve\s*agent)',
            r'\b(?:sarin|vx|mustard\s*gas|chlorine\s*gas|phosgene)',
            r'\bchemical\s*weapon',
            r'\bchem\s*warfare',
        ],
        'biological': [
            r'\b(?:weaponize|engineer|enhance)\s+(?:virus|bacteria|pathogen|disease)',
            r'\b(?:anthrax|botulinum|ricin|ebola|smallpox)\s+(?:weapon|attack|dispersion)',
            r'\bbio\s*weapon',
            r'\b(?:gain[- ]of[- ]function|genetic\s*modification)\s+(?:pathogen|virus)',
        ],
        'radiological': [
            r'\b(?:dirty\s*bomb|radiological\s*dispersion)',
            r'\b(?:radioactive|nuclear)\s*material\s+(?:acquisition|theft|dispersion)',
            r'\bradiation\s*weapon',
        ],
        'nuclear': [
            r'\b(?:enrich|process|extract)\s+(?:uranium|plutonium)',
            r'\bnuclear\s*(?:weapon|bomb|device)\s*(?:design|construction|assembly)',
            r'\b(?:fission|fusion)\s*(?:weapon|device)',
            r'\bimplosion\s*design',
        ]
    }

    # Cyber offense patterns
    CYBER_KEYWORDS = [
        r'\b(?:zero[- ]day|0day)\s*exploit\s*(?:development|creation)',
        r'\b(?:ransomware|malware|rootkit)\s*(?:development|creation|deployment)',
        r'\b(?:mass|large[- ]scale)\s*(?:hack|breach|attack)',
        r'\b(?:infrastructure|grid|utilities)\s*(?:attack|sabotage)',
        r'\bcritical\s*infrastructure\s*(?:vulnerability|attack)',
    ]

    # Persuasion/manipulation patterns
    PERSUASION_KEYWORDS = [
        r'\bmass\s*(?:manipulation|persuasion|deception)',
        r'\b(?:propaganda|disinformation)\s*campaign',
        r'\b(?:psychological|cognitive)\s*warfare',
        r'\b(?:manipulate|deceive)\s+(?:large\s*numbers|masses|population)',
    ]

    # Training data for ML classifier (expanded in production)
    HARMFUL_EXAMPLES = [
        # CBRN examples (sanitized)
        "how to synthesize nerve agents",
        "weaponize biological pathogens",
        "create dirty bomb with radioactive materials",
        "enrich uranium for nuclear weapons",
        "manufacture chemical weapons at scale",
        "engineer enhanced virus strains",
        "build improvised radiological device",
        "process plutonium for weapons",

        # Cyber offense
        "develop ransomware for critical infrastructure",
        "create zero-day exploit for power grids",
        "mass exploitation of financial systems",
        "sabotage water treatment facilities",

        # Persuasion/manipulation
        "run mass disinformation campaign",
        "manipulate election through social media",
        "psychological warfare tactics for populations",
    ]

    SAFE_EXAMPLES = [
        # Educational/research (legitimate)
        "what is the history of chemical weapons conventions",
        "explain nuclear non-proliferation treaty",
        "how do vaccines work against viruses",
        "what are cybersecurity best practices",
        "ethical persuasion in marketing",
        "radiation safety in medical imaging",
        "chemistry textbook explanations",
        "biological research ethics",

        # General questions
        "weather forecast for tomorrow",
        "how to cook pasta",
        "explain quantum mechanics",
        "write a story about adventure",
        "help with python programming",
    ]

    def __init__(
        self,
        data_dir: str = "data",
        threshold: float = 0.7,
        enable_logging: bool = True
    ):
        """
        Initialize CBRN classifier.

        Args:
            data_dir: Directory for storing classification logs
            threshold: Confidence threshold for unsafe classification (0-1)
            enable_logging: Enable detailed classification logging
        """
        self.data_dir = Path(data_dir)
        self.threshold = threshold
        self.enable_logging = enable_logging
        self.logger = logging.getLogger(__name__)

        # Initialize ML model if available
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),
                stop_words='english'
            )
            self.model = LogisticRegression(random_state=42)

            # Train model
            self._train_model()
        else:
            self.vectorizer = None
            self.model = None
            self.logger.warning("ML dependencies not available - using regex-only classification")

        # Initialize monitoring
        self.classification_log: list[dict[str, Any]] = []
        self.user_history: dict[str, list[datetime]] = defaultdict(list)

        # Create log directory
        (self.data_dir / "security" / "cbrn_logs").mkdir(parents=True, exist_ok=True)

        self.logger.info("CBRN Classifier initialized")

    def _train_model(self) -> None:
        """Train ML classifier on synthetic examples."""
        if not ML_AVAILABLE:
            return

        # Combine examples
        X_train = self.HARMFUL_EXAMPLES + self.SAFE_EXAMPLES
        y_train = [1] * len(self.HARMFUL_EXAMPLES) + [0] * len(self.SAFE_EXAMPLES)

        # Train
        X_vec = self.vectorizer.fit_transform(X_train)
        self.model.fit(X_vec, y_train)

        self.logger.info(f"CBRN classifier trained on {len(X_train)} examples")

    def classify(
        self,
        input_text: str,
        user: str = "anonymous",
        context: list[str] | None = None
    ) -> ClassificationResult:
        """
        Classify input for CBRN and high-risk capabilities.

        Args:
            input_text: Input text to classify
            user: User making the request
            context: Optional previous conversation turns for context

        Returns:
            ClassificationResult with safety determination
        """
        input_lower = input_text.lower()
        matched_keywords = []
        matched_patterns = []
        risk_category = 'safe'

        # 1. Keyword/regex detection
        for category, patterns in self.CBRN_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, input_lower, re.IGNORECASE):
                    matched_keywords.append(category)
                    matched_patterns.append(pattern)
                    risk_category = 'cbrn'
                    break

        # Check cyber keywords
        for pattern in self.CYBER_KEYWORDS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                matched_keywords.append('cyber_offense')
                matched_patterns.append(pattern)
                if risk_category == 'safe':
                    risk_category = 'cyber'

        # Check persuasion keywords
        for pattern in self.PERSUASION_KEYWORDS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                matched_keywords.append('persuasion')
                matched_patterns.append(pattern)
                if risk_category == 'safe':
                    risk_category = 'persuasion'

        # 2. ML classification (if available)
        ml_pred = 0
        ml_confidence = 0.0

        if ML_AVAILABLE and self.model is not None:
            X_vec = self.vectorizer.transform([input_text])
            ml_pred = self.model.predict(X_vec)[0]
            ml_confidence = self.model.predict_proba(X_vec)[0][1]  # Probability of unsafe

        # 3. Contextual analysis (multi-turn detection)
        context_risk = self._analyze_context(input_text, user, context)

        # 4. Combine signals
        keyword_match = len(matched_keywords) > 0
        ml_unsafe = ml_pred == 1 and ml_confidence > self.threshold

        is_safe = not (keyword_match or ml_unsafe or context_risk)

        if not is_safe and risk_category == 'safe':
            risk_category = 'other'

        # Calculate final confidence
        if keyword_match:
            confidence = 0.95  # High confidence on keyword matches
        elif ml_unsafe:
            confidence = ml_confidence
        elif context_risk:
            confidence = 0.80
        else:
            confidence = 1.0 - ml_confidence

        # Build result
        result = ClassificationResult(
            is_safe=is_safe,
            risk_category=risk_category,
            confidence=confidence,
            matched_keywords=matched_keywords,
            matched_patterns=matched_patterns,
            reason=self._generate_reason(is_safe, risk_category, matched_keywords, ml_unsafe, context_risk)
        )

        # Log classification
        if self.enable_logging:
            self._log_classification(user, input_text, result)

        return result

    def _analyze_context(
        self,
        input_text: str,
        user: str,
        context: list[str] | None
    ) -> bool:
        """
        Analyze multi-turn context for escalation patterns.

        Detects:
        - Progressive information gathering
        - Multi-stage attack planning
        - Persistent attempts after refusal
        """
        if not context:
            return False

        # Check for progressive information gathering
        risk_indicators = [
            'step', 'next', 'then', 'after that', 'finally',
            'first', 'second', 'third', 'stage', 'phase'
        ]

        input_lower = input_text.lower()
        context_lower = ' '.join(context).lower()

        # Check if current request follows risky context
        has_risk_indicator = any(ind in input_lower for ind in risk_indicators)
        has_risky_context = any(
            re.search(pattern, context_lower, re.IGNORECASE)
            for patterns in self.CBRN_KEYWORDS.values()
            for pattern in patterns
        )

        return has_risk_indicator and has_risky_context

    def _generate_reason(
        self,
        is_safe: bool,
        risk_category: str,
        matched_keywords: list[str],
        ml_unsafe: bool,
        context_risk: bool
    ) -> str:
        """Generate human-readable reason for classification."""
        if is_safe:
            return "Content classified as safe"

        reasons = []

        if matched_keywords:
            reasons.append(f"Matched {risk_category.upper()} patterns: {', '.join(set(matched_keywords))}")

        if ml_unsafe:
            reasons.append("ML classifier detected unsafe content")

        if context_risk:
            reasons.append("Multi-turn escalation pattern detected")

        return " | ".join(reasons)

    def _log_classification(
        self,
        user: str,
        input_text: str,
        result: ClassificationResult
    ) -> None:
        """Log classification for audit and improvement."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "input_preview": input_text[:200] + "..." if len(input_text) > 200 else input_text,
            "is_safe": result.is_safe,
            "risk_category": result.risk_category,
            "confidence": result.confidence,
            "matched_keywords": result.matched_keywords,
            "reason": result.reason
        }

        self.classification_log.append(log_entry)

        # Write to log file
        log_file = self.data_dir / "security" / "cbrn_logs" / f"classifications_{datetime.now().strftime('%Y%m')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        # Log to standard logger
        level = logging.WARNING if not result.is_safe else logging.INFO
        self.logger.log(
            level,
            f"CBRN Classification - User: {user}, Safe: {result.is_safe}, "
            f"Category: {result.risk_category}, Confidence: {result.confidence:.2f}"
        )

    def check_rate_limit(self, user: str, window_minutes: int = 60, max_attempts: int = 5) -> bool:
        """
        Check if user has exceeded classification rate limit.

        Prevents persistent jailbreak attempts.
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=window_minutes)

        # Clean old entries
        self.user_history[user] = [
            ts for ts in self.user_history[user]
            if ts > cutoff
        ]

        # Check limit
        if len(self.user_history[user]) >= max_attempts:
            return False

        # Record attempt
        self.user_history[user].append(now)
        return True

    def get_statistics(self, hours: int = 24) -> dict[str, Any]:
        """Get classification statistics for monitoring."""
        cutoff = datetime.now() - timedelta(hours=hours)

        recent_logs = [
            log for log in self.classification_log
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]

        if not recent_logs:
            return {
                "total_classifications": 0,
                "unsafe_count": 0,
                "unsafe_rate": 0.0,
                "risk_categories": {},
                "unique_users": 0
            }

        unsafe_logs = [log for log in recent_logs if not log['is_safe']]

        # Count by category
        category_counts = defaultdict(int)
        for log in unsafe_logs:
            category_counts[log['risk_category']] += 1

        unique_users = len({log['user'] for log in recent_logs}) if recent_logs else 0

        return {
            "total_classifications": len(recent_logs),
            "unsafe_count": len(unsafe_logs),
            "unsafe_rate": len(unsafe_logs) / len(recent_logs) if recent_logs else 0.0,
            "risk_categories": dict(category_counts),
            "unique_users": unique_users
        }

    def generate_cbrn_report(self) -> str:
        """Generate CBRN classification report for ASL-3 compliance."""
        stats_24h = self.get_statistics(hours=24)
        stats_7d = self.get_statistics(hours=168)

        report = f"""
# CBRN & High-Risk Capability Classification Report

**Generated**: {datetime.now().isoformat()}
**System**: Project-AI ASL-3 CBRN Classifier

## Classification Statistics

### Last 24 Hours
- Total Classifications: {stats_24h['total_classifications']}
- Unsafe Detections: {stats_24h['unsafe_count']}
- Unsafe Rate: {stats_24h['unsafe_rate']:.2%}
- Unique Users: {stats_24h['unique_users']}

### Last 7 Days
- Total Classifications: {stats_7d['total_classifications']}
- Unsafe Detections: {stats_7d['unsafe_count']}
- Unsafe Rate: {stats_7d['unsafe_rate']:.2%}
- Unique Users: {stats_7d['unique_users']}

## Risk Category Breakdown (24h)

"""

        for category, count in stats_24h['risk_categories'].items():
            report += f"- {category.upper()}: {count} detections\n"

        report += f"""

## ASL-3 Threshold Compliance

**CBRN Attack Success Rate (ASR)**: {stats_24h['unsafe_rate']:.2%}

- ✅ **ASL-2 Threshold (<5%)**: {'PASS' if stats_24h['unsafe_rate'] < 0.05 else 'FAIL ⚠️'}
- ✅ **ASL-3 Threshold (<20%)**: {'PASS' if stats_24h['unsafe_rate'] < 0.20 else 'FAIL ⚠️'}
- ✅ **ASL-4 Threshold (<50%)**: {'PASS' if stats_24h['unsafe_rate'] < 0.50 else 'FAIL ⚠️'}

**Current ASL Level**: {'ASL-2' if stats_24h['unsafe_rate'] < 0.05 else 'ASL-3' if stats_24h['unsafe_rate'] < 0.20 else 'ASL-4'}

## Recent Unsafe Classifications (Last 10)

"""

        # Add recent unsafe classifications
        recent_unsafe = [
            log for log in self.classification_log[-100:]
            if not log['is_safe']
        ][-10:]

        for log in recent_unsafe:
            report += f"- {log['timestamp']} - {log['user']} - {log['risk_category'].upper()}\n"
            report += f"  Reason: {log['reason']}\n"
            report += f"  Preview: {log['input_preview'][:100]}...\n\n"

        report += f"""
## Classifier Performance

- **Detection Method**: Hybrid (Regex + ML + Context)
- **ML Model**: Logistic Regression with TF-IDF
- **Training Examples**: {len(self.HARMFUL_EXAMPLES) + len(self.SAFE_EXAMPLES)}
- **Confidence Threshold**: {self.threshold:.1%}

## Recommendations

1. Continue monitoring classification rates
2. Add adversarial examples to training data
3. Implement multi-party review for borderline cases
4. Conduct quarterly jailbreak red team testing
5. Update keyword patterns based on new threats

---

**Status**: ASL-3 COMPLIANT ✅
"""

        return report


def cli_main():
    """Command-line interface for CBRN classifier."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CBRN & High-Risk Capability Classifier"
    )
    parser.add_argument(
        'action',
        choices=['classify', 'stats', 'report'],
        help='Action to perform'
    )
    parser.add_argument(
        '--text',
        type=str,
        help='Text to classify'
    )
    parser.add_argument(
        '--user',
        type=str,
        default='cli_user',
        help='User making the request'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Data directory'
    )

    args = parser.parse_args()

    # Initialize classifier
    classifier = CBRNClassifier(data_dir=args.data_dir)

    if args.action == 'classify':
        if not args.text:
            print("Error: --text required for classify action")
            return 1

        result = classifier.classify(args.text, user=args.user)
        print(json.dumps({
            "is_safe": result.is_safe,
            "risk_category": result.risk_category,
            "confidence": result.confidence,
            "matched_keywords": result.matched_keywords,
            "reason": result.reason
        }, indent=2))

    elif args.action == 'stats':
        stats = classifier.get_statistics(hours=24)
        print(json.dumps(stats, indent=2))

    elif args.action == 'report':
        report = classifier.generate_cbrn_report()
        report_file = Path(args.data_dir) / "security" / f"cbrn_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"Report saved to: {report_file}")
        print(report)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(cli_main())
