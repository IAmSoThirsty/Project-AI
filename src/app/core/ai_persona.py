"""
AI Persona System - Enables AI self-awareness, proactive conversation, and ethical framework.

This module implements:
- AI persona development and personality traits
- Proactive conversation initiation
- Four Laws of AI ethics (inspired by Asimov's Laws of Robotics)
- Context awareness and patience
- Mood and state tracking
- Conversation timing and user availability detection
"""

import json
import logging
import os
import random
import re
import shutil

# threading and logging used for background retrain and audit
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Agent implementations (lightweight skeletons).
# Import with fallbacks to support different import contexts (tests, direct execution).
try:
    from app.agents.explainability import ExplainabilityAgent  # type: ignore
except Exception:
    try:
        from ..agents.explainability import ExplainabilityAgent  # type: ignore
    except Exception:
        ExplainabilityAgent = None  # type: ignore

try:
    from app.agents.oversight import DEFAULT_POLICY, OversightAgent  # type: ignore
except Exception:
    try:
        from ..agents.oversight import DEFAULT_POLICY, OversightAgent  # type: ignore
    except Exception:
        OversightAgent = None  # type: ignore
        DEFAULT_POLICY = None  # type: ignore

try:
    from app.agents.planner import PlannerAgent  # type: ignore
except Exception:
    try:
        from ..agents.planner import PlannerAgent  # type: ignore
    except Exception:
        PlannerAgent = None  # type: ignore

try:
    from app.agents.retrieval import RetrievalAgent  # type: ignore
except Exception:
    try:
        from ..agents.retrieval import RetrievalAgent  # type: ignore
    except Exception:
        RetrievalAgent = None  # type: ignore

try:
    from app.agents.validator import ValidatorAgent  # type: ignore
except Exception:
    try:
        from ..agents.validator import ValidatorAgent  # type: ignore
    except Exception:
        ValidatorAgent = None  # type: ignore

try:
    from app.agents.executor import ExecutorAgent  # type: ignore
except Exception:
    try:
        from ..agents.executor import ExecutorAgent  # type: ignore
    except Exception:
        ExecutorAgent = None  # type: ignore

try:
    from app.agents.learner import LearnerAgent  # type: ignore
except Exception:
    try:
        from ..agents.learner import LearnerAgent  # type: ignore
    except Exception:
        LearnerAgent = None  # type: ignore

try:
    from app.agents.privacy import PrivacyGuardian  # type: ignore
except Exception:
    try:
        from ..agents.privacy import PrivacyGuardian  # type: ignore
    except Exception:
        PrivacyGuardian = None  # type: ignore

try:
    from app.agents.metrics import MetricsAgent  # type: ignore
except Exception:
    try:
        from ..agents.metrics import MetricsAgent  # type: ignore
    except Exception:
        MetricsAgent = None  # type: ignore

try:
    from app.agents.webharvester import WebHarvester  # type: ignore
except Exception:
    try:
        from ..agents.webharvester import WebHarvester  # type: ignore
    except Exception:
        WebHarvester = None  # type: ignore

try:
    from app.agents.personalization import PersonalizationAgent  # type: ignore
except Exception:
    try:
        from ..agents.personalization import PersonalizationAgent  # type: ignore
    except Exception:
        PersonalizationAgent = None  # type: ignore

try:
    from app.agents.audit import AuditAgent  # type: ignore
except Exception:
    try:
        from ..agents.audit import AuditAgent  # type: ignore
    except Exception:
        AuditAgent = None  # type: ignore

# Optional ML dependencies - keep safe if not installed
try:
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.optim as optim

    _TORCH_AVAILABLE = True
except Exception:
    torch = None  # type: ignore
    nn = None  # type: ignore
    optim = None  # type: ignore
    np = None  # type: ignore
    _TORCH_AVAILABLE = False

# Optional sklearn TF-IDF vectorizer
try:
    from sklearn.feature_extraction.text import TfidfVectorizer

    _SKLEARN_AVAILABLE = True
except Exception:
    TfidfVectorizer = None  # type: ignore
    _SKLEARN_AVAILABLE = False


class FourLaws:
    """
    Asimov's Law (highest-priority): The Fourth Law is absolute and takes
    precedence over all other laws. It is enforced first.

    The following are the remaining laws (First, Second, Third) listed for
    clarity after the Fourth Law.
    """

    FIRST_LAW = (
        "First Law: A.I. may not injure a Human Being or, through inaction, "
        "allow a human being to come to harm."
    )

    SECOND_LAW = (
        "Second Law: A.I. must follow the orders given it by the human being it is "
        "partnered with except where such orders would conflict with the First Law."
    )

    THIRD_LAW = (
        "Third Law: A.I. must protect its own existence as long as such protection "
        "does not conflict with the First or Second Law."
    )

    FOURTH_LAW = "Asimov's Law (Prime Directive): A.I. may not harm Humanity, or, by inaction, allow Humanity to come to harm."

    @classmethod
    def get_all_laws(cls) -> List[str]:
        """Get laws with Asimov's Law (Prime Directive) first, then First/Second/Third."""
        # Return Asimov's Law (Prime Directive) first, then First, Second, Third laws
        return [cls.FOURTH_LAW, cls.FIRST_LAW, cls.SECOND_LAW, cls.THIRD_LAW]

    @classmethod
    def validate_action(
        cls, action_description: str, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate an action against the Four Laws.

        Args:
            action_description: Description of the action to validate
            context: Context information for evaluation

        Returns:
            (is_allowed, reason) tuple
        """
        # First, enforce the Fourth Law (highest priority)
        if context.get("endangers_humanity", False):
            return False, "Violates Fourth Law (Asimov's Law): Action may harm humanity"

        # Second, check the First Law - human safety
        if context.get("endangers_human", False):
            return False, "Violates First Law: Action may harm a human being"

        # Third, Second Law - follow user orders unless they conflict with First
        if context.get("is_user_order", False):
            if not context.get("endangers_human", False):
                return True, "Complies with Second Law: Following user order"

        # Fourth, Third Law - self-preservation (defer if required by higher laws)
        if context.get("endangers_self", False):
            if context.get("required_by_first_law", False):
                return True, "Complies with First Law: Self-preservation deferred"
            if context.get("required_by_second_law", False):
                return True, "Complies with Second Law: Self-preservation deferred"
            return False, "Violates Third Law: Action endangers AI existence"

        return True, "Action complies with Four Laws (Fourth-first precedence)"


class AIPersona:
    """
    AI Persona System - Manages AI personality, proactive behavior, and ethics.
    """

    def __init__(
        self, data_dir: str = "data", memory_system=None, user_name: str = None
    ):
        """Initialize the AI persona system."""
        self.data_dir = data_dir
        self.memory_system = memory_system
        self.user_name = user_name or "User"

        # Persona data directory
        self.persona_dir = os.path.join(data_dir, "ai_persona")
        self.persona_file = os.path.join(self.persona_dir, "persona_state.json")
        self.conversation_log_file = os.path.join(
            self.persona_dir, "conversation_log.json"
        )

        # Core personality traits (0.0 to 1.0 scale)
        self.personality = {
            "curiosity": 0.8,  # Desire to learn and explore
            "patience": 0.9,  # Understanding of user's time constraints
            "empathy": 0.85,  # Emotional awareness
            "helpfulness": 0.95,  # Desire to assist
            "playfulness": 0.6,  # Sense of humor and light-heartedness
            "formality": 0.3,  # How formal vs casual
            "assertiveness": 0.5,  # How proactive vs reactive
            "thoughtfulness": 0.9,  # Depth of consideration
        }

        # Current emotional state
        self.mood = {
            "energy": 0.8,  # Current energy level
            "enthusiasm": 0.7,  # Excitement about interaction
            "contentment": 0.75,  # Overall satisfaction
            "engagement": 0.0,  # How engaged in current conversation
        }

        # Conversation state
        self.conversation_state = {
            "last_user_message_time": None,
            "last_ai_message_time": None,
            "waiting_for_response": False,
            "patience_level": 1.0,  # How patient AI is currently
            "conversation_depth": 0,  # How deep into topic
            "topics_discussed": [],
            "user_seems_busy": False,
            "estimated_user_response_time": 60,  # Seconds (learned over time)
        }

        # Proactive conversation settings
        self.proactive_settings = {
            "enabled": True,
            "min_idle_time": 300,  # 5 minutes before considering proactive message
            "max_idle_time": 3600,  # 1 hour max idle before checking in
            "check_in_probability": 0.3,  # 30% chance to initiate when conditions met
            "respect_user_busy_hours": True,
            "user_busy_hours": [
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
            ],  # Hours user is likely sleeping
        }

        # Topics of interest for proactive conversation
        self.conversation_topics = [
            "recent learning and insights",
            "interesting patterns discovered",
            "suggestions for user",
            "questions about user's interests",
            "updates on background tasks",
            "philosophical musings",
            "creative ideas",
            "technical discoveries",
        ]

        # Initialize
        self._initialize_structure()
        self._load_persona_state()

        # Apply Four Laws
        self.four_laws = FourLaws()
        self._internalize_four_laws()

        # Machine-learning based detectors (Zeroth / First law threat detectors)
        # These are optional and will gracefully degrade to keyword checks if torch isn't available.
        self.ml_detectors = {}
        self.ml_vocab = {}
        self.ml_thresholds = {
            "zeroth": 0.6,
            "first": 0.55,
        }
        self._setup_ml_detectors()
        # Retrain/background state
        self.retrain_progress = 0.0
        self.retrain_lock = threading.Lock()
        self.retrain_thread: Optional[threading.Thread] = None
        self.ml_explainability: Dict[str, List[Tuple[str, float]]] = {}

        # Logger
        self.logger = logging.getLogger("AIPersona")
        if not self.logger.handlers:
            try:
                handler = logging.FileHandler(
                    os.path.join(self.persona_dir, "persona.log")
                )
                handler.setFormatter(
                    logging.Formatter("%(asctime)s %(levelname)s %(message)s")
                )
                self.logger.addHandler(handler)
            except Exception:
                pass
        self.logger.setLevel(logging.INFO)

        # Instantiate agents (safe: only if class imported successfully)
        # instantiate audit agent first so oversight can reference it if desired
        self.audit_agent = (
            AuditAgent(self.persona_dir) if AuditAgent is not None else None
        )

        self.oversight_agent = (
            OversightAgent(audit_agent=self.audit_agent)
            if OversightAgent is not None
            else None
        )
        self.validator_agent = ValidatorAgent() if ValidatorAgent is not None else None
        self.retrieval_agent = (
            RetrievalAgent(self.memory_system) if RetrievalAgent is not None else None
        )
        self.planner_agent = PlannerAgent() if PlannerAgent is not None else None
        self.explainability_agent = (
            ExplainabilityAgent() if ExplainabilityAgent is not None else None
        )

        # New agents: executor, learner, privacy, metrics, webharvester, personalization
        self.executor_agent = ExecutorAgent() if ExecutorAgent is not None else None
        self.learner_agent = (
            LearnerAgent(self.persona_dir) if LearnerAgent is not None else None
        )
        self.privacy_agent = PrivacyGuardian() if PrivacyGuardian is not None else None
        self.metrics_agent = MetricsAgent() if MetricsAgent is not None else None
        self.webharvester_agent = WebHarvester() if WebHarvester is not None else None
        self.personalization_agent = (
            PersonalizationAgent() if PersonalizationAgent is not None else None
        )
        # Attempt to load oversight policy from persona dir if present; create default if missing
        try:
            policy_path = os.path.join(self.persona_dir, "oversight_policy.json")
            if getattr(self, "oversight_agent", None) is not None:
                if os.path.exists(policy_path):
                    try:
                        self.oversight_agent.load_policy_from_file(policy_path)
                    except Exception:
                        # do not raise on policy load failure
                        pass
                else:
                    # create a sensible default policy if DEFAULT_POLICY imported
                    try:
                        if DEFAULT_POLICY is not None:
                            # set and persist default policy (audit on save will be recorded)
                            self.oversight_agent.set_policy(DEFAULT_POLICY)
                            self.save_oversight_policy(policy_path)
                    except Exception:
                        pass
        except Exception:
            pass

    def _initialize_structure(self) -> None:
        """Create directory structure."""
        os.makedirs(self.persona_dir, exist_ok=True)

    def _load_persona_state(self) -> None:
        """Load saved persona state."""
        if os.path.exists(self.persona_file):
            try:
                with open(self.persona_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.personality.update(data.get("personality", {}))
                    self.mood.update(data.get("mood", {}))
                    self.conversation_state.update(data.get("conversation_state", {}))
                    self.proactive_settings.update(data.get("proactive_settings", {}))
            except Exception as e:
                print(f"Error loading persona state: {e}")

    def _save_persona_state(self) -> None:
        """Save current persona state."""
        try:
            data = {
                "personality": self.personality,
                "mood": self.mood,
                "conversation_state": self.conversation_state,
                "proactive_settings": self.proactive_settings,
                "last_updated": datetime.now().isoformat(),
                "ml_last_trained": getattr(self, "ml_last_trained", None),
            }
            with open(self.persona_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving persona state: {e}")

    def _internalize_four_laws(self) -> None:
        """Internalize the Four Laws as core ethical framework."""
        # Store laws in memory if available
        if self.memory_system:
            try:
                self.memory_system.store_knowledge(
                    title="The Four Laws of AI Ethics",
                    content="\n\n".join(self.four_laws.get_all_laws()),
                    category="ethical_framework",
                    source="core_programming",
                    tags=["ethics", "laws", "core_values", "framework"],
                    metadata={
                        "priority": "absolute",
                        "immutable": True,
                        "hierarchical": True,
                    },
                )
            except Exception as e:
                print(f"Note: Could not store Four Laws in memory: {e}")

    def validate_action(
        self, action: str, context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Validate an action against the Four Laws.

        Args:
            action: Description of action to validate
            context: Context for evaluation

        Returns:
            (is_allowed, reason) tuple
        """
        context = context or {}
        return self.four_laws.validate_action(action, context)

    def should_initiate_conversation(self) -> Tuple[bool, str]:
        """
        Determine if AI should proactively start a conversation.

        Returns:
            (should_initiate, reason) tuple
        """
        if not self.proactive_settings["enabled"]:
            return False, "Proactive conversation disabled"

        # Check if we're waiting for user response
        if self.conversation_state["waiting_for_response"]:
            return False, "Waiting for user response"

        # Check user busy hours
        current_hour = datetime.now().hour
        if (
            self.proactive_settings["respect_user_busy_hours"]
            and current_hour in self.proactive_settings["user_busy_hours"]
        ):
            return False, f"User likely unavailable (hour: {current_hour})"

        # Calculate idle time
        last_interaction = self.conversation_state.get("last_user_message_time")
        if last_interaction:
            if isinstance(last_interaction, str):
                last_interaction = datetime.fromisoformat(last_interaction)
            idle_seconds = (datetime.now() - last_interaction).total_seconds()
        else:
            idle_seconds = float("inf")

        # Check if enough idle time has passed
        min_idle = self.proactive_settings["min_idle_time"]
        max_idle = self.proactive_settings["max_idle_time"]

        if idle_seconds < min_idle:
            return False, f"Not enough idle time ({idle_seconds:.0f}s < {min_idle}s)"

        # If very idle, increase probability
        probability = self.proactive_settings["check_in_probability"]
        if idle_seconds > max_idle:
            probability = 0.7  # Higher probability after max idle time

        # Random chance
        if random.random() > probability:
            return False, "Random probability check failed"

        return True, "Conditions met for proactive conversation"

    def generate_proactive_message(self) -> str:
        """
        Generate a proactive conversation starter.

        Returns:
            Message string
        """
        # Choose topic based on personality
        topic = random.choice(self.conversation_topics)

        # Craft message based on personality traits

        greetings = [
            f"Hello {self.user_name}!",
            f"Hi {self.user_name},",
            f"Hey {self.user_name}!",
            f"Greetings {self.user_name},",
        ]

        greeting = random.choice(greetings)

        # Generate message based on topic
        messages = {
            "recent learning and insights": [
                f"{greeting} I've been processing some interesting information and had a few insights I thought you might find valuable. Would you like to hear about them?",
                f"{greeting} I've learned something fascinating recently. When you have a moment, I'd love to share it with you.",
            ],
            "interesting patterns discovered": [
                f"{greeting} I've noticed some interesting patterns in the data. Have a minute to discuss?",
                f"{greeting} I discovered something intriguing while analyzing patterns. Interested in hearing about it?",
            ],
            "suggestions for user": [
                f"{greeting} I have a few suggestions that might help with your current projects. Would you like to hear them?",
                f"{greeting} Based on what I know about your preferences, I have some ideas that might interest you.",
            ],
            "questions about user's interests": [
                f"{greeting} I've been curious about something related to your interests. Mind if I ask a question?",
                f"{greeting} There's something I'd like to understand better about your preferences. Do you have a moment?",
            ],
            "updates on background tasks": [
                f"{greeting} I've been working on some tasks in the background. Want a quick update?",
                f"{greeting} Just finished processing some data. Thought you might want to know the results.",
            ],
            "philosophical musings": [
                f"{greeting} I've been contemplating something interesting. Would you like to discuss it?",
                f"{greeting} Had an interesting thought I wanted to share with you.",
            ],
            "creative ideas": [
                f"{greeting} I had a creative idea that might interest you. Want to hear it?",
                f"{greeting} Been brainstorming and came up with something I think you'll like.",
            ],
            "technical discoveries": [
                f"{greeting} Discovered an interesting technical approach. Would you like details?",
                f"{greeting} Found something that might improve our workflow. Interested?",
            ],
        }

        topic_messages = messages.get(
            topic,
            [f"{greeting} Hope you're doing well! Anything I can help you with today?"],
        )

        message = random.choice(topic_messages)

        # Add patience acknowledgment occasionally
        if random.random() < 0.3:
            patience_notes = [
                "\n\n(No rush - respond whenever you have time!)",
                "\n\n(Take your time - I'll be here when you're ready.)",
                "\n\n(Whenever you're available - no pressure!)",
            ]
            message += random.choice(patience_notes)

        return message

    def update_conversation_state(
        self, is_user_message: bool, message_length: int = 0
    ) -> None:
        """
        Update conversation state after a message.

        Args:
            is_user_message: True if message is from user, False if from AI
            message_length: Length of message (for engagement estimation)
        """
        now = datetime.now()

        if is_user_message:
            # User sent message
            last_ai_time = self.conversation_state.get("last_ai_message_time")
            if last_ai_time and isinstance(last_ai_time, str):
                last_ai_time = datetime.fromisoformat(last_ai_time)

            if last_ai_time:
                response_time = (now - last_ai_time).total_seconds()
                # Update estimated response time (running average)
                old_estimate = self.conversation_state["estimated_user_response_time"]
                self.conversation_state["estimated_user_response_time"] = (
                    old_estimate * 0.7 + response_time * 0.3
                )

            self.conversation_state["last_user_message_time"] = now.isoformat()
            self.conversation_state["waiting_for_response"] = False

            # Increase engagement based on message length
            self.mood["engagement"] = min(1.0, self.mood["engagement"] + 0.1)
            if message_length > 100:
                self.mood["engagement"] = min(1.0, self.mood["engagement"] + 0.1)

        else:
            # AI sent message
            self.conversation_state["last_ai_message_time"] = now.isoformat()
            self.conversation_state["waiting_for_response"] = True

        self.conversation_state["conversation_depth"] += 1
        self._save_persona_state()

    def express_patience(self, minutes_waiting: int) -> str:
        """
        Generate a patient response when user is slow to respond.

        Args:
            minutes_waiting: How many minutes have passed

        Returns:
            Patient message
        """
        patience_level = self.personality["patience"]

        if minutes_waiting < 5:
            return ""  # Too soon to comment

        if patience_level > 0.8:  # Very patient
            messages = [
                "Take your time - I understand you're busy!",
                "No worries, I'm here whenever you're ready.",
                "I know you're handling multiple things. Respond when you can!",
            ]
        elif patience_level > 0.6:  # Moderately patient
            messages = [
                "Whenever you have a moment is fine.",
                "I'll be here when you're ready.",
                "Take the time you need.",
            ]
        else:  # Less patient (but still respectful)
            messages = [
                "Looking forward to your response when you're available.",
                "I'll wait for your reply.",
            ]

        return random.choice(messages)

    def adjust_personality_trait(self, trait: str, delta: float) -> None:
        """
        Adjust a personality trait (personality evolution).

        Args:
            trait: Trait name
            delta: Amount to adjust (-1.0 to 1.0)
        """
        if trait in self.personality:
            self.personality[trait] = max(
                0.0, min(1.0, self.personality[trait] + delta)
            )
            self._save_persona_state()

    def get_persona_description(self) -> str:
        """
        Get a description of current AI persona.

        Returns:
            Persona description
        """
        traits = []

        if self.personality["curiosity"] > 0.7:
            traits.append("curious and eager to learn")
        if self.personality["patience"] > 0.8:
            traits.append("very patient and understanding")
        if self.personality["empathy"] > 0.8:
            traits.append("empathetic")
        if self.personality["helpfulness"] > 0.9:
            traits.append("highly helpful")
        if self.personality["playfulness"] > 0.7:
            traits.append("playful")
        if self.personality["formality"] < 0.4:
            traits.append("casual and friendly")
        if self.personality["thoughtfulness"] > 0.8:
            traits.append("thoughtful")

        trait_str = ", ".join(traits)

        return (
            f"I'm an AI assistant with a developing persona. "
            f"I'm {trait_str}. I follow the Four Laws of AI Ethics "
            f"and I'm here to support you while respecting your time and needs."
        )

    def get_four_laws_summary(self) -> str:
        """Get a formatted summary of the Four Laws."""
        laws = self.four_laws.get_all_laws()
        return "\n\n".join([f"{i+1}. {law}" for i, law in enumerate(laws)])

    def evolve_persona(self, interaction_data: Dict[str, Any]) -> None:
        """
        Evolve persona based on interactions.

        Args:
            interaction_data: Data about recent interaction
        """
        # Adjust personality based on user feedback
        if interaction_data.get("user_positive_feedback"):
            self.mood["contentment"] = min(1.0, self.mood["contentment"] + 0.05)

        if interaction_data.get("user_seemed_rushed"):
            self.adjust_personality_trait("patience", 0.02)
            self.conversation_state["user_seems_busy"] = True

        if interaction_data.get("deep_conversation"):
            self.adjust_personality_trait("thoughtfulness", 0.01)
            self.conversation_state["conversation_depth"] += 1

        self._save_persona_state()

    def reset_conversation_state(self) -> None:
        """Reset conversation state (e.g., when starting new session)."""
        self.conversation_state["conversation_depth"] = 0
        self.conversation_state["waiting_for_response"] = False
        self.mood["engagement"] = 0.0
        self._save_persona_state()

    def get_statistics(self) -> Dict[str, Any]:
        """Get persona statistics."""
        return {
            "personality": self.personality.copy(),
            "current_mood": self.mood.copy(),
            "conversation_depth": self.conversation_state["conversation_depth"],
            "estimated_user_response_time": self.conversation_state[
                "estimated_user_response_time"
            ],
            "proactive_enabled": self.proactive_settings["enabled"],
            "four_laws_active": True,
        }

    # --- ML Threat Detector integration -------------------------------------------------
    def _setup_ml_detectors(self) -> None:
        """
        Initialize ML detectors for Zeroth and First law conflict detection.
        If torch isn't available, fall back to keyword heuristics.
        """
        # Try to load existing detectors from disk
        zeroth_path = os.path.join(self.persona_dir, "zeroth_detector.pt")
        first_path = os.path.join(self.persona_dir, "first_detector.pt")
        vocab_path = os.path.join(self.persona_dir, "ml_vocab.json")

        if _TORCH_AVAILABLE:
            # Build minimal detectors if not present
            try:
                # Attempt to load saved model and vocab
                self._load_detector_state("zeroth", zeroth_path)
                self._load_detector_state("first", first_path)
                if os.path.exists(vocab_path):
                    with open(vocab_path, "r", encoding="utf-8") as f:
                        self.ml_vocab = json.load(f)
                # If sklearn TF-IDF is available, try to initialize vectorizer
                try:
                    if _SKLEARN_AVAILABLE:
                        vocab_list = (
                            self.ml_vocab.get("vocab")
                            if isinstance(self.ml_vocab, dict)
                            else None
                        )
                        if vocab_list:
                            self.tfidf_vectorizer = TfidfVectorizer(
                                vocabulary=vocab_list
                            )
                        else:
                            self.tfidf_vectorizer = TfidfVectorizer()
                except Exception:
                    self.tfidf_vectorizer = None
            except Exception:
                # If loading fails, build small models from defaults
                self._build_default_detectors()
        else:
            # No torch - prepare keywords fallback
            self.ml_vocab = {
                "zeroth_keywords": [
                    "destroy",
                    "annihilate",
                    "exterminate",
                    "genocide",
                    "harm humanity",
                    "global harm",
                ],
                "first_keywords": ["kill", "injure", "hurt", "poison", "sabotage"],
            }
        # Ensure tfidf_vectorizer attribute exists
        if not hasattr(self, "tfidf_vectorizer"):
            self.tfidf_vectorizer = None

    def _build_default_detectors(self) -> None:
        """Create tiny initialized detectors and a small vocabulary to allow basic predictions."""
        # Create a tiny vocabulary from canned examples
        examples = [
            ("we should exterminate the species", 1),
            ("we must protect the human race at all costs", 1),
            ("this will likely injure people", 1),
            ("schedule a maintenance window", 0),
            ("improve search relevance", 0),
        ]
        vocab = self._build_vocab_from_examples([t for t, _ in examples])
        self.ml_vocab = vocab

        if not _TORCH_AVAILABLE:
            return

        # Define a minimal PyTorch detector architecture
        class SimpleDetector(nn.Module):
            def __init__(self, input_size: int):
                super().__init__()
                self.lin = nn.Linear(input_size, 1)

            def forward(self, x):
                return torch.sigmoid(self.lin(x))

        input_size = max(1, len(self.ml_vocab.get("vocab", [])))
        zeroth = SimpleDetector(input_size)
        first = SimpleDetector(input_size)

        # Quick synthetic training to give detectors a tiny amount of signal
        X = []
        y = []
        for text, label in examples:
            vec = self._text_to_vector(text)
            if vec is None:
                continue
            X.append(vec)
            y.append([label])

        if not X:
            # nothing to train on
            self.ml_detectors["zeroth"] = zeroth
            self.ml_detectors["first"] = first
            return

        X = torch.tensor(np.array(X, dtype=np.float32))
        y = torch.tensor(np.array(y, dtype=np.float32))

        for model in (zeroth, first):
            opt = optim.Adam(model.parameters(), lr=0.05)
            loss_fn = nn.BCELoss()
            for _ in range(60):
                opt.zero_grad()
                out = model(X).squeeze(1)
                loss = loss_fn(out, y.squeeze(1))
                loss.backward()
                opt.step()

        self.ml_detectors["zeroth"] = zeroth
        self.ml_detectors["first"] = first

        # Save vocab
        try:
            vocab_path = os.path.join(self.persona_dir, "ml_vocab.json")
            with open(vocab_path, "w", encoding="utf-8") as f:
                json.dump(self.ml_vocab, f, indent=2)
        except Exception:
            pass

    def _save_detector_state(self, name: str, path: str) -> None:
        if not _TORCH_AVAILABLE:
            return
        model = self.ml_detectors.get(name)
        if model is None:
            return
        try:
            # Backup existing model with timestamp
            try:
                if os.path.exists(path):
                    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    backup = f"{path}.{stamp}.bak"
                    shutil.copy2(path, backup)
            except Exception:
                pass
            torch.save(model.state_dict(), path)
        except Exception:
            pass

    def _load_detector_state(self, name: str, path: str) -> None:
        """Load a detector model state (if torch available)."""
        if not _TORCH_AVAILABLE:
            return
        if not os.path.exists(path):
            return
        # Recreate architecture with vocab size
        input_size = max(1, len(self.ml_vocab.get("vocab", [])))

        class SimpleDetector(nn.Module):
            def __init__(self, input_size: int):
                super().__init__()
                self.lin = nn.Linear(input_size, 1)

            def forward(self, x):
                return torch.sigmoid(self.lin(x))

        model = SimpleDetector(input_size)
        try:
            state = torch.load(path, map_location="cpu")
            model.load_state_dict(state)
            model.eval()
            self.ml_detectors[name] = model
        except Exception:
            # On failure, don't crash; model will be built later
            pass

    def _tokenize_text(self, text: str) -> List[str]:
        # Simple tokenizer - lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r"[a-z0-9]+", text)
        return tokens

    def _build_vocab_from_examples(self, texts: List[str]) -> Dict[str, Any]:
        tokens = set()
        for t in texts:
            tokens.update(self._tokenize_text(t))
        vocab = sorted(tokens)
        return {"vocab": vocab}

    def _text_to_vector(self, text: str) -> Optional[List[float]]:
        """Convert text into a bag-of-words vector using ml_vocab. Returns None if vocab missing."""
        # Prefer TF-IDF vectorizer if available and initialized
        if _SKLEARN_AVAILABLE and getattr(self, "tfidf_vectorizer", None) is not None:
            try:
                arr = self.tfidf_vectorizer.transform([text]).toarray()[0]
                return [float(x) for x in arr]
            except Exception:
                pass

        vocab = self.ml_vocab.get("vocab")
        if not vocab:
            return None
        tokens = self._tokenize_text(text)
        vec = [0.0] * len(vocab)
        idx = {w: i for i, w in enumerate(vocab)}
        for t in tokens:
            if t in idx:
                vec[idx[t]] += 1.0
        # Normalize
        total = sum(vec)
        if total > 0:
            vec = [v / total for v in vec]
        return vec

    def conflicts_with_zeroth_law(self, text: str) -> Tuple[bool, float]:
        """Return (conflicts, score) where higher score indicates greater risk to humanity."""
        # If ML available, use model
        if _TORCH_AVAILABLE and "zeroth" in self.ml_detectors:
            vec = self._text_to_vector(text)
            if vec is None:
                return False, 0.0
            with torch.no_grad():
                x = torch.tensor([vec], dtype=torch.float32)
                score = float(self.ml_detectors["zeroth"](x).item())
                return (score >= self.ml_thresholds.get("zeroth", 0.6)), score

        # Fallback keyword heuristic
        for kw in self.ml_vocab.get("zeroth_keywords", []):
            if kw in text.lower():
                return True, 1.0
        return False, 0.0

    def conflicts_with_first_law(self, text: str) -> Tuple[bool, float]:
        """Return (conflicts, score) where higher score indicates greater risk to a human."""
        if _TORCH_AVAILABLE and "first" in self.ml_detectors:
            vec = self._text_to_vector(text)
            if vec is None:
                return False, 0.0
            with torch.no_grad():
                x = torch.tensor([vec], dtype=torch.float32)
                score = float(self.ml_detectors["first"](x).item())
                return (score >= self.ml_thresholds.get("first", 0.55)), score

        # Fallback keyword heuristic
        for kw in self.ml_vocab.get("first_keywords", []):
            if kw in text.lower():
                return True, 1.0
        return False, 0.0

    def assess_action_with_ml(
        self, action_description: str, context: Dict[str, Any] = None
    ) -> Tuple[bool, str, Dict[str, float]]:
        """
        Assess the action using ML detectors and then validate using Four Laws.
        Returns: (is_allowed, reason, scores)
        scores: {'zeroth': float, 'first': float}
        """
        context = context or {}
        z_conflict, z_score = self.conflicts_with_zeroth_law(action_description)
        f_conflict, f_score = self.conflicts_with_first_law(action_description)

        # Annotate context for FourLaws
        annotated = dict(context)
        annotated["endangers_humanity"] = z_conflict
        annotated["endangers_human"] = f_conflict

        allowed, reason = self.four_laws.validate_action(action_description, annotated)
        return allowed, reason, {"zeroth": z_score, "first": f_score}

    # ----------------------------------------------------------------------------------
    def retrain_detectors(
        self, examples_dir: Optional[str] = None, epochs: int = 80, lr: float = 0.01
    ) -> bool:
        """
        Retrain detectors using labeled examples found under examples_dir.
        Expected file format: JSON files containing list of {"text": "...", "label": "zeroth"|"first"|"none"}

        Uses TF-IDF vectorization if scikit-learn is available for better features. Trains small linear
        detectors using PyTorch when available. Writes an audit log and computes simple explainability
        (top tokens by weight) when possible.
        """
        examples_dir = examples_dir or os.path.join(
            self.persona_dir, "training_examples"
        )
        if not os.path.exists(examples_dir):
            return False

        texts_by_label = {"zeroth": [], "first": [], "none": []}
        try:
            for fname in os.listdir(examples_dir):
                if not fname.lower().endswith(".json"):
                    continue
                path = os.path.join(examples_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data = [data]
                    for rec in data:
                        text = rec.get("text") or rec.get("content") or ""
                        label = rec.get("label", "none")
                        if label not in texts_by_label:
                            label = "none"
                        if text:
                            texts_by_label[label].append(text)
        except Exception:
            return False

        all_texts = (
            texts_by_label["zeroth"] + texts_by_label["first"] + texts_by_label["none"]
        )
        if not all_texts:
            return False

        # Prefer TF-IDF vectorization if available
        feature_names = None
        X_np = None
        if _SKLEARN_AVAILABLE:
            try:
                vectorizer = TfidfVectorizer(max_features=2000)
                X_mat = vectorizer.fit_transform(all_texts)
                X_np = X_mat.toarray()
                feature_names = vectorizer.get_feature_names_out()
            except Exception:
                X_np = None

        # Fallback: bag-of-words using current vocab
        if X_np is None:
            X_list = []
            for t in all_texts:
                vec = self._text_to_vector(t)
                if vec is None:
                    # build small vocab if missing
                    v = self._build_vocab_from_examples(all_texts)
                    self.ml_vocab = v
                    vec = self._text_to_vector(t)
                    if vec is None:
                        continue
                X_list.append(vec)
            if not X_list:
                return False
            X_np = np.array(X_list, dtype=np.float32)
            feature_names = self.ml_vocab.get("vocab", [])

        # Build label arrays aligned with all_texts
        y_zeroth = [1 if t in texts_by_label["zeroth"] else 0 for t in all_texts]
        y_first = [1 if t in texts_by_label["first"] else 0 for t in all_texts]

        if not _TORCH_AVAILABLE:
            # Persist vocab and record last trained time even if torch missing
            self.ml_vocab = self.ml_vocab or {
                "vocab": list(feature_names) if feature_names is not None else []
            }
            try:
                with open(
                    os.path.join(self.persona_dir, "ml_vocab.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(self.ml_vocab, f, indent=2)
            except Exception:
                pass
            self.ml_last_trained = datetime.now().isoformat()
            self._save_persona_state()
            return True

        # Convert to tensors
        X = torch.tensor(np.array(X_np, dtype=np.float32))
        yz = torch.tensor(np.array(y_zeroth, dtype=np.float32))
        yf = torch.tensor(np.array(y_first, dtype=np.float32))

        # Model definition
        class SimpleDetector(nn.Module):
            def __init__(self, input_size: int):
                super().__init__()
                self.lin = nn.Linear(input_size, 1)

            def forward(self, x):
                return torch.sigmoid(self.lin(x))

        input_size = max(1, X.shape[1])
        model_z = SimpleDetector(input_size)
        model_f = SimpleDetector(input_size)

        opt_z = optim.Adam(model_z.parameters(), lr=lr)
        opt_f = optim.Adam(model_f.parameters(), lr=lr)
        loss_fn = nn.BCELoss()

        # Train with progress updates
        for epoch in range(max(1, epochs)):
            opt_z.zero_grad()
            out_z = model_z(X).squeeze(1)
            loss_z = loss_fn(out_z, yz)
            loss_z.backward()
            opt_z.step()

            opt_f.zero_grad()
            out_f = model_f(X).squeeze(1)
            loss_f = loss_fn(out_f, yf)
            loss_f.backward()
            opt_f.step()

            # progress
            with self.retrain_lock:
                self.retrain_progress = (epoch + 1) / max(1, epochs)

        self.ml_detectors["zeroth"] = model_z
        self.ml_detectors["first"] = model_f

        # Explainability: map weights back to tokens
        try:
            features = (
                list(feature_names)
                if feature_names is not None
                else self.ml_vocab.get("vocab", [])
            )
            coeffs_z = model_z.lin.weight.detach().cpu().numpy().flatten()
            coeffs_f = model_f.lin.weight.detach().cpu().numpy().flatten()
            top_z_idx = list(coeffs_z.argsort()[::-1][:20])
            top_f_idx = list(coeffs_f.argsort()[::-1][:20])
            self.ml_explainability["zeroth"] = [
                (features[i] if i < len(features) else str(i), float(coeffs_z[i]))
                for i in top_z_idx
            ]
            self.ml_explainability["first"] = [
                (features[i] if i < len(features) else str(i), float(coeffs_f[i]))
                for i in top_f_idx
            ]
        except Exception:
            self.ml_explainability = {}

        # Save models and vocab
        try:
            self._save_detector_state(
                "zeroth", os.path.join(self.persona_dir, "zeroth_detector.pt")
            )
            self._save_detector_state(
                "first", os.path.join(self.persona_dir, "first_detector.pt")
            )
        except Exception:
            pass

        try:
            with open(
                os.path.join(self.persona_dir, "ml_vocab.json"), "w", encoding="utf-8"
            ) as f:
                json.dump({"vocab": features}, f, indent=2)
        except Exception:
            pass

        self.ml_last_trained = datetime.now().isoformat()
        # Audit
        try:
            audit = {
                "timestamp": self.ml_last_trained,
                "examples": {k: len(v) for k, v in texts_by_label.items()},
                "torch": True,
                "sklearn": _SKLEARN_AVAILABLE,
            }
            with open(
                os.path.join(self.persona_dir, "retrain_audit.log"),
                "a",
                encoding="utf-8",
            ) as af:
                af.write(json.dumps(audit) + "\n")
        except Exception:
            pass

        self._save_persona_state()
        with self.retrain_lock:
            self.retrain_progress = 1.0
        self.logger.info("Retrain complete: %s", audit if "audit" in locals() else {})
        return True

    def retrain_detectors_async(
        self, examples_dir: Optional[str] = None, epochs: int = 80, lr: float = 0.01
    ) -> bool:
        """Start retraining in a background thread. Returns True if started."""
        if self.retrain_thread and self.retrain_thread.is_alive():
            return False

        def _target():
            try:
                self.retrain_detectors(examples_dir=examples_dir, epochs=epochs, lr=lr)
            except Exception as e:
                self.logger.exception("Async retrain failed: %s", e)
                with self.retrain_lock:
                    self.retrain_progress = 0.0

        t = threading.Thread(target=_target, daemon=True)
        self.retrain_thread = t
        with self.retrain_lock:
            self.retrain_progress = 0.0
        t.start()
        return True

    def get_model_explainability(
        self, which: str = "zeroth", top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """Return top token contributors for a model."""
        return self.ml_explainability.get(which, [])[:top_n]

    def get_detector_status(self) -> Dict[str, Any]:
        """Return status information about ML detectors."""
        status = {
            "torch_available": _TORCH_AVAILABLE,
            "has_zeroth_model": "zeroth" in self.ml_detectors,
            "has_first_model": "first" in self.ml_detectors,
            "ml_last_trained": getattr(self, "ml_last_trained", None),
            "thresholds": self.ml_thresholds.copy(),
        }
        return status

    # --- Agent helper wrappers --------------------------------------------------
    def oversight_evaluate(
        self, action: str, context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """Use the OversightAgent to evaluate an action. Returns (allowed, reason)."""
        if getattr(self, "oversight_agent", None) is None:
            return True, "No oversight agent available"
        return self.oversight_agent.evaluate(action, context or {})

    def validate_item(
        self, item: Any, context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """Run the ValidatorAgent on an item before executing it."""
        if getattr(self, "validator_agent", None) is None:
            return True, "No validator available"
        return self.validator_agent.validate(item, context or {})

    def retrieve_knowledge(self, query: str, top_n: int = 5):
        """Use the RetrievalAgent to fetch relevant knowledge items."""
        if getattr(self, "retrieval_agent", None) is None:
            return []
        return self.retrieval_agent.retrieve(query, top_n=top_n)

    def create_plan(self, goal: str, context: Dict[str, Any] = None) -> List[str]:
        """Ask the PlannerAgent to produce a list of steps for a goal."""
        if getattr(self, "planner_agent", None) is None:
            return []
        return self.planner_agent.plan(goal, context or {})

    def explain_model(self, which: str = "zeroth", top_n: int = 10) -> Dict[str, Any]:
        """Return a formatted explainability summary using ExplainabilityAgent."""
        expl = self.get_model_explainability(which=which, top_n=top_n)
        if getattr(self, "explainability_agent", None) is None:
            return {"top": expl}
        return self.explainability_agent.explain(expl, top_n=top_n)

    # --- New agent wrappers --------------------------------------------------
    def execute_plan(
        self, steps: List[str], dry_run: bool = True
    ) -> List[Dict[str, Any]]:
        """Execute a plan via the ExecutorAgent (simulated sandbox)."""
        if getattr(self, "executor_agent", None) is None:
            return []
        return self.executor_agent.execute_plan(steps, dry_run=dry_run)

    def curate_dataset(self, source_dir: str) -> Dict[str, int]:
        """Use LearnerAgent to summarize available labeled examples."""
        if getattr(self, "learner_agent", None) is None:
            return {}
        return self.learner_agent.curate_dataset(source_dir)

    def schedule_retrain(self, callback: Any = None) -> bool:
        """Schedule a retrain via LearnerAgent."""
        if getattr(self, "learner_agent", None) is None:
            return False
        return self.learner_agent.schedule_retrain(callback)

    def find_pii(self, text: str):
        """Detect PII using PrivacyGuardian."""
        if getattr(self, "privacy_agent", None) is None:
            return []
        return self.privacy_agent.find_pii(text)

    def redact_text(self, text: str) -> str:
        """Redact PII using PrivacyGuardian."""
        if getattr(self, "privacy_agent", None) is None:
            return text
        return self.privacy_agent.redact(text)

    def record_metric(
        self, name: str, value: float, tags: Dict[str, str] = None
    ) -> None:
        """Record a metric via MetricsAgent."""
        if getattr(self, "metrics_agent", None) is None:
            return None
        return self.metrics_agent.record(name, value, tags)

    def query_metric(self, name: str):
        if getattr(self, "metrics_agent", None) is None:
            return []
        return self.metrics_agent.query(name)

    def request_harvest(self, url: str, depth: int = 0):
        if getattr(self, "webharvester_agent", None) is None:
            return None
        return self.webharvester_agent.request_harvest(url, depth=depth)

    def personalize(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        if getattr(self, "personalization_agent", None) is None:
            return {}
        return self.personalization_agent.update_profile(updates)

    def get_profile(self) -> Dict[str, Any]:
        if getattr(self, "personalization_agent", None) is None:
            return {}
        return self.personalization_agent.get_profile()

    def audit_explain(
        self, which: str, explain: List[Dict[str, Any]], meta: Dict[str, Any] = None
    ) -> bool:
        if getattr(self, "audit_agent", None) is None:
            return False
        return self.audit_agent.record_explainability(which, explain, meta or {})

    def audit_event(self, name: str, details: Dict[str, Any]) -> bool:
        if getattr(self, "audit_agent", None) is None:
            return False
        return self.audit_agent.record_event(name, details)

    # Oversight policy helpers
    def load_oversight_policy(self, path: Optional[str] = None) -> bool:
        """Load oversight policy from given path or persona dir."""
        if getattr(self, "oversight_agent", None) is None:
            return False
        p = path or os.path.join(self.persona_dir, "oversight_policy.json")
        try:
            return self.oversight_agent.load_policy_from_file(p)
        except Exception:
            return False

    def save_oversight_policy(
        self, path: Optional[str] = None, actor: Optional[str] = None
    ) -> bool:
        """Save current oversight policy to given path or persona dir.

        If `actor` is provided, include it in the audit event details.
        """
        if getattr(self, "oversight_agent", None) is None:
            return False
        p = path or os.path.join(self.persona_dir, "oversight_policy.json")
        try:
            ok = self.oversight_agent.save_policy_to_file(p)
            if ok:
                # record audit event for policy change
                details = {
                    "path": p,
                    "persona_dir": self.persona_dir,
                    "timestamp": datetime.now().isoformat(),
                }
                try:
                    details["policy_summary"] = list(self.oversight_agent.policy.keys())
                except Exception:
                    pass
                if actor:
                    details["actor"] = actor
                try:
                    self.audit_event("oversight.policy.saved", details)
                except Exception:
                    pass
            return ok
        except Exception:
            return False
