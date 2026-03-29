import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: constitutional-amendment-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Constitutional Amendment Service",
    version="1.0.0",
    description="Manages the three-tier review process from T.A.M.S.-Ω — 72 hour emergency, 30 day standard, 90 day constitutional. Enforces review periods. Auto-reverts emergency amendments if not ratified. The living governance engine.",
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
            "constitutional_amendment_service=app.main:main",
        ],
    },
)
