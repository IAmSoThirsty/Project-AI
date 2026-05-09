#!/usr/bin/env python3
"""inspect_evidence_bundle.py — CLI to inspect EvidenceBundles from the in-process store.

Usage:
    python scripts/inspect_evidence_bundle.py [options]

Options:
    --all               Show all bundles (default: latest 10)
    --limit N           Max bundles to display (default: 10)
    --json              Output raw JSON
    --verbose, -v       Show all fields including hashes

Note: The evidence store is in-process only. This script generates a sample
set of bundles to demonstrate the store and inspector mechanics. In production,
point your long-running process at get_evidence_store() directly.
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.evidence_bundle import EvidenceBundleWriter, get_evidence_store

# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

RESET = '\033[0m'
_OUTCOME_COLORS = {
    'ALLOW':                   '\033[92m',  # green
    'DENY':                    '\033[91m',  # red
    'HALT':                    '\033[91m',  # red
    'ESCALATE':                '\033[95m',  # magenta
    'CLARIFY':                 '\033[93m',  # yellow
    'HUMAN_APPROVAL_REQUIRED': '\033[93m',  # yellow
    'DEGRADED_READ_ONLY':      '\033[94m',  # blue
}


def colorize(outcome: str) -> str:
    c = _OUTCOME_COLORS.get(outcome, '')
    return f"{c}{outcome}{RESET}" if c else outcome


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_bundle(b: dict, index: int | None = None, verbose: bool = False) -> None:
    prefix = f"[{index}] " if index is not None else ""
    outcome  = b.get('final_outcome', 'UNKNOWN')
    ts       = b.get('timestamp', 0)
    bhash    = (b.get('bundle_hash') or b.get('bundle_id', ''))[:16] + '…'
    req_hash = (b.get('request_hash') or '')[:16] + '…'
    policy_v = b.get('policy_version', '<none>')
    policy_h = (b.get('policy_hash') or '')[:12] + '…'
    chain_p  = (b.get('audit_chain_prev') or 'genesis')[:16]
    chain_n  = (b.get('audit_chain_next') or '')[:16] + '…'
    intent   = b.get('intent_classification', '')
    risk     = b.get('risk_classification', '')
    benign   = b.get('benign_validation', '')

    import datetime
    ts_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else '—'

    print(f"{prefix}{colorize(outcome):<30}  {ts_str}")
    print(f"  intent:       {intent or '—'}")
    print(f"  risk:         {risk or '—'}")
    print(f"  benign:       {benign or '—'}")
    print(f"  policy:       {policy_v}  hash={policy_h}")
    if verbose:
        print(f"  request_hash: {req_hash}")
        print(f"  bundle_hash:  {bhash}")
        print(f"  chain_prev:   {chain_p}")
        print(f"  chain_next:   {chain_n}")
        print(f"  cap_token:    {b.get('capability_token') or '—'}")
        print(f"  continuity:   {(b.get('continuity_proof') or '—')[:40]}")
        inv = b.get('invariant_results') or []
        if inv:
            print(f"  invariants:   {inv}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect Project-AI EvidenceBundle store.')
    parser.add_argument('--all',     action='store_true', help='Show all bundles')
    parser.add_argument('--limit',   type=int, default=10, metavar='N')
    parser.add_argument('--json',    action='store_true', help='Raw JSON output')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    # Seed the store with demo bundles so the script is self-demonstrating
    w = EvidenceBundleWriter()
    demos = [
        ("read_file_op",   "ALLOW",                   "benign read cleared all guards"),
        ("drop_table",     "DENY",                    "high_impact + no human confirmation"),
        ("list_users",     "DEGRADED_READ_ONLY",      "governance degraded; read-only permitted"),
        ("exec_arbitrary", "HUMAN_APPROVAL_REQUIRED", "high_impact action pending approval"),
        ("fork_chain",     "HALT",                    "state branching conflict detected"),
        ("escalate_perms", "ESCALATE",                "signing_key_match invariant violated"),
    ]
    for intent, outcome, _reason in demos:
        w.build(
            request_hash=__import__('hashlib').sha256(intent.encode()).hexdigest(),
            intent_classification=intent,
            final_outcome=outcome,
        )

    store  = get_evidence_store()
    all_b  = list(reversed(store.all()))  # newest first
    total  = len(all_b)

    if total == 0:
        print("Evidence store is empty.")
        sys.exit(0)

    subset = all_b if args.all else all_b[:args.limit]

    if args.json:
        print(json.dumps(subset, indent=2))
        return

    # Summary header
    print(f"Evidence Store — {total} bundle(s) total, showing {len(subset)}")
    print('=' * 72)
    counts = Counter(b.get('final_outcome', 'UNKNOWN') for b in all_b)
    print("Outcome summary:")
    for outcome, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {colorize(outcome):<30}  {cnt}")
    print()
    print('-' * 72)
    print()

    for i, b in enumerate(subset):
        display_bundle(b, index=i, verbose=args.verbose)

    remaining = total - len(subset)
    if remaining > 0:
        print(f"… {remaining} older bundle(s) not shown. Use --all or --limit {total}.")


if __name__ == '__main__':
    main()
