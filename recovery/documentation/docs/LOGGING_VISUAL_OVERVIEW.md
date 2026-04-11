# 🏗️ Logging Architecture - Visual Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │  Main App    │  │ Microservices│  │   Workers    │  │    APIs      ││
│  │  (FastAPI)   │  │  (8 services)│  │  (Temporal)  │  │  (REST)      ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
│         │                 │                 │                 │         │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                                     │                                    │
└─────────────────────────────────────┼────────────────────────────────────┘
                                      │
                        ┌─────────────▼────────────┐
                        │   LOGGING LAYER          │
                        │   (config/logging_*.py)  │
                        │                          │
                        │  ✓ JSON Formatter        │
                        │  ✓ Correlation IDs       │
                        │  ✓ Security Redaction    │
                        │  ✓ PII Protection        │
                        └─────────────┬────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
    ┌─────▼─────┐            ┌────────▼────────┐         ┌───────▼──────┐
    │  Console  │            │   File Logs     │         │    Loki      │
    │  (stdout) │            │   (Rotating)    │         │ (Centralized)│
    └───────────┘            └────────┬────────┘         └───────┬──────┘
                                      │                          │
                             ┌────────▼─────────┐        ┌───────▼──────┐
                             │  Log Rotation    │        │  Promtail    │
                             │  • 7yr audit     │        │  (Shipper)   │
                             │  • Daily gzip    │        └───────┬──────┘
                             │  • Size limits   │                │
                             └──────────────────┘        ┌───────▼──────┐
                                                         │   Grafana    │
                                                         │ (Dashboard)  │
                                                         └──────────────┘
```

## Log Flow Diagram

```
Request → Application → Logger → Filters → Formatters → Handlers → Destinations
   │                       │         │          │           │            │
   │                       │         │          │           │            ├─→ Console
   │                       │         │          │           │            ├─→ app.log
   │                       │         │          │           │            ├─→ error.log
   │                       │         │          │           │            ├─→ audit.log
   │                       │         │          │           │            ├─→ metrics.log
   │                       │         │          │           │            └─→ Loki
   │                       │         │          │           │
   │                       │         │          │           └─→ RotatingFileHandler
   │                       │         │          │               TimedRotatingFileHandler
   │                       │         │          │
   │                       │         │          └─→ JSONFormatter
   │                       │         │              StructuredFormatter
   │                       │         │              AuditFormatter
   │                       │         │
   │                       │         └─→ CorrelationFilter
   │                       │             SecurityRedactionFilter
   │                       │             PIIRedactionFilter
   │                       │
   │                       └─→ Logger
   │                           (app.core, app.security, app.audit, etc.)
   │
   └─→ Correlation ID
       User Context
       Request Metadata
```

## File Structure

```
Sovereign-Governance-Substrate/
│
├── config/                          # Logging Configuration
│   ├── logging.yml                  # Main YAML config (5.1 KB)
│   ├── logging_config.py            # Setup module (10 KB)
│   ├── logging_formatters.py        # Formatters (4.9 KB)
│   ├── logging_filters.py           # Filters (5.2 KB)
│   ├── logrotate.conf               # Linux rotation (2.5 KB)
│   ├── logrotate.ps1                # Windows rotation (3.7 KB)
│   ├── loki-config.yml              # Loki config (2.2 KB)
│   └── promtail-config.yml          # Promtail config (5.9 KB)
│
├── logs/                            # Log Files
│   ├── app.log                      # Main logs (1 year)
│   ├── error.log                    # Errors (2 years)
│   ├── audit/
│   │   └── audit.log                # Audit trail (7 YEARS) ⚠️
│   ├── metrics/
│   │   └── metrics.log              # Performance (30 days)
│   ├── debug/
│   │   └── debug.log                # Debug (7 days)
│   ├── access/
│   │   └── access.log               # API access (90 days)
│   └── microservices/
│       ├── firewall.log
│       ├── incident.log
│       └── *.log
│
├── docker-compose.logging.yml       # Centralized stack (2.7 KB)
│
├── examples/
│   └── logging_example.py           # Usage examples (2.8 KB)
│
├── tests/
│   └── test_logging_integration.py  # Test suite (8 KB)
│
└── Documentation/
    ├── LOGGING_ARCHITECTURE_REPORT.md      (18.8 KB)
    ├── LOGGING_CONFIGURATION.md            (21.4 KB)
    ├── LOGGING_DEPLOYMENT_CHECKLIST.md     (11.8 KB)
    └── LOGGING_MISSION_COMPLETE.md         (15.9 KB)
```

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. APPLICATION GENERATES LOG                                     │
│    logger.info("User action", extra={'user_id': '123'})         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 2. FILTERS PROCESS                                               │
│    • CorrelationFilter adds request ID                          │
│    • SecurityRedactionFilter masks credentials                  │
│    • PIIRedactionFilter removes sensitive data                  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 3. FORMATTER STRUCTURES                                          │
│    {                                                             │
│      "timestamp": "2026-04-09T14:23:45.123Z",                   │
│      "level": "INFO",                                            │
│      "message": "User action",                                   │
│      "correlation_id": "req-abc123",                            │
│      "user_id": "123"                                            │
│    }                                                             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 4. HANDLERS DISTRIBUTE                                           │
│    • Console → stdout (for Docker)                              │
│    • RotatingFileHandler → logs/app.log                         │
│    • TimedRotatingFileHandler → logs/audit/audit.log            │
│    • StreamHandler → Loki (via Promtail)                        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│ 5. ROTATION & STORAGE                                            │
│    • Daily rotation at midnight                                  │
│    • Compression with gzip (70% reduction)                       │
│    • Retention per policy (7 years for audit)                   │
│    • Old logs → /archive or cold storage                         │
└──────────────────────────────────────────────────────────────────┘
```

## Retention Timeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LOG RETENTION TIMELINE                          │
└─────────────────────────────────────────────────────────────────────┘

Debug Logs:
[■■■■■■■] 7 days
└─ Deleted after 7 days

Metrics Logs:
[■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 30 days
└─ Deleted after 30 days

Access Logs:
[■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 90 days
└─ Deleted after 90 days

Application Logs:
[████████████████████████████████████████████████████████████] 365 days (1 year)
└─ Deleted after 1 year

Error Logs:
[████████████████████████████████████████████████████████████████████████] 730 days (2 years)
└─ Deleted after 2 years

AUDIT LOGS: ⚠️ CRITICAL
[██████████████████████████████████████████████████████████████████████████████████████████████████████████] 2,555 days (7 YEARS)
└─ IMMUTABLE - Compliance requirement
└─ NEVER auto-delete without legal approval
└─ Compressed, checksummed, archived
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                    User Request Flow                           │
└────────────────────────────────────────────────────────────────┘

HTTP Request
    │
    ├─→ API Gateway
    │       │
    │       ├─→ Generate Correlation ID
    │       │       │
    │       │       └─→ set_correlation_id("req-xyz")
    │       │
    │       └─→ Route to Service
    │               │
    │               ├─→ Service Logic
    │               │       │
    │               │       ├─→ logger.info("Processing")
    │               │       │       └─→ Includes correlation_id automatically
    │               │       │
    │               │       ├─→ Database Query
    │               │       │       └─→ audit.log_data_access(...)
    │               │       │
    │               │       └─→ Business Logic
    │               │               └─→ logger.debug("Step complete")
    │               │
    │               ├─→ Response
    │               │       └─→ perf.log_request(duration_ms=45)
    │               │
    │               └─→ Error Handling
    │                       └─→ logger.error("Failed", exc_info=True)
    │
    └─→ Response to Client

All logs contain correlation_id → Can trace entire request flow
```

## Deployment Workflow

```
┌───────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PROCESS                             │
└───────────────────────────────────────────────────────────────────┘

1. PRE-DEPLOYMENT
   ├─ Install dependencies (pip install python-json-logger pyyaml)
   ├─ Create log directories (mkdir -p logs/{audit,metrics,...})
   ├─ Test configuration (python tests/test_logging_integration.py)
   └─ Review documentation

2. DEPLOYMENT
   ├─ Update application
   │  └─ Add: from config.logging_config import setup_logging
   │          setup_logging()
   │
   ├─ Configure log rotation
   │  ├─ Linux: sudo cp config/logrotate.conf /etc/logrotate.d/
   │  └─ Windows: Setup Task Scheduler (logrotate.ps1)
   │
   └─ Start centralized logging (optional)
      └─ docker-compose -f docker-compose.logging.yml up -d

3. VERIFICATION
   ├─ Check logs created (ls -lh logs/)
   ├─ Verify JSON format (head -1 logs/app.log | python -m json.tool)
   ├─ Test correlation IDs (grep correlation_id logs/app.log)
   ├─ Verify redaction (grep password logs/app.log → [REDACTED])
   └─ Query in Grafana (http://localhost:3001)

4. POST-DEPLOYMENT
   ├─ Monitor disk usage (df -h /app/logs)
   ├─ Verify rotation working (ls logs/app.log-*)
   ├─ Setup alerts (Prometheus + AlertManager)
   └─ Train team on log access

```

## Quick Reference Card

```
╔════════════════════════════════════════════════════════════════╗
║                   LOGGING QUICK REFERENCE                      ║
╠════════════════════════════════════════════════════════════════╣
║ SETUP                                                          ║
║   from config.logging_config import setup_logging             ║
║   setup_logging()                                              ║
║                                                                ║
║ BASIC LOGGING                                                  ║
║   logger = get_logger(__name__)                               ║
║   logger.info("Message", extra={'key': 'value'})              ║
║                                                                ║
║ CORRELATION IDs                                                ║
║   set_correlation_id(f"req-{uuid.uuid4()}")                   ║
║   # All logs now include correlation_id                       ║
║                                                                ║
║ AUDIT LOGGING                                                  ║
║   audit = get_audit_logger()                                  ║
║   audit.log_access(user_id, resource, action, outcome)        ║
║                                                                ║
║ PERFORMANCE                                                    ║
║   perf = get_performance_logger()                             ║
║   perf.log_request(endpoint, method, duration_ms, status)     ║
║                                                                ║
║ LOG LOCATIONS                                                  ║
║   logs/app.log          - Application (1 year)                ║
║   logs/error.log        - Errors (2 years)                    ║
║   logs/audit/audit.log  - Audit (7 YEARS) ⚠️                  ║
║   logs/metrics/         - Performance (30 days)               ║
║   logs/access/          - API access (90 days)                ║
║                                                                ║
║ QUERY LOGS (Grafana)                                           ║
║   {job="sovereign-app"}                                       ║
║   {job="sovereign-app"} | json | correlation_id="req-xyz"     ║
║                                                                ║
║ ENVIRONMENT VARIABLES                                          ║
║   LOG_LEVEL=INFO    # DEBUG, INFO, WARNING, ERROR             ║
║   LOG_JSON=true     # true for production                     ║
║   LOG_DIR=logs      # Log directory                           ║
╚════════════════════════════════════════════════════════════════╝
```

---

**Visual Overview Complete** | Version 1.0.0 | 2026-04-09
