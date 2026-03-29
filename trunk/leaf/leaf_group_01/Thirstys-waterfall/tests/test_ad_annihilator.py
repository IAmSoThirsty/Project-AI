# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_ad_annihilator.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_ad_annihilator.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Comprehensive AD Annihilator Testing Suite
Tests for HOLY WAR mode - complete ad annihilation
"""

import unittest
from thirstys_waterfall.ad_annihilator import (
    AdAnnihilator,
    AdBlockDatabase,
    TrackerDestroyer,
    AutoplayKiller,
)


class TestAdBlockDatabase(unittest.TestCase):
    """Test ad domain database"""

    def setUp(self):
        """Setup test fixtures"""
        self.db = AdBlockDatabase()

    def test_database_initialization(self):
        """Test database loads comprehensive ad lists"""
        self.assertGreater(len(self.db.ad_domains), 10)
        self.assertGreater(len(self.db.malvertising_domains), 0)
        self.assertGreater(len(self.db.cryptomining_domains), 0)

    def test_known_ad_domains_blocked(self):
        """Test known ad domains are in blocklist"""
        known_ad_domains = [
            "doubleclick.net",
            "googlesyndication.com",
            "outbrain.com",
            "taboola.com",
        ]

        for domain in known_ad_domains:
            self.assertTrue(self.db.is_blocked(domain), f"{domain} should be blocked")

    def test_legit_domains_not_blocked(self):
        """Test legitimate domains are not blocked"""
        legit_domains = ["google.com", "example.com", "github.com"]

        for domain in legit_domains:
            self.assertFalse(
                self.db.is_blocked(domain), f"{domain} should not be blocked"
            )

    def test_malvertising_domains_blocked(self):
        """Test malicious advertising domains are blocked"""
        for domain in self.db.malvertising_domains:
            self.assertTrue(self.db.is_blocked(domain))

    def test_cryptomining_domains_blocked(self):
        """Test cryptomining domains are blocked"""
        cryptomining = ["coinhive.com", "coin-hive.com", "jsecoin.com"]

        for domain in cryptomining:
            self.assertTrue(
                self.db.is_blocked(domain),
                f"Cryptomining domain {domain} should be blocked",
            )


class TestAdAnnihilator(unittest.TestCase):
    """Test HOLY WAR engine"""

    def setUp(self):
        """Setup test fixtures"""
        self.config = {
            "nuclear_level": True,
            "block_popups": True,
            "block_redirects": True,
            "kill_autoplay": True,
            "block_trackers": True,
        }
        self.annihilator = AdAnnihilator(self.config)

    def tearDown(self):
        """Cleanup"""
        if self.annihilator._active:
            self.annihilator.stop()

    def test_annihilator_initialization(self):
        """Test HOLY WAR engine initializes correctly"""
        self.assertFalse(self.annihilator._active)
        self.assertTrue(self.annihilator.config["nuclear_level"])

        # Verify ad domains loaded
        self.assertGreater(len(self.annihilator.ad_domains), 0)

        # Verify patterns loaded
        self.assertGreater(len(self.annihilator.ad_patterns), 0)

    def test_annihilator_start_stop(self):
        """Test starting and stopping holy war"""
        self.annihilator.start()
        self.assertTrue(self.annihilator._active)

        self.annihilator.stop()
        self.assertFalse(self.annihilator._active)

    def test_ad_url_blocked(self):
        """Test ad URLs are blocked"""
        ad_urls = [
            "https://doubleclick.net/ad?id=123",
            "https://googlesyndication.com/adsbygoogle.js",
            "https://outbrain.com/widget",
            "https://taboola.com/rec",
        ]

        self.annihilator.start()

        for url in ad_urls:
            result = self.annihilator.check_url(url)
            self.assertTrue(result["should_block"], f"{url} should be blocked")
            self.assertIn("reason", result)

    def test_legit_url_allowed(self):
        """Test legitimate URLs are not blocked"""
        legit_urls = [
            "https://example.com",
            "https://github.com/project",
            "https://stackoverflow.com/questions",
        ]

        self.annihilator.start()

        for url in legit_urls:
            result = self.annihilator.check_url(url)
            self.assertFalse(result["should_block"], f"{url} should not be blocked")

    def test_ad_patterns_detected(self):
        """Test ad pattern matching"""
        self.annihilator.start()

        ad_urls = [
            "https://example.com/ads/banner.jpg",
            "https://example.com/advertisement.html",
            "https://example.com/track?ad=123",
        ]

        for url in ad_urls:
            result = self.annihilator.check_url(url)
            # Should be blocked due to pattern match
            self.assertTrue(result["should_block"])

    def test_ad_element_detection(self):
        """Test HTML element ad detection"""
        self.annihilator.start()

        # Ad element with ad class
        result = self.annihilator.check_element(
            '<div class="ad-container"></div>', "ad-container", ""
        )
        self.assertTrue(result["should_block"])

        # Ad element with ad ID
        result = self.annihilator.check_element(
            '<div id="advertising"></div>', "", "advertising"
        )
        self.assertTrue(result["should_block"])

    def test_script_blocking(self):
        """Test ad script blocking"""
        self.annihilator.start()

        # Known ad script
        ad_script = "https://googlesyndication.com/adsbygoogle.js"
        self.assertTrue(self.annihilator.block_script(ad_script))

        # Legitimate script
        legit_script = "https://example.com/app.js"
        self.assertFalse(self.annihilator.block_script(legit_script))

    def test_popup_blocking_always_active(self):
        """Test popups are always blocked in HOLY WAR mode"""
        self.annihilator.start()

        # Should always return True in holy war mode
        blocked = self.annihilator.intercept_popup()
        self.assertTrue(blocked)

        # Verify stats updated
        stats = self.annihilator.get_stats()
        self.assertGreater(stats["popups_obliterated"], 0)

    def test_redirect_interception(self):
        """Test suspicious redirects are blocked"""
        self.annihilator.start()

        # Suspicious redirect to ad domain
        ad_redirect = "https://doubleclick.net/redirect"
        self.assertTrue(self.annihilator.intercept_redirect(ad_redirect))

        # Normal redirect
        normal_redirect = "https://example.com/page"
        self.assertFalse(self.annihilator.intercept_redirect(normal_redirect))

    def test_autoplay_killing(self):
        """Test autoplay is always killed"""
        self.annihilator.start()

        # Should always kill autoplay
        killed = self.annihilator.kill_autoplay()
        self.assertTrue(killed)

        # Verify stats
        stats = self.annihilator.get_stats()
        self.assertGreater(stats["autoplay_killed"], 0)

    def test_tracker_blocking(self):
        """Test tracker domains are blocked"""
        self.annihilator.start()

        tracker_urls = [
            "https://google-analytics.com/collect",
            "https://facebook.com/tr",
            "https://connect.facebook.net/pixel",
        ]

        for url in tracker_urls:
            result = self.annihilator.check_url(url)
            self.assertTrue(result["should_block"])

    def test_stats_tracking(self):
        """Test blocking statistics are tracked"""
        self.annihilator.start()

        # Block some URLs
        self.annihilator.check_url("https://doubleclick.net/ad")
        self.annihilator.intercept_popup()
        self.annihilator.kill_autoplay()

        stats = self.annihilator.get_stats()

        self.assertIn("ads_blocked", stats)
        self.assertIn("trackers_destroyed", stats)  # Changed from trackers_blocked
        self.assertIn("popups_obliterated", stats)  # Changed from popups_blocked
        self.assertIn("autoplay_killed", stats)
        self.assertGreater(stats["ads_blocked"], 0)

    def test_holy_war_status(self):
        """Test status shows HOLY WAR mode active"""
        self.annihilator.start()

        status = self.annihilator.get_status()

        self.assertTrue(status["active"])
        self.assertTrue(status["holy_war_mode"])
        self.assertIn("ad_domains_blocked", status)  # Changed from domains_blocked
        self.assertIn("ad_patterns", status)  # Changed from patterns_loaded


class TestTrackerDestroyer(unittest.TestCase):
    """Test tracker destruction"""

    def setUp(self):
        """Setup test fixtures"""
        self.destroyer = TrackerDestroyer()

    def test_tracker_destroyer_initialization(self):
        """Test destroyer loads tracker database"""
        self.assertGreater(len(self.destroyer._tracker_domains), 0)

    def test_known_trackers_blocked(self):
        """Test known tracking domains are blocked"""
        # Test trackers that are actually in our database
        trackers = ["google-analytics.com", "facebook.com/tr", "mixpanel.com"]

        for tracker in trackers:
            self.assertTrue(self.destroyer.should_block(tracker))

    def test_tracking_scripts_blocked(self):
        """Test tracking scripts are identified and blocked"""
        # Test URLs containing known tracker domains
        tracking_urls = [
            "https://google-analytics.com/analytics.js",
            "https://mixpanel.com/tracking.js",
            "https://segment.com/pixel.js",
        ]

        for url in tracking_urls:
            self.assertTrue(self.destroyer.should_block(url))


class TestAutoplayKiller(unittest.TestCase):
    """Test autoplay killer"""

    def setUp(self):
        """Setup test fixtures"""
        self.killer = AutoplayKiller()

    def test_autoplay_killer_initialization(self):
        """Test autoplay killer initializes"""
        self.assertIsNotNone(self.killer)

    def test_autoplay_always_blocked(self):
        """Test autoplay is always blocked"""
        # Should always return True
        self.assertTrue(self.killer.block_autoplay())

    def test_video_autoplay_killed(self):
        """Test video autoplay detection"""
        video_element = '<video autoplay src="ad.mp4"></video>'
        self.assertTrue(self.killer.is_autoplay(video_element))

    def test_audio_autoplay_killed(self):
        """Test audio autoplay detection"""
        audio_element = '<audio autoplay src="ad.mp3"></audio>'
        self.assertTrue(self.killer.is_autoplay(audio_element))


class TestAdAnnihilatorIntegration(unittest.TestCase):
    """Integration tests for complete ad annihilation workflow"""

    def setUp(self):
        """Setup test fixtures"""
        self.config = {"nuclear_level": True}
        self.annihilator = AdAnnihilator(self.config)
        self.annihilator.start()

    def tearDown(self):
        """Cleanup"""
        if self.annihilator._active:
            self.annihilator.stop()

    def test_complete_ad_blocking_workflow(self):
        """Test complete workflow of blocking ads, popups, trackers"""
        # Block ad URL
        ad_result = self.annihilator.check_url("https://doubleclick.net/ad")
        self.assertTrue(ad_result["should_block"])

        # Block popup
        popup_blocked = self.annihilator.intercept_popup()
        self.assertTrue(popup_blocked)

        # Kill autoplay
        autoplay_killed = self.annihilator.kill_autoplay()
        self.assertTrue(autoplay_killed)

        # Verify all stats updated
        stats = self.annihilator.get_stats()
        self.assertGreater(stats["ads_blocked"], 0)
        self.assertGreater(stats["popups_obliterated"], 0)
        self.assertGreater(stats["autoplay_killed"], 0)

    def test_malvertising_protection(self):
        """Test protection against malicious advertising"""
        malvertising_url = "https://malicious-ads.com/scam"

        result = self.annihilator.check_url(malvertising_url)
        self.assertTrue(result["should_block"])
        self.assertIn("malvertising", result["reason"].lower())


if __name__ == "__main__":
    unittest.main()
