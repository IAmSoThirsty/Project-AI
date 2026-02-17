# Project-AI Main Page

Welcome to **Project-AI** — a comprehensive, production-grade AI assistant platform with advanced security, governance, and health monitoring capabilities.

## Quick Links

- [Documentation Home](README.md)
- [Architecture Overview](architecture/)
- [Developer Guides](developer/)
- [Security & Compliance](security_compliance/)

## System Health

Project-AI includes a comprehensive health monitoring and reporting system that provides real-time visibility into system status, resource utilization, and operational health.

### Health Report

The latest system health report provides diagnostic information including:

- **CPU Usage**: Current processor utilization and core count
- **Memory Usage**: RAM consumption and availability
- **Disk Usage**: Storage capacity and free space
- **Platform Information**: Operating system, Python version, and system architecture
- **Dependencies**: Installed packages and versions
- **Configuration**: Active configuration settings

**[View Latest Health Report](assets/health_report.png)**

### Health Snapshots

Detailed health snapshots are available in YAML format at `data/health_snapshots/` for programmatic access and historical tracking.

### Generating Health Reports

To generate a new health report, run:

```bash

# Using the CLI

python -m src.app health report

# Or directly via the module

python -m src.app.health.report
```

This will:

1. Collect system diagnostics (CPU, memory, disk, platform info)
1. Scan installed dependencies
1. Generate a timestamped YAML snapshot in `data/health_snapshots/`
1. Create a PNG visualization in `docs/assets/`
1. Log the event to the cryptographic audit log

### Audit Trail

All health report generation events are logged to the cryptographic audit log (`governance/audit_log.yaml`) with SHA-256 chaining for tamper detection.

Verify the audit log integrity:

```bash
python -m src.app health verify-audit
```

## Configuration

Health reporting is configurable via TOML configuration files or environment variables:

```toml
[health]
collect_system_metrics = true
collect_dependencies = true
collect_config_summary = true
snapshot_dir = "data/health_snapshots"
report_dir = "docs/assets"
```

Environment variables:

- `PROJECTAI_HEALTH_COLLECT_SYSTEM_METRICS`
- `PROJECTAI_HEALTH_COLLECT_DEPENDENCIES`
- `PROJECTAI_HEALTH_SNAPSHOT_DIR`
- `PROJECTAI_HEALTH_REPORT_DIR`

## Architecture Integration

The health reporting system integrates with Project-AI's core architecture:

- **Config Module** (`src/app/core/config.py`): Configuration-driven collection
- **Audit Log** (`src/app/governance/audit_log.py`): Cryptographic event logging with SHA-256 chaining
- **Health Reporter** (`src/app/health/report.py`): System diagnostics and report generation
- **CLI** (`src/app/cli.py`): Command-line interface for health operations

## Features

### Production-Grade Quality

- ✅ **Comprehensive Diagnostics**: CPU, memory, disk, platform, dependencies
- ✅ **Multiple Output Formats**: YAML snapshots for machines, PNG reports for humans
- ✅ **Cryptographic Audit Trail**: SHA-256-chained audit log for tamper detection
- ✅ **Configuration Integration**: Fully configurable via TOML or environment variables
- ✅ **Automatic Directory Creation**: No manual setup required
- ✅ **Robust Error Handling**: Graceful degradation with detailed logging
- ✅ **CLI Integration**: Simple command-line interface

### Canonical Asset Management

The health report follows Project-AI's canonical asset pattern:

- **Canonical Path**: `docs/assets/health_report.png` (always the latest report)
- **Timestamped Archives**: `docs/assets/health_report_YYYYMMDD_HHMMSS.png` (historical tracking)
- **YAML Snapshots**: `data/health_snapshots/health_snapshot_YYYYMMDD_HHMMSS.yaml` (machine-readable archives)

## Security & Governance

The health reporting system adheres to Project-AI's security and governance standards:

1. **Audit Logging**: Every report generation is logged with cryptographic chaining
1. **Chain Verification**: Detect any tampering attempts via `verify-audit` command
1. **No Sensitive Data**: Health reports exclude sensitive configuration values
1. **Append-Only Logs**: Audit logs are append-only for forensic integrity
1. **Structured Output**: YAML format ensures parsability and tool compatibility

## Next Steps

- [Read the Full Documentation](README.md)
- [Explore the Architecture](architecture/)
- [Review Security Policies](security_compliance/)
- [Contribute to the Project](developer/CONTRIBUTING.md)

______________________________________________________________________

**Project-AI** — Building safe, transparent, and accountable AI systems.
