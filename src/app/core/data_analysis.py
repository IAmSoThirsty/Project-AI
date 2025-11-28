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
        """Return basic summary statistics and metadata for the loaded dataset."""
        if self.data is None:
            return "No data loaded"

        return {
            "basic_stats": self.data.describe().to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "column_types": self.data.dtypes.to_dict(),
            "row_count": len(self.data),
            "column_count": len(self.data.columns),
        }

    def create_visualization(self, plot_type: str, x_col: str | None = None, y_col: str | None = None):
        """Create a matplotlib Figure or a Qt canvas depending on environment.

        Returns a Figure or a FigureCanvasQTAgg when available.
        """
        if self.data is None:
            return None

        figure = Figure(figsize=(8, 6))
        axes = figure.add_subplot(111)

        try:
            if plot_type == "scatter":
                axes.scatter(self.data[x_col], self.data[y_col])
                axes.set_xlabel(x_col)
                axes.set_ylabel(y_col)
            elif plot_type == "histogram":
                axes.hist(self.data[x_col], bins=30)
                axes.set_xlabel(x_col)
                axes.set_ylabel("Frequency")
            elif plot_type == "boxplot":
                self.data.boxplot(column=x_col, ax=axes)
            elif plot_type == "correlation":
                correlation_matrix = self.data.corr()
                axes.imshow(correlation_matrix)
                axes.set_xticks(range(len(correlation_matrix.columns)))
                axes.set_yticks(range(len(correlation_matrix.columns)))
                axes.set_xticklabels(correlation_matrix.columns, rotation=45)
                axes.set_yticklabels(correlation_matrix.columns)

            if FigureCanvasQTAgg is not None:
                return FigureCanvasQTAgg(figure)

            return figure
        except Exception as exc:  # pragma: no cover - runtime visualization errors
            print(f"Error creating visualization: {exc}")
            return None

    def perform_clustering(self, columns, n_clusters: int = 3):
        """Run KMeans clustering on specified numeric columns and return (figure, clusters)."""
        if self.data is None:
            return None, None

        try:
            feature_data = self.data[columns].values
            scaled_feature_data = self.scaler.fit_transform(feature_data)

            pca = PCA(n_components=2)
            pca_transformed_data = pca.fit_transform(scaled_feature_data)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_feature_data)

            figure = Figure(figsize=(8, 6))
            axes = figure.add_subplot(111)
            scatter_plot = axes.scatter(pca_transformed_data[:, 0], pca_transformed_data[:, 1], c=cluster_labels, cmap="viridis")
            axes.set_xlabel("First Principal Component")
            axes.set_ylabel("Second Principal Component")
            axes.set_title("K-means Clustering Results")
            figure.colorbar(scatter_plot)

            if FigureCanvasQTAgg is not None:
                return FigureCanvasQTAgg(figure), cluster_labels

            return figure, cluster_labels
        except Exception as exc:  # pragma: no cover
            print(f"Error performing clustering: {exc}")
            return None, None
