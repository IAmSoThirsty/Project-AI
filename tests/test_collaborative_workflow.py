"""Tests for collaborative workflow system."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.agents.collaborative_workflow import (
    CollaborativeAgent,
    CollaborativeWorkflow,
    ReviewerAgent,
    WriterAgent,
    run_collaborative_workflow,
)


class TestCollaborativeAgent:
    """Tests for CollaborativeAgent base class."""
    
    def test_initialization_without_openai(self) -> None:
        """Test agent initialization when OpenAI is not available."""
        agent = CollaborativeAgent(
            role="TestAgent",
            instructions="Test instructions",
        )
        
        assert agent.role == "TestAgent"
        assert agent.instructions == "Test instructions"
        assert agent.message_history == []
    
    def test_reset_history(self) -> None:
        """Test resetting message history."""
        agent = CollaborativeAgent(
            role="TestAgent",
            instructions="Test instructions",
        )
        
        # Add some history
        agent.message_history = [
            {"role": "user", "content": "test1"},
            {"role": "assistant", "content": "response1"},
        ]
        
        # Reset
        agent.reset_history()
        
        assert agent.message_history == []
    
    @patch("app.agents.collaborative_workflow.openai.OpenAI")
    def test_generate_response_with_openai(self, mock_openai_class: MagicMock) -> None:
        """Test response generation with OpenAI."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Generated response"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Create agent with mocked OpenAI
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = CollaborativeAgent(
                role="TestAgent",
                instructions="Test instructions",
            )
            agent.client = mock_client
            agent.openai_available = True
            
            # Generate response
            response = agent.generate_response("Test prompt")
            
            assert response == "Generated response"
            assert len(agent.message_history) == 2
            assert agent.message_history[0]["role"] == "user"
            assert agent.message_history[1]["role"] == "assistant"
    
    def test_generate_response_without_openai(self) -> None:
        """Test response generation without OpenAI (mock mode)."""
        agent = CollaborativeAgent(
            role="TestAgent",
            instructions="Test instructions",
        )
        agent.openai_available = False
        
        response = agent.generate_response("Test prompt")
        
        assert "[TestAgent - OpenAI not available]" in response
        assert "Mock response" in response


class TestWriterAgent:
    """Tests for WriterAgent."""
    
    def test_initialization(self) -> None:
        """Test writer agent initialization."""
        writer = WriterAgent()
        
        assert writer.role == "Writer"
        assert "Writer agent" in writer.instructions
        assert "create initial content" in writer.instructions.lower()
    
    @patch("app.agents.collaborative_workflow.openai.OpenAI")
    def test_writer_response_format(self, mock_openai_class: MagicMock) -> None:
        """Test writer generates proper content."""
        # Mock OpenAI
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="# Test Article\n\nThis is test content."
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            writer = WriterAgent()
            writer.client = mock_client
            writer.openai_available = True
            
            response = writer.generate_response("Write about testing")
            
            assert "Test Article" in response
            assert "test content" in response


class TestReviewerAgent:
    """Tests for ReviewerAgent."""
    
    def test_initialization(self) -> None:
        """Test reviewer agent initialization."""
        reviewer = ReviewerAgent()
        
        assert reviewer.role == "Reviewer"
        assert "Reviewer agent" in reviewer.instructions
        assert "feedback" in reviewer.instructions.lower()
        assert "REFINE or ACCEPT" in reviewer.instructions
    
    @patch("app.agents.collaborative_workflow.openai.OpenAI")
    def test_reviewer_provides_feedback(self, mock_openai_class: MagicMock) -> None:
        """Test reviewer provides structured feedback."""
        # Mock OpenAI
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        "Strengths: Clear structure\n"
                        "Improvements: Add examples\n"
                        "Recommendation: REFINE"
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            reviewer = ReviewerAgent()
            reviewer.client = mock_client
            reviewer.openai_available = True
            
            response = reviewer.generate_response("Test content to review")
            
            assert "Strengths:" in response
            assert "Improvements:" in response
            assert "Recommendation:" in response


class TestCollaborativeWorkflow:
    """Tests for CollaborativeWorkflow orchestration."""
    
    def test_initialization(self) -> None:
        """Test workflow initialization."""
        workflow = CollaborativeWorkflow(max_iterations=3)
        
        assert workflow.max_iterations == 3
        assert isinstance(workflow.writer, WriterAgent)
        assert isinstance(workflow.reviewer, ReviewerAgent)
        assert workflow.workflow_history == []
    
    def test_workflow_saves_trace(self, tmp_path: Path) -> None:
        """Test workflow saves execution trace."""
        # Mock data directory
        data_dir = tmp_path / "data" / "collaborative_workflows"
        data_dir.mkdir(parents=True)
        
        with patch("app.agents.collaborative_workflow.os.makedirs"):
            workflow = CollaborativeWorkflow(max_iterations=1)
            
            # Mock agents to avoid OpenAI calls
            workflow.writer.openai_available = False
            workflow.reviewer.openai_available = False
            
            # Mock reviewer to accept immediately
            with patch.object(
                workflow.reviewer,
                "generate_response",
                return_value="Strengths: Good.\nRecommendation: ACCEPT",
            ):
                with patch.object(
                    workflow.writer,
                    "generate_response",
                    return_value="Test content",
                ):
                    result = workflow.execute("Test request")
            
            assert result["iterations"] == 1
            assert result["final_content"] == "Test content"
            assert "history" in result
    
    @patch("app.agents.collaborative_workflow.openai.OpenAI")
    def test_workflow_refinement_loop(self, mock_openai_class: MagicMock) -> None:
        """Test workflow performs refinement iterations."""
        # Mock OpenAI
        mock_client = MagicMock()
        
        # First iteration: Writer creates, Reviewer asks for refinement
        # Second iteration: Writer refines, Reviewer accepts
        responses = [
            "Initial content",  # Writer iteration 1
            "Strengths: OK\nRecommendation: REFINE",  # Reviewer iteration 1
            "Refined content with improvements",  # Writer iteration 2
            "Strengths: Excellent\nRecommendation: ACCEPT",  # Reviewer iteration 2
        ]
        
        mock_response_iter = iter(responses)
        
        def create_mock_response(*args, **kwargs):
            content = next(mock_response_iter)
            mock_resp = MagicMock()
            mock_resp.choices = [
                MagicMock(message=MagicMock(content=content))
            ]
            return mock_resp
        
        mock_client.chat.completions.create.side_effect = create_mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            workflow = CollaborativeWorkflow(max_iterations=2)
            workflow.writer.client = mock_client
            workflow.writer.openai_available = True
            workflow.reviewer.client = mock_client
            workflow.reviewer.openai_available = True
            
            result = workflow.execute("Test request")
            
            # Should complete in 2 iterations
            assert result["iterations"] == 2
            assert "Refined content" in result["final_content"]
            assert not result["max_iterations_reached"]
            
            # Check history
            assert len(result["history"]["iterations"]) == 2
            assert result["history"]["iterations"][0]["decision"] == "REFINE"
            assert result["history"]["iterations"][1]["decision"] == "ACCEPTED"
    
    def test_workflow_max_iterations(self) -> None:
        """Test workflow respects max iteration limit."""
        workflow = CollaborativeWorkflow(max_iterations=1)
        workflow.writer.openai_available = False
        workflow.reviewer.openai_available = False
        
        # Mock reviewer to always ask for refinement
        with patch.object(
            workflow.reviewer,
            "generate_response",
            return_value="Recommendation: REFINE",
        ):
            with patch.object(
                workflow.writer,
                "generate_response",
                return_value="Content",
            ):
                result = workflow.execute("Test")
        
        assert result["iterations"] == 1
        assert result["max_iterations_reached"] is True


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_run_collaborative_workflow(self) -> None:
        """Test convenience function."""
        with patch("app.agents.collaborative_workflow.CollaborativeWorkflow") as mock_class:
            mock_workflow = MagicMock()
            mock_workflow.execute.return_value = {
                "final_content": "Test",
                "iterations": 1,
            }
            mock_class.return_value = mock_workflow
            
            result = run_collaborative_workflow("Test request")
            
            assert result["final_content"] == "Test"
            mock_class.assert_called_once()
            mock_workflow.execute.assert_called_once_with("Test request")


class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow_without_openai(self) -> None:
        """Test complete workflow in mock mode (no OpenAI)."""
        workflow = CollaborativeWorkflow(max_iterations=2)
        
        # Verify agents are created
        assert workflow.writer.openai_available is False
        assert workflow.reviewer.openai_available is False
        
        # Execute workflow (will use mock responses)
        result = workflow.execute("Explain collaborative AI")
        
        # Verify result structure
        assert "final_content" in result
        assert "iterations" in result
        assert "history" in result
        assert result["iterations"] >= 1
