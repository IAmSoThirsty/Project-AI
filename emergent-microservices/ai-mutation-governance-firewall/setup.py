from setuptools import setup, find_packages

setup(
    name="AI Mutation Governance Firewall",
    version="1.0.0",
    description="build a runtime AI mutation gate.
Microservices:
Model change proposal intake
Deterministic shadow simulation
Quorum validation engine
Rollback + snapshot manager
Cryptographic replay verification
This becomes: “A Kubernetes admission controller for AI evolution.”
This is niche but elite.
DARPA, defense, sovereign AI labs would care.",
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
