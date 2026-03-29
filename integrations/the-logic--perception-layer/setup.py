import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-logic--perception-layer / setup.py
# ============================================================================ #
from setuptools import setup, find_packages

setup(
    name="The Logic & Perception Layer",
    version="1.0.0",
    description="Heuristic Drift Inhibitor: Works with your Semantic Drift Monitor. It doesn't just watch the drift; it actively forces the AI weights or logic gates back to a "Golden Baseline" if the system starts hallucinating or diverging from its original purpose.
Consensus Hallucination Filter: In a multi-cloud setup, this service compares outputs from the same request across different regions. If they differ, it flags a "Reality Fracture" and forces a re-compute.
Contextual Amnesia Service: A "Right to be Forgotten" engine. It ensures that when data is marked for Knowledge Decay, every trace, log, and cached fragment across the entire stack is purged simultaneously.",
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
            "the_logic_&_perception_layer=app.main:main",
        ],
    },
)
