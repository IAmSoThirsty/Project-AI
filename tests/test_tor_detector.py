
import unittest
from unittest.mock import patch, MagicMock
import urllib.request
from src.cerberus.sase.core.normalization import TorDetector

class TestTorDetector(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_load_tor_list_success(self, mock_urlopen):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.read.return_value = (
            "ExitNode 000102030405060708090A0B0C0D0E0F10111213\n"
            "Published 2023-01-01 00:00:00\n"
            "LastStatus 2023-01-01 01:00:00\n"
            "ExitAddress 1.2.3.4 2023-01-01 00:30:00\n"
            "ExitAddress 5.6.7.8 2023-01-01 00:45:00\n"
        ).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        detector = TorDetector()

        self.assertIn("1.2.3.4", detector.tor_exit_nodes)
        self.assertIn("5.6.7.8", detector.tor_exit_nodes)
        self.assertEqual(len(detector.tor_exit_nodes), 2)
        self.assertTrue(detector.is_tor_exit("1.2.3.4"))
        self.assertFalse(detector.is_tor_exit("185.220.101.1"))

    @patch('urllib.request.urlopen')
    def test_load_tor_list_failure(self, mock_urlopen):
        # Mock failed response
        mock_urlopen.side_effect = Exception("Connection error")

        detector = TorDetector()

        # Should fallback to static list
        self.assertIn("185.220.101.1", detector.tor_exit_nodes)
        self.assertIn("185.220.101.2", detector.tor_exit_nodes)
        self.assertEqual(len(detector.tor_exit_nodes), 2)
        self.assertTrue(detector.is_tor_exit("185.220.101.1"))

    @patch('urllib.request.urlopen')
    def test_load_tor_list_empty(self, mock_urlopen):
        # Mock successful but empty response
        mock_response = MagicMock()
        mock_response.read.return_value = "No exit addresses here".encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        detector = TorDetector()

        # Should fallback to static list
        self.assertIn("185.220.101.1", detector.tor_exit_nodes)

if __name__ == "__main__":
    unittest.main()
