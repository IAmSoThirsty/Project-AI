# Design Pattern Quick Reference Index

**Quick navigation to design patterns and usage examples across Project-AI codebase**

---

## 🔍 How to Use This Index

This index provides three ways to find pattern information:

1. **By Category** - Browse patterns by type (Validation, Persistence, etc.)
2. **By Usage Count** - Find most/least used patterns
3. **By File** - Find what patterns a specific file uses

---

## 📊 Patterns by Category

### Validation Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **Tuple Return Validation** | 9 | ✅ Active | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-11-tuple-return-validation]] |
| **Exception-Based Validation** | 4 | ✅ Security Only | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-12-exception-based-validation]] |

**Key Files:**
- [[utils/validators.py]] - Canonical implementations
- [[src/app/gui/dashboard_utils.py#L150-L171]] - GUI validation (3 validators)
- [[src/app/core/hydra_50_security.py#L140-L575]] - Security validation (4 validators)

---

### Persistence Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **JSON State Persistence** | 25+ | ✅ Universal | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-21-json-state-persistence]] |
| **Encrypted Persistence** | 14 | ✅ Security | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-22-encrypted-persistence]] |

**Key Files:**
- [[src/app/core/ai_systems.py#L402]] - Core AI systems (6 systems)
- [[src/app/core/location_tracker.py#L28]] - Encrypted GPS history
- [[src/app/core/user_manager.py]] - User profiles with encryption

**Critical Rules:**
- ⚠️ Always call `_save_state()` after mutations
- ⚠️ Always create data directory in `__init__`

---

### Async Execution Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **PyQt6 QRunnable** | 11 | ✅ GUI Standard | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-31-pyqt6-qrunnable-gui-thread-safety]] |
| **Retry with Backoff** | 10 | ⚠️ **UNDERUTILIZED** | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-32-retry-with-exponential-backoff]] |

**Key Files:**
- [[src/app/gui/dashboard_utils.py#L65]] - `AsyncWorker` canonical implementation
- [[src/app/gui/image_generation.py]] - Image generation (20-60s operations)
- [[e2e/utils/test_helpers.py]] - `retry_on_failure()` implementation

**Critical Rules:**
- ⚠️ NEVER use `threading.Thread` in PyQt6 GUI
- ⚠️ Always use signals for cross-thread communication

---

### Error Handling Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **Centralized Error Handler** | 11 | ✅ GUI Standard | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-41-centralized-error-handler]] |
| **Try-Except with Fallback** | 50+ | ✅ Universal | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-42-try-except-with-fallback]] |

**Key Files:**
- [[src/app/gui/dashboard_utils.py]] - `ErrorHandler` canonical implementation
- All GUI modules (100% adoption)

---

### Logging Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **Module-Level Logger** | 184 | ✅ Perfect | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-51-module-level-logger]] |
| **Structured Logging Context** | 150+ | ⚠️ Migration | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-52-structured-logging-context]] |

**Key Files:**
- Universal adoption (100% of codebase)

**Pattern:**
```python
import logging
logger = logging.getLogger(__name__)
```

---

### Configuration Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **Layered Configuration** | 5 | ⚠️ Partial | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-61-layered-configuration]] |

**Key Files:**
- [[src/app/core/god_tier_config.py]] - God Tier configuration
- [[src/app/core/config.py]] - Application config

**Priority:** Environment → File → Defaults

---

### Architecture Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **Abstract Interface (ABC)** | 50+ | ✅ Foundational | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-71-abstract-interface-abc]] |
| **Plugin Interface** | 6 | ✅ Extensibility | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-72-plugin-interface-pattern]] |
| **Three-Tier Architecture** | 1 | ✅ Core | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-73-three-tier-architecture]] |
| **Dependency Injection** | 30+ | ⚠️ Expanding | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-74-dependency-injection]] |
| **Factory Pattern** | 3 | ⚠️ **UNDERUTILIZED** | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-75-factory-pattern]] |
| **Builder Pattern** | 1 | ⚠️ **UNDERUTILIZED** | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-76-builder-pattern]] |
| **Registry Pattern** | 1 | ✅ Core | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-79-registry-pattern]] |
| **Protocol Pattern** | 4 | ✅ Emerging | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-78-protocol-pattern-typingprotocol]] |

**Key Files:**
- [[src/app/core/interfaces.py]] - Core interface abstractions
- [[src/app/core/cognition_kernel.py]] - Three-tier architecture root
- [[src/app/core/bootstrap_orchestrator.py]] - Dependency injection factory
- [[src/app/infrastructure/vpn/backends.py#L451]] - VPN backend factory

---

### Behavioral Patterns

| Pattern | Usage Count | Status | Quick Link |
|---------|-------------|--------|------------|
| **Strategy (Enum)** | 6 | ✅ Active | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-101-strategy-pattern-enum-based]] |
| **Observer (PyQt Signal)** | 11 | ✅ GUI Standard | [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-102-observer-pattern-pyqt-signal]] |

**Key Files:**
- [[src/app/core/multimodal_fusion.py#L45]] - `FusionStrategy` enum
- [[src/app/gui/leather_book_interface.py]] - PyQt signals (user_logged_in, etc.)

---

## 🔝 Patterns by Usage Count (Most → Least)

1. **Module-Level Logger** - 184 modules (100%) - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-51-module-level-logger]]
2. **Structured Logging** - 150+ modules (82%) - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-52-structured-logging-context]]
3. **Try-Except Fallback** - 50+ locations - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-42-try-except-with-fallback]]
4. **Abstract Interface** - 50+ interfaces - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-71-abstract-interface-abc]]
5. **Dependency Injection** - 30+ modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-74-dependency-injection]]
6. **JSON State Persistence** - 25+ modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-21-json-state-persistence]]
7. **Encrypted Persistence** - 14 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-22-encrypted-persistence]]
8. **Centralized Error Handler** - 11 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-41-centralized-error-handler]]
9. **QRunnable Async** - 11 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-31-pyqt6-qrunnable-gui-thread-safety]]
10. **Observer (PyQt Signal)** - 11 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-102-observer-pattern-pyqt-signal]]
11. **Retry with Backoff** - 10 modules ⚠️ - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-32-retry-with-exponential-backoff]]
12. **Tuple Return Validation** - 9 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-11-tuple-return-validation]]
13. **Strategy (Enum)** - 6 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-101-strategy-pattern-enum-based]]
14. **Plugin Interface** - 6 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-72-plugin-interface-pattern]]
15. **Layered Config** - 5 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-61-layered-configuration]]
16. **Exception Validation** - 4 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-12-exception-based-validation]]
17. **Protocol Pattern** - 4 modules - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-78-protocol-pattern-typingprotocol]]
18. **Factory Pattern** - 3 modules ⚠️ - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-75-factory-pattern]]
19. **Three-Tier Architecture** - 1 (core) - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-73-three-tier-architecture]]
20. **Registry Pattern** - 1 (core) - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-79-registry-pattern]]
21. **Builder Pattern** - 1 ⚠️ - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-76-builder-pattern]]
22. **System Init Factory** - 1 (bootstrap) - [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-712-system-initialization-factory]]

---

## 📂 Patterns by File

### Core Systems

**src/app/core/ai_systems.py** (Multiple patterns):
- JSON State Persistence (6 systems) - [[#L402]]
- Module-Level Logger - [[#L1]]
- Tuple Return Validation (custom validators)

**src/app/core/user_manager.py**:
- JSON State Persistence - [[#save_users]]
- Encrypted Persistence - [[#L69]]
- Tuple Return Validation - [[#L234]]
- Module-Level Logger

**src/app/core/hydra_50_security.py**:
- Tuple Return Validation (4 validators) - [[#L140-L575]]
- Encrypted Persistence - [[#L415]]
- Module-Level Logger

**src/app/core/interfaces.py**:
- Abstract Interface (3 interfaces) - [[#L23]], [[#L94]], [[#L218]]
- Module-Level Logger

**src/app/core/cognition_kernel.py**:
- Three-Tier Architecture - [[#CognitionKernel]]
- Dependency Injection
- Abstract Interface
- Module-Level Logger

---

### GUI Modules

**src/app/gui/dashboard_utils.py**:
- QRunnable Async - [[#L65]] (AsyncWorker)
- Centralized Error Handler - [[#ErrorHandler]]
- Tuple Return Validation (3 validators) - [[#L150-L171]]
- Module-Level Logger

**src/app/gui/image_generation.py**:
- QRunnable Async - [[#ImageGenerationWorker]]
- Observer (PyQt Signal) - [[#image_generated]]
- Centralized Error Handler
- Module-Level Logger

**src/app/gui/leather_book_interface.py**:
- Observer (PyQt Signal) - [[#user_logged_in]]
- QRunnable Async
- Centralized Error Handler
- Module-Level Logger

---

### Infrastructure

**src/app/infrastructure/vpn/backends.py**:
- Factory Pattern - [[#L451]] (VPNBackendFactory)
- Abstract Interface - [[#L24]] (VPNBackend)
- Module-Level Logger

**src/app/infrastructure/vpn/vpn_manager.py**:
- Encrypted Persistence - [[#L38]]
- Retry with Backoff
- Module-Level Logger

---

### Security

**src/app/security/advanced/hardware_root_of_trust.py**:
- Abstract Interface - [[#L39]] (HardwareInterface)
- Module-Level Logger

**src/app/security/advanced/privacy_ledger.py**:
- Encrypted Persistence - [[#L368]]
- Module-Level Logger

---

### Utilities & Testing

**e2e/utils/test_helpers.py**:
- Retry with Backoff - [[#retry_on_failure]] (canonical)

**utils/validators.py**:
- Tuple Return Validation - [[#validate_actor]], [[#validate_action]]
- Exception-Based Validation - [[#validate_target]]

---

## ⚠️ Underutilized Patterns (Action Required)

### 🔴 CRITICAL: Retry with Exponential Backoff

**Current:** 10 implementations  
**Should Be:** 40+ implementations  
**Gap:** 30 missing retry mechanisms

**Missing Locations:**
- All OpenAI API calls (5 locations)
- All GitHub API calls (3 locations)
- All external data fetching (10+ locations)
- All cloud/remote operations (12+ locations)

**Action:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#critical-retry-with-exponential-backoff]]

---

### 🟡 HIGH: Factory Pattern

**Current:** 3 factories  
**Should Be:** 10+ factories  
**Gap:** 7 missing factories

**Missing Factories:**
- ModelProviderFactory (OpenAI, Anthropic, local, Azure)
- StorageBackendFactory (JSON, SQLite, PostgreSQL)
- SecurityProviderFactory (MFA, hardware tokens, biometrics)
- AgentFactory (25+ specialized agents)

**Action:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#high-priority-factory-pattern]]

---

### 🟢 MEDIUM: Builder Pattern

**Current:** 1 builder  
**Should Be:** 5+ builders  
**Gap:** 4 missing builders

**Missing Builders:**
- RAGQueryBuilder (8+ params)
- LearningRequestBuilder (6+ params)
- ConfigBuilder (12+ params)
- ActionBuilder (7+ params)

**Action:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#medium-priority-builder-pattern]]

---

## 📚 Full Documentation Links

- **Comprehensive Catalog:** [[AGENT-082-PATTERN-USAGE-CATALOG.md]]
- **Original Pattern Map:** [[relationships/utilities/02-common-patterns-map.md]]
- **Mission Summary:** [[AGENT-082-MISSION-SUMMARY.md]]
- **Architecture Evaluation:** [[ARCHITECTURE_DESIGN_PATTERNS_EVALUATION.md]]
- **Plugin Patterns:** [[source-docs/plugins/07-plugin-extensibility-patterns.md]]
- **Architecture Quick Ref:** [[.github/instructions/ARCHITECTURE_QUICK_REF.md]]

---

## 🎯 Quick Search Tips

**Find pattern usage:**
```bash
# Search for pattern by keyword
grep -r "AsyncWorker" AGENT-082-PATTERN-USAGE-CATALOG.md

# Search for file in catalog
grep -r "dashboard_utils.py" AGENT-082-PATTERN-USAGE-CATALOG.md
```

**Find patterns in specific file:**
1. Open this index
2. Search for filename (Ctrl+F)
3. Follow wiki links to usage examples

**Find underutilized patterns:**
- [[#-underutilized-patterns-action-required]]
- [[AGENT-082-PATTERN-USAGE-CATALOG.md#underutilized-patterns-report]]

---

**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-082  
**Status:** ✅ Complete

**Quick Links:**
- [Pattern Usage Matrix](AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-usage-matrix)
- [Underutilized Patterns Report](AGENT-082-PATTERN-USAGE-CATALOG.md#underutilized-patterns-report)
- [Pattern Evolution Roadmap](AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-evolution-recommendations)
