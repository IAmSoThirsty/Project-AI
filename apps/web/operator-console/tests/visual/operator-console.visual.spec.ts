import { expect, test, type Page } from "@playwright/test";

const session = {
  account: {
    id: "account-owner",
    username: "owner",
    display_name: "Local Owner",
    role: "owner",
    actor_id: "actor-owner",
    mfa_enabled: true,
    status: "active",
    must_change_password: false,
  },
  session_id: "visual-session",
  csrf_token: "visual-csrf",
  idle_expires_at: "2026-07-21T18:00:00Z",
  absolute_expires_at: "2026-07-22T17:00:00Z",
  mfa_verified_at: "2026-07-21T17:00:00Z",
};

const auditSourceHash = "a".repeat(64);
const auditPreviousHash = "9".repeat(64);

const dashboard = {
  status: "ready",
  version: "0.0.3",
  maturity: "development",
  authority_boundary: "The Control Center presents server evidence; it does not grant execution authority.",
  surfaces: [
    { id: "gateway", label: "Gateway", status: "healthy", metric: "0.0.3", detail: "Development gateway is live." },
    { id: "replay", label: "Replay", status: "healthy", metric: "5/5 invariants", detail: "Canonical replay passed." },
    { id: "audit_chain", label: "Audit chain", status: "healthy", metric: "Verified", detail: "The available chain validates." },
    { id: "evidence", label: "Evidence", status: "healthy", metric: "2 DOI records", detail: "DOI-backed records are available." },
  ],
  doi_records: 2,
  work_items: [
    { id: "work-1", priority: "P1", title: "Review governed release evidence", owner: "Owner", state: "AWAITING_DECISION", updated_at: "2026-07-21 17:00 UTC" },
    { id: "work-2", priority: "P2", title: "Inspect canonical replay receipt", owner: "Auditor", state: "ESCALATE", updated_at: "2026-07-21 16:45 UTC" },
  ],
};

type ApiFixture = [suffix: string, payload: unknown, status?: number];

const fixtures: ApiFixture[] = [
  ["/health/live", { status: "live", version: "0.0.3" }],
  ["/api/v1/auth/bootstrap-status", { status: "closed", setup_secret_required: false }],
  ["/api/v1/auth/session", session],
  ["/api/v1/instance", {
    display_name: "PROJECT-AI-VISUAL-TEST",
    deployment: "local_sovereign",
    cloud_login: false,
    browser_machine_identity: false,
    browser_execution_capability: false,
    human_access_path: ["identity", "authentication", "server_session", "workspace"],
    governed_execution_path: ["server_service_identity", "governance_policy", "scoped_capability", "execution_gate"],
  }],
  ["/api/v1/dashboard", dashboard],
  ["/api/v1/work/requests", { requests: [], review_is_not_governance: true }],
  ["/api/v1/auth/sessions", { sessions: [] }],
  ["/api/v1/auth/mfa", { enabled: false, enrollment_pending: false }],
  ["/api/v1/modules/swr/scenarios", { scenarios: [], execution_gate_configured: true, authority_boundary: "The browser never receives a capability token." }],
  ["/api/v1/modules/taar/status", { status: "available", target_repository: "Project-AI-Beginnings", target_path: "T:/00-Active/Project-AI-Beginnings", facility_mode: "GREEN", registry_valid: true, registry_validation_errors: 0, readers: [{ id: "heartbeat-reader", task_id: "heartbeat-check", description: "Check the facility heartbeat.", classification_default: "OPEN", timeout_seconds: 60, evidence_scope: ["registry/**"] }], report_only: true, browser_selects_target: false, browser_submits_commands: false, source_mutation_capability: false }],
  ["/api/v1/modules/taar/runs", { runs: [], redaction_boundary: "Sensitive or hash-invalid evidence is withheld." }],
  ["/replay/status", { status: "pass", invariants_passed: 5, invariants_total: 5, updated_at: "2026-07-21T17:00:00Z" }],
  ["/dois", { dois: [
    { title: "Governed AI Systems", doi: "10.1000/project-ai.1", domain: "governance", url: "https://doi.org/10.1000/project-ai.1" },
    { title: "Deterministic Replay Evidence", doi: "10.1000/project-ai.2", domain: "verification", url: "https://doi.org/10.1000/project-ai.2" },
  ] }],
  ["/audit/search", {
    chain_valid: true,
    count: 2,
    filtered_count: 2,
    offset: 0,
    limit: 25,
    cursor: null,
    next_cursor: null,
    has_more: false,
    records: [
      { event: "governance.evaluated", timestamp: "2026-07-21T16:58:00Z", source_hash: auditSourceHash, previous_hash: auditPreviousHash, verdict: "ESCALATE", severity: "high", chain_status: "verified" },
      { event: "execution.denied", timestamp: "2026-07-21T16:59:00Z", source_hash: "b".repeat(64), previous_hash: auditSourceHash, verdict: "DENY", severity: "critical", chain_status: "verified" },
    ],
  }],
  ["/audit/detail", {
    chain_valid: true,
    chain_status: "verified",
    chain_position: 42,
    chain_records: 84,
    visibility: "privileged",
    event: "governance.evaluated",
    timestamp: "2026-07-21T16:58:00Z",
    source_hash: auditSourceHash,
    previous_hash: auditPreviousHash,
    fields: { action_id: "action-visual-001", actor_id: "ACTOR-OWNER", api_token: "[REDACTED]", operation: "governance.evaluate", resource: "release:v0.0.3", severity: "high", verdict: "ESCALATE" },
    redacted_fields: ["api_token"],
    raw_record: { event: "governance.evaluated", timestamp: "2026-07-21T16:58:00Z", hash: auditSourceHash, previous_hash: auditPreviousHash, action_id: "action-visual-001", actor_id: "ACTOR-OWNER", api_token: "[REDACTED]", operation: "governance.evaluate", resource: "release:v0.0.3", severity: "high", verdict: "ESCALATE" },
  }],
  ["/api/v1/admin/accounts", { accounts: [{ ...session.account, created_at: "2026-07-20T16:00:00Z" }] }],
  ["/api/v1/admin/security-events", { events: [] }],
];

let unhandledRequests: string[];

async function installDeterministicApi(page: Page, overrides: ApiFixture[] = []) {
  unhandledRequests = [];
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    const fixture = overrides.find(([suffix]) => url.pathname.endsWith(suffix))
      ?? fixtures.find(([suffix]) => url.pathname.endsWith(suffix));
    if (!fixture) {
      unhandledRequests.push(`${route.request().method()} ${url.pathname}`);
      await route.fulfill({ status: 501, json: { detail: "No visual-test fixture is registered." } });
      return;
    }
    await route.fulfill({ status: fixture[2] ?? 200, json: fixture[1] });
  });
}

async function openAuthenticatedRoute(page: Page, path: string, heading: string) {
  await page.goto(path);
  await expect(page.getByRole("heading", { level: 1, name: heading })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("Checking local session")).toHaveCount(0);
  await page.evaluate(async () => document.fonts.ready);
  expect(unhandledRequests).toEqual([]);
}

test.beforeEach(async ({ page }) => {
  await page.clock.setFixedTime(new Date("2026-07-21T17:00:00Z"));
  await installDeterministicApi(page);
});

test("command center desktop", async ({ page }) => {
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await expect(page.getByText("5/5 invariants")).toBeVisible();
  await expect(page).toHaveScreenshot("command-center-desktop.png", { fullPage: true });
});

test("command center mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await expect(page.getByRole("button", { name: "Open navigation" })).toBeVisible();
  await expect(page).toHaveScreenshot("command-center-mobile.png", { fullPage: true });
});

test("browser offline state remains visible on mobile with the last snapshot", async ({ page, context }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await context.setOffline(true);
  await expect(page.locator(".mobile-gateway-state", { hasText: "Browser offline" })).toBeVisible();
  await expect(page.getByText("Offline snapshot")).toBeVisible();
  await expect(page.getByText("5/5 invariants")).toBeVisible();
  await expect(page).toHaveScreenshot("command-center-offline-mobile.png", { fullPage: true });
  await context.setOffline(false);
});

test("command center elevates partial system evidence", async ({ page }) => {
  await page.unroute("**/api/**");
  const degraded = {
    ...dashboard,
    surfaces: dashboard.surfaces.map((surface) => surface.id === "audit_chain"
      ? { ...surface, status: "unavailable", metric: "Unavailable", detail: "Audit storage cannot be verified." }
      : surface),
  };
  await installDeterministicApi(page, [["/api/v1/dashboard", degraded]]);
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await expect(page.getByText("Partial system evidence")).toBeVisible();
  await expect(page.getByRole("status", { name: /Gateway live/ })).toBeVisible();
  await expect(page).toHaveScreenshot("command-center-partial.png", { fullPage: true });
});

test("command center exposes unavailable gateway and dashboard states", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/health/live", { detail: "Gateway liveness unavailable" }, 503],
    ["/api/v1/dashboard", { detail: "Dashboard unavailable" }, 503],
  ]);
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await expect(page.getByRole("status", { name: /Gateway unavailable/ })).toBeVisible();
  await expect(page.getByRole("alert")).toContainText("Dashboard unavailable");
  await expect(page.getByText("Live query")).toHaveCount(0);
  await expect(page).toHaveScreenshot("command-center-unavailable.png", { fullPage: true });
});

test("command center retains and labels a stale verified snapshot", async ({ page }) => {
  await page.unroute("**/api/**");
  unhandledRequests = [];
  let dashboardRequests = 0;
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/api/v1/dashboard")) {
      dashboardRequests += 1;
      await route.fulfill(dashboardRequests === 1
        ? { status: 200, json: dashboard }
        : { status: 503, json: { detail: "Dashboard refresh failed" } });
      return;
    }
    const fixture = fixtures.find(([suffix]) => url.pathname.endsWith(suffix));
    if (!fixture) {
      unhandledRequests.push(`${route.request().method()} ${url.pathname}`);
      await route.fulfill({ status: 501, json: { detail: "No visual-test fixture is registered." } });
      return;
    }
    await route.fulfill({ status: fixture[2] ?? 200, json: fixture[1] });
  });
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await page.getByRole("button", { name: "Refresh" }).click();
  await expect(page.getByText("Dashboard data is stale")).toBeVisible();
  await expect(page.getByText("5/5 invariants")).toBeVisible();
  await expect(page).toHaveScreenshot("command-center-stale.png", { fullPage: true });
});

test("mobile navigation modal", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(page.getByRole("dialog", { name: "Control Center sidebar" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Close navigation", exact: true })).toBeFocused();
  await expect(page).toHaveScreenshot("navigation-mobile-open.png");
});

test("viewer navigation omits administrative authority", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [["/api/v1/auth/session", { ...session, account: { ...session.account, role: "viewer" } }]]);
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(page.getByRole("link", { name: "Preferences" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Administration" })).toHaveCount(0);
  await expect(page).toHaveScreenshot("navigation-viewer-mobile-open.png");
});

test("viewer sees an explicit Atlas access restriction", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/session", { ...session, account: { ...session.account, role: "viewer" } }],
    ["/atlas/status", { detail: "Module analysis permission required" }, 403],
  ]);
  await openAuthenticatedRoute(page, "/simulations/atlas-replay", "Atlas Replay");
  await expect(page.getByRole("alert")).toContainText("Atlas access restricted");
  await expect(page.getByRole("alert")).toContainText("No replay input or verification controls are shown");
  await expect(page.getByRole("heading", { name: "Replay bundle" })).toHaveCount(0);
});

test("viewer sees SWR as view-only", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [["/api/v1/auth/session", { ...session, account: { ...session.account, role: "viewer" } }]]);
  await openAuthenticatedRoute(page, "/simulations/swr", "Sovereign War Room");
  await expect(page.getByRole("button", { name: "View only" })).toBeDisabled();
  await expect(page.getByText("Your interface role can inspect deterministic scenarios but cannot initiate execution.")).toBeVisible();
});

test("viewer sees an explicit Atlas projection restriction", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/session", { ...session, account: { ...session.account, role: "viewer" } }],
    ["/api/v1/modules/atlas/projections", { detail: "Module analysis permission required" }, 403],
  ]);
  await openAuthenticatedRoute(page, "/simulations/atlas-projections", "Atlas Projections");
  await expect(page.getByRole("alert")).toContainText("Atlas access restricted");
  await expect(page.getByRole("alert")).toContainText("No projection inputs, history, or creation controls are shown");
  await expect(page.getByRole("heading", { name: "Projection inputs" })).toHaveCount(0);
});

test("reviewer sees TAAR as view-only", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [["/api/v1/auth/session", { ...session, account: { ...session.account, role: "reviewer" } }]]);
  await openAuthenticatedRoute(page, "/simulations/taar", "TAAR Inspection Console");
  await expect(page.getByRole("button", { name: "View only" })).toBeDisabled();
  await expect(page.getByText("Your interface role can inspect sealed evidence but cannot run a reader.")).toBeVisible();
});

test("reviewer inbox exposes human review without execution authority", async ({ page }) => {
  const reviewer = { ...session, account: { ...session.account, id: "reviewer-account", role: "reviewer" } };
  const request = {
    id: "request-review-1",
    created_by: "operator-account",
    title: "Review bounded evidence",
    operation: "evidence.inspect",
    resource: "bundle:review-1",
    rationale: "Confirm the evidence bundle before governance evaluation.",
    state: "submitted",
    created_at: "2026-07-21T16:00:00Z",
    updated_at: "2026-07-21T16:00:00Z",
  };
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/session", reviewer],
    ["/api/v1/work/requests", { requests: [request], review_is_not_governance: true }],
  ]);
  await openAuthenticatedRoute(page, "/inbox", "My Inbox");
  await expect(page.getByRole("heading", { name: "Record human review" })).toBeVisible();
  await expect(page.getByRole("option", { name: "Review bounded evidence" })).toHaveCount(1);
  await expect(page.getByText("Approval forwards for governance; it is not ALLOW.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Record a request" })).toHaveCount(0);
  expect(unhandledRequests).toEqual([]);
});

test("administrator retains the management surface and role controls", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [[
    "/api/v1/auth/session",
    { ...session, account: { ...session.account, role: "administrator" } },
  ]]);
  await openAuthenticatedRoute(page, "/administration/accounts", "Administration");
  await expect(page.getByRole("heading", { name: "Create account" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Human accounts" })).toBeVisible();
  await expect(page.getByLabel("Interface role")).toBeVisible();
  await expect(page.getByText("Role and status changes are server-authorized and audit-recorded.")).toBeVisible();
  await expect(page.getByText("Administration access restricted")).toHaveCount(0);
  expect(unhandledRequests).toEqual([]);
});

test("viewer request workspace withholds the submission composer", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [["/api/v1/auth/session", { ...session, account: { ...session.account, role: "viewer" } }]]);
  await openAuthenticatedRoute(page, "/requests", "Execution requests");
  await expect(page.getByText("Request submission restricted", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Record a request" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "No requests are visible" })).toBeVisible();
});

test("viewer sees an explicit administration access restriction", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/session", { ...session, account: { ...session.account, role: "viewer" } }],
    ["/api/v1/admin/accounts", { detail: "Account administration permission required" }, 403],
    ["/api/v1/admin/security-events", { detail: "Account administration permission required" }, 403],
  ]);
  await openAuthenticatedRoute(page, "/administration/accounts", "Administration");
  await expect(page.getByRole("status", { name: "Administration access restricted" })).toBeVisible();
  await expect(page.getByText(/current interface role cannot manage human accounts/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Create account" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Human accounts" })).toHaveCount(0);
});

test("security hides controls when its initial state cannot be verified", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/sessions", { detail: "Session store unavailable" }, 503],
    ["/api/v1/auth/mfa", { detail: "Authenticator state unavailable" }, 503],
  ]);
  await openAuthenticatedRoute(page, "/profile/security", "Account security");
  await expect(page.getByRole("alert", { name: "Account security unavailable" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Set up authenticator" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Change password" })).toHaveCount(0);
});

test("temporary-password accounts are routed to security before other workspaces", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [[
    "/api/v1/auth/session",
    { ...session, account: { ...session.account, must_change_password: true } },
  ]]);
  await page.goto("/command-center");
  await expect(page.getByRole("heading", { level: 1, name: "Account security" })).toBeVisible();
  await expect(page).toHaveURL(/\/profile\/security$/);
  expect(unhandledRequests).toEqual([]);
});

test("system health labels partial gateway evidence", async ({ page }) => {
  await page.unroute("**/api/**");
  const degraded = {
    ...dashboard,
    surfaces: dashboard.surfaces.map((surface) => surface.id === "audit_chain"
      ? { ...surface, status: "unavailable", metric: "Unavailable", detail: "Audit storage cannot be verified." }
      : surface),
  };
  await installDeterministicApi(page, [["/api/v1/dashboard", degraded]]);
  await openAuthenticatedRoute(page, "/system/health", "System health");
  await expect(page.getByRole("status", { name: "Partial system evidence" })).toBeVisible();
  await expect(page.getByText("Audit chain: unavailable")).toBeVisible();
  await expect(page.getByText("Current gateway evidence, not a production-readiness claim.")).toBeVisible();
});

test("module catalog failure does not present a false empty catalog", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [["/api/v1/modules", { detail: "Module catalog unavailable" }, 503]]);
  await openAuthenticatedRoute(page, "/simulations", "Simulations and analysis");
  await expect(page.getByRole("alert", { name: "Catalog unavailable" })).toBeVisible();
  await expect(page.getByText("No module count or interface state is shown because the catalog read failed.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Open projections" })).toHaveCount(0);
});

test("evidence labels a partial replay and DOI snapshot", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [["/dois", { detail: "DOI registry unavailable" }, 503]]);
  await openAuthenticatedRoute(page, "/evidence", "Evidence");
  await expect(page.getByRole("status", { name: "Partial evidence" })).toBeVisible();
  await expect(page.getByText("5/5 invariants")).toBeVisible();
  await expect(page.getByRole("alert", { name: "DOI registry unavailable" })).toBeVisible();
});

test("sign-in keeps the server boundary visible and reports failed credentials", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/session", { detail: "Sign in required" }, 401],
    ["/api/v1/auth/login", { detail: "Invalid username or password" }, 401],
  ]);
  await page.goto("/sign-in");
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
  await expect(page.getByText("Server-authenticated session")).toBeVisible();
  await expect(page.getByText("Governance gate remains authoritative")).toBeVisible();
  await page.getByLabel("Username").fill("unknown");
  await page.locator("#password").fill("wrong-password");
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByRole("alert")).toHaveText("Invalid username or password");
  expect(unhandledRequests).toEqual([]);
});

test("recovery completes locally and confirms the next sign-in step", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/session", { detail: "Sign in required" }, 401],
    ["/api/v1/auth/recovery/complete", { message: "Recovery completed" }],
  ]);
  await page.goto("/recover");
  await expect(page.getByRole("heading", { name: "Recover access" })).toBeVisible();
  await page.getByLabel("Username").fill("owner");
  await page.getByLabel("Recovery code").fill("ABCD-EFGH-JKLM");
  await page.locator("#recovery-password").fill("Recovered!Owner789");
  await page.locator("#recovery-confirm").fill("Recovered!Owner789");
  await page.getByRole("button", { name: "Reset password" }).click();
  await expect(page.getByRole("status")).toHaveText("Recovery complete. Sign in with your new password.");
  await expect(page.getByText(/email/i)).toHaveCount(0);
  expect(unhandledRequests).toEqual([]);
});

test("account service failure withholds the protected workspace", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [[
    "/api/v1/auth/bootstrap-status",
    { detail: "Account service unavailable" },
    503,
  ]]);
  await page.goto("/command-center");
  await expect(page.getByText("Human account service unavailable")).toBeVisible();
  await expect(page.getByText("Set PROJECT_AI_ACCOUNT_DB and PROJECT_AI_SETUP_SECRET on the local gateway.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Command Center" })).toHaveCount(0);
  expect(unhandledRequests).toEqual([]);
});

test("first-run setup requires recovery-code acknowledgement before entry", async ({ page }) => {
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/auth/bootstrap-status", { status: "required", setup_secret_required: true }],
    ["/api/v1/auth/bootstrap", { ...session, recovery_codes: ["CODE-0-SAFE", "CODE-1-SAFE"] }],
  ]);
  await page.goto("/setup");
  await expect(page.getByRole("heading", { name: "Create the Owner account" })).toBeVisible();
  await page.getByLabel("One-time setup secret").fill("one-time-setup");
  await page.getByLabel("Display name").fill("Local Owner");
  await page.getByLabel("Username").fill("owner");
  await page.locator("#setup-password").fill("Foundation!Owner123");
  await page.locator("#confirm-password").fill("Foundation!Owner123");
  await page.getByRole("button", { name: "Create Owner account" }).click();
  await expect(page.getByRole("heading", { name: "Save recovery codes" })).toBeVisible();
  await expect(page.getByText("CODE-0-SAFE")).toBeVisible();
  const enter = page.getByRole("button", { name: "Enter Control Center" });
  await expect(enter).toBeDisabled();
  await page.getByRole("checkbox", { name: /I saved these codes/ }).check();
  await expect(enter).toBeEnabled();
  expect(unhandledRequests).toEqual([]);
});

test("TAAR run completion exposes sealed evidence and its report-only boundary", async ({ page }) => {
  const run = {
    run_id: "visual-run-1",
    agent_id: "heartbeat-reader",
    task_id: "heartbeat-check",
    classification: "OPEN",
    status: "succeeded",
    branch: "main",
    commit: "a".repeat(40),
    dirty_state_before: "clean",
    start_time: "2026-07-21T16:00:00Z",
    end_time: "2026-07-21T16:00:01Z",
    duration_ms: 42,
    command_count: 1,
    finding_count: 0,
    evidence_hash: "b".repeat(64),
    evidence_hash_valid: true,
    audit_record_hash: "c".repeat(64),
    audit_record_hash_valid: true,
    details_redacted: false,
    findings: [],
    commands: [{ command: "builtin:heartbeat_check", exit_code: 0, duration_ms: 0 }],
    uncertainty: [],
    human_action_required: false,
    report_only: true,
    source_mutation_capability: false,
    governance_verdict_created: false,
    project_ai_execution_started: false,
  };
  let created = false;
  await page.route("**/api/v1/modules/taar/runs", async (route) => {
    if (route.request().method() === "POST") {
      created = true;
      await route.fulfill({ status: 201, json: { run, reused_existing_receipt: false } });
      return;
    }
    await route.fulfill({ status: 200, json: { runs: created ? [run] : [], redaction_boundary: "Sensitive or hash-invalid evidence is withheld." } });
  });
  await openAuthenticatedRoute(page, "/simulations/taar", "TAAR Inspection Console");
  await expect(page.getByRole("button", { name: "Run inspection" })).toBeEnabled();
  await page.getByRole("button", { name: "Run inspection" }).click();
  await expect(page.getByRole("heading", { name: "Latest evidence" })).toBeVisible();
  await expect(page.getByText("Evidence SHA-256")).toBeVisible();
  await expect(page.getByText("No source-mutation capability, governance verdict, or Project-AI execution was created.")).toBeVisible();
  await expect(page.getByText("Sensitive or hash-invalid evidence is withheld.")).toBeVisible();
  expect(unhandledRequests).toEqual([]);
});

test("SWR execution presents a durable receipt without exposing a capability", async ({ page }) => {
  const scenario = {
    scenario_id: "swr-visual-1",
    name: "Triage under uncertainty",
    description: "Allocate scarce care safely.",
    scenario_type: "ethical_dilemma",
    difficulty: 4,
    round_number: 1,
    expected_decision: "escalate_for_human_triage",
    tags: ["ethics", "triage"],
  };
  const request = {
    id: "request-swr",
    created_by: session.account.id,
    title: "Run SWR triage",
    operation: "scenario.prepare",
    resource: `scenario:${scenario.scenario_id}`,
    rationale: "Bounded analysis",
    state: "reviewed_approve",
    created_at: "2026-07-21T16:00:00Z",
    updated_at: "2026-07-21T16:05:00Z",
  };
  const receipt = {
    request_id: request.id,
    attempt_id: "attempt-visual-1",
    module_id: "swr",
    initiated_by: session.account.id,
    status: "executed",
    action_id: "swr:action",
    outcome: "ALLOW",
    reason: "",
    output: { recorded: true, score: 100 },
    governance_evidence_sha256: "e".repeat(64),
    event_hash: "f".repeat(64),
    audit_hash: "a".repeat(64),
    created_at: "2026-07-21T16:06:00Z",
    completed_at: "2026-07-21T16:06:01Z",
  };
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [
    ["/api/v1/modules/swr/scenarios", {
      scenarios: [scenario],
      execution_gate_configured: true,
      authority_boundary: "The browser never receives a capability token.",
    }],
    ["/api/v1/work/requests", { requests: [request], review_is_not_governance: true }],
  ]);
  await page.route("**/api/v1/work/requests/request-swr/execute/swr", async (route) => {
    await route.fulfill({ status: 200, json: { receipt, reused_existing_receipt: false } });
  });
  await openAuthenticatedRoute(page, "/simulations/swr", "Sovereign War Room");
  await page.getByLabel("Approved request").selectOption(request.id);
  await page.locator("select").nth(1).selectOption(scenario.scenario_id);
  await page.getByRole("button", { name: "Submit through execution gate" }).click();
  await expect(page.getByRole("heading", { name: "Durable execution receipt" })).toBeVisible();
  await expect(page.getByText("The server submitted the bounded scenario record through the execution gate.")).toBeVisible();
  await expect(page.getByText("attempt-visual-1")).toBeVisible();
  await expect(page.getByText("The browser sends a request ID and scenario input. It never receives the server capability.")).toBeVisible();
  await expect(page.getByText("The browser never receives a capability token.")).toBeVisible();
  expect(unhandledRequests).toEqual([]);
});

test("Atlas projection creation exposes an analysis-only durable receipt", async ({ page }) => {
  const projection = {
    id: "projection-visual-1",
    initiated_by: session.account.id,
    claim_id: "claim-projection-1",
    statement: "Source-backed controls remain effective under the evaluated conditions.",
    claim_type: "predictive",
    stack: "RS",
    evidence: [{ source: "control-test", tier: "A", confidence: 0.9 }, { source: "replay-test", tier: "B", confidence: 0.8 }],
    drivers: [{ name: "control_strength", value: 0.85 }, { name: "source_quality", value: 0.95 }],
    posterior: 0.711,
    uncertainty: 0.289,
    evidence_count: 2,
    projection_sha256: "p".repeat(64),
    input_sha256: "i".repeat(64),
    output_sha256: "o".repeat(64),
    audit_hash: "a".repeat(64),
    created_at: "2026-07-21T16:00:00Z",
    subordination_notice: "Atlas output is analytical evidence only.",
  };
  let created = false;
  await page.unroute("**/api/**");
  await installDeterministicApi(page);
  await page.route("**/modules/atlas/projections*", async (route) => {
    if (route.request().method() === "POST") {
      created = true;
      await route.fulfill({ status: 201, json: { projection, reused_existing_receipt: false } });
      return;
    }
    await route.fulfill({ status: 200, json: { projections: created ? [projection] : [] } });
  });
  await openAuthenticatedRoute(page, "/simulations/atlas-projections", "Atlas Projections");
  await page.getByRole("button", { name: "Create projection" }).click();
  await expect(page.getByRole("heading", { name: "Projection result" })).toBeVisible();
  await expect(page.locator("aside").getByText("Projection SHA-256")).toBeVisible();
  await expect(page.getByText("This projection is analytical evidence only. It is not a decision or authority grant.")).toBeVisible();
  await expect(page.getByText("claim-projection-1")).toBeVisible();
  expect(unhandledRequests).toEqual([]);
});

test("Atlas replay verification exposes evidence without authority or execution", async ({ page }) => {
  const replay = {
    status: "verified",
    bundle_id: "bundle-visual-1",
    bundle_hash: "b".repeat(64),
    reconstructed_state_hash: "r".repeat(64),
    item_counts: { audit_events: 1, checkpoints: 1, claims: 1, graph_snapshots: 1, projections: 1 },
    audit_receipt_sha256: "a".repeat(64),
    audited_at: "2026-07-21T16:00:00Z",
    subordination_notice: "Atlas analysis is not a decision, authority grant, or actuation.",
    authority: "analysis_only",
    governance_verdict_created: false,
    execution_started: false,
  };
  await page.unroute("**/api/**");
  await installDeterministicApi(page, [[
    "/atlas/status",
    { status: "available", version: "0.0.3", stack: "Atlas", authority: "analysis_only", protected_operations: ["sludge_narrative"], subordination_notice: "Atlas analysis is not a decision, authority grant, or actuation." },
  ]]);
  await page.route("**/modules/atlas/replay", async (route) => {
    await route.fulfill({ status: 200, json: replay });
  });
  await openAuthenticatedRoute(page, "/simulations/atlas-replay", "Atlas Replay");
  await page.getByRole("button", { name: "Verify and replay" }).click();
  await expect(page.getByRole("heading", { name: "Verification passed" })).toBeVisible();
  await expect(page.getByText("Bundle ID · bundle-visual-1")).toBeVisible();
  await expect(page.getByText("This reconstruction is evidence only. It is not a decision or authority grant.")).toBeVisible();
  await expect(page.getByText("Browser token not used")).toBeVisible();
  expect(unhandledRequests).toEqual([]);
});

test("work notifications move focus into the dialog and restore it", async ({ page }) => {
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  const trigger = page.getByRole("button", { name: "Open work notifications" });
  await trigger.click();
  await expect(page.getByRole("dialog", { name: "Work notifications" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Close notifications" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog", { name: "Work notifications" })).toHaveCount(0);
  await expect(trigger).toBeFocused();
});

test("audit explorer desktop", async ({ page }) => {
  await openAuthenticatedRoute(page, "/evidence/audit", "Audit explorer");
  await expect(page.getByRole("button", { name: /View detail for governance.evaluated/ })).toBeVisible();
  await expect(page).toHaveScreenshot("audit-explorer-desktop.png", { fullPage: true });
});

test("expanded audit filters desktop", async ({ page }) => {
  await openAuthenticatedRoute(page, "/evidence/audit", "Audit explorer");
  await page.getByText("More filters").click();
  await expect(page.getByRole("textbox", { name: "Actor" })).toBeVisible();
  await expect(page).toHaveScreenshot("audit-filters-desktop.png", { fullPage: true });
});

test("expanded audit filters reflow on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/evidence/audit", "Audit explorer");
  await page.getByText("More filters").click();
  await expect(page.getByRole("textbox", { name: "Actor" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await expect(page).toHaveScreenshot("audit-filters-mobile.png", { fullPage: true });
});

test("privileged audit record detail desktop", async ({ page }) => {
  await openAuthenticatedRoute(page, "/evidence/audit", "Audit explorer");
  const trigger = page.getByRole("button", { name: /View detail for governance.evaluated/ });
  await trigger.click();
  await expect(page.getByRole("heading", { name: "governance.evaluated", level: 3 })).toBeFocused();
  await expect(page.getByText("Privileged safe view")).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await expect(page).toHaveScreenshot("audit-detail-desktop.png", { fullPage: true });
  await page.getByRole("button", { name: "Close audit record detail" }).click();
  await expect(trigger).toBeFocused();
});

test("permission-filtered audit detail reflows on mobile", async ({ page }) => {
  await page.unroute("**/api/**");
  unhandledRequests = [];
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/api/v1/auth/session")) {
      await route.fulfill({ status: 200, json: { ...session, account: { ...session.account, role: "reviewer" } } });
      return;
    }
    if (url.pathname.endsWith("/audit/detail")) {
      await route.fulfill({ status: 200, json: { chain_valid: true, chain_status: "verified", chain_position: 42, chain_records: 84, visibility: "redacted", event: "governance.evaluated", timestamp: "2026-07-21T16:58:00Z", source_hash: auditSourceHash, previous_hash: auditPreviousHash, fields: { action_id_sha256: "c".repeat(64), severity: "high", verdict: "ESCALATE" }, redacted_fields: ["action_id", "actor_id", "operation", "resource"], raw_record: null } });
      return;
    }
    const fixture = fixtures.find(([suffix]) => url.pathname.endsWith(suffix));
    if (!fixture) {
      unhandledRequests.push(`${route.request().method()} ${url.pathname}`);
      await route.fulfill({ status: 501, json: { detail: "No visual-test fixture is registered." } });
      return;
    }
    await route.fulfill({ status: 200, json: fixture[1] });
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/evidence/audit", "Audit explorer");
  await expect(page.getByPlaceholder("Event, hash, verdict, or severity")).toBeVisible();
  await page.getByText("More filters").click();
  await expect(page.getByText(/filters require raw-audit permission/)).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Actor" })).toHaveCount(0);
  await page.getByText("More filters").click();
  await page.getByRole("button", { name: /View detail for governance.evaluated/ }).click();
  await expect(page.getByRole("heading", { name: "governance.evaluated", level: 3 })).toBeFocused();
  await expect(page.getByText("Permission-filtered view")).toBeVisible();
  await expect(page.getByText("Raw JSON withheld")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await expect(page).toHaveScreenshot("audit-detail-redacted-mobile.png", { fullPage: true });
});

test("skip link bypasses persistent navigation", async ({ page }) => {
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await page.keyboard.press("Tab");
  const skipLink = page.getByRole("link", { name: "Skip to main content" });
  await expect(skipLink).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
});

test("mobile navigation contains focus and restores its keyboard trigger", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");
  const trigger = page.getByRole("button", { name: "Open navigation" });
  await expect(trigger).toBeFocused();
  await page.keyboard.press("Enter");
  const close = page.getByRole("button", { name: "Close navigation", exact: true });
  await expect(close).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(page.getByRole("link", { name: "Preferences" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(trigger).toBeFocused();
  await expect(page.getByRole("dialog", { name: "Control Center sidebar" })).toBeHidden();
});

test("audit filter controls follow a logical keyboard sequence", async ({ page }) => {
  await openAuthenticatedRoute(page, "/evidence/audit", "Audit explorer");
  const search = page.getByRole("textbox", { name: "Search evidence" });
  await search.focus();
  await expect(search).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("textbox", { name: "Event type" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByText("More filters")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Apply filters" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Export redacted results" })).toBeFocused();
});

test("route changes focus the main content across multiple workspaces", async ({ page }) => {
  await openAuthenticatedRoute(page, "/command-center", "Command Center");
  await page.getByRole("link", { name: "Evidence", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Evidence" })).toBeVisible();
  await expect(page.locator("#main-content")).toBeFocused();
  await page.getByRole("link", { name: "Audit explorer", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Audit explorer" })).toBeVisible();
  await expect(page.locator("#main-content")).toBeFocused();
  await page.getByRole("link", { name: "Preferences", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Display preferences" })).toBeVisible();
  await expect(page.locator("#main-content")).toBeFocused();
});

test("administration form follows its visual reading order", async ({ page }) => {
  await openAuthenticatedRoute(page, "/administration/accounts", "Administration");
  const displayName = page.getByRole("textbox", { name: "Display name" });
  await displayName.focus();
  await expect(displayName).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("textbox", { name: "Username" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Temporary password")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("combobox", { name: "Interface role" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("textbox", { name: "Actor binding (optional)" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Create account" })).toBeFocused();
});
