"""a cryptographic content authenticity network.
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
Public verifies via hash proof."""

__version__ = "1.0.0"
