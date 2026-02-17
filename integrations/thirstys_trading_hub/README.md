# Thirsty's Trading Hub Integration

## Overview

This module integrates **Thirsty's Trading Hub** into Project AI, providing comprehensive trading capabilities, market analysis, and portfolio management within the AI governance framework.

## Architecture

The Trading Hub integration follows Project AI's governance-first architecture, ensuring all trading operations are subject to:

- **Four Laws Validation**: Ethical constraints on trading actions
- **Cerberus Security**: Threat detection and prevention
- **TARL Policy Enforcement**: Trading policy compliance
- **Audit Logging**: Complete trading activity trail

## Features

### 1. Market Data Integration

- Real-time market data streaming
- Historical data analysis
- Multi-asset support (stocks, crypto, forex, commodities)
- Technical indicator calculations

### 2. Trading Operations

- Order placement and management
- Portfolio tracking and rebalancing
- Risk management and position sizing
- Automated trading strategies

### 3. Analysis & Reporting

- Performance analytics
- Risk metrics and reporting
- Trade journaling and insights
- Market sentiment analysis

### 4. Governance & Safety

- Trading limit enforcement
- Risk threshold monitoring
- Compliance checking
- Emergency stop mechanisms

## Installation

### Dependencies

Add to `requirements.txt`:
```
alpaca-trade-api>=3.0.0
ccxt>=4.0.0  # Cryptocurrency exchange integration
pandas>=1.5.0
numpy>=1.20.0
ta>=0.11.0  # Technical analysis library
```

### Environment Configuration

Add to `.env`:
```bash

# Trading Hub Configuration

TRADING_HUB_ENABLED=true
TRADING_MODE=paper  # paper or live

# Alpaca API (for stocks)

ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Binance API (for crypto)

BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here

# Risk Limits

TRADING_MAX_POSITION_SIZE=10000
TRADING_MAX_DAILY_LOSS=500
TRADING_MAX_PORTFOLIO_RISK=0.02
```

## Usage

### Basic Trading

```python
from integrations.thirstys_trading_hub import TradingHub

# Initialize trading hub

hub = TradingHub(mode="paper")

# Get market data

market_data = hub.get_market_data("AAPL")

# Place order (subject to governance)

order = hub.place_order(
    symbol="AAPL",
    quantity=10,
    side="buy",
    order_type="market"
)

# Check portfolio

portfolio = hub.get_portfolio()
```

## Testing

### Unit Tests

```bash
pytest integrations/thirstys_trading_hub/tests/ -v
```

### E2E Tests

```bash
pytest e2e/scenarios/test_trading_hub_e2e.py -v
```

### Paper Trading

Test strategies in paper trading mode before live deployment:

```python
hub = TradingHub(mode="paper")

# All trades are simulated

```

## License

MIT License - Same as Project AI
