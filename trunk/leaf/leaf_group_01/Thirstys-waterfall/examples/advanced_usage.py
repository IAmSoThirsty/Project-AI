# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / advanced_usage.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / advanced_usage.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Example: Advanced configuration and VPN usage
"""

from thirstys_waterfall import ThirstysWaterfall
import time


def main():
    # Initialize with custom config
    print("Initializing Thirstys Waterfall with maximum privacy...")
    waterfall = ThirstysWaterfall()

    # Override config for demonstration
    waterfall.config.set("vpn.multi_hop", True)
    waterfall.config.set("vpn.hop_count", 5)
    waterfall.config.set("browser.fingerprint_protection", True)
    waterfall.config.set("privacy.anti_fingerprint", True)

    # Start system
    print("\nStarting all subsystems...")
    waterfall.start()

    # Show VPN status (BUILT-IN VPN)
    print("\n" + "=" * 60)
    print("BUILT-IN VPN STATUS")
    print("=" * 60)
    vpn_status = waterfall.vpn.get_status()
    print(f"  Connected: {vpn_status['connected']}")
    print(f"  Multi-hop: {vpn_status['multi_hop']}")
    print(f"  Route hops: {len(vpn_status['route'])}")
    print(f"  Kill switch: {vpn_status['kill_switch']}")
    print(f"  DNS protected: {vpn_status['dns_protected']}")
    print(f"  Stealth mode: {vpn_status['stealth_mode']}")

    # Show firewall statistics (ALL 8 TYPES)
    print("\n" + "=" * 60)
    print("FIREWALL STATISTICS (8 Types)")
    print("=" * 60)
    fw_stats = waterfall.firewall.get_statistics()
    for fw_type, stats in fw_stats.items():
        print(f"\n  {fw_type.upper()}:")
        print(f"    Packets inspected: {stats['packets_inspected']}")
        print(f"    Packets allowed: {stats['packets_allowed']}")
        print(f"    Packets blocked: {stats['packets_blocked']}")
        print(f"    Threats detected: {stats['threats_detected']}")

    # Test browser with privacy features
    print("\n" + "=" * 60)
    print("BROWSER PRIVACY FEATURES")
    print("=" * 60)
    browser_status = waterfall.browser.get_status()
    print(f"  Incognito mode: {browser_status['incognito_mode']}")
    print(f"  No history: {browser_status['no_history']}")
    print(f"  No cache: {browser_status['no_cache']}")
    print(f"  No cookies: {browser_status['no_cookies']}")
    print(f"  No pop-ups: {browser_status['no_popups']}")
    print(f"  No redirects: {browser_status['no_redirects']}")
    print(f"  Tab isolation: {browser_status['tab_isolation']}")
    print(f"  Fingerprint protection: {browser_status['fingerprint_protection']}")
    print(f"  Tracker blocking: {browser_status['tracker_blocking']}")

    # Show anti-fingerprinting status
    print("\n" + "=" * 60)
    print("ANTI-FINGERPRINTING PROTECTION")
    print("=" * 60)
    fp_status = waterfall.anti_fingerprint.get_protection_status()
    for feature, enabled in fp_status.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}")

    # Privacy audit
    print("\n" + "=" * 60)
    print("PRIVACY AUDIT")
    print("=" * 60)
    audit = waterfall.run_privacy_audit()
    print(f"  DNS leak test: {'PASS' if audit['dns_leak'] else 'FAIL'}")
    print(f"  IPv6 leak test: {'PASS' if audit['ipv6_leak'] else 'FAIL'}")
    print(f"  WebRTC leak test: {'PASS' if audit['webrtc_leak'] else 'FAIL'}")
    print(f"  Privacy violations: {audit['violations']}")
    print(f"  Events logged: {audit['events_logged']}")

    # Test VPN reconnection
    print("\n" + "=" * 60)
    print("TESTING VPN RECONNECTION")
    print("=" * 60)
    print("  Reconnecting VPN...")
    waterfall.vpn.reconnect()
    time.sleep(1)
    print("  VPN reconnected successfully")

    # Stop system
    print("\n" + "=" * 60)
    print("Stopping Thirstys Waterfall...")
    waterfall.stop()
    print("System stopped. All data wiped (ephemeral storage).")
    print("=" * 60)


if __name__ == "__main__":
    main()
