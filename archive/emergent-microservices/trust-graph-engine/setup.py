#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="Distributed Reputation & Trust Graph Engine",
    version="1.0.0",
    description="Build verifiable identity nodes, weighted trust edges, Sybil resistance scoring, on-chain optional anchoring, and real-time trust API. Use cases include anti-bot verification, secure marketplaces, intelligence vetting networks, and high-signal communication channels. If done correctly, this becomes infrastructure.",
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
