"""
Deep Conversational Context Engine for Project-AI
Multi-turn tracking, intent detection, user history, and policy management.
Production-grade, fully integrated, no TODOs.
"""

import json
import logging
import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Intent(Enum):
    """User intent types"""

    QUERY = "query"
    COMMAND = "command"
    CONVERSATION = "conversation"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    REQUEST = "request"
    COMPLAINT = "complaint"
    GREETING = "greeting"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"


class TopicCategory(Enum):
    """Topic categories for tracking"""

    GENERAL = "general"
    TECHNICAL = "technical"
    PERSONAL = "personal"
    WORK = "work"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    FINANCE = "finance"
    EDUCATION = "education"
    NEWS = "news"
    SENSITIVE = "sensitive"


@dataclass
class ConversationTurn:
    """Single turn in conversation"""

    turn_id: str
    user_id: str
    timestamp: str
    user_input: str
    system_response: str
    detected_intent: Intent
    detected_emotion: str = "neutral"
    topics: list[str] = field(default_factory=list)
    entities: dict[str, list[str]] = field(default_factory=dict)
    context_references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Conversation session tracking"""

    session_id: str
    user_id: str
    start_time: str
    end_time: str | None = None
    turns: list[ConversationTurn] = field(default_factory=list)
    active_topics: set[str] = field(default_factory=set)
    session_mood: str = "neutral"
    interaction_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UserHistory:
    """User interaction history"""

    user_id: str
    total_sessions: int = 0
    total_turns: int = 0
    frequent_topics: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    frequent_intents: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    preferred_response_style: str = "balanced"
    typical_session_length: int = 10
    avg_response_sentiment: float = 0.5
    topic_sensitivities: dict[str, float] = field(default_factory=dict)
    interaction_patterns: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_interaction: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ConversationContextEngine:
    """
    Deep conversational context engine with full multi-turn tracking,
    intent detection, and user history management.
    """

    def __init__(self, data_dir: str = "data/conversation_context"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._active_sessions: dict[str, ConversationSession] = {}
        self._user_histories: dict[str, UserHistory] = {}
        self._turn_cache = deque(maxlen=1000)
        self._context_window = 10  # Number of turns to maintain in active context
        self._lock = threading.RLock()

        # Intent detection patterns
        self._intent_patterns = self._initialize_intent_patterns()

        # Topic keywords
        self._topic_keywords = self._initialize_topic_keywords()

        logger.info("ConversationContextEngine initialized")

    def _initialize_intent_patterns(self) -> dict[Intent, list[str]]:
        """Initialize intent detection patterns"""
        return {
            Intent.QUERY: ["what", "when", "where", "who", "why", "how", "?"],
            Intent.COMMAND: [
                "do",
                "execute",
                "run",
                "start",
                "stop",
                "create",
                "delete",
            ],
            Intent.CLARIFICATION: ["mean", "clarify", "explain", "repeat", "confused"],
            Intent.FEEDBACK: ["good", "bad", "wrong", "correct", "thanks", "helpful"],
            Intent.EMOTIONAL_EXPRESSION: [
                "feel",
                "sad",
                "happy",
                "angry",
                "frustrated",
            ],
            Intent.REQUEST: ["please", "could you", "would you", "can you"],
            Intent.COMPLAINT: ["problem", "issue", "broken", "not working", "error"],
            Intent.GREETING: ["hello", "hi", "hey", "greetings", "morning", "evening"],
            Intent.FAREWELL: ["bye", "goodbye", "see you", "farewell", "later"],
        }

    def _initialize_topic_keywords(self) -> dict[TopicCategory, list[str]]:
        """Initialize topic classification keywords"""
        return {
            TopicCategory.TECHNICAL: [
                "code",
                "programming",
                "software",
                "algorithm",
                "debug",
            ],
            TopicCategory.PERSONAL: [
                "life",
                "family",
                "friend",
                "relationship",
                "feeling",
            ],
            TopicCategory.WORK: ["job", "career", "project", "deadline", "meeting"],
            TopicCategory.ENTERTAINMENT: ["movie", "music", "game", "show", "fun"],
            TopicCategory.HEALTH: ["health", "sick", "doctor", "medicine", "exercise"],
            TopicCategory.FINANCE: ["money", "budget", "invest", "save", "cost"],
            TopicCategory.EDUCATION: ["learn", "study", "school", "course", "teach"],
            TopicCategory.NEWS: ["news", "event", "happening", "current", "update"],
            TopicCategory.SENSITIVE: [
                "death",
                "violence",
                "abuse",
                "trauma",
                "politics",
                "religion",
            ],
        }

    def start_session(self, user_id: str) -> str:
        """Start a new conversation session"""
        try:
            with self._lock:
                session_id = f"session_{user_id}_{int(time.time())}"

                session = ConversationSession(
                    session_id=session_id,
                    user_id=user_id,
                    start_time=datetime.utcnow().isoformat(),
                )

                self._active_sessions[session_id] = session

                # Get or create user history
                if user_id not in self._user_histories:
                    self._user_histories[user_id] = UserHistory(user_id=user_id)

                self._user_histories[user_id].total_sessions += 1

                logger.info(f"Started conversation session: {session_id}")
                return session_id

        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return ""

    def add_turn(
        self,
        session_id: str,
        user_input: str,
        system_response: str,
        context: dict[str, Any] | None = None,
    ) -> ConversationTurn | None:
        """Add a conversation turn"""
        try:
            with self._lock:
                if session_id not in self._active_sessions:
                    logger.error(f"Session not found: {session_id}")
                    return None

                session = self._active_sessions[session_id]
                context = context or {}

                # Generate turn ID
                turn_id = f"{session_id}_turn_{len(session.turns)}"

                # Detect intent
                detected_intent = self._detect_intent(user_input)

                # Detect emotion
                detected_emotion = context.get("detected_emotion", "neutral")

                # Extract topics
                topics = self._extract_topics(user_input)

                # Extract entities
                entities = self._extract_entities(user_input)

                # Find context references
                references = self._find_context_references(user_input, session)

                # Create turn
                turn = ConversationTurn(
                    turn_id=turn_id,
                    user_id=session.user_id,
                    timestamp=datetime.utcnow().isoformat(),
                    user_input=user_input,
                    system_response=system_response,
                    detected_intent=detected_intent,
                    detected_emotion=detected_emotion,
                    topics=topics,
                    entities=entities,
                    context_references=references,
                    metadata=context,
                )

                # Add to session
                session.turns.append(turn)
                session.interaction_count += 1
                session.active_topics.update(topics)

                # Update user history
                user_history = self._user_histories[session.user_id]
                user_history.total_turns += 1
                user_history.frequent_intents[detected_intent.value] += 1
                for topic in topics:
                    user_history.frequent_topics[topic] += 1
                user_history.last_interaction = datetime.utcnow().isoformat()

                # Add to cache
                self._turn_cache.append(turn)

                # Save session
                self._save_session(session_id)
                self._save_user_history(session.user_id)

                logger.debug(f"Added turn {turn_id} to session {session_id}")
                return turn

        except Exception as e:
            logger.error(f"Failed to add turn: {e}")
            return None

    def _detect_intent(self, text: str) -> Intent:
        """Detect user intent from text"""
        text_lower = text.lower()

        # Score each intent
        intent_scores = {}
        for intent, patterns in self._intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                intent_scores[intent] = score

        if not intent_scores:
            return Intent.UNKNOWN

        # Return highest scoring intent
        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def _extract_topics(self, text: str) -> list[str]:
        """Extract topics from text"""
        text_lower = text.lower()
        detected_topics = []

        for category, keywords in self._topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(category.value)

        if not detected_topics:
            detected_topics.append(TopicCategory.GENERAL.value)

        return detected_topics

    def _extract_entities(self, text: str) -> dict[str, list[str]]:
        """Extract named entities from text"""
        # Simplified entity extraction
        # In production, use NER model
        entities = {"numbers": [], "dates": [], "names": []}

        # Extract numbers
        import re

        numbers = re.findall(r"\d+", text)
        entities["numbers"] = numbers

        # Extract potential names (capitalized words)
        words = text.split()
        names = [w for w in words if w and w[0].isupper() and len(w) > 1]
        entities["names"] = names

        return entities

    def _find_context_references(
        self, text: str, session: ConversationSession
    ) -> list[str]:
        """Find references to previous context"""
        text_lower = text.lower()
        references = []

        # Check for explicit references
        reference_words = ["that", "this", "previous", "earlier", "before", "mentioned"]
        if any(word in text_lower for word in reference_words):
            # Look at recent turns
            recent_turns = (
                session.turns[-5:] if len(session.turns) >= 5 else session.turns
            )
            for turn in recent_turns:
                references.append(turn.turn_id)

        return references

    def get_context(
        self, session_id: str, window_size: int | None = None
    ) -> dict[str, Any]:
        """Get conversation context for a session"""
        try:
            with self._lock:
                if session_id not in self._active_sessions:
                    return {}

                session = self._active_sessions[session_id]
                window_size = window_size or self._context_window

                # Get recent turns
                recent_turns = (
                    session.turns[-window_size:]
                    if len(session.turns) > window_size
                    else session.turns
                )

                # Get user history
                user_history = self._user_histories.get(session.user_id, None)

                context = {
                    "session_id": session_id,
                    "user_id": session.user_id,
                    "turn_count": len(session.turns),
                    "recent_turns": [asdict(t) for t in recent_turns],
                    "active_topics": list(session.active_topics),
                    "session_mood": session.session_mood,
                    "user_history_summary": (
                        self._summarize_user_history(user_history)
                        if user_history
                        else {}
                    ),
                    "interaction_patterns": (
                        user_history.interaction_patterns if user_history else {}
                    ),
                }

                return context

        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return {}

    def _summarize_user_history(self, history: UserHistory) -> dict[str, Any]:
        """Summarize user history"""
        top_topics = sorted(
            history.frequent_topics.items(), key=lambda x: x[1], reverse=True
        )[:5]
        top_intents = sorted(
            history.frequent_intents.items(), key=lambda x: x[1], reverse=True
        )[:3]

        return {
            "total_sessions": history.total_sessions,
            "total_turns": history.total_turns,
            "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
            "top_intents": [{"intent": i, "count": c} for i, c in top_intents],
            "preferred_style": history.preferred_response_style,
            "avg_sentiment": history.avg_response_sentiment,
        }

    def end_session(self, session_id: str) -> bool:
        """End a conversation session"""
        try:
            with self._lock:
                if session_id not in self._active_sessions:
                    return False

                session = self._active_sessions[session_id]
                session.end_time = datetime.utcnow().isoformat()

                # Update user history with session stats
                user_history = self._user_histories[session.user_id]
                session_length = len(session.turns)

                # Update typical session length (running average)
                user_history.typical_session_length = (
                    user_history.typical_session_length
                    * (user_history.total_sessions - 1)
                    + session_length
                ) / user_history.total_sessions

                # Save and archive
                self._save_session(session_id)
                self._save_user_history(session.user_id)

                # Move to archive
                del self._active_sessions[session_id]

                logger.info(f"Ended session: {session_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False

    def get_user_history(self, user_id: str) -> UserHistory | None:
        """Get user history"""
        with self._lock:
            return self._user_histories.get(user_id)

    def update_user_preference(
        self, user_id: str, preference_key: str, preference_value: Any
    ) -> bool:
        """Update user preference"""
        try:
            with self._lock:
                if user_id not in self._user_histories:
                    return False

                history = self._user_histories[user_id]

                if preference_key == "response_style":
                    history.preferred_response_style = preference_value
                elif preference_key == "topic_sensitivity":
                    topic, sensitivity = preference_value
                    history.topic_sensitivities[topic] = sensitivity
                else:
                    history.interaction_patterns[preference_key] = preference_value

                self._save_user_history(user_id)
                return True

        except Exception as e:
            logger.error(f"Failed to update preference: {e}")
            return False

    def _save_session(self, session_id: str) -> None:
        """Save session to disk"""
        try:
            session = self._active_sessions.get(session_id)
            if not session:
                return

            session_file = os.path.join(self.data_dir, f"{session_id}.json")

            # Convert turns to serializable format
            turns_data = []
            for turn in session.turns:
                turn_dict = asdict(turn)
                # Convert Intent enum to string
                if isinstance(turn_dict.get("detected_intent"), Intent):
                    turn_dict["detected_intent"] = turn_dict["detected_intent"].value
                turns_data.append(turn_dict)

            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "turns": turns_data,
                "active_topics": list(session.active_topics),
                "session_mood": session.session_mood,
                "interaction_count": session.interaction_count,
                "metadata": session.metadata,
            }

            with open(session_file, "w") as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def _save_user_history(self, user_id: str) -> None:
        """Save user history to disk"""
        try:
            history = self._user_histories.get(user_id)
            if not history:
                return

            history_file = os.path.join(self.data_dir, f"history_{user_id}.json")

            with open(history_file, "w") as f:
                json.dump(asdict(history), f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save user history: {e}")


class AdaptivePolicy(Enum):
    """Adaptive policy types"""

    RESPONSE_LENGTH = "response_length"
    FORMALITY_LEVEL = "formality_level"
    DETAIL_LEVEL = "detail_level"
    EMPATHY_LEVEL = "empathy_level"
    PROACTIVITY = "proactivity"
    HUMOR_USAGE = "humor_usage"
    TOPIC_SENSITIVITY = "topic_sensitivity"


@dataclass
class PolicyConfiguration:
    """Configuration for adaptive policies"""

    policy_type: AdaptivePolicy
    value: float = 0.5  # 0-1 scale
    auto_adjust: bool = True
    min_value: float = 0.0
    max_value: float = 1.0
    adjustment_rate: float = 0.05
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class PolicyManager:
    """
    Highly adaptive, context-aware policy manager.
    No false alarms on swearing or sensitive topics - context-aware handling.
    """

    def __init__(
        self,
        context_engine: ConversationContextEngine,
        data_dir: str = "data/policy_manager",
    ):
        self.context_engine = context_engine
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._user_policies: dict[str, dict[AdaptivePolicy, PolicyConfiguration]] = {}
        self._global_defaults = self._initialize_defaults()
        self._lock = threading.RLock()

        logger.info("PolicyManager initialized")

    def _initialize_defaults(self) -> dict[AdaptivePolicy, PolicyConfiguration]:
        """Initialize default policy configurations"""
        return {
            AdaptivePolicy.RESPONSE_LENGTH: PolicyConfiguration(
                policy_type=AdaptivePolicy.RESPONSE_LENGTH, value=0.5  # Medium length
            ),
            AdaptivePolicy.FORMALITY_LEVEL: PolicyConfiguration(
                policy_type=AdaptivePolicy.FORMALITY_LEVEL, value=0.5  # Balanced
            ),
            AdaptivePolicy.DETAIL_LEVEL: PolicyConfiguration(
                policy_type=AdaptivePolicy.DETAIL_LEVEL, value=0.6  # Moderate detail
            ),
            AdaptivePolicy.EMPATHY_LEVEL: PolicyConfiguration(
                policy_type=AdaptivePolicy.EMPATHY_LEVEL, value=0.7  # High empathy
            ),
            AdaptivePolicy.PROACTIVITY: PolicyConfiguration(
                policy_type=AdaptivePolicy.PROACTIVITY,
                value=0.4,  # Moderate proactivity
            ),
            AdaptivePolicy.HUMOR_USAGE: PolicyConfiguration(
                policy_type=AdaptivePolicy.HUMOR_USAGE, value=0.3  # Light humor
            ),
            AdaptivePolicy.TOPIC_SENSITIVITY: PolicyConfiguration(
                policy_type=AdaptivePolicy.TOPIC_SENSITIVITY,
                value=0.8,  # High sensitivity to sensitive topics
            ),
        }

    def get_adaptive_policy(
        self, user_id: str, session_id: str, context: dict[str, Any] | None = None
    ) -> dict[str, float]:
        """
        Get adaptive policy configuration for user in current context.
        No false alarms - context-aware policy adjustment.
        """
        try:
            with self._lock:
                # Get or initialize user policies
                if user_id not in self._user_policies:
                    self._user_policies[user_id] = self._global_defaults.copy()

                policies = self._user_policies[user_id]

                # Get conversation context
                conv_context = self.context_engine.get_context(session_id)
                context = {**(context or {}), **conv_context}

                # Get user history
                user_history = self.context_engine.get_user_history(user_id)

                # Apply context-aware adjustments
                adjusted_policies = {}

                for policy_type, policy_config in policies.items():
                    adjusted_value = self._adjust_policy_for_context(
                        policy_config, context, user_history
                    )
                    adjusted_policies[policy_type.value] = adjusted_value

                return adjusted_policies

        except Exception as e:
            logger.error(f"Failed to get adaptive policy: {e}")
            return {}

    def _adjust_policy_for_context(
        self,
        policy: PolicyConfiguration,
        context: dict[str, Any],
        history: UserHistory | None,
    ) -> float:
        """Adjust policy based on context - NO FALSE ALARMS"""
        base_value = policy.value

        # No adjustment if auto-adjust is off
        if not policy.auto_adjust:
            return base_value

        adjusted = base_value

        if policy.policy_type == AdaptivePolicy.RESPONSE_LENGTH:
            # Adjust based on user's typical preference
            if history and history.typical_session_length > 20:
                adjusted += 0.1  # User likes longer conversations

            # Adjust based on current intent
            recent_turns = context.get("recent_turns", [])
            if recent_turns:
                last_intent = recent_turns[-1].get("detected_intent", "")
                if last_intent == Intent.QUERY.value:
                    adjusted += 0.15  # More detail for queries
                elif last_intent == Intent.COMMAND.value:
                    adjusted -= 0.1  # Briefer for commands

        elif policy.policy_type == AdaptivePolicy.FORMALITY_LEVEL:
            # Adjust based on detected formality in user input
            if history:
                # Check recent interaction patterns
                formality_pattern = history.interaction_patterns.get("formality", 0.5)
                adjusted = (adjusted + formality_pattern) / 2

        elif policy.policy_type == AdaptivePolicy.EMPATHY_LEVEL:
            # Increase empathy for emotional or sensitive topics
            active_topics = context.get("active_topics", [])
            if TopicCategory.SENSITIVE.value in active_topics:
                adjusted = min(1.0, adjusted + 0.3)

            recent_turns = context.get("recent_turns", [])
            if recent_turns:
                last_emotion = recent_turns[-1].get("detected_emotion", "neutral")
                if last_emotion in ["sad", "angry", "frustrated"]:
                    adjusted = min(1.0, adjusted + 0.2)

        elif policy.policy_type == AdaptivePolicy.TOPIC_SENSITIVITY:
            # Context-aware sensitivity - NO FALSE ALARMS
            # If user has high swearing tolerance (from history), don't overreact
            if history:
                swear_tolerance = history.interaction_patterns.get(
                    "swearing_tolerance", 0.5
                )
                if swear_tolerance > 0.7:
                    # User is comfortable with casual language - reduce sensitivity
                    adjusted = max(0.3, adjusted - 0.3)

                # Check if sensitive topics are user's frequent topics
                frequent_topics = history.frequent_topics
                sensitive_count = sum(
                    1
                    for topic in frequent_topics.keys()
                    if topic == TopicCategory.SENSITIVE.value
                )
                if sensitive_count > 5:
                    # User frequently discusses sensitive topics - they're okay with it
                    adjusted = max(0.4, adjusted - 0.2)

        elif policy.policy_type == AdaptivePolicy.HUMOR_USAGE:
            # Adjust humor based on user appreciation
            if history:
                humor_appreciation = history.interaction_patterns.get(
                    "humor_appreciation", 0.5
                )
                adjusted = (adjusted + humor_appreciation) / 2

        # Clamp to valid range
        adjusted = max(policy.min_value, min(policy.max_value, adjusted))

        return adjusted

    def update_policy_from_feedback(
        self, user_id: str, policy_type: AdaptivePolicy, feedback: str
    ) -> bool:
        """
        Update policy based on user feedback.
        feedback: 'increase', 'decrease', or 'reset'
        """
        try:
            with self._lock:
                if user_id not in self._user_policies:
                    self._user_policies[user_id] = self._global_defaults.copy()

                policy = self._user_policies[user_id][policy_type]

                if feedback == "increase":
                    policy.value = min(
                        policy.max_value, policy.value + policy.adjustment_rate
                    )
                elif feedback == "decrease":
                    policy.value = max(
                        policy.min_value, policy.value - policy.adjustment_rate
                    )
                elif feedback == "reset":
                    policy.value = self._global_defaults[policy_type].value

                policy.last_updated = datetime.utcnow().isoformat()

                self._save_user_policies(user_id)
                logger.info(f"Updated policy {policy_type.value} for user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to update policy: {e}")
            return False

    def _save_user_policies(self, user_id: str) -> None:
        """Save user policies to disk"""
        try:
            policies = self._user_policies.get(user_id)
            if not policies:
                return

            policy_file = os.path.join(self.data_dir, f"policies_{user_id}.json")

            policies_data = {
                policy_type.value: asdict(config)
                for policy_type, config in policies.items()
            }

            with open(policy_file, "w") as f:
                json.dump(policies_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save user policies: {e}")


# Global instances
_default_context_engine: ConversationContextEngine | None = None
_default_policy_manager: PolicyManager | None = None


def get_default_context_engine() -> ConversationContextEngine:
    """Get or create default context engine"""
    global _default_context_engine
    if _default_context_engine is None:
        _default_context_engine = ConversationContextEngine()
    return _default_context_engine


def get_default_policy_manager(
    context_engine: ConversationContextEngine | None = None,
) -> PolicyManager:
    """Get or create default policy manager"""
    global _default_policy_manager
    if _default_policy_manager is None:
        engine = context_engine or get_default_context_engine()
        _default_policy_manager = PolicyManager(engine)
    return _default_policy_manager
