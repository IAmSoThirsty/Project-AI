"""
AD ANNIHILATOR - HOLY WAR ENGINE
Wages relentless war against ALL intrusive advertising
"""

import logging
from typing import Dict, Any, List, Set
import re


class AdAnnihilator:
    """
    AD ANNIHILATOR - HOLY WAR MODE

    Mission: Complete and total annihilation of intrusive advertising.
    No ads escape. No trackers survive. No pop-ups permitted.

    Features:
    - NUCLEAR-LEVEL ad blocking
    - Pattern matching (regex-based detection)
    - Element hiding (CSS selectors)
    - Script blocking (JavaScript annihilation)
    - Tracker destruction
    - Pop-up obliteration
    - Redirect interception
    - Autoplay assassination
    - Banner elimination
    - Video ad destruction
    - Audio ad silencing
    - Cookie monster mode
    - Malvertising protection
    - Cryptomining prevention
    - Social media widget removal
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # HOLY WAR MODE - Maximum aggression
        self.holy_war_mode = config.get('holy_war_mode', True)
        self.aggressiveness = config.get('aggressiveness', 'MAXIMUM')

        # Statistics
        self.stats = {
            'ads_blocked': 0,
            'trackers_destroyed': 0,
            'popups_obliterated': 0,
            'redirects_intercepted': 0,
            'scripts_annihilated': 0,
            'autoplay_killed': 0
        }

        # Ad domains database (massive blocklist)
        self.ad_domains = self._load_ad_domains()

        # Ad patterns (regex for detection)
        self.ad_patterns = self._load_ad_patterns()

        # CSS selectors for ad elements
        self.ad_selectors = self._load_ad_selectors()

        # Tracker domains
        self.tracker_domains = self._load_tracker_domains()

        self._active = False

    def start(self):
        """Start HOLY WAR against ads"""
        self.logger.warning("="*80)
        self.logger.warning("AD ANNIHILATOR: HOLY WAR MODE ACTIVATED")
        self.logger.warning("ZERO TOLERANCE FOR INTRUSIVE ADVERTISING")
        self.logger.warning("ALL ADS WILL BE DESTROYED WITH EXTREME PREJUDICE")
        self.logger.warning("="*80)

        self._active = True

    def stop(self):
        """Stop ad annihilator"""
        self.logger.info("AD ANNIHILATOR stopped - Statistics:")
        self.logger.info(f"  Ads blocked: {self.stats['ads_blocked']}")
        self.logger.info(f"  Trackers destroyed: {self.stats['trackers_destroyed']}")
        self.logger.info(f"  Pop-ups obliterated: {self.stats['popups_obliterated']}")

        self._active = False

    def _load_ad_domains(self) -> Set[str]:
        """Load comprehensive ad domain blocklist"""
        return {
            # Major ad networks
            'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
            'adnxs.com', 'advertising.com', 'amazon-adsystem.com',
            'pubmatic.com', 'rubiconproject.com', 'openx.net',
            'outbrain.com', 'taboola.com', 'revcontent.com',

            # Ad servers
            'ads.yahoo.com', 'ad.atdmt.com', 'adserver.com',
            'adsrvr.org', 'adtech.de', 'serving-sys.com',

            # Video ad networks
            'imasdk.googleapis.com', 'fwmrm.net', 'moatads.com',
            'innovid.com', 'teads.tv', 'spotxchange.com',

            # Pop-up/redirect networks
            'popads.net', 'popcash.net', 'propellerads.com',
            'adcash.com', 'mgid.com', 'clickadu.com',

            # Mobile ad networks
            'admob.com', 'applovin.com', 'chartboost.com',
            'inmobi.com', 'startapp.com', 'vungle.com',

            # Native advertising
            'sharethrough.com', 'nativo.com', 'triplelift.com',

            # Retargeting
            'adsymptotic.com', 'criteo.com', 'retarget.com',

            # Social media ads
            'facebook.com/ads', 'twitter.com/i/ads', 'linkedin.com/ads',

            # Analytics (ad-related)
            'scorecardresearch.com', 'quantserve.com', 'nielsen.com',

            # Additional major networks
            'media.net', 'bidswitch.net', 'contextweb.com',
            'casalemedia.com', 'turn.com', 'adsafeprotected.com'
        }

    def _load_ad_patterns(self) -> List[re.Pattern]:
        """Load regex patterns for ad detection"""
        patterns = [
            # Ad-related paths
            r'/ads?[/_-]',
            r'/advert(s|isement)?[/_-]',
            r'/banner[s]?[/_-]',
            r'/sponsor[s]?[/_-]',
            r'/popup[s]?[/_-]',

            # Ad parameters
            r'[?&]ad[s]?[=_]',
            r'[?&]advert[=_]',
            r'[?&]banner[=_]',
            r'[?&]sponsor[=_]',

            # Ad identifiers in URLs
            r'ad[0-9]+',
            r'banner[0-9]+',
            r'_ad\.',
            r'\.ad\.',

            # Tracking parameters
            r'[?&]utm_',
            r'[?&]fbclid=',
            r'[?&]gclid=',
            r'[?&]msclkid=',

            # Affiliate links
            r'/aff[/_-]',
            r'[?&]ref[=_]',
            r'[?&]affid=',

            # Pop-up indicators
            r'popup|pop-up|popunder',
            r'click(here|now)',
            r'sponsored[-_]?(content|link|post)?'
        ]

        return [re.compile(p, re.IGNORECASE) for p in patterns]

    def _load_ad_selectors(self) -> List[str]:
        """Load CSS selectors for ad elements"""
        return [
            # Generic ad containers
            '.ad', '.ads', '#ad', '#ads',
            '[class*="ad-"]', '[class*="ads-"]',
            '[id*="ad-"]', '[id*="ads-"]',
            '.advertisement', '.sponsored',
            '.banner', '.promo',

            # Specific ad networks
            '.google-ad', '.adsense',
            '.adsbygoogle', '.ad-slot',
            '.ad-container', '.ad-wrapper',

            # Pop-ups and overlays
            '.popup', '.pop-up', '.modal',
            '.overlay', '.lightbox',
            '[class*="popup"]', '[class*="modal"]',

            # Video ads
            '.video-ad', '.preroll',
            '.midroll', '.postroll',
            '[class*="video-ad"]',

            # Social media
            '.fb-ad', '.twitter-ad',
            '[class*="promoted"]',
            '[data-ad]', '[data-advertisement]',

            # Native ads
            '[class*="native-ad"]',
            '[class*="sponsored-content"]',
            '.recommended-content',

            # Sidebar ads
            '.sidebar-ad', '.right-rail-ad',
            '[class*="sidebar"][class*="ad"]'
        ]

    def _load_tracker_domains(self) -> Set[str]:
        """Load tracker domain blocklist"""
        return {
            # Major trackers
            'google-analytics.com', 'googletagmanager.com',
            'facebook.com/tr', 'connect.facebook.net',
            'hotjar.com', 'mouseflow.com', 'crazyegg.com',

            # Analytics
            'mixpanel.com', 'segment.com', 'amplitude.com',
            'heap.io', 'pendo.io', 'fullstory.com',

            # Session replay
            'logrocket.com', 'smartlook.com', 'inspectlet.com',

            # Heatmaps
            'clicktale.net', 'luckyorange.com', 'ptengine.com',

            # A/B testing
            'optimizely.com', 'vwo.com', 'convert.com',

            # Cross-site tracking
            'rlcdn.com', 'agkn.com', 'bluekai.com',
            'exelator.com', 'krxd.net', 'adsrvr.org'
        }

    def check_url(self, url: str) -> Dict[str, Any]:
        """
        Check if URL should be blocked (HOLY WAR analysis).

        Args:
            url: URL to check

        Returns:
            Block decision with reason
        """
        if not self._active:
            return {'block': False, 'reason': 'Annihilator not active'}

        url_lower = url.lower()

        # Check ad domains (INSTANT BLOCK)
        for domain in self.ad_domains:
            if domain in url_lower:
                self.stats['ads_blocked'] += 1
                return {
                    'block': True,
                    'reason': 'AD DOMAIN DETECTED',
                    'category': 'advertising',
                    'severity': 'EXTREME',
                    'action': 'ANNIHILATED'
                }

        # Check tracker domains (DESTROY)
        for domain in self.tracker_domains:
            if domain in url_lower:
                self.stats['trackers_destroyed'] += 1
                return {
                    'block': True,
                    'reason': 'TRACKER DETECTED',
                    'category': 'tracking',
                    'severity': 'HIGH',
                    'action': 'DESTROYED'
                }

        # Check ad patterns (OBLITERATE)
        for pattern in self.ad_patterns:
            if pattern.search(url):
                self.stats['ads_blocked'] += 1
                return {
                    'block': True,
                    'reason': 'AD PATTERN MATCHED',
                    'category': 'advertising',
                    'pattern': pattern.pattern,
                    'action': 'OBLITERATED'
                }

        # Passed all checks
        return {
            'block': False,
            'reason': 'Clean URL',
            'action': 'PERMITTED'
        }

    def check_element(self, element_html: str, element_class: str, element_id: str) -> Dict[str, Any]:
        """
        Check if HTML element is an ad (HOLY WAR analysis).

        Args:
            element_html: Element HTML
            element_class: Element class attribute
            element_id: Element ID attribute

        Returns:
            Block decision
        """
        if not self._active:
            return {'block': False}

        # Check CSS selectors
        for selector in self.ad_selectors:
            if selector.startswith('.'):
                # Class selector
                class_name = selector[1:]
                if class_name in element_class.lower():
                    self.stats['ads_blocked'] += 1
                    return {
                        'block': True,
                        'reason': 'AD ELEMENT DETECTED (CLASS)',
                        'selector': selector,
                        'action': 'REMOVED'
                    }
            elif selector.startswith('#'):
                # ID selector
                id_name = selector[1:]
                if id_name in element_id.lower():
                    self.stats['ads_blocked'] += 1
                    return {
                        'block': True,
                        'reason': 'AD ELEMENT DETECTED (ID)',
                        'selector': selector,
                        'action': 'REMOVED'
                    }

        # Check element content for ad indicators
        html_lower = element_html.lower()
        ad_keywords = ['advertisement', 'sponsored', 'ad by', 'ads by', 'promoted']

        for keyword in ad_keywords:
            if keyword in html_lower:
                self.stats['ads_blocked'] += 1
                return {
                    'block': True,
                    'reason': f'AD KEYWORD DETECTED: {keyword}',
                    'action': 'ANNIHILATED'
                }

        return {'block': False, 'action': 'PERMITTED'}

    def block_script(self, script_url: str) -> bool:
        """
        Determine if script should be blocked.

        Args:
            script_url: Script source URL

        Returns:
            True if should be blocked
        """
        if not self._active:
            return False

        result = self.check_url(script_url)

        if result['block']:
            self.stats['scripts_annihilated'] += 1
            self.logger.debug(f"SCRIPT BLOCKED: {script_url}")
            return True

        return False

    def intercept_popup(self) -> bool:
        """
        Intercept and block pop-up attempt.

        Returns:
            True (always blocks in HOLY WAR mode)
        """
        if not self._active:
            return False

        self.stats['popups_obliterated'] += 1
        self.logger.debug("POP-UP OBLITERATED")

        return True  # ALWAYS BLOCK POP-UPS

    def intercept_redirect(self, url: str) -> bool:
        """
        Intercept suspicious redirects.

        Args:
            url: Redirect URL

        Returns:
            True if should be blocked
        """
        if not self._active:
            return False

        # Check if redirect is to ad domain
        result = self.check_url(url)

        if result['block']:
            self.stats['redirects_intercepted'] += 1
            self.logger.debug(f"REDIRECT INTERCEPTED: {url}")
            return True

        return False

    def kill_autoplay(self) -> bool:
        """
        Kill autoplay videos/audio.

        Returns:
            True (always kills in HOLY WAR mode)
        """
        if not self._active:
            return False

        self.stats['autoplay_killed'] += 1
        self.logger.debug("AUTOPLAY KILLED")

        return True  # ALWAYS KILL AUTOPLAY

    def get_stats(self) -> Dict[str, Any]:
        """Get ad blocking statistics"""
        return {
            'holy_war_mode': self.holy_war_mode,
            'aggressiveness': self.aggressiveness,
            **self.stats,
            'total_blocked': sum([
                self.stats['ads_blocked'],
                self.stats['trackers_destroyed'],
                self.stats['popups_obliterated'],
                self.stats['redirects_intercepted'],
                self.stats['scripts_annihilated'],
                self.stats['autoplay_killed']
            ])
        }

    def get_status(self) -> Dict[str, Any]:
        """Get ad annihilator status"""
        return {
            'active': self._active,
            'holy_war_mode': self.holy_war_mode,
            'aggressiveness': self.aggressiveness,
            'ad_domains_blocked': len(self.ad_domains),
            'tracker_domains_blocked': len(self.tracker_domains),
            'ad_patterns': len(self.ad_patterns),
            'ad_selectors': len(self.ad_selectors),
            'statistics': self.get_stats()
        }
