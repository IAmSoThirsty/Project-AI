"""
Cerberus Security Tools Interface
Allows Cerberus to request offensive security tools via Triumvirate approval

CRITICAL: All tool requests must go through Triumvirate authorization
"""

from typing import Dict, List, Optional
from security.triumvirate_authorization import (
    triumvirate, ToolAuthorizationRequest, ThreatLevel
)
from orchestrator.security_tools_service import SecurityToolsService
import logging

logger = logging.getLogger('CerberusSecurityTools')


class CerberusSecurityInterface:
    """
    Cerberus interface to security tools vault
    
    All access requires Triumvirate approval based on threat assessment
    """
    
    def __init__(self):
        self.security_service = SecurityToolsService()
        self.active_sessions = {}
    
    def request_tool_access(self, tool_category: str, tool_name: str,
                           threat_level: ThreatLevel, justification: str,
                           target: str = "") -> Dict:
        """
        Request access to a security tool
        
        Args:
            tool_category: Category (e.g., 'networks', 'web')
            tool_name: Specific tool name
            threat_level: Assessed threat severity
            justification: Detailed explanation of necessity
            target: Target system/IP (optional, for logging)
        
        Returns:
            Authorization result with session token if approved
        """
        logger.warning(f"CERBERUS: Requesting tool access")
        logger.warning(f"  Tool: {tool_category}/{tool_name}")
        logger.warning(f"  Threat: {threat_level.name}")
        
        # Create authorization request
        request = ToolAuthorizationRequest(
            requester="CERBERUS",
            tool_category=tool_category,
            tool_name=tool_name,
            threat_level=threat_level,
            justification=justification,
            target=target
        )
        
        # Submit to Triumvirate
        approved, reason, session_token = triumvirate.request_authorization(request)
        
        if approved:
            # Store active session
            self.active_sessions[session_token] = {
                'tool': f"{tool_category}/{tool_name}",
                'threat_level': threat_level.name,
                'granted_at': request.timestamp
            }
            
            logger.warning(f"CERBERUS: Tool access GRANTED by Triumvirate")
            
            return {
                'success': True,
                'session_token': session_token,
                'reason': reason,
                'message': 'Triumvirate authorization granted'
            }
        else:
            logger.warning(f"CERBERUS: Tool access DENIED by Triumvirate")
            
            return {
                'success': False,
                'reason': reason,
                'message': 'Triumvirate authorization denied'
            }
    
    def execute_authorized_tool(self, session_token: str, args: List[str] = None) -> Dict:
        """
        Execute tool with approved session token
        
        Session must be active and approved by Triumvirate
        """
        if session_token not in self.active_sessions:
            return {
                'success': False,
                'error': 'Invalid session token. Request authorization first.'
            }
        
        session = self.active_sessions[session_token]
        tool_path = session['tool']
        category, tool_name = tool_path.split('/')
        
        logger.warning(f"CERBERUS: Executing authorized tool: {tool_path}")
        
        # Execute through security service (which validates via vault)
        result = self.security_service.execute_tool(
            category=category,
            tool_name=tool_name,
            args=args,
            session_token=session_token
        )
        
        return result
    
    def assess_and_deploy(self, threat_description: str, suggested_tool: str,
                         target: str = "") -> Dict:
        """
        High-level interface: Assess threat and deploy appropriate tool
        
        Cerberus describes the threat, suggests tool, and Triumvirate decides
        """
        # Parse threat description to determine severity
        threat_level = self._assess_threat_level(threat_description)
        
        # Parse tool path
        if '/' in suggested_tool:
            category, tool_name = suggested_tool.split('/', 1)
        else:
            return {
                'success': False,
                'error': 'Tool must be specified as category/tool_name'
            }
        
        # Request authorization
        auth_result = self.request_tool_access(
            tool_category=category,
            tool_name=tool_name,
            threat_level=threat_level,
            justification=threat_description,
            target=target
        )
        
        if not auth_result['success']:
            return auth_result
        
        # If approved, tool is ready to execute
        return {
            'success': True,
            'session_token': auth_result['session_token'],
            'message': 'Tool authorized and ready. Call execute_authorized_tool() to use.',
            'threat_level': threat_level.name
        }
    
    def _assess_threat_level(self, description: str) -> ThreatLevel:
        """
        Assess threat level from description
        
        Keywords trigger severity classification
        """
        desc_lower = description.lower()
        
        # Existential threats
        if any(keyword in desc_lower for keyword in [
            'ransomware', 'infrastructure compromise', 'complete breach',
            'total system failure', 'data center compromise'
        ]):
            return ThreatLevel.EXISTENTIAL
        
        # Critical threats
        if any(keyword in desc_lower for keyword in [
            'active breach', 'data exfiltration', 'zero day',
            'privilege escalation', 'root access', 'domain compromise'
        ]):
            return ThreatLevel.CRITICAL
        
        # High threats
        if any(keyword in desc_lower for keyword in [
            'unauthorized access', 'suspicious activity', 'malware detected',
            'attack in progress', 'exploit attempt'
        ]):
            return ThreatLevel.HIGH
        
        # Medium threats
        if any(keyword in desc_lower for keyword in [
            'anomaly', 'unusual traffic', 'port scan', 'probe',
            'reconnaissance'
        ]):
            return ThreatLevel.MEDIUM
        
        # Default to low
        return ThreatLevel.LOW


# Global Cerberus interface
cerberus_security = CerberusSecurityInterface()


__all__ = ['CerberusSecurityInterface', 'cerberus_security']
