"""Phase 2C tests: hierarchical ETL fallback (LIVE -> CACHE -> SYNTHETIC)."""

from __future__ import annotations

import json
from pathlib import Path

from global_scenario._simulation_contract import RiskDomain
from global_scenario.global_scenario_engine import (
    DataSourceTier,
    DomainLoadResult,
    ResilientDataSource,
)


def _make_engine(tmp_path: Path) -> ResilientDataSource:
    return ResilientDataSource(str(tmp_path / "cache"))


def _seed_cache(engine: ResilientDataSource, url: str, params: dict, payload: dict) -> None:
    key = engine._cache_key(url, params)
    (engine.cache_dir / f"{key}.json").write_text(json.dumps(payload))


def test_live_tier_when_api_returns_data(tmp_path: Path, monkeypatch):
    engine = _make_engine(tmp_path)

    def fake_live(url, params=None):
        return ["meta", [{"countryiso3code": "USA", "date": "2020", "value": 1.5}]]

    monkeypatch.setattr(engine, "_fetch_live", fake_live)
    res: DomainLoadResult = engine.load_with_fallback(
        domain=RiskDomain.ECONOMIC,
        live_url="http://x",
        live_params={"a": "1"},
        parse=lambda r: {"USA": {2020: 1.5}} if r else {},
        synthetic=lambda: {},
        source_name="world_bank",
    )
    assert res.tier is DataSourceTier.LIVE
    assert res.data == {"USA": {2020: 1.5}}


def test_cache_tier_when_live_empty(tmp_path: Path, monkeypatch):
    engine = _make_engine(tmp_path)
    monkeypatch.setattr(engine, "_fetch_live", lambda url, params=None: None)
    # Seed a stale/any-age cache blob
    _seed_cache(
        engine,
        "http://x",
        {"a": "1"},
        {
            "timestamp": "2020-01-01T00:00:00+00:00",
            "response": ["meta", [{"countryiso3code": "USA", "date": "2020", "value": 2.0}]],
        },
    )
    res = engine.load_with_fallback(
        domain=RiskDomain.INFLATION,
        live_url="http://x",
        live_params={"a": "1"},
        parse=lambda r: {"USA": {2020: 2.0}} if r else {},
        synthetic=lambda: {},
        source_name="world_bank",
    )
    assert res.tier is DataSourceTier.CACHE
    assert res.data == {"USA": {2020: 2.0}}


def test_synthetic_tier_when_live_and_cache_empty(tmp_path: Path, monkeypatch):
    engine = _make_engine(tmp_path)
    monkeypatch.setattr(engine, "_fetch_live", lambda url, params=None: None)
    res = engine.load_with_fallback(
        domain=RiskDomain.CLIMATE,
        live_url="http://x",
        live_params={"a": "1"},
        parse=lambda r: {},
        synthetic=lambda: {"USA": {2020: 0.0}},
        source_name="world_bank",
    )
    assert res.tier is DataSourceTier.SYNTHETIC
    assert res.data == {"USA": {2020: 0.0}}
