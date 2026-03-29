import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-obsidian-protocol / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Obsidian Protocol",
    version="1.0.0",
    description="This is a single-binary microservice that lives outside your main cluster. Its only job is to monitor the Cerberus Containment Service. If Cerberus reports a breach that the Master Controller can't fix, Obsidian wipes the encryption keys in the Cryptographic Agility Service, turning your entire data hoard into useless noise.",
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
            "the_obsidian_protocol=app.main:main",
        ],
    },
)
