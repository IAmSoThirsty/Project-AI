import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: cerberus-containment-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Cerberus Containment Service",
    version="1.0.0",
    description="Separate from Triumvirate's rule evaluation — this is the enforcement layer. When Cerberus says deny, this service actually executes the containment. Rate limiting, circuit breaking, quarantine, isolation. The difference between a governance decision and a governance action.",
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
            "cerberus_containment_service=app.main:main",
        ],
    },
)
