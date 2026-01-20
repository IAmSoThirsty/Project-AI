"""
Temporal Activity Definitions for Project-AI.

Activities are individual units of work that can be executed by workers.
They represent the actual business logic invoked by workflows.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

from temporalio import activity

logger = logging.getLogger(__name__)


# Learning Activities

@activity.defn
async def validate_learning_content(request: dict) -> bool:
    """
    Validate that learning content is appropriate and well-formed.

    Args:
        request: Learning request dictionary

    Returns:
        True if content is valid, False otherwise
    """
    activity.logger.info(f"Validating learning content for category: {request.get('category')}")

    content = request.get("content", "")

    # Basic validation
    if not content or len(content) < 10:
        activity.logger.warning("Content too short")
        return False

    if len(content) > 100000:  # 100KB limit
        activity.logger.warning("Content too large")
        return False

    # Check for valid category
    valid_categories = ["security", "programming", "data_science", "general", "tips", "facts"]
    if request.get("category") not in valid_categories:
        activity.logger.warning(f"Invalid category: {request.get('category')}")
        return False

    activity.logger.info("Content validation passed")
    return True


@activity.defn
async def check_black_vault(content: str) -> bool:
    """
    Check if content is in the Black Vault (forbidden content).

    Args:
        content: Content to check

    Returns:
        True if content is allowed, False if blocked
    """
    activity.logger.info("Checking Black Vault for content")

    # Hash the content
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    # Check against Black Vault (load from file in production)
    black_vault_path = Path("data/learning_requests/black_vault.json")
    if black_vault_path.exists():
        try:
            with open(black_vault_path) as f:
                black_vault = json.load(f)
                if content_hash in black_vault.get("hashes", []):
                    activity.logger.warning("Content blocked by Black Vault")
                    return False
        except Exception as e:
            activity.logger.error(f"Error reading Black Vault: {e}")

    activity.logger.info("Content allowed by Black Vault")
    return True


@activity.defn
async def process_learning_request(request: dict) -> str:
    """
    Process a learning request and extract knowledge.

    Args:
        request: Learning request dictionary

    Returns:
        Generated knowledge ID
    """
    activity.logger.info(f"Processing learning request: {request.get('source')}")

    # Generate unique knowledge ID
    timestamp = datetime.now().isoformat()
    knowledge_id = hashlib.sha256(
        f"{request.get('content')}{timestamp}".encode()
    ).hexdigest()[:16]

    activity.logger.info(f"Generated knowledge ID: {knowledge_id}")
    return knowledge_id


@activity.defn
async def store_knowledge(data: dict) -> bool:
    """
    Store knowledge in the knowledge base.

    Args:
        data: Dictionary with knowledge_id and request data

    Returns:
        True if stored successfully
    """
    knowledge_id = data.get("knowledge_id")
    request = data.get("request", {})

    activity.logger.info(f"Storing knowledge: {knowledge_id}")

    # Ensure data directory exists
    knowledge_path = Path("data/memory/knowledge.json")
    knowledge_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing knowledge
    knowledge_base = {}
    if knowledge_path.exists():
        try:
            with open(knowledge_path) as f:
                knowledge_base = json.load(f)
        except Exception as e:
            activity.logger.error(f"Error loading knowledge base: {e}")
            knowledge_base = {}

    # Add new knowledge
    category = request.get("category", "general")
    if category not in knowledge_base:
        knowledge_base[category] = []

    knowledge_base[category].append({
        "id": knowledge_id,
        "content": request.get("content"),
        "source": request.get("source"),
        "timestamp": datetime.now().isoformat(),
        "user_id": request.get("user_id"),
    })

    # Save updated knowledge base
    try:
        with open(knowledge_path, "w") as f:
            json.dump(knowledge_base, f, indent=2)
        activity.logger.info(f"Knowledge stored successfully: {knowledge_id}")
        return True
    except Exception as e:
        activity.logger.error(f"Error storing knowledge: {e}")
        return False


# Image Generation Activities

@activity.defn
async def check_content_safety(prompt: str) -> bool:
    """
    Check if image prompt is safe and appropriate.

    Args:
        prompt: Image generation prompt

    Returns:
        True if safe, False otherwise
    """
    activity.logger.info("Checking content safety for image prompt")

    # Blocked keywords (simplified version)
    blocked_keywords = [
        "explicit", "nude", "nsfw", "violent", "gore",
        "weapon", "drug", "hate", "offensive"
    ]

    prompt_lower = prompt.lower()
    for keyword in blocked_keywords:
        if keyword in prompt_lower:
            activity.logger.warning(f"Blocked keyword detected: {keyword}")
            return False

    activity.logger.info("Content safety check passed")
    return True


@activity.defn
async def generate_image(request: dict) -> dict:
    """
    Generate image using configured backend.

    Args:
        request: Image generation request

    Returns:
        Dictionary with image_path and metadata
    """
    activity.logger.info(f"Generating image with {request.get('backend')} backend")

    # In production, this would call the actual ImageGenerator
    # For now, return a placeholder result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"generated_{timestamp}.png"
    image_path = Path("data/images") / image_filename

    # Ensure directory exists
    image_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "image_path": str(image_path),
        "metadata": {
            "prompt": request.get("prompt"),
            "style": request.get("style"),
            "size": request.get("size"),
            "backend": request.get("backend"),
            "timestamp": datetime.now().isoformat(),
        }
    }

    activity.logger.info(f"Image generation completed: {image_path}")
    return result


@activity.defn
async def store_image_metadata(result: dict) -> bool:
    """
    Store image generation metadata.

    Args:
        result: Image generation result with metadata

    Returns:
        True if stored successfully
    """
    activity.logger.info("Storing image metadata")

    metadata_path = Path("data/images/metadata.json")
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing metadata
    all_metadata = []
    if metadata_path.exists():
        try:
            with open(metadata_path) as f:
                all_metadata = json.load(f)
        except Exception as e:
            activity.logger.error(f"Error loading metadata: {e}")

    # Add new metadata
    all_metadata.append(result.get("metadata", {}))

    # Save updated metadata
    try:
        with open(metadata_path, "w") as f:
            json.dump(all_metadata, f, indent=2)
        activity.logger.info("Metadata stored successfully")
        return True
    except Exception as e:
        activity.logger.error(f"Error storing metadata: {e}")
        return False


# Data Analysis Activities

@activity.defn
async def validate_data_file(file_path: str) -> bool:
    """
    Validate that data file exists and is readable.

    Args:
        file_path: Path to data file

    Returns:
        True if valid, False otherwise
    """
    activity.logger.info(f"Validating data file: {file_path}")

    path = Path(file_path)

    if not path.exists():
        activity.logger.warning(f"File does not exist: {file_path}")
        return False

    if not path.is_file():
        activity.logger.warning(f"Path is not a file: {file_path}")
        return False

    # Check file extension
    valid_extensions = [".csv", ".xlsx", ".json", ".txt"]
    if path.suffix not in valid_extensions:
        activity.logger.warning(f"Invalid file extension: {path.suffix}")
        return False

    activity.logger.info("Data file validation passed")
    return True


@activity.defn
async def load_data(file_path: str) -> dict:
    """
    Load data from file.

    Args:
        file_path: Path to data file

    Returns:
        Dictionary with loaded data
    """
    activity.logger.info(f"Loading data from: {file_path}")

    # In production, this would use pandas or other data loading libraries
    # For now, return placeholder
    return {
        "file_path": file_path,
        "loaded_at": datetime.now().isoformat(),
        "rows": 0,
        "columns": 0,
    }


@activity.defn
async def perform_analysis(data: dict) -> dict:
    """
    Perform data analysis.

    Args:
        data: Data dictionary with analysis type

    Returns:
        Analysis results
    """
    analysis_type = data.get("type", "statistics")
    activity.logger.info(f"Performing {analysis_type} analysis")

    # Placeholder results
    results = {
        "analysis_type": analysis_type,
        "completed_at": datetime.now().isoformat(),
        "summary": f"{analysis_type} analysis completed",
    }

    activity.logger.info("Analysis completed")
    return results


@activity.defn
async def generate_visualizations(results: dict) -> str:
    """
    Generate visualizations from analysis results.

    Args:
        results: Analysis results

    Returns:
        Path to output directory
    """
    activity.logger.info("Generating visualizations")

    output_dir = Path("data/analysis") / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    activity.logger.info(f"Visualizations saved to: {output_dir}")
    return str(output_dir)


# Memory Expansion Activities

@activity.defn
async def extract_memory_information(messages: list) -> list:
    """
    Extract key information from conversation messages.

    Args:
        messages: List of message dictionaries

    Returns:
        List of extracted information items
    """
    activity.logger.info(f"Extracting information from {len(messages)} messages")

    # Placeholder extraction
    extracted = []
    for i, msg in enumerate(messages):
        if len(msg.get("content", "")) > 20:  # Only meaningful messages
            extracted.append({
                "index": i,
                "content": msg.get("content"),
                "timestamp": msg.get("timestamp", datetime.now().isoformat()),
            })

    activity.logger.info(f"Extracted {len(extracted)} items")
    return extracted


@activity.defn
async def store_memories(data: dict) -> int:
    """
    Store memories in the memory system.

    Args:
        data: Dictionary with conversation_id, info, and user_id

    Returns:
        Number of memories stored
    """
    conversation_id = data.get("conversation_id")
    info = data.get("info", [])

    activity.logger.info(f"Storing {len(info)} memories for conversation: {conversation_id}")

    memory_path = Path("data/memory/conversations.json")
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing memories
    all_memories = {}
    if memory_path.exists():
        try:
            with open(memory_path) as f:
                all_memories = json.load(f)
        except Exception as e:
            activity.logger.error(f"Error loading memories: {e}")

    # Add new memories
    if conversation_id not in all_memories:
        all_memories[conversation_id] = []

    all_memories[conversation_id].extend(info)

    # Save updated memories
    try:
        with open(memory_path, "w") as f:
            json.dump(all_memories, f, indent=2)
        activity.logger.info(f"Stored {len(info)} memories")
        return len(info)
    except Exception as e:
        activity.logger.error(f"Error storing memories: {e}")
        return 0


@activity.defn
async def update_memory_indexes(conversation_id: str) -> bool:
    """
    Update memory indexes for fast retrieval.

    Args:
        conversation_id: ID of the conversation

    Returns:
        True if successful
    """
    activity.logger.info(f"Updating memory indexes for: {conversation_id}")

    # Placeholder for index update logic
    # In production, this would update search indexes, embeddings, etc.

    activity.logger.info("Memory indexes updated")
    return True


# Crisis Response Activities

@activity.defn
async def validate_crisis_request(request: dict) -> bool:
    """
    Validate crisis request parameters.

    Args:
        request: Crisis request dictionary with target and missions

    Returns:
        True if request is valid, False otherwise
    """
    activity.logger.info(f"Validating crisis request for target: {request.get('target_member')}")

    # Validate target member
    target = request.get("target_member")
    if not target or len(target) < 3:
        activity.logger.warning("Invalid target member")
        return False

    # Validate missions list
    missions = request.get("missions", [])
    if not missions or len(missions) == 0:
        activity.logger.warning("No missions provided")
        return False

    # Validate each mission has required fields
    for mission in missions:
        if not all(key in mission for key in ["phase_id", "agent_id", "action", "target"]):
            activity.logger.warning(f"Invalid mission structure: {mission}")
            return False

    activity.logger.info(f"Crisis request validated: {len(missions)} mission phases")
    return True


@activity.defn
async def initialize_crisis_response(data: dict) -> bool:
    """
    Initialize crisis response tracking.

    Args:
        data: Dictionary with crisis_id and target

    Returns:
        True if initialized successfully
    """
    crisis_id = data.get("crisis_id")
    target = data.get("target")

    activity.logger.info(f"Initializing crisis response: {crisis_id} for target: {target}")

    # Ensure data directory exists
    crisis_path = Path("data/crises")
    crisis_path.mkdir(parents=True, exist_ok=True)

    # Create crisis record
    crisis_file = crisis_path / f"{crisis_id}.json"
    crisis_data = {
        "crisis_id": crisis_id,
        "target": target,
        "status": "initiated",
        "started_at": datetime.now().isoformat(),
        "phases": [],
    }

    try:
        with open(crisis_file, "w") as f:
            json.dump(crisis_data, f, indent=2)
        activity.logger.info(f"Crisis response initialized: {crisis_id}")
        return True
    except Exception as e:
        activity.logger.error(f"Error initializing crisis: {e}")
        return False


@activity.defn
async def perform_agent_mission(mission: dict) -> bool:
    """
    Execute agent mission deployment.

    This activity represents the core agent deployment action.
    In production, this would interface with actual agent systems.

    Args:
        mission: Mission phase dictionary with agent_id, action, target, etc.

    Returns:
        True if mission completed successfully
    """
    phase_id = mission.get("phase_id")
    agent_id = mission.get("agent_id")
    action = mission.get("action")
    target = mission.get("target")

    activity.logger.info(
        f"AGENT DEPLOYMENT - Phase: {phase_id} | "
        f"Agent: {agent_id} | Action: {action} | Target: {target}"
    )

    # Simulate agent mission execution
    # In production, this would:
    # - Deploy agent to execution environment
    # - Execute mission-specific actions
    # - Monitor agent progress
    # - Handle agent-specific errors

    activity.logger.info(
        f"Agent {agent_id} deployed successfully for mission phase {phase_id}"
    )

    return True


@activity.defn
async def log_mission_phase(data: dict) -> bool:
    """
    Log mission phase completion or failure.

    Args:
        data: Dictionary with crisis_id, phase_id, status, and optional error

    Returns:
        True if logged successfully
    """
    crisis_id = data.get("crisis_id")
    phase_id = data.get("phase_id")
    status = data.get("status")
    error = data.get("error")

    activity.logger.info(
        f"Logging mission phase: {phase_id} - Status: {status}"
    )

    # Load crisis record
    crisis_file = Path("data/crises") / f"{crisis_id}.json"
    if not crisis_file.exists():
        activity.logger.warning(f"Crisis file not found: {crisis_id}")
        return False

    try:
        with open(crisis_file) as f:
            crisis_data = json.load(f)

        # Add phase log entry
        phase_log = {
            "phase_id": phase_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        if error:
            phase_log["error"] = error

        crisis_data["phases"].append(phase_log)

        # Save updated record
        with open(crisis_file, "w") as f:
            json.dump(crisis_data, f, indent=2)

        activity.logger.info(f"Mission phase logged: {phase_id}")
        return True
    except Exception as e:
        activity.logger.error(f"Error logging phase: {e}")
        return False


@activity.defn
async def finalize_crisis_response(data: dict) -> bool:
    """
    Finalize crisis response and update status.

    Args:
        data: Dictionary with crisis_id, completed count, and failed count

    Returns:
        True if finalized successfully
    """
    crisis_id = data.get("crisis_id")
    completed = data.get("completed", 0)
    failed = data.get("failed", 0)

    activity.logger.info(
        f"Finalizing crisis response: {crisis_id} "
        f"(Completed: {completed}, Failed: {failed})"
    )

    crisis_file = Path("data/crises") / f"{crisis_id}.json"
    if not crisis_file.exists():
        activity.logger.warning(f"Crisis file not found: {crisis_id}")
        return False

    try:
        with open(crisis_file) as f:
            crisis_data = json.load(f)

        # Update crisis status
        crisis_data["status"] = "completed" if failed == 0 else "partial_failure"
        crisis_data["completed_at"] = datetime.now().isoformat()
        crisis_data["summary"] = {
            "completed_phases": completed,
            "failed_phases": failed,
            "total_phases": completed + failed,
        }

        # Save final record
        with open(crisis_file, "w") as f:
            json.dump(crisis_data, f, indent=2)

        activity.logger.info(f"Crisis response finalized: {crisis_id}")
        return True
    except Exception as e:
        activity.logger.error(f"Error finalizing crisis: {e}")
        return False


# Export all activities
learning_activities = [
    validate_learning_content,
    check_black_vault,
    process_learning_request,
    store_knowledge,
]

image_activities = [
    check_content_safety,
    generate_image,
    store_image_metadata,
]

data_activities = [
    validate_data_file,
    load_data,
    perform_analysis,
    generate_visualizations,
]

memory_activities = [
    extract_memory_information,
    store_memories,
    update_memory_indexes,
]

crisis_activities = [
    validate_crisis_request,
    initialize_crisis_response,
    perform_agent_mission,
    log_mission_phase,
    finalize_crisis_response,
]
