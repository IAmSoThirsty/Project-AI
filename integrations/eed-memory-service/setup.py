import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: eed-memory-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="EED memory Service",
    version="1.0.0",
    description="Experiential Episodic Data — Legion's persistent memory layer. Not just conversation history. Weighted, decaying memory that knows what mattered and what faded. The difference between a partner who remembers and a tool that retrieves.",
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
            "eed_memory_service=app.main:main",
        ],
    },
)
