"""
Writer-Reviewer Multi-Agent Workflow
======================================
A collaborative workflow where a Writer agent creates initial content,
a Reviewer agent provides concise feedback, and they collaborate to
produce refined content.

Flow:
1. User sends request to Writer
2. Writer creates initial content
3. Content passes to Reviewer for feedback
4. Writer refines based on feedback
5. Both agents yield collaborative result as final output
"""

from azure.ai.foundry.agents import (
    Agent,
    AgentThread,
    AgentRunner,
    AgentGraphExecutor,
)
from azure.ai.foundry.agents.state import StateMessage
from azure.identity import DefaultAzureCredential
import os
import logging
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WriterReviewerWorkflow:
    """Multi-agent workflow orchestrating Writer and Reviewer collaboration."""
    
    def __init__(self, project_endpoint: str, model_deployment_name: str):
        """
        Initialize the Writer-Reviewer workflow.
        
        Args:
            project_endpoint: Azure AI Foundry project endpoint URL
            model_deployment_name: Name of the model deployment to use
        """
        self.project_endpoint = project_endpoint
        self.model_deployment_name = model_deployment_name
        self.credential = DefaultAzureCredential()
        
        # Initialize agents
        self._create_agents()
        
        # Create workflow graph
        self._create_workflow_graph()
    
    def _create_agents(self):
        """Create Writer and Reviewer agents."""
        
        # Writer Agent: Creates initial content
        self.writer_agent = Agent(
            name="ContentWriter",
            model=self.model_deployment_name,
            instructions="""You are a professional content writer. Your role is to:
            1. Understand the user's content request thoroughly
            2. Create clear, well-structured, and engaging content
            3. Be receptive to feedback and willing to refine your work
            4. Maintain a professional yet accessible tone
            
            When creating content:
            - Focus on clarity and coherence
            - Use appropriate structure (headings, paragraphs, lists)
            - Ensure factual accuracy when relevant
            - Make it audience-appropriate
            
            When receiving feedback:
            - Acknowledge the suggestions
            - Incorporate actionable feedback
            - Maintain the core message while improving quality""",
            credentials=self.credential,
            project_endpoint=self.project_endpoint,
        )
        
        # Reviewer Agent: Provides concise, actionable feedback
        self.reviewer_agent = Agent(
            name="ContentReviewer",
            model=self.model_deployment_name,
            instructions="""You are a professional content reviewer. Your role is to:
            1. Analyze content for clarity, coherence, and quality
            2. Provide concise, actionable feedback
            3. Focus on high-impact improvements
            4. Be constructive and specific
            
            When reviewing content:
            - Identify 2-3 key areas for improvement
            - Be specific about what needs changing and why
            - Suggest concrete improvements
            - Note what works well
            - Keep feedback concise (3-5 bullet points maximum)
            
            Feedback format:
            ✅ Strengths: [What works well]
            🔧 Improvements: [2-3 specific actionable changes]
            💡 Suggestion: [Optional enhancement]""",
            credentials=self.credential,
            project_endpoint=self.project_endpoint,
        )
    
    def _create_workflow_graph(self):
        """Create the workflow execution graph."""
        
        # Define workflow stages
        async def writer_stage(state: dict[str, Any]) -> dict[str, Any]:
            """Stage 1: Writer creates initial content."""
            user_request = state.get("user_request", "")
            iteration = state.get("iteration", 0)
            feedback = state.get("feedback", "")
            
            # Create thread for writer
            thread = AgentThread()
            
            if iteration == 0:
                # First iteration: create initial content
                prompt = f"Create content for the following request:\n\n{user_request}"
            else:
                # Refinement iteration: incorporate feedback
                previous_content = state.get("content", "")
                prompt = f"""Refine the following content based on the reviewer's feedback.

Previous content:
{previous_content}

Reviewer feedback:
{feedback}

Please revise the content to address the feedback while maintaining quality."""
            
            # Run writer agent
            runner = AgentRunner(agent=self.writer_agent, thread=thread)
            async with runner:
                await runner.create_message(content=prompt)
                result = await runner.run()
                
                # Extract content from response
                if result.messages:
                    content = result.messages[-1].content[0].text.value
                else:
                    content = ""
            
            state["content"] = content
            state["iteration"] = iteration + 1
            
            logger.info(f"Writer iteration {iteration + 1} complete")
            return state
        
        async def reviewer_stage(state: dict[str, Any]) -> dict[str, Any]:
            """Stage 2: Reviewer provides feedback."""
            content = state.get("content", "")
            iteration = state.get("iteration", 0)
            
            # Create thread for reviewer
            thread = AgentThread()
            
            prompt = f"""Review the following content and provide concise, actionable feedback:

{content}

Remember to keep feedback concise (3-5 bullet points) and focus on high-impact improvements."""
            
            # Run reviewer agent
            runner = AgentRunner(agent=self.reviewer_agent, thread=thread)
            async with runner:
                await runner.create_message(content=prompt)
                result = await runner.run()
                
                # Extract feedback from response
                if result.messages:
                    feedback = result.messages[-1].content[0].text.value
                else:
                    feedback = ""
            
            state["feedback"] = feedback
            
            logger.info(f"Reviewer iteration {iteration} complete")
            return state
        
        async def decide_next(state: dict[str, Any]) -> str:
            """Decision node: continue refining or finalize?"""
            iteration = state.get("iteration", 0)
            max_iterations = state.get("max_iterations", 2)
            
            if iteration >= max_iterations:
                return "finalize"
            else:
                return "refine"
        
        async def finalize_stage(state: dict[str, Any]) -> dict[str, Any]:
            """Stage 3: Finalize and return result."""
            state["status"] = "complete"
            logger.info("Workflow complete")
            return state
        
        # Create graph executor
        self.graph = AgentGraphExecutor()
        
        # Add nodes
        self.graph.add_node("writer", writer_stage)
        self.graph.add_node("reviewer", reviewer_stage)
        self.graph.add_node("decide", decide_next)
        self.graph.add_node("finalize", finalize_stage)
        
        # Add edges
        self.graph.add_edge("START", "writer")
        self.graph.add_edge("writer", "reviewer")
        self.graph.add_edge("reviewer", "decide")
        self.graph.add_conditional_edges(
            "decide",
            {
                "refine": "writer",
                "finalize": "finalize",
            }
        )
        self.graph.add_edge("finalize", "END")
    
    async def run(self, user_request: str, max_iterations: int = 2) -> str:
        """
        Run the Writer-Reviewer workflow.
        
        Args:
            user_request: The content request from the user
            max_iterations: Maximum refinement iterations (default: 2)
        
        Returns:
            Final refined content as plain text
        """
        # Initial state
        initial_state = {
            "user_request": user_request,
            "iteration": 0,
            "max_iterations": max_iterations,
            "content": "",
            "feedback": "",
            "status": "running",
        }
        
        # Execute workflow
        final_state = await self.graph.run(initial_state)
        
        # Return final content
        return final_state.get("content", "")


# Entry point for hosted agent responses protocol
async def handle_message(message: StateMessage) -> str:
    """
    Handle incoming messages from users.
    
    Args:
        message: The incoming message state
    
    Returns:
        The refined content after Writer-Reviewer collaboration
    """
    # Extract configuration from environment
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4")
    
    if not project_endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable not set")
    
    # Create workflow instance
    workflow = WriterReviewerWorkflow(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment,
    )
    
    # Extract user request from message
    user_request = message.content
    
    # Run workflow
    result = await workflow.run(user_request)
    
    return result


# For local testing
if __name__ == "__main__":
    import asyncio
    
    async def test_workflow():
        """Test the workflow locally."""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
        model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4")
        
        workflow = WriterReviewerWorkflow(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment,
        )
        
        # Test request
        test_request = """Write a brief introduction (2-3 paragraphs) about the 
        importance of collaboration in software development."""
        
        print("🚀 Starting Writer-Reviewer workflow...")
        print(f"Request: {test_request}\n")
        
        result = await workflow.run(test_request)
        
        print("✅ Workflow complete!")
        print("\n📝 Final refined content:")
        print("=" * 60)
        print(result)
        print("=" * 60)
    
    asyncio.run(test_workflow())
