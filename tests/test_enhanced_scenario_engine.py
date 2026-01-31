#!/usr/bin/env python3
"""
Tests for Enhanced Global Scenario Engine Features

Tests for:
- Expanded country coverage configuration
- IMF and WHO data integration
- Real-time monitoring capabilities
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from app.core.scenario_config import (
    COMPREHENSIVE_COUNTRY_LIST,
    ECONOMIC_BLOCS,
    REGIONAL_GROUPS,
    get_country_list,
    get_country_metadata,
)
from app.core.enhanced_data_sources import IMFDataSource, WHODataSource
from app.core.realtime_monitoring import (
    IncrementalUpdateManager,
    MonitoringDashboard,
    RealTimeAlertSystem,
    WebhookNotifier,
)


class TestScenarioConfig:
    """Test scenario configuration module."""
    
    def test_comprehensive_country_list_size(self):
        """Test that comprehensive list has 50+ countries."""
        assert len(COMPREHENSIVE_COUNTRY_LIST) >= 50
        assert len(COMPREHENSIVE_COUNTRY_LIST) == 57  # Current count
    
    def test_regional_groups_defined(self):
        """Test that regional groups are properly defined."""
        assert "north_america" in REGIONAL_GROUPS
        assert "europe" in REGIONAL_GROUPS
        assert "asia" in REGIONAL_GROUPS or "east_asia" in REGIONAL_GROUPS
        
        # Check some countries are in correct regions
        assert "USA" in REGIONAL_GROUPS["north_america"]
        assert "DEU" in REGIONAL_GROUPS["europe"]
    
    def test_economic_blocs_defined(self):
        """Test that economic blocs are defined."""
        assert "g20" in ECONOMIC_BLOCS
        assert "g7" in ECONOMIC_BLOCS
        assert "brics" in ECONOMIC_BLOCS
        
        # Check G20 has correct size
        assert len(ECONOMIC_BLOCS["g20"]) == 21  # 19 countries + 2 (ARG, ZAF)
    
    def test_get_country_list_comprehensive(self):
        """Test getting comprehensive country list."""
        countries = get_country_list("comprehensive")
        assert len(countries) >= 50
        assert "USA" in countries
        assert "CHN" in countries
    
    def test_get_country_list_by_bloc(self):
        """Test getting country list by economic bloc."""
        g7 = get_country_list(bloc="g7")
        assert len(g7) == 7
        assert "USA" in g7
        assert "GBR" in g7
    
    def test_get_country_list_by_region(self):
        """Test getting country list by region."""
        europe = get_country_list(region="europe")
        assert len(europe) > 0
        assert "DEU" in europe
        assert "FRA" in europe
    
    def test_get_country_metadata(self):
        """Test getting country metadata."""
        usa_meta = get_country_metadata("USA")
        
        assert usa_meta["code"] == "USA"
        assert "north_america" in usa_meta["regions"]
        assert "g7" in usa_meta["blocs"]
        assert usa_meta["development"] == "developed"
        assert usa_meta["population_tier"] == "mega"


class TestIMFDataSource:
    """Test IMF data source connector."""
    
    @pytest.fixture
    def imf_source(self):
        """Create IMF data source for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IMFDataSource(tmpdir)
    
    def test_initialization(self, imf_source):
        """Test IMF data source initializes correctly."""
        assert imf_source.cache_dir.exists()
        assert imf_source.session is not None
        assert len(imf_source.INDICATORS) >= 10
    
    def test_indicators_defined(self, imf_source):
        """Test that IMF indicators are defined."""
        assert "govt_debt" in imf_source.INDICATORS
        assert "govt_deficit" in imf_source.INDICATORS
        assert "inflation_avg" in imf_source.INDICATORS
    
    @patch('requests.Session.get')
    def test_fetch_indicator_with_mock(self, mock_get, imf_source):
        """Test fetching IMF indicator with mocked response."""
        # Mock empty response for demo
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = imf_source.fetch_indicator("GGXWDG_NGDP", 2020, 2022, ["USA"])
        
        # Should return empty dict (API limitations in demo mode)
        assert isinstance(result, dict)


class TestWHODataSource:
    """Test WHO data source connector."""
    
    @pytest.fixture
    def who_source(self):
        """Create WHO data source for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield WHODataSource(tmpdir)
    
    def test_initialization(self, who_source):
        """Test WHO data source initializes correctly."""
        assert who_source.cache_dir.exists()
        assert who_source.session is not None
        assert len(who_source.INDICATORS) >= 8
    
    def test_indicators_defined(self, who_source):
        """Test that WHO indicators are defined."""
        assert "life_expectancy" in who_source.INDICATORS
        assert "infant_mortality" in who_source.INDICATORS
        assert "health_expenditure" in who_source.INDICATORS
    
    @patch('requests.Session.get')
    def test_fetch_indicator_with_mock(self, mock_get, who_source):
        """Test fetching WHO indicator with mocked response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = who_source.fetch_indicator("WHOSIS_000001", 2020, 2022, ["USA"])
        
        assert isinstance(result, dict)


class TestIncrementalUpdateManager:
    """Test incremental update manager."""
    
    @pytest.fixture
    def engine_mock(self):
        """Create mock engine."""
        from app.core.simulation_contingency_root import RiskDomain
        
        engine = MagicMock()
        engine.historical_data = {RiskDomain.ECONOMIC: {}}
        return engine
    
    @pytest.fixture
    def update_manager(self, engine_mock):
        """Create update manager."""
        return IncrementalUpdateManager(engine_mock)
    
    def test_initialization(self, update_manager):
        """Test update manager initializes correctly."""
        assert update_manager.engine is not None
        assert len(update_manager.update_log) == 0
    
    def test_update_country_data(self, update_manager):
        """Test updating country data."""
        success = update_manager.update_country_data("USA", "economic", 2024, 2.5)
        
        assert success
        assert len(update_manager.update_log) == 1
        
        # Check update was logged
        log_entry = update_manager.update_log[0]
        assert log_entry["country"] == "USA"
        assert log_entry["domain"] == "economic"
        assert log_entry["year"] == 2024
        assert log_entry["new_value"] == 2.5
    
    def test_get_update_history(self, update_manager):
        """Test getting update history."""
        update_manager.update_country_data("USA", "economic", 2024, 2.5)
        update_manager.update_country_data("CHN", "inflation", 2024, 3.0)
        
        history = update_manager.get_update_history()
        assert len(history) == 2


class TestRealTimeAlertSystem:
    """Test real-time alert system."""
    
    @pytest.fixture
    def engine_mock(self):
        """Create mock engine."""
        engine = MagicMock()
        engine.simulate_scenarios.return_value = []
        engine.generate_alerts.return_value = []
        return engine
    
    @pytest.fixture
    def alert_system(self, engine_mock):
        """Create alert system."""
        return RealTimeAlertSystem(engine_mock, alert_threshold=0.7)
    
    def test_initialization(self, alert_system):
        """Test alert system initializes correctly."""
        assert alert_system.alert_threshold == 0.7
        assert len(alert_system.subscribers) == 0
        assert not alert_system.monitoring
    
    def test_subscribe_unsubscribe(self, alert_system):
        """Test subscribing and unsubscribing."""
        def callback(alert):
            pass
        
        alert_system.subscribe(callback)
        assert len(alert_system.subscribers) == 1
        
        alert_system.unsubscribe(callback)
        assert len(alert_system.subscribers) == 0
    
    def test_emit_alert(self, alert_system):
        """Test emitting alerts."""
        callback_called = []
        
        def callback(alert):
            callback_called.append(alert)
        
        alert_system.subscribe(callback)
        
        mock_alert = MagicMock()
        alert_system.emit_alert(mock_alert)
        
        assert len(callback_called) == 1
        assert len(alert_system.alert_queue) == 1


class TestMonitoringDashboard:
    """Test monitoring dashboard."""
    
    @pytest.fixture
    def engine_mock(self):
        """Create mock engine."""
        from app.core.simulation_contingency_root import RiskDomain
        
        engine = MagicMock()
        engine.historical_data = {
            RiskDomain.ECONOMIC: {
                "USA": {2020: 2.5, 2021: 3.0},
                "CHN": {2020: 6.0, 2021: 8.0}
            }
        }
        engine.threshold_events = []
        engine.scenarios = []
        engine.alerts = []
        return engine
    
    @pytest.fixture
    def dashboard(self, engine_mock):
        """Create monitoring dashboard."""
        return MonitoringDashboard(engine_mock)
    
    def test_initialization(self, dashboard):
        """Test dashboard initializes correctly."""
        assert dashboard.engine is not None
        assert len(dashboard.metrics_history) == 0
    
    def test_get_current_metrics(self, dashboard):
        """Test getting current metrics."""
        metrics = dashboard.get_current_metrics()
        
        assert "timestamp" in metrics
        assert "data_points" in metrics
        assert "countries" in metrics
        assert "domains" in metrics
        assert metrics["data_points"] == 4  # 2 countries × 2 years
        assert metrics["countries"] == 2
        assert metrics["domains"] == 1
    
    def test_metrics_history(self, dashboard):
        """Test metrics history tracking."""
        dashboard.get_current_metrics()
        dashboard.get_current_metrics()
        
        assert len(dashboard.metrics_history) == 2
        
        history = dashboard.get_metrics_history(minutes=60)
        assert len(history) >= 1


class TestWebhookNotifier:
    """Test webhook notifier."""
    
    @pytest.fixture
    def webhook_notifier(self):
        """Create webhook notifier."""
        return WebhookNotifier(["https://example.com/webhook"])
    
    def test_initialization(self, webhook_notifier):
        """Test webhook notifier initializes correctly."""
        assert len(webhook_notifier.webhook_urls) == 1
        assert webhook_notifier.webhook_urls[0] == "https://example.com/webhook"
    
    def test_add_remove_webhook(self, webhook_notifier):
        """Test adding and removing webhooks."""
        webhook_notifier.add_webhook("https://example.com/webhook2")
        assert len(webhook_notifier.webhook_urls) == 2
        
        webhook_notifier.remove_webhook("https://example.com/webhook2")
        assert len(webhook_notifier.webhook_urls) == 1
    
    @patch('requests.Session.post')
    def test_notify_with_mock(self, mock_post, webhook_notifier):
        """Test notifying webhooks with mocked response."""
        from app.core.simulation_contingency_root import AlertLevel, ScenarioProjection
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create mock alert
        mock_scenario = MagicMock(spec=ScenarioProjection)
        mock_scenario.title = "Test Crisis"
        mock_scenario.likelihood = 0.8
        mock_scenario.severity = AlertLevel.HIGH
        mock_scenario.year = 2027
        
        mock_alert = MagicMock()
        mock_alert.alert_id = "test_alert_1"
        mock_alert.risk_score = 80.0
        mock_alert.scenario = mock_scenario
        mock_alert.explainability = "Test explanation " * 100
        
        webhook_notifier.notify(mock_alert)
        
        assert mock_post.called
        assert len(webhook_notifier.notification_log) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
