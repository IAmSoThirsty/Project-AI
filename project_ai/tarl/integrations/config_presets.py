"""
T.A.R.L. Configuration Presets

Improved UX with opinionated defaults for different deployment scenarios.
Makes it easy to get started with T.A.R.L. without configuring every knob.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DeploymentProfile(Enum):
    """Pre-configured deployment profiles"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    HIGH_AVAILABILITY = "high_availability"
    LOW_RESOURCE = "low_resource"


class ComplianceProfile(Enum):
    """Pre-configured compliance profiles"""

    NONE = "none"
    BASIC = "basic"
    HEALTHCARE = "healthcare"  # HIPAA, GDPR
    FINANCIAL = "financial"  # SOC2, PCI-DSS
    EU_REGULATED = "eu_regulated"  # EU AI Act, GDPR
    GOVERNMENT = "government"  # FedRAMP, NIST


@dataclass
class TarlConfig:
    """Unified configuration for T.A.R.L. with smart defaults"""

    # Deployment settings
    deployment_profile: DeploymentProfile = DeploymentProfile.DEVELOPMENT
    compliance_profile: ComplianceProfile = ComplianceProfile.NONE

    # Worker settings
    workers: int = 4
    max_workers: int = 16
    worker_timeout: int = 300

    # Storage settings
    data_dir: str = "data/tarl"
    enable_persistence: bool = True
    snapshot_interval: int = 60

    # Observability settings
    enable_metrics: bool = True
    enable_tracing: bool = False
    log_level: str = "INFO"
    structured_logging: bool = True

    # Security settings
    enable_capability_checks: bool = True
    enable_guardrails: bool = True
    require_attestations: bool = False

    # Performance settings
    enable_caching: bool = True
    enable_compression: bool = False
    max_queue_depth: int = 1000

    # Feature flags
    enable_multi_tenant: bool = False
    enable_ai_provenance: bool = False
    enable_compliance_enforcement: bool = False
    enable_recording: bool = False

    # Advanced settings (usually don't need to change)
    heartbeat_interval: int = 30
    lease_duration: int = 300
    max_retries: int = 3
    retry_backoff_factor: float = 2.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for stack initialization"""
        return {
            "workers": self.workers,
            "data_dir": self.data_dir,
            "enable_metrics": self.enable_metrics,
            "log_level": self.log_level,
            "enable_multi_tenant": self.enable_multi_tenant,
            "enable_ai_provenance": self.enable_ai_provenance,
            "enable_compliance": self.enable_compliance_enforcement,
            "enable_recording": self.enable_recording,
        }


class ConfigPresets:
    """Pre-configured settings for common scenarios"""

    @staticmethod
    def development() -> TarlConfig:
        """Development environment - fast feedback, minimal overhead"""
        return TarlConfig(
            deployment_profile=DeploymentProfile.DEVELOPMENT,
            workers=2,
            log_level="DEBUG",
            enable_metrics=True,
            enable_tracing=True,
            enable_recording=True,  # Enable for debugging
            enable_persistence=True,
            snapshot_interval=30,
            require_attestations=False,
            enable_capability_checks=False,  # Faster iteration
            enable_guardrails=False,
        )

    @staticmethod
    def testing() -> TarlConfig:
        """Testing environment - isolated, reproducible"""
        return TarlConfig(
            deployment_profile=DeploymentProfile.TESTING,
            workers=1,  # Deterministic execution
            log_level="WARNING",
            enable_metrics=False,  # Faster tests
            enable_persistence=False,  # In-memory only
            enable_recording=True,  # For test replay
            data_dir="/tmp/tarl_test",
            enable_capability_checks=True,
            enable_guardrails=True,
            max_queue_depth=100,
        )

    @staticmethod
    def staging() -> TarlConfig:
        """Staging environment - production-like"""
        return TarlConfig(
            deployment_profile=DeploymentProfile.STAGING,
            workers=4,
            log_level="INFO",
            enable_metrics=True,
            enable_tracing=True,
            enable_persistence=True,
            snapshot_interval=60,
            enable_capability_checks=True,
            enable_guardrails=True,
            require_attestations=True,
            enable_compliance_enforcement=True,
            enable_ai_provenance=True,
        )

    @staticmethod
    def production() -> TarlConfig:
        """Production environment - optimized, secure"""
        return TarlConfig(
            deployment_profile=DeploymentProfile.PRODUCTION,
            workers=8,
            max_workers=32,
            log_level="INFO",
            enable_metrics=True,
            enable_tracing=True,
            enable_persistence=True,
            snapshot_interval=300,
            enable_caching=True,
            enable_compression=True,
            enable_capability_checks=True,
            enable_guardrails=True,
            require_attestations=True,
            enable_compliance_enforcement=True,
            enable_ai_provenance=True,
            structured_logging=True,
            max_queue_depth=10000,
            heartbeat_interval=60,
            lease_duration=600,
        )

    @staticmethod
    def high_availability() -> TarlConfig:
        """High availability - maximum redundancy"""
        return TarlConfig(
            deployment_profile=DeploymentProfile.HIGH_AVAILABILITY,
            workers=16,
            max_workers=64,
            log_level="WARNING",  # Reduce log overhead
            enable_metrics=True,
            enable_tracing=False,  # Reduce overhead
            enable_persistence=True,
            snapshot_interval=600,  # Less frequent snapshots
            enable_caching=True,
            enable_compression=True,
            enable_capability_checks=True,
            enable_guardrails=True,
            require_attestations=True,
            structured_logging=True,
            max_queue_depth=50000,
            heartbeat_interval=30,
            lease_duration=600,
            max_retries=5,
            retry_backoff_factor=1.5,
        )

    @staticmethod
    def low_resource() -> TarlConfig:
        """Low resource - minimal memory/CPU footprint"""
        return TarlConfig(
            deployment_profile=DeploymentProfile.LOW_RESOURCE,
            workers=1,
            max_workers=2,
            log_level="ERROR",
            enable_metrics=False,
            enable_tracing=False,
            enable_persistence=True,
            snapshot_interval=600,
            enable_caching=False,
            enable_compression=True,
            max_queue_depth=100,
            enable_capability_checks=True,
            enable_guardrails=False,
            require_attestations=False,
        )

    @staticmethod
    def healthcare_compliant() -> TarlConfig:
        """Healthcare compliance (HIPAA, GDPR)"""
        config = ConfigPresets.production()
        config.compliance_profile = ComplianceProfile.HEALTHCARE
        config.require_attestations = True
        config.enable_compliance_enforcement = True
        config.enable_ai_provenance = True
        config.enable_guardrails = True
        config.structured_logging = True
        return config

    @staticmethod
    def financial_compliant() -> TarlConfig:
        """Financial compliance (SOC2, PCI-DSS)"""
        config = ConfigPresets.production()
        config.compliance_profile = ComplianceProfile.FINANCIAL
        config.require_attestations = True
        config.enable_compliance_enforcement = True
        config.enable_ai_provenance = True
        config.enable_guardrails = True
        config.structured_logging = True
        return config

    @staticmethod
    def eu_regulated() -> TarlConfig:
        """EU regulation compliance (EU AI Act, GDPR)"""
        config = ConfigPresets.production()
        config.compliance_profile = ComplianceProfile.EU_REGULATED
        config.require_attestations = True
        config.enable_compliance_enforcement = True
        config.enable_ai_provenance = True
        config.enable_guardrails = True
        config.structured_logging = True
        config.enable_recording = True  # For audit trail
        return config


class ConfigBuilder:
    """Fluent builder for custom configurations"""

    def __init__(self, base_preset: str | None = None):
        if base_preset:
            preset_method = getattr(ConfigPresets, base_preset, None)
            if preset_method:
                self._config = preset_method()
            else:
                self._config = TarlConfig()
        else:
            self._config = TarlConfig()

    def with_workers(self, count: int) -> "ConfigBuilder":
        """Set number of workers"""
        self._config.workers = count
        return self

    def with_compliance(self, profile: ComplianceProfile) -> "ConfigBuilder":
        """Set compliance profile"""
        self._config.compliance_profile = profile
        self._config.require_attestations = True
        self._config.enable_compliance_enforcement = True
        return self

    def enable_feature(self, feature: str) -> "ConfigBuilder":
        """Enable a specific feature"""
        feature_map = {
            "multi_tenant": "enable_multi_tenant",
            "ai_provenance": "enable_ai_provenance",
            "compliance": "enable_compliance_enforcement",
            "recording": "enable_recording",
            "metrics": "enable_metrics",
            "tracing": "enable_tracing",
            "caching": "enable_caching",
            "compression": "enable_compression",
            "guardrails": "enable_guardrails",
        }

        attr = feature_map.get(feature)
        if attr:
            setattr(self._config, attr, True)
        return self

    def disable_feature(self, feature: str) -> "ConfigBuilder":
        """Disable a specific feature"""
        feature_map = {
            "multi_tenant": "enable_multi_tenant",
            "ai_provenance": "enable_ai_provenance",
            "compliance": "enable_compliance_enforcement",
            "recording": "enable_recording",
            "metrics": "enable_metrics",
            "tracing": "enable_tracing",
            "caching": "enable_caching",
            "compression": "enable_compression",
            "guardrails": "enable_guardrails",
        }

        attr = feature_map.get(feature)
        if attr:
            setattr(self._config, attr, False)
        return self

    def with_log_level(self, level: str) -> "ConfigBuilder":
        """Set log level"""
        self._config.log_level = level
        return self

    def with_data_dir(self, path: str) -> "ConfigBuilder":
        """Set data directory"""
        self._config.data_dir = path
        return self

    def build(self) -> TarlConfig:
        """Build the configuration"""
        return self._config


def quick_start(
    profile: str = "development", compliance: str | None = None, **overrides
) -> dict[str, Any]:
    """
    Quick start configuration - get started with one line

    Examples:
        # Development
        config = quick_start("development")

        # Production with EU compliance
        config = quick_start("production", compliance="eu_regulated")

        # Staging with custom workers
        config = quick_start("staging", workers=8)

    Args:
        profile: Deployment profile (development, staging, production, etc.)
        compliance: Compliance profile (healthcare, financial, eu_regulated, etc.)
        **overrides: Additional configuration overrides

    Returns:
        dict: Configuration dictionary ready for stack initialization
    """
    # Get base preset
    preset_method = getattr(ConfigPresets, profile, None)
    if not preset_method:
        raise ValueError(f"Unknown profile: {profile}")

    config = preset_method()

    # Apply compliance if specified
    if compliance:
        compliance_method = getattr(ConfigPresets, f"{compliance}_compliant", None)
        if compliance_method:
            config = compliance_method()
        else:
            # Set compliance profile directly
            try:
                config.compliance_profile = ComplianceProfile[compliance.upper()]
                config.require_attestations = True
                config.enable_compliance_enforcement = True
            except KeyError:
                pass

    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config.to_dict()


def print_preset_guide():
    """Print a guide to all available presets"""
    print("=" * 80)
    print("T.A.R.L. CONFIGURATION PRESETS")
    print("=" * 80)
    print()
    print("Get started quickly with opinionated defaults for your use case.")
    print()

    presets = [
        ("development", "Fast feedback, debugging enabled, minimal security"),
        ("testing", "Isolated, reproducible, deterministic execution"),
        ("staging", "Production-like, full features enabled"),
        ("production", "Optimized, secure, full features"),
        ("high_availability", "Maximum redundancy, high throughput"),
        ("low_resource", "Minimal memory/CPU footprint"),
        ("healthcare_compliant", "HIPAA + GDPR compliance"),
        ("financial_compliant", "SOC2 + PCI-DSS compliance"),
        ("eu_regulated", "EU AI Act + GDPR compliance"),
    ]

    for name, desc in presets:
        print(f"{name:25s} - {desc}")

    print()
    print("=" * 80)
    print()
    print("Quick Start Usage:")
    print()
    print("  from project_ai.tarl.integrations.config_presets import quick_start")
    print("  from project_ai.tarl.integrations import ExtendedTarlStackBox")
    print()
    print("  # One-line configuration")
    print("  config = quick_start('production', compliance='eu_regulated')")
    print("  stack = ExtendedTarlStackBox(config=config)")
    print()
    print("Advanced Usage:")
    print()
    print("  from project_ai.tarl.integrations.config_presets import ConfigBuilder")
    print()
    print("  # Fluent builder pattern")
    print("  config = (ConfigBuilder('production')")
    print("            .with_workers(16)")
    print("            .enable_feature('ai_provenance')")
    print("            .with_log_level('DEBUG')")
    print("            .build())")
    print()
    print("=" * 80)


if __name__ == "__main__":
    print_preset_guide()
