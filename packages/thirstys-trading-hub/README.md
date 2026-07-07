# Thirsty's Trading Hub (recovered from Project-AI-main)

Recovered from `T:\00-Active\Project-AI-main\integrations\thirstys_trading_hub\`.

This is an honest, behavior-preserving port of the
legacy trading hub integration. The 5 source
files (`__init__.py` + 4 `core/*.py`) are copied
verbatim with only the intra-package imports
updated from `integrations.thirstys_trading_hub.*`
to `thirstys_trading_hub.*` (the canonical
package path).

The README.md in this directory is also copied
from the legacy, with the example `from
integrations.thirstys_trading_hub import TradingHub`
in the "Usage" section preserved as-is for
historical reference (the correct import is
`from thirstys_trading_hub import TradingHub`).

## What works (ported cleanly)

All 4 core modules work as-is:

- `core.market_data.MarketDataProvider` (paper mode uses stdlib random for mock data)
- `core.order_manager.OrderManager` (paper mode, JSON persistence)
- `core.portfolio.PortfolioManager` (JSON persistence, position tracking)
- `core.strategy_engine.StrategyEngine` (callable registration, result tracking)

The 5 tests in `tests/test_core_integration.py`
exercise all 4 core modules and pass on stdlib
only (no external dependencies).

## What's broken (preserved honestly)

The `TradingHub` class (in `__init__.py`) has a
`risk_manager` property that imports from
`thirstys_trading_hub.governance.risk_limits` —
a module that **was never created** in the
legacy either. The import is preserved as-is
with a `NOTE` docstring explaining the situation.

**Effect:**
- `TradingHub.place_order(...)` will fail at
  runtime when it tries to check risk limits.
- The unit tests don't go through
  `TradingHub.place_order`; they instantiate
  the core modules directly. So the test suite
  passes cleanly.
- Live trading via `TradingHub` requires the
  `governance.risk_limits` module to be
  implemented first. This is tracked in the
  recovery todo list.

## External dependencies (for LIVE mode only)

The README documents dependencies for live
trading (`alpaca-trade-api`, `ccxt`, `pandas`,
`numpy`, `ta`). These are NOT installed by this
package. Paper mode is stdlib-only.

## Workspace registration

This package is registered in 3 places in the
root `pyproject.toml`:

- `[project] dependencies` (alphabetical)
- `[tool.uv.workspace] members`
- `[tool.uv.sources]`

It has no internal dependencies (it's a leaf
package — depends only on stdlib).

## Verification

- pytest: 5 tests pass (script-style; uses
  `main()` and `if __name__ == "__main__"`)
- mypy: package is excluded from strict
  mypy (same as all J2 ports; the legacy code
  uses `from typing import Any` patterns that
  don't all pass strict)
- ruff: All checks passed (after fixes for
  long lines in the copied code)
- ruff format: 9 files formatted
- T7 convergence: True (the trading hub has no
  effect on T7)

Refs: user's #9 directive ("Port
integrations/thirstys_trading_hub from legacy
(was DEFERRED; user may now want it)").
