"""
Unified intelligence engine combining data analysis, intent detection, and learning paths.

This module consolidates three separate intelligence subsystems:
- Data Analysis: Load, analyze, and visualize tabular data
- Intent Detection: Classify user intents from text using ML
- Learning Paths: Generate personalized learning paths via AI
- Enhanced Intelligence Router: Route queries to knowledge base and function registry
"""

import json
import os

import joblib
import openai
import pandas as pd
from matplotlib.figure import Figure
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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
        if any(word in query_lower for word in ["help", "functions", "tools", "what can you do"]):
            if self.function_registry:
                return {
                    "route": "function_help",
                    "response": self.function_registry.get_help(),
                    "metadata": {
                        "function_count": len(self.function_registry.list_functions()),
                        "categories": self.function_registry.get_categories()
                    }
                }
                
        # Check if query is asking about knowledge/facts
        if any(word in query_lower for word in ["what", "who", "where", "when", "tell me about"]):
            if self.memory_system:
                # Extract key terms for search (simplified approach)
                search_terms = [word for word in query.split() if len(word) > 3]
                if search_terms:
                    results = self.memory_system.query_knowledge(
                        " ".join(search_terms[:3]),  # Use first 3 significant words
                        limit=5
                    )
                    if results:
                        return {
                            "route": "knowledge_query",
                            "response": self._format_knowledge_results(results),
                            "metadata": {
                                "results_count": len(results),
                                "query_terms": search_terms[:3]
                            }
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
                                    "function_info": self.function_registry.get_function_info(func_name)
                                }
                            }
                            
        # Check for conversation history search
        if any(word in query_lower for word in ["remember", "conversation", "history", "discussed"]):
            if self.memory_system:
                search_terms = [word for word in query.split() if len(word) > 3]
                if search_terms:
                    results = self.memory_system.search_conversations(
                        " ".join(search_terms[:3]),
                        limit=5
                    )
                    if results:
                        return {
                            "route": "conversation_search",
                            "response": self._format_conversation_results(results),
                            "metadata": {
                                "results_count": len(results),
                                "query_terms": search_terms[:3]
                            }
                        }
                        
        # Default: general query
        return {
            "route": "general",
            "response": "I can help you with knowledge queries, function calls, and more. Try asking me a question or type 'help' to see available functions.",
            "metadata": {
                "memory_available": self.memory_system is not None,
                "functions_available": self.function_registry is not None
            }
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
            return {
                "success": False,
                "error": "Function registry not available"
            }
            
        try:
            result = self.function_registry.call(function_name, **kwargs)
            return {
                "success": True,
                "result": result,
                "function_name": function_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "function_name": function_name
            }


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
            memory=None
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

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def generate_path(self, interest, skill_level="beginner"):
        """Generate a personalized learning path."""
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

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an educational expert creating learning paths."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            return response.choices[0].message.content
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
