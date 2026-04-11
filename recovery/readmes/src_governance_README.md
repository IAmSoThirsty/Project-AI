# Governance Module

## Overview

Core governance implementation for sovereign substrate. Handles voting, proposals, and decentralized decision-making.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.governance import GovernanceEngine

engine = GovernanceEngine()
proposal = engine.create_proposal("Increase block size")
engine.vote(proposal.id, vote="yes")
```

## API

**Classes:**

- `GovernanceEngine`: Main governance orchestrator
- `Proposal`: Governance proposal object
- `VotingMechanism`: Vote counting and validation

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](../../LICENSE) for license information.
