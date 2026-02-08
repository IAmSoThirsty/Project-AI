"""
Setup and Teardown Utilities for E2E Tests

Handles test environment initialization, cleanup, and state management.
"""

from __future__ import annotations

import json
import logging
import shutil
import tempfile
from pathlib import Path

from e2e.config.e2e_config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class E2ETestEnvironment:
    """Manages E2E test environment setup and teardown."""

    def __init__(self):
        """Initialize test environment manager."""
        self.temp_dir: Path | None = None
        self.backup_data_dir: Path | None = None
        self.original_data_dir = PROJECT_ROOT / "data"

    def setup(self) -> None:
        """Set up the test environment."""
        logger.info("Setting up E2E test environment")

        # Create temporary directory for test data
        self.temp_dir = Path(tempfile.mkdtemp(prefix="e2e_test_"))
        logger.info("Created temporary directory: %s", self.temp_dir)

        # Backup existing data directory if it exists
        if self.original_data_dir.exists():
            self.backup_data_dir = Path(tempfile.mkdtemp(prefix="e2e_backup_"))
            shutil.copytree(self.original_data_dir, self.backup_data_dir / "data")
            logger.info("Backed up data directory to: %s", self.backup_data_dir)

        # Create test data directories
        self._create_test_data_dirs()

        # Initialize test data
        self._initialize_test_data()

        logger.info("E2E test environment setup complete")

    def teardown(self) -> None:
        """Tear down the test environment."""
        logger.info("Tearing down E2E test environment")

        # Remove temporary directory
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info("Removed temporary directory: %s", self.temp_dir)

        # Restore backed up data directory
        if self.backup_data_dir and self.backup_data_dir.exists():
            if self.original_data_dir.exists():
                shutil.rmtree(self.original_data_dir)
            shutil.copytree(self.backup_data_dir / "data", self.original_data_dir)
            shutil.rmtree(self.backup_data_dir)
            logger.info("Restored backed up data directory")

        logger.info("E2E test environment teardown complete")

    def _create_test_data_dirs(self) -> None:
        """Create necessary test data directories."""
        test_data_dirs = [
            self.temp_dir / "data" / "ai_persona",
            self.temp_dir / "data" / "memory",
            self.temp_dir / "data" / "learning_requests",
            self.temp_dir / "data" / "command_override",
            self.temp_dir / "data" / "audit_logs",
            self.temp_dir / "data" / "plugins",
        ]

        for directory in test_data_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug("Created test data directory: %s", directory)

    def _initialize_test_data(self) -> None:
        """Initialize test data files."""
        # Create test users.json
        users_file = self.temp_dir / "users.json"
        test_users = {
            "admin": {
                "username": "admin",
                "password_hash": "$2b$12$dummy_hash_for_testing",
                "role": "admin",
            },
            "testuser": {
                "username": "testuser",
                "password_hash": "$2b$12$dummy_hash_for_testing",
                "role": "user",
            },
        }
        with open(users_file, "w") as f:
            json.dump(test_users, f, indent=2)
        logger.debug("Created test users file: %s", users_file)

        # Create test AI persona state
        persona_state_file = self.temp_dir / "data" / "ai_persona" / "state.json"
        test_persona_state = {
            "personality_traits": {
                "curiosity": 0.8,
                "empathy": 0.7,
                "creativity": 0.9,
            },
            "mood": "neutral",
            "interaction_count": 0,
        }
        with open(persona_state_file, "w") as f:
            json.dump(test_persona_state, f, indent=2)
        logger.debug("Created test persona state: %s", persona_state_file)

        # Create test memory knowledge base
        knowledge_file = self.temp_dir / "data" / "memory" / "knowledge.json"
        test_knowledge = {
            "user_preferences": [],
            "learned_facts": [],
            "conversation_history": [],
        }
        with open(knowledge_file, "w") as f:
            json.dump(test_knowledge, f, indent=2)
        logger.debug("Created test knowledge base: %s", knowledge_file)

    def get_temp_dir(self) -> Path:
        """Get the temporary directory path."""
        if not self.temp_dir:
            raise RuntimeError("Test environment not set up")
        return self.temp_dir

    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.teardown()


def setup_e2e_environment() -> E2ETestEnvironment:
    """Set up and return an E2E test environment."""
    env = E2ETestEnvironment()
    env.setup()
    return env


def teardown_e2e_environment(env: E2ETestEnvironment) -> None:
    """Tear down an E2E test environment."""
    env.teardown()
