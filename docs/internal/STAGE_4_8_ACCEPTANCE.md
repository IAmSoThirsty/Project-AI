# Stage 4.8 Acceptance: Governance Framework

**Status:** ACCEPTED FOR DEVELOPMENT

## Selective Ingest

Fifteen explicitly allowlisted governance assets were imported into
`packages/rlp/governance_framework/`: prompts, policies, templates,
checklists, examples, parser fixtures, the source test module, and the
compliance parser. Every file has a source path and SHA-256 digest in
`STAGE_4_7_4_8_IMPORT_REPORT.json`.

The embedded `governance_agent/venv`, caches, temporary files, generated
reports, operational output, and all non-allowlisted files were never
traversed or copied. The allowlisted materials are included as package data in
the RLP wheel but do not gain execution authority.

## Verification

- `run_compliance_tests.py --dry-run` parsed 10 test prompts and 8 failure
  cases, for 18/18 structurally valid compliance fixtures.
- The full repository unit suite passes with the governance reference tree
  excluded from automatic pytest discovery.
- The imported `test_governance_agent.py` is retained as reference evidence;
  it is not claimed as executed because its `governance_agent` runtime was
  deliberately excluded from this selective ingest.

Arbiter and RLP remain experimental operator-side inputs and cannot bypass the
AI-side execution gate.
