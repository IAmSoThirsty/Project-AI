from setuptools import setup, find_packages

setup(
    name="Autonomous Compliance-as-Code Engine",
    version="1.0.0",
    description="Build a regulator-ready microservice fabric that:
Ingests policy (YAML/DSL)
Compiles invariants
Evaluates runtime actions deterministically
Produces signed audit trails
Exports SOC2 / ISO / NIST artifacts automatically
Add:
Continuous evidence generation
Machine-verifiable compliance proofs
API to expose compliance state to customers",
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
