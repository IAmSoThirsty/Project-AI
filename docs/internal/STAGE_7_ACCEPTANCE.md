# Stage 7 Acceptance: Capability

**Status:** ACCEPTED FOR DEVELOPMENT

- [x] Package depends downward on `project-ai-kernel` only.
- [x] Tokens use canonical JSON and HMAC-SHA256 with a minimum 256-bit secret.
- [x] Claims bind issuer, subject, operation, resource, issue time, expiry, and token ID.
- [x] TTL is positive and bounded by authority policy.
- [x] Signature, schema, issuer, time order, and exact scope are verified.
- [x] Expired, revoked, scope-mismatched, malformed, and replayed tokens fail closed.
- [x] One-time consumption is lock-protected for the execution stage.
- [x] Ruff and strict MyPy pass.
- [x] Tests: `9 passed`; branch coverage: `91.95%`.
- [x] Wheel and source distribution build successfully at `0.0.0.dev0`.

Legacy source hashes are recorded in `STAGE_7_SOURCE_MAP.md`; the legacy
repository remains unchanged.
