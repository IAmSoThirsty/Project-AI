#!/usr/bin/env python3
"""
verify_frozen_history.py — Independent verifier for the frozen-history file.

Walks PROJECT-AI_FROZEN_HISTORY.md section by section.

For each section, the generator:
  1. Builds a BODY (no chain link line in it).
  2. Computes SHA-256 of the body.
  3. Injects the chain link line into the section, where the chain link's
     `this` value is the hash from step 2.

So the verifier must:
  - Extract the chain link line's `prev` and `this` hashes.
  - Hash the section text MINUS the chain link line.
  - Compare the recomputed hash to the chain link's `this` value.
  - Confirm `prev` matches the previous section's `this`.

Exit 0 = chain intact. Exit 1 = tamper detected.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

GENESIS = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def find_section_bounds(text: str) -> list[tuple[int, int]]:
    """
    Return [(start_offset, end_offset), ...] for each commit section.
    end_offset is the start of the next section, or the start of the
    "# Branches" block, or end-of-file for the last section.
    """
    SECTION_HEADER_RE = re.compile(r"^## Commit (\d+) / (\d+) — `([0-9a-f]{12})`$", re.MULTILINE)
    BRANCHES_RE = re.compile(r"^# Branches$", re.MULTILINE)
    TAGS_RE = re.compile(r"^# Tags$", re.MULTILINE)
    LEDGER_RE = re.compile(r"^# Ledger Head$", re.MULTILINE)

    starts = [m.start() for m in SECTION_HEADER_RE.finditer(text)]
    if not starts:
        return []

    # Find boundaries
    boundaries = []
    for i, start in enumerate(starts):
        if i + 1 < len(starts):
            end = starts[i + 1]
        else:
            # Last section ends at start of next top-level block, or EOF
            end_candidates = [
                m.start() for m in [BRANCHES_RE.search(text, start), TAGS_RE.search(text, start), LEDGER_RE.search(text, start)]
                if m
            ]
            end = min(end_candidates) if end_candidates else len(text)
        boundaries.append((start, end))
    return boundaries


def extract_body(section_text: str) -> str:
    """
    Remove the chain link line from the section text. The chain link line
    is the line starting with "- **Chain link:**" — anything else stays.
    """
    CHAIN_LINK_RE = re.compile(r"^- \*\*Chain link:\*\* `([0-9a-f]{64})` -> `([0-9a-f]{64})`$", re.MULTILINE)
    m = CHAIN_LINK_RE.search(section_text)
    if not m:
        return section_text  # chain link missing; let main loop report it
    # Find full line bounds (start of line to end of line, including the trailing \n)
    line_start = section_text.rfind("\n", 0, m.start()) + 1
    line_end = section_text.find("\n", m.end())
    if line_end == -1:
        line_end = len(section_text)
    else:
        line_end += 1  # include the \n
    return section_text[:line_start] + section_text[line_end:]


def verify(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    print(f"[verify] file: {path}")
    print(f"[verify] size: {len(text):,} bytes")
    print()

    boundaries = find_section_bounds(text)
    print(f"[verify] found {len(boundaries)} commit sections")
    print()

    CHAIN_LINK_RE = re.compile(r"^- \*\*Chain link:\*\* `([0-9a-f]{64})` -> `([0-9a-f]{64})`$", re.MULTILINE)
    LEDGER_HEAD_RE = re.compile(r"^The final section's SHA-256 \(binds the entire chain\): `([0-9a-f]{64})`$", re.MULTILINE)

    expected_prev = GENESIS
    sections_ok = 0
    sections_fail = 0
    last_this = GENESIS
    ledger_head_claimed: str | None = None

    for i, (start, end) in enumerate(boundaries):
        section_text = text[start:end]
        m = CHAIN_LINK_RE.search(section_text)
        if not m:
            print(f"  [FAIL] section {i + 1}: no chain link line found")
            sections_fail += 1
            continue
        claimed_prev, claimed_this = m.group(1), m.group(2)

        body = extract_body(section_text)
        recomputed = hashlib.sha256(body.encode("utf-8")).hexdigest()

        ok_hash = recomputed == claimed_this
        ok_link = claimed_prev == expected_prev

        if ok_hash and ok_link:
            sections_ok += 1
            if sections_ok <= 3 or sections_ok % 500 == 0:
                print(f"  [OK]   section {sections_ok}: {claimed_this[:16]}.. (prev={claimed_prev[:16]}..)")
        else:
            sections_fail += 1
            if sections_fail <= 5:
                print(f"  [FAIL] section {i + 1}:")
                if not ok_hash:
                    print(f"         hash mismatch: claimed={claimed_this[:16]}..  recomputed={recomputed[:16]}..")
                if not ok_link:
                    print(f"         chain broken: prev={claimed_prev[:16]}..  expected_prev={expected_prev[:16]}..")

        expected_prev = claimed_this
        last_this = claimed_this

    # Ledger head
    lm = LEDGER_HEAD_RE.search(text)
    if lm:
        ledger_head_claimed = lm.group(1)

    print()
    print(f"[verify] sections OK:    {sections_ok}")
    print(f"[verify] sections FAIL:  {sections_fail}")
    print(f"[verify] last section hash: {last_this[:16]}..")
    print(f"[verify] ledger head claimed in footer: {ledger_head_claimed[:16] if ledger_head_claimed else 'NOT FOUND'}..")
    if ledger_head_claimed and ledger_head_claimed != last_this:
        print("  [FAIL] ledger head mismatch")
        sections_fail += 1
    print()
    if sections_fail == 0 and sections_ok > 0:
        print(f"[verify] CHAIN INTACT. {sections_ok} sections verified.")
        return 0
    else:
        print(f"[verify] CHAIN BROKEN. {sections_fail} failures.")
        return 1


if __name__ == "__main__":
    p = Path(sys.argv[1] if len(sys.argv) > 1 else r"T:\Project-AI-Beginnings\docs\internal\frozen-history\PROJECT-AI_FROZEN_HISTORY.md")
    sys.exit(verify(p))
