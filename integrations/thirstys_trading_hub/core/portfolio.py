"""Portfolio management system for Thirsty's Trading Hub.

Tracks positions, balances, and portfolio state with JSON persistence.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Trading position data structure."""

    symbol: str
    quantity: float
    average_entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    side: str = "long"
    opened_at: int = field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000)
    )
    updated_at: int = field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000)
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_price(self, current_price: float) -> None:
        """Update current price and calculate unrealized PnL.

        Args:
            current_price: Current market price
        """
        self.current_price = current_price
        self.updated_at = int(datetime.now(UTC).timestamp() * 1000)

        if self.side == "long":
            self.unrealized_pnl = (
                current_price - self.average_entry_price
            ) * self.quantity
        else:
            self.unrealized_pnl = (
                self.average_entry_price - current_price
            ) * self.quantity


@dataclass
class Balance:
    """Account balance information."""

    currency: str
    total: float
    available: float
    locked: float = 0.0


@dataclass
class PortfolioState:
    """Complete portfolio state snapshot."""

    total_equity: float
    total_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    cash_balance: float
    positions_count: int
    positions: list[Position]
    balances: list[Balance]
    timestamp: int = field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000)
    )


class PortfolioManager:
    """Manages portfolio state, positions, and balances."""

    def __init__(
        self,
        data_dir: str = "data/trading_hub",
        initial_balance: float = 100000.0,
        currency: str = "USD",
    ):
        """Initialize portfolio manager.

        Args:
            data_dir: Directory for portfolio persistence
            initial_balance: Starting cash balance
            currency: Base currency for portfolio
        """
        self.data_dir = data_dir
        self.currency = currency
        self.initial_balance = initial_balance
        self._positions: dict[str, Position] = {}
        self._balances: dict[str, Balance] = {
            currency: Balance(
                currency=currency, total=initial_balance, available=initial_balance
            )
        }
        self._realized_pnl: float = 0.0
        self._trade_history: list[dict[str, Any]] = []

        os.makedirs(data_dir, exist_ok=True)
        self._load_state()

        logger.info(
            "PortfolioManager initialized with %s %s balance", initial_balance, currency
        )

    def _load_state(self) -> None:
        """Load portfolio state from persistent storage."""
        portfolio_file = os.path.join(self.data_dir, "portfolio.json")
        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file) as f:
                    data = json.load(f)

                    for pos_data in data.get("positions", []):
                        position = Position(
                            symbol=pos_data["symbol"],
                            quantity=pos_data["quantity"],
                            average_entry_price=pos_data["average_entry_price"],
                            current_price=pos_data.get("current_price", 0.0),
                            unrealized_pnl=pos_data.get("unrealized_pnl", 0.0),
                            realized_pnl=pos_data.get("realized_pnl", 0.0),
                            side=pos_data.get("side", "long"),
                            opened_at=pos_data["opened_at"],
                            updated_at=pos_data["updated_at"],
                            metadata=pos_data.get("metadata", {}),
                        )
                        self._positions[position.symbol] = position

                    for bal_data in data.get("balances", []):
                        balance = Balance(
                            currency=bal_data["currency"],
                            total=bal_data["total"],
                            available=bal_data["available"],
                            locked=bal_data.get("locked", 0.0),
                        )
                        self._balances[balance.currency] = balance

                    self._realized_pnl = data.get("realized_pnl", 0.0)
                    self._trade_history = data.get("trade_history", [])

                logger.info(
                    f"Loaded portfolio: {len(self._positions)} positions, "
                    f"{len(self._balances)} balances"
                )
            except Exception as e:
                logger.error("Failed to load portfolio state: %s", e)

    def _save_state(self) -> None:
        """Save portfolio state to persistent storage."""
        portfolio_file = os.path.join(self.data_dir, "portfolio.json")
        try:
            data = {
                "positions": [
                    {
                        "symbol": p.symbol,
                        "quantity": p.quantity,
                        "average_entry_price": p.average_entry_price,
                        "current_price": p.current_price,
                        "unrealized_pnl": p.unrealized_pnl,
                        "realized_pnl": p.realized_pnl,
                        "side": p.side,
                        "opened_at": p.opened_at,
                        "updated_at": p.updated_at,
                        "metadata": p.metadata,
                    }
                    for p in self._positions.values()
                ],
                "balances": [
                    {
                        "currency": b.currency,
                        "total": b.total,
                        "available": b.available,
                        "locked": b.locked,
                    }
                    for b in self._balances.values()
                ],
                "realized_pnl": self._realized_pnl,
                "trade_history": self._trade_history,
                "updated_at": int(datetime.now(UTC).timestamp() * 1000),
            }

            with open(portfolio_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save portfolio state: %s", e)

    def get_state(self) -> PortfolioState:
        """Get current portfolio state snapshot.

        Returns:
            PortfolioState with complete portfolio information
        """
        unrealized_pnl = sum(p.unrealized_pnl for p in self._positions.values())
        cash_balance = self._balances.get(
            self.currency, Balance(self.currency, 0.0, 0.0)
        ).total
        total_equity = cash_balance + sum(
            p.quantity * p.current_price for p in self._positions.values()
        )
        total_pnl = unrealized_pnl + self._realized_pnl

        return PortfolioState(
            total_equity=round(total_equity, 2),
            total_pnl=round(total_pnl, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            realized_pnl=round(self._realized_pnl, 2),
            cash_balance=round(cash_balance, 2),
            positions_count=len(self._positions),
            positions=list(self._positions.values()),
            balances=list(self._balances.values()),
        )

    def get_positions(self) -> list[Position]:
        """Get all open positions.

        Returns:
            List of open positions
        """
        return list(self._positions.values())

    def get_position(self, symbol: str) -> Position | None:
        """Get position for a specific symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            Position if exists, None otherwise
        """
        return self._positions.get(symbol)

    def update_position(
        self,
        symbol: str,
        quantity: float,
        price: float,
        side: str = "long",
        metadata: dict[str, Any] | None = None,
    ) -> Position:
        """Update or create a position.

        Args:
            symbol: Trading pair symbol
            quantity: Position quantity (positive for add, negative for reduce)
            price: Transaction price
            side: Position side ('long' or 'short')
            metadata: Additional position metadata

        Returns:
            Updated position

        Raises:
            ValueError: If invalid parameters provided
        """
        if quantity == 0:
            raise ValueError("Quantity cannot be zero")

        current_position = self._positions.get(symbol)

        if current_position is None:
            if quantity < 0:
                raise ValueError("Cannot reduce non-existent position")

            position = Position(
                symbol=symbol,
                quantity=abs(quantity),
                average_entry_price=price,
                current_price=price,
                side=side,
                metadata=metadata or {},
            )
            self._positions[symbol] = position

            self._record_trade(symbol, quantity, price, "open")

            logger.info(
                "Opened new %s position: %s %s @ %s", side, symbol, abs(quantity), price
            )

        else:
            if quantity > 0:
                total_quantity = current_position.quantity + quantity
                total_cost = (
                    current_position.quantity * current_position.average_entry_price
                    + quantity * price
                )
                current_position.average_entry_price = total_cost / total_quantity
                current_position.quantity = total_quantity
                current_position.current_price = price
                current_position.update_price(price)

                self._record_trade(symbol, quantity, price, "add")

                logger.info(
                    f"Added to position: {symbol} +{quantity} @ {price}, "
                    f"new avg: {current_position.average_entry_price:.2f}"
                )

            else:
                reduce_quantity = abs(quantity)
                if reduce_quantity > current_position.quantity:
                    raise ValueError(
                        f"Cannot reduce position by {reduce_quantity}, "
                        f"only {current_position.quantity} available"
                    )

                pnl = (price - current_position.average_entry_price) * reduce_quantity
                if current_position.side == "short":
                    pnl = -pnl

                self._realized_pnl += pnl
                current_position.realized_pnl += pnl
                current_position.quantity -= reduce_quantity
                current_position.current_price = price
                current_position.update_price(price)

                self._record_trade(symbol, quantity, price, "reduce", pnl=pnl)

                if current_position.quantity == 0:
                    del self._positions[symbol]
                    logger.info("Closed position: %s, realized PnL: %s", symbol, pnl)
                else:
                    logger.info(
                        f"Reduced position: {symbol} {quantity} @ {price}, "
                        f"realized PnL: {pnl:.2f}"
                    )

            position = current_position

        self._save_state()
        return position

    def update_prices(self, prices: dict[str, float]) -> None:
        """Update current prices for all positions.

        Args:
            prices: Dictionary mapping symbols to current prices
        """
        for symbol, price in prices.items():
            if symbol in self._positions:
                self._positions[symbol].update_price(price)

        self._save_state()

    def get_balance(self, currency: str | None = None) -> Balance:
        """Get balance for a specific currency.

        Args:
            currency: Currency code (uses base currency if None)

        Returns:
            Balance for specified currency
        """
        currency = currency or self.currency
        return self._balances.get(
            currency, Balance(currency=currency, total=0.0, available=0.0)
        )

    def update_balance(
        self,
        currency: str,
        amount: float,
        lock: bool = False,
    ) -> Balance:
        """Update balance for a currency.

        Args:
            currency: Currency code
            amount: Amount to add (positive) or subtract (negative)
            lock: Whether to lock the amount (unavailable for trading)

        Returns:
            Updated balance

        Raises:
            ValueError: If insufficient balance
        """
        current_balance = self._balances.get(
            currency, Balance(currency=currency, total=0.0, available=0.0)
        )

        if lock:
            if amount > current_balance.available:
                raise ValueError(
                    f"Insufficient available balance: {current_balance.available} {currency}"
                )
            current_balance.available -= amount
            current_balance.locked += amount
        else:
            new_total = current_balance.total + amount
            if new_total < 0:
                raise ValueError(
                    f"Insufficient balance: {current_balance.total} {currency}"
                )

            current_balance.total = new_total
            if amount < 0:
                current_balance.available += amount
            else:
                current_balance.available += amount

        self._balances[currency] = current_balance
        self._save_state()

        logger.debug(
            f"Updated balance: {currency} {amount:+.2f}, "
            f"new total: {current_balance.total:.2f}"
        )

        return current_balance

    def _record_trade(
        self,
        symbol: str,
        quantity: float,
        price: float,
        action: str,
        pnl: float = 0.0,
    ) -> None:
        """Record trade in history.

        Args:
            symbol: Trading pair symbol
            quantity: Trade quantity
            price: Trade price
            action: Trade action ('open', 'add', 'reduce', 'close')
            pnl: Realized PnL (if applicable)
        """
        trade = {
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "action": action,
            "pnl": pnl,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        }
        self._trade_history.append(trade)

    def get_trade_history(
        self, symbol: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get trade history, optionally filtered by symbol.

        Args:
            symbol: Optional symbol to filter trades
            limit: Maximum number of trades to return

        Returns:
            List of historical trades
        """
        trades = self._trade_history
        if symbol:
            trades = [t for t in trades if t["symbol"] == symbol]
        return trades[-limit:]

    def calculate_metrics(self) -> dict[str, Any]:
        """Calculate portfolio performance metrics.

        Returns:
            Dictionary with performance metrics
        """
        state = self.get_state()

        return_pct = (
            (state.total_equity - self.initial_balance) / self.initial_balance * 100
            if self.initial_balance > 0
            else 0.0
        )

        winning_trades = [t for t in self._trade_history if t.get("pnl", 0) > 0]
        losing_trades = [t for t in self._trade_history if t.get("pnl", 0) < 0]
        total_trades = len(winning_trades) + len(losing_trades)

        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0.0

        return {
            "total_return_pct": round(return_pct, 2),
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate_pct": round(win_rate, 2),
            "realized_pnl": round(state.realized_pnl, 2),
            "unrealized_pnl": round(state.unrealized_pnl, 2),
            "total_pnl": round(state.total_pnl, 2),
        }
