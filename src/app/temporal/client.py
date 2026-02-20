"""
Temporal.io Client Configuration for Project-AI.

Manages connection to Temporal server, client lifecycle, and worker setup.
"""

import asyncio
import logging
import os

from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

logger = logging.getLogger(__name__)


class TemporalClientManager:
    """
    Manages Temporal.io client connections and worker lifecycle.

    This class handles:
    - Connection to Temporal server (local or cloud)
    - TLS/mTLS configuration for secure connections
    - Worker registration and lifecycle
    - Client health checks and reconnection
    """

    def __init__(
        self,
        target_host: str | None = None,
        namespace: str = "default",
        task_queue: str = "project-ai-tasks",
        tls_config: TLSConfig | None = None,
    ):
        """
        Initialize Temporal client manager.

        Args:
            target_host: Temporal server address (e.g., 'localhost:7233')
            namespace: Temporal namespace (default: 'default')
            task_queue: Task queue name for workers
            tls_config: Optional TLS configuration for secure connections
        """
        self.target_host = target_host or os.getenv("TEMPORAL_HOST", "localhost:7233")
        self.namespace = namespace or os.getenv("TEMPORAL_NAMESPACE", "default")
        self.task_queue = task_queue or os.getenv("TEMPORAL_TASK_QUEUE", "project-ai-tasks")
        self.tls_config = tls_config
        self._client: Client | None = None
        self._workers: list[Worker] = []

    async def connect(self) -> Client:
        """
        Establish connection to Temporal server.

        Returns:
            Connected Temporal client instance

        Raises:
            ConnectionError: If unable to connect to Temporal server
        """
        try:
            logger.info(f"Connecting to Temporal server at {self.target_host}, " f"namespace: {self.namespace}")

            self._client = await Client.connect(
                self.target_host,
                namespace=self.namespace,
                tls=self.tls_config,
            )

            logger.info("Successfully connected to Temporal server")
            return self._client

        except Exception as e:
            logger.error("Failed to connect to Temporal server: %s", e)
            raise ConnectionError(f"Unable to connect to Temporal at {self.target_host}") from e

    async def disconnect(self):
        """Close connection and cleanup resources."""
        if self._client:
            logger.info("Disconnecting from Temporal server")
            # Temporal client doesn't require explicit close in newer versions
            self._client = None
            self._workers.clear()

    @property
    def client(self) -> Client | None:
        """Get the connected client instance."""
        return self._client

    def create_worker(
        self,
        workflows: list,
        activities: list,
        max_concurrent_activities: int = 100,
        max_concurrent_workflow_tasks: int = 100,
    ) -> Worker:
        """
        Create a Temporal worker for processing workflows and activities.

        Args:
            workflows: List of workflow classes to register
            activities: List of activity functions to register
            max_concurrent_activities: Max parallel activity executions
            max_concurrent_workflow_tasks: Max parallel workflow tasks

        Returns:
            Configured Worker instance
        """
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")

        worker = Worker(
            self._client,
            task_queue=self.task_queue,
            workflows=workflows,
            activities=activities,
            max_concurrent_activities=max_concurrent_activities,
            max_concurrent_workflow_tasks=max_concurrent_workflow_tasks,
        )

        self._workers.append(worker)
        logger.info(
            f"Created worker for task queue '{self.task_queue}' with "
            f"{len(workflows)} workflows and {len(activities)} activities"
        )
        return worker

    async def run_worker(self, worker: Worker):
        """
        Start a worker and run it until interrupted.

        Args:
            worker: The worker to run
        """
        logger.info("Starting worker on task queue '%s'", self.task_queue)
        try:
            await worker.run()
        except asyncio.CancelledError:
            logger.info("Worker cancelled")
        except Exception as e:
            logger.error("Worker error: %s", e)
            raise

    async def health_check(self) -> bool:
        """
        Perform health check on Temporal connection.

        Returns:
            True if connection is healthy, False otherwise
        """
        if not self._client:
            return False

        try:
            # Try to describe namespace as a health check
            await self._client.describe_namespace()
            return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False

    @classmethod
    async def create_cloud_client(
        cls,
        namespace: str,
        client_cert_path: str,
        client_key_path: str,
        api_key: str | None = None,
    ) -> "TemporalClientManager":
        """
        Create a client configured for Temporal Cloud.

        Args:
            namespace: Cloud namespace (e.g., 'my-namespace.a2b3c')
            client_cert_path: Path to client certificate file
            client_key_path: Path to client private key file
            api_key: Optional API key for authentication

        Returns:
            Configured TemporalClientManager instance
        """
        # Read certificate and key
        with open(client_cert_path, "rb") as f:
            client_cert = f.read()
        with open(client_key_path, "rb") as f:
            client_key = f.read()

        # Create TLS config
        tls_config = TLSConfig(
            client_cert=client_cert,
            client_private_key=client_key,
        )

        # Extract account from namespace (format: namespace.account_id)
        account_id = namespace.split(".")[-1]
        target_host = f"{account_id}.tmprl.cloud:7233"

        manager = cls(
            target_host=target_host,
            namespace=namespace,
            tls_config=tls_config,
        )

        await manager.connect()
        return manager

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
