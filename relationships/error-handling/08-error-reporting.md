# Error Reporting Relationship Map

**System:** Error Reporting  
**Mission:** Document error reporting mechanisms, external integrations, and incident notification systems  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Error Reporting Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Multi-Channel Error Reporting System                         │
│                                                               │
│  Channel 1: Internal Reporting                               │
│  ├─ Application logs (local files)                          │
│  ├─ Console output (development)                            │
│  ├─ In-memory error buffers                                 │
│  └─ System event logs                                       │
│                                                               │
│  Channel 2: User-Facing Reporting                           │
│  ├─ GUI error dialogs (QMessageBox)                        │
│  ├─ Status bar notifications                                │
│  ├─ In-app error panels                                     │
│  └─ Toast/snackbar messages                                 │
│                                                               │
│  Channel 3: Administrative Reporting                         │
│  ├─ Email alerts (SMTP)                                     │
│  ├─ Dashboard health indicators                             │
│  ├─ Audit log reports                                       │
│  └─ System health snapshots                                 │
│                                                               │
│  Channel 4: External Reporting (Future)                     │
│  ├─ Sentry/error tracking services                          │
│  ├─ Slack/Teams notifications                               │
│  ├─ PagerDuty/incident management                           │
│  └─ Metrics dashboards (Grafana)                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Internal Error Reporting

### Console/File Logging
**Primary Mechanism:** Python `logging` module  
**Locations:** All modules

**Error Report Format:**
```
2025-06-15 10:30:45,123 - app.core.ai_systems - ERROR - Failed to save persona state: [Errno 28] No space left on device
Traceback (most recent call last):
  File "/app/core/ai_systems.py", line 215, in _save_state
    json.dump(self.state, f, indent=2)
  File "/usr/lib/python3.11/json/__init__.py", line 179, in dump
    for chunk in iterable:
OSError: [Errno 28] No space left on device
```

**Components:**
- **Timestamp:** Precise error occurrence time
- **Logger name:** Source module identification
- **Level:** ERROR/CRITICAL severity
- **Message:** Human-readable description
- **Stack trace:** Full call stack for debugging

**Configuration:**
```python
# From config.py
"general": {
    "log_level": "INFO",  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    "data_dir": "data",
    "verbose": False,
}
```

---

### Structured Error Reports

**Implementation Pattern:**
```python
class ErrorReport:
    """Structured error report for analysis."""
    
    def __init__(
        self,
        error: Exception,
        context: dict[str, Any],
        severity: str = "ERROR"
    ):
        self.timestamp = datetime.now(timezone.utc)
        self.error_type = type(error).__name__
        self.error_message = str(error)
        self.context = context
        self.severity = severity
        self.stack_trace = traceback.format_exc()
        self.correlation_id = str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.error_type,
            "error_message": self.error_message,
            "context": self.context,
            "severity": self.severity,
            "stack_trace": self.stack_trace,
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
```

**Usage:**
```python
try:
    process_user_data(user_id)
except Exception as e:
    report = ErrorReport(
        error=e,
        context={
            "user_id": user_id,
            "operation": "data_processing",
            "module": "analytics",
            "input_size": len(data)
        },
        severity="CRITICAL" if isinstance(e, DataCorruptionError) else "ERROR"
    )
    
    # Log structured report
    logger.error("Error report: %s", report.to_json())
    
    # Store for analysis
    error_database.store(report.to_dict())
```

---

## User-Facing Error Reporting

### GUI Error Dialogs

**Primary Implementation:** `QMessageBox` (PyQt6)  
**Locations:** All GUI modules (80+ usage sites)

**Error Dialog Types:**

#### 1. Critical Errors
```python
QMessageBox.critical(
    parent,
    "Error",              # Title
    error_message         # Message
)
```

**Example:**
```python
try:
    save_configuration(config)
except Exception as e:
    QMessageBox.critical(
        self,
        "Configuration Error",
        f"Failed to save configuration:\n{str(e)}"
    )
```

**Visual:**
```
┌─────────────────────────────────┐
│ ⛔ Configuration Error          │
├─────────────────────────────────┤
│ Failed to save configuration:   │
│ [Errno 13] Permission denied:  │
│ '/etc/config.json'              │
│                                  │
│           [   OK   ]            │
└─────────────────────────────────┘
```

---

#### 2. Warning Dialogs
```python
QMessageBox.warning(
    parent,
    "Warning",
    warning_message
)
```

**Example:**
```python
if not user_authenticated:
    QMessageBox.warning(
        self,
        "Authorization Required",
        "You must be logged in to perform this action."
    )
```

**Visual:**
```
┌─────────────────────────────────┐
│ ⚠️ Authorization Required       │
├─────────────────────────────────┤
│ You must be logged in to        │
│ perform this action.            │
│                                  │
│           [   OK   ]            │
└─────────────────────────────────┘
```

---

#### 3. Information Dialogs
```python
QMessageBox.information(
    parent,
    "Success",
    success_message
)
```

**Example:**
```python
QMessageBox.information(
    self,
    "Operation Complete",
    "Data successfully synchronized to cloud."
)
```

---

### Status Bar Notifications

**Implementation:** `QStatusBar`

```python
# Temporary message (5 second timeout)
self.status_bar.showMessage(
    "⚠️ Image generation service temporarily unavailable",
    timeout=5000  # milliseconds
)

# Permanent status indicator
self.status_bar.showMessage("🔴 DEGRADED MODE")
```

**Use Cases:**
- Non-critical errors
- Degraded service notifications
- Temporary connectivity issues
- Background operation failures

---

### DashboardErrorHandler Integration

**Location:** `src/app/gui/dashboard_utils.py`

**Centralized Error Display:**
```python
class DashboardErrorHandler:
    @staticmethod
    def handle_exception(
        exception: Exception,
        context: str = "Operation",
        show_dialog: bool = True,
        parent=None,
    ) -> None:
        """
        Handle exception with logging and optional dialog.
        
        This provides consistent error reporting across GUI.
        """
        error_message = f"{context}: {str(exception)}"
        logger.error(error_message, exc_info=True)
        
        if show_dialog:
            QMessageBox.critical(parent, "Error", error_message)
```

**Consistent Usage Pattern:**
```python
# Throughout GUI code
try:
    perform_operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e,
        context="User Management",
        show_dialog=True,
        parent=self
    )
```

---

## Administrative Error Reporting

### Email Alerts

**Location:** `src/app/core/emergency_alert.py`

**Implementation:**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ErrorEmailReporter:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
    
    def send_error_report(
        self,
        to_addrs: list[str],
        error: Exception,
        context: dict
    ):
        """Send error report via email."""
        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = f"[CRITICAL] System Error: {type(error).__name__}"
        
        # Email body
        body = f"""
        Critical Error Detected
        
        Error Type: {type(error).__name__}
        Error Message: {str(error)}
        
        Context:
        {json.dumps(context, indent=2)}
        
        Timestamp: {datetime.now().isoformat()}
        
        Stack Trace:
        {traceback.format_exc()}
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info("Error report sent to: %s", to_addrs)
        except Exception as e:
            logger.error("Failed to send error report email: %s", e)
```

**Usage:**
```python
# Configuration from environment
email_reporter = ErrorEmailReporter(
    smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    username=os.getenv("SMTP_USERNAME"),
    password=os.getenv("SMTP_PASSWORD"),
    from_addr=os.getenv("SMTP_FROM", "errors@projectai.com")
)

# Send critical error report
try:
    critical_operation()
except Exception as e:
    logger.critical("Critical error: %s", e)
    
    # Send to administrators
    email_reporter.send_error_report(
        to_addrs=["admin@projectai.com"],
        error=e,
        context={
            "operation": "critical_operation",
            "user": current_user,
            "system_state": system.get_state()
        }
    )
```

**Triggers:**
- CRITICAL level errors
- Security violations
- Data corruption detected
- System integrity compromised

---

### Health Snapshot Reports

**Location:** `src/app/core/health_monitoring_continuity.py`

**Purpose:** Periodic system health reports

```python
class HealthSnapshotReporter:
    def generate_health_report(self) -> dict:
        """
        Generate comprehensive health report.
        
        Returns structured report of all system components.
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_health": self._calculate_overall_health(),
            "components": {
                component: monitor.get_health()
                for component, monitor in self.monitors.items()
            },
            "degraded_services": self._get_degraded_services(),
            "recent_errors": self._get_recent_errors(),
            "continuity_score": self._calculate_continuity_score(),
            "recommendations": self._generate_recommendations()
        }
    
    def save_snapshot(self, snapshot_dir: Path):
        """Save health snapshot to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"health_snapshot_{timestamp}.json"
        filepath = snapshot_dir / filename
        
        report = self.generate_health_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Health snapshot saved: %s", filepath)
```

**Scheduled Reporting:**
```python
# Run hourly health snapshots
schedule.every(1).hours.do(
    health_reporter.save_snapshot,
    snapshot_dir=Path("data/health_snapshots")
)
```

---

## External Error Reporting (Future)

### Sentry Integration (Planned)

**Configuration:**
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENV", "development"),
    traces_sample_rate=1.0,
    release=get_version()
)
```

**Automatic Error Capture:**
```python
try:
    operation()
except Exception as e:
    # Automatically captured by Sentry
    sentry_sdk.capture_exception(e)
    raise
```

**Custom Context:**
```python
with sentry_sdk.configure_scope() as scope:
    scope.set_context("user", {
        "id": user_id,
        "username": username,
        "role": user_role
    })
    scope.set_tag("component", "ai_systems")
    scope.set_tag("severity", "critical")
    
    # This exception will include all context
    raise CustomException("Operation failed")
```

---

### Slack/Teams Notifications (Planned)

**Implementation:**
```python
import requests

class SlackErrorReporter:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def report_error(
        self,
        error: Exception,
        severity: str,
        context: dict
    ):
        """Send error notification to Slack."""
        message = {
            "text": f":rotating_light: {severity} Error Detected",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity}: {type(error).__name__}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Error:*\n{str(error)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Context:*\n```{json.dumps(context, indent=2)}```"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            logger.error("Failed to send Slack notification: %s", e)
```

---

## Error Report Aggregation

### Error Database

**Purpose:** Centralized error storage for analysis

```python
import sqlite3

class ErrorDatabase:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                severity TEXT NOT NULL,
                module TEXT,
                context TEXT,
                stack_trace TEXT,
                correlation_id TEXT,
                resolved BOOLEAN DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def store_error(self, error_report: dict):
        """Store error report in database."""
        self.conn.execute("""
            INSERT INTO errors (
                timestamp, error_type, error_message, severity,
                module, context, stack_trace, correlation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            error_report["timestamp"],
            error_report["error_type"],
            error_report["error_message"],
            error_report["severity"],
            error_report.get("module"),
            json.dumps(error_report.get("context", {})),
            error_report.get("stack_trace"),
            error_report.get("correlation_id")
        ))
        self.conn.commit()
    
    def get_recent_errors(self, limit: int = 100) -> list[dict]:
        """Get recent errors."""
        cursor = self.conn.execute("""
            SELECT * FROM errors
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_error_statistics(self) -> dict:
        """Get error statistics."""
        cursor = self.conn.execute("""
            SELECT
                error_type,
                COUNT(*) as count,
                MAX(timestamp) as last_occurrence
            FROM errors
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY error_type
            ORDER BY count DESC
        """)
        
        return {
            "last_24_hours": [
                {
                    "error_type": row[0],
                    "count": row[1],
                    "last_occurrence": row[2]
                }
                for row in cursor.fetchall()
            ]
        }
```

---

## Error Report Triggers

### Automatic Triggers
1. **Exception Caught:** Every caught exception generates report
2. **CRITICAL Log Level:** All CRITICAL logs generate report
3. **Security Violation:** Security exceptions always reported
4. **Circuit Breaker Opens:** Component failure reported
5. **Health Check Failure:** Consecutive failures reported

### Manual Triggers
1. **User Report Button:** GUI "Report Issue" button
2. **Admin Dashboard:** Manual error report generation
3. **CLI Command:** `projectai report-error`

---

## Error Report Metrics

### Tracking
```python
class ErrorMetrics:
    def __init__(self):
        self.error_counts: dict[str, int] = defaultdict(int)
        self.error_timestamps: dict[str, list] = defaultdict(list)
    
    def record_error(self, error_type: str):
        self.error_counts[error_type] += 1
        self.error_timestamps[error_type].append(datetime.now())
    
    def get_error_rate(self, error_type: str, window_minutes: int = 60) -> float:
        """Get errors per minute for error type."""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        recent = [
            ts for ts in self.error_timestamps[error_type]
            if ts > cutoff
        ]
        return len(recent) / window_minutes
```

---

## Related Systems

**Dependencies:**
- [Error Logging](#07-error-logging.md) - Source of error data
- [User Feedback](#09-user-feedback.md) - User-facing reports
- [Exception Classes](#01-exception-hierarchy.md) - Reported errors
- [Error Handlers](#02-error-handlers.md) - Trigger reports

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
