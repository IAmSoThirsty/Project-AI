#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="Sovereign Data Vault Layer",
    version="1.0.0",
    description="Microservices for zero-knowledge encryption layer, capability-based access control, time-bound decryption tokens, audit trail hashing, and revocation propagation service. Use case: your data, provably inaccessible without your cryptographic consent.",
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
            "sovereign_data_vault_layer=app.main:main",
        ],
    },
)
