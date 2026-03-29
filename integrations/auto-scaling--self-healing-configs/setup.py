import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: auto-scaling--self-healing-configs / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Auto-scaling & self-healing configs",
    version="1.0.0",
    description="generate Kubernetes manifests with auto-scaling and self-healing configurations out-of-the-box",
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
            "auto_scaling_&_self_healing_configs=app.main:main",
        ],
    },
)
