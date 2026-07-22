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
  await expect(page.getByRole("heading", { level: 1, name: heading })).toBeVisible();
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
