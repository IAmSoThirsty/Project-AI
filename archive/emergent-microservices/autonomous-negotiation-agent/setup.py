#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="Autonomous Negotiation Agent Infrastructure",
    version="1.0.0",
    description="Build an agent system that negotiates contracts via structured constraints, produces verifiable agreements, signs with cryptographic identity, tracks performance obligations, and auto-triggers dispute arbitration logic. This is programmable legal infrastructure.",
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
            "autonomous_negotiation_agent_infrastructure=app.main:main",
        ],
    },
)
