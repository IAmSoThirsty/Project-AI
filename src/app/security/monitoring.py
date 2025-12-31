"""Security monitoring and alerting integration.

This module implements:
- AWS CloudWatch integration for metrics
- AWS SNS for threat alerting
- Structured audit logging
- Versioning and incident detection
- Threat campaign signatures
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available - CloudWatch/SNS features disabled")


@dataclass
class SecurityEvent:
    """Security event data structure."""

    event_type: str
    severity: str  # critical, high, medium, low
    source: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "severity": self.severity,
            "source": self.source,
            "description": self.description,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class SecurityMonitor:
    """Security monitoring with AWS CloudWatch and SNS integration."""

    def __init__(
        self,
        region: str = "us-east-1",
        sns_topic_arn: Optional[str] = None,
        cloudwatch_namespace: str = "ProjectAI/Security",
    ):
        """Initialize security monitor.

        Args:
            region: AWS region
            sns_topic_arn: SNS topic ARN for alerts
            cloudwatch_namespace: CloudWatch namespace
        """
        self.region = region
        self.sns_topic_arn = sns_topic_arn
        self.cloudwatch_namespace = cloudwatch_namespace

        self.event_log: List[SecurityEvent] = []
        self.threat_signatures: Dict[str, List[str]] = {}

        if BOTO3_AVAILABLE:
            self.cloudwatch = boto3.client("cloudwatch", region_name=region)
            self.sns = boto3.client("sns", region_name=region)
        else:
            self.cloudwatch = None
            self.sns = None
            logger.warning("boto3 not available - using local logging only")

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Log security event and send alerts if needed.

        Args:
            event_type: Type of event (e.g., 'authentication_failure')
            severity: Event severity (critical, high, medium, low)
            source: Event source
            description: Event description
            metadata: Additional metadata
        """
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            description=description,
            metadata=metadata or {},
        )

        self.event_log.append(event)

        # Log to standard logging
        log_level = {
            "critical": logging.CRITICAL,
            "high": logging.ERROR,
            "medium": logging.WARNING,
            "low": logging.INFO,
        }.get(severity, logging.INFO)

        logger.log(log_level, "Security event: %s - %s", event_type, description)

        # Send to CloudWatch (only if credentials available)
        if self.cloudwatch:
            try:
                self._send_to_cloudwatch(event)
            except Exception as e:
                logger.debug("CloudWatch unavailable: %s", e)

        # Send alert for critical/high severity
        if severity in ["critical", "high"] and self.sns:
            try:
                self._send_alert(event)
            except Exception as e:
                logger.debug("SNS unavailable: %s", e)

    def _send_to_cloudwatch(self, event: SecurityEvent) -> None:
        """Send event to CloudWatch metrics.

        Args:
            event: Security event
        """
        try:
            # Send metric
            self.cloudwatch.put_metric_data(
                Namespace=self.cloudwatch_namespace,
                MetricData=[
                    {
                        "MetricName": f"SecurityEvent_{event.event_type}",
                        "Value": 1,
                        "Unit": "Count",
                        "Timestamp": time.time(),
                        "Dimensions": [
                            {"Name": "Severity", "Value": event.severity},
                            {"Name": "Source", "Value": event.source},
                        ],
                    }
                ],
            )

            logger.debug("Event sent to CloudWatch: %s", event.event_type)

        except ClientError as e:
            logger.error("Failed to send to CloudWatch: %s", e)

    def _send_alert(self, event: SecurityEvent) -> None:
        """Send alert via SNS.

        Args:
            event: Security event
        """
        if not self.sns_topic_arn:
            logger.warning("No SNS topic configured - alert not sent")
            return

        try:
            message = {
                "default": f"Security Alert: {event.event_type}",
                "email": self._format_email_alert(event),
                "sms": f"Security Alert ({event.severity}): {event.event_type}",
            }

            self.sns.publish(
                TopicArn=self.sns_topic_arn,
                Subject=f"[{event.severity.upper()}] Security Alert",
                Message=json.dumps(message),
                MessageStructure="json",
            )

            logger.info("Alert sent via SNS: %s", event.event_type)

        except ClientError as e:
            logger.error("Failed to send SNS alert: %s", e)

    def _format_email_alert(self, event: SecurityEvent) -> str:
        """Format event as email alert.

        Args:
            event: Security event

        Returns:
            Formatted email body
        """
        return f"""
Security Alert
==============

Type: {event.event_type}
Severity: {event.severity}
Source: {event.source}
Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.timestamp))}

Description:
{event.description}

Metadata:
{json.dumps(event.metadata, indent=2)}

---
This is an automated security alert from Project-AI
"""

    def add_threat_signature(self, campaign_name: str, indicators: List[str]) -> None:
        """Add threat campaign signature.

        Args:
            campaign_name: Name of threat campaign
            indicators: List of indicators (IPs, hashes, patterns)
        """
        self.threat_signatures[campaign_name] = indicators
        logger.info("Added threat signature: %s (%d indicators)", campaign_name, len(indicators))

    def check_threat_signatures(self, data: str) -> List[str]:
        """Check data against threat signatures.

        Args:
            data: Data to check

        Returns:
            List of matching campaign names
        """
        matches = []

        for campaign_name, indicators in self.threat_signatures.items():
            for indicator in indicators:
                if indicator in data:
                    matches.append(campaign_name)
                    logger.warning("Threat signature matched: %s (indicator: %s)", campaign_name, indicator[:50])
                    break

        return matches

    def get_event_statistics(
        self, time_window: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get event statistics.

        Args:
            time_window: Optional time window in seconds

        Returns:
            Statistics dictionary
        """
        if time_window:
            cutoff = time.time() - time_window
            events = [e for e in self.event_log if e.timestamp >= cutoff]
        else:
            events = self.event_log

        stats = {
            "total_events": len(events),
            "by_severity": {},
            "by_type": {},
            "by_source": {},
        }

        for event in events:
            # Count by severity
            stats["by_severity"][event.severity] = (
                stats["by_severity"].get(event.severity, 0) + 1
            )

            # Count by type
            stats["by_type"][event.event_type] = (
                stats["by_type"].get(event.event_type, 0) + 1
            )

            # Count by source
            stats["by_source"][event.source] = (
                stats["by_source"].get(event.source, 0) + 1
            )

        return stats

    def detect_anomalies(
        self, time_window: float = 3600, threshold: int = 10
    ) -> List[Dict[str, Any]]:
        """Detect anomalous event patterns.

        Args:
            time_window: Time window in seconds
            threshold: Event count threshold for anomaly

        Returns:
            List of detected anomalies
        """
        cutoff = time.time() - time_window
        recent_events = [e for e in self.event_log if e.timestamp >= cutoff]

        # Group by type
        event_counts = {}
        for event in recent_events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

        # Find anomalies
        anomalies = []
        for event_type, count in event_counts.items():
            if count >= threshold:
                anomalies.append(
                    {
                        "event_type": event_type,
                        "count": count,
                        "time_window": time_window,
                        "threshold": threshold,
                    }
                )

                logger.warning(
                    "Anomaly detected: %s occurred %d times in %d seconds",
                    event_type,
                    count,
                    time_window,
                )

        return anomalies

    def export_audit_log(self, output_path: str, format: str = "json") -> None:
        """Export audit log to file.

        Args:
            output_path: Output file path
            format: Export format (json or csv)
        """
        if format == "json":
            with open(output_path, "w") as f:
                events_dict = [e.to_dict() for e in self.event_log]
                json.dump(events_dict, f, indent=2)

        elif format == "csv":
            import csv

            with open(output_path, "w", newline="") as f:
                if not self.event_log:
                    return

                fieldnames = ["timestamp", "event_type", "severity", "source", "description"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for event in self.event_log:
                    writer.writerow(
                        {
                            "timestamp": event.timestamp,
                            "event_type": event.event_type,
                            "severity": event.severity,
                            "source": event.source,
                            "description": event.description,
                        }
                    )

        logger.info("Audit log exported to: %s", output_path)


class StructuredLogger:
    """Structured logging with JSON format."""

    def __init__(self, log_path: str = "data/audit_logs/security.log"):
        """Initialize structured logger.

        Args:
            log_path: Path to log file
        """
        self.log_path = log_path

        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(self, level: str, message: str, **kwargs) -> None:
        """Log structured message.

        Args:
            level: Log level (info, warning, error, critical)
            message: Log message
            **kwargs: Additional structured fields
        """
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs,
        }

        # Append to log file
        with open(self.log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.log("info", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.log("warning", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.log("error", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.log("critical", message, **kwargs)
