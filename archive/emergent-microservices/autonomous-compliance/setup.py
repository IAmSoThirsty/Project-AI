#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="Autonomous Compliance-as-Code Engine",
    version="1.0.0",
    description="Build a regulator-ready microservice fabric that ingests policy (YAML/DSL), compiles invariants, evaluates runtime actions deterministically, produces signed audit trails, and exports SOC2/ISO/NIST artifacts automatically. Includes continuous evidence generation, machine-verifiable compliance proofs, and API to expose compliance state to customers.",
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
            "autonomous_compliance_as_code_engine=app.main:main",
        ],
    },
)
