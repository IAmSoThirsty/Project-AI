#!/usr/bin/env python3
"""Extract violation examples from ruff results."""
import json
from collections import defaultdict

with open('ruff_results.json') as f:
    data = json.load(f)

examples = defaultdict(list)
for v in data:
    examples[v['code']].append(v)

print("Sample violations by category:\n")
for code in ['SIM102', 'F401', 'B904', 'E722', 'N806']:
    if examples[code]:
        ex = examples[code][0]
        print(f"\n{code} - {ex['message']}")
        print(f"  Example: {ex['filename']}:{ex['location']['row']}")
