# Temporal Workflows

## Workflow Definitions

Temporal workflows are durable, fault-tolerant functions that coordinate activities and handle business logic with automatic retries and state persistence.

## Core Workflow Implementations

### Image Generation Workflow

```python
# src/app/temporal/workflows/image_generation_workflow.py
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from datetime import timedelta
from typing import Dict, Any
import asyncio

from ..activities.image_activities import (
    validate_prompt,
    check_content_filter,
    generate_with_huggingface,
    generate_with_openai,
    save_image_to_storage,
    update_generation_history,
    send_completion_notification
)
from ..monitoring import track_workflow_metrics
from .registry import registered_workflow

@dataclass
class ImageGenerationInput:
    """Input for image generation workflow"""
    user_id: str
    prompt: str
    style: str = "photorealistic"
    size: str = "1024x1024"
    backend: str = "huggingface"
    negative_prompt: str = ""

@dataclass
class ImageGenerationOutput:
    """Output from image generation workflow"""
    image_url: str
    image_path: str
    metadata: Dict[str, Any]
    generation_time: float
    status: str

@registered_workflow
class ImageGenerationWorkflow:
    """Workflow for generating images with AI models"""
    
    @workflow.run
    @track_workflow_metrics
    async def run(self, input: ImageGenerationInput) -> ImageGenerationOutput:
        """Execute image generation workflow"""
        workflow.logger.info(
            f"Starting image generation workflow for user {input.user_id}"
        )
        
        # Step 1: Validate prompt
        validation_result = await workflow.execute_activity(
            validate_prompt,
            input.prompt,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0
            )
        )
        
        if not validation_result["valid"]:
            raise ApplicationError(
                f"Invalid prompt: {validation_result['reason']}",
                non_retryable=True
            )
        
        # Step 2: Content filtering
        filter_result = await workflow.execute_activity(
            check_content_filter,
            input.prompt,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        
        if not filter_result["safe"]:
            raise ApplicationError(
                f"Content filter: {filter_result['reason']}",
                non_retryable=True
            )
        
        # Step 3: Generate image (with backend-specific logic)
        image_data = None
        generation_error = None
        
        try:
            if input.backend == "huggingface":
                image_data = await workflow.execute_activity(
                    generate_with_huggingface,
                    {
                        "prompt": input.prompt,
                        "negative_prompt": input.negative_prompt,
                        "style": input.style,
                        "size": input.size
                    },
                    start_to_close_timeout=timedelta(seconds=120),
                    retry_policy=RetryPolicy(
                        maximum_attempts=3,
                        initial_interval=timedelta(seconds=5),
                        maximum_interval=timedelta(seconds=30),
                        backoff_coefficient=2.0,
                        non_retryable_error_types=["ContentPolicyViolation"]
                    )
                )
            elif input.backend == "openai":
                image_data = await workflow.execute_activity(
                    generate_with_openai,
                    {
                        "prompt": input.prompt,
                        "size": input.size,
                        "quality": "hd" if input.style == "photorealistic" else "standard"
                    },
                    start_to_close_timeout=timedelta(seconds=60),
                    retry_policy=RetryPolicy(
                        maximum_attempts=3,
                        initial_interval=timedelta(seconds=5),
                        maximum_interval=timedelta(seconds=20),
                        backoff_coefficient=2.0
                    )
                )
            else:
                raise ApplicationError(f"Unknown backend: {input.backend}", non_retryable=True)
        
        except ApplicationError as e:
            generation_error = str(e)
            workflow.logger.error(f"Image generation failed: {generation_error}")
            # Continue with error handling activities
        
        # Step 4: Save to storage (only if generation succeeded)
        storage_result = None
        if image_data and not generation_error:
            storage_result = await workflow.execute_activity(
                save_image_to_storage,
                {
                    "image_data": image_data["image_base64"],
                    "user_id": input.user_id,
                    "metadata": {
                        "prompt": input.prompt,
                        "style": input.style,
                        "backend": input.backend
                    }
                },
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=5,
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=30),
                    backoff_coefficient=2.0
                )
            )
        
        # Step 5: Update generation history (best effort, don't fail workflow)
        try:
            await workflow.execute_activity(
                update_generation_history,
                {
                    "user_id": input.user_id,
                    "prompt": input.prompt,
                    "image_url": storage_result["url"] if storage_result else None,
                    "status": "success" if storage_result else "failed",
                    "error": generation_error
                },
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1)
                ),
                heartbeat_timeout=timedelta(seconds=5)
            )
        except Exception as e:
            workflow.logger.warning(f"Failed to update history: {e}")
        
        # Step 6: Send completion notification (async, don't wait)
        workflow.start_activity(
            send_completion_notification,
            {
                "user_id": input.user_id,
                "status": "success" if storage_result else "failed",
                "image_url": storage_result["url"] if storage_result else None
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Return result
        if storage_result:
            return ImageGenerationOutput(
                image_url=storage_result["url"],
                image_path=storage_result["path"],
                metadata=image_data["metadata"],
                generation_time=image_data["generation_time"],
                status="success"
            )
        else:
            raise ApplicationError(f"Image generation failed: {generation_error}")
```

### Learning Path Workflow

```python
# src/app/temporal/workflows/learning_path_workflow.py
from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from typing import List, Dict
from dataclasses import dataclass

from ..activities.learning_activities import (
    analyze_user_skill_level,
    generate_learning_modules,
    fetch_learning_resources,
    create_personalized_schedule,
    save_learning_path,
    notify_user
)
from ..monitoring import track_workflow_metrics
from .registry import registered_workflow

@dataclass
class LearningPathInput:
    """Input for learning path generation workflow"""
    user_id: str
    category: str
    skill_level: str
    time_commitment_hours: int
    learning_style: str = "balanced"

@dataclass
class LearningPathOutput:
    """Output from learning path generation"""
    path_id: str
    modules: List[Dict]
    estimated_duration_days: int
    resources_count: int

@registered_workflow
class LearningPathWorkflow:
    """Workflow for generating personalized learning paths"""
    
    @workflow.run
    @track_workflow_metrics
    async def run(self, input: LearningPathInput) -> LearningPathOutput:
        """Execute learning path generation workflow"""
        
        # Step 1: Analyze user's current skill level
        skill_analysis = await workflow.execute_activity(
            analyze_user_skill_level,
            {
                "user_id": input.user_id,
                "category": input.category
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Step 2: Generate learning modules with OpenAI
        modules = await workflow.execute_activity(
            generate_learning_modules,
            {
                "category": input.category,
                "skill_level": skill_analysis["level"],
                "time_commitment_hours": input.time_commitment_hours,
                "learning_style": input.learning_style
            },
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=5),
                maximum_interval=timedelta(seconds=30),
                backoff_coefficient=2.0
            )
        )
        
        # Step 3: Fetch resources for each module (parallel execution)
        resource_tasks = []
        for module in modules["modules"]:
            task = workflow.execute_activity(
                fetch_learning_resources,
                {
                    "topic": module["topic"],
                    "difficulty": module["difficulty"]
                },
                start_to_close_timeout=timedelta(seconds=45),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )
            resource_tasks.append(task)
        
        # Wait for all resource fetching to complete
        resources_list = await asyncio.gather(*resource_tasks)
        
        # Combine modules with their resources
        for i, module in enumerate(modules["modules"]):
            module["resources"] = resources_list[i]["resources"]
        
        # Step 4: Create personalized schedule
        schedule = await workflow.execute_activity(
            create_personalized_schedule,
            {
                "modules": modules["modules"],
                "time_commitment_hours": input.time_commitment_hours
            },
            start_to_close_timeout=timedelta(seconds=20),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        
        # Step 5: Save learning path to database
        save_result = await workflow.execute_activity(
            save_learning_path,
            {
                "user_id": input.user_id,
                "category": input.category,
                "modules": modules["modules"],
                "schedule": schedule,
                "skill_level": skill_analysis["level"]
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=5,
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                backoff_coefficient=2.0
            )
        )
        
        # Step 6: Notify user (async, don't block)
        workflow.start_activity(
            notify_user,
            {
                "user_id": input.user_id,
                "path_id": save_result["path_id"],
                "message": "Your personalized learning path is ready!"
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        return LearningPathOutput(
            path_id=save_result["path_id"],
            modules=modules["modules"],
            estimated_duration_days=schedule["duration_days"],
            resources_count=sum(len(m["resources"]) for m in modules["modules"])
        )
```

### Data Analysis Workflow

```python
# src/app/temporal/workflows/data_analysis_workflow.py
from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from dataclasses import dataclass
from typing import Dict, Any

from ..activities.data_activities import (
    load_dataset,
    validate_data,
    perform_exploratory_analysis,
    apply_clustering,
    generate_visualizations,
    save_analysis_results
)
from ..monitoring import track_workflow_metrics
from .registry import registered_workflow

@dataclass
class DataAnalysisInput:
    """Input for data analysis workflow"""
    user_id: str
    file_path: str
    file_type: str
    analysis_type: str = "exploratory"

@registered_workflow
class DataAnalysisWorkflow:
    """Workflow for analyzing user-uploaded data"""
    
    @workflow.run
    @track_workflow_metrics
    async def run(self, input: DataAnalysisInput) -> Dict[str, Any]:
        """Execute data analysis workflow"""
        
        # Step 1: Load dataset
        dataset = await workflow.execute_activity(
            load_dataset,
            {
                "file_path": input.file_path,
                "file_type": input.file_type
            },
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Step 2: Validate data quality
        validation = await workflow.execute_activity(
            validate_data,
            dataset,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        
        if not validation["valid"]:
            raise ApplicationError(
                f"Data validation failed: {validation['errors']}",
                non_retryable=True
            )
        
        # Step 3: Exploratory analysis
        eda_results = await workflow.execute_activity(
            perform_exploratory_analysis,
            dataset,
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=5)
            )
        )
        
        # Step 4: Apply clustering (if requested)
        clustering_results = None
        if input.analysis_type == "clustering":
            clustering_results = await workflow.execute_activity(
                apply_clustering,
                {
                    "dataset": dataset,
                    "n_clusters": eda_results.get("suggested_clusters", 3)
                },
                start_to_close_timeout=timedelta(seconds=180),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )
        
        # Step 5: Generate visualizations
        visualizations = await workflow.execute_activity(
            generate_visualizations,
            {
                "eda_results": eda_results,
                "clustering_results": clustering_results
            },
            start_to_close_timeout=timedelta(seconds=90),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Step 6: Save results
        save_result = await workflow.execute_activity(
            save_analysis_results,
            {
                "user_id": input.user_id,
                "eda_results": eda_results,
                "clustering_results": clustering_results,
                "visualizations": visualizations
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=5)
        )
        
        return {
            "analysis_id": save_result["analysis_id"],
            "summary": eda_results["summary"],
            "visualization_urls": visualizations["urls"],
            "status": "completed"
        }
```

## Workflow Signals and Queries

### Signals (Modify Running Workflows)

```python
# src/app/temporal/workflows/cancellable_workflow.py
from temporalio import workflow
from temporalio.exceptions import CancelledError
import asyncio

@registered_workflow
class CancellableImageGenerationWorkflow:
    """Image generation workflow with cancellation support"""
    
    def __init__(self):
        self._cancelled = False
        self._pause_requested = False
    
    @workflow.signal
    async def cancel(self):
        """Signal to cancel the workflow"""
        workflow.logger.info("Cancel signal received")
        self._cancelled = True
    
    @workflow.signal
    async def pause(self):
        """Signal to pause the workflow"""
        workflow.logger.info("Pause signal received")
        self._pause_requested = True
    
    @workflow.signal
    async def resume(self):
        """Signal to resume the workflow"""
        workflow.logger.info("Resume signal received")
        self._pause_requested = False
    
    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        """Query current workflow status"""
        return {
            "cancelled": self._cancelled,
            "paused": self._pause_requested
        }
    
    @workflow.run
    async def run(self, input: ImageGenerationInput) -> ImageGenerationOutput:
        """Execute with cancellation support"""
        
        # Check for cancellation before each step
        if self._cancelled:
            raise CancelledError("Workflow was cancelled")
        
        # Validation step
        validation_result = await workflow.execute_activity(...)
        
        # Wait if paused
        while self._pause_requested and not self._cancelled:
            await asyncio.sleep(1)
        
        if self._cancelled:
            raise CancelledError("Workflow was cancelled")
        
        # Continue with generation...
        image_data = await workflow.execute_activity(...)
        
        return ImageGenerationOutput(...)
```

### Queries (Read Workflow State)

```python
# Query workflow status from client
from temporalio.client import Client

async def check_workflow_status(workflow_id: str):
    """Query the status of a running workflow"""
    client = await Client.connect("localhost:7233")
    
    handle = client.get_workflow_handle(workflow_id)
    status = await handle.query("get_status")
    
    print(f"Workflow status: {status}")
    return status
```

## Child Workflows

```python
# Parent workflow that spawns child workflows
@registered_workflow
class BatchImageGenerationWorkflow:
    """Generate multiple images in parallel"""
    
    @workflow.run
    async def run(self, prompts: List[str], user_id: str) -> List[str]:
        """Generate images for multiple prompts"""
        
        # Start child workflows for each prompt
        child_handles = []
        for i, prompt in enumerate(prompts):
            handle = await workflow.start_child_workflow(
                ImageGenerationWorkflow.run,
                ImageGenerationInput(
                    user_id=user_id,
                    prompt=prompt,
                    backend="huggingface"
                ),
                id=f"batch-image-{workflow.info().workflow_id}-{i}",
                task_queue="project-ai-high-priority",
                execution_timeout=timedelta(minutes=5)
            )
            child_handles.append(handle)
        
        # Wait for all child workflows to complete
        results = await asyncio.gather(
            *[handle.result() for handle in child_handles],
            return_exceptions=True
        )
        
        # Extract image URLs, handle failures
        image_urls = []
        for result in results:
            if isinstance(result, Exception):
                workflow.logger.error(f"Child workflow failed: {result}")
                image_urls.append(None)
            else:
                image_urls.append(result.image_url)
        
        return image_urls
```

## Scheduled Workflows (Cron)

```python
# src/app/temporal/workflows/maintenance_workflow.py
@registered_workflow
class MaintenanceWorkflow:
    """Scheduled maintenance tasks"""
    
    @workflow.run
    async def run(self) -> Dict[str, Any]:
        """Execute daily maintenance"""
        
        # Clean up old temporary files
        cleanup_result = await workflow.execute_activity(
            cleanup_temp_files,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Archive old generation history
        archive_result = await workflow.execute_activity(
            archive_old_history,
            {"days_old": 90},
            start_to_close_timeout=timedelta(minutes=60),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Update analytics
        analytics_result = await workflow.execute_activity(
            update_daily_analytics,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        return {
            "files_cleaned": cleanup_result["count"],
            "records_archived": archive_result["count"],
            "analytics_updated": analytics_result["success"]
        }

# Schedule the workflow
async def schedule_maintenance():
    """Schedule daily maintenance workflow"""
    client = await Client.connect("localhost:7233")
    
    await client.create_schedule(
        "daily-maintenance",
        schedule=ScheduleSpec(
            cron_expressions=["0 2 * * *"]  # 2 AM daily
        ),
        action=ScheduleActionStartWorkflow(
            MaintenanceWorkflow.run,
            id="maintenance",
            task_queue="project-ai-scheduled"
        )
    )
```

## Error Handling Patterns

```python
# Workflow with saga pattern for compensation
@registered_workflow
class TransactionalWorkflow:
    """Workflow with compensation logic"""
    
    def __init__(self):
        self.completed_steps = []
    
    @workflow.run
    async def run(self, input: Dict) -> Dict:
        """Execute with compensation"""
        
        try:
            # Step 1: Reserve resources
            reserve_result = await workflow.execute_activity(
                reserve_resources,
                input,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            self.completed_steps.append("reserve")
            
            # Step 2: Process request
            process_result = await workflow.execute_activity(
                process_request,
                reserve_result,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            self.completed_steps.append("process")
            
            # Step 3: Commit transaction
            commit_result = await workflow.execute_activity(
                commit_transaction,
                process_result,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=5)
            )
            self.completed_steps.append("commit")
            
            return commit_result
        
        except Exception as e:
            # Compensate completed steps in reverse order
            workflow.logger.error(f"Workflow failed: {e}, compensating...")
            await self._compensate()
            raise
    
    async def _compensate(self):
        """Compensate completed steps"""
        for step in reversed(self.completed_steps):
            try:
                if step == "reserve":
                    await workflow.execute_activity(
                        release_resources,
                        start_to_close_timeout=timedelta(seconds=30),
                        retry_policy=RetryPolicy(maximum_attempts=5)
                    )
                elif step == "process":
                    await workflow.execute_activity(
                        rollback_processing,
                        start_to_close_timeout=timedelta(minutes=2),
                        retry_policy=RetryPolicy(maximum_attempts=5)
                    )
                elif step == "commit":
                    await workflow.execute_activity(
                        rollback_transaction,
                        start_to_close_timeout=timedelta(seconds=30),
                        retry_policy=RetryPolicy(maximum_attempts=5)
                    )
            except Exception as comp_error:
                workflow.logger.error(f"Compensation failed for {step}: {comp_error}")
```

## Testing Workflows

```python
# tests/test_workflows.py
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.app.temporal.workflows.image_generation_workflow import (
    ImageGenerationWorkflow,
    ImageGenerationInput
)

@pytest.mark.asyncio
async def test_image_generation_workflow_success():
    """Test successful image generation workflow"""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Register workflow and activities
        worker = Worker(
            env.client,
            task_queue="test-queue",
            workflows=[ImageGenerationWorkflow],
            activities=[
                validate_prompt,
                check_content_filter,
                generate_with_huggingface,
                save_image_to_storage,
                update_generation_history,
                send_completion_notification
            ]
        )
        
        async with worker:
            # Execute workflow
            result = await env.client.execute_workflow(
                ImageGenerationWorkflow.run,
                ImageGenerationInput(
                    user_id="test_user",
                    prompt="A beautiful sunset",
                    backend="huggingface"
                ),
                id="test-workflow",
                task_queue="test-queue"
            )
            
            # Assertions
            assert result.status == "success"
            assert result.image_url is not None
            assert "sunset" in result.metadata["prompt"].lower()
```
