# Data Directory

## Overview

Central data storage for application data, datasets, and persistent storage. Includes training data, configurations, and runtime data.

## Installation

```bash

# Initialize data directory

mkdir -p data/datasets data/cache data/logs
```

## Usage

```python
from pathlib import Path

data_dir = Path("data")
datasets_dir = data_dir / "datasets"
```

## API

Data directory structure:

- `datasets/`: Training and test datasets
- `cache/`: Temporary cache files
- `logs/`: Application logs

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](../../LICENSE) for license information.
