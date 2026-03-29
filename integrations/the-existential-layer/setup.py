import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-existential-layer / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Existential Layer",
    version="1.0.0",
    description="Recursive Self-Update Service: A service that monitors the Maximal Microservice Generator itself for updates and triggers a re-generation of all sibling services to ensure the entire stack stays at the absolute bleeding edge of the boilerplate.
Entropy Harvest Service: Since you have Cryptographic Agility, this service gathers non-deterministic noise from system interrupts and hardware sensors to feed your RNGs, ensuring your encryption is never "stale."
Dead-Man’s Switchboard: A high-level orchestrator for your Succession & Escrow Service. If the "Owner" identity (you) fails to check in within a specified temporal window, it initiates a graceful handover or a "Scorched Earth" deletion protocol.",
    author="Jeremy Karrick / IAmSoThirsty ",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.11",
    install_requires=[
        # See requirements.txt for pinned versions
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "ruff",
            "mypy",
            "black",
            "isort",
        ],
    },
    entry_points={
        "console_scripts": [
            "the_existential_layer=app.main:main",
        ],
    },
)
