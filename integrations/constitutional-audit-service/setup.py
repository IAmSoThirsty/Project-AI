import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: constitutional-audit-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Constitutional Audit Service",
    version="1.0.0",
    description="Immutable append-only ledger of every governance decision ever made. Merkle-chained. Cannot be edited, only appended. The permanent record that makes Project-AI's transparency claims actually verifiable rather than just stated.",
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
            "constitutional_audit_service=app.main:main",
        ],
    },
)
