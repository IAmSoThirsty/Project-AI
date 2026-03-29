import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-trinity-harmonizer / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Trinity Harmonizer",
    version="1.0.0",
    description="This is the top-level logic gate. When the Medical Knowledge Service suggests a procedure, but the Legal Corpus Service flags a liability, and the Temporal Dissonance Bridge shows a conflict in the timeline—this service breaks the tie.
Function: Weight-based arbitration.",
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
            "the_trinity_harmonizer=app.main:main",
        ],
    },
)
