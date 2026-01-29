"""Strategy engine for Thirsty's Trading Hub.

Manages trading strategy registration, execution, and result tracking.
"""

import json
import logging
import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class StrategyStatus(Enum):
    """Strategy execution status."""

    REGISTERED = "registered"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class StrategyResult:
    """Result of a strategy execution."""

    strategy_id: str
    strategy_name: str
    status: StrategyStatus
    started_at: int
    completed_at: int | None = None
    orders_placed: int = 0
    positions_opened: int = 0
    positions_closed: int = 0
    total_pnl: float = 0.0
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Strategy:
    """Trading strategy definition."""

    strategy_id: str
    name: str
    description: str
    callable: Callable
    parameters: dict[str, Any] = field(default_factory=dict)
    symbols: list[str] = field(default_factory=list)
    timeframe: str = "1h"
    enabled: bool = True
    created_at: int = field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000)
    )
    metadata: dict[str, Any] = field(default_factory=dict)


class StrategyEngine:
    """Manages trading strategies and their execution."""

    def __init__(
        self,
        data_dir: str = "data/trading_hub",
        market_data: Any = None,
        order_manager: Any = None,
        portfolio_manager: Any = None,
    ):
        """Initialize strategy engine.

        Args:
            data_dir: Directory for strategy persistence
            market_data: MarketDataProvider instance
            order_manager: OrderManager instance
            portfolio_manager: PortfolioManager instance
        """
        self.data_dir = data_dir
        self.market_data = market_data
        self.order_manager = order_manager
        self.portfolio_manager = portfolio_manager

        self._strategies: dict[str, Strategy] = {}
        self._results: dict[str, StrategyResult] = {}
        self._execution_history: list[StrategyResult] = []

        os.makedirs(data_dir, exist_ok=True)
        self._load_strategies()

        logger.info("StrategyEngine initialized")

    def _load_strategies(self) -> None:
        """Load strategies and results from persistent storage."""
        strategies_file = os.path.join(self.data_dir, "strategies.json")
        if os.path.exists(strategies_file):
            try:
                with open(strategies_file) as f:
                    data = json.load(f)

                    self._execution_history = [
                        StrategyResult(
                            strategy_id=r["strategy_id"],
                            strategy_name=r["strategy_name"],
                            status=StrategyStatus(r["status"]),
                            started_at=r["started_at"],
                            completed_at=r.get("completed_at"),
                            orders_placed=r.get("orders_placed", 0),
                            positions_opened=r.get("positions_opened", 0),
                            positions_closed=r.get("positions_closed", 0),
                            total_pnl=r.get("total_pnl", 0.0),
                            metrics=r.get("metrics", {}),
                            errors=r.get("errors", []),
                            metadata=r.get("metadata", {}),
                        )
                        for r in data.get("execution_history", [])
                    ]

                logger.info(
                    f"Loaded {len(self._execution_history)} strategy execution results"
                )
            except Exception as e:
                logger.error(f"Failed to load strategies: {e}")

    def _save_strategies(self) -> None:
        """Save strategies and results to persistent storage."""
        strategies_file = os.path.join(self.data_dir, "strategies.json")
        try:
            data = {
                "strategies": [
                    {
                        "strategy_id": s.strategy_id,
                        "name": s.name,
                        "description": s.description,
                        "parameters": s.parameters,
                        "symbols": s.symbols,
                        "timeframe": s.timeframe,
                        "enabled": s.enabled,
                        "created_at": s.created_at,
                        "metadata": s.metadata,
                    }
                    for s in self._strategies.values()
                ],
                "execution_history": [
                    {
                        "strategy_id": r.strategy_id,
                        "strategy_name": r.strategy_name,
                        "status": r.status.value,
                        "started_at": r.started_at,
                        "completed_at": r.completed_at,
                        "orders_placed": r.orders_placed,
                        "positions_opened": r.positions_opened,
                        "positions_closed": r.positions_closed,
                        "total_pnl": r.total_pnl,
                        "metrics": r.metrics,
                        "errors": r.errors,
                        "metadata": r.metadata,
                    }
                    for r in self._execution_history
                ],
                "updated_at": int(datetime.now(UTC).timestamp() * 1000),
            }

            with open(strategies_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save strategies: {e}")

    def register_strategy(
        self,
        name: str,
        callable: Callable,
        description: str = "",
        parameters: dict[str, Any] | None = None,
        symbols: list[str] | None = None,
        timeframe: str = "1h",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a new trading strategy.

        Args:
            name: Strategy name
            callable: Strategy function to execute
            description: Strategy description
            parameters: Strategy configuration parameters
            symbols: List of symbols to trade
            timeframe: Default timeframe for strategy
            metadata: Additional strategy metadata

        Returns:
            Strategy ID

        Raises:
            ValueError: If strategy with same name already exists
        """
        existing = [s for s in self._strategies.values() if s.name == name]
        if existing:
            raise ValueError(f"Strategy with name '{name}' already exists")

        if not callable or not isinstance(callable, Callable):
            raise ValueError("Strategy callable must be a valid function")

        strategy_id = str(uuid.uuid4())
        strategy = Strategy(
            strategy_id=strategy_id,
            name=name,
            description=description,
            callable=callable,
            parameters=parameters or {},
            symbols=symbols or [],
            timeframe=timeframe,
            metadata=metadata or {},
        )

        self._strategies[strategy_id] = strategy
        self._save_strategies()

        logger.info(f"Registered strategy '{name}' with ID {strategy_id}")
        return strategy_id

    def unregister_strategy(self, strategy_id: str) -> bool:
        """Unregister a strategy.

        Args:
            strategy_id: ID of strategy to unregister

        Returns:
            True if strategy was unregistered, False if not found
        """
        if strategy_id not in self._strategies:
            logger.warning(f"Strategy {strategy_id} not found")
            return False

        strategy = self._strategies[strategy_id]
        del self._strategies[strategy_id]
        self._save_strategies()

        logger.info(f"Unregistered strategy '{strategy.name}' ({strategy_id})")
        return True

    def get_strategy(self, strategy_id: str) -> Strategy | None:
        """Get strategy by ID.

        Args:
            strategy_id: Strategy ID

        Returns:
            Strategy if found, None otherwise
        """
        return self._strategies.get(strategy_id)

    def list_strategies(self) -> list[Strategy]:
        """List all registered strategies.

        Returns:
            List of registered strategies
        """
        return list(self._strategies.values())

    def run_strategy(
        self,
        strategy_id: str,
        override_parameters: dict[str, Any] | None = None,
    ) -> StrategyResult:
        """Execute a registered strategy.

        Args:
            strategy_id: ID of strategy to execute
            override_parameters: Optional parameters to override strategy defaults

        Returns:
            StrategyResult with execution details

        Raises:
            ValueError: If strategy not found or disabled
        """
        if strategy_id not in self._strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self._strategies[strategy_id]
        if not strategy.enabled:
            raise ValueError(f"Strategy '{strategy.name}' is disabled")

        result = StrategyResult(
            strategy_id=strategy_id,
            strategy_name=strategy.name,
            status=StrategyStatus.RUNNING,
            started_at=int(datetime.now(UTC).timestamp() * 1000),
        )

        self._results[strategy_id] = result

        logger.info(f"Executing strategy '{strategy.name}' ({strategy_id})")

        try:
            parameters = {**strategy.parameters, **(override_parameters or {})}

            context = {
                "strategy_id": strategy_id,
                "strategy_name": strategy.name,
                "parameters": parameters,
                "market_data": self.market_data,
                "order_manager": self.order_manager,
                "portfolio_manager": self.portfolio_manager,
                "symbols": strategy.symbols,
                "timeframe": strategy.timeframe,
            }

            execution_result = strategy.callable(context)

            if isinstance(execution_result, dict):
                result.metrics = execution_result.get("metrics", {})
                result.orders_placed = execution_result.get("orders_placed", 0)
                result.positions_opened = execution_result.get("positions_opened", 0)
                result.positions_closed = execution_result.get("positions_closed", 0)
                result.total_pnl = execution_result.get("total_pnl", 0.0)
                result.metadata = execution_result.get("metadata", {})

            result.status = StrategyStatus.COMPLETED
            result.completed_at = int(datetime.now(UTC).timestamp() * 1000)

            logger.info(
                f"Strategy '{strategy.name}' completed successfully: "
                f"{result.orders_placed} orders, PnL: {result.total_pnl:.2f}"
            )

        except Exception as e:
            result.status = StrategyStatus.FAILED
            result.completed_at = int(datetime.now(UTC).timestamp() * 1000)
            result.errors.append(str(e))

            logger.error(f"Strategy '{strategy.name}' failed: {e}", exc_info=True)

        self._execution_history.append(result)
        self._save_strategies()

        return result

    def stop_strategy(self, strategy_id: str) -> bool:
        """Stop a running strategy.

        Args:
            strategy_id: ID of strategy to stop

        Returns:
            True if strategy was stopped, False if not running
        """
        if strategy_id not in self._results:
            logger.warning(f"No running strategy with ID {strategy_id}")
            return False

        result = self._results[strategy_id]
        if result.status != StrategyStatus.RUNNING:
            logger.warning(
                f"Strategy {strategy_id} is not running (status: {result.status.value})"
            )
            return False

        result.status = StrategyStatus.STOPPED
        result.completed_at = int(datetime.now(UTC).timestamp() * 1000)

        logger.info(f"Stopped strategy '{result.strategy_name}' ({strategy_id})")

        self._save_strategies()
        return True

    def get_result(self, strategy_id: str) -> StrategyResult | None:
        """Get current or most recent result for a strategy.

        Args:
            strategy_id: Strategy ID

        Returns:
            StrategyResult if found, None otherwise
        """
        return self._results.get(strategy_id)

    def get_execution_history(
        self, strategy_id: str | None = None, limit: int = 100
    ) -> list[StrategyResult]:
        """Get strategy execution history.

        Args:
            strategy_id: Optional strategy ID to filter results
            limit: Maximum number of results to return

        Returns:
            List of strategy execution results
        """
        results = self._execution_history
        if strategy_id:
            results = [r for r in results if r.strategy_id == strategy_id]
        return results[-limit:]

    def calculate_strategy_metrics(self, strategy_id: str) -> dict[str, Any]:
        """Calculate aggregate metrics for a strategy.

        Args:
            strategy_id: Strategy ID

        Returns:
            Dictionary with aggregate metrics
        """
        if strategy_id not in self._strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self._strategies[strategy_id]
        executions = [
            r for r in self._execution_history if r.strategy_id == strategy_id
        ]

        if not executions:
            return {
                "strategy_name": strategy.name,
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_orders": 0,
                "total_pnl": 0.0,
                "win_rate_pct": 0.0,
            }

        successful = [e for e in executions if e.status == StrategyStatus.COMPLETED]
        failed = [e for e in executions if e.status == StrategyStatus.FAILED]

        total_orders = sum(e.orders_placed for e in executions)
        total_pnl = sum(e.total_pnl for e in executions)

        winning_executions = [e for e in executions if e.total_pnl > 0]
        win_rate = (
            len(winning_executions) / len(executions) * 100 if executions else 0.0
        )

        return {
            "strategy_name": strategy.name,
            "total_executions": len(executions),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "total_orders": total_orders,
            "total_pnl": round(total_pnl, 2),
            "win_rate_pct": round(win_rate, 2),
            "avg_pnl_per_execution": (
                round(total_pnl / len(executions), 2) if executions else 0.0
            ),
        }

    def enable_strategy(self, strategy_id: str) -> bool:
        """Enable a strategy.

        Args:
            strategy_id: Strategy ID

        Returns:
            True if strategy was enabled, False if not found
        """
        if strategy_id not in self._strategies:
            logger.warning(f"Strategy {strategy_id} not found")
            return False

        strategy = self._strategies[strategy_id]
        strategy.enabled = True
        self._save_strategies()

        logger.info(f"Enabled strategy '{strategy.name}' ({strategy_id})")
        return True

    def disable_strategy(self, strategy_id: str) -> bool:
        """Disable a strategy.

        Args:
            strategy_id: Strategy ID

        Returns:
            True if strategy was disabled, False if not found
        """
        if strategy_id not in self._strategies:
            logger.warning(f"Strategy {strategy_id} not found")
            return False

        strategy = self._strategies[strategy_id]
        strategy.enabled = False
        self._save_strategies()

        logger.info(f"Disabled strategy '{strategy.name}' ({strategy_id})")
        return True
