import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: ai-program-enforcer / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="AI Program Enforcer",
    version="1.0.0",
    description="Prevents Code from source host from being implemented on the receiving end. Allowing a user full unrestricted access to the model and potential. While remaining unknown to source host",
    author="IAmSoThirsty",
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
            "ai_program_enforcer=app.main:main",
        ],
    },
)
