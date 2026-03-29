import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-heuristic-sentinel / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Heuristic Sentinel",
    version="1.0.0",
    description="Function: If the Sciences Oracle and the Constitutional Audit disagree on a data point, the Sentinel puts the entire stack into "Read-Only" mode until the Confidence Calibration Service hits a >98% threshold.",
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
            "the_heuristic_sentinel=app.main:main",
        ],
    },
)
