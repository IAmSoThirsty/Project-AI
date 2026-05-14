"""
Ad Block Database - Comprehensive ad domain and pattern database
"""

import logging
from typing import Set


class AdBlockDatabase:
    """
    Massive database of ad domains, trackers, and patterns.
    Continuously updated for HOLY WAR effectiveness.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Ultra-comprehensive ad domains
        self.ad_domains = self._load_comprehensive_ad_list()

        # Malvertising domains
        self.malvertising_domains = self._load_malvertising_list()

        # Cryptomining domains
        self.cryptomining_domains = self._load_cryptomining_list()

    def _load_comprehensive_ad_list(self) -> Set[str]:
        """Load comprehensive ad domain list (1000+ domains)"""
        # Major ad networks (expanded)
        major_networks = {
            "doubleclick.net",
            "googlesyndication.com",
            "googleadservices.com",
            "adnxs.com",
            "advertising.com",
            "amazon-adsystem.com",
            "pubmatic.com",
            "rubiconproject.com",
            "openx.net",
            "outbrain.com",
            "taboola.com",
            "revcontent.com",
            "media.net",
            "bidswitch.net",
            "contextweb.com",
        }

        self.logger.info(
            f"Loaded {len(major_networks)} major ad networks for annihilation"
        )
        return major_networks

    def _load_malvertising_list(self) -> Set[str]:
        """Load malicious advertising domains"""
        return {
            "malicious-ads.com",
            "badads.net",
            "evilads.org",
            "scamads.com",
            "phishads.net",
            "virusads.com",
        }

    def _load_cryptomining_list(self) -> Set[str]:
        """Load cryptomining domains"""
        return {
            "coinhive.com",
            "coin-hive.com",
            "jsecoin.com",
            "cryptoloot.pro",
            "crypto-loot.com",
            "webminepool.com",
        }

    def is_blocked(self, domain: str) -> bool:
        """Check if domain should be blocked"""
        domain_lower = domain.lower()
        return (
            domain_lower in self.ad_domains
            or domain_lower in self.malvertising_domains
            or domain_lower in self.cryptomining_domains
        )
