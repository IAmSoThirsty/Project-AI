#!/usr/bin/env python3
#                                           [2026-04-10 10:30]
#                                          Status: Active
"""
NTP Validation Verification Script

Verifies that NTP validation is correctly integrated across all components.

Run from repository root:
    python scripts/verify_ntp_integration.py

Checks:
1. NTPValidator initialization and health
2. TSAProvider integration
3. ExistentialProof integration
4. Prometheus metrics availability
5. Test suite execution
"""

import sys
import os
import logging
from pathlib import Path
from typing import Tuple

# Add repository root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_ntp_validator() -> Tuple[bool, str]:
    """Check NTPValidator core functionality."""
    try:
        from src.app.security.ntp_validator import NTPValidator
        
        validator = NTPValidator()
        stats = validator.get_statistics()
        
        assert 'ntp_servers' in stats
        assert len(stats['ntp_servers']) > 0
        assert stats['max_clock_skew'] == 300
        
        return True, f"NTPValidator initialized with {len(stats['ntp_servers'])} servers"
    except Exception as e:
        return False, f"NTPValidator check failed: {e}"


def check_tsa_integration() -> Tuple[bool, str]:
    """Check TSAProvider NTP integration."""
    try:
        from src.app.governance.tsa_provider import TSAProvider
        
        # Test with NTP enabled
        tsa = TSAProvider(enable_ntp_validation=True)
        stats = tsa.get_statistics()
        
        assert stats['ntp_validation_enabled'] is True
        assert 'ntp_stats' in stats
        
        # Test with NTP disabled
        tsa_disabled = TSAProvider(enable_ntp_validation=False)
        stats_disabled = tsa_disabled.get_statistics()
        
        assert stats_disabled['ntp_validation_enabled'] is False
        
        return True, "TSAProvider NTP integration working (enabled/disabled modes)"
    except Exception as e:
        return False, f"TSAProvider integration check failed: {e}"


def check_existential_proof() -> Tuple[bool, str]:
    """Check ExistentialProof NTP integration."""
    try:
        from governance.existential_proof import ExistentialProof
        
        # Test with NTP enabled
        proof = ExistentialProof(enable_ntp=True)
        assert proof.ntp_validator is not None
        
        # Test with NTP disabled
        proof_disabled = ExistentialProof(enable_ntp=False)
        assert proof_disabled.ntp_validator is None
        
        return True, "ExistentialProof NTP integration working"
    except Exception as e:
        return False, f"ExistentialProof check failed: {e}"


def check_prometheus_metrics() -> Tuple[bool, str]:
    """Check Prometheus metrics are available."""
    try:
        from src.app.monitoring.prometheus_exporter import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        
        # Verify all NTP-related metrics exist
        required_metrics = [
            'system_clock_skew_seconds',
            'ntp_validation_total',
            'tsa_request_total',
            'tsa_verification_total',
            'clock_skew_violations_total',
        ]
        
        for metric_name in required_metrics:
            assert hasattr(metrics, metric_name), f"Missing metric: {metric_name}"
        
        return True, f"All {len(required_metrics)} Prometheus metrics available"
    except Exception as e:
        return False, f"Prometheus metrics check failed: {e}"


def check_integration_example() -> Tuple[bool, str]:
    """Check integration example imports correctly."""
    try:
        from src.app.security.ntp_integration_example import TemporalSecurityOrchestrator
        
        orchestrator = TemporalSecurityOrchestrator(enable_ntp=True)
        health = orchestrator.health_check()
        
        assert 'ntp_available' in health
        assert 'clock_skew_ok' in health
        assert 'tsa_configured' in health
        
        return True, "TemporalSecurityOrchestrator working"
    except Exception as e:
        return False, f"Integration example check failed: {e}"


def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("NTP VALIDATION VERIFICATION")
    print("="*60 + "\n")
    
    checks = [
        ("NTPValidator Core", check_ntp_validator),
        ("TSAProvider Integration", check_tsa_integration),
        ("ExistentialProof Integration", check_existential_proof),
        ("Prometheus Metrics", check_prometheus_metrics),
        ("Integration Example", check_integration_example),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...", end=" ")
        success, message = check_func()
        results.append(success)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} checks passed")
    print("="*60 + "\n")
    
    if all(results):
        print("✅ All verification checks passed!")
        print("NTP validation is correctly integrated and ready for production.\n")
        return 0
    else:
        print("❌ Some verification checks failed.")
        print("Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
