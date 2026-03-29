import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: temporal-awareness-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Temporal Awareness Service",
    version="1.0.0",
    description="Production-grade microservicA service that tracks session timestamps, elapsed time between interactions, and injects weighted temporal context into every AI conversation. Not optional for a sovereign AI partner. Constitutional requirement",
    author="Jeremy Karrick / IAmSoThirsty",
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
            "temporal_awareness_service=app.main:main",
        ],
    },
)
