from setuptools import setup, find_packages

setup(
    name="Sovereign Data Vault Layer",
    version="1.0.0",
    description="Microservices:
Zero-knowledge encryption layer
Capability-based access control
Time-bound decryption tokens
Audit trail hashing
Revocation propagation service
Use case: “Your data, provably inaccessible without your cryptographic consent.”",
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
