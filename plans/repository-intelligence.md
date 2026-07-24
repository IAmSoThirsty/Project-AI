# Project-AI Repository Intelligence

## Goal
Give Project-AI a read-only, deterministic, local capability to index and search its own source code and documentation with provenance-preserving results.

## Research Summary
- Repository/code intelligence is more reliable when exact lexical matches and semantic recall are combined; code queries often depend on identifiers, paths, and symbols that dense-only retrieval can miss.
- Structure-aware code chunking and metadata such as path, language, and line range are important for assembling trustworthy context.
- Project-AI already contains a reusable `packages/knowledge` subsystem with deterministic chunk IDs, persisted vector indexes, CPU-only hashing/model2vec/Ollama embedders, supported text extraction, and provenance metadata.
- The existing `apps/services` FastAPI host is read-only and authority-free, making it the safest integration boundary for an initial repository-intelligence surface.
- Baseline: `apps/services/tests` plus `packages/knowledge/tests` currently pass: 45 tests passed. No repository search/status endpoint currently exists.

## Approach
Implement one capability first: repository intelligence. Reuse the existing knowledge primitives rather than adding a new vector database or hosted LLM dependency. Build an offline repository snapshot/index, retain path and line-range provenance, combine deterministic lexical matching with the existing semantic index, and expose only read-only query/status operations through a dedicated service role. Keep generated artifacts, dependency/vendor trees, caches, secrets, and binary files excluded by policy. Do not add actuation, governance authority, or write endpoints.

This is preferred over starting with RAG, model routing, multimodality, local generation, or adversarial testing because the repository index is a prerequisite knowledge substrate for those capabilities and can be implemented locally on the available CPU-only Windows environment without credentials.

## Subtasks
1. Extend the knowledge layer with repository-specific file selection, metadata/provenance, structure-aware chunk records, deterministic lexical lookup, and persisted snapshot/index loading; expected output: reusable repository-intelligence implementation and unit tests (verify exact path/identifier queries return the expected files and persisted results are identical).
2. Add an offline repository-index build/refresh command that scans the Project-AI tree while enforcing exclusion, file-size, and path-safety policies; expected output: index artifacts plus a machine-readable status/manifest (verify the current repository can be indexed and counts are non-zero, generated/vendor/cache paths are absent, and hashes/paths are deterministic).
3. Integrate a read-only `repository-intelligence` service role into the existing FastAPI service host with status and search responses that include source path, line range, match score, and excerpt; expected output: HTTP endpoints and strict response models (verify empty queries, invalid limits, missing indexes, and normal searches fail or return explicit results rather than silent defaults).
4. Add service and package tests covering authorization-free read-only behavior, exclusion rules, lexical/semantic ranking, provenance, persistence, and error handling; expected output: expanded test suite with the original 45 tests still passing plus new coverage.
5. Document the capability, build/refresh command, environment configuration, endpoint contract, limitations, and safe operating boundary; expected output: updated service/knowledge documentation and an operator-facing usage example.
6. Run the implementation end-to-end against the actual repository, query representative questions about the Android client, knowledge package, and service host, and report concrete result counts and top paths; expected output: verified local index, passing tests, and a short completion report (verify results vary by query and contain real repository paths/excerpts, not constant or fallback responses).

## Deliverables
| File Path | Description |
|-----------|-------------|
| `t:\00-Active\Project-AI-Beginnings\packages\knowledge\...` | Repository index, retrieval, provenance, and build implementation |
| `t:\00-Active\Project-AI-Beginnings\apps\services\...` | Read-only repository-intelligence service role and API models |
| `t:\00-Active\Project-AI-Beginnings\data\repository-intelligence\...` | Locally generated repository snapshot/index artifacts, if safe to materialize |
| `t:\00-Active\Project-AI-Beginnings\plans\repository-intelligence.md` | This implementation plan |
| `t:\00-Active\Project-AI-Beginnings\docs\...` and/or package READMEs | Operator and developer documentation |

## Evaluation Criteria
- Existing baseline remains green: the original 45 service/knowledge tests pass.
- New repository-intelligence tests pass, including deterministic persistence and exclusion-policy tests.
- A real index of the current repository is built with non-zero files/chunks and a manifest containing hashes and counts.
- At least three representative queries return non-empty, query-dependent results with real paths and excerpts; exact identifier/path queries retrieve the expected component.
- Results expose provenance sufficient to locate the source (`path`, line range or chunk range, and content hash).
- No endpoint can mutate files, issue authority, execute commands, or silently fall back to an empty/all-pass answer.
- Missing or stale index state is explicit in status/errors.

## Notes
- Use the project virtual environment at `t:\00-Active\Project-AI-Beginnings\.venv` for verification.
- The environment has no GPU and limited available RAM, so the first implementation must remain CPU/local and avoid requiring a hosted model or heavyweight runtime.
- Do not index `.git`, virtual environments, dependency trees, build outputs, caches, generated artifacts, secrets, or binary files.
- Preserve the existing downward dependency direction and authority-free service boundary.
