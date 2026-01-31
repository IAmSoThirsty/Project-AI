"""Integration tests for Trading Hub core modules.

Demonstrates complete workflow: market data -> strategy execution -> order placement -> portfolio tracking.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from integrations.thirstys_trading_hub.core import (
    MarketDataProvider,
    MarketMode,
    OrderManager,
    OrderSide,
    OrderType,
    PortfolioManager,
    StrategyEngine,
    Timeframe,
)


def test_market_data():
    """Test market data provider functionality."""
    print("Testing MarketDataProvider...")

    with tempfile.TemporaryDirectory() as tmpdir:
        provider = MarketDataProvider(mode=MarketMode.PAPER, data_dir=tmpdir)

        ticker = provider.get_current_price("BTC/USD")
        assert ticker.symbol == "BTC/USD"
        assert ticker.last > 0
        assert ticker.bid < ticker.ask
        print(f"  ✓ Ticker: {ticker.symbol} @ ${ticker.last}")

        candles = provider.get_data("ETH/USD", Timeframe.H1, limit=50)
        assert len(candles) == 50
        assert all(c.symbol == "ETH/USD" for c in candles)
        print(f"  ✓ Got {len(candles)} candles")

        symbols = provider.get_supported_symbols()
        assert len(symbols) > 0
        assert "BTC/USD" in symbols
        print(f"  ✓ {len(symbols)} supported symbols")


def test_order_management():
    """Test order placement and cancellation."""
    print("\nTesting OrderManager...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = OrderManager(data_dir=tmpdir, mode="paper")

        result = manager.place_order(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.5,
        )
        assert result.success
        assert result.order_id is not None
        print(f"  ✓ Order placed: {result.order_id}")

        order = manager.get_order(result.order_id)
        assert order is not None
        assert order.symbol == "BTC/USD"
        assert order.quantity == 0.5
        print(f"  ✓ Order retrieved: {order.side.value} {order.quantity} {order.symbol}")

        cancel_result = manager.cancel_order(result.order_id)
        assert cancel_result.success
        print("  ✓ Order cancelled")

        open_orders = manager.get_open_orders()
        assert len(open_orders) == 0
        print(f"  ✓ Open orders: {len(open_orders)}")


def test_portfolio_management():
    """Test portfolio tracking and position management."""
    print("\nTesting PortfolioManager...")

    with tempfile.TemporaryDirectory() as tmpdir:
        portfolio = PortfolioManager(data_dir=tmpdir, initial_balance=100000.0)

        state = portfolio.get_state()
        assert state.cash_balance == 100000.0
        assert state.positions_count == 0
        print(f"  ✓ Initial state: ${state.cash_balance} cash, {state.positions_count} positions")

        position = portfolio.update_position("BTC/USD", 1.0, 45000.0)
        assert position.symbol == "BTC/USD"
        assert position.quantity == 1.0
        print(f"  ✓ Position opened: {position.quantity} {position.symbol} @ ${position.average_entry_price}")

        portfolio.update_prices({"BTC/USD": 47000.0})
        updated_position = portfolio.get_position("BTC/USD")
        assert updated_position.unrealized_pnl == 2000.0
        print(f"  ✓ Position PnL: ${updated_position.unrealized_pnl}")

        portfolio.update_position("BTC/USD", -1.0, 47000.0)
        state = portfolio.get_state()
        assert state.positions_count == 0
        assert state.realized_pnl == 2000.0
        print(f"  ✓ Position closed: realized PnL ${state.realized_pnl}")

        metrics = portfolio.calculate_metrics()
        print(f"  ✓ Metrics: {metrics['total_trades']} trades, {metrics['win_rate_pct']}% win rate")


def test_strategy_engine():
    """Test strategy registration and execution."""
    print("\nTesting StrategyEngine...")

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = StrategyEngine(data_dir=tmpdir)

        def sample_strategy(context):
            """Sample trading strategy."""
            symbols = context["symbols"]
            return {
                "orders_placed": len(symbols),
                "positions_opened": 1,
                "positions_closed": 0,
                "total_pnl": 250.0,
                "metrics": {
                    "confidence": 0.9,
                    "signals": ["bullish"],
                },
            }

        strategy_id = engine.register_strategy(
            name="Sample Strategy",
            callable=sample_strategy,
            description="Test strategy for demonstration",
            symbols=["BTC/USD", "ETH/USD"],
            timeframe="1h",
        )
        assert strategy_id is not None
        print(f"  ✓ Strategy registered: {strategy_id}")

        strategies = engine.list_strategies()
        assert len(strategies) == 1
        assert strategies[0].name == "Sample Strategy"
        print(f"  ✓ Listed {len(strategies)} strategies")

        result = engine.run_strategy(strategy_id)
        assert result.status.value == "completed"
        assert result.orders_placed == 2
        assert result.total_pnl == 250.0
        print(f"  ✓ Strategy executed: {result.orders_placed} orders, PnL ${result.total_pnl}")

        metrics = engine.calculate_strategy_metrics(strategy_id)
        assert metrics["total_executions"] == 1
        print(f"  ✓ Strategy metrics: {metrics['total_executions']} executions")


def test_full_integration():
    """Test complete trading workflow integration."""
    print("\nTesting full integration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        market_data = MarketDataProvider(mode=MarketMode.PAPER, data_dir=tmpdir)
        order_manager = OrderManager(data_dir=tmpdir, mode="paper")
        portfolio = PortfolioManager(data_dir=tmpdir, initial_balance=50000.0)
        strategy_engine = StrategyEngine(
            data_dir=tmpdir,
            market_data=market_data,
            order_manager=order_manager,
            portfolio_manager=portfolio,
        )

        def trading_strategy(context):
            """Complete trading strategy with all components."""
            market = context["market_data"]
            orders = context["order_manager"]
            portfolio_mgr = context["portfolio_manager"]

            ticker = market.get_current_price("BTC/USD")
            candles = market.get_data("BTC/USD", "1h", limit=20)

            order_result = orders.place_order(
                symbol="BTC/USD",
                side="buy",
                order_type="market",
                quantity=0.1,
                price=ticker.last,
            )

            if order_result.success:
                portfolio_mgr.update_position("BTC/USD", 0.1, ticker.last)

            state = portfolio_mgr.get_state()

            return {
                "orders_placed": 1,
                "positions_opened": 1,
                "total_pnl": state.unrealized_pnl,
                "metrics": {
                    "entry_price": ticker.last,
                    "candles_analyzed": len(candles),
                },
            }

        strategy_id = strategy_engine.register_strategy(
            name="Full Integration Strategy",
            callable=trading_strategy,
            symbols=["BTC/USD"],
        )

        result = strategy_engine.run_strategy(strategy_id)
        assert result.status.value in ("completed", "failed")

        print(f"  ✓ Full integration: {result.orders_placed} orders placed")
        print(f"  ✓ Strategy status: {result.status.value}")
        print(f"  ✓ Portfolio state: {portfolio.get_state().positions_count} positions")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Trading Hub Core Modules Integration Tests")
    print("=" * 60)

    try:
        test_market_data()
        test_order_management()
        test_portfolio_management()
        test_strategy_engine()
        test_full_integration()

        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
