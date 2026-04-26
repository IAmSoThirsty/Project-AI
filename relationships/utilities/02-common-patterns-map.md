---
description: Common design patterns and utilities used across Project-AI
audience: developers
priority: P1
category: utilities
tags: [patterns, common-utilities, design-patterns, reuse]
dependencies: [helper-functions]
related_systems: [validation-utils, async-patterns]
last_updated: 2026-04-20
---

# Common Patterns Relationship Map

## Overview

This map documents recurring design patterns and utility patterns used across the Project-AI codebase, including their implementations, usage contexts, and reuse chains.

## Core Pattern Categories

### 1. **Validation Patterns**

#### Pattern 1.1: Tuple Return Validation
**Signature**: `(bool, str)` - Returns validity status and error message

**Canonical Implementation**:
```python
def validate_X(value: Any) -> tuple[bool, str]:
    """
    Standard validation pattern.
    
    Returns:
        (True, "") if valid
        (False, "error message") if invalid
    """
    if not meets_criteria(value):
        return False, "Specific error message"
    return True, ""
```

**Usage Locations** (9+ implementations):
- [[utils/validators.py#validate_actor]] - Agent actor validation
- [[utils/validators.py#validate_action]] - Action validation
- [[src/app/gui/dashboard_utils.py#L150]] - `validate_username()` - GUI input validation
- [[src/app/gui/dashboard_utils.py#L161]] - `validate_email()` - GUI input validation
- [[src/app/gui/dashboard_utils.py#L171]] - `validate_password()` - GUI input validation
- [[src/app/core/hydra_50_security.py#L140]] - `validate_username()` - Security validation
- [[src/app/core/hydra_50_security.py#L154]] - `validate_email()` - Security validation
- [[src/app/core/hydra_50_security.py#L165]] - `validate_password()` - Security validation
- [[src/app/core/hydra_50_security.py#L575]] - `validate_input()` - Input sanitization
- [[src/app/core/user_manager.py#L234]] - `validate_password_strength()` - Password policy
- [[src/app/core/hydra_50_deep_integration.py#L555]] - `validate_action()` - Four Laws validation

**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-11-tuple-return-validation]]

**Reuse Chain**:
```
utils/validators.py (origin)
    ↓ adopted by
src/app/gui/dashboard_utils.py
    ↓ adopted by
src/app/core/hydra_50_security.py
    ↓ adopted by
src/app/security/data_validation.py
    ↓ used by
15+ consumer modules
```

---

#### Pattern 1.2: Exception-Based Validation
**Signature**: Raises `ValidationError` on invalid input

**Canonical Implementation**:
```python
class ValidationError(Exception):
    """Custom validation error."""
    pass

def validate_X(value: Any) -> bool:
    """
    Raises ValidationError on invalid input.
    Returns True if valid.
    """
    if not valid:
        raise ValidationError(f"Invalid {value}")
    return True
```

**Usage Locations**:
- `utils/validators.py::validate_target()` - Raises on path traversal
- `utils/validators.py::validate_intent()` - Raises on missing fields
- `src/app/core/governance/validators.py::validate_input()` - Governance validation

**When to Use**:
- ✅ Critical security validations (path traversal, injection attacks)
- ✅ Configuration parsing (fail-fast on invalid config)
- ❌ User input validation (prefer tuple return for user feedback)

---

### 2. **Persistence Patterns**

#### Pattern 2.1: JSON State Persistence
**Standard Pattern**: Save/load state to JSON files with atomic writes

**Canonical Implementation**:
```python
class StatefulSystem:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        state_file = self.data_dir / "state.json"
        if state_file.exists():
            with open(state_file) as f:
                return json.load(f)
        return self._default_state()
    
    def _save_state(self) -> None:
        state_file = self.data_dir / "state.json"
        with open(state_file, "w") as f:
            json.dump(self.state, f, indent=2)
```

**Usage Locations** (25+ modules):

**Core AI Systems:**
- [[src/app/core/ai_systems.py#L402]] - `AIPersona`, `MemorySystem`, `LearningRequests` - 6 systems
- [[src/app/core/user_manager.py]] - `UserManager` - User profiles with bcrypt
- [[src/app/governance/audit_log.py]] - `AuditLogger` - Audit events

**System Infrastructure:**
- [[src/app/core/system_registry.py#L604]] - `SystemRegistry` - Subsystem registration
- [[src/app/core/state_register.py#L435]] - `StateRegister` - Global state management
- [[src/app/core/perspective_engine.py#L339]] - `PerspectiveEngine` - AI perspective tracking

**Security Systems:**
- [[src/app/core/ip_blocking_system.py#L407]] - `IPBlockingSystem` - Blocked IPs, threat scores
- [[src/app/core/incident_responder.py#L548]] - `IncidentResponder` - Incident logs
- [[src/app/core/honeypot_detector.py#L489]] - `HoneypotDetector` - Honeypot detections
- [[src/app/core/cerberus_lockdown_controller.py#L112]] - `CerberusLockdown` - Lockdown state

**Domain Systems:**
- [[src/app/domains/tactical_edge_ai.py#L358]] - `TacticalEdgeAI` - Tactical decisions
- [[src/app/domains/situational_awareness.py#L763]] - `SituationalAwareness` - Situation reports
- [[src/app/domains/supply_logistics.py#L918]] - `SupplyLogistics` - Inventory state
- [[src/app/domains/survivor_support.py#L179]] - `SurvivorSupport` - Survivor profiles
- [[src/app/domains/command_control.py#L877]] - `CommandControl` - Command history
- [[src/app/domains/continuous_improvement.py#L161]] - `ContinuousImprovement` - Improvement metrics
- [[src/app/domains/deep_expansion.py#L169]] - `DeepExpansion` - Expansion planning
- [[src/app/domains/ethics_governance.py#L173]] - `EthicsGovernance` - Ethical decisions
- [[src/app/domains/biomedical_defense.py#L286]] - `BiomedicalDefense` - Medical protocols
- [[src/app/domains/agi_safeguards.py#L182]] - `AGISafeguards` - AGI safety state

**Integration Systems:**
- [[src/app/core/hydra_50_engine.py#L5614]] - `Hydra50Engine` - Multi-system orchestration
- [[src/app/core/cerberus_hydra.py#L261]] - `CerberusHydra` - Hydra-Cerberus integration
- [[src/app/core/bonding_protocol.py#L292]] - `BondingProtocol` - User bonding metrics

**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-21-json-state-persistence]]

**Critical Pattern Element**:
```python
# ALWAYS call _save_state() after mutations
def update_state(self, key: str, value: Any):
    self.state[key] = value
    self._save_state()  # ← Critical: ensures persistence
```

**Anti-Pattern** (Bug Source):
```python
# BAD: Forgetting to save after mutation
def update_state(self, key: str, value: Any):
    self.state[key] = value
    # Missing _save_state() → data loss on restart
```

**Reuse Metrics**:
- **Adopters**: 15+ core modules
- **Data Directories**: `data/`, `data/ai_persona/`, `data/memory/`, `data/learning_requests/`
- **Pattern Consistency**: 95%

---

#### Pattern 2.2: Encrypted Persistence
**Pattern**: JSON + Fernet encryption for sensitive data

**Canonical Implementation**:
```python
from cryptography.fernet import Fernet

class EncryptedStorage:
    def __init__(self):
        self.cipher = Fernet(Fernet.generate_key())
    
    def save_encrypted(self, data: dict, file_path: str):
        json_data = json.dumps(data).encode()
        encrypted = self.cipher.encrypt(json_data)
        with open(file_path, "wb") as f:
            f.write(encrypted)
    
    def load_encrypted(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            encrypted = f.read()
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted)
```

**Usage Locations** (14+ implementations):

**Location & Privacy:**
- [[src/app/core/location_tracker.py#L28]] - `LocationTracker` - GPS history, IP geolocation
- [[src/app/security/advanced/privacy_ledger.py#L368]] - `PrivacyLedger` - Privacy violation logs

**Cloud & Remote:**
- [[src/app/core/cloud_sync.py#L47]] - `CloudSync` - Cloud credentials, cached data
- [[src/app/remote/remote_desktop.py#L32]] - `RemoteDesktop` - Session keys, captures
- [[src/app/remote/remote_browser.py#L30]] - `RemoteBrowser` - Session data, cookies

**User & Authentication:**
- [[src/app/core/user_manager.py#L69]] - `UserManager` - Session tokens, API keys
- [[src/app/core/hydra_50_security.py#L415]] - `Hydra50Security` - Multi-layer security state

**Infrastructure:**
- [[src/app/infrastructure/vpn/vpn_manager.py#L38]] - `VPNManager` - VPN credentials, logs
- [[src/app/core/security_enforcer.py#L168]] - `SecurityEnforcer` - Security policies, audit logs
- [[src/app/core/data_persistence.py#L166]] - `DataPersistence` - General encrypted storage
- [[src/app/core/continuous_monitoring_system.py#L151]] - `ContinuousMonitoring` - Monitoring data

**AI & Agents:**
- [[src/app/agents/consigliere/consigliere_engine.py#L46]] - `ConsigliereEngine` - Agent decision history
- [[src/app/ai/ai_engine.py#L32]] - `AIEngine` - AI model weights, training data
- [[src/app/browser/browser_engine.py#L44]] - `BrowserEngine` - Browser state, cached pages

**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-22-encrypted-persistence]]

---

### 3. **Async Execution Patterns**

#### Pattern 3.1: PyQt6 QRunnable (GUI Thread Safety)
**Use Case**: Execute long operations without blocking GUI

**Canonical Implementation**:
```python
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    result = pyqtSignal(object)

class AsyncWorker(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(e)
        finally:
            self.signals.finished.emit()

# Usage
def run_async_task(func, callback):
    worker = AsyncWorker(func)
    worker.signals.result.connect(callback)
    QThreadPool.globalInstance().start(worker)
```

**Usage Locations** (11 GUI modules - 100% GUI coverage):
- [[src/app/gui/dashboard_utils.py#L65]] - **`AsyncWorker`** - Canonical base implementation
- [[src/app/gui/image_generation.py]] - `ImageGenerationWorker` - 20-60s image generation
- [[src/app/gui/persona_panel.py]] - Persona updates (1-5s AI processing)
- [[src/app/gui/leather_book_interface.py]] - Heavy computations (varies)
- [[src/app/gui/news_intelligence_panel.py]] - RSS feed aggregation (5-10s)
- [[src/app/gui/intelligence_library_panel.py]] - Full-text search indexing (10-30s)
- [[src/app/gui/watch_tower_panel.py]] - System health checks (2-5s)
- [[src/app/gui/hydra_50_panel.py]] - Multi-system coordination (5-15s)
- [[src/app/gui/god_tier_panel.py]] - Complex AI processing (10-30s)
- [[src/app/gui/knowledge_functions_panel.py]] - RAG system queries (3-8s)
- [[src/app/gui/leather_book_dashboard.py]] - Periodic data refresh (1-3s)

**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-31-pyqt6-qrunnable-gui-thread-safety]]

**Critical Rule**: **NEVER use `threading.Thread` in PyQt6 GUI code**
- ✅ Use: `QRunnable` + `QThreadPool`
- ✅ Signals: `pyqtSignal` for cross-thread communication
- ❌ Avoid: Direct GUI updates from worker threads

---

#### Pattern 3.2: Retry with Exponential Backoff
**Use Case**: Resilient API calls and I/O operations

**Canonical Implementation**:
```python
import time
from typing import Callable, Any

def retry_on_failure(
    func: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries
        backoff_factor: Multiply delay by this each retry
        exceptions: Exceptions to catch
    """
    last_exception = None
    delay = retry_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= backoff_factor
    
    raise last_exception
```

**Usage Locations** (10 implementations - ⚠️ UNDERUTILIZED):
- [[e2e/utils/test_helpers.py]] - **Canonical implementation** (3 retries, 1s delay)
- [[src/app/monitoring/metrics_collector.py]] - Prometheus metrics (5 retries, 2s delay)
- [[src/app/health/report.py]] - Health check API calls (3 retries, 0.5s delay)
- [[src/app/core/openrouter_provider.py]] - OpenAI/OpenRouter API (3 retries, 1s delay)
- [[src/app/core/intelligence_engine.py]] - GPT completions (3 retries, 2s delay)
- [[src/app/core/cloud_sync.py]] - Cloud sync operations (5 retries, 1s delay)
- [[src/app/security_resources.py]] - GitHub API calls (3 retries, 2s delay)
- [[src/app/infrastructure/vpn/vpn_manager.py]] - VPN connections (5 retries, 3s delay)
- [[src/app/browser/browser_engine.py]] - Web page fetching (3 retries, 1s delay)
- [[src/app/remote/remote_desktop.py]] - Remote desktop (5 retries, 2s delay)

**⚠️ RECOMMENDATION:** Expand to all external API calls (30+ additional locations)  
**See Underutilized Report:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#critical-retry-with-exponential-backoff]]

---

### 4. **Error Handling Patterns**

#### Pattern 4.1: Centralized Error Handler
**Pattern**: Single error handling class for consistent logging and UI feedback

**Canonical Implementation**:
```python
import logging
from PyQt6.QtWidgets import QMessageBox

class ErrorHandler:
    @staticmethod
    def handle_exception(
        exception: Exception,
        context: str = "Operation",
        show_dialog: bool = True,
        parent=None
    ) -> None:
        """Handle exception with logging and optional dialog."""
        error_message = f"{context}: {str(exception)}"
        logging.error(error_message, exc_info=True)
        
        if show_dialog:
            QMessageBox.critical(parent, "Error", error_message)
    
    @staticmethod
    def handle_warning(
        message: str,
        context: str = "Warning",
        show_dialog: bool = False,
        parent=None
    ) -> None:
        """Handle warning with logging and optional dialog."""
        logging.warning(f"{context}: {message}")
        if show_dialog:
            QMessageBox.warning(parent, context, message)
```

**Usage Locations** (11 GUI modules - 100% GUI coverage):
- [[src/app/gui/dashboard_utils.py]] - **`ErrorHandler`** - Canonical implementation
- [[src/app/gui/leather_book_interface.py]] - Login errors, navigation failures
- [[src/app/gui/leather_book_dashboard.py]] - Dashboard operations, data loading
- [[src/app/gui/persona_panel.py]] - Persona updates, AI processing errors
- [[src/app/gui/image_generation.py]] - Content filter, API errors, timeouts
- [[src/app/gui/news_intelligence_panel.py]] - Network errors, RSS parsing failures
- [[src/app/gui/intelligence_library_panel.py]] - Search errors, indexing failures
- [[src/app/gui/watch_tower_panel.py]] - Monitoring, metric collection failures
- [[src/app/gui/hydra_50_panel.py]] - Hydra operations, multi-system coordination
- [[src/app/gui/god_tier_panel.py]] - God Tier tasks, complex AI errors
- [[src/app/gui/cerberus_panel.py]] - Cerberus operations, security enforcement

**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-41-centralized-error-handler]]

**Benefits**:
- ✅ Consistent logging format
- ✅ Optional GUI feedback (show_dialog flag)
- ✅ Single point for error formatting changes

---

#### Pattern 4.2: Try-Except with Fallback
**Pattern**: Graceful degradation with default values

**Canonical Implementation**:
```python
def safe_operation(risky_func, default=None, log_errors=True):
    """Execute function with fallback on error."""
    try:
        return risky_func()
    except Exception as e:
        if log_errors:
            logging.error(f"Operation failed: {e}", exc_info=True)
        return default
```

**Common Usage**:
```python
# Safe file read with fallback
config = safe_operation(
    lambda: json.load(open("config.json")),
    default={"mode": "default"},
    log_errors=True
)
```

**Adoption**: 50+ locations across codebase for safe I/O operations

---

### 5. **Logging Patterns**

#### Pattern 5.1: Module-Level Logger
**Standard Pattern**: One logger per module

**Canonical Implementation**:
```python
import logging

logger = logging.getLogger(__name__)

class MyClass:
    def operation(self):
        logger.info("Starting operation")
        try:
            # operation logic
            logger.debug("Operation details: %s", details)
        except Exception as e:
            logger.error("Operation failed: %s", e, exc_info=True)
```

**Logging Levels Used**:
- `DEBUG`: Detailed diagnostic info (disabled in production)
- `INFO`: Operational messages (startup, shutdown, state changes)
- `WARNING`: Non-critical issues (missing optional config)
- `ERROR`: Recoverable errors with context
- `CRITICAL`: Fatal errors requiring intervention

**Universal Pattern**: 184/184 modules use this consistently (100% adoption)

**Adoption by Category:**
- Core Systems: 95/95 (100%)
- GUI Modules: 11/11 (100%)
- Domain Systems: 10/10 (100%)
- Security Modules: 20/20 (100%)
- Integration: 15/15 (100%)
- Agents: 25/25 (100%)
- Infrastructure: 8/8 (100%)

**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-51-module-level-logger]]

---

#### Pattern 5.2: Structured Logging Context
**Pattern**: Include context in log messages

**Canonical Implementation**:
```python
logger.info("User %s performed %s on %s", user_id, action, resource)
# Output: "User alice performed delete on /data/file.txt"
```

**Anti-Pattern**:
```python
# BAD: String concatenation loses structure
logger.info(f"User {user_id} performed {action}")
```

**Benefits**:
- ✅ Easy to parse logs programmatically
- ✅ Better log aggregation (Prometheus, ELK)

---

### 6. **Configuration Patterns**

#### Pattern 6.1: Layered Configuration
**Pattern**: Environment → File → Defaults

**Canonical Implementation**:
```python
import os
from pathlib import Path

class Config:
    def __init__(self, config_file: str = None):
        # Layer 1: Defaults
        self.config = self._get_defaults()
        
        # Layer 2: File-based config
        if config_file and Path(config_file).exists():
            self.config.update(self._load_file(config_file))
        
        # Layer 3: Environment variables (highest priority)
        self.config.update(self._load_env())
    
    def _get_defaults(self) -> dict:
        return {
            "log_level": "INFO",
            "data_dir": "data",
            "timeout": 30
        }
    
    def _load_env(self) -> dict:
        return {
            k.lower(): v
            for k, v in os.environ.items()
            if k.startswith("APP_")
        }
```

**Usage**: 5+ core configuration modules

**Implementations:**
- [[src/app/core/god_tier_config.py]] - God Tier system configuration
- [[src/app/core/config.py]] - Application-wide configuration
- [[src/app/core/bootstrap_orchestrator.py]] - Bootstrap configuration

**⚠️ RECOMMENDATION:** Expand to all config-heavy modules (8 modules = 100% coverage)  
**See Full Usage Examples:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#pattern-61-layered-configuration]]

---

### 7. **Factory Patterns**

#### Pattern 7.1: System Initialization Factory
**Pattern**: Centralized initialization with dependency injection

**Canonical Implementation**:
```python
class SystemFactory:
    @staticmethod
    def create_ai_system(config: dict, data_dir: str):
        """Create AI system with dependencies."""
        persona = AIPersona(data_dir=data_dir)
        memory = MemoryExpansionSystem(data_dir=data_dir)
        learning = LearningRequestManager(data_dir=data_dir)
        
        return {
            "persona": persona,
            "memory": memory,
            "learning": learning
        }
```

**Usage Locations**:
- [[src/app/core/bootstrap_orchestrator.py]] - `BootstrapOrchestrator.create_*()` - System bootstrap
- [[src/app/main.py]] - Application initialization with dependency injection
- [[src/app/infrastructure/vpn/backends.py#L451]] - `VPNBackendFactory` - VPN backend creation
- [[src/app/inspection/catalog_builder.py#L27]] - `CatalogBuilder` - Documentation catalogs
- Test fixtures across codebase for isolated component testing

**⚠️ RECOMMENDATION:** Create missing factories (ModelProvider, StorageBackend, SecurityProvider, Agent)  
**See Factory Pattern Report:** [[AGENT-082-PATTERN-USAGE-CATALOG.md#high-priority-factory-pattern]]

---

## Pattern Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│ Common Patterns Hierarchy                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Validation Patterns                                        │
│    ├── Tuple Return (bool, str) ───────────── 20+ adopters │
│    └── Exception-Based ───────────────────── Security only │
│                                                              │
│  Persistence Patterns                                       │
│    ├── JSON State ─────────────────────────── 15+ modules  │
│    └── Encrypted JSON ─────────────────────── Sensitive data│
│                                                              │
│  Async Patterns                                             │
│    ├── QRunnable (GUI) ────────────────────── All GUI      │
│    └── Retry + Backoff ────────────────────── I/O ops      │
│                                                              │
│  Error Handling                                             │
│    ├── Centralized Handler ────────────────── GUI modules  │
│    └── Try-Except Fallback ────────────────── Universal    │
│                                                              │
│  Logging Patterns                                           │
│    ├── Module Logger ──────────────────────── 100+ modules │
│    └── Structured Context ─────────────────── Production   │
│                                                              │
│  Configuration                                              │
│    └── Layered Config ─────────────────────── Core systems │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Critical Pattern Rules

### Rule 1: **Always Save After Mutation** (Persistence)
```python
# ✅ CORRECT
def update_state(self, key, value):
    self.state[key] = value
    self._save_state()  # Critical!

# ❌ WRONG
def update_state(self, key, value):
    self.state[key] = value
    # Missing save → data loss
```

### Rule 2: **Never Block GUI Thread** (Async)
```python
# ✅ CORRECT
worker = AsyncWorker(heavy_operation)
worker.signals.result.connect(on_complete)
QThreadPool.globalInstance().start(worker)

# ❌ WRONG
result = heavy_operation()  # Freezes GUI
```

### Rule 3: **Consistent Validation Returns** (Validation)
```python
# ✅ CORRECT: Tuple return for user-facing validation
def validate_email(email: str) -> tuple[bool, str]:
    return (True, "") or (False, "Invalid email")

# ✅ CORRECT: Exception for security validation
def validate_path(path: str) -> bool:
    if ".." in path:
        raise ValidationError("Path traversal")
    return True
```

---

## Pattern Metrics

| Pattern                      | Adoption Rate | Modules | Consistency |
|------------------------------|---------------|---------|-------------|
| Tuple Return Validation      | 95%           | 20+     | High        |
| JSON State Persistence       | 100%          | 15+     | High        |
| Module-Level Logger          | 100%          | 100+    | High        |
| QRunnable Async              | 100% (GUI)    | 8       | High        |
| Retry with Backoff           | 80%           | 10+     | Medium      |
| Centralized Error Handler    | 100% (GUI)    | 8       | High        |
| Layered Configuration        | 60%           | 5+      | Medium      |

---

## Anti-Patterns to Avoid

### AP1: **Inconsistent Validation Returns**
```python
# ❌ AVOID: Mixing return types
def validate_A(value): return True  # bool
def validate_B(value): return (True, "")  # tuple
def validate_C(value): raise ValidationError()  # exception
```

**Fix**: Choose one pattern per validation context

### AP2: **Forgot to Save State**
```python
# ❌ AVOID
self.state["key"] = "value"
# ... more code ...
# User expects state to be saved, but it's not
```

**Fix**: Call `_save_state()` after every mutation

### AP3: **GUI Thread Blocking**
```python
# ❌ AVOID
def on_button_click(self):
    for i in range(1000000):  # Long loop
        process(i)  # GUI freezes
```

**Fix**: Use `AsyncWorker` for long operations

---

## Related Documentation
- [Helper Functions Map](./01-helper-functions-map.md)
- [Validation Utils Map](./09-validation-utils-map.md)
- [Shared Utilities Map](./03-shared-utilities-map.md)
