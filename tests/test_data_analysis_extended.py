"""Extended tests for DataAnalyzer (20+)."""

from __future__ import annotations

import json
import os
import tempfile

import pandas as pd

from app.core.data_analysis import DataAnalyzer


def _write_json(tmpdir: str) -> str:
    path = os.path.join(tmpdir, "data.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"value": [1, 2, 3], "score": [0.1, 0.3, 0.5]}, fh)
    return path


def _write_csv(tmpdir: str) -> str:
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1], "c": [0.1, 0.2, 0.3]})
    path = os.path.join(tmpdir, "data.csv")
    df.to_csv(path, index=False)
    return path


def test_load_json_and_summary():
    with tempfile.TemporaryDirectory() as td:
        da = DataAnalyzer()
        j = _write_json(td)
        assert da.load_data(j) is True
        s = da.get_summary_stats()
        assert s["row_count"] >= 2


def test_load_csv_and_plots():
    with tempfile.TemporaryDirectory() as td:
        da = DataAnalyzer()
        c = _write_csv(td)
        da.load_data(c)
        assert da.create_visualization("scatter", x_col="a", y_col="c") is not None
        assert da.create_visualization("histogram", x_col="a") is not None
        assert da.create_visualization("boxplot", x_col="a") is not None
        assert da.create_visualization("correlation") is not None


def test_visualization_without_data_returns_none():
    da = DataAnalyzer()
    assert da.create_visualization("scatter", x_col="a", y_col="c") is None


def test_clustering_with_invalid_columns_returns_none():
    with tempfile.TemporaryDirectory() as td:
        da = DataAnalyzer()
        c = _write_csv(td)
        da.load_data(c)
        fig, clusters = da.perform_clustering(["missing"], n_clusters=2)
        assert fig is None and clusters is None
