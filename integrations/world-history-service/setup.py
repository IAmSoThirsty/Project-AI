import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: world-history-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="World History Service",
    version="1.0.0",
    description="Not Western-centric. Full geographic and cultural coverage. Timeline engine. Causal chain mapping — what led to what and why. Cross-cultural event correlation. Legion should know that things happened everywhere, not just in textbooks.",
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
            "world_history_service=app.main:main",
        ],
    },
)
