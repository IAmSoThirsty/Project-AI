"""
System Health Reporting Module

This module provides production-grade system health diagnostics and reporting:
- System metrics collection (CPU, memory, disk, platform info)
- Dependency scanning (installed packages with versions)
- YAML snapshot generation for machine-readable output
- PNG health report rendering for human consumption
- Cryptographic audit logging via AuditLog
- Configuration-driven collection with Config integration
- Automatic directory creation
- Robust error handling

Usage:
    # Programmatic usage
    from app.health.report import HealthReporter

    reporter = HealthReporter()
    success, snapshot_path, report_path = reporter.generate_full_report()

    # CLI usage
    python -m src.app.health.report
"""

import logging
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import psutil
import yaml

# Use non-interactive backend for server environments
matplotlib.use('Agg')

from app.core.config import get_config
from app.governance.audit_log import AuditLog

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_SNAPSHOT_DIR = Path(__file__).parent.parent.parent.parent / "data" / "health_snapshots"
DEFAULT_REPORT_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "assets"


class HealthReporter:
    """System health reporter with diagnostics, YAML snapshots, and PNG rendering.

    This class collects comprehensive system health information and outputs it in
    both machine-readable (YAML) and human-readable (PNG) formats, with full
    audit trail integration.

    Example:
        >>> reporter = HealthReporter()
        >>> success, snapshot_path, report_path = reporter.generate_full_report()
        >>> if success:
        ...     print(f"Report: {report_path}")
    """

    def __init__(
        self,
        snapshot_dir: Path | None = None,
        report_dir: Path | None = None,
        audit_log: AuditLog | None = None
    ):
        """Initialize the health reporter.

        Args:
            snapshot_dir: Directory for YAML snapshots (default: data/health_snapshots)
            report_dir: Directory for PNG reports (default: docs/assets)
            audit_log: Optional AuditLog instance (creates new if None)
        """
        # Load configuration
        self.config = get_config()

        # Set directories from config or defaults
        health_config = self.config.get_section("health")
        self.snapshot_dir = snapshot_dir or Path(health_config.get("snapshot_dir", DEFAULT_SNAPSHOT_DIR))
        self.report_dir = report_dir or Path(health_config.get("report_dir", DEFAULT_REPORT_DIR))

        # Create directories
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Initialize audit log
        self.audit_log = audit_log or AuditLog()

        logger.info(f"HealthReporter initialized: snapshots={self.snapshot_dir}, reports={self.report_dir}")

    def collect_system_metrics(self) -> dict[str, Any]:
        """Collect system-level metrics.

        Returns:
            Dictionary containing CPU, memory, disk, and platform information
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(logical=True),
                    "count_physical": psutil.cpu_count(logical=False),
                },
                "memory": {
                    "total_mb": memory.total / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024),
                    "used_mb": memory.used / (1024 * 1024),
                    "usage_percent": memory.percent,
                },
                "disk": {
                    "total_gb": disk.total / (1024 ** 3),
                    "used_gb": disk.used / (1024 ** 3),
                    "free_gb": disk.free / (1024 ** 3),
                    "usage_percent": disk.percent,
                },
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": sys.version,
                    "python_implementation": platform.python_implementation(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {"error": str(e)}

    def collect_dependencies(self) -> dict[str, str]:
        """Collect installed Python packages and versions.

        Returns:
            Dictionary mapping package names to versions
        """
        try:
            import pkg_resources

            dependencies = {}
            for package in pkg_resources.working_set:
                dependencies[package.project_name] = package.version

            return dependencies
        except Exception as e:
            logger.error(f"Failed to collect dependencies: {e}")
            return {"error": str(e)}

    def collect_config_summary(self) -> dict[str, Any]:
        """Collect summary of current configuration.

        Returns:
            Dictionary with configuration overview
        """
        try:
            return {
                "sections": list(self.config.config.keys()),
                "log_level": self.config.get("general", "log_level"),
                "ai_provider": self.config.get("ai", "provider"),
                "security_enabled": self.config.get("security", "enable_four_laws"),
            }
        except Exception as e:
            logger.error(f"Failed to collect config summary: {e}")
            return {"error": str(e)}

    def generate_yaml_snapshot(self) -> tuple[bool, Path | None]:
        """Generate a YAML snapshot of system health.

        Returns:
            Tuple of (success, snapshot_path)
        """
        try:
            # Collect all data based on config
            health_config = self.config.get_section("health")

            snapshot = {
                "generated_at": datetime.now(UTC).isoformat(),
                "version": "1.0.0",
            }

            if health_config.get("collect_system_metrics", True):
                snapshot["system_metrics"] = self.collect_system_metrics()

            if health_config.get("collect_dependencies", True):
                snapshot["dependencies"] = self.collect_dependencies()

            if health_config.get("collect_config_summary", True):
                snapshot["config_summary"] = self.collect_config_summary()

            # Generate snapshot filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_path = self.snapshot_dir / f"health_snapshot_{timestamp}.yaml"

            # Write YAML snapshot
            with open(snapshot_path, "w", encoding="utf-8") as f:
                yaml.dump(snapshot, f, default_flow_style=False, sort_keys=False)

            logger.info(f"YAML snapshot generated: {snapshot_path}")
            return True, snapshot_path

        except Exception as e:
            logger.error(f"Failed to generate YAML snapshot: {e}")
            return False, None

    def generate_png_report(self, snapshot_data: dict[str, Any]) -> tuple[bool, Path | None]:
        """Generate a PNG health report visualization.

        Args:
            snapshot_data: Health snapshot data dictionary

        Returns:
            Tuple of (success, report_path)
        """
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Project-AI System Health Report', fontsize=16, fontweight='bold')

            # Extract system metrics
            system_metrics = snapshot_data.get("system_metrics", {})
            cpu_data = system_metrics.get("cpu", {})
            memory_data = system_metrics.get("memory", {})
            disk_data = system_metrics.get("disk", {})
            platform_data = system_metrics.get("platform", {})

            # CPU Usage (top-left)
            ax1 = axes[0, 0]
            cpu_usage = cpu_data.get("usage_percent", 0)
            cpu_count = cpu_data.get("count", 0)
            ax1.barh(['CPU Usage'], [cpu_usage], color='#2ecc71' if cpu_usage < 70 else '#e74c3c')
            ax1.set_xlim(0, 100)
            ax1.set_xlabel('Usage (%)')
            ax1.set_title(f'CPU Usage ({cpu_count} cores)')
            ax1.grid(axis='x', alpha=0.3)

            # Memory Usage (top-right)
            ax2 = axes[0, 1]
            memory_usage = memory_data.get("usage_percent", 0)
            memory_total = memory_data.get("total_mb", 0) / 1024  # Convert to GB
            ax2.barh(['Memory Usage'], [memory_usage], color='#3498db' if memory_usage < 80 else '#e74c3c')
            ax2.set_xlim(0, 100)
            ax2.set_xlabel('Usage (%)')
            ax2.set_title(f'Memory Usage ({memory_total:.1f} GB total)')
            ax2.grid(axis='x', alpha=0.3)

            # Disk Usage (bottom-left)
            ax3 = axes[1, 0]
            disk_usage = disk_data.get("usage_percent", 0)
            disk_total = disk_data.get("total_gb", 0)
            ax3.barh(['Disk Usage'], [disk_usage], color='#9b59b6' if disk_usage < 85 else '#e74c3c')
            ax3.set_xlim(0, 100)
            ax3.set_xlabel('Usage (%)')
            ax3.set_title(f'Disk Usage ({disk_total:.1f} GB total)')
            ax3.grid(axis='x', alpha=0.3)

            # System Information (bottom-right)
            ax4 = axes[1, 1]
            ax4.axis('off')

            # Format system info text
            info_text = f"""
System Information:
─────────────────────────
OS: {platform_data.get('system', 'Unknown')} {platform_data.get('release', '')}
Machine: {platform_data.get('machine', 'Unknown')}
Python: {platform_data.get('python_implementation', 'Unknown')}
        {sys.version.split()[0]}

Generated: {snapshot_data.get('generated_at', 'Unknown')[:19]}

Status: {"✓ Healthy" if all([
    cpu_usage < 80,
    memory_usage < 85,
    disk_usage < 90
]) else "⚠ Attention Needed"}
            """

            ax4.text(0.1, 0.5, info_text, fontsize=10, family='monospace',
                    verticalalignment='center', transform=ax4.transAxes)

            plt.tight_layout()

            # Save to canonical path and timestamped path
            canonical_path = self.report_dir / "health_report.png"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_path = self.report_dir / f"health_report_{timestamp}.png"

            fig.savefig(canonical_path, dpi=100, bbox_inches='tight')
            fig.savefig(timestamped_path, dpi=100, bbox_inches='tight')
            plt.close(fig)

            logger.info(f"PNG report generated: {canonical_path}")
            return True, canonical_path

        except Exception as e:
            logger.error(f"Failed to generate PNG report: {e}")
            return False, None

    def generate_full_report(self) -> tuple[bool, Path | None, Path | None]:
        """Generate complete health report with YAML snapshot and PNG visualization.

        Returns:
            Tuple of (success, snapshot_path, report_path)
        """
        try:
            # Generate YAML snapshot
            snapshot_success, snapshot_path = self.generate_yaml_snapshot()
            if not snapshot_success:
                return False, None, None

            # Load snapshot data for PNG generation
            with open(snapshot_path, encoding="utf-8") as f:
                snapshot_data = yaml.safe_load(f)

            # Generate PNG report
            report_success, report_path = self.generate_png_report(snapshot_data)
            if not report_success:
                return False, snapshot_path, None

            # Log to audit
            self.audit_log.log_event(
                event_type="health_report_generated",
                data={
                    "snapshot_path": str(snapshot_path),
                    "report_path": str(report_path),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                description="System health report generated successfully"
            )

            logger.info(f"Full health report generated: snapshot={snapshot_path}, report={report_path}")
            return True, snapshot_path, report_path

        except Exception as e:
            logger.error(f"Failed to generate full report: {e}")

            # Log failure to audit
            self.audit_log.log_event(
                event_type="health_report_failed",
                data={"error": str(e)},
                description="System health report generation failed"
            )

            return False, None, None


def main():
    """CLI entry point for health report generation."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Project-AI System Health Reporter")
    print("=" * 60)
    print()

    # Create reporter and generate report
    reporter = HealthReporter()
    success, snapshot_path, report_path = reporter.generate_full_report()

    if success:
        print("✓ Health report generated successfully!")
        print()
        print(f"  Snapshot: {snapshot_path}")
        print(f"  Report:   {report_path}")
        print()

        # Verify audit log chain
        is_valid, message = reporter.audit_log.verify_chain()
        if is_valid:
            print(f"✓ Audit log chain verified: {message}")
        else:
            print(f"⚠ Audit log chain verification failed: {message}")
    else:
        print("✗ Health report generation failed!")
        print("  Check logs for details.")
        sys.exit(1)

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()


__all__ = ["HealthReporter"]
