#!/usr/bin/env python3
"""
Polyglot AI Execution Engine - Section 6
Project-AI God Tier Zombie Apocalypse Defense Engine

Multi-backend AI execution with intelligent routing and fallback.

Features:
- OpenAI API integration (GPT-4, GPT-3.5-turbo, GPT-4-turbo)
- HuggingFace transformers integration (local inference)
- Model orchestration and intelligent routing
- Automatic fail-safe and fallback mechanisms
- Performance monitoring and cost optimization
- Response caching with TTL
- Rate limiting and quota management
- Streaming support for real-time responses
- Fine-tuning support and model adaptation
"""

import hashlib
import logging
import os
import queue
import sqlite3
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core.interface_abstractions import (
    BaseSubsystem,
    IConfigurable,
    IMonitorable,
    IObservable,
)

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import openai
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available")

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        StoppingCriteria,
        StoppingCriteriaList,
        pipeline,
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available")


# ============================================================================
# ENUMS AND DATACLASSES
# ============================================================================


class ModelBackend(Enum):
    """Available model backends"""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    FALLBACK = "fallback"


class ModelTier(Enum):
    """Model capability tiers"""

    PREMIUM = "premium"  # GPT-4, large models
    STANDARD = "standard"  # GPT-3.5, medium models
    ECONOMY = "economy"  # Small local models
    OFFLINE = "offline"  # Air-gapped local models


class ExecutionStatus(Enum):
    """Execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"
    RATE_LIMITED = "rate_limited"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""

    model_id: str
    backend: ModelBackend
    tier: ModelTier
    model_name: str
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    cost_per_1k_tokens: float = 0.0
    latency_estimate_ms: float = 1000.0
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRequest:
    """AI execution request"""

    request_id: str
    prompt: str
    system_prompt: str | None = None
    model_preference: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7
    stream: bool = False
    priority: int = 5
    timeout_seconds: float = 30.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResponse:
    """AI execution response"""

    request_id: str
    response_text: str
    model_used: str
    backend_used: ModelBackend
    status: ExecutionStatus
    tokens_used: int
    latency_ms: float
    cost_estimate: float
    cached: bool = False
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """Performance metrics for a model"""

    model_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    last_used: float = 0.0


# ============================================================================
# POLYGLOT EXECUTION ENGINE
# ============================================================================


class PolyglotExecutionEngine(BaseSubsystem, IConfigurable, IMonitorable, IObservable):
    """
    Multi-backend AI execution engine with intelligent routing.

    Orchestrates multiple AI backends (OpenAI, HuggingFace) with automatic
    fallback, caching, rate limiting, and cost optimization.
    """

    SUBSYSTEM_METADATA = {
        "id": "polyglot_execution_engine",
        "name": "Polyglot AI Execution Engine",
        "version": "1.0.0",
        "priority": "HIGH",
        "dependencies": [],
        "provides_capabilities": [
            "ai_inference",
            "multi_backend_routing",
            "model_orchestration",
            "response_caching",
            "cost_optimization",
            "streaming_inference",
        ],
        "config": {},
    }

    def __init__(self, data_dir: str = "data", config: dict[str, Any] = None):
        """Initialize polyglot execution engine"""
        super().__init__(data_dir, config)

        # Data persistence
        self.state_dir = os.path.join(data_dir, "polyglot_ai")
        os.makedirs(self.state_dir, exist_ok=True)
        self.db_path = os.path.join(self.state_dir, "ai_execution.db")

        # Model registry
        self.models: dict[str, ModelConfig] = {}
        self.model_metrics: dict[str, ModelMetrics] = defaultdict(
            lambda: ModelMetrics(model_id="")
        )

        # Backend clients
        self.openai_client: Any | None = None
        self.hf_models: dict[str, Any] = {}
        self.hf_tokenizers: dict[str, Any] = {}

        # Request queue and execution
        self.request_queue = queue.PriorityQueue()
        self.active_requests: dict[str, ExecutionRequest] = {}

        # Response caching
        self.cache: dict[str, tuple[ExecutionResponse, float]] = {}
        self.cache_ttl = 3600  # 1 hour
        self.cache_max_size = 1000

        # Rate limiting
        self.rate_limits: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = {
            ModelBackend.OPENAI: 60,
            ModelBackend.HUGGINGFACE: 100,
            ModelBackend.LOCAL: 1000,
        }

        # Fallback chain
        self.fallback_chain: list[str] = []

        # Event subscribers
        self.subscribers: dict[str, list[tuple[str, Callable]]] = defaultdict(list)

        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cached_responses": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency_ms": 0.0,
            "cache_hit_rate": 0.0,
            "fallback_activations": 0,
        }

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.worker_threads: list[threading.Thread] = []

        self._init_database()
        self._initialize_backends()
        self._register_default_models()

        self.logger.info("Polyglot execution engine initialized")

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS executions (
                request_id TEXT PRIMARY KEY,
                prompt TEXT,
                response TEXT,
                model_used TEXT,
                backend TEXT,
                status TEXT,
                tokens_used INTEGER,
                latency_ms REAL,
                cost REAL,
                timestamp REAL,
                metadata TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS model_metrics (
                model_id TEXT PRIMARY KEY,
                total_requests INTEGER,
                successful_requests INTEGER,
                failed_requests INTEGER,
                total_tokens INTEGER,
                total_cost REAL,
                avg_latency_ms REAL,
                cache_hit_rate REAL,
                last_used REAL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                cache_key TEXT PRIMARY KEY,
                response_data TEXT,
                timestamp REAL
            )
        """
        )

        conn.commit()
        conn.close()

    def _initialize_backends(self):
        """Initialize AI backend clients"""
        # OpenAI
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.logger.info("OpenAI client initialized")
                except Exception as e:
                    self.logger.error("Failed to initialize OpenAI: %s", e)

        # HuggingFace (initialized on-demand)
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning(
                "Transformers not available - HuggingFace backend disabled"
            )

    def _register_default_models(self):
        """Register default model configurations"""
        # OpenAI models
        if OPENAI_AVAILABLE:
            self.register_model(
                ModelConfig(
                    model_id="gpt-4",
                    backend=ModelBackend.OPENAI,
                    tier=ModelTier.PREMIUM,
                    model_name="gpt-4",
                    max_tokens=4096,
                    cost_per_1k_tokens=0.03,
                    latency_estimate_ms=2000.0,
                )
            )

            self.register_model(
                ModelConfig(
                    model_id="gpt-4-turbo",
                    backend=ModelBackend.OPENAI,
                    tier=ModelTier.PREMIUM,
                    model_name="gpt-4-turbo-preview",
                    max_tokens=4096,
                    cost_per_1k_tokens=0.01,
                    latency_estimate_ms=1500.0,
                )
            )

            self.register_model(
                ModelConfig(
                    model_id="gpt-3.5-turbo",
                    backend=ModelBackend.OPENAI,
                    tier=ModelTier.STANDARD,
                    model_name="gpt-3.5-turbo",
                    max_tokens=4096,
                    cost_per_1k_tokens=0.001,
                    latency_estimate_ms=1000.0,
                )
            )

        # HuggingFace models (local inference)
        if TRANSFORMERS_AVAILABLE:
            self.register_model(
                ModelConfig(
                    model_id="gpt2",
                    backend=ModelBackend.HUGGINGFACE,
                    tier=ModelTier.ECONOMY,
                    model_name="gpt2",
                    max_tokens=1024,
                    cost_per_1k_tokens=0.0,
                    latency_estimate_ms=500.0,
                )
            )

        # Setup fallback chain
        self.fallback_chain = ["gpt-4-turbo", "gpt-3.5-turbo", "gpt2"]

    # ========================================================================
    # CORE SUBSYSTEM INTERFACE
    # ========================================================================

    def initialize(self) -> bool:
        """Initialize the execution engine"""
        try:
            self.logger.info("Initializing polyglot execution engine")
            self.running = True

            # Start worker threads
            self.worker_threads = [
                threading.Thread(target=self._execution_worker, daemon=True),
                threading.Thread(target=self._cache_cleanup_worker, daemon=True),
                threading.Thread(target=self._metrics_aggregation_worker, daemon=True),
            ]

            for thread in self.worker_threads:
                thread.start()

            self._initialized = True
            self.logger.info("Polyglot execution engine initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to initialize polyglot engine: %s", e)
            return False

    def shutdown(self) -> bool:
        """Shutdown the execution engine"""
        try:
            self.logger.info("Shutting down polyglot execution engine")
            self.running = False

            # Unload HuggingFace models
            for model_name in list(self.hf_models.keys()):
                self._unload_hf_model(model_name)

            # Wait for threads
            for thread in self.worker_threads:
                thread.join(timeout=5)

            self.executor.shutdown(wait=True)
            self._initialized = False

            self.logger.info("Polyglot execution engine shutdown complete")
            return True

        except Exception as e:
            self.logger.error("Error during shutdown: %s", e)
            return False

    def health_check(self) -> bool:
        """Perform health check"""
        if not self._initialized or not self.running:
            return False

        # Check worker threads
        alive_threads = sum(1 for t in self.worker_threads if t.is_alive())
        if alive_threads < len(self.worker_threads):
            self.logger.warning("Only %s/%s workers alive", alive_threads, len(self.worker_threads))
            return False

        # Check if at least one backend is available
        if not self.openai_client and not self.hf_models:
            self.logger.warning("No backends available")
            return False

        return True

    def get_status(self) -> dict[str, Any]:
        """Get current status"""
        status = super().get_status()
        status.update(
            {
                "registered_models": len(self.models),
                "loaded_hf_models": len(self.hf_models),
                "active_requests": len(self.active_requests),
                "cache_size": len(self.cache),
                "openai_available": self.openai_client is not None,
                "hf_available": TRANSFORMERS_AVAILABLE,
                "metrics": self.metrics,
            }
        )
        return status

    # ========================================================================
    # MODEL MANAGEMENT
    # ========================================================================

    def register_model(self, config: ModelConfig) -> bool:
        """Register a model configuration"""
        try:
            self.models[config.model_id] = config
            self.logger.info("Registered model: %s (%s)", config.model_id, config.backend.value)
            return True
        except Exception as e:
            self.logger.error("Failed to register model: %s", e)
            return False

    def _load_hf_model(self, model_name: str) -> bool:
        """Load a HuggingFace model into memory"""
        if not TRANSFORMERS_AVAILABLE:
            return False

        try:
            if model_name in self.hf_models:
                return True

            self.logger.info("Loading HuggingFace model: %s", model_name)

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=(
                    torch.float16 if torch.cuda.is_available() else torch.float32
                ),
                device_map="auto" if torch.cuda.is_available() else None,
            )

            self.hf_tokenizers[model_name] = tokenizer
            self.hf_models[model_name] = model

            self.logger.info("Successfully loaded: %s", model_name)
            return True

        except Exception as e:
            self.logger.error("Failed to load HuggingFace model %s: %s", model_name, e)
            return False

    def _unload_hf_model(self, model_name: str):
        """Unload a HuggingFace model from memory"""
        try:
            if model_name in self.hf_models:
                del self.hf_models[model_name]
                del self.hf_tokenizers[model_name]

                if torch and torch.cuda.is_available():
                    torch.cuda.empty_cache()

                self.logger.info("Unloaded HuggingFace model: %s", model_name)
        except Exception as e:
            self.logger.error("Failed to unload model %s: %s", model_name, e)

    # ========================================================================
    # EXECUTION API
    # ========================================================================

    def execute(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
        timeout: float = 30.0,
    ) -> ExecutionResponse:
        """
        Execute AI inference request.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Preferred model ID
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Enable streaming response
            timeout: Request timeout in seconds

        Returns:
            ExecutionResponse with generated text
        """
        import secrets

        request = ExecutionRequest(
            request_id=secrets.token_hex(8),
            prompt=prompt,
            system_prompt=system_prompt,
            model_preference=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            timeout_seconds=timeout,
        )

        self.metrics["total_requests"] += 1

        # Check cache
        cache_key = self._generate_cache_key(request)
        cached_response = self._get_cached_response(cache_key)

        if cached_response:
            self.metrics["cached_responses"] += 1
            self.metrics["cache_hit_rate"] = (
                self.metrics["cached_responses"] / self.metrics["total_requests"]
            )
            cached_response.cached = True
            return cached_response

        # Select model
        selected_model = self._select_model(request)
        if not selected_model:
            return ExecutionResponse(
                request_id=request.request_id,
                response_text="",
                model_used="none",
                backend_used=ModelBackend.FALLBACK,
                status=ExecutionStatus.FAILED,
                tokens_used=0,
                latency_ms=0.0,
                cost_estimate=0.0,
                error="No available models",
            )

        # Execute with selected model
        start_time = time.time()

        try:
            if selected_model.backend == ModelBackend.OPENAI:
                response = self._execute_openai(request, selected_model)
            elif selected_model.backend == ModelBackend.HUGGINGFACE:
                response = self._execute_huggingface(request, selected_model)
            else:
                raise ValueError(f"Unsupported backend: {selected_model.backend}")

            latency = (time.time() - start_time) * 1000

            response.latency_ms = latency
            response.model_used = selected_model.model_id
            response.backend_used = selected_model.backend
            response.status = ExecutionStatus.COMPLETED

            # Cache response
            self._cache_response(cache_key, response)

            # Update metrics
            self._update_metrics(selected_model.model_id, response)
            self.metrics["successful_requests"] += 1

            # Update average latency
            self.metrics["avg_latency_ms"] = (
                0.9 * self.metrics["avg_latency_ms"] + 0.1 * latency
            )

            return response

        except Exception as e:
            self.logger.error("Execution failed: %s", e)
            self.metrics["failed_requests"] += 1

            # Try fallback
            fallback_response = self._execute_with_fallback(
                request, selected_model.model_id
            )
            if fallback_response:
                return fallback_response

            return ExecutionResponse(
                request_id=request.request_id,
                response_text="",
                model_used=selected_model.model_id,
                backend_used=selected_model.backend,
                status=ExecutionStatus.FAILED,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                cost_estimate=0.0,
                error=str(e),
            )

    def execute_async(self, request: ExecutionRequest) -> str:
        """Queue request for asynchronous execution"""
        self.request_queue.put((request.priority, request))
        self.active_requests[request.request_id] = request
        return request.request_id

    def get_result(
        self, request_id: str, timeout: float = 30.0
    ) -> ExecutionResponse | None:
        """Get result of asynchronous request"""
        # Placeholder - would implement result retrieval
        return None

    # ========================================================================
    # BACKEND EXECUTION
    # ========================================================================

    def _execute_openai(
        self, request: ExecutionRequest, model: ModelConfig
    ) -> ExecutionResponse:
        """Execute request using OpenAI API"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not available")

        # Check rate limit
        if not self._check_rate_limit(ModelBackend.OPENAI):
            raise RuntimeError("Rate limit exceeded for OpenAI")

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        try:
            completion = self.openai_client.chat.completions.create(
                model=model.model_name,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream,
            )

            if request.stream:
                # Handle streaming
                response_text = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                tokens_used = len(response_text.split())  # Rough estimate
            else:
                response_text = completion.choices[0].message.content
                tokens_used = completion.usage.total_tokens

            cost = (tokens_used / 1000) * model.cost_per_1k_tokens

            return ExecutionResponse(
                request_id=request.request_id,
                response_text=response_text,
                model_used=model.model_id,
                backend_used=ModelBackend.OPENAI,
                status=ExecutionStatus.COMPLETED,
                tokens_used=tokens_used,
                latency_ms=0.0,  # Set by caller
                cost_estimate=cost,
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI execution failed: {e}")

    def _execute_huggingface(
        self, request: ExecutionRequest, model: ModelConfig
    ) -> ExecutionResponse:
        """Execute request using HuggingFace transformers"""
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("Transformers not available")

        # Load model if not already loaded
        if not self._load_hf_model(model.model_name):
            raise RuntimeError(f"Failed to load model: {model.model_name}")

        tokenizer = self.hf_tokenizers[model.model_name]
        hf_model = self.hf_models[model.model_name]

        try:
            # Prepare input
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

            inputs = tokenizer(full_prompt, return_tensors="pt")

            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate
            with torch.no_grad():
                outputs = hf_model.generate(
                    **inputs,
                    max_new_tokens=request.max_tokens,
                    temperature=request.temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )

            response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove input prompt from response
            if response_text.startswith(full_prompt):
                response_text = response_text[len(full_prompt) :].strip()

            tokens_used = len(outputs[0])

            return ExecutionResponse(
                request_id=request.request_id,
                response_text=response_text,
                model_used=model.model_id,
                backend_used=ModelBackend.HUGGINGFACE,
                status=ExecutionStatus.COMPLETED,
                tokens_used=tokens_used,
                latency_ms=0.0,  # Set by caller
                cost_estimate=0.0,  # Local inference is free
            )

        except Exception as e:
            raise RuntimeError(f"HuggingFace execution failed: {e}")

    # ========================================================================
    # MODEL SELECTION AND FALLBACK
    # ========================================================================

    def _select_model(self, request: ExecutionRequest) -> ModelConfig | None:
        """Select best model for request"""
        # If model preference specified
        if request.model_preference and request.model_preference in self.models:
            model = self.models[request.model_preference]
            if model.enabled:
                return model

        # Select based on availability and tier
        available_models = [m for m in self.models.values() if m.enabled]

        if not available_models:
            return None

        # Sort by tier (premium first) and latency
        available_models.sort(key=lambda m: (m.tier.value, m.latency_estimate_ms))

        # Check if backend is available
        for model in available_models:
            if (
                model.backend == ModelBackend.OPENAI
                and self.openai_client
                or model.backend == ModelBackend.HUGGINGFACE
                and TRANSFORMERS_AVAILABLE
            ):
                return model

        return None

    def _execute_with_fallback(
        self, request: ExecutionRequest, failed_model_id: str
    ) -> ExecutionResponse | None:
        """Execute request with fallback chain"""
        self.metrics["fallback_activations"] += 1

        # Try fallback chain
        for model_id in self.fallback_chain:
            if model_id == failed_model_id or model_id not in self.models:
                continue

            model = self.models[model_id]
            if not model.enabled:
                continue

            try:
                self.logger.info("Trying fallback model: %s", model_id)

                if model.backend == ModelBackend.OPENAI:
                    response = self._execute_openai(request, model)
                elif model.backend == ModelBackend.HUGGINGFACE:
                    response = self._execute_huggingface(request, model)
                else:
                    continue

                response.metadata["fallback"] = True
                response.metadata["original_model"] = failed_model_id

                self.logger.info("Fallback successful with %s", model_id)
                return response

            except Exception as e:
                self.logger.error("Fallback model %s failed: %s", model_id, e)
                continue

        return None

    # ========================================================================
    # CACHING
    # ========================================================================

    def _generate_cache_key(self, request: ExecutionRequest) -> str:
        """Generate cache key for request"""
        cache_data = f"{request.prompt}|{request.system_prompt}|{request.max_tokens}|{request.temperature}"
        return hashlib.sha256(cache_data.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> ExecutionResponse | None:
        """Get cached response if available and not expired"""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]

            # Check expiry
            if time.time() - timestamp < self.cache_ttl:
                self.logger.info("Cache hit")
                return response
            else:
                # Remove expired entry
                del self.cache[cache_key]

        return None

    def _cache_response(self, cache_key: str, response: ExecutionResponse):
        """Cache response"""
        # Enforce max cache size
        if len(self.cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        self.cache[cache_key] = (response, time.time())

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    def _check_rate_limit(self, backend: ModelBackend) -> bool:
        """Check if backend is within rate limit"""
        current_time = time.time()

        # Clean old entries
        self.rate_limits[backend.value] = deque(
            [
                t
                for t in self.rate_limits[backend.value]
                if current_time - t < self.rate_limit_window
            ],
            maxlen=self.rate_limit_max[backend],
        )

        # Check limit
        if len(self.rate_limits[backend.value]) >= self.rate_limit_max[backend]:
            self.logger.warning("Rate limit exceeded for %s", backend.value)
            return False

        self.rate_limits[backend.value].append(current_time)
        return True

    # ========================================================================
    # WORKER THREADS
    # ========================================================================

    def _execution_worker(self):
        """Process execution request queue"""
        while self.running:
            try:
                priority, request = self.request_queue.get(timeout=1)

                # Execute request
                response = self.execute(
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    model=request.model_preference,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    stream=request.stream,
                    timeout=request.timeout_seconds,
                )

                # Store result (would implement result storage)
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error("Execution worker error: %s", e)

    def _cache_cleanup_worker(self):
        """Clean up expired cache entries"""
        while self.running:
            try:
                current_time = time.time()
                expired_keys = [
                    key
                    for key, (_, timestamp) in self.cache.items()
                    if current_time - timestamp > self.cache_ttl
                ]

                for key in expired_keys:
                    del self.cache[key]

                self.logger.info("Cache cleanup: removed %s expired entries", len(expired_keys))

                time.sleep(300)  # Every 5 minutes

            except Exception as e:
                self.logger.error("Cache cleanup worker error: %s", e)

    def _metrics_aggregation_worker(self):
        """Aggregate and persist metrics"""
        while self.running:
            try:
                # Persist model metrics
                for model_id, metrics in self.model_metrics.items():
                    self._persist_model_metrics(metrics)

                time.sleep(60)  # Every minute

            except Exception as e:
                self.logger.error("Metrics aggregation worker error: %s", e)

    # ========================================================================
    # METRICS AND PERSISTENCE
    # ========================================================================

    def _update_metrics(self, model_id: str, response: ExecutionResponse):
        """Update metrics for model"""
        metrics = self.model_metrics[model_id]
        metrics.model_id = model_id
        metrics.total_requests += 1

        if response.status == ExecutionStatus.COMPLETED:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        metrics.total_tokens += response.tokens_used
        metrics.total_cost += response.cost_estimate

        # Update average latency
        metrics.avg_latency_ms = (
            0.9 * metrics.avg_latency_ms + 0.1 * response.latency_ms
        )

        metrics.last_used = time.time()

        # Update global metrics
        self.metrics["total_tokens"] += response.tokens_used
        self.metrics["total_cost"] += response.cost_estimate

    def _persist_model_metrics(self, metrics: ModelMetrics):
        """Persist model metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO model_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics.model_id,
                    metrics.total_requests,
                    metrics.successful_requests,
                    metrics.failed_requests,
                    metrics.total_tokens,
                    metrics.total_cost,
                    metrics.avg_latency_ms,
                    metrics.cache_hit_rate,
                    metrics.last_used,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error("Failed to persist metrics: %s", e)

    # ========================================================================
    # INTERFACE IMPLEMENTATIONS
    # ========================================================================

    def get_config(self) -> dict[str, Any]:
        """Get current configuration"""
        return {
            "cache_ttl": self.cache_ttl,
            "cache_max_size": self.cache_max_size,
            "rate_limits": {k.value: v for k, v in self.rate_limit_max.items()},
            "fallback_chain": self.fallback_chain,
            "models": {k: v.__dict__ for k, v in self.models.items()},
        }

    def set_config(self, config: dict[str, Any]) -> bool:
        """Update configuration"""
        try:
            if "cache_ttl" in config:
                self.cache_ttl = config["cache_ttl"]
            if "cache_max_size" in config:
                self.cache_max_size = config["cache_max_size"]
            if "fallback_chain" in config:
                self.fallback_chain = config["fallback_chain"]
            return True
        except Exception as e:
            self.logger.error("Failed to set config: %s", e)
            return False

    def validate_config(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """Validate configuration"""
        if "cache_ttl" in config and config["cache_ttl"] <= 0:
            return False, "cache_ttl must be positive"
        if "cache_max_size" in config and config["cache_max_size"] <= 0:
            return False, "cache_max_size must be positive"
        return True, None

    def subscribe(self, event_type: str, callback: Callable) -> str:
        """Subscribe to events"""
        import secrets

        sub_id = secrets.token_hex(8)
        self.subscribers[event_type].append((sub_id, callback))
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        for event_type, subs in self.subscribers.items():
            self.subscribers[event_type] = [
                (sid, cb) for sid, cb in subs if sid != subscription_id
            ]
        return True

    def emit_event(self, event_type: str, data: Any) -> int:
        """Emit event to subscribers"""
        count = 0
        for sub_id, callback in self.subscribers.get(event_type, []):
            try:
                callback(data)
                count += 1
            except Exception as e:
                self.logger.error("Event callback failed: %s", e)
        return count

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

    def get_metric(self, metric_name: str) -> Any:
        """Get specific metric"""
        return self.metrics.get(metric_name)

    def reset_metrics(self) -> bool:
        """Reset all metrics"""
        for key in self.metrics:
            if isinstance(self.metrics[key], (int, float)):
                self.metrics[key] = 0 if isinstance(self.metrics[key], int) else 0.0
        return True
