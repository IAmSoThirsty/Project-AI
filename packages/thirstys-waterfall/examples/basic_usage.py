"""
Example: Basic usage of Thirstys Waterfall
"""

from thirstys_waterfall import ThirstysWaterfall


def main():
    # Initialize Thirstys Waterfall
    print("Initializing Thirstys Waterfall...")
    waterfall = ThirstysWaterfall()

    # Start all subsystems
    print("\nStarting system...")
    waterfall.start()

    # Create a browser tab
    print("\nCreating browser tab...")
    tab_id = waterfall.browser.create_tab()
    print(f"Tab created: {tab_id}")

    # Navigate (with privacy protection)
    print("\nNavigating to URL...")
    url = "https://example.com"
    allowed = waterfall.browser.navigate(tab_id, url)
    print(f"Navigation {'allowed' if allowed else 'blocked'}")

    # Get system status
    print("\nSystem Status:")
    status = waterfall.get_status()
    print(f"  Active: {status['active']}")
    print(f"  Kill Switch: {status['kill_switch']['enabled']}")
    print(f"  VPN Connected: {status['vpn']['connected']}")
    print(f"  Browser Tabs: {status['browser']['open_tabs']}")
    print(f"  Pop-ups Blocked: {status['browser']['no_popups']}")
    print(f"  Redirects Blocked: {status['browser']['no_redirects']}")

    # Run privacy audit
    print("\nRunning privacy audit...")
    audit = waterfall.run_privacy_audit()
    print(f"  DNS Leak: {'Protected' if audit['dns_leak'] else 'LEAK DETECTED'}")
    print(f"  IPv6 Leak: {'Protected' if audit['ipv6_leak'] else 'LEAK DETECTED'}")
    print(f"  WebRTC Leak: {'Protected' if audit['webrtc_leak'] else 'LEAK DETECTED'}")

    # Stop system
    print("\nStopping system...")
    waterfall.stop()
    print("Done!")


if __name__ == "__main__":
    main()
