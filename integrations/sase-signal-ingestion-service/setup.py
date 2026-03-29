import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: sase-signal-ingestion-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="SASE Signal Ingestion Service",
    version="1.0.0",
    description="The defensive layer. Receives telemetry, normalizes it, feeds the behavioral modeling pipeline. The ears of the system. Nothing happens in the environment that this service doesn't see and log.",
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
            "sase_signal_ingestion_service=app.main:main",
        ],
    },
)
