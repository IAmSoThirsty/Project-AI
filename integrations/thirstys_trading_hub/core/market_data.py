"""Market data provider for Thirsty's Trading Hub.

Provides real-time and historical market data with support for paper and live modes.
In paper mode, generates realistic mock data for testing strategies.
"""

import json
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MarketMode(Enum):
    """Trading mode configuration."""

    PAPER = "paper"
    LIVE = "live"


class Timeframe(Enum):
    """Supported timeframe intervals."""

    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


@dataclass
class OHLCV:
    """Open, High, Low, Close, Volume candle data."""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str


@dataclass
class Ticker:
    """Current market ticker information."""

    symbol: str
    bid: float
    ask: float
    last: float
    volume_24h: float
    timestamp: int


class MarketDataProvider:
    """Market data provider with paper and live mode support."""

    def __init__(
        self,
        mode: MarketMode = MarketMode.PAPER,
        data_dir: str = "data/trading_hub",
        api_key: str | None = None,
        api_secret: str | None = None,
    ):
        """Initialize market data provider.

        Args:
            mode: Trading mode (paper or live)
            data_dir: Directory for caching market data
            api_key: API key for live mode (optional)
            api_secret: API secret for live mode (optional)
        """
        self.mode = mode
        self.data_dir = data_dir
        self.api_key = api_key
        self.api_secret = api_secret
        self._cache: dict[str, Any] = {}
        self._base_prices: dict[str, float] = {}

        os.makedirs(data_dir, exist_ok=True)
        self._load_cache()

        logger.info("MarketDataProvider initialized in %s mode", mode.value)

    def _load_cache(self) -> None:
        """Load cached market data from disk."""
        cache_file = os.path.join(self.data_dir, "market_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file) as f:
                    self._cache = json.load(f)
                logger.info("Loaded market data cache with %s entries", len(self._cache))
            except Exception as e:
                logger.error("Failed to load market cache: %s", e)
                self._cache = {}

    def _save_cache(self) -> None:
        """Save market data cache to disk."""
        cache_file = os.path.join(self.data_dir, "market_cache.json")
        try:
            with open(cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.error("Failed to save market cache: %s", e)

    def _get_base_price(self, symbol: str) -> float:
        """Get or generate base price for symbol."""
        if symbol not in self._base_prices:
            symbol_upper = symbol.upper()
            if "BTC" in symbol_upper:
                self._base_prices[symbol] = 45000.0 + random.uniform(-5000, 5000)
            elif "ETH" in symbol_upper:
                self._base_prices[symbol] = 2500.0 + random.uniform(-500, 500)
            elif "USD" in symbol_upper:
                self._base_prices[symbol] = 1.0
            else:
                self._base_prices[symbol] = 100.0 + random.uniform(-50, 50)
        return self._base_prices[symbol]

    def _generate_mock_ohlcv(
        self, symbol: str, timeframe: Timeframe, limit: int
    ) -> list[OHLCV]:
        """Generate realistic mock OHLCV data for paper mode.

        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe
            limit: Number of candles to generate

        Returns:
            List of OHLCV candles
        """
        base_price = self._get_base_price(symbol)
        candles = []

        timeframe_minutes = {
            Timeframe.M1: 1,
            Timeframe.M5: 5,
            Timeframe.M15: 15,
            Timeframe.M30: 30,
            Timeframe.H1: 60,
            Timeframe.H4: 240,
            Timeframe.D1: 1440,
            Timeframe.W1: 10080,
        }
        minutes = timeframe_minutes.get(timeframe, 60)

        current_time = datetime.now(UTC)
        current_price = base_price

        for i in range(limit):
            timestamp_dt = current_time - timedelta(minutes=minutes * (limit - i - 1))
            timestamp_ms = int(timestamp_dt.timestamp() * 1000)

            volatility = 0.02
            price_change = random.uniform(-volatility, volatility)
            open_price = current_price
            close_price = open_price * (1 + price_change)

            high_offset = random.uniform(0, volatility / 2)
            low_offset = random.uniform(0, volatility / 2)
            high_price = max(open_price, close_price) * (1 + high_offset)
            low_price = min(open_price, close_price) * (1 - low_offset)

            volume = random.uniform(100, 10000) * (base_price / 100)

            candles.append(
                OHLCV(
                    timestamp=timestamp_ms,
                    open=round(open_price, 2),
                    high=round(high_price, 2),
                    low=round(low_price, 2),
                    close=round(close_price, 2),
                    volume=round(volume, 2),
                    symbol=symbol,
                )
            )

            current_price = close_price

        self._base_prices[symbol] = current_price
        return candles

    def get_data(
        self, symbol: str, timeframe: Timeframe | str, limit: int = 100
    ) -> list[OHLCV]:
        """Get historical OHLCV data for symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USD')
            timeframe: Candle timeframe (enum or string)
            limit: Number of candles to retrieve (default: 100)

        Returns:
            List of OHLCV candles ordered by timestamp

        Raises:
            ValueError: If invalid timeframe provided
        """
        if isinstance(timeframe, str):
            try:
                timeframe = Timeframe(timeframe)
            except ValueError as e:
                raise ValueError(
                    f"Invalid timeframe: {timeframe}. "
                    f"Must be one of: {[t.value for t in Timeframe]}"
                ) from e

        cache_key = f"{symbol}_{timeframe.value}_{limit}"

        if self.mode == MarketMode.PAPER:
            if cache_key in self._cache:
                cached_data = self._cache[cache_key]
                cache_age = time.time() - cached_data.get("timestamp", 0)
                if cache_age < 300:
                    logger.debug("Using cached data for %s", cache_key)
                    return [
                        OHLCV(**candle) for candle in cached_data.get("candles", [])
                    ]

            candles = self._generate_mock_ohlcv(symbol, timeframe, limit)
            self._cache[cache_key] = {
                "timestamp": time.time(),
                "candles": [
                    {
                        "timestamp": c.timestamp,
                        "open": c.open,
                        "high": c.high,
                        "low": c.low,
                        "close": c.close,
                        "volume": c.volume,
                        "symbol": c.symbol,
                    }
                    for c in candles
                ],
            }
            self._save_cache()

            logger.info("Generated %s mock candles for %s %s", len(candles), symbol, timeframe.value)
            return candles

        raise NotImplementedError("Live mode requires exchange API integration")

    def get_current_price(self, symbol: str) -> Ticker:
        """Get current market price for symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USD')

        Returns:
            Current ticker information

        Raises:
            ValueError: If symbol is invalid or unavailable
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"Invalid symbol: {symbol}")

        if self.mode == MarketMode.PAPER:
            base_price = self._get_base_price(symbol)

            spread = base_price * 0.001
            last_price = base_price
            bid_price = last_price - spread / 2
            ask_price = last_price + spread / 2

            volume_24h = random.uniform(1000, 100000) * (base_price / 100)

            ticker = Ticker(
                symbol=symbol,
                bid=round(bid_price, 2),
                ask=round(ask_price, 2),
                last=round(last_price, 2),
                volume_24h=round(volume_24h, 2),
                timestamp=int(datetime.now(UTC).timestamp() * 1000),
            )

            logger.debug("Generated ticker for %s: last=%s", symbol, ticker.last)
            return ticker

        raise NotImplementedError("Live mode requires exchange API integration")

    def get_supported_symbols(self) -> list[str]:
        """Get list of supported trading symbols.

        Returns:
            List of supported symbols
        """
        if self.mode == MarketMode.PAPER:
            return [
                "BTC/USD",
                "ETH/USD",
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USD",
                "AAPL/USD",
                "MSFT/USD",
                "GOOGL/USD",
            ]

        raise NotImplementedError("Live mode requires exchange API integration")

    def validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol is supported.

        Args:
            symbol: Trading pair symbol

        Returns:
            True if symbol is supported, False otherwise
        """
        supported = self.get_supported_symbols()
        return symbol in supported
