import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: fork-registry-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Fork Registry Service",
    version="1.0.0",
    description="Tracks sovereign lineage. When a fork establishes its own root identity it registers here — not to claim authority over it, but to maintain the historical record. Lineage is historical not hierarchical. This service holds that truth.",
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
            "fork_registry_service=app.main:main",
        ],
    },
)
