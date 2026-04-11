<!--                                        [2026-03-05 00:00]  -->
<!--                                       Productivity: Active  -->

# `engines/` — Simulation & Scenario Engines

> **Specialized engines for adversarial simulation, war gaming, defense modeling, and scenario evaluation.**

## 🔐 NEW: Enhanced Cryptographic War Engine (Post-Quantum Cryptography)

**File**: `crypto_war_enhanced.py` | **Tests**: `test_crypto_war_enhanced.py` (40 tests)

Complete post-quantum cryptography implementation protecting against quantum computing threats:

**Features**:
- ✅ **NIST PQC Finalists**: Kyber (KEM), Dilithium (signatures), SPHINCS+ (signatures)
- ✅ **Lattice-Based Schemes**: LWE, NTRU
- ✅ **Algorithm Agility**: Dynamic threat-based crypto selection
- ✅ **Migration Engine**: Automated classical → PQC migration with rollback
- ✅ **Hybrid Mode**: Classical + PQC for transitional security

**Quick Start**:
```python
from engines.crypto_war_enhanced import create_pqc_engine, CryptoAlgorithm

engine = create_pqc_engine(threat_level="high")
keypair = engine.generate_pqc_keypair(CryptoAlgorithm.KYBER_768, "key1")
signature = engine.pqc_sign(b"message", "key1", CryptoAlgorithm.DILITHIUM_3)
```

**Documentation**:
- 📖 [POST_QUANTUM_CRYPTO_GUIDE.md](POST_QUANTUM_CRYPTO_GUIDE.md) - Complete PQC guide
- 📋 [PQC_EXAMPLES.md](PQC_EXAMPLES.md) - 12 practical examples
- 🔄 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Classical to PQC migration

**Demo**: `python engines/crypto_war_enhanced.py`

---

## Engines

### Core

| Engine | Files | Purpose |
|---|---:|---|
| **`atlas/`** | 51 | Atlas intelligence engine — global threat mapping and correlation |
| **`hydra_50/`** | 13 | Hydra-50 multi-headed defense engine — parallel threat evaluation |
| **`sovereign_war_room/`** | 15 | Sovereign war room — command center for coordinated defense |
| **`django_state/`** | 26 | Django-based state management — persistent state for web-facing engines |

### Threat Simulation

| Engine | Files | Purpose |
|---|---:|---|
| **`ai_takeover/`** | 12 | AI takeover scenarios — tests sovereign defenses against rogue AI |
| **`alien_invaders/`** | 15 | Alien invasion scenarios — extreme-case stress testing |
| **`emp_defense/`** | 18 | EMP defense simulation — electromagnetic pulse survivability |
| **`zombie_defense/`** | 2 | Zombie defense scenarios — cascading failure simulation |
| **`cognitive_warfare/`** | 2 | Cognitive warfare — psychological manipulation defense |

### Governance & Strategy

| Engine | Files | Purpose |
|---|---:|---|
| **`constitutional_scenario/`** | 1 | Constitutional scenario evaluation |
| **`global_scenario/`** | 3 | Global scenario engine — world-state simulation |
| **`novel_security_scenarios/`** | 2 | Novel security scenario generation |
| **`simulation_contract/`** | 1 | Simulation contract definitions |
| **`consigliere/`** | 2 | Strategic advisor engine |

## Usage

Engines are invoked through the PACE engine or directly:

```python
from engines.atlas import AtlasEngine
from engines.hydra_50 import Hydra50Engine

atlas = AtlasEngine(config)
threat_map = atlas.evaluate(scenario)
```
