import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-sovereign-skin / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Sovereign Skin",
    version="1.0.0",
    description="The Logic: Instead of checking passwords, it checks Behavioral Integrity. If a request comes in that fits the Linguistics of a known threat but has the Identity of a valid user, the Cerberus service locks the "Temporal Bridge" to prevent data egress.
The Status: It turns your stack into a "Zero-Trust" fortress where even the services don't fully trust each other without the Confidence Calibration check-in.",
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
            "the_sovereign_skin=app.main:main",
        ],
    },
)
