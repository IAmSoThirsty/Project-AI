"""
Core Task Activities.

These activities implement atomic operations that can be orchestrated by workflows.
Each activity represents a single unit of work that can be executed and retried independently.

Activities should be:
- Idempotent: Safe to retry without side effects
- Short-lived: Complete within reasonable timeouts
- Focused: Do one thing well
"""

import asyncio
import hashlib
import logging
from datetime import datetime

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def validate_input(data: str) -> bool:
    """
    Validate input data before processing.

    This activity checks that the input meets basic requirements:
    - Not empty
    - Not too large
    - Contains safe content

    Args:
        data: Input data string to validate

    Returns:
        True if input is valid, False otherwise
    """
    activity.logger.info("Validating input data...")

    # Basic validation checks
    if not data or not isinstance(data, str):
        activity.logger.warning("Input is empty or not a string")
        return False

    if len(data) < 3:
        activity.logger.warning("Input too short")
        return False

    if len(data) > 10000:
        activity.logger.warning("Input too large (>10KB)")
        return False

    # Check for potentially problematic content
    dangerous_patterns = ["<script>", "javascript:", "eval("]
    for pattern in dangerous_patterns:
        if pattern.lower() in data.lower():
            activity.logger.warning(f"Dangerous pattern detected: {pattern}")
            return False

    activity.logger.info("Input validation passed")
    return True


@activity.defn
async def simulate_ai_call(prompt: str) -> str:
    """
    Simulate an AI API call (e.g., to OpenAI, local model, etc.).

    In a real implementation, this would:
    - Call an actual AI API (OpenAI, Anthropic, local LLM)
    - Handle API rate limits and errors
    - Process the response

    Args:
        prompt: The prompt or input for the AI

    Returns:
        Simulated AI response string

    Example:
        >>> response = await simulate_ai_call("Explain quantum computing")
        >>> print(response)
        "AI Response: quantum computing explanation..."
    """
    activity.logger.info(f"Simulating AI call with prompt: {prompt[:50]}...")

    # Simulate API call delay
    await asyncio.sleep(2)

    # Generate a deterministic response based on the input
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]

    response = (
        f"AI Response (id: {prompt_hash}): "
        f"Processed '{prompt[:30]}...' successfully. "
        f"This is a simulated response showing successful AI processing. "
        f"Timestamp: {datetime.now().isoformat()}"
    )

    activity.logger.info("AI call completed successfully")
    return response


@activity.defn
async def process_ai_task(task_data: dict) -> str:
    """
    Process an AI task with the given data.

    This activity represents the final processing step after AI inference.
    It could involve:
    - Storing results in a database
    - Generating reports
    - Triggering notifications
    - Updating user profiles

    Args:
        task_data: Dictionary containing:
            - input: Original user input
            - ai_response: Response from AI system
            - user_id: Optional user identifier

    Returns:
        Summary of the processing result
    """
    activity.logger.info("Processing AI task...")

    input_data = task_data.get("input", "")
    ai_response = task_data.get("ai_response", "")
    user_id = task_data.get("user_id", "anonymous")

    # Simulate processing work
    await asyncio.sleep(1)

    # Create a processing summary
    result_summary = {
        "user_id": user_id,
        "input_length": len(input_data),
        "response_length": len(ai_response),
        "processed_at": datetime.now().isoformat(),
        "status": "completed",
    }

    activity.logger.info(f"Task processing completed for user: {user_id}")

    # Return a formatted result
    return (
        f"Task processed successfully for user '{user_id}'. "
        f"Input: {len(input_data)} chars, "
        f"Response: {len(ai_response)} chars. "
        f"Processed at {result_summary['processed_at']}"
    )
