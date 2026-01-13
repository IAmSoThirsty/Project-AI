"""
Tests for Temporal.io configuration.
"""


from app.temporal.config import TemporalConfig, get_temporal_config


class TestTemporalConfig:
    """Test suite for TemporalConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = TemporalConfig()

        assert config.host == "localhost:7233"
        assert config.namespace == "default"
        assert config.task_queue == "project-ai-tasks"
        assert config.max_concurrent_activities == 50
        assert config.max_concurrent_workflows == 50

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = TemporalConfig(
            host="custom-host:7233",
            namespace="custom-namespace",
            task_queue="custom-queue",
        )

        assert config.host == "custom-host:7233"
        assert config.namespace == "custom-namespace"
        assert config.task_queue == "custom-queue"

    def test_is_cloud_false(self):
        """Test is_cloud property when not using cloud."""
        config = TemporalConfig()
        assert config.is_cloud is False

    def test_is_cloud_true(self):
        """Test is_cloud property when using cloud."""
        config = TemporalConfig(cloud_namespace="my-namespace.a2b3c")
        assert config.is_cloud is True

    def test_get_connection_string_local(self):
        """Test connection string for local server."""
        config = TemporalConfig(host="localhost:7233")
        conn_str = config.get_connection_string()

        assert "Temporal Server" in conn_str
        assert "localhost:7233" in conn_str

    def test_get_temporal_config_singleton(self):
        """Test that get_temporal_config returns singleton."""
        config1 = get_temporal_config()
        config2 = get_temporal_config()

        assert config1 is config2
