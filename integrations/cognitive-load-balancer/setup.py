import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: cognitive-load-balancer / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Cognitive Load Balancer",
    version="1.0.0",
    description="Not for the servers, but for the humans. It shuts down non-essential notifications or dashboards based on the operator's current interaction frequency.",
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
            "cognitive_load_balancer=app.main:main",
        ],
    },
)
