"""Agent security and encapsulation for adversarial control.

This module implements:
- Agent state encapsulation with strict access control
- NumPy/C math protections with bounds checking
- Clipping and outlier resistance for numerical signals
- Runtime fuzzing framework
- Memory isolation for hostile plugins
"""

import logging
import multiprocessing as mp
import threading
from typing import Any, Callable, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class AgentEncapsulation:
    """Secure agent state management with encapsulation."""

    def __init__(self, agent_id: str):
        """Initialize agent encapsulation.

        Args:
            agent_id: Unique agent identifier
        """
        self.agent_id = agent_id
        self._state: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._access_log: List[Dict] = []
        self._allowed_operations = {
            "read": True,
            "write": True,
            "execute": False,  # Disabled by default
        }

    def set_state(self, key: str, value: Any, caller: str) -> None:
        """Set agent state with access control.

        Args:
            key: State key
            value: State value
            caller: Identity of caller

        Raises:
            PermissionError: If write not allowed
        """
        if not self._allowed_operations["write"]:
            logger.warning("Write denied for %s by %s", key, caller)
            raise PermissionError(f"Write operation not allowed for agent {self.agent_id}")

        with self._lock:
            self._state[key] = value
            self._log_access("write", key, caller)
            logger.debug("Agent %s state updated: %s by %s", self.agent_id, key, caller)

    def get_state(self, key: str, caller: str) -> Any:
        """Get agent state with access control.

        Args:
            key: State key
            caller: Identity of caller

        Returns:
            State value

        Raises:
            PermissionError: If read not allowed
            KeyError: If key not found
        """
        if not self._allowed_operations["read"]:
            logger.warning("Read denied for %s by %s", key, caller)
            raise PermissionError(f"Read operation not allowed for agent {self.agent_id}")

        with self._lock:
            self._log_access("read", key, caller)
            return self._state[key]

    def set_permissions(self, read: bool = True, write: bool = True, execute: bool = False) -> None:
        """Set allowed operations for agent.

        Args:
            read: Allow read operations
            write: Allow write operations
            execute: Allow execute operations
        """
        with self._lock:
            self._allowed_operations = {
                "read": read,
                "write": write,
                "execute": execute,
            }
            logger.info("Agent %s permissions updated", self.agent_id)

    def get_access_log(self) -> List[Dict]:
        """Get access log for auditing.

        Returns:
            List of access log entries
        """
        with self._lock:
            return self._access_log.copy()

    def _log_access(self, operation: str, key: str, caller: str) -> None:
        """Log state access for auditing.

        Args:
            operation: Type of operation
            key: State key accessed
            caller: Identity of caller
        """
        import time

        self._access_log.append(
            {
                "timestamp": time.time(),
                "operation": operation,
                "key": key,
                "caller": caller,
                "agent_id": self.agent_id,
            }
        )

        # Keep log size manageable
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-1000:]


class NumericalProtection:
    """Protection for numerical operations with bounds checking."""

    def __init__(self):
        """Initialize numerical protection."""
        self.clip_range = (-1e6, 1e6)  # Default bounds
        self.outlier_threshold = 3.0  # Standard deviations

    def clip_array(self, arr: np.ndarray, min_val: Optional[float] = None, max_val: Optional[float] = None) -> np.ndarray:
        """Clip array values to safe range.

        Args:
            arr: Input array
            min_val: Minimum value (default: -1e6)
            max_val: Maximum value (default: 1e6)

        Returns:
            Clipped array
        """
        min_val = min_val if min_val is not None else self.clip_range[0]
        max_val = max_val if max_val is not None else self.clip_range[1]

        clipped = np.clip(arr, min_val, max_val)

        # Log if clipping occurred
        if not np.array_equal(arr, clipped):
            logger.warning("Array clipped: %d values out of bounds", np.sum(arr != clipped))

        return clipped

    def remove_outliers(self, arr: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
        """Remove outliers from array using Z-score method.

        Args:
            arr: Input array
            threshold: Z-score threshold (default: 3.0)

        Returns:
            Array with outliers removed
        """
        threshold = threshold if threshold is not None else self.outlier_threshold

        if len(arr) == 0:
            return arr

        # Calculate Z-scores
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return arr  # No variation, no outliers

        z_scores = np.abs((arr - mean) / std)

        # Filter outliers
        mask = z_scores < threshold
        filtered = arr[mask]

        removed = len(arr) - len(filtered)
        if removed > 0:
            logger.info("Removed %d outliers from array (threshold: %.1f)", removed, threshold)

        return filtered

    def safe_divide(self, numerator: np.ndarray, denominator: np.ndarray, default: float = 0.0) -> np.ndarray:
        """Perform safe division with zero handling.

        Args:
            numerator: Numerator array
            denominator: Denominator array
            default: Default value for division by zero

        Returns:
            Result array
        """
        # Replace zeros in denominator
        safe_denom = np.where(denominator == 0, 1, denominator)
        result = numerator / safe_denom

        # Set default for original zeros
        result = np.where(denominator == 0, default, result)

        return result

    def validate_numerical_input(self, value: Any) -> bool:
        """Validate numerical input for safety.

        Args:
            value: Value to validate

        Returns:
            True if valid
        """
        try:
            # Convert to numpy array
            arr = np.asarray(value)

            # Check for NaN or Inf
            if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
                logger.warning("Invalid numerical input: NaN or Inf detected")
                return False

            # Check bounds
            if np.any(arr < self.clip_range[0]) or np.any(arr > self.clip_range[1]):
                logger.warning("Numerical input out of safe bounds")
                return False

            return True

        except (ValueError, TypeError) as e:
            logger.error("Invalid numerical input: %s", e)
            return False


class PluginIsolation:
    """Memory isolation for hostile plugins using multiprocessing."""

    def __init__(self, timeout: int = 30):
        """Initialize plugin isolation.

        Args:
            timeout: Execution timeout in seconds
        """
        self.timeout = timeout
        self.execution_log: List[Dict] = []

    def execute_isolated(
        self,
        plugin_func: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
    ) -> Any:
        """Execute plugin in isolated process.

        Args:
            plugin_func: Plugin function to execute
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Result from plugin execution

        Raises:
            TimeoutError: If execution exceeds timeout
            RuntimeError: If plugin execution fails
        """
        kwargs = kwargs or {}

        # Create queue for result
        result_queue = mp.Queue()

        def wrapper():
            """Wrapper to capture result."""
            try:
                result = plugin_func(*args, **kwargs)
                result_queue.put({"success": True, "result": result})
            except Exception as e:
                result_queue.put({"success": False, "error": str(e)})

        # Execute in separate process
        process = mp.Process(target=wrapper)
        process.start()

        # Wait with timeout
        process.join(timeout=self.timeout)

        if process.is_alive():
            # Timeout - terminate process
            process.terminate()
            process.join()
            logger.error("Plugin execution timed out after %d seconds", self.timeout)
            raise TimeoutError(f"Plugin execution exceeded {self.timeout} seconds")

        # Get result
        if not result_queue.empty():
            result_data = result_queue.get()

            if result_data["success"]:
                logger.info("Plugin executed successfully in isolation")
                return result_data["result"]
            else:
                error = result_data["error"]
                logger.error("Plugin execution failed: %s", error)
                raise RuntimeError(f"Plugin execution failed: {error}")
        else:
            logger.error("Plugin execution produced no result")
            raise RuntimeError("Plugin execution produced no result")


class RuntimeFuzzer:
    """Runtime fuzzing framework for testing resilience."""

    def __init__(self):
        """Initialize runtime fuzzer."""
        self.fuzz_strategies = {
            "random_string": self._fuzz_random_string,
            "boundary_values": self._fuzz_boundary_values,
            "type_confusion": self._fuzz_type_confusion,
            "overflow": self._fuzz_overflow,
        }

    def fuzz_input(self, strategy: str, base_input: Any) -> List[Any]:
        """Generate fuzzed inputs using specified strategy.

        Args:
            strategy: Fuzzing strategy name
            base_input: Base input to fuzz

        Returns:
            List of fuzzed inputs
        """
        if strategy not in self.fuzz_strategies:
            logger.warning("Unknown fuzz strategy: %s", strategy)
            return [base_input]

        return self.fuzz_strategies[strategy](base_input)

    def _fuzz_random_string(self, base_input: Any) -> List[Any]:
        """Generate random string fuzzing cases.

        Args:
            base_input: Base input

        Returns:
            List of fuzzed strings
        """
        import random
        import string

        cases = []

        # Very long string
        cases.append("A" * 10000)

        # Special characters
        cases.append("!@#$%^&*()_+-=[]{}|;:',.<>?/")

        # Unicode
        cases.append("你好世界🌍")

        # Empty string
        cases.append("")

        # Random strings
        for length in [1, 10, 100, 1000]:
            random_str = "".join(
                random.choices(string.ascii_letters + string.digits, k=length)
            )
            cases.append(random_str)

        return cases

    def _fuzz_boundary_values(self, base_input: Any) -> List[Any]:
        """Generate boundary value fuzzing cases.

        Args:
            base_input: Base input

        Returns:
            List of boundary values
        """
        cases = [
            0,
            -1,
            1,
            2**31 - 1,  # Max int32
            -(2**31),  # Min int32
            2**63 - 1,  # Max int64
            -(2**63),  # Min int64
            float("inf"),
            float("-inf"),
            float("nan"),
        ]

        return cases

    def _fuzz_type_confusion(self, base_input: Any) -> List[Any]:
        """Generate type confusion fuzzing cases.

        Args:
            base_input: Base input

        Returns:
            List of different types
        """
        cases = [
            None,
            True,
            False,
            0,
            "",
            [],
            {},
            set(),
            lambda x: x,
        ]

        return cases

    def _fuzz_overflow(self, base_input: Any) -> List[Any]:
        """Generate overflow fuzzing cases.

        Args:
            base_input: Base input

        Returns:
            List of overflow cases
        """
        cases = [
            [i for i in range(10000)],  # Large list
            {"key" + str(i): i for i in range(1000)},  # Large dict
            "A" * 1000000,  # 1MB string
        ]

        return cases
