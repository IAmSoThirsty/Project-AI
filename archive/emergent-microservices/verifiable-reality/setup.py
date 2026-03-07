#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
from setuptools import find_packages, setup

setup(
    name="Verifiable Reality Infrastructure (Post-AI Proof Layer)",
    version="1.0.0",
    description="A cryptographic content authenticity network with microservices for identity attestation service (hardware-bound keys, WebAuthn), media signing service (hash + Merkle anchoring), public verification API, browser extension verifier, immutable transparency log, and dispute resolution/counterclaim service. Use case: politicians sign speeches, corporations sign press releases, journalists sign raw footage, and public verifies via hash proof.",
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
