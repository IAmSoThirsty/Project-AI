"""
Thirsty's Trading Hub Integration for Project AI

This module provides comprehensive trading capabilities integrated with
Project AI's governance framework.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Project AI Team"


class TradingHub:
    """
    Main Trading Hub interface for Project AI.

    Provides unified access to trading functionality with built-in governance,
    risk management, and audit logging.
    """

    def __init__(
        self,
        mode: str = "paper",
        data_dir: str | None = None,
        kernel: Any = None,
    ):
        """
        Initialize Trading Hub.

        Args:
            mode: Trading mode - "paper" or "live"
            data_dir: Directory for data storage
            kernel: CognitionKernel for governance routing
        """
        self.mode = mode
        self.data_dir = data_dir
        self.kernel = kernel
        self._enabled = True

        logger.info(f"Initializing Trading Hub in {mode} mode")

        # Initialize components (lazy loading to avoid import errors)
        self._market_data = None
        self._order_manager = None
        self._portfolio = None
        self._risk_manager = None

    def is_enabled(self) -> bool:
        """Check if Trading Hub is enabled and operational."""
        return self._enabled

    @property
    def market_data(self):
        """Lazy load market data provider."""
        if self._market_data is None:
            from integrations.thirstys_trading_hub.core.market_data import (
                MarketDataProvider,
            )

            self._market_data = MarketDataProvider(mode=self.mode)
        return self._market_data

    @property
    def order_manager(self):
        """Lazy load order manager."""
        if self._order_manager is None:
            from integrations.thirstys_trading_hub.core.order_manager import (
                OrderManager,
            )

            self._order_manager = OrderManager(mode=self.mode, kernel=self.kernel)
        return self._order_manager

    @property
    def portfolio(self):
        """Lazy load portfolio manager."""
        if self._portfolio is None:
            from integrations.thirstys_trading_hub.core.portfolio import (
                PortfolioManager,
            )

            self._portfolio = PortfolioManager(data_dir=self.data_dir)
        return self._portfolio

    @property
    def risk_manager(self):
        """Lazy load risk manager."""
        if self._risk_manager is None:
            from integrations.thirstys_trading_hub.governance.risk_limits import (
                RiskManager,
            )

            self._risk_manager = RiskManager()
        return self._risk_manager

    def get_market_data(
        self,
        symbol: str,
        timeframe: str = "1D",
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Get market data for a symbol.

        Args:
            symbol: Trading symbol (e.g., "AAPL", "BTCUSD")
            timeframe: Data timeframe (e.g., "1D", "1H", "15m")
            limit: Number of data points

        Returns:
            Market data dictionary
        """
        if not self._enabled:
            raise RuntimeError("Trading Hub is not enabled")

        logger.info(f"Fetching market data for {symbol}")
        return self.market_data.get_data(symbol, timeframe, limit)

    def place_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str = "market",
        limit_price: float | None = None,
    ) -> dict[str, Any]:
        """
        Place a trading order (subject to governance).

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: "buy" or "sell"
            order_type: "market" or "limit"
            limit_price: Limit price (for limit orders)

        Returns:
            Order result dictionary
        """
        if not self._enabled:
            raise RuntimeError("Trading Hub is not enabled")

        # Check risk limits
        current_price = limit_price or self.market_data.get_current_price(symbol)
        is_allowed, reason = self.risk_manager.check_trade(
            symbol=symbol,
            quantity=quantity,
            price=current_price,
        )

        if not is_allowed:
            raise PermissionError(f"Trade blocked by risk manager: {reason}")

        logger.info(f"Placing {side} order for {quantity} {symbol}")
        return self.order_manager.place_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            limit_price=limit_price,
        )

    def get_portfolio(self) -> dict[str, Any]:
        """Get current portfolio state."""
        if not self._enabled:
            raise RuntimeError("Trading Hub is not enabled")

        return self.portfolio.get_state()

    def emergency_stop(self) -> None:
        """Emergency stop - halt all trading immediately."""
        logger.warning("EMERGENCY STOP: Halting all trading operations")
        self._enabled = False
        if self._order_manager:
            self.order_manager.cancel_all_orders()

    def close_all_positions(self) -> list[dict[str, Any]]:
        """Close all open positions."""
        if not self._enabled:
            raise RuntimeError("Trading Hub is not enabled")

        logger.warning("Closing all open positions")
        positions = self.portfolio.get_positions()
        results = []

        for position in positions:
            try:
                result = self.place_order(
                    symbol=position["symbol"],
                    quantity=position["quantity"],
                    side="sell" if position["side"] == "long" else "buy",
                    order_type="market",
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to close position {position['symbol']}: {e}")

        return results

    def __repr__(self) -> str:
        """String representation."""
        return f"TradingHub(mode={self.mode}, enabled={self._enabled})"


__all__ = [
    "TradingHub",
]
