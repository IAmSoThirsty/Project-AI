#!/usr/bin/env python3
"""
Temporal.io Setup Script for Project-AI.

This script helps set up and start Temporal.io services for Project-AI.
It can run Temporal locally via Docker or connect to Temporal Cloud.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_docker():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            logger.error("Docker is not running. Please start Docker first.")
            return False
        return True
    except FileNotFoundError:
        logger.error("Docker is not installed. Please install Docker first.")
        return False


def check_docker_compose():
    """Check if Docker Compose is installed."""
    try:
        subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.error("Docker Compose is not installed.")
        return False


def start_temporal_local():
    """Start Temporal server locally using Docker Compose."""
    logger.info("Starting Temporal server locally...")

    if not check_docker() or not check_docker_compose():
        return False

    try:
        # Start Temporal services
        subprocess.run(
            [
                "docker-compose",
                "up",
                "-d",
                "temporal",
                "temporal-postgresql",
            ],
            check=True,
        )
        logger.info("Temporal server started successfully!")
        logger.info("Web UI available at: http://localhost:8233")
        logger.info("gRPC endpoint: localhost:7233")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Temporal server: {e}")
        return False


def start_worker():
    """Start Temporal worker."""
    logger.info("Starting Temporal worker...")

    try:
        # Start worker via Docker Compose
        subprocess.run(
            ["docker-compose", "up", "-d", "temporal-worker"],
            check=True,
        )
        logger.info("Temporal worker started successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start worker: {e}")
        return False


def stop_temporal():
    """Stop Temporal services."""
    logger.info("Stopping Temporal services...")

    try:
        subprocess.run(
            [
                "docker-compose",
                "stop",
                "temporal",
                "temporal-postgresql",
                "temporal-worker",
            ],
            check=True,
        )
        logger.info("Temporal services stopped successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop Temporal services: {e}")
        return False


def show_status():
    """Show status of Temporal services."""
    logger.info("Checking Temporal services status...")

    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("\nTemporal Services Status:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get status: {e}")
        return False


def create_env_file():
    """Create .env.temporal file if it doesn't exist."""
    env_file = Path(".env.temporal")
    env_example = Path(".env.temporal.example")

    if env_file.exists():
        logger.info(".env.temporal file already exists")
        return True

    if env_example.exists():
        logger.info("Creating .env.temporal from example file...")
        env_example.read_text()
        env_file.write_text(env_example.read_text())
        logger.info("Created .env.temporal - please review and update as needed")
        return True

    logger.warning("No .env.temporal.example found")
    return False


def setup_workspace_reference():
    """Create workspace reference file."""
    workspace_file = Path("config/temporal/workspace_info.txt")
    workspace_file.parent.mkdir(parents=True, exist_ok=True)

    workspace_content = """
Temporal.io Workspace Information for Project-AI
================================================

Original Development Workspace: Expert space waddle

This integration was initially developed in the "Expert space waddle" workspace
and has been synced to this GitHub repository.

All Temporal workflows, activities, and configurations have been migrated
from the workspace to ensure full reproducibility and team collaboration.

Setup Instructions:
- See docs/TEMPORAL_SETUP.md for detailed setup guide
- Use scripts/setup_temporal.py to start local Temporal server
- Review config/temporal/ for configuration files
""".strip()

    workspace_file.write_text(workspace_content)
    logger.info(f"Created workspace reference: {workspace_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Setup and manage Temporal.io for Project-AI"
    )
    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "worker", "init"],
        help="Command to execute",
    )

    args = parser.parse_args()

    if args.command == "init":
        logger.info("Initializing Temporal configuration...")
        create_env_file()
        setup_workspace_reference()
        logger.info("Initialization complete!")
        return 0

    elif args.command == "start":
        if not start_temporal_local():
            return 1
        return 0

    elif args.command == "worker":
        if not start_worker():
            return 1
        return 0

    elif args.command == "stop":
        if not stop_temporal():
            return 1
        return 0

    elif args.command == "status":
        if not show_status():
            return 1
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
