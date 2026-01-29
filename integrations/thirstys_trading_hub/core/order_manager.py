"""Order management system for Thirsty's Trading Hub.

Handles order placement, cancellation, and tracking with governance routing
through the cognition kernel for all order operations.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order type classification."""

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderSide(Enum):
    """Order side (buy or sell)."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order execution status."""

    PENDING = "pending"
    SUBMITTED = "submitted"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class Order:
    """Order data structure."""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float | None = None
    stop_price: float | None = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    created_at: int = field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000)
    )
    updated_at: int = field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000)
    )
    filled_at: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderResult:
    """Result of an order operation."""

    success: bool
    order_id: str | None = None
    message: str = ""
    order: Order | None = None
    governance_decision: dict[str, Any] | None = None


class OrderManager:
    """Manages order lifecycle with governance routing."""

    def __init__(
        self,
        data_dir: str = "data/trading_hub",
        mode: str = "paper",
        kernel: Any = None,
    ):
        """Initialize order manager.

        Args:
            data_dir: Directory for order persistence
            mode: Trading mode ('paper' or 'live')
            kernel: CognitionKernel instance for governance routing
        """
        self.data_dir = data_dir
        self.mode = mode
        self.kernel = kernel
        self._orders: dict[str, Order] = {}
        self._order_history: list[Order] = []

        os.makedirs(data_dir, exist_ok=True)
        self._load_orders()

        logger.info(f"OrderManager initialized in {mode} mode")

    def _load_orders(self) -> None:
        """Load orders from persistent storage."""
        orders_file = os.path.join(self.data_dir, "orders.json")
        if os.path.exists(orders_file):
            try:
                with open(orders_file) as f:
                    data = json.load(f)
                    for order_data in data.get("orders", []):
                        order = Order(
                            order_id=order_data["order_id"],
                            symbol=order_data["symbol"],
                            side=OrderSide(order_data["side"]),
                            order_type=OrderType(order_data["order_type"]),
                            quantity=order_data["quantity"],
                            price=order_data.get("price"),
                            stop_price=order_data.get("stop_price"),
                            status=OrderStatus(order_data["status"]),
                            filled_quantity=order_data.get("filled_quantity", 0.0),
                            average_fill_price=order_data.get(
                                "average_fill_price", 0.0
                            ),
                            created_at=order_data["created_at"],
                            updated_at=order_data["updated_at"],
                            filled_at=order_data.get("filled_at"),
                            metadata=order_data.get("metadata", {}),
                        )
                        if order.status in (
                            OrderStatus.OPEN,
                            OrderStatus.PARTIALLY_FILLED,
                        ):
                            self._orders[order.order_id] = order
                        self._order_history.append(order)

                logger.info(
                    f"Loaded {len(self._orders)} active orders, "
                    f"{len(self._order_history)} total orders"
                )
            except Exception as e:
                logger.error(f"Failed to load orders: {e}")
                self._orders = {}
                self._order_history = []

    def _save_orders(self) -> None:
        """Save orders to persistent storage."""
        orders_file = os.path.join(self.data_dir, "orders.json")
        try:
            data = {
                "orders": [
                    {
                        "order_id": o.order_id,
                        "symbol": o.symbol,
                        "side": o.side.value,
                        "order_type": o.order_type.value,
                        "quantity": o.quantity,
                        "price": o.price,
                        "stop_price": o.stop_price,
                        "status": o.status.value,
                        "filled_quantity": o.filled_quantity,
                        "average_fill_price": o.average_fill_price,
                        "created_at": o.created_at,
                        "updated_at": o.updated_at,
                        "filled_at": o.filled_at,
                        "metadata": o.metadata,
                    }
                    for o in self._order_history
                ],
                "updated_at": int(datetime.now(UTC).timestamp() * 1000),
            }

            with open(orders_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save orders: {e}")

    def _route_through_governance(
        self, action_name: str, order: Order, context: dict[str, Any]
    ) -> tuple[bool, str, dict[str, Any] | None]:
        """Route order action through cognition kernel for governance approval.

        Args:
            action_name: Name of the action (e.g., 'place_order', 'cancel_order')
            order: Order being acted upon
            context: Additional context for governance decision

        Returns:
            Tuple of (approved, reason, governance_decision)
        """
        if self.kernel is None:
            logger.warning("No kernel provided, skipping governance routing")
            return True, "No kernel configured", None

        try:
            from app.core.cognition_kernel import Action, ExecutionType

            action = Action(
                action_id=str(uuid.uuid4()),
                action_name=action_name,
                action_type=ExecutionType.TOOL_INVOCATION,
                callable=lambda: None,
                source="trading_hub",
                risk_level=self._assess_risk_level(order),
                mutation_targets=[],
                metadata={
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "side": order.side.value,
                    "quantity": order.quantity,
                    "order_type": order.order_type.value,
                    **context,
                },
            )

            governance_decision = self.kernel.governance_evaluate(action)

            if governance_decision.get("approved", False):
                logger.info(
                    f"Order action '{action_name}' approved by governance: "
                    f"{governance_decision.get('reason', 'No reason provided')}"
                )
                return (
                    True,
                    governance_decision.get("reason", "Approved"),
                    governance_decision,
                )

            reason = governance_decision.get("reason", "Rejected by governance")
            logger.warning(f"Order action '{action_name}' rejected: {reason}")
            return False, reason, governance_decision

        except Exception as e:
            logger.error(f"Governance routing failed: {e}")
            return False, f"Governance error: {e}", None

    def _assess_risk_level(self, order: Order) -> str:
        """Assess risk level of an order.

        Args:
            order: Order to assess

        Returns:
            Risk level string ('low', 'medium', 'high')
        """
        if self.mode == "paper":
            return "low"

        if order.order_type == OrderType.MARKET:
            return "medium"

        if order.quantity * (order.price or 0) > 10000:
            return "high"

        return "medium"

    def place_order(
        self,
        symbol: str,
        side: OrderSide | str,
        order_type: OrderType | str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OrderResult:
        """Place a new order with governance approval.

        Args:
            symbol: Trading pair symbol
            side: Order side (buy/sell)
            order_type: Type of order
            quantity: Quantity to trade
            price: Limit price (required for limit orders)
            stop_price: Stop price (required for stop orders)
            metadata: Additional order metadata

        Returns:
            OrderResult with success status and order details
        """
        if isinstance(side, str):
            try:
                side = OrderSide(side.lower())
            except ValueError:
                return OrderResult(
                    success=False,
                    message=f"Invalid order side: {side}. Must be 'buy' or 'sell'",
                )

        if isinstance(order_type, str):
            try:
                order_type = OrderType(order_type.lower())
            except ValueError:
                return OrderResult(
                    success=False,
                    message=f"Invalid order type: {order_type}",
                )

        if quantity <= 0:
            return OrderResult(
                success=False,
                message=f"Invalid quantity: {quantity}. Must be greater than 0",
            )

        if order_type == OrderType.LIMIT and price is None:
            return OrderResult(
                success=False,
                message="Limit orders require a price",
            )

        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            status=OrderStatus.PENDING,
            metadata=metadata or {},
        )

        approved, reason, gov_decision = self._route_through_governance(
            "place_order",
            order,
            {
                "mode": self.mode,
                "estimated_value": quantity * (price or 0),
            },
        )

        if not approved:
            order.status = OrderStatus.REJECTED
            order.metadata["rejection_reason"] = reason
            self._order_history.append(order)
            self._save_orders()

            return OrderResult(
                success=False,
                order_id=order_id,
                message=f"Order rejected by governance: {reason}",
                order=order,
                governance_decision=gov_decision,
            )

        if self.mode == "paper":
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_fill_price = price or 0.0
            order.filled_at = int(datetime.now(UTC).timestamp() * 1000)
            order.updated_at = order.filled_at

            logger.info(
                f"Paper mode: Order {order_id} filled - "
                f"{side.value} {quantity} {symbol} @ {order.average_fill_price}"
            )
        else:
            order.status = OrderStatus.SUBMITTED

        self._orders[order_id] = order
        self._order_history.append(order)
        self._save_orders()

        return OrderResult(
            success=True,
            order_id=order_id,
            message=f"Order placed successfully: {order.status.value}",
            order=order,
            governance_decision=gov_decision,
        )

    def cancel_order(self, order_id: str) -> OrderResult:
        """Cancel an existing order.

        Args:
            order_id: ID of order to cancel

        Returns:
            OrderResult with success status
        """
        if order_id not in self._orders:
            return OrderResult(
                success=False,
                order_id=order_id,
                message=f"Order {order_id} not found or already completed",
            )

        order = self._orders[order_id]

        approved, reason, gov_decision = self._route_through_governance(
            "cancel_order",
            order,
            {"mode": self.mode},
        )

        if not approved:
            return OrderResult(
                success=False,
                order_id=order_id,
                message=f"Cancel rejected by governance: {reason}",
                order=order,
                governance_decision=gov_decision,
            )

        order.status = OrderStatus.CANCELLED
        order.updated_at = int(datetime.now(UTC).timestamp() * 1000)

        del self._orders[order_id]
        self._save_orders()

        logger.info(f"Order {order_id} cancelled")

        return OrderResult(
            success=True,
            order_id=order_id,
            message="Order cancelled successfully",
            order=order,
            governance_decision=gov_decision,
        )

    def cancel_all_orders(self, symbol: str | None = None) -> dict[str, Any]:
        """Cancel all open orders, optionally filtered by symbol.

        Args:
            symbol: Optional symbol to filter orders (cancels all if None)

        Returns:
            Dictionary with cancellation results
        """
        orders_to_cancel = [
            order_id
            for order_id, order in self._orders.items()
            if symbol is None or order.symbol == symbol
        ]

        if not orders_to_cancel:
            return {
                "success": True,
                "cancelled_count": 0,
                "message": "No open orders to cancel",
            }

        cancelled = []
        failed = []

        for order_id in orders_to_cancel:
            result = self.cancel_order(order_id)
            if result.success:
                cancelled.append(order_id)
            else:
                failed.append({"order_id": order_id, "reason": result.message})

        message = f"Cancelled {len(cancelled)} orders"
        if failed:
            message += f", {len(failed)} failed"

        logger.info(message)

        return {
            "success": len(cancelled) > 0,
            "cancelled_count": len(cancelled),
            "failed_count": len(failed),
            "cancelled_orders": cancelled,
            "failed_orders": failed,
            "message": message,
        }

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ID.

        Args:
            order_id: Order ID to retrieve

        Returns:
            Order if found, None otherwise
        """
        return self._orders.get(order_id)

    def get_open_orders(self, symbol: str | None = None) -> list[Order]:
        """Get all open orders, optionally filtered by symbol.

        Args:
            symbol: Optional symbol to filter orders

        Returns:
            List of open orders
        """
        orders = list(self._orders.values())
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders

    def get_order_history(
        self, symbol: str | None = None, limit: int = 100
    ) -> list[Order]:
        """Get order history, optionally filtered by symbol.

        Args:
            symbol: Optional symbol to filter orders
            limit: Maximum number of orders to return

        Returns:
            List of historical orders
        """
        orders = self._order_history
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders[-limit:]

    def get_order_status(self, order_id: str) -> OrderStatus | None:
        """Get status of an order.

        Args:
            order_id: Order ID to check

        Returns:
            OrderStatus if found, None otherwise
        """
        order = self._orders.get(order_id)
        if order:
            return order.status

        for order in reversed(self._order_history):
            if order.order_id == order_id:
                return order.status

        return None
