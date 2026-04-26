# Settings Manager - Comprehensive Configuration System

**Module**: `config/settings_manager.py`  
**Purpose**: God-tier encrypted settings management for all application features  
**Classification**: Core Configuration System  
**Security Level**: Critical (God-tier encryption required)

---

## Overview

The `SettingsManager` provides comprehensive configuration management with 7-layer God-tier encryption. It manages 11 major setting categories covering all Project-AI features including privacy, security, browser, ad blocker, AI assistant, remote access, network/VPN, firewalls, and support systems.

### Key Characteristics

- **Encryption**: All settings encrypted with God-tier encryption (7 layers)
- **Categories**: 11 comprehensive setting categories
- **Persistence**: JSON-based storage with cryptographic protection
- **Validation**: Security-critical setting validation
- **Export/Import**: Encrypted settings transfer between instances
- **Audit Trail**: Security setting changes logged with warnings

---

## Architecture

### Class Structure

```python
class SettingsManager:
    """Comprehensive Settings Manager with God tier encryption."""
    
    def __init__(self, god_tier_encryption):
        self.logger: logging.Logger
        self.god_tier_encryption: GodTierEncryption
        self._cipher: Fernet
        self.settings: dict[str, dict[str, Any]]
        self._modified: bool
        self._defaults: dict
```

### Setting Categories

#### 1. General Settings
```python
"general": {
    "language": "en",
    "theme": "dark",
    "auto_start": False,
    "minimize_to_tray": True,
    "check_updates": False,  # Privacy-first
    "notifications": True
}
```

#### 2. Privacy Settings (God Tier)
```python
"privacy": {
    "god_tier_encryption": True,
    "encryption_layers": 7,
    "quantum_resistant": True,
    "data_minimization": True,
    "on_device_only": True,
    "no_telemetry": True,
    "no_logging": True,
    "forensic_resistance": True,
    "perfect_forward_secrecy": True,
    "ephemeral_storage": True
}
```

#### 3. Security Settings
```python
"security": {
    "kill_switch": True,
    "kill_switch_mode": "aggressive",  # aggressive/normal
    "vpn_multi_hop": True,
    "vpn_required": True,
    "dns_leak_protection": True,
    "ipv6_leak_protection": True,
    "webrtc_leak_protection": True,
    "firewall_count": 8,
    "firewall_mode": "maximum",
    "auto_security_audit": True,
    "malware_scanning": True,
    "phishing_protection": True
}
```

#### 4. Browser Settings
```python
"browser": {
    "incognito_mode": True,
    "no_history": True,
    "no_cache": True,
    "no_cookies": True,
    "tab_isolation": True,
    "sandbox_enabled": True,
    "anti_fingerprint": True,
    "keyboard_cloaking": True,
    "mouse_cloaking": True,
    "user_agent_rotation": True,
    "referrer_policy": "no-referrer",
    "download_isolation": True,
    "encrypted_downloads": True
}
```

#### 5. Ad Blocker Settings (HOLY WAR)
```python
"ad_blocker": {
    "enabled": True,
    "holy_war_mode": True,
    "aggressiveness": "MAXIMUM",  # MAXIMUM/HIGH/MEDIUM/LOW
    "block_ads": True,
    "block_trackers": True,
    "block_popups": True,
    "block_redirects": True,
    "block_autoplay": True,
    "block_video_ads": True,
    "block_audio_ads": True,
    "block_banners": True,
    "block_malvertising": True,
    "block_cryptominers": True,
    "block_social_widgets": True,
    "custom_filters": True,
    "update_filters": False  # Manual updates for privacy
}
```

#### 6. Thirsty Consigliere Settings
```python
"consigliere": {
    "enabled": True,
    "on_device_only": True,
    "code_of_omerta": True,
    "capability_mode": "manual",  # manual/auto
    "default_locked": True,
    "data_minimization": True,
    "no_training": True,
    "max_context_size": 10,
    "ephemeral_context": True,
    "action_ledger_size": 100,
    "auto_wipe_on_close": True
}
```

#### 7. Media Downloader Settings
```python
"media_downloader": {
    "enabled": True,
    "default_mode": "best_quality",  # audio_only/video_only/audio_video/best_quality
    "audio_format": "mp3",
    "video_format": "mp4",
    "default_quality": "best",
    "download_directory": "./downloads",
    "library_enabled": True,
    "encrypt_metadata": True,
    "encrypt_files": True,
    "auto_organize": True,
    "thumbnail_encryption": True
}
```

#### 8. AI Assistant Settings
```python
"ai_assistant": {
    "enabled": True,
    "god_tier_encrypted": True,
    "local_inference": True,
    "no_external_calls": True,
    "no_data_collection": True,
    "max_context": 20,
    "capabilities": {
        "text_generation": True,
        "code_assistance": True,
        "problem_solving": True,
        "privacy_analysis": True,
        "security_audit": True
    },
    "conversation_encryption": True,
    "auto_clear_history": True
}
```

#### 9. Remote Access Settings
```python
"remote_access": {
    "browser_enabled": False,  # Disabled by default
    "desktop_enabled": False,  # Disabled by default
    "require_authentication": True,
    "require_vpn": True,
    "encryption_required": True,
    "session_timeout": 3600,  # 1 hour
    "max_sessions": 1,
    "remote_host": "0.0.0.0",
    "remote_port": 9000,
    "desktop_port": 9001,
    "secure_tunnel": True
}
```

#### 10. Network/VPN Settings
```python
"network": {
    "vpn_enabled": True,
    "vpn_protocol": "multi-protocol",
    "vpn_hops": 3,  # Multi-hop routing
    "max_hops": 5,
    "location_spoofing": True,
    "dns_over_https": True,
    "dns_provider": "cloudflare",  # cloudflare/quad9/custom
    "split_tunneling": False,  # All traffic through VPN
    "stealth_mode": True,
    "never_logs": True,
    "connection_timeout": 30,
    "auto_reconnect": True
}
```

#### 11. Firewall Settings (8 Types)
```python
"firewalls": {
    "packet_filtering": {
        "enabled": True,
        "mode": "strict",
        "default_policy": "deny"
    },
    "circuit_level": {
        "enabled": True,
        "tcp_monitoring": True
    },
    "stateful_inspection": {
        "enabled": True,
        "connection_tracking": True
    },
    "proxy": {
        "enabled": True,
        "application_layer": True
    },
    "next_generation": {
        "enabled": True,
        "ai_powered": True,
        "threat_detection": True
    },
    "software": {
        "enabled": True,
        "user_space_protection": True
    },
    "hardware": {
        "enabled": True,
        "hardware_filtering": True
    },
    "cloud": {
        "enabled": True,
        "distributed_protection": True
    }
}
```

#### 12. Support Settings
```python
"support": {
    "qa_enabled": True,
    "contact_enabled": True,
    "feedback_enabled": True,
    "bug_reports_enabled": True,
    "feature_requests_enabled": True,
    "security_reports_enabled": True,
    "code_of_conduct_suggestions": True,
    "encrypt_communications": True
}
```

#### 13. Advanced Settings
```python
"advanced": {
    "debug_mode": False,
    "verbose_logging": False,
    "performance_monitoring": False,
    "memory_optimization": True,
    "cpu_priority": "normal",
    "network_buffer_size": 65536,
    "max_concurrent_connections": 100,
    "encryption_hardware_acceleration": True
}
```

---

## Core API

### Initialization

```python
def __init__(self, god_tier_encryption):
    """Initialize SettingsManager with God-tier encryption.
    
    Args:
        god_tier_encryption: GodTierEncryption instance for data protection
    """
```

### Getting Settings

```python
def get_setting(self, category: str, key: str) -> Any:
    """Get a specific setting value.
    
    Args:
        category: Setting category (e.g., "security", "privacy")
        key: Setting key within category
    
    Returns:
        Setting value or None if not found
    """

def get_category(self, category: str) -> dict[str, Any]:
    """Get all settings in a category.
    
    Returns:
        Copy of category settings dictionary
    """

def get_all_settings(self) -> dict[str, dict[str, Any]]:
    """Get complete settings dictionary.
    
    Returns:
        Copy of all settings
    """
```

### Setting Settings

```python
def set_setting(self, category: str, key: str, value: Any):
    """Set a specific setting value.
    
    Args:
        category: Setting category
        key: Setting key
        value: New value
    
    Side Effects:
        - Logs setting change
        - Logs security warning for critical settings
        - Sets _modified flag
    """
```

### Reset Operations

```python
def reset_category(self, category: str):
    """Reset a category to default values.
    
    Args:
        category: Category to reset
    """

def reset_all():
    """Reset all settings to defaults.
    
    Logs:
        WARNING level log entry
    """
```

### Import/Export

```python
def export_settings(self) -> bytes:
    """Export all settings with God-tier encryption.
    
    Returns:
        Encrypted settings blob
    """

def import_settings(self, encrypted_data: bytes):
    """Import settings from encrypted data.
    
    Args:
        encrypted_data: God-tier encrypted settings
    
    Error Handling:
        Logs errors and continues with existing settings
    """
```

### Validation

```python
def validate_settings(self) -> dict[str, Any]:
    """Validate settings for security and consistency.
    
    Returns:
        {
            "valid": bool,
            "issues": list[str],
            "warnings": int
        }
    
    Validation Checks:
        - God-tier encryption enabled
        - Kill switch enabled
        - HOLY WAR mode enabled
        - Remote access authentication
    """
```

### Status

```python
def get_status(self) -> dict[str, Any]:
    """Get settings manager status.
    
    Returns:
        {
            "god_tier_encrypted": bool,
            "encryption_layers": int,
            "categories": list[str],
            "total_settings": int,
            "modified": bool,
            "validation": dict
        }
    """
```

---

## Configuration Patterns

### 1. Privacy-First Defaults

**Pattern**: All privacy-related settings default to maximum protection.

```python
# Anti-pattern: Opt-in privacy
"check_updates": True  # ❌ Phones home by default

# Correct pattern: Opt-out privacy
"check_updates": False  # ✅ No auto-updates for privacy
```

**Rationale**: Users must explicitly enable features that compromise privacy.

### 2. Security-Critical Setting Changes

**Pattern**: Log security setting changes at WARNING level.

```python
if category in ["security", "privacy", "ad_blocker"]:
    self.logger.warning(
        "SECURITY SETTING CHANGED: %s.%s from %s to %s",
        category, key, old_value, value
    )
```

**Use Case**: Audit trail for security configuration changes.

### 3. Encryption-at-Rest

**Pattern**: All settings stored with God-tier encryption.

```python
def export_settings(self) -> bytes:
    settings_json = json.dumps(self.settings, indent=2)
    return self.god_tier_encryption.encrypt_god_tier(
        settings_json.encode()
    )
```

**Benefit**: Settings file cannot be modified externally without encryption keys.

### 4. Defaults Preservation

**Pattern**: Keep immutable copy of defaults for reset operations.

```python
self._modified = False
self._defaults = self.settings.copy()  # Immutable defaults
```

**Use Case**: Factory reset functionality.

### 5. Validation Before Use

**Pattern**: Validate settings integrity before relying on values.

```python
validation = settings_manager.validate_settings()
if not validation["valid"]:
    for issue in validation["issues"]:
        logger.error("Settings issue: %s", issue)
```

**Benefit**: Catch configuration errors before runtime failures.

---

## Environment Handling

### Environment Variables

Settings can be overridden via environment variables (not implemented in SettingsManager, but common pattern):

```bash
# Override theme
export PROJECT_AI_THEME=dark

# Override VPN hops
export PROJECT_AI_VPN_HOPS=5
```

### Configuration Files

Settings are NOT stored in plain text files by design:

- **Export**: Produces God-tier encrypted blob
- **Import**: Accepts only encrypted data
- **No Plain Text**: Settings never written unencrypted

---

## Integration Patterns

### Pattern 1: Initialization

```python
from config.settings_manager import SettingsManager
from src.app.core.god_tier_encryption import GodTierEncryption

# Initialize encryption first
god_tier_encryption = GodTierEncryption()

# Create settings manager
settings_manager = SettingsManager(god_tier_encryption)
```

### Pattern 2: Reading Settings

```python
# Get specific setting
theme = settings_manager.get_setting("general", "theme")

# Get category
browser_settings = settings_manager.get_category("browser")

# Get all settings
all_settings = settings_manager.get_all_settings()
```

### Pattern 3: Updating Settings

```python
# Update single setting
settings_manager.set_setting("security", "firewall_mode", "maximum")

# Update multiple settings
for key, value in new_browser_settings.items():
    settings_manager.set_setting("browser", key, value)
```

### Pattern 4: Validation

```python
# Validate before use
validation = settings_manager.validate_settings()
if not validation["valid"]:
    logger.error("Invalid settings: %s", validation["issues"])
    # Fix issues or reset to defaults
    settings_manager.reset_all()
```

### Pattern 5: Export/Import

```python
# Export settings
encrypted_settings = settings_manager.export_settings()
with open("settings_backup.enc", "wb") as f:
    f.write(encrypted_settings)

# Import settings
with open("settings_backup.enc", "rb") as f:
    encrypted_settings = f.read()
settings_manager.import_settings(encrypted_settings)
```

---

## Security Considerations

### 1. Encryption Requirements

- **God-Tier Encryption**: All settings encrypted with 7-layer encryption
- **Key Management**: Encryption keys never stored in settings
- **Transport Security**: Use encrypted channels for settings transfer

### 2. Validation Enforcement

```python
# Critical: Validate before trusting settings
validation = settings_manager.validate_settings()
assert validation["valid"], f"Invalid settings: {validation['issues']}"
```

### 3. Audit Trail

- All security setting changes logged
- Timestamp and old/new values recorded
- WARNING level for security-critical changes

### 4. Default Security Posture

- Kill switch enabled by default
- VPN required by default
- All leak protections enabled
- Remote access disabled by default
- Maximum firewall mode by default

### 5. No External Dependencies

- Settings validation is self-contained
- No network calls required
- No external configuration servers

---

## Testing

### Unit Testing

```python
import pytest
from config.settings_manager import SettingsManager

@pytest.fixture
def manager(god_tier_encryption):
    return SettingsManager(god_tier_encryption)

def test_get_setting(manager):
    theme = manager.get_setting("general", "theme")
    assert theme == "dark"

def test_set_setting(manager):
    manager.set_setting("general", "theme", "light")
    assert manager.get_setting("general", "theme") == "light"

def test_validate_settings(manager):
    validation = manager.validate_settings()
    assert validation["valid"] is True
    assert len(validation["issues"]) == 0

def test_reset_category(manager):
    manager.set_setting("general", "theme", "light")
    manager.reset_category("general")
    assert manager.get_setting("general", "theme") == "dark"

def test_export_import(manager):
    encrypted = manager.export_settings()
    assert isinstance(encrypted, bytes)
    
    manager.set_setting("general", "theme", "light")
    manager.import_settings(encrypted)
    assert manager.get_setting("general", "theme") == "dark"
```

### Integration Testing

```python
def test_encryption_integration(manager, god_tier_encryption):
    # Export settings
    encrypted = manager.export_settings()
    
    # Verify encryption
    with pytest.raises(Exception):
        json.loads(encrypted)  # Should fail - encrypted
    
    # Decrypt manually
    decrypted = god_tier_encryption.decrypt_god_tier(encrypted)
    settings = json.loads(decrypted)
    assert "general" in settings
```

---

## Performance Considerations

### Memory Usage

- **In-Memory Storage**: All settings kept in memory
- **Size**: ~10KB for default settings
- **Copies**: Defaults preserved separately (~10KB additional)

### Encryption Overhead

- **Export**: O(n) where n = settings size
- **Import**: O(n) decryption + O(n) JSON parsing
- **Typical Time**: <10ms for export/import

### Optimization Tips

1. **Batch Updates**: Group multiple set_setting calls
2. **Lazy Validation**: Validate only when needed
3. **Category Access**: Use get_category for multiple reads

---

## Troubleshooting

### Issue: Settings Not Persisting

**Symptom**: Changes lost after restart

**Cause**: SettingsManager does not auto-save to disk

**Solution**: Implement persistence layer:
```python
def save_to_disk(self, path: str = "data/settings.enc"):
    encrypted = self.export_settings()
    with open(path, "wb") as f:
        f.write(encrypted)

def load_from_disk(self, path: str = "data/settings.enc"):
    with open(path, "rb") as f:
        encrypted = f.read()
    self.import_settings(encrypted)
```

### Issue: Validation Fails

**Symptom**: validate_settings() returns issues

**Solution**: Check and fix reported issues:
```python
validation = settings_manager.validate_settings()
for issue in validation["issues"]:
    if "God tier encryption is disabled" in issue:
        settings_manager.set_setting("privacy", "god_tier_encryption", True)
    elif "Kill switch is disabled" in issue:
        settings_manager.set_setting("security", "kill_switch", True)
```

### Issue: Cannot Import Settings

**Symptom**: import_settings() fails silently

**Cause**: Encryption key mismatch or corrupted data

**Solution**: Verify encryption keys match:
```python
try:
    manager.import_settings(encrypted_data)
except Exception as e:
    logger.error("Import failed: %s", e)
    # Fall back to defaults
    manager.reset_all()
```

---

## Related Modules

- **God-Tier Encryption**: `src/app/core/god_tier_encryption.py` - Provides encryption layer
- **Settings Dialog**: `src/app/gui/settings_dialog.py` [[src/app/gui/settings_dialog.py]] - GUI for settings management
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - Lower-level configuration
- **Config Settings**: `config/settings.py` - Simple settings persistence

---

## Migration Guide

### From Plain Text Config

If migrating from plain text configuration:

```python
# Old: Plain text JSON
with open("settings.json") as f:
    old_settings = json.load(f)

# New: God-tier encrypted
settings_manager = SettingsManager(god_tier_encryption)
for category, values in old_settings.items():
    for key, value in values.items():
        settings_manager.set_setting(category, key, value)

# Export encrypted
encrypted = settings_manager.export_settings()
with open("settings.enc", "wb") as f:
    f.write(encrypted)
```

### Adding New Settings

To add new settings category:

```python
# 1. Add to defaults in __init__
self.settings = {
    # ... existing categories ...
    "new_category": {
        "setting1": default_value1,
        "setting2": default_value2
    }
}

# 2. Update validation if needed
def validate_settings(self):
    # ... existing validation ...
    if self.settings["new_category"]["setting1"] < 0:
        issues.append("setting1 must be non-negative")
```

---

## Best Practices

1. **Always Validate**: Call validate_settings() after import
2. **Log Security Changes**: Keep audit trail of critical setting changes
3. **Use Defaults**: Leverage reset functions for factory reset
4. **Batch Updates**: Group related setting changes
5. **Encrypt Everything**: Never export settings unencrypted
6. **Test Validation**: Write tests for custom validation rules
7. **Document Defaults**: Keep settings documentation updated
8. **Type Safety**: Validate setting value types before setting
9. **Category Isolation**: Use get_category for related settings
10. **Immutable Defaults**: Never modify _defaults directly

---

## Future Enhancements

1. **Schema Validation**: JSON schema validation for settings structure
2. **Type Hints**: Stronger typing for setting values
3. **Auto-Persistence**: Automatic background save to disk
4. **Setting Profiles**: Multiple configuration profiles (work, home, etc.)
5. **Remote Sync**: Secure cloud sync between devices
6. **Version Control**: Track setting changes over time
7. **Conditional Validation**: Context-aware validation rules
8. **Performance Metrics**: Track setting impact on performance
9. **A/B Testing**: Experimental settings for feature testing
10. **Migration Tools**: Automated settings migration between versions


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[config/settings_manager.py]]
