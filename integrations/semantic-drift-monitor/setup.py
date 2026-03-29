import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: semantic-drift-monitor / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Semantic Drift Monitor",
    version="1.0.0",
    description="Watches for gradual manipulation over long conversations. Single messages look innocent. Patterns across Two Hundred and fifty messages reveal intent. This service sees the arc.",
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
            "semantic_drift_monitor=app.main:main",
        ],
    },
)
