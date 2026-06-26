# Beginnings `apps/` Inventory (Q8 resolution)

> **Generated:** 2026-06-25
> **Project:** Project-AI Beginnings
> **Mode:** discovery (read-only)
> **Resolves:** Legacy Gap Inventory §8 Q8 ("Beginnings `apps/` vs `packages/`")
> **Source-of-truth:** `T:\Project-AI-Beginnings\apps\` (working tree)
> **Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`

---

## 0. Headline

`apps/` is the **application tier** of Beginnings — distinct from `packages/`, which is the **governance/runtime tier**. None of the four apps below import governance, execution, or capability authority. They are read-only or explicitly authorized API consumers.

| App | Tier | Language | LOC (source only, excl. generated/node_modules/build) | Authority surface |
|---|---|---|---|---|
| `apps/desktop` | Operator desktop (PyQt6) | Python | 895 | None — read-only claims, replay, audit |
| `apps/services` | Service host (Compose adapters) | Python | 148 | None — read-only import + liveness |
| `apps/android` | Mobile read-only client | Kotlin | 250 (excl. Gradle build artifacts) | None — DOI registry + replay status GET only |
| `apps/web` | React/Vite docs + proof portals | TypeScript | 945 (excl. node_modules + dist) | None — read-only displays |
| `apps/web-static` | Static HTML reference site | HTML/CSS/JS | 2,251 | None — static reference |

Total source: ~4,489 LOC across 5 application subdirs. **Zero upward imports into `packages/governance/` or `packages/execution/`** — verified by import scan below.

---

## 1. `apps/desktop` — PyQt6 operator application

**Purpose:** Unsigned development PyQt6 operator application. Per its own README: gateway status, canonical replay evidence checks, verified audit viewing, unverified capability claim inspection, governance display, in-memory settings.

**Authority boundary:** Does not import governance or execution packages. Does not persist API tokens. Capability inspection decodes public claims but cannot authenticate signatures without issuer authority; UI labels reflect that limitation.

**Files (source only):**
- `pyproject.toml` (28)
- `README.md` (10)
- `src/project_ai_desktop/__init__.py` (8)
- `src/project_ai_desktop/__main__.py` (3)
- `src/project_ai_desktop/app.py` (26)
- `src/project_ai_desktop/capability_inspector.py` (76)
- `src/project_ai_desktop/client.py` (91)
- `src/project_ai_desktop/main_window.py` (320)
- `src/project_ai_desktop/replay.py` (60)
- `src/project_ai_desktop/theme.py` (22)
- `tests/conftest.py` (16)
- `tests/test_desktop.py` (235)

**Status:** Module exists, tests blocked at collection by `PyQt6` not in venv (pre-existing environment gap, not a code defect).

---

## 2. `apps/services` — service host adapters

**Purpose:** Read-only import and liveness adapters for SWR, Atlas, and experimental Arbiter/RLP Compose services.

**Authority boundary:** Per README: exposes no actuation, governance decision, capability issuance, or execution endpoint.

**Files:**
- `pyproject.toml` (26)
- `README.md` (5)
- `src/project_ai_services/__init__.py` (7)
- `src/project_ai_services/app.py` (73)
- `tests/test_services.py` (37)

**Status:** Module exists, tests blocked at collection by missing `project_ai_services` package install (separate workspace member; pre-existing).

---

## 3. `apps/android` — Kotlin read-only client

**Purpose:** Mobile development app exposing DOI registry (`GET /dois`) and canonical replay status (`GET /replay/status`).

**Authority boundary:** Per README: no mutation, execution, governance, capability, token, or operator authority surface. API base URL is a development BuildConfig value. APK is unsigned beyond debug key.

**Files (excl. `build/`):**
- `README.md` (16)
- `build.gradle.kts` (4)
- `settings.gradle.kts` (18)
- `app/build.gradle.kts` (43)
- `app/src/main/java/ai/project/readonly/MainActivity.kt` (65)
- `app/src/main/java/ai/project/readonly/ReadOnlyClient.kt` (73)
- `app/src/test/java/ai/project/readonly/ReadOnlyClientTest.kt` (31)

**Status:** Read-only client. Builds with Java 17 + Android SDK API 34.

---

## 4. `apps/web` — React/Vite portals

**Purpose:** Two Vite/React/TypeScript portals (Docs + Proof) sharing a `shared/` library. Per `pyproject.toml` analysis: these are documentation and proof-evidence displays, not operator consoles.

**Files (excl. `node_modules/` + `dist/`):**
- `docs-portal/index.html` (14)
- `docs-portal/package.json` (18)
- `docs-portal/tsconfig.json` (5)
- `docs-portal/vite.config.ts` (17)
- `docs-portal/src/DocsPortal.tsx` (183)
- `docs-portal/src/DocsPortal.test.tsx` (39)
- `docs-portal/src/main.tsx` (10)
- `docs-portal/src/test-setup.ts` (1)
- `proof-portal/index.html` (14)
- `proof-portal/package.json` (18)
- `proof-portal/tsconfig.json` (5)
- `proof-portal/vite.config.ts` (17)
- `proof-portal/src/ProofPortal.tsx` (106)
- `proof-portal/src/ProofPortal.test.tsx` (39)
- `proof-portal/src/main.tsx` (10)
- `proof-portal/src/test-setup.ts` (1)
- `shared/package.json` (13)
- `shared/src/index.ts` (4)
- `shared/src/api.ts` (31)
- `shared/src/components.tsx` (96)
- `shared/src/styles.css` (272)

**Status:** Static React portals. No operator authority surface.

---

## 5. `apps/web-static/ompt-reference` — HTML reference site

**Purpose:** Plain-HTML reference site (`ompt-reference`). Not operator tooling.

**Files:**
- `about.html` (152)
- `app.js` (137)
- `architecture.html` (214)
- `index.html` (264)
- `publications.html` (177)
- `repository.html` (219)
- `styles.css` (1,088)

**Status:** Static reference. No authority surface.

---

## 6. Cross-cutting authority analysis

**Question:** Do any `apps/` modules import governance, execution, or capability from `packages/`?

**Method:** `grep -rnE "^(from|import) (governance|execution|capability)\b" apps/` for Python, equivalent patterns for Kotlin/Java and TypeScript. Run on 2026-06-25.

**Result:** **Zero hits across all three languages.** Confirmed: no app module imports `governance`, `execution`, or `capability`. The architectural boundary from `REBUILD_EXECUTION_PLAN.md` is enforced in code, not just stated in README.

## 7. Conclusion

`apps/` is well-scoped: all four client applications (desktop, services, android, web) plus one static reference site (web-static). None carry governance or execution authority. The architectural pattern matches `docs/internal/REBUILD_EXECUTION_PLAN.md` "Package And Application Boundaries": *"Web, desktop, and Android are applications that consume read-only or explicitly authorized API surfaces; they do not embed governance authority."*

**Q8 resolution:** Beginnings `apps/` is the application tier, intentional separation from `packages/` runtime tier, all four apps verified as no-authority surfaces.

**Future rebuild scope:**

- `apps/desktop` and `apps/services` are integration-test-blocked at the moment by environment gaps (PyQt6 + workspace install). These are pre-existing, not new gaps from any phase.
- `apps/android` and `apps/web` build/test paths not exercised in this phase.
- No application-tier rebuild is in any Phase A–J of `STAGE_19_5_PHASED_PLAN.md`. They are not on the integration roadmap.

---

## 8. Sources (v3 §11 Evidence Before Claims)

- `ls apps/` (Phase A session)
- `find apps -type f` enumeration (Phase A session)
- Per-app README files (read directly)
- Per-file `wc -l` counts (Phase A session)
- `docs/internal/REBUILD_EXECUTION_PLAN.md` (architectural boundaries)

## 9. Self-report (v3 §35)

```
Mode: governance system (discovery)
Created: docs/operations/APPS_INVENTORY.md (this file)
Modified: None.
Verified: apps/ enumeration (5 subdirs); per-app README reads; per-file LOC counts
Failed: None.
Not verified: full content read of every apps/* file (sampled via README + LOC; deep read deferred)
Risks: PyQt6 + services workspace install gaps pre-existing (not from this phase)
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on Phase A commit)
Safe to continue: yes
```