#!/usr/bin/env python3
"""
Configuration Loader with Hot-Reload Support
Project-AI Enterprise Monolithic Architecture

Implements:
- Thread-pooled configuration watching
- Hot-reload without application restart
- Error capture and aggregation
- Configuration validation and rollback
- Multi-file configuration support
- Backup and recovery
- Thread-safe operations

Production-ready configuration management with comprehensive error handling.
"""

import hashlib
import json
import logging
import os
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# Default configuration paths
DEFAULT_CONFIG_DIR = Path('config')
DEFAULT_BACKUP_DIR = Path('var/config_backups')
DEFAULT_WATCH_POLL_SEC = 10


class ConfigLoadError(Exception):
    """Raised when configuration loading fails."""
    pass


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigLoader:
    """
    Configuration loader with hot-reload capability.
    
    Features:
    - Thread-pooled file watching
    - Automatic reload on file changes
    - Validation before applying changes
    - Automatic backup and rollback
    - Error aggregation and vault integration
    - Thread-safe operations
    """
    
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        backup_dir: Optional[Path] = None,
        watch_poll_sec: int = DEFAULT_WATCH_POLL_SEC
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
            backup_dir: Directory for configuration backups
            watch_poll_sec: Polling interval for file watching
        """
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.backup_dir = backup_dir or DEFAULT_BACKUP_DIR
        self.watch_poll_sec = watch_poll_sec
        
        # Configuration state
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.file_hashes: Dict[str, str] = {}
        self.lock = threading.Lock()
        
        # Thread pool for watching
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="config_watcher")
        self.watching = False
        self.watch_thread = None
        
        # Reload callbacks
        self.reload_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Error aggregation
        self.error_count = 0
        self.max_errors = 10
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load initial configuration
        self._load_all_configs()
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file contents."""
        if not file_path.exists():
            return ""
        
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _backup_config(self, config_name: str) -> Path:
        """
        Create backup of configuration file.
        
        Args:
            config_name: Name of configuration
            
        Returns:
            Path to backup file
        """
        source_file = self.config_dir / f"{config_name}.yaml"
        if not source_file.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"{config_name}_{timestamp}.yaml"
        
        shutil.copy2(source_file, backup_file)
        logger.info(f"Backed up config '{config_name}' to {backup_file}")
        
        return backup_file
    
    def _validate_config(self, config_data: Dict[str, Any], config_name: str) -> bool:
        """
        Validate configuration data.
        
        Args:
            config_data: Configuration dictionary to validate
            config_name: Name of configuration
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - ensure it's a dictionary
            if not isinstance(config_data, dict):
                raise ConfigValidationError(f"Config must be a dictionary, got {type(config_data)}")
            
            # Config-specific validation
            if config_name == 'distress':
                # Validate distress config structure
                required_keys = ['version', 'vault', 'signals']
                missing = [k for k in required_keys if k not in config_data]
                if missing:
                    raise ConfigValidationError(f"Missing required keys: {', '.join(missing)}")
            
            elif config_name == 'security_hardening':
                # Validate security config
                if 'enabled' not in config_data:
                    raise ConfigValidationError("Security config must have 'enabled' field")
            
            return True
            
        except Exception as e:
            logger.error(f"Config validation failed for '{config_name}': {e}")
            return False
    
    def _load_config_file(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a single configuration file.
        
        Args:
            config_name: Name of configuration (without .yaml extension)
            
        Returns:
            Configuration dictionary or None if load failed
        """
        config_file = self.config_dir / f"{config_name}.yaml"
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}")
            return None
        
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not self._validate_config(config_data, config_name):
                return None
            
            # Update file hash
            self.file_hashes[config_name] = self._compute_file_hash(config_file)
            
            logger.info(f"Loaded config '{config_name}' from {config_file}")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load config '{config_name}': {e}")
            return None
    
    def _load_all_configs(self):
        """Load all configuration files from config directory."""
        if not self.config_dir.exists():
            logger.warning(f"Config directory does not exist: {self.config_dir}")
            return
        
        for config_file in self.config_dir.glob('*.yaml'):
            config_name = config_file.stem
            config_data = self._load_config_file(config_name)
            
            if config_data:
                with self.lock:
                    self.configs[config_name] = config_data
    
    def _reload_config(self, config_name: str) -> bool:
        """
        Reload a single configuration file.
        
        Args:
            config_name: Name of configuration to reload
            
        Returns:
            True if reload successful, False otherwise
        """
        try:
            # Backup current config before reload
            backup_path = self._backup_config(config_name)
            
            # Load new configuration
            new_config = self._load_config_file(config_name)
            
            if new_config is None:
                logger.error(f"Failed to reload config '{config_name}', keeping current")
                return False
            
            # Update configuration
            with self.lock:
                old_config = self.configs.get(config_name)
                self.configs[config_name] = new_config
            
            # Trigger reload callbacks
            for callback in self.reload_callbacks:
                try:
                    callback(config_name, new_config)
                except Exception as e:
                    logger.error(f"Reload callback failed for '{config_name}': {e}")
            
            # Audit the reload
            try:
                from src.app.governance.audit_log import AuditLog
                audit = AuditLog()
                audit.log_event(
                    event_type='config_reloaded',
                    data={
                        'config_name': config_name,
                        'backup_path': str(backup_path) if backup_path else None,
                        'timestamp': datetime.now().isoformat()
                    },
                    actor='system',
                    description=f"Configuration '{config_name}' reloaded successfully"
                )
            except Exception:
                pass
            
            logger.info(f"Successfully reloaded config '{config_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading config '{config_name}': {e}")
            
            # Log error to aggregator
            try:
                from src.app.core.error_aggregator import GlobalErrorAggregator
                from security.black_vault import BlackVault
                
                aggregator = GlobalErrorAggregator()
                aggregator.log(e, {'stage': 'config_reload', 'config_name': config_name})
                
                self.error_count += 1
                if self.error_count >= self.max_errors:
                    vault_id = aggregator.flush_to_vault(BlackVault(), f'config_reload_errors_{config_name}')
                    logger.critical(f"Max config reload errors reached, flushed to vault: {vault_id}")
                    self.error_count = 0
            except Exception:
                pass
            
            return False
    
    def _watcher_thread(self, reload_callback: Optional[Callable] = None):
        """
        Configuration file watcher thread.
        
        Args:
            reload_callback: Optional callback function on reload
        """
        logger.info(f"Config watcher started (poll interval: {self.watch_poll_sec}s)")
        
        while self.watching:
            try:
                time.sleep(self.watch_poll_sec)
                
                # Check all config files for changes
                for config_file in self.config_dir.glob('*.yaml'):
                    config_name = config_file.stem
                    current_hash = self._compute_file_hash(config_file)
                    previous_hash = self.file_hashes.get(config_name, "")
                    
                    if current_hash != previous_hash and current_hash:
                        logger.info(f"Config file changed: {config_name}")
                        self._reload_config(config_name)
                        
                        if reload_callback:
                            try:
                                reload_callback(config_name, self.configs.get(config_name))
                            except Exception as e:
                                logger.error(f"Reload callback failed: {e}")
                
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")
                
                # Log to error aggregator
                try:
                    from src.app.core.error_aggregator import GlobalErrorAggregator
                    from security.black_vault import BlackVault
                    
                    aggregator = GlobalErrorAggregator()
                    aggregator.log(e, {'stage': 'watcher_thread'})
                    aggregator.flush_to_vault(BlackVault(), 'watcher_crash')
                except Exception:
                    pass
    
    def watch(self, reload_callback: Optional[Callable] = None):
        """
        Start watching configuration files for changes.
        
        Args:
            reload_callback: Optional callback function called on reload
        """
        if self.watching:
            logger.warning("Config watcher already running")
            return
        
        self.watching = True
        
        # Add callback if provided
        if reload_callback:
            self.reload_callbacks.append(reload_callback)
        
        # Submit watcher to thread pool
        self.executor.submit(self._watcher_thread, reload_callback)
        
        logger.info("Config watcher thread submitted to executor")
    
    def stop_watching(self):
        """Stop watching configuration files."""
        if not self.watching:
            return
        
        logger.info("Stopping config watcher...")
        self.watching = False
        
        # Wait briefly for watcher to stop
        time.sleep(self.watch_poll_sec + 1)
        
        logger.info("Config watcher stopped")
    
    def get(self, config_name: str, default: Any = None) -> Dict[str, Any]:
        """
        Get configuration by name.
        
        Args:
            config_name: Name of configuration
            default: Default value if not found
            
        Returns:
            Configuration dictionary
        """
        with self.lock:
            return self.configs.get(config_name, default or {})
    
    def get_value(self, config_name: str, key_path: str, default: Any = None) -> Any:
        """
        Get specific configuration value by key path.
        
        Args:
            config_name: Name of configuration
            key_path: Dot-separated key path (e.g., 'vault.kms_provider')
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        config = self.get(config_name)
        
        if not config:
            return default
        
        # Navigate key path
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def reload(self, config_name: str) -> bool:
        """
        Manually reload a configuration.
        
        Args:
            config_name: Name of configuration to reload
            
        Returns:
            True if reload successful
        """
        return self._reload_config(config_name)
    
    def reload_all(self) -> int:
        """
        Reload all configurations.
        
        Returns:
            Number of successfully reloaded configs
        """
        success_count = 0
        
        for config_name in list(self.configs.keys()):
            if self._reload_config(config_name):
                success_count += 1
        
        return success_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get configuration loader statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return {
                'configs_loaded': len(self.configs),
                'config_names': list(self.configs.keys()),
                'watching': self.watching,
                'watch_poll_sec': self.watch_poll_sec,
                'error_count': self.error_count,
                'backup_count': len(list(self.backup_dir.glob('*.yaml')))
            }
    
    def shutdown(self):
        """Shutdown the configuration loader."""
        self.stop_watching()
        self.executor.shutdown(wait=True, cancel_futures=True)
        logger.info("ConfigLoader shutdown complete")


# Global configuration loader instance
_global_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _global_config_loader
    
    if _global_config_loader is None:
        _global_config_loader = ConfigLoader()
    
    return _global_config_loader


if __name__ == '__main__':
    # Testing
    logging.basicConfig(level=logging.INFO)
    
    loader = ConfigLoader()
    
    # Test get config
    distress_config = loader.get('distress')
    print(f"Loaded distress config: {bool(distress_config)}")
    
    # Test get value
    vault_provider = loader.get_value('distress', 'vault.kms_provider', 'unknown')
    print(f"Vault KMS provider: {vault_provider}")
    
    # Test stats
    stats = loader.get_stats()
    print(f"Config stats: {json.dumps(stats, indent=2)}")
    
    # Test watching (run for 30 seconds)
    def on_reload(config_name, config_data):
        print(f"Config reloaded: {config_name}")
    
    loader.watch(on_reload)
    print("Watching for config changes (30 seconds)...")
    time.sleep(30)
    
    loader.shutdown()
