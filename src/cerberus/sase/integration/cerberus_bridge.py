"""
SASE-Cerberus Integration Bridge

Connects SASE adversarial signals to Cerberus Triumvirate authorization system.
"""

import logging
from typing import Any

logger = logging.getLogger("SASE.CerberusBridge")


class SASECerberusBridge:
    """
    Integration bridge between SASE and Cerberus

    Maps SASE confidence scores to Triumvirate threat levels
    and execution requests
    """

    def __init__(self, cerberus_interface=None, triumvirate_auth=None):
        """
        Initialize bridge

        Args:
            cerberus_interface: CerberusSecurityInterface instance (optional)
            triumvirate_auth: TriumvirateAuthorizationSystem instance (optional)
        """
        self.cerberus = cerberus_interface
        self.triumvirate = triumvirate_auth

        # Import existing systems if available
        if cerberus_interface is None:
            try:
                from orchestrator.cerberus_security_interface import (
                    CerberusSecurityInterface,
                )

                self.cerberus = CerberusSecurityInterface()
            except ImportError:
                logger.warning("Cerberus interface not available")

        if triumvirate_auth is None:
            try:
                from security.triumvirate_authorization import (
                    TriumvirateAuthorizationSystem,
                )

                self.triumvirate = TriumvirateAuthorizationSystem()
            except ImportError:
                logger.warning("Triumvirate auth not available")

        logger.info("SASE-Cerberus bridge initialized")

    def map_confidence_to_threat_level(self, confidence_pct: int) -> str:
        """
        Map SASE confidence % to Triumvirate ThreatLevel

        SASE Scale:
        - <30%: LOW
        - 30-49%: MEDIUM
        - 50-69%: HIGH
        - 70-84%: CRITICAL
        - 85-100%: SEVERE

        Triumvirate Scale:
        - LOW
        - MEDIUM
        - HIGH
        - CRITICAL
        - EXISTENTIAL
        """
        if confidence_pct < 30:
            return "LOW"
        elif confidence_pct < 50:
            return "MEDIUM"
        elif confidence_pct < 70:
            return "HIGH"
        elif confidence_pct < 85:
            return "CRITICAL"
        else:
            return "EXISTENTIAL"  # SEVERE maps to EXISTENTIAL

    def request_cerberus_action(self, sase_result: dict[str, Any]) -> dict[str, Any]:
        """
        Request Cerberus action based on SASE analysis

        Args:
            sase_result: Result from SASE.process_telemetry()

        Returns:
            Cerberus action result
        """
        if not sase_result.get("success"):
            return {"success": False, "reason": "SASE processing failed"}

        confidence = sase_result["confidence"]
        threat_class = sase_result.get("threat_class", {})

        # Only request action for MEDIUM+ threats
        if confidence["confidence_percentage"] < 30:
            logger.info("Confidence too low for Cerberus action")
            return {"success": True, "action": "monitor_only"}

        # Map to Triumvirate threat level
        threat_level = self.map_confidence_to_threat_level(confidence["confidence_percentage"])

        # Build threat description
        threat_desc = self._build_threat_description(sase_result)

        # Determine suggested tool
        suggested_tool = self._suggest_tool(confidence, threat_class)

        # Request authorization via Triumvirate
        if self.triumvirate:
            from security.triumvirate_authorization import (
                ThreatLevel,
                ToolAuthorizationRequest,
            )

            # Map string to ThreatLevel enum
            threat_level_enum = getattr(ThreatLevel, threat_level, ThreatLevel.MEDIUM)

            auth_request = ToolAuthorizationRequest(
                requester="SASE_ENGINE",
                tool_category="security_tool",
                tool_name=suggested_tool,
                threat_level=threat_level_enum,
                justification=threat_desc,
                target=sase_result.get("event_id", "unknown"),
            )

            approved, reason, session_token = self.triumvirate.request_authorization(auth_request)

            if approved:
                logger.warning(f"Triumvirate APPROVED: {suggested_tool}")

                # Execute via Cerberus if available
                if self.cerberus:
                    result = self.cerberus.execute_tool(suggested_tool, session_token)
                    return result
                else:
                    return {
                        "success": True,
                        "approved": True,
                        "tool": suggested_tool,
                        "session_token": session_token,
                    }
            else:
                logger.warning(f"Triumvirate DENIED: {reason}")
                return {"success": False, "approved": False, "reason": reason}
        else:
            # Triumvirate not available, return recommendation
            return {
                "success": True,
                "recommendation": suggested_tool,
                "threat_level": threat_level,
                "threat_description": threat_desc,
            }

    def _build_threat_description(self, sase_result: dict) -> str:
        """Build human-readable threat description"""
        confidence = sase_result["confidence"]
        threat_class = sase_result.get("threat_class", {})
        behavior_state = sase_result.get("behavior_state")

        desc_parts = []

        desc_parts.append(f"SASE confidence: {confidence['confidence_percentage']}%")
        desc_parts.append(f"Classification: {confidence['threat_classification']}")

        if threat_class:
            desc_parts.append(f"Actor type: {threat_class.get('actor_class', 'unknown')}")
            desc_parts.append(f"Risk level: {threat_class.get('risk_level', 0)}/10")

        if behavior_state:
            desc_parts.append(f"Behavioral state: {behavior_state}")

        if confidence.get("trend"):
            desc_parts.append(f"Trend: {confidence['trend']}")

        return " | ".join(desc_parts)

    def _suggest_tool(self, confidence: dict, threat_class: dict) -> str:
        """Suggest appropriate security tool"""
        confidence_pct = confidence["confidence_percentage"]

        # Map confidence to tool
        if confidence_pct >= 85:
            return "incident_response"
        elif confidence_pct >= 70:
            return "threat_containment"
        elif confidence_pct >= 50:
            return "network_isolator"
        elif confidence_pct >= 30:
            return "monitoring_agent"
        else:
            return "passive_monitor"


__all__ = ["SASECerberusBridge"]
