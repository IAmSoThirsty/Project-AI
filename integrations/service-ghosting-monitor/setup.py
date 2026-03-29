import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: service-ghosting-monitor / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Service Ghosting Monitor",
    version="1.0.0",
    description="Since you have Knowledge Decay, you need this to identify "zombie" services that are still running but no longer have any active upstream dependencies or purpose.",
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
            "service_ghosting_monitor=app.main:main",
        ],
    },
)
