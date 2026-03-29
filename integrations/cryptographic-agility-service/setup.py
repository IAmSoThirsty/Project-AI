import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: cryptographic-agility-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Cryptographic Agility Service",
    version="1.0.0",
    description="When a primitive becomes vulnerable — T.A.M.S.-Ω Tier-Zero Constitutional Event — this service orchestrates the migration. Freeze, classify, transition, archive. The thing that keeps the cryptographic foundation from becoming a single point of failure",
    author="Jeremy Karrick / IAmSoThirsty",
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
            "cryptographic_agility_service=app.main:main",
        ],
    },
)
