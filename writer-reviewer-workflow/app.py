"""
Writer-Reviewer Content Collaboration Workflow

Multi-agent workflow where a Writer creates initial content and a Reviewer
provides feedback to refine it. Both agents yield their outputs as the final result.
"""

import logging
import os
from typing import Annotated, Any

from agent_framework import BaseAgent, ConversationContext
from agent_framework.clients import AzureOpenAIResponsesClient
from agent_framework.graph import Graph
from agent_framework.hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from dotenv import load_dotenv

# Load environment variables (Foundry-injected vars take precedence)
load_dotenv(override=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """
    Writer agent that creates initial content based on user requests.
    """

    def __init__(self, client: AzureOpenAIResponsesClient, model_deployment: str):
        """
        Initialize Writer agent.

        Args:
            client: Azure OpenAI client for model inference
            model_deployment: Name of the model deployment to use
        """
        super().__init__(
            name="writer",
            instructions="""You are a skilled content writer. Your role is to:
1. Understand the user's content request
2. Create well-structured, engaging initial content
3. Focus on clarity, coherence, and meeting the user's requirements
4. Provide content that is ready for review and refinement

Write in a professional yet accessible tone. Ensure your content is comprehensive
and addresses all aspects of the request.""",
            model=model_deployment,
            client=client,
        )
        logger.info("Writer agent initialized with model: %s", model_deployment)

    async def run(
        self,
        context: ConversationContext,
        state: Annotated[dict[str, Any], "Current workflow state"],
    ) -> dict[str, Any]:
        """
        Execute writer agent to create initial content.

        Args:
            context: Conversation context with user messages
            state: Current workflow state

        Returns:
            Updated state with writer's content
        """
        logger.info("Writer agent starting content creation")

        # Get the user's request from the conversation
        user_request = context.messages[-1].content if context.messages else "Create content"
        logger.info("User request: %s", user_request[:100])

        # Create content using the agent
        response = await super().run(context)

        # Extract the writer's content
        writer_content = response.messages[-1].content if response.messages else ""

        logger.info("Writer agent completed. Content length: %d chars", len(writer_content))

        # Update state with writer's output
        state["writer_content"] = writer_content
        state["original_request"] = user_request

        return state


class ReviewerAgent(BaseAgent):
    """
    Reviewer agent that provides feedback and refinements to content.
    """

    def __init__(self, client: AzureOpenAIResponsesClient, model_deployment: str):
        """
        Initialize Reviewer agent.

        Args:
            client: Azure OpenAI client for model inference
            model_deployment: Name of the model deployment to use
        """
        super().__init__(
            name="reviewer",
            instructions="""You are an expert content reviewer. Your role is to:
1. Carefully review the provided content
2. Identify areas for improvement (clarity, structure, completeness, tone)
3. Provide concise, actionable feedback
4. Suggest specific refinements to enhance the content quality

Focus on constructive criticism. Be specific about what to improve and why.
Your feedback should be clear and easy to act upon.""",
            model=model_deployment,
            client=client,
        )
        logger.info("Reviewer agent initialized with model: %s", model_deployment)

    async def run(
        self,
        context: ConversationContext,
        state: Annotated[dict[str, Any], "Current workflow state"],
    ) -> dict[str, Any]:
        """
        Execute reviewer agent to provide feedback on writer's content.

        Args:
            context: Conversation context
            state: Current workflow state with writer's content

        Returns:
            Updated state with reviewer's feedback
        """
        logger.info("Reviewer agent starting content review")

        # Get the writer's content from state
        writer_content = state.get("writer_content", "")
        original_request = state.get("original_request", "")

        if not writer_content:
            logger.warning("No writer content found in state")
            state["reviewer_feedback"] = "No content to review."
            return state

        # Create a new context with the writer's content for review
        review_context = ConversationContext(
            messages=[
                {
                    "role": "user",
                    "content": f"""Please review this content that was created for the following request:

Original Request: {original_request}

Content to Review:
{writer_content}

Provide concise, actionable feedback on how to improve this content.""",
                }
            ]
        )

        # Get reviewer feedback
        response = await super().run(review_context)

        # Extract reviewer's feedback
        reviewer_feedback = response.messages[-1].content if response.messages else ""

        logger.info("Reviewer agent completed. Feedback length: %d chars", len(reviewer_feedback))

        # Update state with reviewer's output
        state["reviewer_feedback"] = reviewer_feedback

        return state


def build_workflow(client: AzureOpenAIResponsesClient, model_deployment: str) -> Graph:
    """
    Build the Writer-Reviewer workflow graph.

    Args:
        client: Azure OpenAI client
        model_deployment: Model deployment name

    Returns:
        Configured workflow graph
    """
    logger.info("Building Writer-Reviewer workflow graph")

    # Create agents
    writer = WriterAgent(client, model_deployment)
    reviewer = ReviewerAgent(client, model_deployment)

    # Define output executor function
    def format_output(state: dict[str, Any]) -> str:
        """
        Format the final collaborative output from both agents.

        Args:
            state: Workflow state containing both agents' outputs

        Returns:
            Plain text output with writer's content and reviewer's feedback
        """
        writer_content = state.get("writer_content", "No content generated")
        reviewer_feedback = state.get("reviewer_feedback", "No feedback provided")

        output = f"""=== WRITER-REVIEWER COLLABORATION OUTPUT ===

INITIAL CONTENT (by Writer):
{writer_content}

---

REVIEW & FEEDBACK (by Reviewer):
{reviewer_feedback}

=== END OF COLLABORATION ==="""

        logger.info("Formatted collaborative output: %d chars", len(output))
        return output

    # Build workflow graph
    graph = Graph()

    # Add nodes
    graph.add_node("writer", writer)
    graph.add_node("reviewer", reviewer)
    graph.add_node("format_output", format_output)

    # Define edges: writer → reviewer → format_output
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", "format_output")

    # Set entry point
    graph.set_entry_point("writer")

    # Set finish point (output executor)
    graph.set_finish_point("format_output")

    logger.info("Workflow graph built successfully")

    return graph


def create_client() -> AzureOpenAIResponsesClient:
    """
    Create Azure OpenAI client with appropriate credentials.

    Returns:
        Configured AzureOpenAIResponsesClient instance
    """
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    
    if not project_endpoint:
        raise ValueError(
            "FOUNDRY_PROJECT_ENDPOINT environment variable is required. "
            "Set it in .env file for local development."
        )

    # Use ManagedIdentityCredential in production (Foundry), DefaultAzureCredential for local dev
    is_production = os.getenv("FOUNDRY_AGENT_NAME") is not None
    credential = ManagedIdentityCredential() if is_production else DefaultAzureCredential()

    logger.info(
        "Creating Azure OpenAI client with %s credentials",
        "ManagedIdentity" if is_production else "DefaultAzure"
    )

    client = AzureOpenAIResponsesClient(
        endpoint=project_endpoint,
        credential=credential,
    )

    return client


def main():
    """
    Main entrypoint: Initialize and run the hosted agent server.
    """
    logger.info("Starting Writer-Reviewer Workflow Application")

    # Get configuration
    model_deployment = os.getenv(
        "FOUNDRY_MODEL_DEPLOYMENT_NAME",
        os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    )
    logger.info("Using model deployment: %s", model_deployment)

    # Create Azure OpenAI client
    client = create_client()

    # Build workflow graph
    workflow_graph = build_workflow(client, model_deployment)

    # Compile the graph
    app = workflow_graph.compile()
    logger.info("Workflow graph compiled successfully")

    # Create hosting server with the compiled graph
    server = ResponsesHostServer(agent=app)

    logger.info("Starting HTTP server on port 8088...")
    server.run()


if __name__ == "__main__":
    main()
