# Override Hierarchy System Relationships

**System:** Override Hierarchy  
**Core Files:**
- `src/app/core/config.py` [[src/app/core/config.py]] - 4-tier precedence system
- `config/settings_manager.py` - Runtime setting overrides
- Environment variables - Highest priority overrides
- `src/app/core/command_override.py` [[src/app/core/command_override.py]] - Safety protocol overrides

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\09_override_hierarchy_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Override Hierarchy Architecture

Project-AI implements **multiple override hierarchies** across different systems:

1. **CLI Config Hierarchy** - 4 tiers (Env > Project > User > Defaults)
2. **Settings Manager Hierarchy** - Runtime overrides (import, set_setting)
3. **Command Override Hierarchy** - Safety protocol emergency overrides

---

## Hierarchy 1: CLI Configuration Override Precedence

### File: `src/app/core/config.py` [[src/app/core/config.py]]

### 4-Tier Precedence (Highest to Lowest)

```
┌──────────────────────────────────────────┐
│  TIER 1: Environment Variables           │  ← HIGHEST PRIORITY
│  Format: PROJECTAI_SECTION_KEY=value     │
│  Example: PROJECTAI_AI_MODEL=gpt-4       │
│  Scope: Any config key can be overridden │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 2: Project Config                  │  ← Project-specific
│  File: ./.projectai.toml                 │
│  Location: Current working directory     │
│  Scope: Project team settings            │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 3: User Config                     │  ← User preferences
│  File: ~/.projectai.toml                 │
│  Location: User's home directory         │
│  Scope: Personal settings                │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 4: Default Values                  │  ← LOWEST PRIORITY
│  Location: Config.DEFAULTS dictionary    │
│  Scope: Hardcoded fallbacks              │
└──────────────────────────────────────────┘
```

### Implementation

```python
def _load_config(self, config_path: Path | None = None) -> None:
    """Load configuration with 4-tier override hierarchy."""
    
    # TIER 4: Start with defaults (lowest priority)
    self.config = self.DEFAULTS.copy()
    
    # TIER 3: Merge user config (overrides defaults)
    user_config_path = Path.home() / ".projectai.toml"
    if user_config_path.exists():
        self._merge_config(self._read_toml(user_config_path))
    
    # TIER 2: Merge project config (overrides user config)
    project_config_path = Path.cwd() / ".projectai.toml"
    if project_config_path.exists():
        self._merge_config(self._read_toml(project_config_path))
    
    # TIER 1: Apply environment overrides (highest priority)
    self._apply_env_overrides()
```

### Environment Variable Override Pattern

```python
def _apply_env_overrides(self) -> None:
    """Apply environment variable overrides with PROJECTAI_ prefix."""
    prefix = "PROJECTAI_"
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Parse: PROJECTAI_GENERAL_LOG_LEVEL → section="general", key="log_level"
            parts = key[len(prefix):].lower().split("_", 1)
            if len(parts) == 2:
                section, config_key = parts
                
                if section in self.config:
                    # Type preservation
                    original_value = self.config[section].get(config_key)
                    if isinstance(original_value, bool):
                        value = value.lower() in ("true", "1", "yes")
                    elif isinstance(original_value, int):
                        value = int(value)
                    elif isinstance(original_value, float):
                        value = float(value)
                    
                    # Override value (HIGHEST PRIORITY)
                    self.config[section][config_key] = value
```

---

## Hierarchy 2: API Config Override Precedence

### File: `config/settings.py`

### 2-Tier Precedence (Simple)

```
┌──────────────────────────────────────────┐
│  TIER 1: Environment Variables           │  ← HIGHEST
│  Example: API_PORT=8001                  │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 2: Hardcoded Defaults              │  ← LOWEST
│  Example: API_PORT default is 8001       │
└──────────────────────────────────────────┘
```

### Implementation

```python
class Config:
    # Direct environment variable access with defaults
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Environment ALWAYS wins (no file-based config)
```

**Pattern:** Single-level override via `os.getenv(key, default)`.

---

## Hierarchy 3: Settings Manager Override Precedence

### File: `config/settings_manager.py`

### Runtime Override Hierarchy

```
┌──────────────────────────────────────────┐
│  TIER 1: set_setting() Calls             │  ← Runtime overrides
│  Example: set_setting("privacy", ...)    │
│  Timing: Anytime during execution        │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 2: import_settings() Imports       │  ← Bulk overrides
│  Source: Encrypted export file           │
│  Timing: User-initiated import           │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 3: Constructor Defaults            │  ← Initial state
│  Location: __init__ method               │
│  Timing: Object creation                 │
└──────────────────────────────────────────┘
```

### Runtime Override Pattern

```python
def set_setting(self, category: str, key: str, value: Any):
    """Set a specific setting (HIGHEST PRIORITY - runtime override)."""
    if category not in self.settings:
        self.settings[category] = {}
    
    old_value = self.settings[category].get(key)
    
    # OVERRIDE: Replaces existing value immediately
    self.settings[category][key] = value
    self._modified = True
    
    # Log override
    self.logger.info("Setting updated: %s.%s = %s", category, key, value)
    
    # Warn on security-critical overrides
    if category in ["security", "privacy", "ad_blocker"]:
        self.logger.warning(
            "SECURITY SETTING CHANGED: %s.%s from %s to %s",
            category, key, old_value, value
        )
```

**Pattern:** Last write wins - no precedence validation.

---

## Hierarchy 4: Command Override System

### File: `src/app/core/command_override.py` [[src/app/core/command_override.py]]

### Emergency Override Hierarchy

```
┌──────────────────────────────────────────┐
│  TIER 1: Master Override Password        │  ← HIGHEST (Emergency)
│  Scope: ALL safety protocols             │
│  Effect: Disables all 10 safety systems  │
│  Audit: Logged to command_override_audit │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 2: Individual Protocol Overrides   │  ← Selective disabling
│  Scope: Single safety protocol           │
│  Example: disable_safety("content_filter")│
│  Audit: Logged with reason               │
└──────────────────────────────────────────┘
                ↓ overrides
┌──────────────────────────────────────────┐
│  TIER 3: Default Safety State            │  ← LOWEST (Normal ops)
│  State: All protocols enabled            │
│  Location: __init__ method               │
└──────────────────────────────────────────┘
```

### Master Override Implementation

> **Security Critical**: Master override system integrated with [[../security/03_defense_layers.md|Defense Layers]] and [[../security/07_security_metrics.md|Security Metrics]]

```python
def activate_master_override(self, password: str) -> bool:
    """Activate master override - disables ALL safety protocols."""
    if not self.authenticate_master(password):
        self.failed_auth_attempts += 1
        self._save_config()
        self._audit_log("Master override auth failed")  # → [[../monitoring/01-logging-system.md|Logging System]]
        return False
    
    # MASTER OVERRIDE: Disable ALL 10 safety protocols
    for protocol in self.safety_protocols:
        self.safety_protocols[protocol] = False
    
    self.master_override_active = True
    self.authenticated = True
    self.auth_timestamp = datetime.now().isoformat()
    
    self._save_config()  # → [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]]
    self._audit_log("MASTER OVERRIDE ACTIVATED - ALL SAFETY DISABLED")  # → [[../security/07_security_metrics.md|Security Metrics]]
    
    return True
```

### Individual Protocol Override

```python
def disable_safety(self, protocol_name: str, reason: str = "") -> bool:
    """Disable individual safety protocol (requires authentication)."""
    if not self.authenticated:
        return False
    
    if protocol_name in self.safety_protocols:
        # SELECTIVE OVERRIDE: Disable single protocol
        self.safety_protocols[protocol_name] = False
        self._save_config()
        self._audit_log(f"Safety disabled: {protocol_name}", reason=reason)
        return True
    
    return False
```

**10 Safety Protocols (Override Targets):**

```python
safety_protocols = {
    "content_filter": True,
    "prompt_safety": True,
    "data_validation": True,
    "rate_limiting": True,
    "user_approval": True,
    "api_safety": True,
    "ml_safety": True,
    "plugin_sandbox": True,
    "cloud_encryption": True,
    "emergency_only": True
}
```

---

## Override Conflict Resolution

### CLI Config (Last Layer Wins)

```bash
# Default
log_level = "INFO"

# User config
PROJECTAI_GENERAL_LOG_LEVEL=DEBUG  # ← Overrides to DEBUG

# Later in script
PROJECTAI_GENERAL_LOG_LEVEL=ERROR  # ← Overrides to ERROR (last wins)
```

**Resolution:** Environment variables are read once at startup - last set value wins.

### Settings Manager (Last Write Wins)

```python
# Initial state
settings.set_setting("privacy", "god_tier_encryption", True)

# Runtime override 1
settings.set_setting("privacy", "god_tier_encryption", False)

# Runtime override 2
settings.set_setting("privacy", "god_tier_encryption", True)

# Final state: True (last write)
```

**Resolution:** No conflict detection - always overwrites.

---

## Override Audit Trail

### CLI Config (No Audit)

```python
# No tracking of overrides
# Cannot answer: "Which tier set this value?"
```

**Limitation:** No provenance tracking.

### Settings Manager (Partial Audit)

```python
# Logs changes but not full history
logger.info("Setting updated: %s.%s = %s", category, key, value)

# Security changes get warnings
logger.warning("SECURITY SETTING CHANGED: %s.%s from %s to %s", ...)
```

**Limitation:** No persistent audit log (only runtime logging).

### Command Override (Full Audit)

```python
def _audit_log(self, action: str, reason: str = ""):
    """Append to audit log with timestamp."""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - {action}"
    if reason:
        log_entry += f" - Reason: {reason}"
    
    try:
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Audit log failed: {e}")
```

**Audit Log Location:** `data/command_override_audit.log` → [[../security/07_security_metrics.md|Security Metrics]]

**Example Entries:**
```
2025-04-20T14:30:00 - Master override auth failed
2025-04-20T14:31:00 - Master override auth successful
2025-04-20T14:31:00 - MASTER OVERRIDE ACTIVATED - ALL SAFETY DISABLED
2025-04-20T14:35:00 - Safety disabled: content_filter - Reason: Emergency debugging
```

> **Full Audit Trail**: Integrated with [[../monitoring/01-logging-system.md|Logging System]]

---

## Override Validation

### CLI Config (No Validation)

```python
# Invalid overrides are NOT caught
PROJECTAI_AI_TEMPERATURE=invalid  # ← Will crash on float() conversion

# Type mismatch not validated
PROJECTAI_SECURITY_ENABLE_FOUR_LAWS=maybe  # ← Not "true"/"false", becomes False
```

### Settings Manager (Security Validation Only)

```python
def validate_settings(self) -> dict[str, Any]:
    """Validate critical overrides."""
    issues = []
    
    # Check if security overrides are dangerous
    if not self.settings["security"]["kill_switch"]:
        issues.append("Kill switch is disabled!")
    
    # Check conflicting overrides
    if (self.settings["remote_access"]["browser_enabled"] and
        not self.settings["remote_access"]["require_authentication"]):
        issues.append("Remote access without authentication!")
    
    return {"valid": len(issues) == 0, "issues": issues}
```

**Pattern:** Validates **state** but not individual override operations.

---

## Override Persistence

### CLI Config (Not Persistent)

```bash
# Environment overrides are session-only
export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
python -m src.app.main  # ← Uses DEBUG

# New terminal session
python -m src.app.main  # ← Uses default (INFO) - override lost
```

**Solution:** Add to shell profile or .env file.

### Settings Manager (Persistent via Export)

```python
# Change settings
settings.set_setting("privacy", "god_tier_encryption", False)

# Export to persist
encrypted_data = settings.export_settings()
with open("settings_backup.enc", "wb") as f:
    f.write(encrypted_data)

# Later: Import to restore overrides
with open("settings_backup.enc", "rb") as f:
    settings.import_settings(f.read())
```

### Command Override (Persistent via Config File)

```python
# Override state saved to JSON
def _save_config(self) -> None:
    """Save override state to file."""
    config = {
        "master_password_hash": self.master_password_hash,
        "safety_protocols": self.safety_protocols,  # ← Persists override state
        "failed_auth_attempts": self.failed_auth_attempts
    }
    with open(self.config_file, "w") as f:
        json.dump(config, f)
```

**File:** `data/command_override_config.json`

---

## Cross-System Override Precedence

### Question: What if environment variable conflicts with imported settings?

**CLI Config:**
```bash
# Environment
PROJECTAI_GENERAL_LOG_LEVEL=DEBUG

# User config file
[general]
log_level = "ERROR"
```

**Result:** Environment wins (DEBUG used).

**Settings Manager:**
```python
# No environment variable integration
# Only in-memory overrides via set_setting() and import_settings()
```

**Result:** No conflict - separate systems.

---

## Override Hierarchy Matrix

| Config System | Highest Priority | Medium Priority | Lowest Priority | Persistent |
|--------------|------------------|-----------------|-----------------|-----------|
| **CLI Config** | Environment vars | Project config | User config → Defaults | No (env), Yes (files) |
| **API Config** | Environment vars | N/A | Hardcoded defaults | No (env) |
| **Settings Manager** | `set_setting()` | `import_settings()` | Constructor defaults | Via export/import |
| **Command Override** | Master override | Individual overrides | Default (all enabled) | Yes (JSON file) |

---

## Recommended: Unified Override System

```python
class UnifiedOverrideSystem:
    """Centralized override management with provenance."""
    
    PRECEDENCE_ORDER = [
        "emergency_override",    # Tier 1: Emergency (Command Override)
        "environment",           # Tier 2: Environment variables
        "runtime",               # Tier 3: Runtime set_setting()
        "project_config",        # Tier 4: Project config file
        "user_config",           # Tier 5: User config file
        "import",                # Tier 6: Imported settings
        "default"                # Tier 7: Hardcoded defaults
    ]
    
    def get_value(self, section: str, key: str) -> tuple[Any, str]:
        """Get value with highest-priority source."""
        for tier in self.PRECEDENCE_ORDER:
            value = self._get_from_tier(tier, section, key)
            if value is not None:
                return value, tier  # Return value + provenance
        return None, "none"
    
    def set_value(self, section: str, key: str, value: Any, tier: str):
        """Set value at specific tier with audit."""
        self._validate_override(section, key, value, tier)
        self._audit_override(section, key, value, tier)
        self._store_override(section, key, value, tier)
```

---

## Related Systems

### Configuration Systems
- [Config Loader](./01_config_loader_relationships.md)
- [Environment Manager](./02_environment_manager_relationships.md)
- [Config Inheritance](./08_config_inheritance_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)
- [Default Values](./10_default_values_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Override security policies
- [[../security/03_defense_layers.md|Defense Layers]] - Master override authentication
- [[../security/07_security_metrics.md|Security Metrics]] - Override audit logging
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Override state persistence
- [[../monitoring/01-logging-system.md|Logging System]] - Override action logging
