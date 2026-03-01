from setuptools import setup, find_packages

setup(
    name="Distributed Reputation & Trust Graph Engine",
    version="1.0.0",
    description="Build:
Verifiable identity nodes
Weighted trust edges
Sybil resistance scoring
On-chain optional anchoring
Real-time trust API
Use cases:
Anti-bot verification
Secure marketplaces
Intelligence vetting networks
High-signal communication channels
If done correctly, this becomes infrastructure.",
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
            "distributed_reputation_&_trust_graph_engine=app.main:main",
        ],
    },
)
