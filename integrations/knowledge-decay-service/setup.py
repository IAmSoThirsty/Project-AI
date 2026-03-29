import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: knowledge-decay-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Knowledge Decay Service",
    version="1.0.0",
    description="Information goes stale. This service tracks the age and volatility of cached knowledge. Medical guidelines change. Laws change. Science updates. Knows when to re-verify.",
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
            "knowledge_decay_service=app.main:main",
        ],
    },
)
