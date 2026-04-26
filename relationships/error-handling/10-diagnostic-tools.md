# Diagnostic Tools Relationship Map

**System:** Diagnostic Tools  
**Mission:** Document debugging tools, error analysis utilities, and diagnostic capabilities  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## Diagnostic Tools Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Diagnostic Tools Hierarchy                                   │
│                                                               │
│  Tier 1: Built-in Python Tools                              │
│  ├─ Python logging module                                   │
│  ├─ Stack traces (traceback module)                         │
│  ├─ Exception inspection                                    │
│  └─ Python debugger (pdb)                                   │
│                                                               │
│  Tier 2: Custom Diagnostic Systems                          │
│  ├─ TraceLogger (causal chains)                             │
│  ├─ TamperproofLog (audit trail)                            │
│  ├─ Health monitoring                                       │
│  └─ Error database (sqlite)                                 │
│                                                               │
│  Tier 3: Analysis & Reporting Tools                         │
│  ├─ Health snapshots                                        │
│  ├─ Error statistics                                        │
│  ├─ Performance metrics                                     │
│  └─ System state dumps                                      │
│                                                               │
│  Tier 4: External Tools (Future)                            │
│  ├─ Sentry error tracking                                   │
│  ├─ Profiling tools                                         │
│  ├─ Distributed tracing                                     │
│  └─ APM integration                                         │
└──────────────────────────────────────────────────────────────┘
```

---

## Built-in Python Diagnostic Tools

### 1. Stack Trace Analysis

**Module:** `traceback`

**Basic Usage:**
```python
import traceback

try:
    risky_operation()
except Exception as e:
    # Get full stack trace
    stack_trace = traceback.format_exc()
    
    # Log with full context
    logger.error(
        "Operation failed: %s\n%s",
        str(e),
        stack_trace
    )
```

**Advanced Stack Analysis:**
```python
import traceback
import sys

def get_detailed_traceback() -> dict:
    """
    Extract detailed traceback information.
    
    Returns structured traceback data for analysis.
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    
    if not exc_tb:
        return {}
    
    # Extract all frames
    frames = []
    for frame_summary in traceback.extract_tb(exc_tb):
        frames.append({
            "filename": frame_summary.filename,
            "line_number": frame_summary.lineno,
            "function": frame_summary.name,
            "code": frame_summary.line
        })
    
    return {
        "exception_type": exc_type.__name__ if exc_type else None,
        "exception_message": str(exc_value),
        "frames": frames,
        "full_trace": traceback.format_exc()
    }

# Usage
try:
    operation()
except Exception:
    traceback_data = get_detailed_traceback()
    logger.error("Detailed traceback: %s", json.dumps(traceback_data, indent=2))
```

---

### 2. Exception Inspection

**Extract exception details:**
```python
import sys

def inspect_exception(exception: Exception) -> dict:
    """
    Extract comprehensive exception information.
    
    Returns:
        Dictionary with exception details for diagnostics.
    """
    return {
        "type": type(exception).__name__,
        "message": str(exception),
        "args": exception.args,
        "attributes": {
            key: value
            for key, value in vars(exception).items()
            if not key.startswith("_")
        },
        "cause": (
            inspect_exception(exception.__cause__)
            if exception.__cause__ else None
        ),
        "context": (
            inspect_exception(exception.__context__)
            if exception.__context__ else None
        ),
        "traceback": traceback.format_exc()
    }

# Usage
try:
    operation()
except Exception as e:
    details = inspect_exception(e)
    logger.error("Exception details: %s", json.dumps(details, indent=2))
```

**Example Output:**
```json
{
    "type": "SecurityViolationException",
    "message": "Operation blocked by security gateway",
    "args": [],
    "attributes": {
        "operation_id": "OP-12345",
        "reason": "Violates FourLaws hierarchy",
        "threat_level": "CRITICAL",
        "enforcement_actions": ["BLOCK", "LOG", "ALERT"]
    },
    "cause": null,
    "context": null,
    "traceback": "..."
}
```

---

### 3. Python Debugger (pdb)

**Interactive Debugging:**
```python
import pdb

def problematic_function():
    # Set breakpoint
    pdb.set_trace()  # Execution stops here
    
    # When execution reaches here, you get interactive shell:
    # (Pdb) print(variable)
    # (Pdb) next  # Execute next line
    # (Pdb) step  # Step into function
    # (Pdb) continue  # Resume execution
    
    result = complex_calculation()
    return result
```

**Post-Mortem Debugging:**
```python
import pdb
import sys

try:
    problematic_operation()
except Exception:
    # Drop into debugger at exception point
    pdb.post_mortem(sys.exc_info()[2])
```

---

## Custom Diagnostic Systems

### 1. TraceLogger - Causal Chain Analysis

**Location:** `src/app/audit/trace_logger.py`

**Purpose:** Trace decision-making processes for debugging AI systems

**Diagnostic Usage:**
```python
# Initialize tracer
tracer = TraceLogger(storage_path="diagnostics/traces")

# Start trace for operation
trace_id = tracer.start_trace(
    operation="ai_decision",
    context={
        "user_input": user_message,
        "persona_state": persona.get_state(),
        "timestamp": datetime.now().isoformat()
    }
)

# Log each decision step
tracer.log_step(
    trace_id,
    step_name="input_validation",
    data={"valid": True, "sanitized": sanitized_input}
)

tracer.log_step(
    trace_id,
    step_name="four_laws_check",
    data={"allowed": True, "laws_evaluated": 4}
)

tracer.log_step(
    trace_id,
    step_name="ai_inference",
    data={
        "model": "gpt-3.5-turbo",
        "tokens": 150,
        "latency_ms": 450
    }
)

# Complete trace
tracer.complete_trace(
    trace_id,
    result={"response": ai_response, "success": True}
)

# Later: Analyze trace
trace = tracer.get_trace(trace_id)
logger.info("Trace analysis: %s", json.dumps(trace, indent=2))
```

**Analysis Capabilities:**
```python
class TraceAnalyzer:
    def __init__(self, tracer: TraceLogger):
        self.tracer = tracer
    
    def find_bottlenecks(self, trace_id: str) -> list[dict]:
        """Identify performance bottlenecks in trace."""
        trace = self.tracer.get_trace(trace_id)
        steps = trace["steps"]
        
        bottlenecks = []
        for i in range(len(steps) - 1):
            duration = self._calculate_duration(steps[i], steps[i+1])
            if duration > 1000:  # > 1 second
                bottlenecks.append({
                    "step": steps[i]["name"],
                    "duration_ms": duration,
                    "data": steps[i]["data"]
                })
        
        return bottlenecks
    
    def find_failure_paths(self) -> list[dict]:
        """Find traces that resulted in failures."""
        return [
            trace for trace in self.tracer.traces.values()
            if trace.get("status") == "failed"
        ]
```

---

### 2. Health Monitoring Diagnostics

**Location:** `src/app/core/health_monitoring_continuity.py`

**Diagnostic Capabilities:**

#### Component Health Analysis
```python
class HealthDiagnostics:
    def __init__(self, monitoring_system):
        self.monitoring = monitoring_system
    
    def diagnose_component(self, component: str) -> dict:
        """
        Comprehensive component diagnostics.
        
        Returns:
            Diagnostic report with health history and recommendations.
        """
        monitor = self.monitoring.monitors.get(component)
        if not monitor:
            return {"error": "Component not found"}
        
        # Get health history
        history = list(monitor.health_checks)
        
        # Analyze patterns
        recent_failures = sum(
            1 for check in history[-10:]
            if check.status != HealthStatus.HEALTHY.value
        )
        
        failure_rate = recent_failures / min(len(history), 10)
        
        # Identify trends
        trend = self._analyze_trend(history)
        
        return {
            "component": component,
            "current_status": monitor.last_status.value,
            "consecutive_failures": monitor.consecutive_failures,
            "consecutive_successes": monitor.consecutive_successes,
            "recent_failure_rate": failure_rate,
            "trend": trend,
            "recommendations": self._generate_recommendations(
                component, failure_rate, trend
            ),
            "history": [
                {
                    "timestamp": check.timestamp,
                    "status": check.status,
                    "response_time_ms": check.response_time_ms,
                    "error": check.error_message
                }
                for check in history[-20:]  # Last 20 checks
            ]
        }
    
    def _analyze_trend(self, history: list) -> str:
        """Analyze health trend."""
        if len(history) < 5:
            return "insufficient_data"
        
        recent = history[-5:]
        healthy_count = sum(
            1 for check in recent
            if check.status == HealthStatus.HEALTHY.value
        )
        
        if healthy_count == 5:
            return "stable_healthy"
        elif healthy_count == 0:
            return "persistent_failure"
        elif healthy_count > healthy_count:
            return "improving"
        else:
            return "degrading"
    
    def _generate_recommendations(
        self,
        component: str,
        failure_rate: float,
        trend: str
    ) -> list[str]:
        """Generate diagnostic recommendations."""
        recommendations = []
        
        if failure_rate > 0.5:
            recommendations.append(
                "High failure rate detected - consider restarting component"
            )
        
        if trend == "degrading":
            recommendations.append(
                "Health is degrading - investigate resource usage"
            )
        elif trend == "persistent_failure":
            recommendations.append(
                "Component persistently failing - manual intervention needed"
            )
        
        return recommendations
```

**Usage:**
```python
diagnostics = HealthDiagnostics(health_monitoring_system)

# Diagnose specific component
report = diagnostics.diagnose_component("database")

logger.info("Diagnostic report:\n%s", json.dumps(report, indent=2))

# If issues detected
if report["recent_failure_rate"] > 0.3:
    logger.warning(
        "Component %s showing issues. Recommendations: %s",
        "database",
        report["recommendations"]
    )
```

---

### 3. Error Database Analysis

**Purpose:** Aggregate and analyze error patterns

**Implementation:**
```python
import sqlite3
from collections import Counter

class ErrorAnalyzer:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
    
    def get_error_statistics(
        self,
        time_window_hours: int = 24
    ) -> dict:
        """
        Analyze error patterns in time window.
        
        Returns:
            Statistical analysis of errors.
        """
        cursor = self.conn.execute("""
            SELECT
                error_type,
                severity,
                module,
                timestamp
            FROM errors
            WHERE timestamp > datetime('now', '-{} hours')
        """.format(time_window_hours))
        
        errors = cursor.fetchall()
        
        # Count by type
        error_types = Counter(error[0] for error in errors)
        
        # Count by module
        modules = Counter(error[2] for error in errors)
        
        # Count by severity
        severities = Counter(error[1] for error in errors)
        
        # Calculate error rate over time
        hourly_rates = self._calculate_hourly_rates(errors)
        
        return {
            "total_errors": len(errors),
            "time_window_hours": time_window_hours,
            "error_types": dict(error_types.most_common(10)),
            "affected_modules": dict(modules.most_common(10)),
            "severity_distribution": dict(severities),
            "hourly_error_rate": hourly_rates,
            "top_error": error_types.most_common(1)[0] if error_types else None
        }
    
    def find_correlated_errors(self, error_type: str) -> list[str]:
        """
        Find errors that occur together with specified error type.
        
        Useful for identifying cascading failures.
        """
        cursor = self.conn.execute("""
            SELECT DISTINCT e2.error_type
            FROM errors e1
            JOIN errors e2 ON 
                ABS(STRFTIME('%s', e1.timestamp) - STRFTIME('%s', e2.timestamp)) < 60
            WHERE e1.error_type = ?
            AND e2.error_type != ?
        """, (error_type, error_type))
        
        return [row[0] for row in cursor.fetchall()]
    
    def detect_error_spikes(self) -> list[dict]:
        """
        Detect unusual error rate spikes.
        
        Returns list of spike events with context.
        """
        # Get hourly error counts
        cursor = self.conn.execute("""
            SELECT
                STRFTIME('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as count
            FROM errors
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY hour
            ORDER BY hour
        """)
        
        hourly_counts = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # Calculate average and standard deviation
        counts = [count for _, count in hourly_counts]
        avg = sum(counts) / len(counts)
        std_dev = (sum((x - avg) ** 2 for x in counts) / len(counts)) ** 0.5
        
        # Detect spikes (> 2 standard deviations above mean)
        threshold = avg + (2 * std_dev)
        
        spikes = [
            {
                "timestamp": hour,
                "error_count": count,
                "threshold": threshold,
                "severity": "high" if count > avg + (3 * std_dev) else "medium"
            }
            for hour, count in hourly_counts
            if count > threshold
        ]
        
        return spikes
```

**Usage:**
```python
analyzer = ErrorAnalyzer("data/errors.db")

# Get statistics
stats = analyzer.get_error_statistics(time_window_hours=24)
logger.info("Error statistics (last 24h):\n%s", json.dumps(stats, indent=2))

# Find correlated errors
if stats["top_error"]:
    correlated = analyzer.find_correlated_errors(stats["top_error"][0])
    logger.info(
        "Errors correlated with %s: %s",
        stats["top_error"][0],
        correlated
    )

# Detect spikes
spikes = analyzer.detect_error_spikes()
if spikes:
    logger.warning("Error spikes detected: %s", json.dumps(spikes, indent=2))
```

---

## System State Diagnostics

### 1. State Snapshot Tool

**Purpose:** Capture complete system state for post-mortem analysis

```python
import psutil
import platform

class SystemStateDumper:
    def capture_snapshot(self) -> dict:
        """
        Capture comprehensive system state snapshot.
        
        Returns:
            Complete system state for diagnostics.
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_info": self._get_system_info(),
            "process_info": self._get_process_info(),
            "resource_usage": self._get_resource_usage(),
            "application_state": self._get_application_state(),
            "recent_errors": self._get_recent_errors(),
            "health_status": self._get_health_status(),
            "configuration": self._get_configuration()
        }
    
    def _get_system_info(self) -> dict:
        """Get system information."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    def _get_process_info(self) -> dict:
        """Get current process information."""
        process = psutil.Process()
        
        return {
            "pid": process.pid,
            "status": process.status(),
            "create_time": datetime.fromtimestamp(
                process.create_time()
            ).isoformat(),
            "num_threads": process.num_threads(),
            "cpu_affinity": process.cpu_affinity() if hasattr(process, 'cpu_affinity') else None
        }
    
    def _get_resource_usage(self) -> dict:
        """Get resource usage statistics."""
        process = psutil.Process()
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_info": {
                "rss": process.memory_info().rss,
                "vms": process.memory_info().vms,
                "rss_mb": process.memory_info().rss / (1024 ** 2),
                "percent": process.memory_percent()
            },
            "system_cpu_percent": psutil.cpu_percent(interval=0.1),
            "system_memory": {
                "total_gb": psutil.virtual_memory().total / (1024 ** 3),
                "available_gb": psutil.virtual_memory().available / (1024 ** 3),
                "percent_used": psutil.virtual_memory().percent
            },
            "disk_usage": {
                partition.mountpoint: {
                    "total_gb": psutil.disk_usage(partition.mountpoint).total / (1024 ** 3),
                    "used_gb": psutil.disk_usage(partition.mountpoint).used / (1024 ** 3),
                    "free_gb": psutil.disk_usage(partition.mountpoint).free / (1024 ** 3),
                    "percent": psutil.disk_usage(partition.mountpoint).percent
                }
                for partition in psutil.disk_partitions()
            }
        }
    
    def _get_application_state(self) -> dict:
        """Get application-specific state."""
        return {
            "operating_mode": getattr(app_state, 'operating_mode', 'unknown'),
            "active_users": len(getattr(app_state, 'active_sessions', [])),
            "enabled_features": getattr(app_state, 'enabled_features', []),
            "circuit_breakers": {
                name: breaker.state
                for name, breaker in getattr(
                    app_state, 'circuit_breakers', {}
                ).items()
            }
        }
    
    def save_snapshot(self, output_dir: Path):
        """Save snapshot to file."""
        snapshot = self.capture_snapshot()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"state_snapshot_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        logger.info("State snapshot saved: %s", filepath)
        return filepath
```

**Usage:**
```python
dumper = SystemStateDumper()

# On critical error
try:
    critical_operation()
except Exception as e:
    logger.critical("Critical error - capturing state snapshot")
    snapshot_path = dumper.save_snapshot(Path("diagnostics/snapshots"))
    logger.critical("Snapshot saved: %s", snapshot_path)
    raise
```

---

## Diagnostic Commands (CLI)

### Health Check Command
```python
# src/app/cli/hydra_50_cli.py
import typer

@app.command()
def diagnose(
    component: str = typer.Option(None, help="Component to diagnose"),
    verbose: bool = typer.Option(False, help="Verbose output")
):
    """Run system diagnostics."""
    
    if component:
        # Diagnose specific component
        diagnostics = HealthDiagnostics(health_system)
        report = diagnostics.diagnose_component(component)
        
        typer.echo(f"\n=== Diagnostic Report: {component} ===")
        typer.echo(f"Status: {report['current_status']}")
        typer.echo(f"Failure Rate: {report['recent_failure_rate']:.1%}")
        typer.echo(f"Trend: {report['trend']}")
        
        if report['recommendations']:
            typer.echo("\nRecommendations:")
            for rec in report['recommendations']:
                typer.echo(f"  • {rec}")
    else:
        # Full system diagnostics
        dumper = SystemStateDumper()
        snapshot = dumper.capture_snapshot()
        
        typer.echo("\n=== System Diagnostics ===")
        typer.echo(f"CPU Usage: {snapshot['resource_usage']['system_cpu_percent']}%")
        typer.echo(f"Memory Usage: {snapshot['resource_usage']['system_memory']['percent_used']}%")
        typer.echo(f"Operating Mode: {snapshot['application_state']['operating_mode']}")
        
        if verbose:
            typer.echo(f"\nFull report:\n{json.dumps(snapshot, indent=2)}")
```

---

## Related Systems

**Dependencies:**
- [Error Logging](#07-error-logging.md) - Source of diagnostic data
- [Health Monitoring](#src/app/core/health_monitoring_continuity.py) - Health diagnostics
- [Trace Logger](#src/app/audit/trace_logger.py) - Decision tracing
- [Error Database](#08-error-reporting.md) - Error analysis

**Integration Points:**
- Python logging provides base diagnostics
- TraceLogger enables decision analysis
- Health monitoring provides component diagnostics
- Error database enables pattern analysis

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
