"""atlas.schemas - Canonical JSON Schema validation for ATLAS Omega.

SUBORDINATION NOTICE:
This module is part of ATLAS Omega, a SECONDARY, OPTIONAL
tool subordinate to Project-AI.

Primary System: Project-AI (Jeremy Karrick, Architect and Founder)
Triumvirate governance: ACTIVE and UNCHANGED

The schemas module loads + validates + provides access to
all canonical Draft-07 JSON schemas for the atlas stack,
with SHA-256 integrity verification. Includes:

- claim.schema.json: factual claims (id, statement,
  claimant, veracity, impact, evidence, metadata)
- influence_graph.schema.json: influence graph structure
- opinion.schema.json: opinion objects
- organization.schema.json: organization objects
- projection_pack.schema.json: projection pack outputs
- world_state.schema.json: world state snapshots
"""
