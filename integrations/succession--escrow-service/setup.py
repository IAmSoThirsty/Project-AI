import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: succession--escrow-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Succession & Escrow Service",
    version="1.0.0",
    description="T.A.M.S.-Ω Section 7. Cryptographic threshold escrow for sovereign identity. 3-of-5 key holders. The service that ensures Project-AI survives its founder. This one is personal.",
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
            "succession_&_escrow_service=app.main:main",
        ],
    },
)
