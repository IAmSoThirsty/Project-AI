import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-epoch-synchronizer / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Epoch Synchronizer",
    version="1.0.0",
    description="Function: It treats "Time" as a versioned database. If you change a parameter in the past (simulation-wise), it re-calculates the downstream effects on your Medical and Legal modules.",
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
            "the_epoch_synchronizer=app.main:main",
        ],
    },
)
