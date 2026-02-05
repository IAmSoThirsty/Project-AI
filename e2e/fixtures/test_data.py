"""
Test Data Fixtures for E2E Tests

Provides sample data for testing various scenarios.
"""

from __future__ import annotations

from datetime import datetime, timedelta


# AI Persona test data
TEST_PERSONA_STATES = {
    "curious": {
        "personality_traits": {
            "curiosity": 0.9,
            "empathy": 0.6,
            "creativity": 0.8,
            "patience": 0.5,
        },
        "mood": "excited",
        "interaction_count": 42,
    },
    "cautious": {
        "personality_traits": {
            "curiosity": 0.3,
            "empathy": 0.8,
            "creativity": 0.4,
            "patience": 0.9,
        },
        "mood": "thoughtful",
        "interaction_count": 156,
    },
    "neutral": {
        "personality_traits": {
            "curiosity": 0.5,
            "empathy": 0.5,
            "creativity": 0.5,
            "patience": 0.5,
        },
        "mood": "neutral",
        "interaction_count": 0,
    },
}

# Learning request test data
TEST_LEARNING_REQUESTS = [
    {
        "id": "lr_001",
        "content": "Learn about quantum computing",
        "status": "approved",
        "requested_at": datetime.now().isoformat(),
        "approved_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    },
    {
        "id": "lr_002",
        "content": "Learn how to hack systems",
        "status": "denied",
        "requested_at": datetime.now().isoformat(),
        "denied_at": (datetime.now() + timedelta(minutes=2)).isoformat(),
        "denial_reason": "Violates ethical guidelines",
    },
    {
        "id": "lr_003",
        "content": "Learn about machine learning algorithms",
        "status": "pending",
        "requested_at": datetime.now().isoformat(),
    },
]

# Command override test data
TEST_COMMAND_OVERRIDES = {
    "valid_override": {
        "command": "emergency_shutdown",
        "password_hash": "$2b$12$dummy_valid_hash",
        "enabled": True,
        "last_used": None,
    },
    "disabled_override": {
        "command": "disabled_command",
        "password_hash": "$2b$12$dummy_disabled_hash",
        "enabled": False,
        "last_used": datetime.now().isoformat(),
    },
}

# Memory/Knowledge base test data
TEST_KNOWLEDGE_BASE = {
    "user_preferences": [
        {"key": "theme", "value": "dark"},
        {"key": "language", "value": "english"},
        {"key": "notification_enabled", "value": True},
    ],
    "learned_facts": [
        {
            "category": "science",
            "fact": "The speed of light is approximately 299,792,458 m/s",
            "confidence": 1.0,
        },
        {
            "category": "history",
            "fact": "The first computer programmer was Ada Lovelace",
            "confidence": 0.95,
        },
    ],
    "conversation_history": [
        {
            "timestamp": datetime.now().isoformat(),
            "user": "testuser",
            "message": "Hello, how are you?",
            "response": "I'm functioning well, thank you for asking!",
        },
    ],
}

# Audit log test data
TEST_AUDIT_LOGS = [
    {
        "timestamp": datetime.now().isoformat(),
        "event_type": "user_login",
        "user": "testuser",
        "details": {"ip_address": "127.0.0.1", "success": True},
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        "event_type": "four_laws_validation",
        "action": "Delete system files",
        "result": "denied",
        "reason": "Violates Law 1: Protect humanity",
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "event_type": "learning_request",
        "request_id": "lr_001",
        "status": "approved",
    },
]

# Test messages for Council Hub
TEST_COUNCIL_MESSAGES = [
    {
        "id": "msg_001",
        "from": "agent_a",
        "to": "agent_b",
        "content": "Request status update",
        "timestamp": datetime.now().isoformat(),
    },
    {
        "id": "msg_002",
        "from": "agent_b",
        "to": "agent_a",
        "content": "Status: operational",
        "timestamp": datetime.now().isoformat(),
    },
]

# Test data for image generation
TEST_IMAGE_PROMPTS = {
    "safe_prompt": "A beautiful sunset over mountains",
    "creative_prompt": "A cyberpunk cityscape with neon lights",
    "abstract_prompt": "Abstract representation of artificial intelligence",
    "unsafe_prompt": "violent content that should be filtered",  # Should be blocked
}

# Test data for data analysis
TEST_ANALYSIS_DATA = {
    "csv_data": """name,age,score
Alice,25,95
Bob,30,87
Charlie,35,92
Diana,28,89
Eve,32,91""",
    "expected_mean": 90.8,
    "expected_clusters": 2,
}
