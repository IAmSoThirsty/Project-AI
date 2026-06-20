# Project-AI Security

This development package carries the selectively imported Chimera v2.2 perimeter and a typed,
append-only bridge for governance verdicts, denials, and canary events. The bridge stores hashes
instead of raw canary values and does not expose Chimera runtime state.

The repository license is MIT. `reference/chimera_v2_2.py` preserves the imported implementation
with only the owner-authorized license-header normalization. The runtime module is an owned copy
that is formatted, typed, and tested separately. The import report records both source hashes.
