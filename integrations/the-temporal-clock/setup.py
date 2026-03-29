import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-temporal-clock / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Temporal Clock",
    version="1.0.0",
    description="The Logic: This layer ensures that the World History Service and the Constitutional Amendment Service are looking at the same "version" of reality.
The Status: It prevents "causal leakage"—making sure a hypothetical medical scenario doesn't accidentally trigger a real-world legal audit in your other services.",
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
            "the_temporal_clock=app.main:main",
        ],
    },
)
