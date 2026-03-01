from setuptools import setup, find_packages

setup(
    name="Autonomous Incident Reflex System",
    version="1.0.0",
    description="Build:
Threat detection microservice
Policy evaluation gate
Reflexive action executor
Evidence preservation pipeline
Cryptographic chain-of-custody service
Think: CrowdStrike + immutable evidence + deterministic replay.
Defense sector eats this up.",
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
