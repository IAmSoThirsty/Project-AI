"""
Temporal Workflow Definitions for Project-AI.

Defines durable workflows for AI operations including learning,
memory expansion, image generation, and data analysis.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)


# Workflow input/output data classes
@dataclass
class LearningRequest:
    """Input for AI learning workflow."""
    content: str
    source: str
    category: str
    user_id: str | None = None


@dataclass
class LearningResult:
    """Result from AI learning workflow."""
    success: bool
    knowledge_id: str | None = None
    error: str | None = None


@dataclass
class ImageGenerationRequest:
    """Input for image generation workflow."""
    prompt: str
    style: str = "photorealistic"
    size: str = "1024x1024"
    backend: str = "huggingface"
    user_id: str | None = None


@dataclass
class ImageGenerationResult:
    """Result from image generation workflow."""
    success: bool
    image_path: str | None = None
    metadata: dict | None = None
    error: str | None = None


@dataclass
class DataAnalysisRequest:
    """Input for data analysis workflow."""
    file_path: str
    analysis_type: str  # 'clustering', 'statistics', 'visualization'
    user_id: str | None = None


@dataclass
class DataAnalysisResult:
    """Result from data analysis workflow."""
    success: bool
    results: dict | None = None
    output_path: str | None = None
    error: str | None = None


@dataclass
class MemoryExpansionRequest:
    """Input for memory expansion workflow."""
    conversation_id: str
    messages: list[dict]
    user_id: str | None = None


@dataclass
class MemoryExpansionResult:
    """Result from memory expansion workflow."""
    success: bool
    memory_count: int = 0
    error: str | None = None


# Workflow Definitions

@workflow.defn
class AILearningWorkflow:
    """
    Durable workflow for AI learning requests.

    Handles the complete learning pipeline including:
    - Content validation
    - Black Vault checks
    - Knowledge extraction
    - Storage and indexing
    - Approval workflow
    """

    @workflow.run
    async def run(self, request: LearningRequest) -> LearningResult:
        """
        Execute the AI learning workflow.

        Args:
            request: Learning request with content and metadata

        Returns:
            Learning result with success status and knowledge ID
        """
        workflow.logger.info(
            f"Starting AI learning workflow for category: {request.category}"
        )

        try:
            # Activity 1: Validate content
            is_valid = await workflow.execute_activity(
                "validate_learning_content",
                request,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            if not is_valid:
                return LearningResult(
                    success=False,
                    error="Content validation failed"
                )

            # Activity 2: Check Black Vault
            is_allowed = await workflow.execute_activity(
                "check_black_vault",
                request.content,
                start_to_close_timeout=timedelta(seconds=10),
            )

            if not is_allowed:
                return LearningResult(
                    success=False,
                    error="Content blocked by Black Vault"
                )

            # Activity 3: Process learning request
            knowledge_id = await workflow.execute_activity(
                "process_learning_request",
                request,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=30),
                ),
            )

            # Activity 4: Store in knowledge base
            await workflow.execute_activity(
                "store_knowledge",
                {"knowledge_id": knowledge_id, "request": request},
                start_to_close_timeout=timedelta(seconds=30),
            )

            workflow.logger.info(f"Learning workflow completed: {knowledge_id}")
            return LearningResult(success=True, knowledge_id=knowledge_id)

        except Exception as e:
            workflow.logger.error(f"Learning workflow failed: {e}")
            return LearningResult(success=False, error=str(e))


@workflow.defn
class ImageGenerationWorkflow:
    """
    Durable workflow for image generation.

    Handles:
    - Content filtering
    - Style processing
    - Image generation (with retries)
    - Storage and metadata tracking
    """

    @workflow.run
    async def run(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Execute the image generation workflow.

        Args:
            request: Image generation request with prompt and parameters

        Returns:
            Generation result with image path and metadata
        """
        workflow.logger.info(
            f"Starting image generation workflow: {request.backend}"
        )

        try:
            # Activity 1: Content filtering
            is_safe = await workflow.execute_activity(
                "check_content_safety",
                request.prompt,
                start_to_close_timeout=timedelta(seconds=10),
            )

            if not is_safe:
                return ImageGenerationResult(
                    success=False,
                    error="Prompt failed content safety check"
                )

            # Activity 2: Generate image (long-running, needs retries)
            result = await workflow.execute_activity(
                "generate_image",
                request,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(minutes=1),
                ),
            )

            # Activity 3: Store metadata
            await workflow.execute_activity(
                "store_image_metadata",
                result,
                start_to_close_timeout=timedelta(seconds=30),
            )

            workflow.logger.info("Image generation workflow completed")
            return ImageGenerationResult(
                success=True,
                image_path=result["image_path"],
                metadata=result.get("metadata"),
            )

        except Exception as e:
            workflow.logger.error(f"Image generation workflow failed: {e}")
            return ImageGenerationResult(success=False, error=str(e))


@workflow.defn
class DataAnalysisWorkflow:
    """
    Durable workflow for data analysis tasks.

    Handles:
    - File validation
    - Data loading and preprocessing
    - Analysis execution
    - Result visualization and storage
    """

    @workflow.run
    async def run(self, request: DataAnalysisRequest) -> DataAnalysisResult:
        """
        Execute the data analysis workflow.

        Args:
            request: Analysis request with file path and type

        Returns:
            Analysis result with findings and output path
        """
        workflow.logger.info(
            f"Starting data analysis workflow: {request.analysis_type}"
        )

        try:
            # Activity 1: Validate file
            is_valid = await workflow.execute_activity(
                "validate_data_file",
                request.file_path,
                start_to_close_timeout=timedelta(seconds=30),
            )

            if not is_valid:
                return DataAnalysisResult(
                    success=False,
                    error="File validation failed"
                )

            # Activity 2: Load data
            data = await workflow.execute_activity(
                "load_data",
                request.file_path,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            # Activity 3: Perform analysis
            results = await workflow.execute_activity(
                "perform_analysis",
                {"data": data, "type": request.analysis_type},
                start_to_close_timeout=timedelta(minutes=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=2,
                    initial_interval=timedelta(seconds=10),
                ),
            )

            # Activity 4: Generate visualizations
            output_path = await workflow.execute_activity(
                "generate_visualizations",
                results,
                start_to_close_timeout=timedelta(minutes=5),
            )

            workflow.logger.info("Data analysis workflow completed")
            return DataAnalysisResult(
                success=True,
                results=results,
                output_path=output_path,
            )

        except Exception as e:
            workflow.logger.error(f"Data analysis workflow failed: {e}")
            return DataAnalysisResult(success=False, error=str(e))


@workflow.defn
class MemoryExpansionWorkflow:
    """
    Durable workflow for memory expansion.

    Handles:
    - Conversation processing
    - Knowledge extraction
    - Memory storage
    - Index updates
    """

    @workflow.run
    async def run(self, request: MemoryExpansionRequest) -> MemoryExpansionResult:
        """
        Execute the memory expansion workflow.

        Args:
            request: Memory expansion request with conversation data

        Returns:
            Result with count of memories created
        """
        workflow.logger.info(
            f"Starting memory expansion workflow for conversation: "
            f"{request.conversation_id}"
        )

        try:
            # Activity 1: Extract key information
            extracted_info = await workflow.execute_activity(
                "extract_memory_information",
                request.messages,
                start_to_close_timeout=timedelta(minutes=2),
            )

            # Activity 2: Store memories
            memory_count = await workflow.execute_activity(
                "store_memories",
                {
                    "conversation_id": request.conversation_id,
                    "info": extracted_info,
                    "user_id": request.user_id,
                },
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            # Activity 3: Update indexes
            await workflow.execute_activity(
                "update_memory_indexes",
                request.conversation_id,
                start_to_close_timeout=timedelta(seconds=30),
            )

            workflow.logger.info(
                f"Memory expansion workflow completed: {memory_count} memories"
            )
            return MemoryExpansionResult(
                success=True,
                memory_count=memory_count,
            )

        except Exception as e:
            workflow.logger.error(f"Memory expansion workflow failed: {e}")
            return MemoryExpansionResult(success=False, error=str(e))
