"""
Capability Manager - Fine-grained permission system
"""

import logging
from typing import Dict, Any
from cryptography.fernet import Fernet
import time


class CapabilityManager:
    """Manages capabilities with fine-grained user control"""

    def __init__(self, cipher: Fernet):
        self.logger = logging.getLogger(__name__)
        self._cipher = cipher

        # Define available capabilities
        self.capabilities = {
            'page_content': {'description': 'Access current page content', 'risk_level': 'medium'},
            'browsing_history': {'description': 'Access browsing history', 'risk_level': 'high'},
            'filesystem': {'description': 'Access filesystem', 'risk_level': 'high'},
            'network_access': {'description': 'Make network requests (VPN only)', 'risk_level': 'medium'},
            'search': {'description': 'Perform encrypted searches', 'risk_level': 'low'},
            'bookmarks': {'description': 'Access bookmarks', 'risk_level': 'medium'},
            'downloads': {'description': 'Manage downloads', 'risk_level': 'low'},
            'clipboard': {'description': 'Access clipboard', 'risk_level': 'high'},
            'media_download': {'description': 'Download audio/video', 'risk_level': 'low'},
            'remote_desktop': {'description': 'Remote desktop connection', 'risk_level': 'high'},
            'ai_assistant': {'description': 'God tier AI assistant', 'risk_level': 'medium'}
        }

        self._permission_requests = []

    def request_permission(self, capability: str, reason: str) -> bool:
        """Request permission for a capability"""
        if capability not in self.capabilities:
            self.logger.error(f"Unknown capability: {capability}")
            return False

        cap_info = self.capabilities[capability]

        request = {
            'capability': capability,
            'reason': reason,
            'risk_level': cap_info['risk_level'],
            'timestamp': time.time()
        }
        self._permission_requests.append(request)

        self.logger.info(f"Capability requested: {capability} (Risk: {cap_info['risk_level']}) - {reason}")

        # Auto-grant low/medium risk, deny high risk (in production: user prompt)
        if cap_info['risk_level'] == 'high':
            self.logger.warning(f"High-risk capability denied: {capability}")
            return False

        return True

    def get_capability_info(self, capability: str) -> Dict[str, Any]:
        """Get information about a capability"""
        return self.capabilities.get(capability, {})
