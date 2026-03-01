from setuptools import setup, find_packages

setup(
    name="Verifiable Reality Infrastructure (Post-AI Proof Layer)",
    version="1.0.0",
    description="a cryptographic content authenticity network.
Microservices:
Identity attestation service (hardware-bound keys, WebAuthn)
Media signing service (hash + Merkle anchoring)
Public verification API
Browser extension verifier
Immutable transparency log
Dispute resolution / counterclaim service
Use case:
Politicians sign speeches.
Corporations sign press releases.
Journalists sign raw footage.
Public verifies via hash proof.",
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
            "verifiable_reality_infrastructure_(post_ai_proof_layer)=app.main:main",
        ],
    },
)
