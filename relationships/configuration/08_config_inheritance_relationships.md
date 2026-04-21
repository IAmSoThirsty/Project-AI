# Config Inheritance System Relationships

**System:** Config Inheritance  
**Core Files:**
- `src/app/core/config.py` [[src/app/core/config.py]] - Cascading TOML config inheritance
- `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - YAML merging via `_dict_to_config()`
- `config/settings_manager.py` - Import/merge settings

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\08_config_inheritance_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Inheritance Architecture

Project-AI implements **two distinct inheritance patterns**:

1. **Cascading File Inheritance** (CLI Config) - Multi-file merge with precedence
2. **Import/Merge Pattern** (Settings Manager) - Selective field updates

**God Tier Config does NOT support inheritance** - single YAML file only.

---

## Pattern 1: Cascading File Inheritance (CLI Config)

### File: `src/app/core/config.py` [[src/app/core/config.py]]

### Inheritance Chain

```
Default Values (Hardcoded)
    ↓
User Config (~/.projectai.toml)
    ↓
Project Config (./.projectai.toml)
    ↓
Environment Variables (PROJECTAI_*)
```

**Precedence:** Later sources **override** earlier sources for conflicting keys.

### Implementation

```python
def _load_config(self, config_path: Path | None = None) -> None:
    """Load configuration with cascading inheritance."""
    
    # 1. Start with defaults (base layer)
    self.config = self.DEFAULTS.copy()
    
    # 2. Merge user config (layer 1)
    user_config_path = Path.home() / ".projectai.toml"
    if user_config_path.exists():
        self._merge_config(self._read_toml(user_config_path))
    
    # 3. Merge project config (layer 2)
    project_config_path = Path.cwd() / ".projectai.toml"
    if project_config_path.exists():
        self._merge_config(self._read_toml(project_config_path))
    
    # 4. Merge explicit config file (layer 3, optional)
    if config_path and config_path.exists():
        self._merge_config(self._read_toml(config_path))
    
    # 5. Apply environment overrides (layer 4, highest)
    self._apply_env_overrides()
```

### Merge Algorithm

```python
def _merge_config(self, new_config: dict[str, Any]) -> None:
    """Merge new configuration into existing config.
    
    Behavior:
    - Adds new sections
    - Updates existing keys in existing sections
    - Does NOT delete keys from base config
    """
    for section, values in new_config.items():
        if section not in self.config:
            # New section → add entirely
            self.config[section] = {}
        
        if isinstance(values, dict):
            # Section exists → update keys
            self.config[section].update(values)
        else:
            # Non-dict value → replace entirely
            self.config[section] = values
```

### Example: Three-Layer Inheritance

**Layer 0: Defaults (Hardcoded)**
```python
DEFAULTS = {
    "general": {
        "log_level": "INFO",
        "data_dir": "data",
        "verbose": False
    },
    "ai": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
}
```

**Layer 1: User Config (~/.projectai.toml)**
```toml
[general]
log_level = "DEBUG"          # ← Overrides default "INFO"

[ai]
model = "gpt-4"              # ← Overrides default "gpt-3.5-turbo"
```

**Layer 2: Project Config (./.projectai.toml)**
```toml
[general]
data_dir = "custom_data"     # ← Overrides default "data"

[ai]
temperature = 0.9            # ← Overrides default 0.7
```

**Layer 3: Environment (PROJECTAI_GENERAL_VERBOSE=true)**
```bash
PROJECTAI_GENERAL_VERBOSE=true  # ← Overrides default False
```

**Final Merged Config:**
```python
{
    "general": {
        "log_level": "DEBUG",        # ← From user config
        "data_dir": "custom_data",   # ← From project config
        "verbose": True              # ← From environment
    },
    "ai": {
        "model": "gpt-4",            # ← From user config
        "temperature": 0.9           # ← From project config
    }
}
```

---

## Pattern 2: Import/Merge Settings (Settings Manager)

### File: `config/settings_manager.py`

```python
def import_settings(self, encrypted_data: bytes):
    """Import settings from encrypted data with selective merge."""
    try:
        # Decrypt imported data
        decrypted_data = self.god_tier_encryption.decrypt_god_tier(encrypted_data)
        imported = json.loads(decrypted_data.decode())
        
        # Merge: UPDATE existing categories, don't replace entirely
        for category, values in imported.items():
            if category in self.settings:
                # Category exists → update keys (preserve other keys)
                self.settings[category].update(values)
            else:
                # New category → add entirely
                self.settings[category] = values
        
        self._modified = True
        self.logger.info("Settings imported successfully")
    
    except Exception as e:
        self.logger.error("Failed to import settings: %s", e)
```

### Merge Behavior

```python
# Current settings:
settings = {
    "privacy": {
        "god_tier_encryption": True,
        "no_telemetry": True,
        "existing_key": "value"
    }
}

# Imported settings:
imported = {
    "privacy": {
        "god_tier_encryption": False,  # ← Overrides existing
        "new_key": "new_value"          # ← Adds new key
        # "no_telemetry" not present → PRESERVED
    }
}

# After merge:
settings = {
    "privacy": {
        "god_tier_encryption": False,   # ← Updated
        "no_telemetry": True,           # ← Preserved (not in import)
        "existing_key": "value",        # ← Preserved (not in import)
        "new_key": "new_value"          # ← Added
    }
}
```

**Key Difference from CLI Config:**
- Settings Manager uses `dict.update()` → **preserves keys not in import**
- CLI Config uses `dict.update()` similarly → same behavior

---

## Non-Inheritance Pattern (God Tier Config)

### File: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]

**God Tier Config does NOT support inheritance.** It loads from a **single YAML file** only.

```python
def load_config(self) -> GodTierConfig:
    """Load configuration from SINGLE YAML file."""
    if os.path.exists(self.config_file):
        with open(self.config_file) as f:
            config_dict = yaml.safe_load(f)
        
        if config_dict:
            self.config = self._dict_to_config(config_dict)
    else:
        # No file → use defaults
        self.config = GodTierConfig()  # All dataclass defaults
    
    return self.config
```

**No multi-file support.** To achieve "inheritance":
1. Manually merge YAML files before loading, OR
2. Maintain multiple YAML files and switch via environment variable

```python
# Workaround: Environment-based config selection
env = os.getenv("ENVIRONMENT", "production")
config_file = f"config/god_tier_config.{env}.yaml"
manager = ConfigurationManager(config_file)
```

---

## Inheritance Depth Comparison

| Config System | Max Depth | Layers | Merge Strategy |
|--------------|-----------|--------|---------------|
| **CLI Config** | 4 | Defaults → User → Project → Env | `dict.update()` per layer |
| **Settings Manager** | 1 | Current → Import | `dict.update()` on import |
| **God Tier** | 0 | Single file only | No merge |
| **API Config** | 1 | Defaults → Env | Direct override via `os.getenv()` |

---

## Inheritance Visualization

### CLI Config (4 Layers)

```
┌─────────────────────────────────────────┐
│  Layer 0: DEFAULTS (Hardcoded)          │
│  {                                      │
│    "general": {"log_level": "INFO"},    │
│    "ai": {"model": "gpt-3.5-turbo"}     │
│  }                                      │
└─────────────────────────────────────────┘
         ↓ merge
┌─────────────────────────────────────────┐
│  Layer 1: ~/.projectai.toml             │
│  [general]                              │
│  log_level = "DEBUG"                    │
│  → Overrides "INFO"                     │
└─────────────────────────────────────────┘
         ↓ merge
┌─────────────────────────────────────────┐
│  Layer 2: ./.projectai.toml             │
│  [ai]                                   │
│  model = "gpt-4"                        │
│  → Overrides "gpt-3.5-turbo"            │
└─────────────────────────────────────────┘
         ↓ merge
┌─────────────────────────────────────────┐
│  Layer 3: Environment (PROJECTAI_*)     │
│  PROJECTAI_GENERAL_VERBOSE=true         │
│  → Adds "verbose": True                 │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Final Config:                          │
│  {                                      │
│    "general": {                         │
│      "log_level": "DEBUG",  ← Layer 1   │
│      "verbose": True        ← Layer 3   │
│    },                                   │
│    "ai": {                              │
│      "model": "gpt-4"       ← Layer 2   │
│    }                                    │
│  }                                      │
└─────────────────────────────────────────┘
```

---

## Key Deletion Behavior

### CLI Config: Keys Are NOT Deleted

```toml
# ~/.projectai.toml
[general]
log_level = "DEBUG"
data_dir = "data"

# ./.projectai.toml
[general]
log_level = "INFO"  # ← Overrides "DEBUG"
# data_dir not specified → PRESERVED as "data"
```

**Result:** `data_dir` remains from user config.

### Settings Manager: Keys Are NOT Deleted

```python
# Current:
settings["privacy"]["god_tier_encryption"] = True
settings["privacy"]["no_telemetry"] = True

# Import:
imported["privacy"]["god_tier_encryption"] = False
# "no_telemetry" not in import

# After merge:
# "no_telemetry" still True (preserved)
```

**Pattern:** Both systems use **additive merging** - keys are never deleted.

---

## Inheritance and Validation

### CLI Config (No Validation)

```python
# Merged config has no validation
# Possible to create invalid combinations via inheritance
[security]
enable_four_laws = false  # From user config

[security]
enable_black_vault = true  # From project config
# ← Might create invalid state if Black Vault requires Four Laws
```

**Risk:** Invalid cross-key dependencies.

### Settings Manager (Post-Merge Validation)

```python
def import_settings(self, encrypted_data: bytes):
    """Import and merge settings."""
    # ... merge logic ...
    
    # SHOULD validate after merge (not implemented):
    validation = self.validate_settings()
    if not validation["valid"]:
        logger.error(f"Imported settings violate policies: {validation['issues']}")
        # Rollback or reject import
```

**Recommendation:** Validate after every merge operation.

---

## Inheritance Audit Trail

### CLI Config (No Audit)

```python
# No tracking of which layer set which value
# Cannot determine: "Where did this value come from?"
```

### Settings Manager (Partial Logging)

```python
def set_setting(self, category: str, key: str, value: Any):
    """Set setting with logging."""
    old_value = self.settings[category].get(key)
    self.settings[category][key] = value
    
    # Log change
    self.logger.info("Setting updated: %s.%s = %s", category, key, value)
    
    if category in ["security", "privacy", "ad_blocker"]:
        self.logger.warning(
            "SECURITY SETTING CHANGED: %s.%s from %s to %s",
            category, key, old_value, value
        )
```

**Limitation:** Logs changes but not **source** of change.

---

## Recommended: Inheritance with Provenance

```python
@dataclass
class ConfigValue:
    """Config value with provenance tracking."""
    value: Any
    source: str  # "default" | "user_config" | "project_config" | "env"
    timestamp: str

class ConfigWithProvenance:
    def __init__(self):
        self.config = {}
    
    def merge_layer(self, new_config: dict, source: str):
        """Merge with provenance tracking."""
        for section, values in new_config.items():
            if section not in self.config:
                self.config[section] = {}
            
            for key, value in values.items():
                self.config[section][key] = ConfigValue(
                    value=value,
                    source=source,
                    timestamp=datetime.now().isoformat()
                )
    
    def get(self, section: str, key: str):
        """Get value with provenance."""
        config_value = self.config[section][key]
        logger.info(f"{section}.{key} = {config_value.value} (from {config_value.source})")
        return config_value.value
```

---

## Inheritance Conflicts

### Example: Conflicting Security Policies

```toml
# ~/.projectai.toml (User wants debugging)
[security]
enable_four_laws = false
enable_audit_log = false

# ./.projectai.toml (Project enforces security)
[security]
enable_four_laws = true
enable_audit_log = true
```

**Result:** Project config wins (later layer).

**Problem:** User's intent overridden without warning.

**Solution:** Conflict detection and warnings:

```python
def _merge_config_with_warnings(self, new_config: dict, source: str):
    """Merge config and warn on conflicts."""
    for section, values in new_config.items():
        for key, new_value in values.items():
            old_value = self.config.get(section, {}).get(key)
            if old_value is not None and old_value != new_value:
                logger.warning(
                    f"Config conflict: {section}.{key} changed from "
                    f"{old_value} to {new_value} by {source}"
                )
```

---

## Relationships to Other Systems

### Config Loader ← Inheritance

```python
# Inheritance implements loader's merge strategy
config = Config()  # ← Automatically applies 4-layer inheritance
```

### Override Hierarchy ← Inheritance

```python
# Inheritance IS the override hierarchy
# Later layers override earlier layers
```

### Default Values ← Inheritance

```python
# Defaults form the base inheritance layer
self.config = self.DEFAULTS.copy()  # ← Layer 0
```

---

## Related Systems

### Configuration Systems
- [Config Loader](./01_config_loader_relationships.md)
- [Override Hierarchy](./09_override_hierarchy_relationships.md)
- [Default Values](./10_default_values_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Inherited security policies
- [[../security/07_security_metrics.md|Security Metrics]] - Config inheritance audit trail
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Multi-layer config persistence
- [[../monitoring/01-logging-system.md|Logging System]] - Inheritance conflict logging
