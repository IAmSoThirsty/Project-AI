from setuptools import setup, find_packages

setup(
    name="Autonomous Negotiation Agent Infrastructure",
    version="1.0.0",
    description="Build an agent system that:
Negotiates contracts via structured constraints
Produces verifiable agreements
Signs with cryptographic identity
Tracks performance obligations
Auto-triggers dispute arbitration logic
This is programmable legal infrastructure.",
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
