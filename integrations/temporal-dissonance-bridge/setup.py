import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: temporal-dissonance-bridge / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Temporal Dissonance Bridge",
    version="1.0.0",
    description="Injects honest temporal context into every conversation. Knows how much time passed. Knows what weight that duration carries. Asks what the gap contained rather than pretending it was nothing.",
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
            "temporal_dissonance_bridge=app.main:main",
        ],
    },
)
