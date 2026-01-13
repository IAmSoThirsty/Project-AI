#!/usr/bin/env python3
"""
Example: Image Generation Workflow with Temporal.io

This example demonstrates how to use the ImageGenerationWorkflow to generate
images with durable execution and automatic retries.
"""

import asyncio
import logging
from datetime import datetime

from app.temporal.client import TemporalClientManager
from app.temporal.workflows import ImageGenerationRequest, ImageGenerationWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run image generation workflow example."""
    logger.info("Starting Image Generation Workflow example")

    # Create and connect client
    manager = TemporalClientManager()
    await manager.connect()

    try:
        # Create image generation request
        request = ImageGenerationRequest(
            prompt="A serene mountain landscape at sunset with a crystal clear lake",
            style="photorealistic",
            size="1024x1024",
            backend="huggingface",
            user_id="example_user",
        )

        # Generate unique workflow ID
        workflow_id = f"image-gen-{datetime.now().timestamp()}"

        logger.info(f"Starting workflow: {workflow_id}")
        logger.info(f"Prompt: {request.prompt}")

        # Start workflow
        handle = await manager.client.start_workflow(
            ImageGenerationWorkflow.run,
            request,
            id=workflow_id,
            task_queue="project-ai-tasks",
        )

        logger.info("Workflow started, waiting for result...")
        logger.info("This may take several minutes...")

        # Wait for result (automatic retries if generation fails)
        result = await handle.result()

        if result.success:
            logger.info("✓ Image generation successful!")
            logger.info(f"  Image saved to: {result.image_path}")
            logger.info(f"  Metadata: {result.metadata}")
        else:
            logger.error(f"✗ Image generation failed: {result.error}")

    finally:
        await manager.disconnect()

    logger.info("Example complete")


if __name__ == "__main__":
    asyncio.run(main())
