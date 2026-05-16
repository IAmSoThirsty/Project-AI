"""Multi-agent collaborative workflow system for Project-AI.

Implements Writer-Reviewer collaboration pattern where multiple AI agents
work together to produce refined outputs through iterative feedback loops.

All operations route through CognitionKernel for governance tracking.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class CollaborativeAgent(KernelRoutedAgent):
    """Base class for collaborative workflow agents.
    
    Provides OpenAI integration and message history tracking.
    All operations route through CognitionKernel.
    """
    
    def __init__(
        self,
        role: str,
        instructions: str,
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize collaborative agent.
        
        Args:
            role: Agent role (e.g., "Writer", "Reviewer")
            instructions: System instructions for this agent
            kernel: CognitionKernel instance for routing operations
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        
        self.role = role
        self.instructions = instructions
        self.message_history: list[dict[str, str]] = []
        
        # OpenAI client initialization
        self.openai_available = False
        self.client = None
        
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)
                self.openai_available = True
                logger.info(f"{role} agent: OpenAI client initialized")
            else:
                logger.warning(f"{role} agent: OPENAI_API_KEY not found")
        except ImportError:
            logger.warning(f"{role} agent: openai package not installed")
    
    def generate_response(self, prompt: str, context: str | None = None) -> str:
        """Generate response using OpenAI.
        
        Routes through kernel for governance tracking.
        
        Args:
            prompt: User prompt or request
            context: Optional context from previous agent
            
        Returns:
            Generated response text
        """
        return self._execute_through_kernel(
            action=self._do_generate_response,
            action_name=f"{self.role}.generate_response",
            action_args=(prompt, context),
        )
    
    def _do_generate_response(self, prompt: str, context: str | None) -> str:
        """Internal: Generate response (called through kernel)."""
        if not self.openai_available:
            return f"[{self.role} - OpenAI not available] Mock response to: {prompt[:50]}..."
        
        # Build messages
        messages = [{"role": "system", "content": self.instructions}]
        
        # Add context from previous agent if provided
        if context:
            messages.append({
                "role": "user",
                "content": f"Previous work:\n\n{context}"
            })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Add message history (last 3 exchanges to keep context manageable)
        for msg in self.message_history[-6:]:  # Last 3 exchanges = 6 messages
            messages.append(msg)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            
            content = response.choices[0].message.content
            
            # Update history
            self.message_history.append({"role": "user", "content": prompt})
            self.message_history.append({"role": "assistant", "content": content})
            
            return content
            
        except Exception as exc:
            logger.error(f"{self.role} generation failed: {exc}")
            return f"[{self.role} Error] {exc}"
    
    def reset_history(self) -> None:
        """Clear message history."""
        self.message_history.clear()


class WriterAgent(CollaborativeAgent):
    """Writer agent that creates initial content."""
    
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        instructions = """You are a Writer agent in a collaborative workflow.

Your role:
- Create clear, well-structured initial content based on user requests
- Write in a professional, informative style
- Organize information logically with clear sections
- Be thorough but concise

Focus on creating a solid first draft that provides value while being open to refinement."""
        
        super().__init__(
            role="Writer",
            instructions=instructions,
            kernel=kernel,
        )


class ReviewerAgent(CollaborativeAgent):
    """Reviewer agent that provides constructive feedback."""
    
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        instructions = """You are a Reviewer agent in a collaborative workflow.

Your role:
- Provide concise, actionable feedback on the Writer's content
- Identify specific areas for improvement
- Suggest concrete changes to enhance clarity and quality
- Be constructive and specific

Format your feedback as:
1. Strengths: What works well
2. Improvements: Specific suggestions (2-3 max)
3. Recommendation: REFINE or ACCEPT"""
        
        super().__init__(
            role="Reviewer",
            instructions=instructions,
            kernel=kernel,
        )


class CollaborativeWorkflow(KernelRoutedAgent):
    """Orchestrates multi-agent collaborative workflows.
    
    Manages Writer-Reviewer collaboration with iterative refinement.
    All workflow operations route through CognitionKernel.
    """
    
    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        max_iterations: int = 2,
    ) -> None:
        """Initialize collaborative workflow.
        
        Args:
            kernel: CognitionKernel instance for routing operations
            max_iterations: Maximum refinement iterations
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        
        self.writer = WriterAgent(kernel=kernel)
        self.reviewer = ReviewerAgent(kernel=kernel)
        self.max_iterations = max_iterations
        
        # Workflow state tracking
        self.workflow_history: list[dict[str, Any]] = []
        os.makedirs("data/collaborative_workflows", exist_ok=True)
    
    def execute(self, user_request: str) -> dict[str, Any]:
        """Execute collaborative workflow.
        
        Routes through kernel for governance tracking.
        
        Args:
            user_request: User's request for content/analysis
            
        Returns:
            Dictionary containing:
                - final_content: Refined output
                - iterations: Number of refinement cycles
                - history: Complete workflow trace
        """
        return self._execute_through_kernel(
            action=self._do_execute_workflow,
            action_name="CollaborativeWorkflow.execute",
            action_args=(user_request,),
        )
    
    def _do_execute_workflow(self, user_request: str) -> dict[str, Any]:
        """Internal: Execute workflow (called through kernel)."""
        logger.info(f"Starting collaborative workflow: {user_request[:50]}...")
        
        # Reset agent histories
        self.writer.reset_history()
        self.reviewer.reset_history()
        
        workflow_trace = {
            "request": user_request,
            "timestamp": datetime.now(UTC).isoformat(),
            "iterations": [],
        }
        
        current_content = None
        iteration_count = 0
        
        for i in range(self.max_iterations):
            iteration_count = i + 1
            iteration_data = {"iteration": iteration_count}
            
            # Writer creates or refines content
            if current_content is None:
                # First iteration: create initial content
                prompt = user_request
                context = None
            else:
                # Subsequent iterations: refine based on feedback
                prompt = f"Please refine the content based on this feedback:\n\n{feedback}"
                context = current_content
            
            logger.info(f"Iteration {iteration_count}: Writer generating...")
            writer_output = self.writer.generate_response(prompt, context)
            iteration_data["writer_output"] = writer_output
            current_content = writer_output
            
            # Reviewer provides feedback
            logger.info(f"Iteration {iteration_count}: Reviewer evaluating...")
            review_prompt = f"Please review this content:\n\n{current_content}"
            feedback = self.reviewer.generate_response(review_prompt)
            iteration_data["reviewer_feedback"] = feedback
            
            # Check if reviewer accepts
            if "ACCEPT" in feedback.upper():
                logger.info(f"Reviewer accepted after {iteration_count} iteration(s)")
                iteration_data["decision"] = "ACCEPTED"
                workflow_trace["iterations"].append(iteration_data)
                break
            else:
                iteration_data["decision"] = "REFINE"
                workflow_trace["iterations"].append(iteration_data)
        
        # Compile final result
        result = {
            "final_content": current_content,
            "iterations": iteration_count,
            "history": workflow_trace,
            "max_iterations_reached": iteration_count >= self.max_iterations,
        }
        
        # Save workflow trace
        self._save_workflow_trace(workflow_trace, result)
        
        return result
    
    def _save_workflow_trace(
        self,
        workflow_trace: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """Save workflow execution trace to disk."""
        timestamp_slug = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"data/collaborative_workflows/workflow_{timestamp_slug}.json"
        
        trace_data = {
            "workflow_trace": workflow_trace,
            "result_summary": {
                "iterations": result["iterations"],
                "max_iterations_reached": result["max_iterations_reached"],
                "final_content_length": len(result["final_content"]),
            },
        }
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(trace_data, f, indent=2)
            logger.info(f"Workflow trace saved to {filename}")
        except Exception as exc:
            logger.warning(f"Failed to save workflow trace: {exc}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def run_collaborative_workflow(
    user_request: str,
    kernel: CognitionKernel | None = None,
    max_iterations: int = 2,
) -> dict[str, Any]:
    """Convenience function to run a collaborative workflow.
    
    Args:
        user_request: User's content request
        kernel: Optional CognitionKernel instance
        max_iterations: Maximum refinement iterations
        
    Returns:
        Workflow result dictionary
    """
    workflow = CollaborativeWorkflow(
        kernel=kernel,
        max_iterations=max_iterations,
    )
    return workflow.execute(user_request)
