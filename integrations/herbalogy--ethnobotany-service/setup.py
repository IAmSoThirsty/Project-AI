import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: herbalogy--ethnobotany-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Herbalogy & Ethnobotany Service",
    version="1.0.0",
    description="Plant identification, traditional medicinal use, contraindications, regional variants, indigenous knowledge attribution. Important: includes provenance — who knew this first and where.",
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
            "herbalogy_&_ethnobotany_service=app.main:main",
        ],
    },
)
