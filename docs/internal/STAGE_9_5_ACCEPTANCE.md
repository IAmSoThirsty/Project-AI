# Stage 9.5 Acceptance: Android Read-Only Client

**Status:** ACCEPTED FOR DEVELOPMENT (REVISED SCOPE)
**Unity:** DEFERRED BY USER DECISION ON 2026-06-21

- [x] Standalone Gradle 8.2 / AGP 8.2.1 / Kotlin 1.9.22 project.
- [x] Java 17, compile/target SDK 34, minimum SDK 26.
- [x] Android SDK Platform 34, Build Tools 34.0.0, and Platform Tools installed.
- [x] Client exposes only fixed `GET /dois` and `GET /replay/status` calls.
- [x] No POST, mutation, execution, governance, capability, or token API exists.
- [x] Unit tests verify endpoint selection and canonical payload mapping.
- [x] `testDebugUnitTest` passes.
- [x] `assembleDebug` produces an 804,466-byte development APK.
- [x] Development APK SHA-256: `EFFFC894FCAC236DA51BA8B82742C2E83E5E4C4E21F47B70CE3AC08A535326B8`.
- [x] Version is `0.0.0.dev0`; no release artifact is tracked or published.

AGP emitted a non-blocking SDK XML compatibility warning because command-line
tools 21.0 are newer than AGP 8.2.1. Compilation, tests, DEX, packaging, and
debug signing all passed.

The Unity editor environment install completed before cancellation was
observed, but no Unity project or repository files were created. Unity is not
part of the revised acceptance checkpoint.
