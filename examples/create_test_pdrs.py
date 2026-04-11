#!/usr/bin/env python3
"""Quick test to verify CLI tools work with persistent storage."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cognition.pdr_enhanced import PDRRegistry, PDRDecision, PDRSeverity

# Create registry with test storage
registry = PDRRegistry(
    storage_path=Path("test_pdr_cli"),
    checkpoint_interval=5,
    auto_sign=True
)

# Create test PDRs
print("Creating test PDRs...")
pdr_ids = []

for i in range(3):
    pdr = registry.create_pdr(
        request_id=f"REQ-CLI-{i:03d}",
        decision=PDRDecision.ALLOW if i % 2 == 0 else PDRDecision.DENY,
        severity=PDRSeverity.LOW,
        rationale=f"CLI test PDR {i}",
        context={"index": i}
    )
    pdr_ids.append(pdr.pdr_id)
    print(f"  ✓ Created {pdr.pdr_id}")

print(f"\n✅ Created {len(pdr_ids)} PDRs")
print(f"\nNow run:")
print(f"  python tools/pdr_verify.py --storage test_pdr_cli list")
print(f"  python tools/pdr_verify.py --storage test_pdr_cli verify {pdr_ids[0]}")
print(f"  python tools/pdr_verify.py --storage test_pdr_cli stats")
