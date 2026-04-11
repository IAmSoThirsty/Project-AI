# Application Core

## Overview

Core application functionality including initialization, configuration management, and central orchestration.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.app.core import ApplicationCore

app = ApplicationCore()
app.initialize()
app.run()
```

## API

**Classes:**

- `ApplicationCore`: Main application orchestrator
- `ConfigManager`: Configuration management
- `ServiceRegistry`: Service discovery and registration

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](../../LICENSE) for license information.
