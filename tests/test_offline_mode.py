"""
Tests for offline mode functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.core.network_utils import NetworkStatus, is_online
from app.core.learning_paths import LearningPathManager, OFFLINE_TEMPLATES
from app.core.security_resources import SecurityResourceManager, OFFLINE_REPO_CACHE
from app.core.location_tracker import LocationTracker


class TestNetworkUtils:
    """Tests for network utility functions."""

    def test_network_status_initialization(self):
        """Test NetworkStatus initializes correctly."""
        ns = NetworkStatus()
        assert ns._is_online is None
        assert ns._callbacks == []

    def test_check_connectivity_returns_bool(self):
        """Test check_connectivity returns boolean."""
        ns = NetworkStatus()
        result = ns.check_connectivity(timeout=1.0)
        assert isinstance(result, bool)

    def test_is_online_property_performs_check_if_none(self):
        """Test is_online property performs check when not yet checked."""
        ns = NetworkStatus()
        assert ns._is_online is None
        _ = ns.is_online
        # After access, _is_online should be set
        assert ns._is_online is not None

    def test_add_and_remove_callback(self):
        """Test adding and removing status callbacks."""
        ns = NetworkStatus()

        def callback(status):
            pass

        ns.add_status_callback(callback)
        assert callback in ns._callbacks

        ns.remove_status_callback(callback)
        assert callback not in ns._callbacks


class TestLearningPathsOffline:
    """Tests for offline learning path generation."""

    def test_offline_templates_exist(self):
        """Test that offline templates are defined."""
        assert len(OFFLINE_TEMPLATES) > 0
        assert 'programming' in OFFLINE_TEMPLATES
        assert 'python' in OFFLINE_TEMPLATES

    def test_get_offline_template_exact_match(self):
        """Test getting offline template with exact match."""
        lm = LearningPathManager()
        template = lm._get_offline_template('python', 'beginner')
        assert 'Learning Path: Python' in template
        assert 'Beginner' in template

    def test_get_offline_template_partial_match(self):
        """Test getting offline template with partial match."""
        lm = LearningPathManager()
        # 'python programming' should match 'python' or 'programming'
        template = lm._get_offline_template('python programming', 'beginner')
        assert 'Learning Path' in template

    def test_get_offline_template_fallback_to_generic(self):
        """Test generic template for unknown topics."""
        lm = LearningPathManager()
        template = lm._get_offline_template('underwater basket weaving', 'beginner')
        assert 'Learning Path' in template
        assert 'underwater basket weaving' in template.lower()
        assert 'offline template' in template.lower()

    @patch('app.core.learning_paths.is_online')
    def test_generate_path_uses_offline_when_no_connection(self, mock_is_online):
        """Test generate_path falls back to offline when not connected."""
        mock_is_online.return_value = False
        lm = LearningPathManager(api_key=None)
        result = lm.generate_path('python', 'beginner')
        assert 'Learning Path' in result
        # Should use offline template
        assert 'offline' in result.lower() or 'Python' in result

    @patch('app.core.learning_paths.is_online')
    def test_generate_path_uses_offline_when_no_api_key(self, mock_is_online):
        """Test generate_path uses offline when no API key."""
        mock_is_online.return_value = True
        lm = LearningPathManager(api_key=None)
        result = lm.generate_path('programming', 'beginner')
        assert 'Learning Path' in result


class TestSecurityResourcesOffline:
    """Tests for offline security resources."""

    def test_offline_cache_exists(self):
        """Test that offline cache is populated."""
        assert len(OFFLINE_REPO_CACHE) > 0
        assert 'swisskyrepo/PayloadsAllTheThings' in OFFLINE_REPO_CACHE

    def test_get_cached_details_returns_builtin_cache(self):
        """Test getting cached details from built-in cache."""
        sr = SecurityResourceManager()
        details = sr._get_cached_details('swisskyrepo/PayloadsAllTheThings')
        assert details is not None
        assert details['name'] == 'PayloadsAllTheThings'
        assert details['offline_cached'] is True

    @patch('app.core.security_resources.is_online')
    def test_get_repo_details_offline_mode(self, mock_is_online):
        """Test get_repo_details uses cache when offline."""
        mock_is_online.return_value = False
        sr = SecurityResourceManager()
        details = sr.get_repo_details('swisskyrepo/PayloadsAllTheThings')
        assert details is not None
        assert details['offline_cached'] is True

    @patch('app.core.security_resources.is_online')
    def test_get_repo_details_unknown_repo_offline(self, mock_is_online):
        """Test get_repo_details returns placeholder for unknown repos offline."""
        mock_is_online.return_value = False
        sr = SecurityResourceManager()
        details = sr.get_repo_details('unknown/unknown-repo')
        assert details is not None
        assert details['description'] == 'Details unavailable offline'
        assert details['offline_cached'] is True


class TestLocationTrackerOffline:
    """Tests for offline location tracking."""

    def test_offline_placeholder(self):
        """Test offline placeholder location."""
        lt = LocationTracker()
        placeholder = lt._get_offline_placeholder()
        assert placeholder['offline'] is True
        assert placeholder['source'] == 'offline'
        assert 'Unknown' in placeholder['city']

    @patch('app.core.location_tracker.is_online')
    def test_get_location_from_ip_offline(self, mock_is_online):
        """Test get_location_from_ip returns placeholder when offline."""
        mock_is_online.return_value = False
        lt = LocationTracker()
        location = lt.get_location_from_ip()
        assert location is not None
        assert location['offline'] is True

    @patch('app.core.location_tracker.is_online')
    def test_get_location_from_ip_uses_cached(self, mock_is_online):
        """Test get_location_from_ip uses cached location when offline."""
        mock_is_online.return_value = False
        lt = LocationTracker()
        # Set a cached location
        lt._last_known_location = {
            'city': 'Cached City',
            'region': 'Cached Region',
            'country': 'Cached Country',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'source': 'ip'
        }
        location = lt.get_location_from_ip()
        assert location is not None
        assert location['city'] == 'Cached City'
        assert location['offline'] is True
        assert location['source'] == 'cached'

    @patch('app.core.location_tracker.is_online')
    def test_get_location_from_coords_offline(self, mock_is_online):
        """Test get_location_from_coords returns basic info when offline."""
        mock_is_online.return_value = False
        lt = LocationTracker()
        location = lt.get_location_from_coords(40.7128, -74.0060)
        assert location is not None
        assert location['latitude'] == 40.7128
        assert location['longitude'] == -74.0060
        assert location['offline'] is True
        assert 'offline' in location['address'].lower()

    def test_offline_mode_property(self):
        """Test offline_mode property."""
        lt = LocationTracker()
        assert lt.offline_mode is False
        lt._offline_mode = True
        assert lt.offline_mode is True

    def test_get_last_known_location(self, tmp_path):
        """Test get_last_known_location."""
        lt = LocationTracker()

        # No location yet
        assert lt.get_last_known_location() is None

        # Set a location
        lt._last_known_location = {'city': 'Test City'}
        assert lt.get_last_known_location()['city'] == 'Test City'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
