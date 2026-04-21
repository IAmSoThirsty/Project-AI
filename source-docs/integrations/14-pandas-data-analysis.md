# Pandas Data Analysis Integration

## Overview
Project-AI integrates pandas for tabular data loading, analysis, and visualization (src/app/core/data_analysis.py).

## Supported Formats
- CSV: read_csv()
- Excel: read_excel()
- JSON: read_json()

## Implementation
`python
# src/app/core/data_analysis.py
import pandas as pd

class DataAnalyzer:
    def __init__(self):
        self.data = None
    
    def load_data(self, file_path: str) -> bool:
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            return True
        except Exception as e:
            print(f'Error loading data: {e}')
            return False
    
    def get_summary_stats(self) -> dict:
        if self.data is None:
            return {}
        
        return {
            'basic_stats': self.data.describe().to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'column_types': self.data.dtypes.to_dict(),
            'row_count': len(self.data),
            'column_count': len(self.data.columns)
        }
`

## Usage Patterns
`python
from app.core.data_analysis import DataAnalyzer

analyzer = DataAnalyzer()

# Load CSV
analyzer.load_data('data/sales_data.csv')

# Get statistics
stats = analyzer.get_summary_stats()
print(f\"Rows: {stats['row_count']}, Columns: {stats['column_count']}\")

# Data filtering
filtered = analyzer.data[analyzer.data['sales'] > 1000]

# Aggregation
monthly_totals = analyzer.data.groupby('month')['sales'].sum()

# Correlation analysis
correlations = analyzer.data.corr()
`

## Visualization with Matplotlib
`python
from matplotlib.figure import Figure

def create_visualization(data: pd.DataFrame, plot_type: str):
    fig = Figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    
    if plot_type == 'scatter':
        ax.scatter(data['x'], data['y'])
    elif plot_type == 'histogram':
        ax.hist(data['value'], bins=30)
    elif plot_type == 'boxplot':
        data.boxplot(ax=ax)
    
    return fig
`

## References
- Pandas: https://pandas.pydata.org
- Pandas User Guide: https://pandas.pydata.org/docs/user_guide/index.html


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
