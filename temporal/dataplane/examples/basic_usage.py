"""
Example: Using the Data Plane Client

Demonstrates sending messages, uploading artifacts, and using cache.
"""

import asyncio
import logging
from temporal.dataplane import DataPlaneClient, DataPlaneConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Example data plane usage."""
    
    # Create client with configuration from environment
    config = DataPlaneConfig.from_env()
    client = DataPlaneClient(config)
    
    try:
        # Connect to data plane
        logger.info("Connecting to data plane...")
        await client.connect()
        
        # Example 1: Send small message
        logger.info("Example 1: Sending small message...")
        await client.send_message(
            topic="agents.communication",
            data=b"Hello, Agent World!",
            agent_id="agent-001",
        )
        
        # Example 2: Upload artifact
        logger.info("Example 2: Uploading artifact...")
        object_key = await client.upload_artifact(
            artifact_name="build.tar.gz",
            data=b"Build output...",
            artifact_type="build",
        )
        logger.info(f"Artifact uploaded: {object_key}")
        
        # Example 3: Cache operations
        logger.info("Example 3: Cache operations...")
        await client.cache_set("session:123", b"data", ttl=300)
        cached = await client.cache_get("session:123")
        logger.info(f"Cached: {cached}")
        
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
