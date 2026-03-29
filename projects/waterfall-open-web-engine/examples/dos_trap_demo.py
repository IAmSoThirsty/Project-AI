# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / dos_trap_demo.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / dos_trap_demo.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python3
"""
DOS Trap Mode Demonstration
Shows comprehensive system compromise detection and response capabilities.
"""

import logging
import time
import os
import secrets
from thirstys_waterfall.security import (
    DOSTrapMode,
    create_dos_trap,
    ThreatLevel,
    SanitizationMode,
)
from thirstys_waterfall.security.hardware_root_of_trust import HardwareRootOfTrust
from thirstys_waterfall.kill_switch import GlobalKillSwitch


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def generate_demo_secret(length: int = 24) -> bytes:
    """
    Generate a cryptographically secure random secret for demonstration purposes.

    SECURITY NOTE: This function generates random secrets for demo/testing only.
    In production, secrets MUST be:
    - Loaded from environment variables (e.g., os.environ.get('SECRET_NAME'))
    - Retrieved from a secure vault (e.g., HashiCorp Vault, AWS Secrets Manager)
    - Never hardcoded in source code or configuration files

    Args:
        length: Length of the secret in bytes

    Returns:
        Cryptographically secure random bytes
    """
    return secrets.token_bytes(length)


def get_demo_credentials() -> dict:
    """
    Get demo credentials from environment or generate safe demo values.

    SECURITY NOTE: In production environments, credentials MUST be:
    - Loaded from environment variables
    - Retrieved from secure secret management systems
    - Rotated regularly according to security policy
    - Never logged, committed to source control, or stored in plaintext

    Environment variables (optional for demo):
    - DEMO_MASTER_ENCRYPTION_KEY: Master encryption key (base64 encoded)
    - DEMO_MASTER_SIGNING_KEY: Master signing key (base64 encoded)
    - DEMO_ROOT_KEY: Root key (base64 encoded)
    - DEMO_USER_PASSWORD: User password for demo
    - DEMO_API_TOKEN: API token for demo

    Returns:
        Dictionary containing demo credentials (randomly generated if not in env)
    """
    import base64

    # Try to load from environment, generate random if not present
    # This demonstrates the secure pattern: env vars > secure vault > NEVER hardcode

    master_encryption_key = os.environ.get("DEMO_MASTER_ENCRYPTION_KEY")
    if master_encryption_key:
        master_encryption_key = base64.b64decode(master_encryption_key)
    else:
        master_encryption_key = generate_demo_secret(24)
        print("  ℹ️  Generated random master_encryption_key (not from env)")

    master_signing_key = os.environ.get("DEMO_MASTER_SIGNING_KEY")
    if master_signing_key:
        master_signing_key = base64.b64decode(master_signing_key)
    else:
        master_signing_key = generate_demo_secret(24)
        print("  ℹ️  Generated random master_signing_key (not from env)")

    root_key = os.environ.get("DEMO_ROOT_KEY")
    if root_key:
        root_key = base64.b64decode(root_key)
    else:
        root_key = generate_demo_secret(20)
        print("  ℹ️  Generated random root_key (not from env)")

    return {
        "master_keys": {
            "master_encryption_key": master_encryption_key,
            "master_signing_key": master_signing_key,
            "root_key": root_key,
        },
        "session_keys": {
            "session_1": generate_demo_secret(16),
            "session_2": generate_demo_secret(16),
        },
        "credentials": {
            "user_password": os.environ.get(
                "DEMO_USER_PASSWORD", f"demo_pass_{secrets.token_hex(8)}"
            ),
            "api_token": os.environ.get(
                "DEMO_API_TOKEN", f"demo_token_{secrets.token_hex(16)}"
            ),
        },
    }


def threat_response_callback(events):
    """Callback function for threat responses"""
    print("\n" + "=" * 80)
    print("THREAT RESPONSE CALLBACK TRIGGERED")
    print("=" * 80)
    for event in events:
        print("\nThreat Detected:")
        print(f"  Type: {event.compromise_type.value}")
        print(f"  Level: {event.threat_level.name}")
        print(f"  Description: {event.description}")
        print(f"  Indicators: {', '.join(event.indicators)}")
        print(f"  Affected: {', '.join(event.affected_components)}")
    print("=" * 80 + "\n")


def demo_basic_usage():
    """Demonstrate basic DOS trap mode usage"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Basic Usage Demo")
    print("=" * 80 + "\n")

    # Create DOS trap instance
    dos_trap = create_dos_trap()

    # Register response callback
    dos_trap.register_response_callback(threat_response_callback)

    # Enable monitoring
    print("Enabling DOS trap mode...")
    dos_trap.enable()

    # Check status
    status = dos_trap.get_status()
    print("\nDOS Trap Status:")
    print(f"  Active: {status['active']}")
    print(f"  Triggered: {status['triggered']}")
    print(f"  Threat Level: {status['threat_level']}")
    print(f"  Detected Threats: {status['detected_threats']}")

    # Let it monitor for a bit
    print("\nMonitoring for threats (10 seconds)...")
    time.sleep(10)

    # Disable
    print("\nDisabling DOS trap mode...")
    dos_trap.disable()

    # Get final report
    report = dos_trap.get_threat_report()
    print("\nFinal Threat Report:")
    print(f"  Total Threats: {report['total_threats']}")
    print(f"  Current Level: {report['current_threat_level']}")
    print(f"  System Compromised: {report['system_compromised']}")

    print("\n✓ Basic usage demo completed\n")


def demo_hardware_integration():
    """Demonstrate DOS trap with Hardware Root-of-Trust integration"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Hardware Integration Demo")
    print("=" * 80 + "\n")

    # Initialize hardware root of trust
    print("Initializing Hardware Root-of-Trust...")
    hw_trust = HardwareRootOfTrust()
    hw_trust.initialize()

    # Create global kill switch
    print("Initializing Global Kill Switch...")
    kill_switch = GlobalKillSwitch()
    kill_switch.enable()

    # Create DOS trap with integrations
    print("Creating DOS trap with hardware integration...")
    dos_trap = DOSTrapMode(hardware_root_of_trust=hw_trust, kill_switch=kill_switch)
    dos_trap.initialize()

    # Configure for high security
    dos_trap.config["auto_respond"] = True
    dos_trap.config["response_threshold"] = ThreatLevel.MODERATE
    dos_trap.config["monitor_interval"] = 30

    print("\nDOS Trap Configuration:")
    print(f"  Auto Respond: {dos_trap.config['auto_respond']}")
    print(f"  Response Threshold: {dos_trap.config['response_threshold'].name}")
    print(f"  Monitor Interval: {dos_trap.config['monitor_interval']}s")

    # Enable monitoring
    dos_trap.enable()
    print("\nHardware-integrated monitoring active...")
    time.sleep(5)

    # Disable
    dos_trap.disable()
    kill_switch.disable()

    print("\n✓ Hardware integration demo completed\n")


def demo_compromise_detection():
    """Demonstrate compromise detection capabilities"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Compromise Detection Demo")
    print("=" * 80 + "\n")

    dos_trap = create_dos_trap()

    print("Performing comprehensive system scan...")

    # Manual scan
    events = dos_trap.compromise_detector.comprehensive_scan()

    if events:
        print(f"\n⚠️  {len(events)} threats detected:")
        for event in events:
            print(f"\n  {event.compromise_type.value.upper()}")
            print(f"    Level: {event.threat_level.name}")
            print(f"    Description: {event.description}")
    else:
        print("\n✓ No threats detected - system appears clean")

    # Test individual detection methods
    print("\n\nTesting individual detection methods:")

    print("\n1. Rootkit Detection...")
    rootkit_event = dos_trap.compromise_detector.detect_rootkit()
    if rootkit_event:
        print(f"   ⚠️  Rootkit detected: {rootkit_event.description}")
    else:
        print("   ✓ No rootkits detected")

    print("\n2. Kernel Hook Detection...")
    hook_event = dos_trap.compromise_detector.detect_kernel_hooks()
    if hook_event:
        print(f"   ⚠️  Kernel hooks detected: {hook_event.description}")
    else:
        print("   ✓ No kernel hooks detected")

    print("\n3. Memory Anomaly Detection...")
    memory_event = dos_trap.compromise_detector.detect_memory_anomalies()
    if memory_event:
        print(f"   ⚠️  Memory anomalies detected: {memory_event.description}")
    else:
        print("   ✓ No memory anomalies detected")

    print("\n4. Process Injection Detection...")
    injection_event = dos_trap.compromise_detector.detect_process_injection()
    if injection_event:
        print(f"   ⚠️  Process injection detected: {injection_event.description}")
    else:
        print("   ✓ No process injection detected")

    print("\n✓ Compromise detection demo completed\n")


def demo_secret_wiping():
    """Demonstrate secret wiping capabilities"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Secret Wiping Demo")
    print("=" * 80 + "\n")

    dos_trap = create_dos_trap()

    # Generate secure demo secrets (NEVER hardcode in production!)
    print("🔐 SECURITY NOTE: Generating cryptographically secure demo secrets...")
    print("    In production, load secrets from environment variables or secure vault!")
    print("    See get_demo_credentials() for the secure pattern.\n")

    demo_creds = get_demo_credentials()
    master_keys = demo_creds["master_keys"]
    session_keys = demo_creds["session_keys"]
    credentials = demo_creds["credentials"]

    print("Simulated secret storage (randomly generated):")
    print(f"  Master Keys: {len(master_keys)}")
    print(f"  Session Keys: {len(session_keys)}")
    print(f"  Credentials: {len(credentials)}")

    # Wipe master keys
    print("\n1. Wiping master keys...")
    dos_trap.secret_wiper.wipe_master_keys(master_keys)
    print(f"   Remaining master keys: {len(master_keys)}")

    # Wipe session keys
    print("\n2. Wiping session keys...")
    dos_trap.secret_wiper.wipe_session_keys(session_keys)
    print(f"   Remaining session keys: {len(session_keys)}")

    # Wipe credentials
    print("\n3. Wiping credentials...")
    dos_trap.secret_wiper.wipe_credentials(credentials)
    print(f"   Remaining credentials: {len(credentials)}")

    # Emergency wipe
    print("\n4. Emergency wipe all secrets...")
    dos_trap.secret_wiper.emergency_wipe_all()
    print("   ✓ Emergency wipe completed")

    print("\n✓ Secret wiping demo completed\n")


def demo_memory_sanitization():
    """Demonstrate RAM sanitization"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Memory Sanitization Demo")
    print("=" * 80 + "\n")

    dos_trap = create_dos_trap()

    print("Memory sanitization modes:")
    print("  1. SINGLE_PASS - Quick wipe (1 pass)")
    print("  2. THREE_PASS - Standard wipe (3 passes)")
    print("  3. SEVEN_PASS_DOD - DoD 5220.22-M (7 passes)")
    print("  4. GUTMANN - Maximum security (35 passes)")
    print("  5. CRYPTO_ERASE - Cryptographic erasure (1 pass)")

    print("\nPerforming single-pass RAM sanitization...")
    dos_trap.memory_sanitizer.sanitize_ram(SanitizationMode.SINGLE_PASS)
    print("✓ RAM sanitization completed")

    print("\n✓ Memory sanitization demo completed\n")


def demo_disk_sanitization():
    """Demonstrate disk sanitization"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Disk Sanitization Demo")
    print("=" * 80 + "\n")

    dos_trap = create_dos_trap()

    # Create temporary test file
    import tempfile
    import os

    test_file = tempfile.NamedTemporaryFile(delete=False)
    test_file.write(b"Sensitive data that must be securely deleted" * 100)
    test_file.close()

    print(f"Created test file: {test_file.name}")
    print(f"File size: {os.path.getsize(test_file.name)} bytes")

    print("\nPerforming three-pass secure deletion...")
    dos_trap.disk_sanitizer.sanitize_file(test_file.name, SanitizationMode.THREE_PASS)

    if not os.path.exists(test_file.name):
        print("✓ File securely deleted and removed")
    else:
        print("⚠️  File still exists")
        os.remove(test_file.name)

    print("\n✓ Disk sanitization demo completed\n")


def demo_interface_disabling():
    """Demonstrate interface disabling (simulation only)"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Interface Disabling Demo (Simulation)")
    print("=" * 80 + "\n")

    create_dos_trap()

    print("⚠️  NOTE: This is a simulation. Actual interface disabling")
    print("    requires elevated privileges and will disconnect your system.\n")

    print("Interface disabling capabilities:")
    print("  1. Network interfaces (Ethernet, WiFi)")
    print("  2. USB interfaces (all USB devices)")
    print("  3. All I/O interfaces (complete isolation)")

    print("\nSimulation would:")
    print("  • Disable all network adapters")
    print("  • Unbind USB devices")
    print("  • Block all external I/O")
    print("  • Isolate system from network")

    print("\n✓ Interface disabling demo completed\n")


def demo_manual_trigger():
    """Demonstrate manual trigger"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Manual Trigger Demo")
    print("=" * 80 + "\n")

    dos_trap = create_dos_trap()
    dos_trap.register_response_callback(threat_response_callback)

    # Configure for immediate response but don't auto-sanitize
    dos_trap.config["auto_respond"] = True
    dos_trap.config["auto_sanitize"] = False
    dos_trap.config["emergency_shutdown"] = False

    print("Manually triggering DOS trap for testing...")
    print("Reason: Security audit - testing emergency procedures\n")

    dos_trap.manual_trigger("Security audit - testing emergency procedures")

    time.sleep(2)

    # Check status
    status = dos_trap.get_status()
    print("\nPost-Trigger Status:")
    print(f"  Triggered: {status['triggered']}")
    print(f"  Threat Level: {status['threat_level']}")
    print(f"  Detected Threats: {status['detected_threats']}")

    print("\n✓ Manual trigger demo completed\n")


def demo_threat_reporting():
    """Demonstrate comprehensive threat reporting"""
    print("\n" + "=" * 80)
    print("DOS TRAP MODE - Threat Reporting Demo")
    print("=" * 80 + "\n")

    dos_trap = create_dos_trap()

    # Perform scan
    dos_trap.enable()
    time.sleep(3)
    dos_trap.disable()

    # Get comprehensive report
    report = dos_trap.get_threat_report()

    print("Comprehensive Threat Report:")
    print("=" * 60)
    print(f"Total Threats Detected: {report['total_threats']}")
    print(f"Current Threat Level: {report['current_threat_level']}")
    print(
        f"System Status: {'COMPROMISED' if report['system_compromised'] else 'CLEAN'}"
    )

    if report["threats_by_type"]:
        print("\nThreats by Type:")
        for threat_type, count in report["threats_by_type"].items():
            print(f"  {threat_type}: {count}")

    print("\n✓ Threat reporting demo completed\n")


def main():
    """Run all demos"""
    setup_logging()

    print("\n" + "=" * 80)
    print("THIRSTY'S WATERFALL - DOS TRAP MODE DEMONSTRATION")
    print("Production-Grade System Compromise Detection and Response")
    print("=" * 80)

    try:
        # Run demos
        demo_basic_usage()
        demo_compromise_detection()
        demo_secret_wiping()
        demo_memory_sanitization()
        demo_disk_sanitization()
        demo_interface_disabling()
        demo_manual_trigger()
        demo_threat_reporting()
        demo_hardware_integration()

        print("\n" + "=" * 80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
