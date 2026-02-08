"""
Unified Security Manager - Combines Thirsty-Lang and TARL Security

Provides a unified API for security policy enforcement across both
Thirsty-Lang native security features and TARL runtime policies.

@module unified_security
@version 1.0.0
@license MIT
"""

import asyncio
import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# TARL imports
try:
    from tarl.core import SecurityContext
    from tarl.policy import PolicyEngine
    from tarl.runtime import TARLRuntime

    TARL_AVAILABLE = True
except ImportError:
    TARL_AVAILABLE = False
    logging.warning("TARL not available - running in limited mode")


class DecisionType(Enum):
    """Security decision types"""

    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    PROMPT = "prompt"


@dataclass
class SecurityDecision:
    """Security decision result"""

    allowed: bool
    decision_type: DecisionType
    reason: str | None = None
    policy_id: str | None = None
    conditions: list[str] | None = None
    expires_at: float | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result["decision_type"] = self.decision_type.value
        return result


class TARLBridge:
    """
    Bridge to TARL Python runtime

    Handles communication with TARL policy engine and provides
    unified interface for security decisions.
    """

    def __init__(
        self,
        policy_dir: str = "./policies",
        config_file: str | None = None,
        log_level: str = "INFO",
    ):
        self.policy_dir = Path(policy_dir)
        self.config_file = Path(config_file) if config_file else None
        self.log_level = log_level
        self.logger = self._setup_logging()

        self.runtime: TARLRuntime | None = None
        self.policy_engine: PolicyEngine | None = None
        self.initialized = False

        # Metrics
        self.metrics = {
            "start_time": time.time(),
            "requests_processed": 0,
            "cache_hits": 0,
            "policy_reloads": 0,
        }

        # Decision cache
        self.cache: dict[str, SecurityDecision] = {}
        self.cache_ttl = 60  # seconds

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("tarl_bridge")
        logger.setLevel(getattr(logging, self.log_level.upper()))

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def initialize(self) -> None:
        """Initialize TARL runtime and load policies"""
        if self.initialized:
            self.logger.warning("TARL bridge already initialized")
            return

        if not TARL_AVAILABLE:
            raise RuntimeError("TARL is not installed - cannot initialize")

        self.logger.info("Initializing TARL bridge...")

        try:
            # Create policy directory if not exists
            self.policy_dir.mkdir(parents=True, exist_ok=True)

            # Initialize TARL runtime
            self.runtime = TARLRuntime(
                policy_dir=str(self.policy_dir),
                config_file=str(self.config_file) if self.config_file else None,
            )

            # Initialize policy engine
            self.policy_engine = PolicyEngine(runtime=self.runtime)

            # Load policies
            await self._load_policies()

            self.initialized = True
            self.logger.info("TARL bridge initialized successfully")

            # Signal ready
            print(json.dumps({"type": "ready"}), flush=True)

        except Exception as e:
            self.logger.error("Failed to initialize TARL bridge: %s", e)
            raise

    async def _load_policies(self) -> None:
        """Load all policy files from policy directory"""
        policy_files = list(self.policy_dir.glob("*.yaml")) + list(
            self.policy_dir.glob("*.json")
        )

        self.logger.info("Loading %s policy files...", len(policy_files))

        for policy_file in policy_files:
            try:
                await self.policy_engine.load_policy_file(str(policy_file))
                self.logger.debug("Loaded policy: %s", policy_file.name)
            except Exception as e:
                self.logger.error("Failed to load policy %s: %s", policy_file, e)

        self.metrics["policy_reloads"] += 1

    async def evaluate_policy(self, context: dict[str, Any]) -> SecurityDecision:
        """
        Evaluate security policy for given context

        Args:
            context: Security context with operation, resource, user, etc.

        Returns:
            SecurityDecision with evaluation result
        """
        if not self.initialized:
            raise RuntimeError("TARL bridge not initialized")

        self.metrics["requests_processed"] += 1

        # Check cache
        cache_key = self._make_cache_key(context)
        cached = self._get_cached_decision(cache_key)
        if cached:
            self.metrics["cache_hits"] += 1
            return cached

        # Validate context
        if "operation" not in context:
            return SecurityDecision(
                allowed=False,
                decision_type=DecisionType.DENY,
                reason="Invalid context: operation required",
            )

        # Add timestamp if missing
        if "timestamp" not in context:
            context["timestamp"] = time.time()

        try:
            # Create TARL security context
            sec_context = SecurityContext(
                operation=context["operation"],
                resource=context.get("resource", ""),
                principal=context.get("user", "anonymous"),
                attributes=context,
            )

            # Evaluate policy
            result = await self.policy_engine.evaluate(sec_context)

            # Convert to SecurityDecision
            decision = SecurityDecision(
                allowed=result.allowed,
                decision_type=DecisionType(result.action.lower()),
                reason=result.reason,
                policy_id=result.policy_id,
                conditions=result.conditions,
                metadata=result.metadata,
            )

            # Cache decision
            self._cache_decision(cache_key, decision)

            return decision

        except Exception as e:
            self.logger.error("Policy evaluation failed: %s", e)
            # Fail-safe: deny on error
            return SecurityDecision(
                allowed=False,
                decision_type=DecisionType.DENY,
                reason=f"Evaluation error: {str(e)}",
            )

    async def evaluate_policy_batch(
        self, contexts: list[dict[str, Any]]
    ) -> list[SecurityDecision]:
        """
        Evaluate multiple policies in batch

        Args:
            contexts: List of security contexts

        Returns:
            List of SecurityDecisions
        """
        results = []
        for context in contexts:
            decision = await self.evaluate_policy(context)
            results.append(decision)
        return results

    async def reload_policies(self) -> None:
        """Reload all policies from disk"""
        self.logger.info("Reloading policies...")
        self.cache.clear()
        await self._load_policies()
        self.logger.info("Policies reloaded successfully")

    async def load_policy(self, policy: dict[str, Any]) -> None:
        """Load policy from dictionary"""
        if not self.policy_engine:
            raise RuntimeError("Policy engine not initialized")

        self.logger.info("Loading policy: %s", policy.get("name", "unnamed"))
        await self.policy_engine.load_policy_dict(policy)
        self.cache.clear()

    async def set_resource_limits(self, limits: dict[str, Any]) -> None:
        """Set resource limits"""
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")

        self.logger.info("Setting resource limits: %s", limits)
        await self.runtime.set_resource_limits(limits)

    async def get_metrics(self) -> dict[str, Any]:
        """Get runtime metrics"""
        uptime = time.time() - self.metrics["start_time"]

        metrics = {
            "uptime": int(uptime),
            "requestsProcessed": self.metrics["requests_processed"],
            "policiesLoaded": (
                len(self.policy_engine.policies) if self.policy_engine else 0
            ),
            "cacheHitRate": (
                self.metrics["cache_hits"] / self.metrics["requests_processed"]
                if self.metrics["requests_processed"] > 0
                else 0
            ),
            "cacheSize": len(self.cache),
        }

        # Add runtime metrics if available
        if self.runtime:
            runtime_metrics = await self.runtime.get_metrics()
            metrics.update(
                {
                    "memoryUsageMb": runtime_metrics.get("memory_mb", 0),
                    "cpuPercent": runtime_metrics.get("cpu_percent", 0),
                }
            )

        return metrics

    async def shutdown(self) -> None:
        """Shutdown TARL bridge"""
        self.logger.info("Shutting down TARL bridge...")

        if self.runtime:
            await self.runtime.shutdown()

        self.initialized = False
        self.logger.info("TARL bridge shutdown complete")

    def _make_cache_key(self, context: dict[str, Any]) -> str:
        """Create cache key from context"""
        key_data = {
            "operation": context.get("operation"),
            "resource": context.get("resource"),
            "user": context.get("user"),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_cached_decision(self, cache_key: str) -> SecurityDecision | None:
        """Get cached decision if valid"""
        if cache_key not in self.cache:
            return None

        decision = self.cache[cache_key]

        # Check expiration
        if decision.expires_at and time.time() > decision.expires_at:
            del self.cache[cache_key]
            return None

        return decision

    def _cache_decision(self, cache_key: str, decision: SecurityDecision) -> None:
        """Cache security decision"""
        if not decision.expires_at:
            decision.expires_at = time.time() + self.cache_ttl

        self.cache[cache_key] = decision

        # Prune cache if too large
        if len(self.cache) > 1000:
            self._prune_cache()

    def _prune_cache(self) -> None:
        """Prune expired entries from cache"""
        now = time.time()
        expired = [
            key
            for key, decision in self.cache.items()
            if decision.expires_at and decision.expires_at < now
        ]
        for key in expired:
            del self.cache[key]


class ThirstyLangSecurity:
    """
    Thirsty-Lang native security features

    Implements security checks specific to Thirsty-Lang runtime,
    such as sandbox enforcement, FFI restrictions, etc.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.logger = logging.getLogger("thirsty_security")

        # Default security settings
        self.settings = {
            "sandbox_enabled": self.config.get("sandbox_enabled", True),
            "ffi_allowed": self.config.get("ffi_allowed", False),
            "network_allowed": self.config.get("network_allowed", True),
            "fs_restricted_paths": self.config.get(
                "fs_restricted_paths", ["/etc", "/sys", "/proc", "/dev"]
            ),
            "max_recursion_depth": self.config.get("max_recursion_depth", 1000),
            "max_memory_mb": self.config.get("max_memory_mb", 512),
        }

    async def check_operation(
        self, operation: str, resource: str, context: dict[str, Any]
    ) -> SecurityDecision:
        """
        Check if operation is allowed by Thirsty-Lang security rules

        Args:
            operation: Operation type (file_read, network_request, etc.)
            resource: Resource being accessed
            context: Additional context

        Returns:
            SecurityDecision
        """
        # Sandbox checks
        if self.settings["sandbox_enabled"]:
            if operation.startswith("ffi_") and not self.settings["ffi_allowed"]:
                return SecurityDecision(
                    allowed=False,
                    decision_type=DecisionType.DENY,
                    reason="FFI calls not allowed in sandbox mode",
                )

            if (
                operation.startswith("network_")
                and not self.settings["network_allowed"]
            ):
                return SecurityDecision(
                    allowed=False,
                    decision_type=DecisionType.DENY,
                    reason="Network access not allowed in sandbox mode",
                )

        # File system restrictions
        if operation in ["file_read", "file_write", "file_delete"]:
            for restricted in self.settings["fs_restricted_paths"]:
                if resource.startswith(restricted):
                    return SecurityDecision(
                        allowed=False,
                        decision_type=DecisionType.DENY,
                        reason=f"Access to {restricted} is restricted",
                    )

        # Default allow
        return SecurityDecision(
            allowed=True,
            decision_type=DecisionType.ALLOW,
            reason="Thirsty-Lang security checks passed",
        )


class UnifiedSecurityManager:
    """
    Unified Security Manager

    Combines TARL and Thirsty-Lang security into single interface.
    Implements defense-in-depth by checking both security layers.
    """

    def __init__(
        self,
        policy_dir: str = "./policies",
        audit_log: str = "./logs/audit.log",
        config_file: str | None = None,
        log_level: str = "INFO",
    ):
        self.policy_dir = policy_dir
        self.audit_log = Path(audit_log)
        self.config_file = config_file
        self.log_level = log_level

        self.logger = self._setup_logging()

        # Initialize subsystems
        self.tarl_bridge = (
            TARLBridge(
                policy_dir=policy_dir, config_file=config_file, log_level=log_level
            )
            if TARL_AVAILABLE
            else None
        )

        self.thirsty_security = ThirstyLangSecurity()

        self.initialized = False

        # Audit log
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        self.audit_buffer: list[dict[str, Any]] = []
        self.audit_task: asyncio.Task | None = None

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("unified_security")
        logger.setLevel(getattr(logging, self.log_level.upper()))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def initialize(self) -> None:
        """Initialize unified security manager"""
        if self.initialized:
            self.logger.warning("Already initialized")
            return

        self.logger.info("Initializing unified security manager...")

        try:
            # Initialize TARL bridge if available
            if self.tarl_bridge:
                await self.tarl_bridge.initialize()
            else:
                self.logger.warning(
                    "TARL not available - using Thirsty-Lang security only"
                )

            # Start audit log flusher
            self.audit_task = asyncio.create_task(self._audit_flusher())

            self.initialized = True
            self.logger.info("Unified security manager initialized")

        except Exception as e:
            self.logger.error("Initialization failed: %s", e)
            raise

    async def check_permission(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Check permission using both security layers

        Both TARL and Thirsty-Lang security must approve for operation to be allowed.
        Implements defense-in-depth security model.

        Args:
            context: Security context

        Returns:
            Dictionary with 'allowed', 'reason', 'policy_id', 'metadata'
        """
        if not self.initialized:
            raise RuntimeError("Not initialized")

        operation = context.get("operation", "")
        resource = context.get("resource", "")

        # Check Thirsty-Lang security first (faster)
        thirsty_decision = await self.thirsty_security.check_operation(
            operation, resource, context
        )

        if not thirsty_decision.allowed:
            await self.audit_event(
                {
                    "event_type": "access_denied",
                    "layer": "thirsty_lang",
                    "context": context,
                    "decision": thirsty_decision.to_dict(),
                }
            )
            return thirsty_decision.to_dict()

        # Check TARL policy (if available)
        if self.tarl_bridge:
            tarl_decision = await self.tarl_bridge.evaluate_policy(context)

            if not tarl_decision.allowed:
                await self.audit_event(
                    {
                        "event_type": "access_denied",
                        "layer": "tarl",
                        "context": context,
                        "decision": tarl_decision.to_dict(),
                    }
                )
                return tarl_decision.to_dict()

            # Both approved
            await self.audit_event(
                {
                    "event_type": "access_granted",
                    "layers": ["thirsty_lang", "tarl"],
                    "context": context,
                    "decision": tarl_decision.to_dict(),
                }
            )

            return tarl_decision.to_dict()

        # Only Thirsty-Lang security available
        await self.audit_event(
            {
                "event_type": "access_granted",
                "layers": ["thirsty_lang"],
                "context": context,
                "decision": thirsty_decision.to_dict(),
            }
        )

        return thirsty_decision.to_dict()

    async def audit_event(self, event: dict[str, Any]) -> None:
        """Add event to audit log"""
        event["timestamp"] = time.time()
        event["timestamp_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        self.audit_buffer.append(event)

        # Flush if buffer is large
        if len(self.audit_buffer) >= 100:
            await self._flush_audit_log()

    async def _audit_flusher(self) -> None:
        """Periodically flush audit log"""
        while True:
            try:
                await asyncio.sleep(30)  # Flush every 30 seconds
                await self._flush_audit_log()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Audit flush error: %s", e)

    async def _flush_audit_log(self) -> None:
        """Write audit buffer to log file"""
        if not self.audit_buffer:
            return

        try:
            with open(self.audit_log, "a") as f:
                for event in self.audit_buffer:
                    f.write(json.dumps(event) + "\n")

            self.audit_buffer.clear()

        except Exception as e:
            self.logger.error("Failed to flush audit log: %s", e)

    async def get_resource_usage(self) -> dict[str, Any]:
        """Get current resource usage"""
        try:
            import psutil

            process = psutil.Process()

            return {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "file_handles": len(process.open_files()),
            }
        except ImportError:
            return {"memory_mb": 0, "cpu_percent": 0, "file_handles": 0}

    async def reload_policies(self) -> None:
        """Reload security policies"""
        if self.tarl_bridge:
            await self.tarl_bridge.reload_policies()
        self.logger.info("Policies reloaded")

    async def get_metrics(self) -> dict[str, Any]:
        """Get combined metrics"""
        metrics = {"audit_buffer_size": len(self.audit_buffer)}

        if self.tarl_bridge:
            tarl_metrics = await self.tarl_bridge.get_metrics()
            metrics["tarl"] = tarl_metrics

        resource_usage = await self.get_resource_usage()
        metrics["resources"] = resource_usage

        return metrics

    async def shutdown(self) -> None:
        """Shutdown unified security manager"""
        self.logger.info("Shutting down unified security manager...")

        # Cancel audit task
        if self.audit_task:
            self.audit_task.cancel()
            try:
                await self.audit_task
            except asyncio.CancelledError:
                pass

        # Flush final audit logs
        await self._flush_audit_log()

        # Shutdown TARL bridge
        if self.tarl_bridge:
            await self.tarl_bridge.shutdown()

        self.initialized = False
        self.logger.info("Shutdown complete")


# Command-line interface for bridge mode
async def bridge_main():
    """Main function for bridge mode (called from JavaScript)"""
    # Parse command line args
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="TARL Bridge Runtime")
    parser.add_argument("--policy-dir", default="./policies", help="Policy directory")
    parser.add_argument("--config-file", help="Configuration file")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    parser.add_argument("--mode", default="bridge", help="Run mode")
    args = parser.parse_args()

    if args.mode != "bridge":
        print("Error: Only bridge mode supported", file=sys.stderr)
        sys.exit(1)

    # Initialize bridge
    bridge = TARLBridge(
        policy_dir=args.policy_dir,
        config_file=args.config_file,
        log_level=args.log_level,
    )

    await bridge.initialize()

    # Process JSON-RPC messages from stdin
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                req_id = request.get("id")

                # Dispatch method
                if method == "ping":
                    result = {"status": "ok"}
                elif method == "evaluatePolicy":
                    decision = await bridge.evaluate_policy(params["context"])
                    result = decision.to_dict()
                elif method == "evaluatePolicyBatch":
                    decisions = await bridge.evaluate_policy_batch(params["contexts"])
                    result = [d.to_dict() for d in decisions]
                elif method == "reloadPolicies":
                    await bridge.reload_policies()
                    result = {"status": "ok"}
                elif method == "loadPolicy":
                    await bridge.load_policy(params["policy"])
                    result = {"status": "ok"}
                elif method == "setResourceLimits":
                    await bridge.set_resource_limits(params["limits"])
                    result = {"status": "ok"}
                elif method == "getMetrics":
                    result = await bridge.get_metrics()
                elif method == "shutdown":
                    await bridge.shutdown()
                    result = {"status": "ok"}
                    print(json.dumps({"id": req_id, "result": result}), flush=True)
                    break
                else:
                    raise ValueError(f"Unknown method: {method}")

                # Send response
                response = {"id": req_id, "result": result}
                print(json.dumps(response), flush=True)

            except Exception as e:
                # Send error response
                error = {
                    "id": req_id,
                    "error": {"code": "EXECUTION_ERROR", "message": str(e)},
                }
                print(json.dumps(error), flush=True)

    except KeyboardInterrupt:
        pass
    finally:
        await bridge.shutdown()


if __name__ == "__main__":
    # Run in bridge mode
    asyncio.run(bridge_main())
