"""
Privacy Checker - Runs privacy audit checklists
"""

import logging
from typing import Dict, Any, Optional
import re


class PrivacyChecker:
    """Runs privacy audit checklists"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }

    def audit_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Audit a query for privacy concerns"""
        concerns = []
        suggestions = []

        # Check for sensitive data
        for data_type, pattern in self.sensitive_patterns.items():
            if re.search(pattern, query):
                concerns.append(f"Query contains {data_type}")
                suggestions.append(f"Remove or anonymize {data_type}")

        safe = len(concerns) == 0

        if not safe:
            suggestions.append("Process with minimized data only")

        return {
            'safe': safe,
            'concerns': concerns,
            'suggestions': suggestions
        }
