"""Anti-Phishing Engine"""

import logging
from typing import Dict, Any, Set
import re


class AntiPhishingEngine:
    """
    Detects and blocks phishing attempts.
    Protects against social engineering and credential theft.
    """

    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("anti_phishing", True)
        self.logger = logging.getLogger(__name__)
        self._active = False

        self._phishing_domains: Set[str] = set()
        self._suspicious_patterns = []
        self._blocked_count = 0

        self._load_phishing_database()

    def start(self):
        """Start anti-phishing"""
        self.logger.info("Starting Anti-Phishing Engine")
        self._active = True

    def stop(self):
        """Stop anti-phishing"""
        self.logger.info("Stopping Anti-Phishing Engine")
        self._active = False

    def _load_phishing_database(self):
        """Load known phishing domains and patterns"""
        # Example phishing domains (would be loaded from database)
        self._phishing_domains = {
            "secure-login-verify.com",
            "account-verify-secure.com",
            "paypal-secure-login.com",
        }

        # Suspicious URL patterns
        self._suspicious_patterns = [
            r"login.*verify",
            r"secure.*account.*update",
            r"suspended.*account",
            r"confirm.*identity",
            r"urgent.*action.*required",
            r"paypal.*secure",
            r"amazon.*verify",
            r"apple.*icloud.*login",
        ]

    def is_phishing(self, url: str, content: str = "") -> bool:
        """
        Check if URL or content is phishing.

        Returns:
            True if phishing detected
        """
        if not self._active:
            return False

        # Check known phishing domains
        for domain in self._phishing_domains:
            if domain in url:
                self.logger.warning(f"Known phishing domain detected: {domain}")
                self._blocked_count += 1
                return True

        # Check suspicious patterns in URL
        for pattern in self._suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                self.logger.warning(f"Suspicious URL pattern: {pattern}")
                self._blocked_count += 1
                return True

        # Check for homograph attacks (look-alike domains)
        if self._is_homograph_attack(url):
            self.logger.warning(f"Homograph attack detected: {url}")
            self._blocked_count += 1
            return True

        # Check content for phishing indicators
        if content and self._contains_phishing_content(content):
            self.logger.warning("Phishing content detected")
            self._blocked_count += 1
            return True

        return False

    def _is_homograph_attack(self, url: str) -> bool:
        """Detect homograph/lookalike domain attacks"""
        # Check for unicode characters that look like ASCII
        suspicious_chars = ["а", "е", "о", "р", "с", "у", "х"]  # Cyrillic

        for char in suspicious_chars:
            if char in url:
                return True

        return False

    def _contains_phishing_content(self, content: str) -> bool:
        """Check if content contains phishing indicators"""
        phishing_keywords = [
            "verify your account",
            "confirm your identity",
            "suspended account",
            "unusual activity",
            "click here immediately",
            "urgent action required",
            "update payment information",
        ]

        content_lower = content.lower()
        for keyword in phishing_keywords:
            if keyword in content_lower:
                return True

        return False

    def report_phishing(self, url: str):
        """Report new phishing URL"""
        self._phishing_domains.add(url)
        self.logger.info(f"Phishing URL reported and blocked: {url}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get anti-phishing statistics"""
        return {
            "active": self._active,
            "blocked_count": self._blocked_count,
            "known_phishing_domains": len(self._phishing_domains),
        }
