"""
Tests for Temporal.io client manager.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.temporal.client import TemporalClientManager


@pytest.mark.asyncio
class TestTemporalClientManager:
    """Test suite for TemporalClientManager."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        manager = TemporalClientManager()

        assert manager.target_host == "localhost:7233"
        assert manager.namespace == "default"
        assert manager.task_queue == "project-ai-tasks"
        assert manager.tls_config is None
        assert manager._client is None

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        manager = TemporalClientManager(
            target_host="custom-host:7233",
            namespace="custom-namespace",
            task_queue="custom-queue",
        )

        assert manager.target_host == "custom-host:7233"
        assert manager.namespace == "custom-namespace"
        assert manager.task_queue == "custom-queue"

    @patch("app.temporal.client.Client")
    async def test_connect_success(self, mock_client_class):
        """Test successful connection to Temporal server."""
        mock_client = AsyncMock()
        mock_client_class.connect = AsyncMock(return_value=mock_client)

        manager = TemporalClientManager()
        client = await manager.connect()

        assert client == mock_client
        assert manager._client == mock_client
        mock_client_class.connect.assert_called_once()

    @patch("app.temporal.client.Client")
    async def test_connect_failure(self, mock_client_class):
        """Test connection failure handling."""
        mock_client_class.connect = AsyncMock(side_effect=Exception("Connection failed"))

        manager = TemporalClientManager()

        with pytest.raises(ConnectionError):
            await manager.connect()

    async def test_disconnect(self):
        """Test disconnection cleanup."""
        manager = TemporalClientManager()
        manager._client = MagicMock()
        manager._workers = [MagicMock(), MagicMock()]

        await manager.disconnect()

        assert manager._client is None
        assert len(manager._workers) == 0

    def test_client_property(self):
        """Test client property getter."""
        manager = TemporalClientManager()
        assert manager.client is None

        mock_client = MagicMock()
        manager._client = mock_client
        assert manager.client == mock_client

    @patch("app.temporal.client.Worker")
    def test_create_worker(self, mock_worker_class):
        """Test worker creation."""
        mock_client = MagicMock()
        mock_worker = MagicMock()
        mock_worker_class.return_value = mock_worker

        manager = TemporalClientManager()
        manager._client = mock_client

        workflows = [MagicMock(), MagicMock()]
        activities = [MagicMock(), MagicMock(), MagicMock()]

        worker = manager.create_worker(
            workflows=workflows,
            activities=activities,
        )

        assert worker == mock_worker
        assert len(manager._workers) == 1
        mock_worker_class.assert_called_once()

    def test_create_worker_without_client(self):
        """Test worker creation fails without connected client."""
        manager = TemporalClientManager()

        with pytest.raises(RuntimeError, match="Client not connected"):
            manager.create_worker(workflows=[], activities=[])

    @patch("app.temporal.client.Client")
    async def test_health_check_success(self, mock_client_class):
        """Test successful health check."""
        mock_client = AsyncMock()
        mock_client.describe_namespace = AsyncMock()

        manager = TemporalClientManager()
        manager._client = mock_client

        result = await manager.health_check()

        assert result is True
        mock_client.describe_namespace.assert_called_once()

    async def test_health_check_no_client(self):
        """Test health check with no client."""
        manager = TemporalClientManager()

        result = await manager.health_check()

        assert result is False

    @patch("app.temporal.client.Client")
    async def test_health_check_failure(self, mock_client_class):
        """Test health check with connection failure."""
        mock_client = AsyncMock()
        mock_client.describe_namespace = AsyncMock(side_effect=Exception("Connection lost"))

        manager = TemporalClientManager()
        manager._client = mock_client

        result = await manager.health_check()

        assert result is False

    @patch("app.temporal.client.Client")
    async def test_context_manager(self, mock_client_class):
        """Test async context manager protocol."""
        mock_client = AsyncMock()
        mock_client_class.connect = AsyncMock(return_value=mock_client)

        async with TemporalClientManager() as manager:
            assert manager._client == mock_client

        # After exiting context, client should be cleaned up
        assert manager._client is None
