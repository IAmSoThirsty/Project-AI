# Stage 4.7 Acceptance: OMPT And Chimera

**Status:** ACCEPTED FOR DEVELOPMENT

## Imported Source

- The OMPT source parser extracted exactly seven declared files into
  `apps/web-static/ompt-reference/`: five HTML pages, one stylesheet, and one
  JavaScript file.
- The complete Chimera v2.2 implementation is retained under
  `packages/security/reference/` with its original archive/file hashes in the
  import report.
- The Chimera source header is normalized from the superseded dual license to
  the repository MIT license under the current owner's explicit authority.
- The packaged runtime contains only the reusable request classifier, canary
  registry, and append-only audit bridge. Raw canary values are never written
  to relay evidence.

## Exclusions

Chimera environment files, service definitions, container files, runtime
databases, logs, secrets, and operational state were not copied. The static
OMPT reference remains source input for the Stage 14 React applications, not a
production deployment artifact.

## Verification

- Import report regeneration is byte-for-byte deterministic.
- Ruff passes for the import tool and security runtime/tests.
- strict MyPy passes for six security/import source files.
- Security tests: `13 passed`.
- Security branch coverage: `93.63%`.
- Wheel and source distribution build at `0.0.0.dev0`.
- Repository test suite after quarantine collection repair: `32 passed`.

No release, tag, deployment, or production-readiness claim is made.
