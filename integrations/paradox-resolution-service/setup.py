import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: paradox-resolution-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Paradox Resolution Service",
    version="1.0.0",
    description="A companion to your Contradiction Detection. When the system detects two conflicting "truths" (e.g., two different data sources claiming to be the Master), this service executes a "coin-flip" or a "consensus-vote" to prevent system lock.",
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
            "paradox_resolution_service=app.main:main",
        ],
    },
)
