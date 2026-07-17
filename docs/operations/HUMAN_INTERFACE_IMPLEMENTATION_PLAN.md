# Project-AI Human Interface Implementation Plan

**Status:** Implementation in progress; Phase 0/1/2 foundations and the first durable request/review slice are implemented  
**Date:** 2026-07-15  
**Mode:** Repository-wide product and interface plan  
**Repository:** `T:\00-Active\Project-AI-Beginnings`  
**Branch inspected:** `main`  
**Primary decision:** Build one canonical web Control Center and reuse it across browser and desktop delivery. Preserve the existing documentation and proof portals as separate read-only lanes. Keep Android a scoped companion client.  
**Authority boundary:** Human-interface permissions control access to interface features. They do not replace canonical actor identity, capability verification, governance verdicts, or the execution gate.

---

## 1. Outcome

The repository does not yet contain a complete human application. It contains several useful but separate surfaces:

- a React documentation portal;
- a React proof and audit portal;
- a PyQt6 read-only operator desktop;
- a minimal read-only Android client;
- a standalone Flask SWR dashboard;
- public/static reference and manifesto sites;
- a development FastAPI gateway with public reads and a shared bearer token for protected routes.

The planned outcome is a coherent Project-AI product with:

1. a real first-run and sign-in experience;
2. durable human accounts, sessions, roles, and step-up authentication;
3. a permission-aware application shell;
4. an operator command center;
5. evidence, audit, replay, security, governance, execution, capability, simulation, and system-health workflows;
6. administrative user, role, session, and security management;
7. consistent browser, desktop, tablet, and scoped mobile behavior;
8. contract-tested API integration;
9. accessible, responsive, observable, deployable, and rollback-safe delivery.

This document remains the implementation roadmap. The canonical console, dashboard/evidence routes, and local Owner account/session slice now exist; later screens, multi-user authorization, MFA, deployment, and production controls remain pending.

---

## 2. Evidence inspected

### 2.1 Current interface code

- `apps/web/shared/`
- `apps/web/docs-portal/`
- `apps/web/proof-portal/`
- `apps/web/triumvirate-portal/`
- `apps/web-static/ompt-reference/`
- `apps/desktop/`
- `apps/android/`
- `apps/swr-dashboard/`
- `apps/services/`

### 2.2 Current backend and authority code

- `packages/api/src/project_ai_api/app.py`
- `packages/api/src/project_ai_api/models.py`
- `packages/identity/`
- `packages/capability/`
- `packages/governance/`
- `packages/execution/`
- `packages/security/`
- `packages/cerberus/src/cerberus/security/modules/auth.py`
- `packages/cerberus/src/cerberus/security/modules/rbac.py`

### 2.3 Current operational surfaces

- `compose.yaml`
- `helm/project-ai/templates/ingress.yaml`
- `helm/project-ai/templates/portals.yaml`
- `helm/project-ai/values.yaml`
- `docs/operations/APPS_INVENTORY.md`
- `docs/api/API_REFERENCE.md`
- `docs/architecture.md`
- `docs/operator.md`
- `docs/operations/CONTINUITY_MAP.md`
- `docs/internal/REBUILD_EXECUTION_PLAN.md`

### 2.4 Live screens captured during this plan

The current React portals and SWR dashboard were run locally and visually inspected. Evidence was saved outside the repository at:

`C:\Users\Quencher\.codex\visualizations\2026\07\15\019f66ca-df58-7f70-9dbe-84ed249d9f79\interface-audit\`

Accepted captures:

1. `01-docs-overview.png`
2. `02-docs-architecture.png`
3. `03-docs-publications.png`
4. `04-proof-status.png`
5. `05-proof-audit-empty.png`
6. `06-swr-dashboard.png`

---

## 3. Current-state findings

### 3.1 What is already worth preserving

- The OMPT-derived dark visual language is coherent across the React portals and desktop theme.
- The portals use semantic headings, named navigation, status and error regions, keyboard-visible focus, responsive navigation, and explicit development-state wording.
- The proof portal correctly clears the bearer token after each audit request.
- The API distinguishes public and protected routes and fails closed when protected surfaces are not configured.
- The desktop client clearly states that it has no governance authority.
- The application tier is mostly separated from governance and execution packages.
- Compose and Helm already separate API, documentation, proof, and internal services.
- Windows installer work provides a viable local desktop distribution path.

### 3.2 Product gaps

- A canonical operator console, route shell, dashboard/evidence views, and local Owner authentication now exist; the remaining product modules do not.
- Bootstrap, login, logout, current-user, recovery-code reset, session rotation/revocation, and password-change routes exist. TOTP MFA and administrative account flows do not.
- The ordinary product UI uses a human session and never accepts `PROJECT_AI_API_TOKEN`; machine actuation routes remain separately bearer-protected.
- A migrated local SQLite account database exists. PostgreSQL deployment storage,
  one-time SQLite migration, concurrency controls, and dump/restore evidence are implemented.
- Cerberus `AuthManager` and `RBACManager` are in-memory primitives and are not wired into the gateway.
- The canonical `packages/identity` package intentionally models actor identity only; it has no credentials, roles, or human sessions.
- The Owner account stores an optional actor binding; binding administration and verification policy remain pending.
- The operator console now has route-based deep links. The legacy portals retain their existing navigation models.
- There is no notification, inbox, approval queue, assignment, or operator-task model.
- There is no command-center aggregation endpoint.
- Most system packages have no human-facing API surface.
- The standalone SWR dashboard is visually and architecturally separate from the React portals.
- Desktop, web, Android, and SWR duplicate presentation concepts without a shared information architecture.
- The Android client is two buttons and a text area, not an application navigation model.

### 3.3 Concrete defects and drift found during planning

These are current system issues. They are not fixed by this planning-only pass.

1. **Legacy authentication documents overclaim implementation.** Files such as `docs/architecture/visual-maps/data-flows/authentication.md`, `docs/source-docs/core/user_manager.md`, and `docs/source-docs/gui/login.md` describe missing runtime paths such as `src/app/core/user_manager.py`, `users.json`, JWT flows, and a completed login UI. Those paths do not exist in this repository.
2. **The API reference is stale.** It documents response shapes that disagree with `packages/api/src/project_ai_api/models.py`, including replay and audit shapes.
3. **The SWR console entrypoint fails on this Windows host.** Its emoji `print()` calls raise a `UnicodeEncodeError` under the active cp1252 console. The Flask app can run when launched without those prints.
4. **The SWR dashboard is not part of the deployed portal topology.** Compose and Helm expose an SWR service adapter, not `apps/swr-dashboard`.
5. **The SWR dashboard emits unescaped data through `innerHTML`.** Scenario or result data must be treated as untrusted before this UI is exposed beyond controlled local data.
6. **The portal hero scale is presentation-first.** It is effective for documentation but too large and low-density for a daily operator console.
7. **Protected audit access now accepts a human session.** Machine bearer access remains available for non-browser clients; human role-based field filtering and export controls are pending.
8. **Tests are narrow.** Current React tests cover a few successful and error states; there is no route, accessibility, end-to-end, visual-regression, role-matrix, or responsive test suite.
9. **Desktop licensing remains a distribution decision.** The existing PyQt6 dependency is GPL-3.0-only unless a commercial license is obtained; that affects any expanded distributed desktop interface.

---

## 4. Product boundaries

### 4.1 Canonical products

| Product | Purpose | Authentication | Authority |
|---|---|---|---|
| Public Documentation | Architecture, publications, operating concepts | None for public material | None |
| Public Proof | Public-safe health and replay claims | None for public material | None |
| Project-AI Control Center | Authenticated operator, reviewer, auditor, and administrator application | Human session | Requests and observes; never embeds governance authority |
| Desktop Delivery | Local installer, local gateway supervisor, and Control Center launcher/host | Local human session | Same Control Center boundary |
| Android Companion | Alerts, approvals assigned to the user, evidence summaries, and read-only system state | Device-bound session | No direct execution authority |
| Static Triumvirate/OMPT sites | Public narrative/reference material | None | None |

### 4.2 Explicitly separate concepts

- **Human account:** credentials, profile, session, UI roles, and interface permissions.
- **Canonical actor identity:** the active/inactive execution-spine identity in `packages/identity`.
- **Capability:** signed, scoped, expiring authority for an operation and resource.
- **Governance verdict:** `ALLOW`, `DENY`, or `ESCALATE` from the governance layer.
- **Execution:** the sole gated actuation path.

A human session may resolve to a verified actor identity. A UI role may allow the user to request an operation. Neither fact grants execution. The request must still pass identity, capability, governance, audit, and execution checks.

### 4.3 Recommended delivery architecture

Create `apps/web/operator-console` as the canonical interactive UI. Extend `apps/web/shared` into a real shared design and data-contract package. Keep `docs-portal` and `proof-portal` as separate builds that reuse the shared design system.

Desktop should initially:

1. continue supervising the bundled local API;
2. start or serve the built Control Center locally;
3. open the Control Center in the system browser;
4. retain the current native read-only screens as a recovery/fallback surface.

Embedding a web view is optional and should follow the PyQt licensing/distribution decision. Do not build a second full native implementation of every screen.

Android should consume the same OpenAPI contracts but implement a deliberately smaller mobile information architecture.

---

## 5. Human roles and permission model

### 5.1 Initial roles

| Role | Primary use | Examples of allowed UI actions |
|---|---|---|
| Owner | Initial local authority and break-glass administrator | All account/admin settings; may request governed operations |
| Administrator | Account and deployment administration | Users, roles, sessions, integrations, system configuration |
| Operator | Day-to-day system operation | View command center, initiate permitted requests, inspect results |
| Reviewer | Human review for escalated work | View assigned reviews, approve/reject within assigned policy |
| Auditor | Independent evidence review | Audit, replay, proof, exports, read-only security views |
| Analyst | Scenarios, projections, reports, and knowledge | SWR, Atlas, simulations, publications, exports |
| Viewer | General read-only access | Approved dashboards and documentation |

`guardian` may remain a machine/agent role in Cerberus RBAC. It should not automatically become a human account role.

### 5.2 Permission families

- `dashboard.view`
- `inbox.view`, `inbox.assign`
- `governance.view`, `governance.review`
- `execution.request`, `execution.view`
- `capability.view`, `capability.request`, `capability.revoke`
- `audit.view`, `audit.export`
- `security.view`, `security.manage`
- `swr.view`, `swr.request_run`
- `atlas.view`, `atlas.request_projection`
- `taar.view`, `taar.request_task`
- `companion.view`, `companion.manage_own`
- `knowledge.view`, `knowledge.manage`
- `system.view`, `system.configure`
- `accounts.view`, `accounts.manage`
- `roles.view`, `roles.manage`
- `sessions.view_own`, `sessions.revoke_own`, `sessions.manage_all`

### 5.3 Permission rules

- Deny by default.
- Server-side enforcement is mandatory; hidden controls are not authorization.
- Every denied request returns a stable machine code and a safe human explanation.
- High-impact actions require step-up authentication and explicit confirmation.
- Role changes, session revocations, capability requests, and security settings are audited.
- The Owner role cannot bypass governance or execution gates.
- Break-glass access must be time-limited, reason-bound, separately audited, and disabled by default.

---

## 6. Authentication and account architecture

### 6.1 New account boundary

Do not overload `packages/identity`, because that package intentionally represents canonical execution actors. Add a durable human-account package, recommended name:

`packages/accounts/`

It should own:

- accounts and credential records;
- role and permission assignments;
- server-side sessions;
- MFA factors and recovery codes;
- account lockout and rate-limit state;
- account-to-actor bindings;
- security event emission;
- storage interfaces and migrations.

Cerberus `PasswordHasher`, password policy, lockout behavior, and RBAC concepts may be reused after review. The in-memory Cerberus managers are not themselves the production account store.

### 6.2 Storage

- SQLite for bundled single-node desktop/local development.
- PostgreSQL for multi-user/container/Kubernetes deployment.
- One repository/storage interface with the same behavior in both modes.
- Alembic or an equivalent deterministic migration system.
- Encrypted sensitive fields where applicable.
- No plaintext passwords, MFA seeds, recovery codes, or session tokens.
- Backup, restore, migration rollback, and corrupted-store behavior must be documented and tested.

### 6.3 Browser sessions

Use opaque random server-side sessions in cookies:

- `HttpOnly`
- `Secure` outside explicit loopback development
- `SameSite=Lax` or stricter
- short idle timeout plus absolute timeout
- rotation on login, privilege elevation, and password change
- CSRF protection on state-changing requests
- session revocation and device listing

Do not store bearer tokens or JWTs in browser local storage.

### 6.4 Desktop and mobile sessions

- Desktop: use the loopback-bound browser session where possible. If a native handoff token is needed, make it one-time, short-lived, audience-bound, and exchange it for a server-side session.
- Android: use Authorization Code + PKCE against the same account service or a device-code flow for local deployments. Store refresh material only in Android Keystore-backed storage.
- Machine/API tokens remain separate from human sessions and are never entered into the ordinary login form.

### 6.5 First-run bootstrap

No public self-registration by default.

1. System starts in `bootstrap_required` state only when no account exists.
2. Bootstrap is accepted only from loopback or a separately configured trusted setup network.
3. A one-time setup secret is printed to local operator output or written to a protected file.
4. The user creates the Owner account and downloads recovery codes.
5. Bootstrap endpoint permanently disables itself after success.
6. Reopening bootstrap requires an explicit offline/admin recovery procedure.

### 6.6 Required authentication flows

- First-run Owner setup
- Sign in
- Sign out
- Session expired
- Account locked or disabled
- Password change
- Forgot/recover access
- MFA enrollment
- MFA challenge
- Recovery-code challenge
- Step-up authentication
- View and revoke sessions/devices
- Administrator password reset without learning the password
- Account invitation when multi-user mode is enabled
- Account deactivation and actor-binding removal

### 6.7 Authentication API surface

Recommended versioned routes:

- `GET /api/v1/auth/bootstrap-status`
- `POST /api/v1/auth/bootstrap`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/challenge`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/session`
- `POST /api/v1/auth/session/refresh`
- `GET /api/v1/auth/sessions`
- `DELETE /api/v1/auth/sessions/{session_id}`
- `POST /api/v1/auth/password/change`
- `POST /api/v1/auth/recovery/start`
- `POST /api/v1/auth/recovery/complete`
- `POST /api/v1/auth/step-up`
- `GET /api/v1/me`

Responses must not reveal whether an unknown username exists. Rate limits must account for both credential stuffing and attacker-induced account denial of service.

---

## 7. Information architecture

### 7.1 Public navigation

- Overview
- Architecture
- Publications
- Proof status
- Public replay evidence
- Trust and transparency
- Documentation
- Sign in

### 7.2 Authenticated navigation

1. **Home**
   - Command Center
   - My Inbox
   - Notifications
2. **Governance**
   - Decisions
   - Escalations
   - Execution Requests
   - Capabilities
3. **Evidence**
   - Audit Explorer
   - Replay & Proof
   - Security Events
   - Evidence Exports
4. **Operations**
   - Sovereign War Room
   - Atlas
   - Simulations
   - TAAR
   - Companion / Caretaker
5. **Knowledge**
   - Publications
   - Corpus Search
   - Architecture & Docs
6. **System**
   - Services & Health
   - Jobs & Schedules
   - Deployment State
7. **Administration**
   - Users
   - Roles & Permissions
   - Sessions
   - Security Settings
   - Integrations
8. **Personal**
   - Profile
   - Security
   - Preferences
   - Help / About

Navigation is filtered by permission, but direct route access must also be enforced by the server.

---

## 8. Complete screen inventory

### 8.1 Entry and authentication

| Screen | Required states and behaviors |
|---|---|
| Startup/connection check | Connecting, API unavailable, incompatible API version, maintenance, retry, diagnostics link |
| First-run setup | Setup-secret verification, Owner details, password policy, MFA/recovery codes, success, irreversible bootstrap-close notice |
| Sign in | Username/email, password, show/hide, remember-device policy, loading, invalid credentials, lockout, disabled account |
| MFA challenge | TOTP/passkey/recovery method, resend or alternate method when available, attempt limits |
| Recovery | Local recovery-code or administrator workflow; no fake email flow when email is not configured |
| Session expired | Preserve safe return path, discard sensitive unsaved operations, sign in again |
| Access denied | Explain missing permission without leaking restricted data; link to request-access process if implemented |

### 8.2 Global application shell

| Surface | Required behaviors |
|---|---|
| Sidebar | Permission-aware groups, collapse, keyboard operation, active-route indication |
| Top bar | Environment, global search/command palette, connection state, notifications, profile menu |
| Breadcrumbs | Route hierarchy and back navigation |
| Environment banner | Development/staging/production and local/remote labels; never color-only |
| Global status | Online, degraded, offline, stale-data, audit-integrity-failed states |
| Notification center | Read/unread, severity, source, assignment, deep link, dismissal policy |
| Command palette | Navigate, search records, start allowed workflows; never bypass confirmation or authorization |

### 8.3 Command Center

The landing dashboard should answer five questions in one viewport:

1. Is the system healthy?
2. Is evidence integrity valid?
3. What needs my attention?
4. What changed recently?
5. What can I safely do next?

Widgets:

- overall system state;
- gateway and service health;
- replay state and last verification;
- audit-chain integrity and latest record;
- open escalations and assigned reviews;
- pending/failed execution requests;
- active capabilities nearing expiry;
- Chimera denials/canary events;
- current SWR run/result summary;
- scheduled jobs and recent failures;
- recent operator activity;
- explicit stale-data timestamps.

Every widget links to a detailed screen and has loading, empty, error, stale, and permission-denied states.

### 8.4 My Inbox and reviews

- Assigned escalations
- Review due/age/severity
- Requester, actor, operation, resource, policy version, evidence links
- Approve, reject, return for information, abstain where policy permits
- Required rationale
- Step-up authentication for consequential decisions
- Conflict-of-interest and self-approval checks
- Immutable decision receipt
- No client-side-only approval state

### 8.5 Governance decisions

- Decision list with ALLOW/DENY/ESCALATE filters
- Decision detail timeline
- Input normalization
- Governor results and vetoes
- Policy and invariant versions
- Capability check result
- Execution result or explicit non-execution
- Related audit records
- Replay/reconstruction link
- Redaction rules for restricted evidence
- Export with provenance

### 8.6 Execution requests

- Request composer driven by server-provided operation schema
- Actor, operation, resource, payload, capability, and risk preview
- Dry-run/validation when the backend supports it
- Confirmation showing exact intended effect
- Pending, denied, escalated, allowed-not-executed, executed, failed, and rolled-back states
- Idempotency key and duplicate-submission protection
- Execution receipt with audit hash

The UI must never display `ALLOW` as equivalent to `EXECUTED`.

### 8.7 Capabilities

- Capability list and filters
- Verified/unverified/expired/revoked status
- Subject, issuer, operation, resource, issue/expiry times
- Detail screen with signature verification result from the authority service
- Request capability workflow
- Revoke workflow with reason and step-up authentication
- Expiry alerts
- Copy controls that warn about secret handling
- Never imply that the current desktop decoder verifies signatures

### 8.8 Audit Explorer

- Server-side pagination and stable cursor
- Event, actor, account, operation, resource, verdict, severity, and time filters
- Hash, previous hash, and chain segment status
- Record detail with normalized fields and safe raw JSON
- Chain verification action and result
- Integrity-failure lockdown presentation
- Export manifest with query, timestamp, count, and digest
- Redaction and permission-aware field visibility
- No rendering through unescaped HTML

### 8.9 Replay and Proof

- Current replay status
- Last run, duration, code/data version, and invariant counts
- Per-invariant results
- Run history
- Trigger replay request for permitted operators
- Compare two runs
- Evidence bundle link
- Public-safe view separated from authenticated detail
- `not_run`, `running`, `pass`, `fail`, `stale`, and `unavailable` states

### 8.10 Security and Chimera

- Denials, canary hits, threat classifications, containment state
- Severity and time trends with accessible tabular alternatives
- Incident detail timeline
- Related actors, requests, evidence, and affected services
- Acknowledge/assign/resolve workflows where backed by real server state
- Lockdown status and explicit recovery authority
- No decorative "secure" claims without evidence

### 8.11 Sovereign War Room

Replace the standalone template with Control Center routes:

- SWR overview
- Scenario catalog
- Scenario detail
- Run request
- Run progress
- Results list
- Result detail
- System leaderboard
- Per-system performance
- Cryptographic proof detail
- Comparison view

Preserve deterministic/governed execution. Load and run actions must use real API routes and the execution gate. Remove direct `innerHTML` record rendering.

### 8.12 Atlas

- Implemented: authenticated Atlas Replay workspace at `/simulations/atlas-replay`
- Implemented: bounded JSON bundle input, canonical verification, deterministic
  reconstruction summary, five evidence counts, and copyable SHA-256 values
- Implemented: dedicated analysis-run permission, CSRF/same-origin enforcement,
  256 KB request ceiling, fail-closed audit verification, and bounded audit receipt
- Implemented: desktop and narrow responsive layouts with automated accessibility coverage
- Implemented: authenticated Atlas Projections workspace at `/simulations/atlas-projections`
- Implemented: canonical claim/evidence/driver form, deterministic result, idempotent
  creation, durable history and expanded receipt detail across SQLite and PostgreSQL
- Implemented: input/output/projection/audit SHA-256 evidence with raw claim and evidence
  content excluded from the append-only audit relay
- Subordination/analysis-only notice on every relevant screen
- Service status
- Implemented: projection request
- Implemented: projection history and detail
- Sludge sandbox with mandatory fiction banner and contamination controls
- Source snapshot digest
- Export with watermark and provenance
- Never present an Atlas projection as an authoritative verdict

### 8.13 Simulations

- Engine catalog: AI takeover, alien invaders, cognitive warfare, Django state, EMP defense, global scenario, Hydra, and future registered engines
- Maturity, risk, dependencies, supported inputs, and authority boundary
- Run request based on a shared simulation contract
- Progress and cancellation when supported
- Results, comparisons, evidence, and export
- Clear experimental/development labeling

### 8.14 TAAR

- Task definition
- Target repository/scope confirmation
- Agent/reader selection
- Report-only boundary
- Run status
- Hash-sealed evidence bundle
- Append-only audit trail
- Findings and export
- No mutation controls unless the TAAR authority model is explicitly changed and governed

### 8.15 Companion / Caretaker

- Session list and status
- Conversation/workspace view only after privacy review
- Governed memory scopes and provenance
- Revision history
- Model/inference status
- Policy/constitution version
- Export/delete workflows only when real backend authority exists
- Clear distinction between Caretaker's self-governance and canonical Project-AI governance

### 8.16 Knowledge, publications, and docs

- Preserve DOI search and domain filters
- Add meaningful paper titles/abstract metadata when source data supports it
- Corpus search with source, digest, and provenance
- Architecture explorer
- API reference generated from OpenAPI
- Operator runbooks
- Cross-links from runtime records to supporting documentation
- Public and internal visibility labels

### 8.17 System health and operations

- API and adapter service health
- Version/build/commit information
- Dependency compatibility
- Storage and audit availability
- Background job status
- Compose/Kubernetes deployment identity
- Health history and SLO state
- Diagnostics export with secret redaction
- Restart/configure buttons only if a governed backend operation exists

### 8.18 Administration

- User list/detail/create/invite/deactivate
- Actor binding and binding status
- Role list/detail/create/edit
- Permission matrix
- Active sessions and device revocation
- MFA enforcement policy
- Password/session policy
- API/service tokens in a separate machine-credentials area
- Audit retention and export policy
- Integration settings
- Environment configuration with secret-safe editing

### 8.19 Personal settings

- Profile
- Password
- MFA and recovery codes
- Active sessions
- Notification preferences
- Theme, density, time zone, locale, reduced motion
- Default landing page
- Sign out

---

## 9. Shared interaction and state rules

Every data screen must define:

- initial loading;
- background refresh;
- empty state;
- partial/degraded data;
- stale data;
- offline state;
- permission denied;
- record not found;
- validation error;
- server error with correlation ID;
- integrity failure;
- optimistic-update policy or explicit no-optimism policy;
- retry behavior;
- last-updated time;
- export/print behavior where applicable.

High-consequence operations should not use optimistic success. Show pending until the server returns a durable receipt.

### 9.1 Confirmation levels

1. **No confirmation:** navigation, filtering, safe reads.
2. **Simple confirmation:** reversible preference changes.
3. **Reason-required confirmation:** review decisions, revocations, incident resolution.
4. **Step-up plus exact-effect confirmation:** account privilege changes, capability revocation, system configuration, consequential execution request.

### 9.2 Status language

Use canonical, non-overlapping labels:

- Requested
- Validating
- DENY
- ESCALATE
- ALLOW
- Authorized
- Executing
- Executed
- Failed
- Rolled back
- Not verified
- Stale

Never collapse these into a generic green "Success."

---

## 10. API and data-contract work

### 10.1 Versioning and generation

- Introduce `/api/v1` for the human application.
- Keep existing development routes temporarily for compatibility.
- Generate an OpenAPI artifact in CI.
- Generate TypeScript and Kotlin clients from the accepted schema or verify hand-written clients against it.
- Add schema-drift tests between Pydantic models, documentation examples, TypeScript types, Kotlin models, and fixtures.
- Use stable error codes in addition to safe human messages.

### 10.2 Required aggregation routes

- `GET /api/v1/dashboard`
- `GET /api/v1/navigation`
- `GET /api/v1/notifications`
- `GET /api/v1/inbox`
- `GET /api/v1/system/services`
- `GET /api/v1/system/version`
- `GET /api/v1/system/events` via SSE where justified

Avoid making the browser fan out to dozens of services for the landing page. The API should aggregate authorized, redacted view models.

### 10.3 Domain route groups

- `/api/v1/governance/*`
- `/api/v1/execution/*`
- `/api/v1/capabilities/*`
- `/api/v1/audit/*`
- `/api/v1/replay/*`
- `/api/v1/security/*`
- `/api/v1/swr/*`
- `/api/v1/atlas/*`
- `/api/v1/simulations/*`
- `/api/v1/taar/*`
- `/api/v1/companion/*`
- `/api/v1/knowledge/*`
- `/api/v1/admin/*`

Only implement a group when the backing package exposes a truthful, tested operation.

### 10.4 Event updates

Use server-sent events for read-only progress, notification, and health updates unless bidirectional WebSockets are genuinely required. Requirements:

- authenticated connection;
- permission-filtered events;
- reconnection with last-event ID;
- bounded retention;
- heartbeat;
- polling fallback;
- no secrets in event payloads.

---

## 11. Design system

### 11.1 Preserve

- Deep slate/black canvas
- Cool blue authority accents
- Amber evidence/risk accent
- Monospace labels for hashes, routes, and evidence IDs
- Existing OMPT texture only where it does not reduce readability
- Lucide icon family
- Explicit status pills and boundary notices

### 11.2 Add

- Semantic color tokens for info/success/warning/danger/unknown/stale
- Typography scale suitable for dense operations, not only marketing heroes
- 4/8px spacing system
- Compact, comfortable, and spacious density modes
- Table, data grid, pagination, filter bar, timeline, drawer, modal, toast, banner, chart, code, JSON, and empty-state components
- Form field, validation, password, OTP, recovery-code, confirmation, and step-up components
- Skeletons that preserve layout
- Accessible chart palette and required table alternative
- Tokens shared with desktop where practical

### 11.3 Recommended web dependencies

Keep dependencies conservative. Add only after a focused evaluation:

- React Router for real routes and deep links
- TanStack Query for server state
- TanStack Table for complex tables
- React Hook Form plus schema validation
- a tested accessible primitive library if the team does not implement primitives directly
- Playwright for end-to-end and screenshot testing
- axe-core integration for automated accessibility checks

The plan does not require replacing React/Vite or introducing a large UI framework.

---

## 12. Accessibility requirements

Target WCAG 2.2 AA.

- Complete keyboard access and logical focus order
- Skip links and landmarks
- Visible focus not dependent on browser defaults alone
- 44px minimum touch targets where applicable
- Text and non-text contrast checks
- Status not conveyed by color alone
- Proper names and descriptions for every control
- Error summary plus field-level errors
- Focus management after navigation, modal open/close, and failed submission
- Screen-reader announcements for async updates without excessive noise
- Reduced-motion support
- 200% zoom and text resize without content loss
- Reflow at 320 CSS pixels for supported mobile screens
- Accessible tables and sortable-header announcements
- Chart summaries and underlying data tables
- Copyable hashes with full accessible values
- Password-manager-compatible fields
- Passkey and OTP flows tested with platform assistive technology
- Manual testing with NVDA on Windows and TalkBack on Android before release

Automated checks are necessary but not sufficient for an accessibility claim.

---

## 13. Responsive strategy

### Desktop, 1280px and above

- Persistent sidebar
- Multi-column command center
- Table plus detail drawer
- Dense evidence views

### Tablet, 768px to 1279px

- Collapsible sidebar
- Two-column dashboards where space permits
- Full-screen detail drawers

### Narrow web, 320px to 767px

- Bottom sheet or drawer navigation
- Single-column cards
- Replace wide tables with prioritized cards or horizontally scrollable, clearly labeled tables
- Restrict high-complexity authoring workflows where they cannot be made safe

### Android

- Home/status
- Notifications/inbox
- Assigned review summary and safe review actions only after mobile threat modeling
- Evidence/replay summaries
- DOI/knowledge search
- Profile/session security

Do not attempt one-to-one desktop screen parity on Android.

---

## 14. Security requirements

- Threat-model account, session, review, execution-request, audit-export, and recovery flows before implementation.
- No shared machine token in the normal UI.
- CSRF protection for cookie-authenticated writes.
- Strict Content Security Policy without unsafe inline scripts.
- Output encoding everywhere; no record-driven `innerHTML`.
- Same-origin deployment or explicit reviewed CORS allowlist.
- Rate limits for login, recovery, MFA, export, and consequential actions.
- Step-up authentication for privilege and authority-sensitive workflows.
- Server-side permission checks on every route.
- Resource-level authorization, not only route-level roles.
- Secure session rotation and revocation.
- Secret redaction in diagnostics, errors, logs, telemetry, and exports.
- Safe file names and bounded sizes for exports/uploads.
- Audit all authentication, authorization, account, role, review, and session events.
- Fail closed when account storage, audit, capability, governance, or required policy is unavailable.
- Prevent clickjacking with frame policy.
- Set HSTS in TLS deployments.
- Dependency, license, SAST, and container scanning in CI.
- Independent security review before any internet exposure.

---

## 15. Testing strategy

### 15.1 Component tests

- Every shared component and state
- Keyboard interaction
- Form validation
- Status semantics
- Permission-gated rendering
- Error and stale-data states

### 15.2 API contract tests

- OpenAPI matches Pydantic runtime behavior
- Generated clients compile
- TypeScript/Kotlin fixtures match server models
- Stable error codes
- Pagination and event-stream behavior

### 15.3 Integration tests

- Account repository and migrations
- Login, logout, expiry, lockout, MFA, recovery, and session revocation
- Role and resource authorization matrix
- Account-to-actor binding
- Capability/governance/execution separation
- Audit records for every consequential flow

### 15.4 End-to-end tests

Required browser journeys:

1. First-run Owner bootstrap
2. Successful and failed login
3. MFA and recovery code
4. Session expiry and return path
5. Viewer denied from operator/admin routes
6. Operator command-center triage
7. Reviewer processes an ESCALATE item
8. Execution request reaches each canonical terminal state
9. Audit filtering and verified export
10. Replay run and evidence detail
11. SWR scenario through result detail
12. Admin creates/deactivates an account and revokes sessions
13. Offline/degraded gateway recovery
14. Integrity-failure lockdown presentation

### 15.5 Visual and accessibility tests

- Screenshot baselines at desktop, tablet, and narrow widths
- High contrast and reduced motion
- Automated axe checks on every route
- Manual NVDA and TalkBack passes
- 200% zoom and keyboard-only acceptance

### 15.6 Security tests

- CSRF
- session fixation
- session replay
- cookie flags
- brute force and lockout abuse
- authorization bypass
- IDOR/resource scoping
- stored/reflected XSS
- malicious audit/scenario strings
- privilege escalation
- stale step-up token reuse
- export injection
- secret leakage
- fail-closed dependency outages

---

## 16. Deployment and operations work

### 16.1 Compose

- Add `operator-console` service.
- Add durable account storage volume or PostgreSQL service according to mode.
- Add reverse proxy path for `/app` and `/api`.
- Keep `/docs` and `/proof` independent.
- Configure session, CSRF, encryption, and bootstrap secrets through secret-safe mechanisms.
- Add health/readiness checks that distinguish liveness from dependency readiness.

### 16.2 Helm

- Add Control Center Deployment and Service.
- Add `/app` ingress path.
- Add account database configuration and secrets.
- Add network policies for console-to-API and API-to-database only.
- Add PodDisruptionBudget and persistence/backup requirements for account state.
- Add TLS and cookie-security acceptance checks.

### 16.3 Desktop installer

- Bundle the production Control Center assets.
- Serve them from the bundled loopback API or a dedicated loopback static server.
- Open the exact loopback URL after the supervisor proves readiness.
- Preserve the local API token as an internal service credential; do not expose it to browser JavaScript.
- Add clean shutdown for UI server and API child processes.
- Add install/launch/sign-in/uninstall smoke coverage.
- Resolve PyQt licensing before distribution under incompatible terms.

### 16.4 Observability

- Structured server logs with request and correlation IDs
- Authentication and authorization metrics without usernames/passwords/tokens
- Route latency and failure rates
- Frontend error boundary reporting with privacy-safe context
- Session counts and revocation metrics
- Accessibility and performance budgets in CI
- SLOs for login, dashboard, audit search, and consequential request submission

### 16.5 Backup and recovery

- Account database backup and verified restore
- Recovery-code regeneration
- Session invalidation after restore when appropriate
- Audit-store continuity and integrity verification
- Documented rollback for schema and application releases
- Desktop local-data backup/export path

---

## 17. Recommended repository changes

```text
apps/
  web/
    operator-console/
      src/
        app/
        routes/
        features/
        layouts/
        tests/
    shared/
      src/
        api/
        components/
        design-tokens/
        hooks/
        security/
  desktop/
    # supervisor + native fallback + Control Center launcher
  android/
    # scoped companion routes

packages/
  accounts/
    src/accounts/
      models.py
      password.py
      permissions.py
      repository.py
      service.py
      sessions.py
      mfa.py
      recovery.py
      actor_binding.py
    migrations/
    tests/
  api/
    src/project_ai_api/
      routers/
        auth.py
        dashboard.py
        governance.py
        execution.py
        capabilities.py
        audit.py
        replay.py
        security.py
        swr.py
        atlas.py
        simulations.py
        taar.py
        companion.py
        knowledge.py
        admin.py
      dependencies/
      errors.py
      events.py

docs/
  product/
    INFORMATION_ARCHITECTURE.md
    ROLE_PERMISSION_MATRIX.md
    SCREEN_ACCEPTANCE.md
  security/
    HUMAN_AUTH_THREAT_MODEL.md
  operations/
    HUMAN_INTERFACE_IMPLEMENTATION_PLAN.md
    HUMAN_INTERFACE_RELEASE_CHECKLIST.md
```

Do not create all route modules as empty scaffolds. Add each only with a real backing workflow and tests.

---

## 18. Phased execution plan

### Phase 0 — Truth and decisions

**Work**

- Correct or clearly archive stale authentication and API documentation.
- Generate and freeze the current OpenAPI baseline.
- Record the human-account versus actor-identity boundary.
- Decide desktop browser-launch versus embedded-webview delivery.
- Decide SQLite-only local mode plus PostgreSQL deployed mode.
- Resolve PyQt distribution licensing direction.
- Write the role/permission matrix and auth threat model.

**Acceptance**

- No active document claims missing login/JWT/user-manager behavior exists.
- Runtime models and API reference agree.
- Architecture decision records identify every selected boundary.

### Phase 1 — UI foundation

**Work**

- Create `operator-console` with route-based navigation.
- Split shared styles into tokens and components.
- Add app shell, route guards, error boundary, query client, form foundation, and test harness.
- Add Storybook or an equivalent local component catalog only if it is maintained in CI.
- Add accessibility and screenshot-test infrastructure.

**Acceptance**

- Deep links and refresh work on every foundation route.
- Keyboard, narrow viewport, and automated accessibility foundation tests pass.
- Docs and proof portals still build and retain their current behavior.

### Phase 2 — Human accounts and sessions

**Work**

- Implement `packages/accounts` and persistence/migrations.
- Add bootstrap, login, logout, session, password, lockout, MFA, recovery, and account-to-actor binding.
- Add server-side role/resource enforcement and security-event audit.
- Implement all entry/authentication screens.

**Acceptance**

- Auth matrix and negative tests pass.
- No browser-readable machine token.
- Session fixation, CSRF, expiry, revocation, lockout, and recovery tests pass.
- Bootstrap cannot be reused.

### Phase 3 — Shell, Command Center, Inbox

**Work**

- Implement permission-aware navigation, profile, notification center, environment banner, and global status.
- Add dashboard, navigation, inbox, and notification APIs.
- Implement Command Center and My Inbox.

**Acceptance**

- Each role sees only its allowed navigation and server-authorized data.
- Dashboard handles healthy, degraded, offline, stale, empty, and partial states.
- Assigned review deep links work.

### Phase 4 — Evidence and governance

**Work**

- Audit Explorer
- Replay and Proof
- Governance Decisions
- Security/Chimera
- Capability views and verified detail
- Execution request and receipt views

**Acceptance**

- ALLOW, authorization, execution, and audit are visibly distinct.
- Integrity failure locks down evidence-dependent workflows.
- Exports include provenance and digest.
- Consequential actions require reason, exact-effect confirmation, and step-up as specified.

### Phase 5 — Operational modules

**Work**

- Migrate SWR into React/API routes.
- Add Atlas, simulation catalog/runs, TAAR, and selected Companion/Caretaker views.
- Add server-provided operation/input schemas.

**Acceptance**

- Every mutation routes through a real governed backend operation.
- Experimental and analysis-only boundaries are visible.
- Malicious scenario/result strings cannot execute in the browser.
- Run progress, cancellation support, receipts, and terminal states are truthful.

### Phase 6 — Administration and settings

**Work**

- User, role, permission, session, security-policy, integration, profile, MFA, and preference screens.
- Machine credentials in a separate protected area.

**Acceptance**

- Role changes take effect consistently and are audited.
- Deactivation revokes sessions and prevents new access.
- Administrators cannot retrieve passwords, MFA seeds, recovery codes, or raw session tokens.

### Phase 7 — Desktop delivery

**Work**

- Bundle and launch the Control Center.
- Preserve native fallback/diagnostic screens.
- Add loopback bootstrap/session handoff.
- Extend installer smoke tests.

**Acceptance**

- Fresh install to first-run Owner setup works without cloning the repo.
- No secret appears in URL, logs, process arguments, or browser storage.
- Graceful close stops child processes.
- Upgrade and uninstall preserve/remove user data according to an explicit policy.

### Phase 8 — Android companion

**Work**

- Adopt generated API models.
- Implement device sign-in, status, notifications/inbox, evidence summaries, publications, and personal session security.
- Add offline cache with sensitivity-aware storage.

**Acceptance**

- Keystore-backed credentials.
- No cleartext traffic outside explicit emulator development.
- Lost-device session revocation works.
- Read-only boundary remains unless separately threat-modeled and approved.

### Phase 9 — Hardening and release gate

**Work**

- Full security review
- Accessibility audit
- Performance/load testing
- Backup/restore and rollback drills
- Compose, Helm, installer, and CI integration
- Documentation and support runbooks

**Acceptance**

- All role, auth, E2E, accessibility, visual, contract, security, build, deployment, and rollback gates pass.
- No unresolved P0/P1 interface or authentication defect.
- Continuity and release evidence match the exact built commit.

---

## 19. Dependency order

```text
Truth/docs + architecture decisions
  -> shared UI foundation + OpenAPI discipline
    -> human accounts + sessions + permissions
      -> shell + dashboard + inbox
        -> governance/evidence/security workflows
          -> SWR/Atlas/simulations/TAAR/companion workflows
            -> administration
              -> desktop delivery
                -> Android companion
                  -> hardening and release evidence
```

Do not begin consequential operator buttons before the backing API, authorization, audit, and execution receipt contracts exist.

---

## 20. Definition of done for each screen

A screen is complete only when all applicable items are true:

- Real route and deep link
- Server-side permission enforcement
- Loading, empty, error, offline, stale, and forbidden states
- Responsive behavior
- Keyboard and screen-reader behavior
- Automated component tests
- API contract test
- End-to-end happy and negative paths
- Visual baseline
- Safe telemetry and correlation ID
- No secret exposure
- Documentation and help text
- Acceptance criteria tied to runtime evidence
- Continuity map updated

Mock-only cards, disabled buttons without a backing issue, and static status claims do not count as completed screens.

---

## 21. Immediate first implementation slice

The smallest useful, reversible implementation slice is:

1. Phase 0 documentation/API truth corrections.
2. `operator-console` route shell using the existing OMPT design language.
3. Read-only Command Center backed by a new `/api/v1/dashboard` aggregator.
4. Route-based migrations of the existing public status, replay, DOI, and protected audit views.
5. Test harness for routing, responsive layouts, accessibility, and API contract drift.

Do not label this slice a complete application. Human login should follow as Phase 2 and must replace the shared-token audit experience before multi-user or internet-facing use.

---

## 22. Decisions still requiring the user's authority

Implementation can begin with the recommended defaults, but these decisions affect later delivery:

1. **Desktop presentation:** open the canonical console in the system browser (recommended) or embed it in a desktop webview.
2. **Distribution license:** obtain commercial PyQt licensing, distribute under compatible terms, or replace the desktop toolkit.
3. **Multi-user scope:** local single-owner first (recommended) or multi-user from the first account release.
4. **MFA baseline:** TOTP + recovery codes first (recommended), with passkeys in a later slice, or passkeys from the first release.
5. **External identity:** no OAuth/OIDC initially (recommended) or support a named provider.
6. **Mobile authority:** keep Android read-only (recommended) or allow defined review actions after a dedicated mobile threat model.

None of these decisions should delay Phase 0 truth correction or Phase 1 UI foundation.

---

## 23. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Human roles get confused with execution authority | UI could imply or create bypasses | Keep accounts, actor identity, capability, governance, and execution as separate enforced layers |
| Parallel web/desktop implementations diverge | Duplicate defects and inconsistent controls | One canonical web console; desktop as delivery shell/fallback |
| Legacy docs drive implementation | False security and incompatible contracts | Correct/archive stale docs before account work |
| Shared bearer token survives into product UI | No accountability or revocation per user | Replace with server-side human sessions; isolate machine credentials |
| Large dashboard becomes decorative | Operators miss urgent work | Attention-first hierarchy, assignments, timestamps, deep links, density modes |
| Experimental packages appear authoritative | Misleading product claims | Persistent maturity and authority labels from server metadata |
| Audit data leaks secrets | Security exposure | Field-level permissions, redaction, safe raw view, export review |
| Mobile expands authority too early | Higher credential and approval risk | Read-only default and separate threat model |
| PyQt licensing blocks distribution | Desktop release cannot proceed as planned | Decide license/toolkit before expanding native UI |
| API growth bypasses contract discipline | Client drift and false displays | Versioned OpenAPI, generated/verified clients, CI drift gate |

---

## 24. Planning completion state

**Implementation in progress:** The Phase 0/1 foundation now includes a canonical React operator console, responsive application shell, `/command-center`, `/evidence`, and `/evidence/audit` routes, a truthful dashboard aggregation API, a frozen OpenAPI baseline, shared typed API access, automated UI/API tests, and a generated visual reference. The console exposes only implemented routes; future modules are visibly marked as planned.  
**Not ready:** managed PostgreSQL TLS/credential rotation and live-cluster restore drills, full audit filter coverage and redacted bulk export, durable notification history, global record search, additional deep module workflows, desktop/mobile integration, and production accessibility/security acceptance remain incomplete. The current audit explorer provides verified offset pagination, bounded query/event filtering, and JSON export of the displayed page. The shell provides keyboard screen search, live submitted-request notifications, and explicitly browser-local density/reduced-motion preferences. Axe-core automation now covers sign-in, Command Center, request detail, the SWR execution receipt, Atlas Replay, and Atlas Projections. Full-route automation, rendered color contrast, focus/dialog behavior, and assistive-technology acceptance remain open. Request creation uses server-provided, versioned input contracts persisted in workflow schema version 4 alongside generic durable analysis receipts. PostgreSQL adapters provide shared account/session/workflow/receipt state, transaction-locked bootstrap/rate limits/execution reservation, multi-instance visibility, fail-closed SQLite migration, and dump/restore evidence. The SWR route remains the first execution-gate-backed workflow. Atlas Replay and Atlas Projections are separate direct human analysis workflows: both are session/CSRF/permission checked, deterministic, bounded, non-actuating, and visibly subordinate to governance. Projection receipts persist canonical input/output evidence and audit hashes without copying raw claim or evidence content into the audit relay. Human decision, analysis, and execution receipts remain visibly distinct.  
**Recommended next action:** Implement TAAR report inspection or the Atlas Sludge inspection workflow, then complete accessibility and cross-client acceptance.
