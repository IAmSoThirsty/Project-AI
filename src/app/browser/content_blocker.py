"""Content Blocker - blocks trackers, ads, pop-ups, and redirects"""

import logging
from typing import Set, List
import re


class ContentBlocker:
    """
    Content blocker for privacy protection.
    Blocks trackers, ads, malicious content, pop-ups, and redirects.
    """

    def __init__(self, block_trackers: bool = True,
                 block_popups: bool = True,
                 block_redirects: bool = True):
        self.block_trackers = block_trackers
        self.block_popups = block_popups  # NEW REQUIREMENT
        self.block_redirects = block_redirects  # NEW REQUIREMENT
        self.logger = logging.getLogger(__name__)

        self._tracker_domains: Set[str] = set()
        self._malicious_patterns: List[str] = []
        self._blocked_count = 0
        self._active = False

        self._load_blocklists()

    def start(self):
        """Start content blocker"""
        self.logger.info("Starting Content Blocker - blocking trackers, pop-ups, and redirects")
        self._active = True

    def stop(self):
        """Stop content blocker"""
        self.logger.info("Stopping Content Blocker")
        self._active = False

    def _load_blocklists(self):
        """Load tracker and malicious domain lists"""
        # Known tracker domains
        self._tracker_domains = {
            'google-analytics.com',
            'doubleclick.net',
            'facebook.com/tr',
            'facebook.net',
            'googlesyndication.com',
            'googletagmanager.com',
            'scorecardresearch.com',
            'quantserve.com',
            'chartbeat.com',
            'hotjar.com',
            'mouseflow.com',
            'crazyegg.com',
            'inspectlet.com'
        }

        # Malicious patterns
        self._malicious_patterns = [
            r'eval\s*\(',
            r'document\.write\s*\(',
            r'onclick\s*=',
            r'onload\s*=',
            r'onerror\s*=',
            r'<iframe[^>]*>',
            r'javascript:',
            r'window\.open\(',  # NEW REQUIREMENT: Block pop-ups
            r'location\.href\s*=',  # NEW REQUIREMENT: Block redirects
            r'location\.replace\(',  # NEW REQUIREMENT: Block redirects
            r'window\.location\s*=',  # NEW REQUIREMENT: Block redirects
            r'meta.*http-equiv.*refresh'  # NEW REQUIREMENT: Block meta redirects
        ]

    def should_allow_url(self, url: str) -> bool:
        """
        Check if URL should be allowed.

        Returns:
            True if allowed, False if blocked
        """
        if not self._active:
            return True

        # Check tracker domains
        if self.block_trackers and self._is_tracker(url):
            self.logger.debug(f"Blocked tracker: {url}")
            self._blocked_count += 1
            return False

        # Check malicious patterns
        if self._is_malicious(url):
            self.logger.warning(f"Blocked malicious URL: {url}")
            self._blocked_count += 1
            return False

        return True

    def should_allow_content(self, content: str, content_type: str) -> bool:
        """
        Check if content should be allowed.
        Blocks scripts that create pop-ups or redirects.

        Returns:
            True if allowed, False if blocked
        """
        if not self._active:
            return True

        # Check for malicious patterns in content
        for pattern in self._malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.logger.warning(f"Blocked content with pattern: {pattern}")
                self._blocked_count += 1
                return False

        # Block pop-up attempts (NEW REQUIREMENT)
        if self.block_popups and self._contains_popup_code(content):
            self.logger.info("Blocked pop-up attempt")
            self._blocked_count += 1
            return False

        # Block redirect attempts (NEW REQUIREMENT)
        if self.block_redirects and self._contains_redirect_code(content):
            self.logger.info("Blocked redirect attempt")
            self._blocked_count += 1
            return False

        return True

    def _is_tracker(self, url: str) -> bool:
        """Check if URL is a known tracker"""
        for domain in self._tracker_domains:
            if domain in url:
                return True
        return False

    def _is_malicious(self, url: str) -> bool:
        """Check if URL appears malicious"""
        # Check for suspicious patterns
        suspicious = [
            'javascript:',
            'data:text/html',
            '../../../',
            'file://',
            'chrome://'
        ]

        for pattern in suspicious:
            if pattern in url.lower():
                return True

        return False

    def _contains_popup_code(self, content: str) -> bool:
        """Check if content contains pop-up code (NEW REQUIREMENT)"""
        popup_patterns = [
            r'window\.open\s*\(',
            r'showModalDialog\s*\(',
            r'showModelessDialog\s*\(',
            r'<a[^>]*target\s*=\s*["\']_blank["\'][^>]*onclick',
        ]

        for pattern in popup_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def _contains_redirect_code(self, content: str) -> bool:
        """Check if content contains redirect code (NEW REQUIREMENT)"""
        redirect_patterns = [
            r'location\.href\s*=',
            r'location\.replace\s*\(',
            r'location\.assign\s*\(',
            r'window\.location\s*=',
            r'window\.location\.href\s*=',
            r'<meta[^>]*http-equiv\s*=\s*["\']refresh["\']',
        ]

        for pattern in redirect_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def add_tracker_domain(self, domain: str):
        """Add domain to tracker blocklist"""
        self._tracker_domains.add(domain)

    def remove_tracker_domain(self, domain: str):
        """Remove domain from tracker blocklist"""
        self._tracker_domains.discard(domain)

    def get_statistics(self) -> dict:
        """Get blocking statistics"""
        return {
            'blocked_count': self._blocked_count,
            'tracker_domains': len(self._tracker_domains),
            'active': self._active,
            'block_popups': self.block_popups,
            'block_redirects': self.block_redirects
        }
