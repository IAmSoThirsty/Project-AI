#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="AI Mutation Governance Firewall",
    version="1.0.0",
    description="A Kubernetes admission controller for AI evolution - build a runtime AI mutation gate with microservices for model change proposal intake, deterministic shadow simulation, quorum validation engine, rollback + snapshot manager, and cryptographic replay verification. This is niche but elite - DARPA, defense, sovereign AI labs would care.",
    author="IAmSoThirsty",
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
            "ai_mutation_governance_firewall=app.main:main",
        ],
    },
)
