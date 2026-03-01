import hashlib
import json

ROOT_INVARIANTS = [
    "INV_ROOT_1 (Actor identity verified via Ed25519 signature)",
    "INV_ROOT_2 (Capability tokens must be unexpired and correctly signed)",
    "INV_ROOT_3 (Every decision must be recorded in the append-only ledger)",
    "INV_ROOT_4 (All state mutations must pass through the Commit Coordinator)",
    "INV_ROOT_5 (Build artifacts must have valid reproducible attestations)",
    "INV_ROOT_6 (SAFE-HALT must trigger on any invariant violation)",
    "INV_ROOT_7 (Security strictness must be monotonic — no downgrades)",
    "INV_ROOT_8 (Quorum consensus [3f+1] required for high-impact actions)",
    "INV_ROOT_9 (Ledger historical records are immutable and sealed)",
]

data = json.dumps(
    [str(d) for d in sorted(ROOT_INVARIANTS, key=str)],
    sort_keys=True,
    separators=(",", ":"),  # Typical JSON compact representation
)
print(f"Compact: {hashlib.sha256(data.encode()).hexdigest()}")

data_standard = json.dumps(
    [str(d) for d in sorted(ROOT_INVARIANTS, key=str)], sort_keys=True
)
print(f"Standard: {hashlib.sha256(data_standard.encode()).hexdigest()}")
