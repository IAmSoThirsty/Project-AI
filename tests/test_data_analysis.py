import tempfile
from pathlib import Path

import pandas as pd

from app.core.data_analysis import DataAnalyzer


class TestDataAnalyzer:
    """Smoke tests for the data analysis helper."""

    def _write_csv(self, tmpdir: str) -> str:
        df = pd.DataFrame(
            {
                "value": [1, 2, 3],
                "category": ["A", "B", "A"],
                "score": [0.1, 0.3, 0.5],
            }
        )
        path = Path(tmpdir) / "data.csv"
        df.to_csv(path, index=False)
        return str(path)

    def test_load_csv_and_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DataAnalyzer()
            csv_path = self._write_csv(tmpdir)

            assert analyzer.load_data(csv_path) is True
            summary = analyzer.get_summary_stats()

            assert summary["row_count"] == 3
            assert summary["column_count"] == 3
            assert summary["basic_stats"]["value"]["mean"] == 2.0

    def test_create_visualization_scatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DataAnalyzer()
            csv_path = self._write_csv(tmpdir)

            analyzer.load_data(csv_path)
            fig = analyzer.create_visualization("scatter", x_col="value", y_col="score")

            assert fig is not None
            assert hasattr(fig, "figure") or hasattr(fig, "savefig")

    def test_perform_clustering_returns_clusters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DataAnalyzer()
            csv_path = self._write_csv(tmpdir)

            analyzer.load_data(csv_path)
            fig_clusters = analyzer.perform_clustering(columns=["value", "score"], n_clusters=2)

            fig, clusters = fig_clusters
            assert fig is not None
            assert len(clusters) == 3
