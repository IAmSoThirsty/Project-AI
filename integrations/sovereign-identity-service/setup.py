import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: sovereign-identity-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Sovereign Identity Service",
    version="1.0.0",
    description="Cryptographic root identity management. Issues and validates the identity tokens that T.A.M.S.-Ω says must underpin all constitutional authority. No identity service means no cryptographic sovereignty — everything else is built on sand.",
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
            "sovereign_identity_service=app.main:main",
        ],
    },
)
