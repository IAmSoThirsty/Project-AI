import urllib.error
from unittest.mock import MagicMock, patch

from src.cerberus.sase.core.normalization import TorDetector


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
