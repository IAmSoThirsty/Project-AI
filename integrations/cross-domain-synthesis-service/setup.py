import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: cross-domain-synthesis-service / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="Cross-Domain Synthesis Service",
    version="1.0.0",
    description="When a query touches multiple knowledge domains — say, the history of a medicinal plant and its chemical properties and its legal status in three jurisdictions — this service orchestrates the answer across services rather than forcing Legion to context-switch alone.",
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
            "cross_domain_synthesis_service=app.main:main",
        ],
    },
)
