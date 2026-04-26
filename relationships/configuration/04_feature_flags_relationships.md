# Feature Flags System Relationships

**System:** Feature Flags  
**Core Files:**
- Environment variable presence checks (implicit flags)
- `config/settings_manager.py` - Feature enable/disable settings
- API key presence (OpenAI, DeepSeek, Hugging Face)
- Component `enabled` flags in configurations

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\04_feature_flags_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Architecture Overview

Project-AI **does not have a dedicated feature flag system**. Instead, it uses **three implicit patterns**:

1. **API Key Presence** → Feature availability (e.g., OPENAI_API_KEY enables GPT models)
2. **Configuration Booleans** → Feature toggles (e.g., `enabled: true` in YAML)
3. **Settings Manager Flags** → Privacy/security feature controls

---

## Feature Flag Pattern 1: API Key Presence (Implicit)

### Mechanism: Environment Variable Check

```python
# Pattern: API key presence enables feature
import os

openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    # OpenAI features ENABLED
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)
else:
    # OpenAI features DISABLED
    logger.warning("OpenAI features unavailable: missing API key")
```

### Feature → API Key Mapping

| Feature | Environment Variable | File Location | Behavior if Missing |
|---------|---------------------|---------------|---------------------|
| **OpenAI GPT Models** | `OPENAI_API_KEY` | `src/app/core/intelligence_engine.py` [[src/app/core/intelligence_engine.py]] | Feature disabled, error on use |
| **OpenAI DALL-E** | `OPENAI_API_KEY` | `src/app/core/image_generator.py` [[src/app/core/image_generator.py]] | Falls back to Hugging Face |
| **DeepSeek Inference** | `DEEPSEEK_API_KEY` | `src/app/core/deepseek_v32_inference.py` [[src/app/core/deepseek_v32_inference.py]] | Feature unavailable |
| **Hugging Face Models** | `HUGGINGFACE_API_KEY` | `src/app/core/image_generator.py` [[src/app/core/image_generator.py]] | Image gen unavailable |
| **Temporal Workflows** | `TEMPORAL_HOST` | `src/app/temporal/config.py` [[src/app/temporal/config.py]] | Uses default localhost:7233 |

### Example: Image Generator Fallback

```python
# src/app/core/image_generator.py

class ImageGenerator:
    def generate(self, prompt: str, backend: str = "huggingface"):
        if backend == "openai":
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                # Fallback to Hugging Face if no OpenAI key
                logger.warning("No OpenAI key, using Hugging Face")
                backend = "huggingface"
        
        if backend == "huggingface":
            hf_key = os.getenv("HUGGINGFACE_API_KEY")
            if not hf_key:
                return None, "Missing Hugging Face API key"
```

**Pattern**: Graceful degradation with fallback options.

---

## Feature Flag Pattern 2: Configuration Booleans

### God Tier Config Feature Flags

File: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]

```python
@dataclass
class VoiceModelConfig:
    enabled: bool = True              # ← Feature flag
    bonding_enabled: bool = True      # ← Sub-feature flag
    auto_select: bool = True          # ← Behavior flag

@dataclass
class VisualModelConfig:
    enabled: bool = True              # ← Feature flag
    bonding_enabled: bool = True      # ← Sub-feature flag

@dataclass
class CameraConfig:
    enabled: bool = True              # ← Feature flag
    auto_discover: bool = True        # ← Behavior flag

@dataclass
class ConversationConfig:
    enabled: bool = True              # ← Feature flag
    intent_detection: bool = True     # ← Sub-feature flag
    entity_extraction: bool = True    # ← Sub-feature flag
    topic_tracking: bool = True       # ← Sub-feature flag

@dataclass
class PolicyConfig:
    enabled: bool = True              # ← Feature flag
    auto_adjust: bool = True          # ← Behavior flag
    no_false_alarms: bool = True      # ← Critical safety flag

@dataclass
class FusionConfig:
    enabled: bool = True              # ← Feature flag
    event_driven: bool = True         # ← Behavior flag
```

### Usage Pattern

```python
# Load config
config = load_god_tier_config()

# Check feature flag before using component
if config.voice_model.enabled:
    voice_system = VoiceModelSystem(config.voice_model)
    voice_system.initialize()
else:
    logger.info("Voice model disabled in config")

# Nested sub-feature check
if config.voice_model.enabled and config.voice_model.bonding_enabled:
    voice_system.enable_bonding()
```

### CLI Config Feature Flags

File: `src/app/core/config.py` [[src/app/core/config.py]]

```python
DEFAULTS = {
    "general": {
        "verbose": False,                    # ← Output verbosity flag
    },
    "security": {
        "enable_four_laws": True,            # ← Asimov's Laws enforcement
        "enable_black_vault": True,          # ← Content blacklist
        "enable_audit_log": True,            # ← Audit logging
    },
    "health": {
        "collect_system_metrics": True,      # ← System metrics collection
        "collect_dependencies": True,        # ← Dependency scanning
        "collect_config_summary": True,      # ← Config snapshot
    }
}
```

---

## Feature Flag Pattern 3: Settings Manager Feature Controls

### File: `config/settings_manager.py`

```python
class SettingsManager:
    def __init__(self):
        self.settings = {
            # Privacy features
            "privacy": {
                "god_tier_encryption": True,         # ← Encryption flag
                "data_minimization": True,           # ← Data minimization flag
                "on_device_only": True,              # ← Cloud sync flag
                "no_telemetry": True,                # ← Telemetry flag
                "no_logging": True,                  # ← Logging flag
                "forensic_resistance": True,         # ← Anti-forensics flag
                "ephemeral_storage": True,           # ← Temp data flag
            },
            
            # Security features
            "security": {
                "kill_switch": True,                 # ← Emergency shutdown
                "vpn_multi_hop": True,               # ← VPN routing
                "vpn_required": True,                # ← VPN enforcement
                "dns_leak_protection": True,         # ← DNS leak prevention
                "auto_security_audit": True,         # ← Auto security checks
                "malware_scanning": True,            # ← Malware scanning
            },
            
            # Browser features
            "browser": {
                "incognito_mode": True,              # ← Private browsing
                "no_history": True,                  # ← History tracking
                "no_cache": True,                    # ← Caching
                "no_cookies": True,                  # ← Cookie storage
                "tab_isolation": True,               # ← Process isolation
                "anti_fingerprint": True,            # ← Fingerprinting defense
            },
            
            # Ad blocker features
            "ad_blocker": {
                "enabled": True,                     # ← Master flag
                "holy_war_mode": True,               # ← Aggressive mode
                "block_ads": True,                   # ← Ad blocking
                "block_trackers": True,              # ← Tracker blocking
                "block_cryptominers": True,          # ← Cryptominer blocking
            },
            
            # Consigliere AI features
            "consigliere": {
                "enabled": True,                     # ← Master flag
                "on_device_only": True,              # ← Local processing
                "code_of_omerta": True,              # ← Privacy mode
                "auto_wipe_on_close": True,          # ← Session cleanup
            },
            
            # Remote access features
            "remote_access": {
                "browser_enabled": False,            # ← Remote browser
                "desktop_enabled": False,            # ← Remote desktop
                "require_authentication": True,      # ← Auth requirement
            }
        }
```

### Feature Flag Hierarchy

```
Settings Manager (Root)
│
├── Privacy Flags (9 flags)
│   ├── god_tier_encryption ────> Enables/disables 7-layer encryption
│   ├── on_device_only ────────> Disables all cloud features
│   └── no_telemetry ──────────> Disables usage tracking
│
├── Security Flags (6+ flags)
│   ├── kill_switch ───────────> Enables emergency shutdown capability
│   ├── vpn_required ──────────> Enforces VPN for all network traffic
│   └── auto_security_audit ───> Enables periodic security scans
│
├── Browser Flags (12+ flags)
│   ├── incognito_mode ────────> Enables private browsing mode
│   ├── anti_fingerprint ──────> Enables fingerprinting countermeasures
│   └── tab_isolation ─────────> Enables process-per-tab isolation
│
├── Ad Blocker Flags (11 flags)
│   ├── enabled ───────────────> Master switch for ad blocker
│   ├── holy_war_mode ─────────> Enables maximum aggressiveness
│   └── block_cryptominers ────> Blocks cryptocurrency miners
│
└── Feature-Specific Flags
    ├── consigliere.enabled ───> Enables AI assistant
    └── remote_access.* ───────> Remote access features
```

---

## Feature Flag Relationships

### Dependency Chains

```
┌────────────────────────────────────────────┐
│  API Key Presence                          │
│  (OPENAI_API_KEY exists)                   │
└────────────────────────────────────────────┘
         ↓ enables
┌────────────────────────────────────────────┐
│  AI Model Provider Selection               │
│  (provider="openai" in config)             │
└────────────────────────────────────────────┘
         ↓ enables
┌────────────────────────────────────────────┐
│  Feature Usage                             │
│  (Intelligence Engine, Image Gen)          │
└────────────────────────────────────────────┘
```

### Hierarchical Flags

```
┌────────────────────────────────────────────┐
│  settings["ad_blocker"]["enabled"] = True  │
└────────────────────────────────────────────┘
         ↓ required for
┌────────────────────────────────────────────┐
│  settings["ad_blocker"]["holy_war_mode"]   │
│  settings["ad_blocker"]["block_ads"]       │
│  settings["ad_blocker"]["block_trackers"]  │
└────────────────────────────────────────────┘
```

**Pattern**: Parent flag must be `True` for child flags to take effect.

### Inverse Flags

```
┌────────────────────────────────────────────┐
│  settings["privacy"]["on_device_only"]=True│
└────────────────────────────────────────────┘
         ↓ disables
┌────────────────────────────────────────────┐
│  Cloud Sync Features                       │
│  - Remote backup                           │
│  - Cloud storage                           │
│  - External API calls (where possible)     │
└────────────────────────────────────────────┘
```

**Pattern**: Privacy flags often **disable** features rather than enable them.

---

## Feature Flag Access Patterns

### Pattern 1: Direct Check (API Keys)

```python
# In component initialization
def __init__(self):
    self.openai_available = bool(os.getenv("OPENAI_API_KEY"))
    if self.openai_available:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Pattern 2: Config Object Check (God Tier)

```python
# In component initialization
def __init__(self, config: GodTierConfig):
    self.config = config
    
    if self.config.voice_model.enabled:
        self._initialize_voice_model()
    
    if self.config.camera.enabled and self.config.camera.auto_discover:
        self._discover_cameras()
```

### Pattern 3: Settings Manager Check

```python
# Runtime feature check
if settings_manager.get_setting("ad_blocker", "enabled"):
    ad_blocker.block_request(url)

# Combined flag check
if (settings_manager.get_setting("ad_blocker", "enabled") and
    settings_manager.get_setting("ad_blocker", "holy_war_mode")):
    ad_blocker.set_aggressiveness("MAXIMUM")
```

### Pattern 4: CLI Config Check

```python
from app.core.config import get_config

config = get_config()

if config.get("security", "enable_four_laws"):
    from app.agents.oversight import OversightAgent
    oversight = OversightAgent()
    oversight.validate_action(action)
```

---

## Runtime Feature Toggle

### Settings Manager (Supports Runtime Changes)

```python
# Enable/disable features at runtime
settings_manager.set_setting("ad_blocker", "holy_war_mode", True)
# ✓ Takes effect immediately

settings_manager.set_setting("security", "kill_switch", False)
# ✓ Takes effect immediately (but logged as security change)
```

### God Tier Config (Requires Save + Reload)

```python
# Modify config
config.voice_model.enabled = False

# Must save and reload for persistence
manager.save_config()
# ✗ Changes lost on restart unless saved

# Application must reload config
new_config = manager.load_config()
# ✓ Now persistent
```

### CLI Config (Requires Restart)

```python
# Modify .projectai.toml
[security]
enable_four_laws = false

# Application must restart or call
config = get_config(reload=True)
# ✓ Now loaded
```

### API Keys (Requires Restart)

```bash
# Modify .env
OPENAI_API_KEY=sk-new-key-here

# Application must restart
# ✗ No runtime reload mechanism
```

---

## Feature Flag Validation

### Settings Manager Validation

```python
def validate_settings(self) -> dict[str, Any]:
    """Validate critical security flags."""
    issues = []
    
    # Ensure critical flags are enabled
    if not self.settings["privacy"]["god_tier_encryption"]:
        issues.append("God tier encryption is disabled!")
    
    if not self.settings["security"]["kill_switch"]:
        issues.append("Kill switch is disabled!")
    
    # Validate flag combinations
    if (self.settings["remote_access"]["browser_enabled"] and
        not self.settings["remote_access"]["require_authentication"]):
        issues.append("Remote access without authentication!")
    
    return {"valid": len(issues) == 0, "issues": issues}
```

**Pattern**: Validator enforces **security policies** via flag combinations.

---

## Feature Flag Discovery

### Inspection Config (Feature Control)

File: `config/inspection_config.yaml`

```yaml
# Feature flags for inspection system
inspection:
  enabled: true                    # ← Master flag
  deep_analysis: true              # ← Sub-feature

integrity:
  enabled: true                    # ← Master flag
  check_circular_dependencies: true
  check_missing_imports: true
  check_dead_code: true

quality:
  enabled: true                    # ← Master flag
  test_coverage:
    enabled: false                 # ← Sub-feature disabled
    min_coverage: 0.8

lint:
  enabled: true                    # ← Master flag
  tools:
    python: ["ruff", "flake8", "mypy", "bandit"]
```

**Pattern**: YAML-based feature toggles for subsystem components.

---

## Anti-Patterns & Gaps

### ❌ Missing: Centralized Feature Flag Registry

```python
# No single source of truth for all features
# Flags scattered across:
# - Settings Manager (privacy/security)
# - God Tier Config (AI components)
# - CLI Config (security policies)
# - Environment variables (API keys)
```

### ❌ Missing: Feature Flag Audit Trail

```python
# No tracking of when flags were toggled
# Settings Manager logs changes but no structured audit
```

### ❌ Missing: A/B Testing / Gradual Rollout

```python
# No support for:
# - Percentage-based rollouts
# - User-based targeting
# - Canary deployments
```

### ❌ Missing: Feature Flag Dependencies

```python
# No declarative dependency system
# Example desired:
# {
#   "voice_model": {
#     "enabled": true,
#     "requires": ["camera.enabled", "OPENAI_API_KEY"]
#   }
# }
```

---

## Recommended Improvements

### 1. Centralized Feature Flag System

```python
@dataclass
class FeatureFlags:
    """Centralized feature flag registry."""
    
    # AI Features
    openai_gpt: bool = field(default_factory=lambda: bool(os.getenv("OPENAI_API_KEY")))
    deepseek: bool = field(default_factory=lambda: bool(os.getenv("DEEPSEEK_API_KEY")))
    voice_model: bool = True
    visual_model: bool = True
    
    # Security Features
    four_laws: bool = True
    black_vault: bool = True
    kill_switch: bool = True
    
    # Privacy Features
    god_tier_encryption: bool = True
    no_telemetry: bool = True
    
    def is_enabled(self, feature: str) -> bool:
        """Check if feature is enabled with dependency resolution."""
        return getattr(self, feature, False)
```

### 2. Feature Flag Validation with Dependencies

```python
class FeatureFlagValidator:
    DEPENDENCIES = {
        "voice_model": ["camera"],
        "visual_model": ["camera"],
        "openai_gpt": lambda: bool(os.getenv("OPENAI_API_KEY"))
    }
    
    def validate(self, flags: FeatureFlags) -> tuple[bool, list[str]]:
        errors = []
        for feature, deps in self.DEPENDENCIES.items():
            if getattr(flags, feature):
                # Check dependencies
                for dep in deps:
                    if not getattr(flags, dep):
                        errors.append(f"{feature} requires {dep}")
        return len(errors) == 0, errors
```

---

## Related Systems

### Configuration Systems
- [Config Loader](./01_config_loader_relationships.md)
- [Environment Manager](./02_environment_manager_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)
- [Override Hierarchy](./09_override_hierarchy_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Security feature flags
- [[../security/03_defense_layers.md|Defense Layers]] - Feature-based defense activation
- [[../security/07_security_metrics.md|Security Metrics]] - Feature flag audit logging
- [[../monitoring/01-logging-system.md|Logging System]] - Feature state logging
- [[../monitoring/08-metrics-collection.md|Metrics Collection]] - Feature usage metrics
