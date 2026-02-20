"""
Control Plane Hardening System
Implements tamper detection, out-of-band monitoring, and two-man rule for critical actions.
"""

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TamperEventSeverity(Enum):
    """Severity levels for tamper events"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(Enum):
    """Status of approval requests"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class TamperEvent:
    """Tamper detection event"""

    timestamp: datetime
    severity: TamperEventSeverity
    resource_type: str
    resource_name: str
    event_type: str
    details: dict[str, Any]
    detected_by: str
    action_taken: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["severity"] = self.severity.value
        return data


@dataclass
class ApprovalRequest:
    """Two-man rule approval request"""

    request_id: str
    timestamp: datetime
    requester: str
    action: str
    resource: str
    justification: str
    approvers_required: int
    approvers: list[str]
    status: ApprovalStatus
    expires_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.value
        data["expires_at"] = self.expires_at.isoformat()
        return data


class ControlPlaneHardeningSystem:
    """
    Control plane hardening system with:
    - Tamper detection for critical resources
    - Out-of-band monitoring and alerting
    - Two-man rule (M-of-N) approval for critical actions
    - Automated lockdown on tampering
    - Cloud organization policy enforcement
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize control plane hardening system

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.data_dir = self.config.get("data_dir", "data/control_plane")
        self.tamper_log_dir = os.path.join(self.data_dir, "tamper_events")
        self.approval_dir = os.path.join(self.data_dir, "approvals")

        os.makedirs(self.tamper_log_dir, exist_ok=True)
        os.makedirs(self.approval_dir, exist_ok=True)

        # Tamper detection state
        self.tamper_events: list[TamperEvent] = []
        self.monitored_resources: dict[str, str] = {}  # resource -> hash
        self.lockdown_active = False

        # Approval state
        self.approval_requests: dict[str, ApprovalRequest] = {}

        # Critical resources to monitor
        self.critical_resources = self.config.get(
            "critical_resources",
            [
                "kyverno-deployment",
                "kyverno-clusterpolicies",
                "argocd-deployment",
                "argocd-applications",
                "admission-webhooks",
                "audit-policy",
            ],
        )

        # SIEM configuration
        self.siem_endpoint = self.config.get("siem_endpoint")
        self.siem_api_key = self.config.get("siem_api_key")

        # Start monitoring thread
        if self.config.get("enable_monitoring", True):
            self._start_monitoring()

    def _start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Started control plane monitoring")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                self._check_critical_resources()
                time.sleep(self.config.get("monitoring_interval", 60))
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    def _check_critical_resources(self):
        """Check critical resources for tampering"""
        # This would integrate with Kubernetes API to check resources
        # For now, we'll implement the framework

        for resource in self.critical_resources:
            try:
                # Get current state of resource
                current_hash = self._get_resource_hash(resource)

                # Compare with known state
                if resource in self.monitored_resources:
                    if self.monitored_resources[resource] != current_hash:
                        self._handle_tamper_detection(resource, current_hash)

                # Update known state
                self.monitored_resources[resource] = current_hash

            except Exception as e:
                logger.error(f"Error checking resource {resource}: {e}")

    def _get_resource_hash(self, resource: str) -> str:
        """
        Get hash of resource state

        In production, this would query Kubernetes API.
        For now, we simulate it.
        """
        # Placeholder - would use kubectl or kubernetes python client
        resource_data = f"resource-{resource}-{datetime.utcnow().strftime('%Y%m%d')}"
        return hashlib.sha256(resource_data.encode()).hexdigest()

    def _handle_tamper_detection(self, resource: str, current_hash: str):
        """Handle detected tampering"""
        event = TamperEvent(
            timestamp=datetime.utcnow(),
            severity=TamperEventSeverity.CRITICAL,
            resource_type=self._get_resource_type(resource),
            resource_name=resource,
            event_type="unauthorized_modification",
            details={
                "previous_hash": self.monitored_resources.get(resource),
                "current_hash": current_hash,
            },
            detected_by="control-plane-hardening-system",
            action_taken="alert_and_log",
        )

        self.tamper_events.append(event)
        self._save_tamper_event(event)

        # Alert SIEM
        self._alert_siem(event)

        # Check if lockdown is needed
        if self._should_trigger_lockdown(event):
            self._trigger_lockdown(event)

        logger.critical(f"TAMPER DETECTED: {resource}")

    def _get_resource_type(self, resource: str) -> str:
        """Determine resource type from name"""
        if "deployment" in resource.lower():
            return "Deployment"
        elif "policy" in resource.lower():
            return "ClusterPolicy"
        elif "webhook" in resource.lower():
            return "ValidatingWebhookConfiguration"
        elif "application" in resource.lower():
            return "Application"
        return "Unknown"

    def _should_trigger_lockdown(self, event: TamperEvent) -> bool:
        """Determine if event should trigger lockdown"""
        # Lockdown for critical resources
        critical_keywords = ["kyverno", "argocd", "admission", "webhook"]
        return any(keyword in event.resource_name.lower() for keyword in critical_keywords)

    def _trigger_lockdown(self, event: TamperEvent):
        """Trigger cluster lockdown"""
        if self.lockdown_active:
            return

        self.lockdown_active = True
        logger.critical(f"LOCKDOWN TRIGGERED: {event.resource_name}")

        # Log lockdown event
        lockdown_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "reason": f"Tamper detected: {event.resource_name}",
            "event": event.to_dict(),
            "actions": [
                "scale_to_zero_non_critical",
                "disable_admission_webhooks",
                "alert_security_team",
                "create_incident",
            ],
        }

        lockdown_file = os.path.join(self.data_dir, "lockdown.json")
        with open(lockdown_file, "w") as f:
            json.dump(lockdown_data, f, indent=2)

        # Alert SIEM with critical severity
        self._alert_siem_critical(lockdown_data)

    def _alert_siem(self, event: TamperEvent):
        """Send alert to SIEM"""
        if not self.siem_endpoint:
            logger.warning("SIEM endpoint not configured")
            return

        try:
            import requests

            payload = {
                "timestamp": event.timestamp.isoformat(),
                "severity": event.severity.value,
                "event_type": "tamper_detection",
                "resource": event.resource_name,
                "details": event.details,
                "source": "project-ai-control-plane-hardening",
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.siem_api_key}",
            }

            response = requests.post(self.siem_endpoint, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                logger.info(f"SIEM alert sent for {event.resource_name}")
            else:
                logger.error(f"SIEM alert failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to send SIEM alert: {e}")

    def _alert_siem_critical(self, data: dict[str, Any]):
        """Send critical alert to SIEM"""
        if not self.siem_endpoint:
            logger.warning("SIEM endpoint not configured")
            return

        try:
            import requests

            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "critical",
                "event_type": "cluster_lockdown",
                "details": data,
                "source": "project-ai-control-plane-hardening",
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.siem_api_key}",
            }

            response = requests.post(self.siem_endpoint, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                logger.info("SIEM critical alert sent")
            else:
                logger.error(f"SIEM critical alert failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to send SIEM critical alert: {e}")

    def _save_tamper_event(self, event: TamperEvent):
        """Save tamper event to storage"""
        filename = f"tamper_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.tamper_log_dir, filename)

        with open(filepath, "w") as f:
            json.dump(event.to_dict(), f, indent=2)

    def request_critical_action(
        self,
        requester: str,
        action: str,
        resource: str,
        justification: str,
        approvers_required: int = 2,
    ) -> str:
        """
        Request approval for a critical action (two-man rule)

        Args:
            requester: Identity requesting the action
            action: Action to perform
            resource: Resource to act upon
            justification: Justification for the action
            approvers_required: Number of approvers required

        Returns:
            str: Request ID
        """
        import uuid
        from datetime import timedelta

        request_id = str(uuid.uuid4())

        request = ApprovalRequest(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            requester=requester,
            action=action,
            resource=resource,
            justification=justification,
            approvers_required=approvers_required,
            approvers=[],
            status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        self.approval_requests[request_id] = request
        self._save_approval_request(request)

        logger.info(f"Created approval request {request_id} for {action} on {resource}")
        return request_id

    def approve_request(self, request_id: str, approver: str) -> bool:
        """
        Approve a critical action request

        Args:
            request_id: Request identifier
            approver: Identity approving the request

        Returns:
            bool: True if approval recorded successfully
        """
        if request_id not in self.approval_requests:
            logger.error(f"Request {request_id} not found")
            return False

        request = self.approval_requests[request_id]

        # Check if already approved by this approver
        if approver in request.approvers:
            logger.warning(f"Request {request_id} already approved by {approver}")
            return False

        # Check if expired
        if datetime.utcnow() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            self._save_approval_request(request)
            logger.warning(f"Request {request_id} has expired")
            return False

        # Add approval
        request.approvers.append(approver)

        # Check if enough approvals
        if len(request.approvers) >= request.approvers_required:
            request.status = ApprovalStatus.APPROVED
            logger.info(f"Request {request_id} APPROVED with {len(request.approvers)} approvals")

        self._save_approval_request(request)
        return True

    def reject_request(self, request_id: str, rejector: str, reason: str) -> bool:
        """
        Reject a critical action request

        Args:
            request_id: Request identifier
            rejector: Identity rejecting the request
            reason: Reason for rejection

        Returns:
            bool: True if rejection recorded successfully
        """
        if request_id not in self.approval_requests:
            logger.error(f"Request {request_id} not found")
            return False

        request = self.approval_requests[request_id]
        request.status = ApprovalStatus.REJECTED

        self._save_approval_request(request)
        logger.info(f"Request {request_id} REJECTED by {rejector}: {reason}")
        return True

    def is_action_approved(self, request_id: str) -> bool:
        """Check if action is approved"""
        if request_id not in self.approval_requests:
            return False

        request = self.approval_requests[request_id]
        return request.status == ApprovalStatus.APPROVED

    def _save_approval_request(self, request: ApprovalRequest):
        """Save approval request to storage"""
        filepath = os.path.join(self.approval_dir, f"{request.request_id}.json")

        with open(filepath, "w") as f:
            json.dump(request.to_dict(), f, indent=2)

    def get_tamper_events(
        self, severity: TamperEventSeverity | None = None, since: datetime | None = None
    ) -> list[TamperEvent]:
        """Get tamper events, optionally filtered"""
        events = self.tamper_events

        if severity:
            events = [e for e in events if e.severity == severity]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events

    def get_approval_requests(self, status: ApprovalStatus | None = None) -> list[ApprovalRequest]:
        """Get approval requests, optionally filtered by status"""
        requests = list(self.approval_requests.values())

        if status:
            requests = [r for r in requests if r.status == status]

        return requests

    def deactivate_lockdown(self, authorized_by: str) -> bool:
        """
        Deactivate cluster lockdown

        Args:
            authorized_by: Identity authorized to deactivate

        Returns:
            bool: True if successful
        """
        if not self.lockdown_active:
            logger.info("Lockdown is not active")
            return False

        self.lockdown_active = False

        lockdown_file = os.path.join(self.data_dir, "lockdown.json")
        if os.path.exists(lockdown_file):
            os.remove(lockdown_file)

        logger.info(f"Lockdown deactivated by {authorized_by}")
        return True
