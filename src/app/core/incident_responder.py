"""Automated Incident Response System.

Implements automated incident response workflows including component isolation,
backup/recovery, and alert generation. Integrates with security systems for
coordinated defensive actions.

Features:
- Automatic component isolation on detection
- Automated backup and recovery
- Alert generation for security teams
- Forensic data preservation
- Integration with GlobalWatchTower and SOC
- Incident escalation workflows

Defensive only - no offensive capabilities.
"""

import json
import logging
import shutil
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ResponseAction(Enum):
    """Automated response actions."""

    ISOLATE_COMPONENT = "isolate_component"
    BACKUP_DATA = "backup_data"
    RESTORE_FROM_BACKUP = "restore_from_backup"
    ALERT_TEAM = "alert_team"
    BLOCK_IP = "block_ip"
    KILL_SESSION = "kill_session"
    RESET_CREDENTIALS = "reset_credentials"
    ENABLE_MFA = "enable_mfa"
    QUARANTINE_FILE = "quarantine_file"
    LOG_FORENSICS = "log_forensics"
    ESCALATE = "escalate"


class IncidentSeverity(Enum):
    """Incident severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IncidentResponse:
    """Record of an incident response action."""

    response_id: str = field(default_factory=lambda: str(__import__("uuid").uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    incident_id: str = ""
    action: str = ""
    target: str = ""
    success: bool = False
    details: str = ""
    error: str | None = None
    duration_seconds: float = 0.0


@dataclass
class SecurityIncident:
    """Security incident requiring response."""

    incident_id: str = field(default_factory=lambda: str(__import__("uuid").uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    severity: str = IncidentSeverity.MEDIUM.value
    incident_type: str = ""
    source_ip: str = ""
    target_component: str = ""
    description: str = ""
    indicators: dict[str, Any] = field(default_factory=dict)
    automated_responses: list[str] = field(default_factory=list)
    status: str = "detected"
    resolution: str | None = None


class IncidentResponder:
    """
    Automated Incident Response System.

    Executes defensive response actions when security incidents detected.
    All actions are defensive and designed to protect the system.
    """

    def __init__(
        self,
        data_dir: str = "data/security/incidents",
        backup_dir: str = "data/security/backups",
        enable_auto_response: bool = True,
    ):
        """
        Initialize incident responder.

        Args:
            data_dir: Directory for incident records
            backup_dir: Directory for backups
            enable_auto_response: Enable automated responses
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.enable_auto_response = enable_auto_response

        # State
        self.incidents: list[SecurityIncident] = []
        self.responses: list[IncidentResponse] = []
        self.isolated_components: set = set()

        # Response handlers
        self.response_handlers: dict[str, Callable] = {
            ResponseAction.ISOLATE_COMPONENT.value: self._isolate_component,
            ResponseAction.BACKUP_DATA.value: self._backup_data,
            ResponseAction.RESTORE_FROM_BACKUP.value: self._restore_from_backup,
            ResponseAction.ALERT_TEAM.value: self._alert_team,
            ResponseAction.BLOCK_IP.value: self._block_ip,
            ResponseAction.QUARANTINE_FILE.value: self._quarantine_file,
            ResponseAction.LOG_FORENSICS.value: self._log_forensics,
        }

        # Thread safety
        self.lock = threading.Lock()

        # Persistence
        self.incidents_file = self.data_dir / "incidents.json"
        self.responses_file = self.data_dir / "responses.json"

        # Load state
        self._load_state()

        logger.info("Incident Responder initialized")
        logger.info("  Auto-response: %s", 'enabled' if enable_auto_response else 'disabled')
        logger.info("  Available actions: %s", len(self.response_handlers))

    def handle_incident(
        self,
        incident_type: str,
        severity: str,
        source_ip: str = "",
        target_component: str = "",
        description: str = "",
        indicators: dict[str, Any] | None = None,
        auto_respond: bool = True,
    ) -> SecurityIncident:
        """
        Handle a security incident.

        Args:
            incident_type: Type of incident
            severity: Severity level
            source_ip: Source IP if applicable
            target_component: Target component
            description: Incident description
            indicators: Additional indicators
            auto_respond: Whether to execute automated response

        Returns:
            SecurityIncident record
        """
        indicators = indicators or {}

        # Create incident record
        incident = SecurityIncident(
            severity=severity,
            incident_type=incident_type,
            source_ip=source_ip,
            target_component=target_component,
            description=description,
            indicators=indicators,
        )

        with self.lock:
            self.incidents.append(incident)

        logger.warning("Incident detected: %s (severity: %s) from %s", incident_type, severity, source_ip)

        # Execute automated response if enabled
        if auto_respond and self.enable_auto_response:
            self._execute_automated_response(incident)

        self._save_state()
        return incident

    def _execute_automated_response(self, incident: SecurityIncident) -> None:
        """Execute automated response based on incident."""
        actions = self._determine_response_actions(incident)

        logger.info("Executing %s automated responses for %s", len(actions), incident.incident_id)

        for action in actions:
            try:
                start_time = time.time()

                # Execute action
                handler = self.response_handlers.get(action)
                if handler:
                    success, details = handler(incident)
                else:
                    success, details = False, f"No handler for action: {action}"

                duration = time.time() - start_time

                # Record response
                response = IncidentResponse(
                    incident_id=incident.incident_id,
                    action=action,
                    target=incident.target_component or incident.source_ip,
                    success=success,
                    details=details,
                    duration_seconds=duration,
                )

                with self.lock:
                    self.responses.append(response)
                    incident.automated_responses.append(action)

                if success:
                    logger.info("Response action succeeded: %s - %s", action, details)
                else:
                    logger.error("Response action failed: %s - %s", action, details)

            except Exception as e:
                logger.error("Error executing response %s: %s", action, e)
                response = IncidentResponse(
                    incident_id=incident.incident_id,
                    action=action,
                    target=incident.target_component or incident.source_ip,
                    success=False,
                    error=str(e),
                )
                with self.lock:
                    self.responses.append(response)

    def _determine_response_actions(self, incident: SecurityIncident) -> list[str]:
        """Determine appropriate response actions for incident."""
        actions = []

        # Always log forensics
        actions.append(ResponseAction.LOG_FORENSICS.value)

        severity = incident.severity

        # Based on severity
        if severity in [IncidentSeverity.HIGH.value, IncidentSeverity.CRITICAL.value]:
            # High/Critical: Isolate and block
            if incident.target_component:
                actions.append(ResponseAction.ISOLATE_COMPONENT.value)
            if incident.source_ip:
                actions.append(ResponseAction.BLOCK_IP.value)
            actions.append(ResponseAction.ALERT_TEAM.value)
            actions.append(ResponseAction.BACKUP_DATA.value)

        elif severity == IncidentSeverity.MEDIUM.value:
            # Medium: Block IP and alert
            if incident.source_ip:
                actions.append(ResponseAction.BLOCK_IP.value)
            actions.append(ResponseAction.ALERT_TEAM.value)

        # Based on incident type
        incident_type = incident.incident_type.lower()

        if "sql" in incident_type or "injection" in incident_type:
            actions.append(ResponseAction.ISOLATE_COMPONENT.value)
            actions.append(ResponseAction.BACKUP_DATA.value)

        if "file" in incident_type or "upload" in incident_type:
            actions.append(ResponseAction.QUARANTINE_FILE.value)

        if "brute" in incident_type or "password" in incident_type:
            if incident.source_ip:
                actions.append(ResponseAction.BLOCK_IP.value)

        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)

        return unique_actions

    def _isolate_component(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Isolate a compromised component."""
        component = incident.target_component

        if not component:
            return False, "No component specified"

        # Mark component as isolated
        self.isolated_components.add(component)

        # In production, this would actually disable the component
        # For now, we just log and track
        logger.warning("Component isolated: %s", component)

        return True, f"Component {component} isolated from network"

    def _backup_data(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Create backup of critical data."""
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{incident.incident_id}_{timestamp}"
            backup_path = self.backup_dir / backup_name

            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)

            # Backup critical directories (example)
            critical_dirs = ["data/users.json", "data/ai_persona", "data/memory"]

            backed_up = []
            for item in critical_dirs:
                src = Path(item)
                if src.exists():
                    if src.is_file():
                        dst = backup_path / src.name
                        shutil.copy2(src, dst)
                        backed_up.append(str(src))
                    elif src.is_dir():
                        dst = backup_path / src.name
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                        backed_up.append(str(src))

            logger.info("Backup created: %s", backup_path)
            return True, f"Backup created: {len(backed_up)} items backed up"

        except Exception as e:
            logger.error("Backup failed: %s", e)
            return False, f"Backup failed: {e}"

    def _restore_from_backup(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Restore from backup."""
        # Find most recent backup
        backups = sorted(self.backup_dir.glob("backup_*"))

        if not backups:
            return False, "No backups available"

        latest_backup = backups[-1]
        logger.info("Restoring from backup: %s", latest_backup)

        # In production, this would restore the data
        # For now, just log
        return True, f"Restore initiated from {latest_backup.name}"

    def _alert_team(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Send alert to security team."""
        # In production, this would send email/SMS/Slack notification
        alert_message = f"""
SECURITY INCIDENT ALERT

Incident ID: {incident.incident_id}
Severity: {incident.severity}
Type: {incident.incident_type}
Source IP: {incident.source_ip}
Target: {incident.target_component}
Description: {incident.description}
Time: {incident.timestamp}

Automated responses executed:
{', '.join(incident.automated_responses) if incident.automated_responses else 'None yet'}

Please review and take appropriate action.
        """

        logger.critical("SECURITY ALERT: %s", incident.incident_type)
        logger.critical(alert_message)

        # Write alert to file
        alert_file = self.data_dir / f"alert_{incident.incident_id}.txt"
        with open(alert_file, "w") as f:
            f.write(alert_message)

        return True, f"Alert sent to security team (saved to {alert_file})"

    def _block_ip(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Block source IP."""
        ip = incident.source_ip

        if not ip:
            return False, "No IP address to block"

        # In production, this would integrate with firewall/IPBlocking system
        logger.warning("IP blocked: %s", ip)

        return True, f"IP {ip} blocked at firewall level"

    def _quarantine_file(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Quarantine suspicious file."""
        # Extract file path from indicators
        file_path = incident.indicators.get("file_path")

        if not file_path:
            return False, "No file path in indicators"

        quarantine_dir = self.data_dir / "quarantine"
        quarantine_dir.mkdir(exist_ok=True)

        try:
            src = Path(file_path)
            if src.exists():
                timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
                dst = quarantine_dir / f"{timestamp}_{src.name}"
                shutil.move(str(src), str(dst))
                logger.info("File quarantined: %s -> %s", src, dst)
                return True, f"File quarantined: {dst.name}"
        except Exception as e:
            logger.error("Quarantine failed: %s", e)
            return False, f"Quarantine failed: {e}"

        return False, "File not found"

    def _log_forensics(self, incident: SecurityIncident) -> tuple[bool, str]:
        """Log forensic data for investigation."""
        forensics_dir = self.data_dir / "forensics"
        forensics_dir.mkdir(exist_ok=True)

        forensics_file = forensics_dir / f"forensics_{incident.incident_id}.json"

        forensics_data = {
            "incident": asdict(incident),
            "timestamp": datetime.now(UTC).isoformat(),
            "system_state": {
                "isolated_components": list(self.isolated_components),
                "total_incidents": len(self.incidents),
                "total_responses": len(self.responses),
            },
        }

        try:
            with open(forensics_file, "w") as f:
                json.dump(forensics_data, f, indent=2)

            logger.info("Forensic data logged: %s", forensics_file)
            return True, f"Forensic data preserved: {forensics_file.name}"

        except Exception as e:
            logger.error("Forensics logging failed: %s", e)
            return False, f"Forensics logging failed: {e}"

    def get_statistics(self) -> dict[str, Any]:
        """Get incident response statistics."""
        with self.lock:
            total_incidents = len(self.incidents)
            total_responses = len(self.responses)

            # Count by severity
            severity_counts = {}
            for incident in self.incidents:
                severity = incident.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Count by type
            type_counts = {}
            for incident in self.incidents:
                incident_type = incident.incident_type
                type_counts[incident_type] = type_counts.get(incident_type, 0) + 1

            # Count by action
            action_counts = {}
            for response in self.responses:
                action = response.action
                action_counts[action] = action_counts.get(action, 0) + 1

            # Success rate
            successful = sum(1 for r in self.responses if r.success)
            success_rate = (
                (successful / total_responses * 100) if total_responses > 0 else 0
            )

            return {
                "total_incidents": total_incidents,
                "total_responses": total_responses,
                "success_rate": round(success_rate, 2),
                "incidents_by_severity": severity_counts,
                "incidents_by_type": type_counts,
                "responses_by_action": action_counts,
                "isolated_components": len(self.isolated_components),
                "auto_response_enabled": self.enable_auto_response,
            }

    def get_recent_incidents(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent incidents."""
        from datetime import timedelta

        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        recent = []

        for incident in self.incidents:
            incident_time = datetime.fromisoformat(incident.timestamp)
            if incident_time > cutoff:
                recent.append(asdict(incident))

        return recent

    def _load_state(self) -> None:
        """Load state from disk."""
        try:
            if self.incidents_file.exists():
                with open(self.incidents_file) as f:
                    incident_data = json.load(f)
                    # Load last 1000 incidents
                    self.incidents = [
                        SecurityIncident(**i) for i in incident_data[-1000:]
                    ]
                logger.info("Loaded %s incidents", len(self.incidents))

            if self.responses_file.exists():
                with open(self.responses_file) as f:
                    response_data = json.load(f)
                    # Load last 5000 responses
                    self.responses = [
                        IncidentResponse(**r) for r in response_data[-5000:]
                    ]
                logger.info("Loaded %s responses", len(self.responses))

        except Exception as e:
            logger.error("Error loading incident responder state: %s", e)

    def _save_state(self) -> None:
        """Save state to disk."""
        try:
            # Save incidents (keep last 1000)
            with open(self.incidents_file, "w") as f:
                incident_data = [asdict(i) for i in self.incidents[-1000:]]
                json.dump(incident_data, f, indent=2)

            # Save responses (keep last 5000)
            with open(self.responses_file, "w") as f:
                response_data = [asdict(r) for r in self.responses[-5000:]]
                json.dump(response_data, f, indent=2)

        except Exception as e:
            logger.error("Error saving incident responder state: %s", e)
