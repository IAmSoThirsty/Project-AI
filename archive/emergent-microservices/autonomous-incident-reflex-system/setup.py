#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="Autonomous Incident Reflex System",
    version="1.0.0",
    description="Build threat detection microservice, policy evaluation gate, reflexive action executor, evidence preservation pipeline, and cryptographic chain-of-custody service. Think CrowdStrike plus immutable evidence plus deterministic replay - defense sector eats this up.",
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
            "autonomous_incident_reflex_system=app.main:main",
        ],
    },
)
