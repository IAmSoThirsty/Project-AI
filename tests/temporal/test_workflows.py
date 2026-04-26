"""
Tests for Temporal.io workflow definitions.
"""

from app.temporal.workflows import (
    DataAnalysisRequest,
    ImageGenerationRequest,
    LearningRequest,
    LearningResult,
    MemoryExpansionResult,
)


class TestWorkflowDataClasses:
    """Test workflow input/output data classes."""

    def test_learning_request(self):
        """Test LearningRequest data class."""
        request = LearningRequest(
            content="Test content",
            source="test_source",
            category="programming",
            user_id="user123",
        )

        assert request.content == "Test content"
        assert request.source == "test_source"
        assert request.category == "programming"
        assert request.user_id == "user123"

    def test_learning_result_success(self):
        """Test successful LearningResult."""
        result = LearningResult(
            success=True,
            knowledge_id="kb123",
        )

        assert result.success is True
        assert result.knowledge_id == "kb123"
        assert result.error is None

    def test_image_generation_request(self):
        """Test ImageGenerationRequest data class."""
        request = ImageGenerationRequest(
            prompt="A beautiful sunset",
            style="photorealistic",
        )

        assert request.prompt == "A beautiful sunset"
        assert request.style == "photorealistic"
        assert request.size == "1024x1024"
        assert request.backend == "huggingface"

    def test_data_analysis_request(self):
        """Test DataAnalysisRequest data class."""
        request = DataAnalysisRequest(
            file_path="/data/file.csv",
            analysis_type="clustering",
        )

        assert request.file_path == "/data/file.csv"
        assert request.analysis_type == "clustering"

    def test_memory_expansion_result_success(self):
        """Test successful MemoryExpansionResult."""
        result = MemoryExpansionResult(
            success=True,
            memory_count=5,
        )

        assert result.success is True
        assert result.memory_count == 5
        assert result.error is None
