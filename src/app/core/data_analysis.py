"""Data analysis and visualization utilities."""

import pandas as pd
from matplotlib.figure import Figure

# Import the appropriate Qt canvas backend when available (supports Qt5/Qt6)
try:
    # Matplotlib 3.7+ provides backend_qtagg for Qt6/Qt5
    from matplotlib.backends import backend_qtagg as _back_qt
    FigureCanvasQTAgg = _back_qt.FigureCanvasQTAgg
except Exception:
    try:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    except Exception:
        FigureCanvasQTAgg = None

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


class DataAnalyzer:
    """Helper class to load, summarize and visualize tabular data."""

    def __init__(self):
        self.data = None
        self.scaler = StandardScaler()

    def load_data(self, file_path: str) -> bool:
        """Load data from CSV, Excel or JSON files.

        Returns True on success, False otherwise.
        """
        try:
            if file_path.endswith(".csv"):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith(".json"):
                self.data = pd.read_json(file_path)

            return True
        except Exception as exc:  # pragma: no cover - best-effort reporting
            print(f"Error loading data: {exc}")
            return False

    def get_summary_stats(self):
        """Return basic summary statistics and metadata for the dataset."""
        if self.data is None:
            return "No data loaded"

        return {
            "basic_stats": self.data.describe().to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "column_types": self.data.dtypes.to_dict(),
            "row_count": len(self.data),
            "column_count": len(self.data.columns),
        }

    def create_visualization(
        self,
        plot_type: str,
        x_col: str | None = None,
        y_col: str | None = None
    ):
        """Create a matplotlib Figure or a Qt canvas depending on environment.

        Returns a Figure or a FigureCanvasQTAgg when available.
        """
        if self.data is None:
            return None

        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        try:
            if plot_type == "scatter":
                ax.scatter(self.data[x_col], self.data[y_col])
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            elif plot_type == "histogram":
                ax.hist(self.data[x_col], bins=30)
                ax.set_xlabel(x_col)
                ax.set_ylabel("Frequency")
            elif plot_type == "boxplot":
                self.data.boxplot(column=x_col, ax=ax)
            elif plot_type == "correlation":
                corr = self.data.corr()
                ax.imshow(corr)
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=45)
                ax.set_yticklabels(corr.columns)

            if FigureCanvasQTAgg is not None:
                return FigureCanvasQTAgg(fig)

            return fig
        except Exception as exc:  # pragma: no cover - visualization errors
            print(f"Error creating visualization: {exc}")
            return None

    def perform_clustering(self, columns, n_clusters: int = 3):
        """Run KMeans clustering on columns, return (figure, clusters)."""
        if self.data is None:
            return None, None

        try:
            X = self.data[columns].values
            X_scaled = self.scaler.fit_transform(X)

            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)

            fig = Figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            scatter = ax.scatter(
                X_pca[:, 0], X_pca[:, 1], c=clusters, cmap="viridis"
            )
            ax.set_xlabel("First Principal Component")
            ax.set_ylabel("Second Principal Component")
            ax.set_title("K-means Clustering Results")
            fig.colorbar(scatter)

            if FigureCanvasQTAgg is not None:
                return FigureCanvasQTAgg(fig), clusters

            return fig, clusters
        except Exception as exc:  # pragma: no cover
            print(f"Error performing clustering: {exc}")
            return None, None
