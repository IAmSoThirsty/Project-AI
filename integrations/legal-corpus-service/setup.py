import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: legal-corpus-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Legal Corpus Service",
    version="1.0.0",
    description="Jurisdiction-aware. Not legal advice — legal structure. Knows the difference between common law and civil law systems. Flags when something touches regulatory territory.",
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
            "legal_corpus_service=app.main:main",
        ],
    },
)
