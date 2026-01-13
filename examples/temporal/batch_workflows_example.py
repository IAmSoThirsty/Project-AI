#!/usr/bin/env python3
"""
Example: Running Multiple Workflows in Parallel

This example demonstrates how to start multiple workflows simultaneously
and wait for all of them to complete.
"""

import asyncio
import logging
from datetime import datetime

from app.temporal.client import TemporalClientManager
from app.temporal.workflows import (
    AILearningWorkflow,
    LearningRequest,
    MemoryExpansionWorkflow,
    MemoryExpansionRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run multiple workflows in parallel."""
    logger.info("Starting batch workflow example")
    
    # Create and connect client
    manager = TemporalClientManager()
    await manager.connect()
    
    try:
        # Define multiple learning requests
        learning_requests = [
            LearningRequest(
                content="Python asyncio fundamentals",
                source="tutorial",
                category="programming",
            ),
            LearningRequest(
                content="Machine learning model evaluation metrics",
                source="documentation",
                category="data_science",
            ),
            LearningRequest(
                content="Security best practices for web applications",
                source="security_guide",
                category="security",
            ),
        ]
        
        # Start all workflows
        handles = []
        for i, request in enumerate(learning_requests):
            workflow_id = f"batch-learning-{i}-{datetime.now().timestamp()}"
            
            handle = await manager.client.start_workflow(
                AILearningWorkflow.run,
                request,
                id=workflow_id,
                task_queue="project-ai-tasks",
            )
            handles.append(handle)
            logger.info(f"Started workflow {i+1}/{len(learning_requests)}: {workflow_id}")
        
        logger.info(f"All {len(handles)} workflows started, waiting for results...")
        
        # Wait for all workflows to complete
        results = await asyncio.gather(*[h.result() for h in handles])
        
        # Report results
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Batch workflow results:")
        logger.info(f"  Total: {len(results)}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"{'='*60}\n")
        
        for i, result in enumerate(results):
            if result.success:
                logger.info(f"✓ Workflow {i+1}: {result.knowledge_id}")
            else:
                logger.error(f"✗ Workflow {i+1}: {result.error}")
        
    finally:
        await manager.disconnect()
    
    logger.info("Batch example complete")


if __name__ == "__main__":
    asyncio.run(main())
