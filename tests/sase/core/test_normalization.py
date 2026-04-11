import pytest
import urllib.error
from unittest.mock import patch, MagicMock
from src.cerberus.sase.core.normalization import (
    TorDetector,
    VPNDetector,
    EventEnrichmentPipeline,
)

@patch("urllib.request.urlopen")
def test_tor_detector_success(mock_urlopen):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.read.return_value = b"""ExitNode 64D74AAA74F30DC2CFB36343CE5D4451B9A4DBA8
Published 2026-03-13 16:01:48
LastStatus 2026-03-14 02:00:00
ExitAddress 171.25.193.25 2026-03-14 02:18:22
ExitNode 0DC16FEAA5A5E27A974009CBF7748BB6FAAE6DE1
Published 2026-03-13 15:17:13
LastStatus 2026-03-14 02:00:00
ExitAddress 80.67.167.81 2026-03-14 02:38:26
"""
    # mock context manager
    mock_urlopen.return_value.__enter__.return_value = mock_response

    detector = TorDetector()

    # Assert
    assert "171.25.193.25" in detector.tor_exit_nodes
    assert "80.67.167.81" in detector.tor_exit_nodes
    assert len(detector.tor_exit_nodes) == 2
    assert detector.is_tor_exit("171.25.193.25") is True
    assert detector.is_tor_exit("1.1.1.1") is False

@patch("urllib.request.urlopen")
def test_tor_detector_empty_response(mock_urlopen):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.read.return_value = b"Some random content\nNo valid IPs here"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    detector = TorDetector()

    # Assert fallback was used
    assert "185.220.101.1" in detector.tor_exit_nodes
    assert "185.220.101.2" in detector.tor_exit_nodes
    assert len(detector.tor_exit_nodes) == 2

@patch("urllib.request.urlopen")
def test_tor_detector_http_error(mock_urlopen):
    # Setup mock to raise URLError
    mock_urlopen.side_effect = urllib.error.URLError("Network error")

    detector = TorDetector()

    # Assert fallback was used
    assert "185.220.101.1" in detector.tor_exit_nodes
    assert "185.220.101.2" in detector.tor_exit_nodes
    assert len(detector.tor_exit_nodes) == 2

@patch("urllib.request.urlopen")
def test_tor_detector_timeout(mock_urlopen):
    # Setup mock to raise TimeoutError
    mock_urlopen.side_effect = TimeoutError("Timeout")

    detector = TorDetector()

    # Assert fallback was used
    assert "185.220.101.1" in detector.tor_exit_nodes
    assert "185.220.101.2" in detector.tor_exit_nodes
    assert len(detector.tor_exit_nodes) == 2


class TestVPNDetector:
    """Test suite for VPN detection"""

    def test_vpn_detector_initialization(self):
        """Test VPN detector initializes with known ASNs"""
        detector = VPNDetector()
        
        assert len(detector.vpn_asns) > 0
        assert "AS13335" in detector.vpn_asns  # Cloudflare WARP
        assert "AS16509" in detector.vpn_asns  # Amazon AWS
        assert len(detector.ip_cache) == 0

    def test_vpn_detection_via_known_asn(self):
        """Test VPN detection using known VPN ASN"""
        detector = VPNDetector()
        
        # Test with known VPN ASN
        assert detector.is_vpn("1.2.3.4", "AS13335") is True  # Cloudflare WARP
        assert detector.is_vpn("5.6.7.8", "AS62240") is True  # Clouvider
        
    def test_vpn_detection_via_hosting_asn(self):
        """Test VPN detection using hosting provider ASN"""
        detector = VPNDetector()
        
        # Test with hosting provider commonly used by VPNs
        assert detector.is_vpn("10.20.30.40", "AS14061") is True  # DigitalOcean
        assert detector.is_vpn("50.60.70.80", "AS16276") is True  # OVH

    def test_vpn_detection_non_vpn_asn(self):
        """Test that non-VPN ASNs are not flagged"""
        detector = VPNDetector()
        
        # Test with non-VPN ASN
        assert detector.is_vpn("8.8.8.8", "AS15169") is False  # Google Public DNS
        assert detector.is_vpn("1.1.1.1", "AS13333") is False  # Cloudflare DNS (not WARP)

    def test_vpn_detection_no_asn(self):
        """Test VPN detection without ASN information"""
        detector = VPNDetector()
        
        # Without ASN, should return False (no other detection methods active)
        assert detector.is_vpn("192.168.1.1", None) is False
        assert detector.is_vpn("10.0.0.1", None) is False

    def test_vpn_ip_caching(self):
        """Test that VPN detection results are cached"""
        detector = VPNDetector()
        
        # First call - no cache
        result1 = detector.is_vpn("1.2.3.4", "AS13335")
        assert result1 is True
        assert "1.2.3.4" in detector.ip_cache
        
        # Second call - should use cache
        result2 = detector.is_vpn("1.2.3.4", "AS99999")  # Different ASN, but cached
        assert result2 is True  # Returns cached result
        
    def test_vpn_cache_eviction(self):
        """Test cache eviction when max size reached"""
        detector = VPNDetector()
        detector.max_cache_size = 5  # Small cache for testing
        
        # Fill cache beyond max
        for i in range(10):
            detector.is_vpn(f"1.2.3.{i}", "AS99999")
        
        # Cache should not exceed max size
        assert len(detector.ip_cache) <= detector.max_cache_size

    def test_add_vpn_asn(self):
        """Test adding new VPN ASN dynamically"""
        detector = VPNDetector()
        
        # Add custom ASN
        detector.add_vpn_asn("AS12345")
        assert "AS12345" in detector.vpn_asns
        
        # Test detection with new ASN
        assert detector.is_vpn("100.200.1.1", "AS12345") is True

    def test_add_vpn_ip_range(self):
        """Test adding VPN IP ranges"""
        detector = VPNDetector()
        
        # Add custom IP range
        detector.add_vpn_ip_range("10.0.0.0", "10.0.0.255", "TestVPN")
        assert len(detector.vpn_ip_ranges) > 0
        
        # Test detection within range
        assert detector.is_vpn("10.0.0.100", None) is True
        assert detector.is_vpn("10.0.0.1", None) is True
        assert detector.is_vpn("10.0.1.1", None) is False  # Outside range

    def test_ip_to_int_conversion(self):
        """Test IP to integer conversion"""
        detector = VPNDetector()
        
        assert detector._ip_to_int("0.0.0.0") == 0
        assert detector._ip_to_int("255.255.255.255") == 4294967295
        assert detector._ip_to_int("192.168.1.1") == 3232235777
        assert detector._ip_to_int("10.0.0.1") == 167772161

    def test_ip_to_int_invalid(self):
        """Test IP to integer conversion with invalid input"""
        detector = VPNDetector()
        
        with pytest.raises(ValueError):
            detector._ip_to_int("invalid")
        
        with pytest.raises(ValueError):
            detector._ip_to_int("256.1.1.1")

    def test_ip_in_range(self):
        """Test IP range checking"""
        detector = VPNDetector()
        
        assert detector._ip_in_range("10.0.0.50", "10.0.0.0", "10.0.0.255") is True
        assert detector._ip_in_range("10.0.0.0", "10.0.0.0", "10.0.0.255") is True
        assert detector._ip_in_range("10.0.0.255", "10.0.0.0", "10.0.0.255") is True
        assert detector._ip_in_range("10.0.1.0", "10.0.0.0", "10.0.0.255") is False
        assert detector._ip_in_range("9.255.255.255", "10.0.0.0", "10.0.0.255") is False

    def test_multiple_vpn_detection_methods(self):
        """Test that detection works with multiple methods"""
        detector = VPNDetector()
        detector.add_vpn_ip_range("203.0.113.0", "203.0.113.255", "TestVPN")
        detector.add_vpn_asn("AS54321")
        
        # Test ASN-based detection
        assert detector.is_vpn("192.0.2.1", "AS54321") is True
        
        # Test IP range detection
        assert detector.is_vpn("203.0.113.50", None) is True
        
        # Test combination
        assert detector.is_vpn("203.0.113.100", "AS54321") is True
        
        # Test non-VPN
        assert detector.is_vpn("198.51.100.1", "AS99999") is False


@patch("urllib.request.urlopen")
class TestEnrichmentPipelineVPNIntegration:
    """Integration tests for VPN detection in enrichment pipeline"""

    def test_enrichment_pipeline_vpn_detection(self, mock_urlopen):
        """Test VPN detection integrated in enrichment pipeline"""
        # Mock Tor detector
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Create pipeline
        pipeline = EventEnrichmentPipeline()
        
        # Create mock event object with VPN ASN
        mock_event = MagicMock()
        mock_event.source_ip = "45.67.89.10"
        mock_event.asn = "AS13335"  # Cloudflare WARP (VPN)
        mock_event.artifact_id = "test-token-123"
        mock_event.event_id = "evt-001"
        mock_event.event_type = "token_access"
        
        # Test VPN detection directly
        is_vpn = pipeline.vpn_detector.is_vpn(mock_event.source_ip, mock_event.asn)
        
        # VPN should be detected
        assert is_vpn is True
        
    def test_enrichment_pipeline_non_vpn(self, mock_urlopen):
        """Test enrichment pipeline with non-VPN IP"""
        # Mock Tor detector
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Create pipeline
        pipeline = EventEnrichmentPipeline()
        
        # Create mock event with non-VPN ASN
        mock_event = MagicMock()
        mock_event.source_ip = "8.8.8.8"
        mock_event.asn = "AS15169"  # Google (not VPN)
        mock_event.artifact_id = "test-token-456"
        
        # Test VPN detection directly
        is_vpn = pipeline.vpn_detector.is_vpn(mock_event.source_ip, mock_event.asn)
        
        # VPN should NOT be detected
        assert is_vpn is False

    def test_enrichment_pipeline_hosting_provider(self, mock_urlopen):
        """Test enrichment pipeline with hosting provider (potential VPN)"""
        # Mock Tor detector
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Create pipeline
        pipeline = EventEnrichmentPipeline()
        
        # Create mock event with hosting provider ASN
        mock_event = MagicMock()
        mock_event.source_ip = "192.0.2.50"
        mock_event.asn = "AS14061"  # DigitalOcean (hosting/VPN)
        mock_event.artifact_id = "test-token-789"
        
        # Test VPN detection directly
        is_vpn = pipeline.vpn_detector.is_vpn(mock_event.source_ip, mock_event.asn)
        
        # VPN should be detected (hosting provider)
        assert is_vpn is True
