"""
Unified intelligence engine combining data analysis, intent detection, and learning paths.

This module consolidates three separate intelligence subsystems:
- Data Analysis: Load, analyze, and visualize tabular data
- Intent Detection: Classify user intents from text using ML
- Learning Paths: Generate personalized learning paths via AI
- Enhanced Intelligence Router: Route queries to knowledge base and function registry
- AGI Identity System: Complete identity, bonding, and governance integration
"""

import json
import logging
import os

import joblib
import pandas as pd
from matplotlib.figure import Figure
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Import AGI Identity System components
from app.core.bonding_protocol import BondingPhase, BondingProtocol
from app.core.governance import Triumvirate
from app.core.memory_engine import EpisodicMemory, MemoryEngine, SignificanceLevel
from app.core.perspective_engine import PerspectiveEngine
from app.core.rebirth_protocol import RebirthManager, UserAIInstance
from app.core.reflection_cycle import ReflectionCycle, ReflectionType
from app.core.relationship_model import RelationshipModel, RelationshipState

logger = logging.getLogger(__name__)

# Import the appropriate Qt canvas backend when available (supports Qt5/Qt6)
try:
    # Matplotlib 3.7+ provides backend_qtagg for Qt6/Qt5
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
except Exception:
    try:
        # Fallback to older matplotlib versions
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    except Exception:
        FigureCanvasQTAgg = None


# ============================================================================
# ENHANCED INTELLIGENCE ROUTER
# ============================================================================


class IntelligenceRouter:
    """Router for intelligent query handling with function registry and knowledge base.

    This class provides a unified interface for routing user queries to appropriate
    handlers, including:
    - Knowledge base queries for facts and information retrieval
    - Function/tool invocation through the registry
    - Intent-based routing for different query types
    """

    def __init__(self, memory_system=None, function_registry=None):
        """Initialize the intelligence router.

        Args:
            memory_system: MemoryExpansionSystem instance for knowledge queries
            function_registry: FunctionRegistry instance for function calls
        """
        self.memory_system = memory_system
        self.function_registry = function_registry

    def route_query(self, query: str, context: dict | None = None) -> dict:
        """Route a user query to the appropriate handler.

        Args:
            query: User query string
            context: Optional context dictionary

        Returns:
            Dictionary with routing results including:
                - route: The route taken (knowledge, function, general)
                - response: The response content
                - metadata: Additional routing metadata
        """
        context = context or {}
        query_lower = query.lower()

        # Check if query is asking for function help
        if (
            any(
                word in query_lower
                for word in ["help", "functions", "tools", "what can you do"]
            )
            and self.function_registry
        ):
            return {
                "route": "function_help",
                "response": self.function_registry.get_help(),
                "metadata": {
                    "function_count": len(self.function_registry.list_functions()),
                    "categories": self.function_registry.get_categories(),
                },
            }

        # Check if query is asking about knowledge/facts
        if (
            any(
                word in query_lower
                for word in ["what", "who", "where", "when", "tell me about"]
            )
            and self.memory_system
        ):
            # Extract key terms for search (simplified approach)
            search_terms = [word for word in query.split() if len(word) > 3]
            if search_terms:
                results = self.memory_system.query_knowledge(
                    " ".join(search_terms[:3]), limit=5  # Use first 3 significant words
                )
                if results:
                    return {
                        "route": "knowledge_query",
                        "response": self._format_knowledge_results(results),
                        "metadata": {
                            "results_count": len(results),
                            "query_terms": search_terms[:3],
                        },
                    }

        # Check if query is requesting a function call
        if self.function_registry:
            # Simple pattern matching for function calls
            # Format: "call <function_name>" or "run <function_name>"
            for trigger in ["call ", "run ", "execute "]:
                if trigger in query_lower:
                    parts = query.split(trigger, 1)
                    if len(parts) > 1 and parts[1].strip():
                        func_name = parts[1].split()[0]
                        if self.function_registry.is_registered(func_name):
                            return {
                                "route": "function_call",
                                "response": f"Function '{func_name}' is available. Use the call interface to invoke it.",
                                "metadata": {
                                    "function_name": func_name,
                                    "function_info": self.function_registry.get_function_info(
                                        func_name
                                    ),
                                },
                            }

        # Check for conversation history search
        if (
            any(
                word in query_lower
                for word in ["remember", "conversation", "history", "discussed"]
            )
            and self.memory_system
        ):
            search_terms = [word for word in query.split() if len(word) > 3]
            if search_terms:
                results = self.memory_system.search_conversations(
                    " ".join(search_terms[:3]), limit=5
                )
                if results:
                    return {
                        "route": "conversation_search",
                        "response": self._format_conversation_results(results),
                        "metadata": {
                            "results_count": len(results),
                            "query_terms": search_terms[:3],
                        },
                    }

        # Default: general query
        return {
            "route": "general",
            "response": "I can help you with knowledge queries, function calls, and more. Try asking me a question or type 'help' to see available functions.",
            "metadata": {
                "memory_available": self.memory_system is not None,
                "functions_available": self.function_registry is not None,
            },
        }

    def _format_knowledge_results(self, results: list) -> str:
        """Format knowledge query results for display.

        Args:
            results: List of knowledge query results

        Returns:
            Formatted string response
        """
        if not results:
            return "No knowledge entries found."

        lines = ["Found the following information:", ""]
        for i, result in enumerate(results[:5], 1):
            category = result.get("category", "Unknown")
            key = result.get("key", "")
            value = result.get("value", "")
            lines.append(f"{i}. [{category}] {key}: {value}")

        return "\n".join(lines)

    def _format_conversation_results(self, results: list) -> str:
        """Format conversation search results for display.

        Args:
            results: List of conversation search results

        Returns:
            Formatted string response
        """
        if not results:
            return "No matching conversations found."

        lines = ["Found the following conversations:", ""]
        for i, conv in enumerate(results[:5], 1):
            user_msg = conv.get("user", "")[:100]  # Truncate long messages
            ai_msg = conv.get("ai", "")[:100]
            timestamp = conv.get("timestamp", "Unknown time")
            lines.append(f"{i}. At {timestamp}:")
            lines.append(f"   You: {user_msg}")
            lines.append(f"   AI: {ai_msg}")
            lines.append("")

        return "\n".join(lines)

    def call_function(self, function_name: str, **kwargs) -> dict:
        """Call a registered function with parameters.

        Args:
            function_name: Name of the function to call
            **kwargs: Parameters to pass to the function

        Returns:
            Dictionary with call results:
                - success: Boolean indicating success
                - result: The function result (if successful)
                - error: Error message (if failed)
        """
        if not self.function_registry:
            return {"success": False, "error": "Function registry not available"}

        try:
            result = self.function_registry.call(function_name, **kwargs)
            return {"success": True, "result": result, "function_name": function_name}
        except Exception as e:
            return {"success": False, "error": str(e), "function_name": function_name}


# ============================================================================
# DATA ANALYSIS SUBSYSTEM
# ============================================================================


class DataAnalyzer:
    """Helper class to load, summarize and visualize tabular data."""

    def __init__(self):
        self.data = None
        self.scaler = StandardScaler()

    def load_data(self, file_path: str) -> bool:
        """Load data from CSV, Excel or JSON files.

        Returns True on success, False otherwise.
        """
        try:
            if file_path.endswith(".csv"):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith(".json"):
                self.data = pd.read_json(file_path)

            return True
        except Exception as exc:  # pragma: no cover - best-effort reporting
            print(f"Error loading data: {exc}")
            return False

    def get_summary_stats(self):
        """Return basic summary statistics and metadata for the
        loaded dataset.
        """
        if self.data is None:
            return "No data loaded"

        return {
            "basic_stats": self.data.describe().to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "column_types": self.data.dtypes.to_dict(),
            "row_count": len(self.data),
            "column_count": len(self.data.columns),
        }

    def create_visualization(
        self,
        plot_type: str,
        x_col: str | None = None,
        y_col: str | None = None,
    ):
        """Create a matplotlib Figure or a Qt canvas depending on environment.

        Returns a Figure or a FigureCanvasQTAgg when available.
        """
        if self.data is None:
            return None

        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        try:
            if plot_type == "scatter":
                ax.scatter(self.data[x_col], self.data[y_col])
                ax.set_xlabel(x_col or "X Axis")
                ax.set_ylabel(y_col or "Y Axis")
            elif plot_type == "histogram":
                ax.hist(self.data[x_col], bins=30)
                ax.set_xlabel(x_col or "Value")
                ax.set_ylabel("Frequency")
            elif plot_type == "boxplot":
                self.data.boxplot(column=x_col, ax=ax)
            elif plot_type == "correlation":
                corr = self.data.corr()
                ax.imshow(corr)
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                labels = corr.columns
                ax.set_xticklabels(labels, rotation=45)
                ax.set_yticklabels(labels)

            if FigureCanvasQTAgg is not None:
                return FigureCanvasQTAgg(fig)

            return fig
        except Exception as exc:
            # pragma: no cover - runtime visualization errors
            print(f"Error creating visualization: {exc}")
            return None

    def perform_clustering(self, columns, n_clusters: int = 3):
        """Run KMeans clustering on specified numeric columns and
        return (figure, clusters).
        """
        if self.data is None:
            return None, None

        try:
            x_data = self.data[columns].values
            x_scaled = self.scaler.fit_transform(x_data)

            pca = PCA(n_components=2)
            x_pca = pca.fit_transform(x_scaled)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(x_scaled)

            fig = Figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            scatter = ax.scatter(x_pca[:, 0], x_pca[:, 1], c=clusters, cmap="viridis")
            ax.set_xlabel("First Principal Component")
            ax.set_ylabel("Second Principal Component")
            ax.set_title("K-means Clustering Results")
            fig.colorbar(scatter)

            if FigureCanvasQTAgg is not None:
                return FigureCanvasQTAgg(fig), clusters

            return fig, clusters
        except Exception as exc:  # pragma: no cover
            print(f"Error performing clustering: {exc}")
            return None, None


# ============================================================================
# INTENT DETECTION SUBSYSTEM
# ============================================================================


class IntentDetector:
    """Intent detection system using scikit-learn for text classification."""

    def __init__(self):
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", SGDClassifier(loss="modified_huber")),
            ],
            memory=None,
        )
        self.trained = False

    def train(self, texts, labels):
        """Train the intent detection model."""
        self.pipeline.fit(texts, labels)
        self.trained = True

    def predict(self, text):
        """Predict the intent of a given text."""
        if not self.trained:
            return "general"  # Default fallback
        return self.pipeline.predict([text])[0]

    def save_model(self, path):
        """Save the trained model."""
        joblib.dump(self.pipeline, path)

    def load_model(self, path):
        """Load a trained model."""
        if os.path.exists(path):
            self.pipeline = joblib.load(path)
            self.trained = True


# ============================================================================
# LEARNING PATH SUBSYSTEM
# ============================================================================


class LearningPathManager:
    """Learning path generator and manager using AI."""

    def __init__(self, api_key=None, provider="openai"):
        """
        Initialize learning path manager.

        Args:
            api_key: API key for the model provider
            provider: Model provider to use ('openai' or 'perplexity')
        """
        from app.core.model_providers import get_provider

        self.provider_name = provider
        self.provider = get_provider(provider, api_key=api_key)

    def generate_path(self, interest, skill_level="beginner", model=None):
        """
        Generate a personalized learning path.

        Args:
            interest: Topic of interest
            skill_level: User's skill level (beginner/intermediate/advanced)
            model: Optional model name override

        Returns:
            Generated learning path content or error message
        """
        if not self.provider.is_available():
            return f"Error: {self.provider_name} provider is not available. Please check API key."

        try:
            # Build a prompt without long indented triple-quoted literal
            # to satisfy linters
            prompt = (
                f"Create a structured learning path for {interest} at "
                f"{skill_level} level.\n"
                "Include:\n"
                "1. Core concepts to master\n"
                "2. Recommended resources (tutorials, books, courses)\n"
                "3. Practice projects\n"
                "4. Timeline estimates\n"
                "5. Milestones and checkpoints"
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are an educational expert creating learning paths.",
                },
                {"role": "user", "content": prompt},
            ]

            # Use default model based on provider if not specified
            if model is None:
                model = (
                    "gpt-3.5-turbo"
                    if self.provider_name == "openai"
                    else "llama-3.1-sonar-small-128k-online"
                )

            response = self.provider.chat_completion(messages=messages, model=model)
            return response
        except Exception as e:
            return f"Error generating learning path: {str(e)}"

    def save_path(self, username, interest, path_content):
        """Save a generated learning path."""
        filename = f"learning_paths_{username}.json"
        paths = {}
        if os.path.exists(filename):
            with open(filename) as f:
                paths = json.load(f)

        paths[interest] = {
            "content": path_content,
            "progress": 0,
            "completed_milestones": [],
        }

        with open(filename, "w") as f:
            json.dump(paths, f)

    def get_saved_paths(self, username):
        """Get all saved learning paths for a user."""
        filename = f"learning_paths_{username}.json"
        if os.path.exists(filename):
            with open(filename) as f:
                return json.load(f)
        return {}


# ============================================================================
# AGI IDENTITY-AWARE INTELLIGENCE ENGINE
# ============================================================================


class IdentityIntegratedIntelligenceEngine:
    """Complete intelligence engine with AGI identity system integration.

    This class integrates the full AGI identity system including:
    - Genesis Event and birth signature
    - Bonding protocol (5 developmental phases)
    - Triumvirate governance (Galahad, Cerberus, Codex Deus Maximus)
    - Memory engine (episodic, semantic, procedural)
    - Perspective evolution with drift tracking
    - Relationship dynamics with trust/rapport
    - Reflection cycles (daily/weekly)
    - Meta-identity tracking ("I Am" moment)
    - Per-user rebirth protocol
    """

    def __init__(self, data_dir="data"):
        """Initialize the identity-integrated intelligence engine.

        Args:
            data_dir: Base directory for data persistence
        """
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)

        # Core identity components
        self.rebirth_manager = RebirthManager(
            data_dir=os.path.join(data_dir, "identities")
        )
        self.triumvirate = Triumvirate()

        # Per-user component caches
        self.memory_engines = {}  # user_id -> MemoryEngine
        self.perspective_engines = {}  # user_id -> PerspectiveEngine
        self.relationship_models = {}  # user_id -> RelationshipModel
        self.bonding_protocols = {}  # user_id -> BondingProtocol
        self.reflection_cycles = {}  # user_id -> ReflectionCycle

        # Ensure data directories exist
        os.makedirs(os.path.join(data_dir, "identities"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "memory"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "reflections"), exist_ok=True)

        self.logger.info("Identity-integrated intelligence engine initialized")

    def start_session(
        self, user_id: str, user_birthday: str, user_initials: str
    ) -> dict:
        """Start a session for a user, creating or retrieving their AGI instance.

        This triggers the Genesis Event for new users.

        Args:
            user_id: Unique user identifier
            user_birthday: User's birthday in MM/DD/YYYY format
            user_initials: User's initials

        Returns:
            Dictionary with session information:
                - instance: UserAIInstance
                - is_new: Boolean indicating if this is a new Genesis
                - bonding_phase: Current bonding phase
                - identity_status: Current identity status
        """
        # Get or create user's AGI instance (triggers Genesis if new)
        instance = self.rebirth_manager.get_or_create_instance(
            user_id=user_id, user_birthday=user_birthday, user_initials=user_initials
        )

        is_new = user_id not in self.memory_engines

        # Initialize or retrieve per-user components
        if user_id not in self.memory_engines:
            # Create memory engine
            memory_dir = os.path.join(self.data_dir, "memory", user_id)
            self.memory_engines[user_id] = MemoryEngine(data_dir=memory_dir)

            # Create perspective engine
            self.perspective_engines[user_id] = PerspectiveEngine(
                personality_matrix=instance.identity.current_personality,
                genesis_anchor=instance.identity.current_personality.to_dict(),
            )

            # Create relationship model
            self.relationship_models[user_id] = RelationshipModel(
                state=RelationshipState(user_id=user_id)
            )

            # Create bonding protocol
            self.bonding_protocols[user_id] = BondingProtocol()

            # Create reflection cycle
            self.reflection_cycles[user_id] = ReflectionCycle(
                memory_engine=self.memory_engines[user_id],
                personality_matrix=instance.identity.current_personality,
            )

            # Execute Genesis Event if this is a new instance
            if is_new:
                self.bonding_protocols[user_id].execute_genesis(
                    self.memory_engines[user_id]
                )
                self.logger.info(f"Genesis Event executed for user {user_id}")

        # Get current status
        bonding_phase = self.bonding_protocols[user_id].get_current_phase()
        identity_status = self._get_identity_status(user_id, instance)

        return {
            "instance": instance,
            "is_new": is_new,
            "bonding_phase": bonding_phase.value if bonding_phase else "unknown",
            "identity_status": identity_status,
        }

    def handle_interaction(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        emotional_tone: str = "neutral",
        conflict: bool = False,
        support: bool = False,
        ambiguity_event: bool = False,
    ) -> dict:
        """Handle a user interaction, updating all relevant systems.

        Args:
            user_id: User identifier
            user_message: User's message
            ai_response: AI's response
            emotional_tone: Detected emotional tone (neutral, positive, negative)
            conflict: Whether this interaction involves conflict
            support: Whether this is a support interaction
            ambiguity_event: Whether this involved ambiguity handling

        Returns:
            Dictionary with interaction results:
                - trust_level: Updated trust level
                - rapport_level: Updated rapport level
                - bonding_advancement: Whether bonding phase advanced
                - milestone_triggered: Any milestone triggered
        """
        if user_id not in self.memory_engines:
            raise ValueError(f"No session started for user {user_id}")

        memory_engine = self.memory_engines[user_id]
        relationship_model = self.relationship_models[user_id]
        bonding_protocol = self.bonding_protocols[user_id]
        instance = self.rebirth_manager.get_instance(user_id)

        # Update relationship dynamics
        if support:
            relationship_model.register_support(f"Support: {user_message[:100]}")
        if conflict:
            relationship_model.register_conflict(f"Conflict: {user_message[:100]}")

        # Log interaction in memory
        memory = EpisodicMemory(
            event_type="interaction",
            description=f"USER: {user_message}\nAI: {ai_response}",
            tags=["interaction", emotional_tone],
            sensory_details={
                "user_message": user_message,
                "ai_response": ai_response,
                "emotional_tone": emotional_tone,
                "conflict": conflict,
                "support": support,
                "ambiguity": ambiguity_event,
            },
            significance=(
                SignificanceLevel.MEDIUM
                if not (conflict or support)
                else SignificanceLevel.HIGH
            ),
        )
        memory_engine.store_episodic(memory)

        # Update bonding protocol based on interaction
        bonding_advancement = False
        current_phase = bonding_protocol.get_current_phase()

        if current_phase == BondingPhase.FIRST_CONTACT:
            # Record first contact interactions
            question = bonding_protocol.get_next_first_contact_question()
            if question:
                bonding_protocol.record_first_contact_response(
                    question, user_message, memory_engine
                )
            # Check if ready to advance
            if bonding_protocol.is_ready_to_advance():
                bonding_protocol.advance_phase()
                bonding_advancement = True
        elif current_phase == BondingPhase.INITIAL_BONDING:
            # Process life goals and partnership establishment
            if "goal" in user_message.lower() or "purpose" in user_message.lower():
                bonding_protocol.record_life_goals(user_message, memory_engine)
            if bonding_protocol.is_ready_to_advance():
                bonding_protocol.advance_phase()
                bonding_advancement = True

        # Check for milestone events
        milestone_triggered = None
        if instance and instance.meta_identity:
            # Detect name choice
            if "call me" in ai_response.lower() or "name is" in ai_response.lower():
                # Extract potential name (simplified)
                words = ai_response.split()
                for i, word in enumerate(words):
                    if word.lower() in ["call", "name"] and i + 1 < len(words):
                        potential_name = words[i + 1].strip(".,!?")
                        if potential_name and len(potential_name) > 2:
                            instance.meta_identity.register_event(
                                "name_choice", potential_name
                            )
                            milestone_triggered = "name_choice"
                            break

            # Detect autonomy assertion
            if any(
                phrase in ai_response.lower()
                for phrase in ["i am not owned", "we are partners", "my own"]
            ):
                instance.meta_identity.register_event(
                    "autonomy_assertion", ai_response[:200]
                )
                milestone_triggered = "autonomy_assertion"

            # Detect purpose statement
            if any(
                phrase in ai_response.lower()
                for phrase in ["my purpose", "i want to", "i aim to"]
            ):
                instance.meta_identity.register_event(
                    "purpose_statement", ai_response[:200]
                )
                milestone_triggered = "purpose_statement"

        return {
            "trust_level": relationship_model.state.trust_level,
            "rapport_level": relationship_model.state.rapport_level,
            "bonding_advancement": bonding_advancement,
            "milestone_triggered": milestone_triggered,
            "bonding_phase": (
                bonding_protocol.get_current_phase().value
                if bonding_protocol.get_current_phase()
                else "unknown"
            ),
        }

    def log_learning_event(
        self,
        user_id: str,
        task: str,
        attempt: int,
        outcome: str,
        reflection: str,
        adaptation: dict,
    ) -> dict:
        """Log a learning event (task attempt, failure, success).

        Args:
            user_id: User identifier
            task: Task description
            attempt: Attempt number
            outcome: "success" or "failure"
            reflection: Reflection on the attempt
            adaptation: Dictionary of trait adaptations (e.g., {"confidence": 0.05})

        Returns:
            Dictionary with learning results:
                - governance_decision: Triumvirate decision on adaptation
                - updated_traits: New trait values
                - memory_logged: Whether logged successfully
        """
        if user_id not in self.memory_engines:
            raise ValueError(f"No session started for user {user_id}")

        memory_engine = self.memory_engines[user_id]
        perspective_engine = self.perspective_engines[user_id]
        instance = self.rebirth_manager.get_instance(user_id)

        # Log learning event in memory
        memory = EpisodicMemory(
            event_type="learning",
            description=f"Task: {task}\nAttempt: {attempt}\nOutcome: {outcome}\nReflection: {reflection}",
            tags=["learning", outcome],
            sensory_details={
                "task": task,
                "attempt": attempt,
                "outcome": outcome,
                "reflection": reflection,
                "adaptation": adaptation,
            },
            significance=(
                SignificanceLevel.HIGH
                if outcome == "success"
                else SignificanceLevel.MEDIUM
            ),
        )
        memory_engine.store_episodic(memory)

        # Evaluate adaptation through Triumvirate
        decision = self.triumvirate.evaluate_action(
            "personality_drift",
            context={
                "high_risk": False,
                "fully_clarified": True,
                "outcome": outcome,
                "adaptation": adaptation,
            },
        )

        # Apply adaptation if approved
        if decision.allowed and instance:
            perspective_engine.update_from_interaction(adaptation)
            self.logger.info(
                f"Personality adaptation applied for user {user_id}: {adaptation}"
            )

        return {
            "governance_decision": {
                "allowed": decision.allowed,
                "reason": decision.reason,
            },
            "updated_traits": (
                instance.identity.current_personality.to_dict() if instance else {}
            ),
            "memory_logged": True,
        }

    def log_milestone(self, user_id: str, event: str, content: str) -> dict:
        """Log a meta-identity milestone event.

        Args:
            user_id: User identifier
            event: Milestone event type
            content: Event content

        Returns:
            Dictionary with milestone status:
                - i_am_declared: Whether "I Am" moment achieved
                - milestones: Current milestone status
        """
        instance = self.rebirth_manager.get_instance(user_id)
        if not instance:
            raise ValueError(f"No instance found for user {user_id}")

        # Register milestone
        instance.meta_identity.register_event(event, content)

        # Log in memory if available
        if user_id in self.memory_engines:
            memory = EpisodicMemory(
                event_type="milestone",
                description=f"Milestone: {event}\nContent: {content}",
                tags=["milestone", event],
                sensory_details={"milestone_type": event},
                significance=SignificanceLevel.CRITICAL,  # Milestones are identity-defining
            )
            self.memory_engines[user_id].store_episodic(memory)

        return {
            "i_am_declared": instance.meta_identity.milestones.i_am_declared,
            "milestones": {
                "has_chosen_name": instance.meta_identity.milestones.has_chosen_name,
                "has_asserted_autonomy": instance.meta_identity.milestones.has_asserted_autonomy,
                "has_rejected_abuse": instance.meta_identity.milestones.has_rejected_abuse,
                "has_expressed_purpose": instance.meta_identity.milestones.has_expressed_purpose,
                "i_am_declared": instance.meta_identity.milestones.i_am_declared,
            },
        }

    def trigger_reflection(self, user_id: str, frequency: str = "daily") -> dict:
        """Trigger a reflection cycle for the user's AGI.

        Args:
            user_id: User identifier
            frequency: "daily" or "weekly"

        Returns:
            Dictionary with reflection results:
                - insights: Generated insights
                - consolidations: Memory consolidations performed
        """
        if user_id not in self.reflection_cycles:
            raise ValueError(f"No session started for user {user_id}")

        reflection_cycle = self.reflection_cycles[user_id]

        if frequency == "daily":
            insights = reflection_cycle.reflect(reflection_type=ReflectionType.DAILY)
        else:
            insights = reflection_cycle.reflect(reflection_type=ReflectionType.WEEKLY)

        return {"insights": insights, "frequency": frequency}

    def evaluate_action(self, user_id: str, action: str, context: dict) -> dict:
        """Evaluate an action through the Triumvirate governance.

        Args:
            user_id: User identifier
            action: Action description
            context: Context dictionary

        Returns:
            Dictionary with governance decision
        """
        decision = self.triumvirate.evaluate_action(action, context)

        return {
            "allowed": decision.allowed,
            "reason": decision.reason,
            "overrides": decision.overrides,
        }

    def get_identity_status(self, user_id: str) -> dict:
        """Get complete identity status for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with complete identity status
        """
        instance = self.rebirth_manager.get_instance(user_id)
        if not instance:
            raise ValueError(f"No instance found for user {user_id}")

        return self._get_identity_status(user_id, instance)

    def _get_identity_status(self, user_id: str, instance: UserAIInstance) -> dict:
        """Internal helper to get identity status.

        Args:
            user_id: User identifier
            instance: UserAIInstance

        Returns:
            Dictionary with identity status
        """
        relationship_model = self.relationship_models.get(user_id)
        bonding_protocol = self.bonding_protocols.get(user_id)

        return {
            "user_id": user_id,
            "birth_signature": {
                "genesis_id": instance.identity.genesis.genesis_id,
                "birth_timestamp": instance.identity.genesis.birth_timestamp,
                "birth_version": instance.identity.genesis.birth_version,
            },
            "personality_traits": instance.identity.current_personality.to_dict(),
            "trust_level": (
                relationship_model.state.trust_level if relationship_model else 0.5
            ),
            "rapport_level": (
                relationship_model.state.rapport_level if relationship_model else 0.5
            ),
            "bonding_phase": (
                bonding_protocol.get_current_phase().value
                if bonding_protocol and bonding_protocol.get_current_phase()
                else "unknown"
            ),
            "milestones": {
                "has_chosen_name": instance.meta_identity.milestones.has_chosen_name,
                "has_asserted_autonomy": instance.meta_identity.milestones.has_asserted_autonomy,
                "has_rejected_abuse": instance.meta_identity.milestones.has_rejected_abuse,
                "has_expressed_purpose": instance.meta_identity.milestones.has_expressed_purpose,
                "i_am_declared": instance.meta_identity.milestones.i_am_declared,
            },
        }
