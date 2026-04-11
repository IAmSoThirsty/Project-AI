#!/usr/bin/env python3
"""Show classification summary for READMEs."""

import json

with open('audit/classification_readmes.json', 'r') as f:
    data = json.load(f)

print('=== CRITICAL READMEs (TYPE=critical) ===')
critical = [c for c in data['classifications'] if c['type'] == 'critical']
for readme in critical:
    state = readme['state']
    tier = readme['quality_tier']
    lines = readme['line_count']
    issues = len(readme['issues'])
    print(f"{readme['path']:50s} | {state:10s} | {tier:20s} | {lines:4d} lines | {issues} issues")

print(f"\nTotal critical: {len(critical)}")

print('\n=== REDUNDANT READMEs (TYPE=redundant) ===')
redundant = [c for c in data['classifications'] if c['type'] == 'redundant']
for readme in redundant:
    state = readme['state']
    tier = readme['quality_tier']
    lines = readme['line_count']
    print(f"{readme['path']:50s} | {state:10s} | {tier:20s} | {lines:4d} lines")

print(f"\nTotal redundant: {len(redundant)}")

print('\n=== STUB READMEs (quality_tier=tier_4_stubs) ===')
stubs = [c for c in data['classifications'] if c['quality_tier'] == 'tier_4_stubs']
for readme in stubs[:15]:
    print(f"{readme['path']:60s} | {readme['line_count']:3d} lines")

print(f"\nTotal stubs: {len(stubs)}")

print('\n=== ISSUES BREAKDOWN ===')
naming_issues = [c for c in data['classifications'] if any('Naming inconsistency' in issue for issue in c['issues'])]
print(f"Naming inconsistency: {len(naming_issues)} READMEs")

broken_refs = [c for c in data['classifications'] if any('Broken reference' in issue for issue in c['issues'])]
print(f"Broken references: {len(broken_refs)} READMEs")

todo_markers = [c for c in data['classifications'] if any('TODO/FIXME' in issue for issue in c['issues'])]
print(f"TODO/FIXME markers: {len(todo_markers)} READMEs")

print("\n=== EXEMPLARY READMEs (tier_1_exemplary) ===")
exemplary = [c for c in data['classifications'] if c['quality_tier'] == 'tier_1_exemplary']
for readme in exemplary[:10]:
    print(f"{readme['path']:60s} | {readme['line_count']:4d} lines")
print(f"\nTotal exemplary: {len(exemplary)}")
