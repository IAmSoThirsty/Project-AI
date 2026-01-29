# Trading Hub Core Modules

Production-grade core modules for Thirsty's Trading Hub integration with Project AI.

## Overview

The Trading Hub core provides four essential modules for algorithmic trading:

1. **MarketDataProvider** - Real-time and historical market data
2. **OrderManager** - Order placement with governance routing
3. **PortfolioManager** - Position and balance tracking
4. **StrategyEngine** - Trading strategy execution framework

All modules follow Project AI's coding standards with:
- Full error handling and logging
- JSON persistence to data directories
- Type hints and comprehensive docstrings
- Deterministic behavior for testing
- Paper and live mode support

## Quick Start

```python
from integrations.thirstys_trading_hub.core import (
    MarketDataProvider,
    MarketMode,
    OrderManager,
    PortfolioManager,
    StrategyEngine,
    Timeframe,
)

# Initialize components
market_data = MarketDataProvider(mode=MarketMode.PAPER)
order_manager = OrderManager(mode="paper")
portfolio = PortfolioManager(initial_balance=100000.0)
strategy_engine = StrategyEngine(
    market_data=market_data,
    order_manager=order_manager,
    portfolio_manager=portfolio,
)

# Get market data
ticker = market_data.get_current_price("BTC/USD")
candles = market_data.get_data("BTC/USD", Timeframe.H1, limit=100)

# Place order
result = order_manager.place_order(
    symbol="BTC/USD",
    side="buy",
    order_type="market",
    quantity=0.1,
)

# Track portfolio
state = portfolio.get_state()
print(f"Equity: ${state.total_equity}, PnL: ${state.total_pnl}")
```

## Module Details

### MarketDataProvider

Provides market data with caching and paper mode mock data generation.

**Key Features:**
- Mock OHLCV data generation for paper trading
- Realistic price movements with configurable volatility
- Automatic caching with 5-minute TTL
- Support for multiple timeframes (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
- Ticker data with bid/ask spreads

**Methods:**
- `get_data(symbol, timeframe, limit)` - Historical OHLCV candles
- `get_current_price(symbol)` - Current ticker with bid/ask
- `get_supported_symbols()` - List of tradeable symbols
- `validate_symbol(symbol)` - Check if symbol is supported

**Example:**
```python
provider = MarketDataProvider(mode=MarketMode.PAPER)

# Get 50 hourly candles
candles = provider.get_data("ETH/USD", Timeframe.H1, limit=50)

# Get current price
ticker = provider.get_current_price("BTC/USD")
print(f"Bid: ${ticker.bid}, Ask: ${ticker.ask}, Last: ${ticker.last}")
```

### OrderManager

Handles order lifecycle with kernel governance integration.

**Key Features:**
- Governance routing through CognitionKernel
- Automatic risk assessment
- Paper mode instant fill simulation
- Order status tracking and history
- Bulk order cancellation

**Order Types:**
- Market orders (immediate execution)
- Limit orders (price-specific execution)
- Stop-loss orders
- Take-profit orders

**Methods:**
- `place_order(...)` - Place new order with governance approval
- `cancel_order(order_id)` - Cancel single order
- `cancel_all_orders(symbol=None)` - Cancel all or symbol-specific orders
- `get_order(order_id)` - Retrieve order details
- `get_open_orders(symbol=None)` - List open orders
- `get_order_history(symbol=None, limit=100)` - Historical orders

**Example:**
```python
manager = OrderManager(mode="paper", kernel=cognition_kernel)

# Place market order
result = manager.place_order(
    symbol="BTC/USD",
    side="buy",
    order_type="market",
    quantity=0.5,
)

if result.success:
    print(f"Order {result.order_id} placed: {result.message}")
    
    # Cancel if needed
    manager.cancel_order(result.order_id)
```

### PortfolioManager

Tracks positions, balances, and performance metrics.

**Key Features:**
- Position tracking with average entry price
- Real-time unrealized PnL calculation
- Realized PnL on position closes
- Multi-currency balance support
- Trade history persistence
- Performance metrics calculation

**Methods:**
- `get_state()` - Complete portfolio snapshot
- `get_positions()` - All open positions
- `get_position(symbol)` - Specific position
- `update_position(symbol, quantity, price, ...)` - Open/modify position
- `update_prices(prices)` - Bulk price update for PnL
- `get_balance(currency)` - Currency balance
- `update_balance(currency, amount, ...)` - Modify balance
- `calculate_metrics()` - Performance statistics

**Example:**
```python
portfolio = PortfolioManager(initial_balance=50000.0)

# Open position
position = portfolio.update_position("BTC/USD", 1.0, 45000.0)

# Update market price
portfolio.update_prices({"BTC/USD": 46500.0})

# Check PnL
state = portfolio.get_state()
print(f"Unrealized PnL: ${state.unrealized_pnl}")

# Close position
portfolio.update_position("BTC/USD", -1.0, 46500.0)
print(f"Realized PnL: ${state.realized_pnl}")
```

### StrategyEngine

Framework for trading strategy registration and execution.

**Key Features:**
- Dynamic strategy registration
- Context-based strategy execution
- Result tracking and metrics
- Enable/disable strategies
- Aggregate performance analytics
- Error handling and recovery

**Methods:**
- `register_strategy(name, callable, ...)` - Register new strategy
- `unregister_strategy(strategy_id)` - Remove strategy
- `run_strategy(strategy_id, override_parameters=None)` - Execute strategy
- `stop_strategy(strategy_id)` - Stop running strategy
- `list_strategies()` - All registered strategies
- `get_result(strategy_id)` - Most recent result
- `calculate_strategy_metrics(strategy_id)` - Aggregate stats
- `enable_strategy(strategy_id)` / `disable_strategy(strategy_id)`

**Example:**
```python
def moving_average_strategy(context):
    """Simple MA crossover strategy."""
    market = context["market_data"]
    orders = context["order_manager"]
    
    # Get market data
    candles = market.get_data("BTC/USD", "1h", limit=50)
    
    # Calculate signals
    short_ma = sum(c.close for c in candles[-10:]) / 10
    long_ma = sum(c.close for c in candles) / 50
    
    # Place orders based on signal
    if short_ma > long_ma:
        result = orders.place_order("BTC/USD", "buy", "market", 0.1)
        return {
            "orders_placed": 1 if result.success else 0,
            "signal": "bullish",
        }
    
    return {"orders_placed": 0, "signal": "neutral"}

# Register strategy
engine = StrategyEngine(
    market_data=market_data,
    order_manager=order_manager,
)

strategy_id = engine.register_strategy(
    name="MA Crossover",
    callable=moving_average_strategy,
    symbols=["BTC/USD"],
    timeframe="1h",
)

# Execute strategy
result = engine.run_strategy(strategy_id)
print(f"Status: {result.status.value}, Orders: {result.orders_placed}")

# Get metrics
metrics = engine.calculate_strategy_metrics(strategy_id)
print(f"Win rate: {metrics['win_rate_pct']}%")
```

## Governance Integration

The OrderManager integrates with Project AI's CognitionKernel for governance:

```python
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
order_manager = OrderManager(mode="paper", kernel=kernel)

# All orders route through governance
result = order_manager.place_order(
    symbol="BTC/USD",
    side="buy",
    order_type="market",
    quantity=1.0,
)

# Check governance decision
if result.governance_decision:
    print(f"Governance: {result.governance_decision['reason']}")
```

## Testing

Run the integration tests:

```bash
cd integrations/thirstys_trading_hub/tests
python3 test_core_integration.py
```

Tests cover:
- Market data generation and caching
- Order placement and cancellation
- Portfolio position tracking
- Strategy execution
- Full end-to-end workflow

## Data Persistence

All modules persist state to JSON files in `data_dir`:

- **market_cache.json** - Cached market data
- **orders.json** - Order history and state
- **portfolio.json** - Positions and balances
- **strategies.json** - Strategy definitions and results

Files use atomic writes to prevent corruption.

## Error Handling

All modules follow Project AI's error handling patterns:

- Python `logging` module for all logs
- Try-except blocks with detailed error messages
- Validation of inputs with clear error messages
- Graceful degradation when optional components missing

## Architecture Compliance

These modules follow Project AI's architecture:

✅ Production-grade (no TODOs or skeletons)
✅ Type hints on all public methods
✅ Docstrings for all classes and methods
✅ JSON persistence with atomic writes
✅ Deterministic behavior for testing
✅ Error handling and logging
✅ Data directory isolation
✅ Kernel governance routing

## Next Steps

1. **Connectors** - Exchange API integrations (Binance, Coinbase, etc.)
2. **Analysis** - Technical indicators and signal generation
3. **Governance** - Strategy approval workflows
4. **UI Integration** - Desktop app dashboard widgets

## License

Part of Project-AI. See main repository LICENSE.
