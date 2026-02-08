#!/usr/bin/env python3
"""
Legion Configuration
Agent settings, subsystem toggles, and security parameters
"""

LEGION_CONFIG = {
    "agent": {
        "name": "Legion",
        "version": "1.0.0-phase1",
        "description": "God-Tier Monolithic AI - We Are Many",
        "tagline": "For we are many, and we are one",
        "mode": "governance_first",  # All actions through Triumvirate
    },
    "api": {
        "project_ai_url": "http://localhost:8001",
        "timeout": 30,
        "retry_attempts": 3,
    },
    "security": {
        "cerberus_enabled": True,
        "hydra_spawning": True,
        "max_spawn_depth": 5,
        "safety_guard_model": "llama-guard-3-8b",
        "tarl_enforcement": "strict",
        "prompt_injection_detection": True,
        "rate_limit_per_minute": 60,
    },
    "memory": {
        "eed_enabled": True,
        "context_window": 200000,
        "episodic_retention": "permanent",
        "cross_conversation": True,
        "max_history_per_user": 1000,
    },
    "subsystems": {
        "triumvirate": True,  # Galahad + Cerberus + CodexDeus
        "tarl_runtime": True,  # Policy enforcement
        "cognition_kernel": True,  # Multi-agent orchestration
        "global_scenario_engine": True,
        "defense_engine": True,
        "cerberus_hydra": True,  # Exponential security
        "eed_memory": True,  # Extended episodic database
    },
    "capabilities": {
        # Security Operations (Cerberus)
        "threat_monitoring": True,
        "hydra_agent_spawning": True,
        "system_lockdown": True,
        "audit_queries": True,
        # Scenario Forecasting
        "crisis_analysis": True,
        "monte_carlo_simulation": True,
        "world_data_ingestion": True,
        # Memory Management (EED)
        "episodic_recall": True,
        "context_expansion": True,
        "memory_snapshots": True,
        # Agent Orchestration
        "multi_agent_spawning": True,
        "long_context_processing": True,
        "safety_moderation": True,
        # Ethics & Alignment (Galahad)
        "policy_evaluation": True,
        "fairness_assessment": True,
        "compliance_checking": True,
    },
    "logging": {
        "level": "INFO",
        "audit_trail": True,
        "conversation_logging": True,
        "security_events": True,
    },
    "openclaw": {
        "platforms": ["whatsapp", "discord", "telegram", "cli"],
        "auto_reconnect": True,
        "message_queue_size": 100,
    },
}


# Environment-specific overrides
def get_config(environment: str = "development"):
    """Get configuration for specific environment"""
    config = LEGION_CONFIG.copy()

    if environment == "production":
        config["security"]["rate_limit_per_minute"] = 120
        config["logging"]["level"] = "WARNING"
    elif environment == "testing":
        config["security"]["cerberus_enabled"] = False
        config["subsystems"]["defense_engine"] = False
        config["openclaw"]["platforms"] = ["cli"]

    return config


if __name__ == "__main__":
    import json

    print(json.dumps(LEGION_CONFIG, indent=2))
