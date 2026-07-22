import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { ControlCenterApp } from "./App";

const dashboard = {
  status: "ready", version: "0.0.3", maturity: "development",
  authority_boundary: "The Control Center does not grant authority.", doi_records: 2, work_items: [],
  surfaces: [
    { id: "gateway", label: "Gateway", status: "healthy", metric: "0.0.3", detail: "Live" },
    { id: "replay", label: "Replay", status: "healthy", metric: "5/5 invariants", detail: "Pass" },
    { id: "audit_chain", label: "Audit chain", status: "healthy", metric: "0 entries", detail: "Valid" },
    { id: "evidence", label: "Evidence registry", status: "healthy", metric: "2 DOI records", detail: "Available" },
  ],
};

const signedIn = {
  account: { id: "account-1", username: "owner", display_name: "Local Owner", role: "owner", actor_id: "ACTOR-OWNER", mfa_enabled: false, status: "active", must_change_password: false },
  session_id: "session-1", csrf_token: "csrf-test", idle_expires_at: "2026-07-15T13:00:00Z", absolute_expires_at: "2026-07-16T00:00:00Z", mfa_verified_at: null,
};
const storageData = new Map<string, string>();

function response(payload: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => payload } as Response;
}

function auditSummary(
  event: string,
  sourceHash: string,
  timestamp: string,
  options: { previousHash?: string; verdict?: "ALLOW" | "DENY" | "ESCALATE"; severity?: string } = {},
) {
  return {
    event,
    timestamp,
    source_hash: sourceHash,
    previous_hash: options.previousHash ?? "0".repeat(64),
    verdict: options.verdict ?? null,
    severity: options.severity ?? null,
    chain_status: "verified" as const,
  };
}

function useNarrowViewport(): void {
  vi.stubGlobal("matchMedia", vi.fn().mockImplementation((query: string) => ({
    matches: query === "(max-width: 920px)",
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })));
}

async function expectNoAutomatedAccessibilityViolations(): Promise<void> {
  const result = await axe.run(document.body, {
    rules: { "color-contrast": { enabled: false } },
  });
  expect(
    result.violations.map(({ id, impact, nodes }) => ({ id, impact, nodes: nodes.length })),
  ).toEqual([]);
}

function defaultFetch(input: string | URL | Request): Promise<Response> {
  const url = String(input);
  if (url.endsWith("/health/live")) return Promise.resolve(response({ status: "live", version: "0.0.3" }));
  if (url.endsWith("/api/v1/instance")) return Promise.resolve(response({ display_name: "PROJECT-AI-LOCAL", deployment: "local_sovereign", cloud_login: false, browser_machine_identity: false, browser_execution_capability: false, human_access_path: ["identity", "authentication", "server_session", "workspace"], governed_execution_path: ["server_service_identity", "governance_policy", "scoped_capability", "execution_gate"] }));
  if (url.endsWith("/api/v1/auth/bootstrap-status")) return Promise.resolve(response({ status: "closed", setup_secret_required: false }));
  if (url.endsWith("/api/v1/auth/session")) return Promise.resolve(response(signedIn));
  if (url.endsWith("/api/v1/dashboard")) return Promise.resolve(response(dashboard));
  if (url.endsWith("/api/v1/modules")) return Promise.resolve(response({ modules: [{ id: "swr", label: "Sovereign War Room", category: "simulation", maturity: "implemented", interface_status: "available", authority: "Governed deterministic scenarios", summary: "Reviewed scenario requests can produce execution-gate receipts." }, { id: "atlas", label: "Atlas", category: "analysis", maturity: "experimental", interface_status: "available", authority: "Analysis only; never a verdict or authority grant", summary: "Signed-in analysts can verify and reconstruct bounded replay bundles." }, { id: "taar", label: "TAAR", category: "analysis", maturity: "experimental", interface_status: "available", authority: "Registered report-only readers; no source-mutation capability", summary: "Signed-in operators can run registered readers against the fixed server target." }] }));
  if (url.endsWith("/api/v1/modules/taar/status")) return Promise.resolve(response({ status: "available", target_repository: "Project-AI-Beginnings", target_path: "T:/00-Active/Project-AI-Beginnings", facility_mode: "GREEN", registry_valid: true, registry_validation_errors: 0, readers: [{ id: "heartbeat-reader", task_id: "heartbeat-check", description: "Check the TAAR facility heartbeat.", classification_default: "OPEN", timeout_seconds: 60, evidence_scope: ["registry/**", "taar.toml"] }], report_only: true, browser_selects_target: false, browser_submits_commands: false, source_mutation_capability: false }));
  if (url.includes("/api/v1/modules/taar/runs?")) return Promise.resolve(response({ runs: [], redaction_boundary: "Sensitive or hash-invalid evidence is withheld." }));
  if (url.endsWith("/api/v1/work/requests")) return Promise.resolve(response({ requests: [], review_is_not_governance: true }));
  if (url.endsWith("/api/v1/work/operations")) return Promise.resolve(response({ operations: [{ id: "evidence.inspect", label: "Inspect evidence", description: "Request human inspection.", resource_hint: "bundle:42", schema_version: "evidence.inspect/v1", fields: [{ id: "bundle_id", label: "Evidence bundle identifier", description: "The exact evidence bundle to inspect.", placeholder: "42", resource_prefix: "bundle:", min_length: 1, max_length: 128, pattern: "(?!.*\\.\\.)[A-Za-z0-9][A-Za-z0-9._\\/\\-]*" }], consequence: "Records intent only; no execution is started." }], execution_started: false }));
  if (url.endsWith("/replay/status")) return Promise.resolve(response({ status: "pass", invariants_passed: 5, invariants_total: 5, updated_at: "now" }));
  if (url.endsWith("/atlas/status")) return Promise.resolve(response({ status: "available", version: "0.0.3", stack: "Atlas", authority: "analysis_only", protected_operations: ["sludge_narrative"], subordination_notice: "Atlas analysis is not a decision, authority grant, or actuation." }));
  if (url.includes("/api/v1/modules/atlas/projections?")) return Promise.resolve(response({ projections: [] }));
  if (url.endsWith("/api/v1/modules/swr/scenarios")) return Promise.resolve(response({ scenarios: [], execution_gate_configured: true, authority_boundary: "The browser never receives a capability token." }));
  if (url.endsWith("/dois")) return Promise.resolve(response({ dois: [{ title: "Paper-01", doi: "10.1/example", domain: "security", url: "https://doi.org/10.1/example" }] }));
  if (url.endsWith("/audit/search")) return Promise.resolve(response({ chain_valid: true, count: 0, filtered_count: 0, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [] }));
  if (url.endsWith("/api/v1/auth/sessions")) return Promise.resolve(response({ sessions: [{ id: "session-1", current: true, created_at: "2026-07-15T12:00:00Z", last_seen_at: "2026-07-15T12:05:00Z", idle_expires_at: "2026-07-15T13:00:00Z", absolute_expires_at: "2026-07-16T00:00:00Z", user_agent: "Test browser", client_host: "127.0.0.1", revoked: false, mfa_verified_at: null }] }));
  if (url.endsWith("/api/v1/auth/mfa")) return Promise.resolve(response({ enabled: false, enrollment_pending: false }));
  if (url.endsWith("/api/v1/admin/accounts")) return Promise.resolve(response({ accounts: [{ ...signedIn.account, created_at: "2026-07-15T12:00:00Z" }] }));
  if (url.endsWith("/api/v1/admin/security-events")) return Promise.resolve(response({ events: [] }));
  if (url.endsWith("/api/v1/auth/logout")) return Promise.resolve(response({ message: "Signed out" }));
  return Promise.resolve(response({ detail: "Not found" }, 404));
}

beforeEach(() => {
  storageData.clear();
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => storageData.get(key) ?? null,
    setItem: (key: string, value: string) => storageData.set(key, value),
    removeItem: (key: string) => storageData.delete(key),
    clear: () => storageData.clear(),
  });
  window.history.pushState({}, "", "/command-center");
  vi.stubGlobal("fetch", vi.fn(defaultFetch));
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  localStorage.removeItem("project-ai-density");
  localStorage.removeItem("project-ai-reduced-motion");
  delete document.documentElement.dataset.density;
  delete document.documentElement.dataset.reducedMotion;
  vi.unstubAllGlobals();
});

test("renders truthful dashboard data for an authenticated human session", async () => {
  render(<ControlCenterApp />);
  expect(await screen.findByText("5/5 invariants")).toBeInTheDocument();
  expect(await screen.findByRole("status", { name: "Environment: PROJECT-AI-LOCAL" })).toBeInTheDocument();
  expect(await screen.findByRole("status", { name: /Gateway live.*Liveness verified for version 0.0.3/ })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Environment:/ })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Open operator documentation" })).toHaveAttribute("href", "http://127.0.0.1:4173/");
  expect(screen.getByText("No work-item API is available yet.")).toBeInTheDocument();
  const workQueue = screen.getByRole("region", { name: "Work queue table; scroll horizontally to view all columns" });
  expect(workQueue).toHaveAttribute("tabindex", "0");
  expect(workQueue).toHaveAttribute("aria-describedby", "work-queue-scroll-hint");
  expect(screen.getByText("Scroll table")).toBeInTheDocument();
  expect(screen.getByText("The Control Center does not grant authority.")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Open account security" })).toHaveTextContent("Local Owner");
  await expectNoAutomatedAccessibilityViolations();
});

test("reports browser-offline and gateway-unavailable states without a false live signal", async () => {
  const online = vi.spyOn(Navigator.prototype, "onLine", "get").mockReturnValue(true);
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    if (String(input).endsWith("/health/live")) return response({ detail: "Gateway unavailable" }, 503);
    return defaultFetch(input);
  }));
  render(<ControlCenterApp />);
  expect(await screen.findByRole("status", { name: /Gateway unavailable.*No liveness response/ })).toBeInTheDocument();
  expect(screen.queryByText("Live query")).not.toBeInTheDocument();

  online.mockReturnValue(false);
  window.dispatchEvent(new Event("offline"));
  expect(await screen.findByRole("status", { name: /Browser offline.*no network connection/ })).toBeInTheDocument();
  expect(await screen.findByText("Offline snapshot")).toBeInTheDocument();
  expect(screen.getByText(/It is not current evidence/)).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
  online.mockReturnValue(true);
  window.dispatchEvent(new Event("online"));
});

test("keeps a failed dashboard refresh visibly stale while retaining the last verified snapshot", async () => {
  let dashboardCalls = 0;
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    if (String(input).endsWith("/api/v1/dashboard")) {
      dashboardCalls += 1;
      return dashboardCalls === 1
        ? response(dashboard)
        : response({ detail: "Dashboard refresh failed" }, 503);
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  render(<ControlCenterApp />);
  expect(await screen.findByText("5/5 invariants")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Refresh" }));
  expect(await screen.findByText("Dashboard data is stale", {}, { timeout: 5_000 })).toBeInTheDocument();
  expect(screen.getByText(/last verified snapshot/i)).toBeInTheDocument();
  expect(screen.getByText("5/5 invariants")).toBeInTheDocument();
  expect(screen.queryByText("Dashboard unavailable")).not.toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("elevates degraded and unavailable dashboard surfaces as partial evidence", async () => {
  const partialDashboard = {
    ...dashboard,
    surfaces: dashboard.surfaces.map((surface) => surface.id === "audit_chain"
      ? { ...surface, status: "unavailable", metric: "Unavailable", detail: "Audit storage cannot be verified." }
      : surface),
  };
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => String(input).endsWith("/api/v1/dashboard")
    ? response(partialDashboard)
    : defaultFetch(input)));
  render(<ControlCenterApp />);
  expect(await screen.findByText("Partial system evidence")).toBeInTheDocument();
  expect(screen.getByText(/Audit chain: unavailable/)).toBeInTheDocument();
  expect(screen.getByText("Audit storage cannot be verified.")).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("deep-links to evidence and preserves accessible navigation", async () => {
  window.history.pushState({}, "", "/evidence");
  render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Evidence" })).toBeInTheDocument();
  expect(await screen.findByText("Paper-01")).toBeInTheDocument();
  expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeInTheDocument();
});

test("loads protected audit evidence without a browser-readable machine token", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  render(<ControlCenterApp />);
  expect(await screen.findByText("No matching records")).toBeInTheDocument();
  expect(screen.queryByLabelText("Development API token")).not.toBeInTheDocument();
  expect(screen.getByText(/Search results expose normalized summaries only/)).toBeInTheDocument();
});

test("uses stable audit cursors instead of positional paging", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  const anchor = "b".repeat(64);
  const auditRequests: Array<{ url: string; body: Record<string, unknown> }> = [];
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/audit/search")) {
      const body = JSON.parse(String(init?.body)) as Record<string, unknown>;
      auditRequests.push({ url, body });
      const cursor = typeof body.cursor === "string" ? body.cursor : null;
      return cursor
        ? response({ chain_valid: true, count: 4, filtered_count: 4, offset: 3, limit: 25, cursor, next_cursor: null, has_more: false, records: [auditSummary("control.oldest", "a".repeat(64), "2026-07-21T12:00:00Z")] })
        : response({ chain_valid: true, count: 3, filtered_count: 3, offset: 0, limit: 25, cursor: null, next_cursor: anchor, has_more: true, records: [auditSummary("control.newest", "c".repeat(64), "2026-07-21T12:02:00Z"), auditSummary("control.middle", anchor, "2026-07-21T12:01:00Z")] });
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  render(<ControlCenterApp />);
  expect(await screen.findByText("control.newest")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Older" }));
  expect(await screen.findByText("control.oldest")).toBeInTheDocument();
  expect(auditRequests.some(({ body }) => body.cursor === anchor)).toBe(true);
  expect(auditRequests.every(({ url, body }) => !url.includes("?") && !("offset" in body))).toBe(true);
  await user.click(screen.getByRole("button", { name: "Newer" }));
  expect(await screen.findByText("control.newest")).toBeInTheDocument();
});

test("sends the complete normalized audit filter contract", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  const auditRequests: Array<{ url: string; body: Record<string, unknown> }> = [];
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/audit/search")) {
      auditRequests.push({ url, body: JSON.parse(String(init?.body)) as Record<string, unknown> });
      return response({ chain_valid: true, count: 0, filtered_count: 0, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [] });
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  render(<ControlCenterApp />);
  await screen.findByText("No matching records");
  await user.type(screen.getByLabelText("Search evidence"), "action-safe");
  await user.type(screen.getByLabelText("Event type"), "control.filtered");
  await user.click(screen.getByText("More filters"));
  await user.type(screen.getByLabelText("Actor"), "ACTOR-REVIEWER");
  await user.type(screen.getByLabelText("Account"), "account-reviewer");
  await user.type(screen.getByLabelText("Operation"), "evidence.inspect");
  await user.type(screen.getByLabelText("Resource"), "bundle:approved-42");
  await user.selectOptions(screen.getByLabelText("Verdict"), "ESCALATE");
  await user.type(screen.getByLabelText("Severity"), "high");
  fireEvent.change(screen.getByLabelText(/From time/), { target: { value: "2026-07-21T12:00" } });
  fireEvent.change(screen.getByLabelText(/To time/), { target: { value: "2026-07-21T13:00" } });
  await user.click(screen.getByRole("button", { name: "Apply filters" }));
  await waitFor(() => expect(auditRequests).toHaveLength(2));
  expect(auditRequests[1].url).not.toContain("?");
  expect(auditRequests[1].body).toEqual({
    limit: 25,
    query: "action-safe",
    event: "control.filtered",
    actor: "ACTOR-REVIEWER",
    account: "account-reviewer",
    operation: "evidence.inspect",
    resource: "bundle:approved-42",
    verdict: "ESCALATE",
    severity: "high",
    from_time: new Date("2026-07-21T12:00").toISOString(),
    to_time: new Date("2026-07-21T13:00").toISOString(),
  });
  expect(screen.getByText("10 active")).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("requests a permission-gated redacted audit export and downloads its receipt", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  const auditRecord = auditSummary("control.test", "a".repeat(64), "2026-07-21T12:00:00Z");
  const exported = {
    schema_version: "project-ai.audit-export/v1",
    generated_at: "2026-07-21T12:05:00Z",
    source_chain_valid: true,
    source_chain_records: 1,
    matched_records: 1,
    exported_records: 1,
    offset: 0,
    limit: 500,
    filters: { query: "action-safe", event: "control.test" },
    redaction_applied: true,
    redaction_policy: "allowlist-v1",
    records_sha256: "b".repeat(64),
    export_audit_hash: "c".repeat(64),
    records: [{ event: "control.test", timestamp: auditRecord.timestamp, source_hash: auditRecord.source_hash, previous_hash: "0".repeat(64), fields: { action_id: "action-safe" }, redacted_fields: ["message"] }],
  };
  const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/audit/search")) return response({ chain_valid: true, count: 1, filtered_count: 1, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [auditRecord] });
    if (url.endsWith("/audit/export")) {
      expect(init?.method).toBe("POST");
      expect((init?.headers as Headers).get("X-CSRF-Token")).toBe("csrf-test");
      expect(JSON.parse(String(init?.body))).toEqual({ limit: 500, offset: 0, query: "action-safe", event: "control.test" });
      return response(exported);
    }
    return defaultFetch(input);
  });
  vi.stubGlobal("fetch", fetchMock);
  const NativeUrl = URL;
  class DownloadUrl extends NativeUrl {}
  const createObjectURL = vi.fn(() => "blob:audit-export");
  const revokeObjectURL = vi.fn();
  Object.assign(DownloadUrl, { createObjectURL, revokeObjectURL });
  vi.stubGlobal("URL", DownloadUrl);
  const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);

  const user = userEvent.setup();
  render(<ControlCenterApp />);
  await user.type(await screen.findByLabelText("Search evidence"), "action-safe");
  await user.type(screen.getByLabelText("Event type"), "control.test");
  await user.click(screen.getByRole("button", { name: "Apply filters" }));
  await user.click(await screen.findByRole("button", { name: "Export redacted results" }));

  const exportStatus = await screen.findByText(/Exported 1 of 1 matching records with redaction/);
  expect(exportStatus).toHaveAttribute("role", "status");
  expect(createObjectURL).toHaveBeenCalledOnce();
  expect(revokeObjectURL).toHaveBeenCalledWith("blob:audit-export");
  expect(click).toHaveBeenCalledOnce();
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining("/audit/export"),
    expect.objectContaining({ method: "POST", credentials: "same-origin" }),
  );
});

test("does not offer bulk audit export to a viewer", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  const viewer = { ...signedIn, account: { ...signedIn.account, role: "viewer" } };
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/session")) return response(viewer);
    if (url.endsWith("/audit/search")) return response({ chain_valid: true, count: 1, filtered_count: 1, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [auditSummary("control.test", "a".repeat(64), "2026-07-21T12:00:00Z")] });
    return defaultFetch(input);
  }));
  render(<ControlCenterApp />);
  expect(await screen.findByText("Your role can view approved audit evidence but cannot request bulk exports.")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Export redacted results" })).not.toBeInTheDocument();
});

test("opens privileged normalized audit detail with safe escaped raw JSON", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  const sourceHash = "d".repeat(64);
  const previousHash = "c".repeat(64);
  const requests: Array<{ url: string; method: string | undefined; body: unknown }> = [];
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/audit/search")) {
      return response({ chain_valid: true, count: 4, filtered_count: 1, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [auditSummary("control.detail", sourceHash, "2026-07-21T12:00:00Z", { previousHash, verdict: "DENY", severity: "high" })] });
    }
    if (url.endsWith("/audit/detail")) {
      requests.push({ url, method: init?.method, body: JSON.parse(String(init?.body)) });
      return response({
        chain_valid: true,
        chain_status: "verified",
        chain_position: 4,
        chain_records: 4,
        visibility: "privileged",
        event: "control.detail",
        timestamp: "2026-07-21T12:00:00Z",
        source_hash: sourceHash,
        previous_hash: previousHash,
        fields: { action_id: "action-detail-1", api_token: "[REDACTED]", message: "<script>evidence remains text</script>", verdict: "DENY" },
        redacted_fields: ["api_token"],
        raw_record: { event: "control.detail", timestamp: "2026-07-21T12:00:00Z", hash: sourceHash, previous_hash: previousHash, action_id: "action-detail-1", api_token: "[REDACTED]", message: "<script>evidence remains text</script>", verdict: "DENY" },
      });
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  render(<ControlCenterApp />);
  const trigger = await screen.findByRole("button", { name: /View detail for control.detail/ });
  await user.click(trigger);

  const heading = await screen.findByRole("heading", { name: "control.detail", level: 3 });
  await waitFor(() => expect(heading).toHaveFocus());
  expect(screen.getByText("Privileged safe view")).toBeInTheDocument();
  expect(screen.getByText("4 of 4")).toBeInTheDocument();
  expect(screen.getAllByText("[REDACTED]").length).toBeGreaterThan(0);
  expect(screen.getAllByText("<script>evidence remains text</script>").length).toBeGreaterThan(0);
  expect(document.querySelector("script")).toBeNull();
  expect(requests).toEqual([{ url: "/api/audit/detail", method: "POST", body: { source_hash: sourceHash } }]);
  await expectNoAutomatedAccessibilityViolations();

  await user.click(screen.getByRole("button", { name: "Close audit record detail" }));
  expect(trigger).toHaveFocus();
  expect(screen.queryByRole("heading", { name: "control.detail", level: 3 })).not.toBeInTheDocument();
});

test("shows only normalized redacted detail to a reviewer", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  const sourceHash = "e".repeat(64);
  const reviewer = { ...signedIn, account: { ...signedIn.account, role: "reviewer" } };
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/session")) return response(reviewer);
    if (url.endsWith("/audit/search")) return response({ chain_valid: true, count: 1, filtered_count: 1, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [auditSummary("control.restricted", sourceHash, "2026-07-21T12:00:00Z", { severity: "high" })] });
    if (url.endsWith("/audit/detail")) return response({ chain_valid: true, chain_status: "verified", chain_position: 1, chain_records: 1, visibility: "redacted", event: "control.restricted", timestamp: "2026-07-21T12:00:00Z", source_hash: sourceHash, previous_hash: "0".repeat(64), fields: { action_id_sha256: "f".repeat(64), severity: "high" }, redacted_fields: ["action_id", "message", "resource"], raw_record: null });
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  render(<ControlCenterApp />);
  expect(await screen.findByLabelText("Search evidence")).toHaveAttribute("placeholder", "Event, hash, verdict, or severity");
  await user.click(screen.getByText("More filters"));
  expect(screen.queryByLabelText("Actor")).not.toBeInTheDocument();
  expect(screen.getByText(/filters require raw-audit permission/)).toBeInTheDocument();
  await user.click(await screen.findByRole("button", { name: /View detail for control.restricted/ }));

  expect(await screen.findByText("Permission-filtered view")).toBeInTheDocument();
  expect(screen.getByText("Raw JSON withheld")).toBeInTheDocument();
  expect(screen.getByText("action_id_sha256")).toBeInTheDocument();
  expect(screen.queryByText("Safe raw JSON")).not.toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("removes cached audit records when integrity verification fails", async () => {
  window.history.pushState({}, "", "/evidence/audit");
  let searches = 0;
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/audit/search")) {
      searches += 1;
      return searches === 1
        ? response({ chain_valid: true, count: 1, filtered_count: 1, offset: 0, limit: 25, cursor: null, next_cursor: null, has_more: false, records: [auditSummary("control.valid", "a".repeat(64), "2026-07-21T12:00:00Z")] })
        : response({ detail: "Audit hash chain verification failed" }, 503);
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  render(<ControlCenterApp />);
  expect(await screen.findByText("control.valid")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Apply filters" }));

  expect(await screen.findByText(/Audit hash chain verification failed.*No cached records are displayed/)).toBeInTheDocument();
  expect(screen.getByText("Audit locked down")).toBeInTheDocument();
  expect(screen.queryByText("control.valid")).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /View detail for control.valid/ })).not.toBeInTheDocument();
});

test("redirects an unauthenticated deep link to sign in and completes login", async () => {
  const fetchMock = vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/bootstrap-status")) return response({ status: "closed", setup_secret_required: false });
    if (url.endsWith("/api/v1/auth/session")) return response({ detail: "Sign in required" }, 401);
    if (url.endsWith("/api/v1/auth/login")) return response(signedIn);
    return defaultFetch(input);
  });
  vi.stubGlobal("fetch", fetchMock);
  const user = userEvent.setup(); render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
  expect(await screen.findByText("Connected to:")).toHaveTextContent("PROJECT-AI-LOCAL");
  expect(screen.getByText("Authentication establishes identity. Authority is evaluated independently by governance policy.")).toBeInTheDocument();
  expect(screen.getByText("Server-authenticated session")).toBeInTheDocument();
  expect(screen.getByText("Governance gate remains authoritative")).toBeInTheDocument();
  expect(screen.getByText("Capabilities resolve per request")).toBeInTheDocument();
  expect(screen.getByText(/No machine identity or execution token is stored in this browser/)).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
  await user.type(screen.getByLabelText("Username"), "owner");
  await user.type(screen.getByLabelText("Password"), "Foundation!Owner123");
  await user.click(screen.getByRole("button", { name: "Continue" }));
  expect(await screen.findByText("5/5 invariants")).toBeInTheDocument();
  expect(window.location.pathname).toBe("/command-center");
});

test("prompts for an authenticator code only after valid primary credentials", async () => {
  let loginAttempts = 0;
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/bootstrap-status")) return response({ status: "closed", setup_secret_required: false });
    if (url.endsWith("/api/v1/auth/session")) return response({ detail: "Sign in required" }, 401);
    if (url.endsWith("/api/v1/auth/login")) {
      loginAttempts += 1;
      return loginAttempts === 1 ? response({ detail: "Authenticator code required" }, 428) : response({ ...signedIn, account: { ...signedIn.account, mfa_enabled: true }, mfa_verified_at: "2026-07-15T12:10:00Z" });
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup(); window.history.pushState({}, "", "/sign-in"); render(<ControlCenterApp />);
  await user.type(await screen.findByLabelText("Username"), "owner");
  await user.type(screen.getByLabelText("Password"), "Foundation!Owner123");
  await user.click(screen.getByRole("button", { name: "Continue" }));
  await user.type(await screen.findByLabelText("Authenticator code"), "123456");
  await user.click(screen.getByRole("button", { name: "Continue" }));
  expect(await screen.findByText("5/5 invariants")).toBeInTheDocument();
  expect(loginAttempts).toBe(2);
});

test("runs first-time Owner setup and requires recovery-code acknowledgement", async () => {
  const recoveryCodes = Array.from({ length: 10 }, (_, index) => `CODE-${index}-SAFE`);
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/bootstrap-status")) return response({ status: "required", setup_secret_required: true });
    if (url.endsWith("/api/v1/auth/bootstrap")) return response({ ...signedIn, recovery_codes: recoveryCodes });
    return defaultFetch(input);
  }));
  const user = userEvent.setup(); window.history.pushState({}, "", "/setup"); render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Create the Owner account" })).toBeInTheDocument();
  await user.type(screen.getByLabelText("One-time setup secret"), "one-time-setup");
  await user.type(screen.getByLabelText("Display name"), "Local Owner");
  await user.type(screen.getByLabelText("Username"), "owner");
  await user.type(screen.getByLabelText("Password"), "Foundation!Owner123");
  await user.type(screen.getByLabelText("Confirm password"), "Foundation!Owner123");
  await user.click(screen.getByRole("button", { name: "Create Owner account" }));
  expect(await screen.findByRole("heading", { name: "Save recovery codes" })).toBeInTheDocument();
  expect(screen.getByText("CODE-0-SAFE")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Enter Control Center" })).toBeDisabled();
  await user.click(screen.getByRole("checkbox", { name: /I saved these codes/ }));
  expect(screen.getByRole("button", { name: "Enter Control Center" })).toBeEnabled();
});

test("recovers locally without inventing an email workflow", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/bootstrap-status")) return response({ status: "closed", setup_secret_required: false });
    if (url.endsWith("/api/v1/auth/session")) return response({ detail: "Sign in required" }, 401);
    if (url.endsWith("/api/v1/auth/recovery/complete")) return response({ message: "Recovery completed" });
    return defaultFetch(input);
  }));
  const user = userEvent.setup(); window.history.pushState({}, "", "/recover"); render(<ControlCenterApp />);
  await screen.findByRole("heading", { name: "Recover access" });
  await user.type(screen.getByLabelText("Username"), "owner");
  await user.type(screen.getByLabelText("Recovery code"), "ABCD-EFGH-JKLM");
  await user.type(screen.getByLabelText("New password"), "Recovered!Owner789");
  await user.type(screen.getByLabelText("Confirm new password"), "Recovered!Owner789");
  await user.click(screen.getByRole("button", { name: "Reset password" }));
  expect(await screen.findByText("Recovery complete. Sign in with your new password.")).toBeInTheDocument();
  expect(screen.queryByText(/email/i)).not.toBeInTheDocument();
});

test("shows current server session and signs out through CSRF-protected API", async () => {
  const user = userEvent.setup(); window.history.pushState({}, "", "/profile/security"); render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Account security" })).toBeInTheDocument();
  expect(await screen.findByText("This browser")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Sign out" }));
  await waitFor(() => expect(window.location.pathname).toBe("/sign-in"));
  const logoutCall = vi.mocked(fetch).mock.calls.find(([input]) => String(input).endsWith("/api/v1/auth/logout"));
  expect(logoutCall?.[1]?.headers).toEqual(expect.any(Headers));
  expect((logoutCall?.[1]?.headers as Headers).get("X-CSRF-Token")).toBe("csrf-test");
});

test("redirects a temporary-password account to security", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/auth/bootstrap-status")) return response({ status: "closed", setup_secret_required: false });
    if (url.endsWith("/api/v1/auth/session")) return response({ ...signedIn, account: { ...signedIn.account, must_change_password: true } });
    return defaultFetch(input);
  }));
  render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Account security" })).toBeInTheDocument();
  expect(window.location.pathname).toBe("/profile/security");
});

test("shows server-authorized account administration and one-time codes", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/v1/admin/accounts")) {
      const isCreate = init?.method === "POST";
      return isCreate ? response({ account: { ...signedIn.account, id: "account-2", username: "operator.one", display_name: "Operator One", role: "operator", actor_id: null, must_change_password: true, created_at: "2026-07-15T13:00:00Z" }, recovery_codes: ["ABCD-EFGH-JKLM"] }) : response({ accounts: [{ ...signedIn.account, created_at: "2026-07-15T12:00:00Z" }] });
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup(); window.history.pushState({}, "", "/administration/accounts"); render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Administration" })).toBeInTheDocument();
  await user.type(screen.getByLabelText("Display name"), "Operator One");
  await user.type(screen.getByLabelText("Username"), "operator.one");
  await user.type(screen.getByLabelText("Temporary password"), "Temporary!Operator123");
  await user.click(screen.getByRole("button", { name: "Create account" }));
  expect(await screen.findByText("ABCD-EFGH-JKLM")).toBeInTheDocument();
  expect(screen.getByText("Password change required")).toBeInTheDocument();
});

test("isolates narrow-screen navigation focus and restores its trigger", async () => {
  useNarrowViewport();
  const user = userEvent.setup(); render(<ControlCenterApp />);
  await screen.findByText("5/5 invariants");
  const navigation = document.querySelector<HTMLElement>(".console-sidebar");
  const trigger = screen.getByRole("button", { name: "Open navigation" });
  expect(navigation).toHaveAttribute("aria-hidden", "true");
  expect(navigation).toHaveAttribute("inert");
  await user.click(trigger);
  const dialog = screen.getByRole("dialog", { name: "Control Center sidebar" });
  expect(dialog).not.toHaveAttribute("aria-hidden");
  expect(dialog).not.toHaveAttribute("inert");
  const close = screen.getByRole("button", { name: "Close navigation" });
  await waitFor(() => expect(close).toHaveFocus());
  await user.tab({ shift: true });
  expect(screen.getByRole("link", { name: "Preferences" })).toHaveFocus();
  await user.tab();
  expect(close).toHaveFocus();
  await user.keyboard("{Escape}");
  expect(navigation).toHaveAttribute("aria-hidden", "true");
  await waitFor(() => expect(trigger).toHaveFocus());
  expect(window.location.pathname).toBe("/command-center");
});

test("opens keyboard screen search and navigates to a result", async () => {
  const user = userEvent.setup(); render(<ControlCenterApp />);
  await screen.findByText("5/5 invariants");
  await user.keyboard("{Control>}k{/Control}");
  const search = screen.getByRole("textbox", { name: "Screen search" });
  await user.type(search, "preferences");
  await user.click(screen.getByRole("button", { name: "Display preferences" }));
  expect(await screen.findByRole("heading", { name: "Display preferences" })).toBeInTheDocument();
  await waitFor(() => expect(document.querySelector("#main-content")).toHaveFocus());
});

test("contains command-dialog focus and restores the invoking control", async () => {
  const user = userEvent.setup(); render(<ControlCenterApp />);
  await screen.findByText("5/5 invariants");
  const trigger = screen.getByRole("button", { name: "Search Control Center screens" });
  await user.click(trigger);
  const search = screen.getByRole("textbox", { name: "Screen search" });
  await waitFor(() => expect(search).toHaveFocus());
  await user.tab({ shift: true });
  expect(screen.getByRole("button", { name: "Account administration" })).toHaveFocus();
  await user.tab();
  expect(search).toHaveFocus();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("dialog", { name: "Search Control Center screens" })).not.toBeInTheDocument();
  await waitFor(() => expect(trigger).toHaveFocus());
});

const authenticatedRoutes = [
  "/command-center",
  "/inbox",
  "/requests",
  "/evidence",
  "/evidence/audit",
  "/governance",
  "/security",
  "/simulations",
  "/simulations/swr",
  "/simulations/atlas-replay",
  "/simulations/atlas-projections",
  "/simulations/taar",
  "/system/health",
  "/profile/security",
  "/profile/preferences",
  "/administration/accounts",
] as const;

test.each(authenticatedRoutes)("has no automated accessibility violations on %s", async (path) => {
  window.history.pushState({}, "", path);
  render(<ControlCenterApp />);
  await screen.findByRole("heading", { level: 1 });
  await waitFor(() => expect(screen.queryByText("Checking local session")).not.toBeInTheDocument());
  await expectNoAutomatedAccessibilityViolations();
});

test("loads live work notifications and persists browser-local preferences", async () => {
  const request = { id: "request-1", created_by: "operator-1", title: "Review evidence", operation: "evidence.inspect", resource: "bundle:42", rationale: "Verify", state: "submitted", created_at: "2026-07-15T12:00:00Z", updated_at: "2026-07-15T12:00:00Z" };
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => String(input).endsWith("/api/v1/work/requests") ? response({ requests: [request], review_is_not_governance: true }) : defaultFetch(input)));
  const user = userEvent.setup(); render(<ControlCenterApp />);
  await screen.findByText("5/5 invariants");
  await user.click(screen.getByRole("button", { name: "Open work notifications" }));
  expect(await screen.findByText("Review evidence")).toBeInTheDocument();
  await user.click(screen.getByRole("link", { name: "Preferences" }));
  await user.click(await screen.findByRole("radio", { name: "Compact" }));
  await user.click(screen.getByRole("checkbox", { name: "Reduce motion" }));
  expect(localStorage.getItem("project-ai-density")).toBe("compact");
  expect(localStorage.getItem("project-ai-reduced-motion")).toBe("true");
});

test("deep-links to the truthful simulation catalog", async () => {
  window.history.pushState({}, "", "/simulations"); render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Simulations and analysis" })).toBeInTheDocument();
  expect(await screen.findByText("Sovereign War Room")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Open governed workflow" })).toHaveAttribute("href", "/simulations/swr");
  expect(screen.getByRole("link", { name: "Open projections" })).toHaveAttribute("href", "/simulations/atlas-projections");
  expect(screen.getByRole("link", { name: "Open replay workspace" })).toHaveAttribute("href", "/simulations/atlas-replay");
  expect(screen.getByRole("link", { name: "Open inspection console" })).toHaveAttribute("href", "/simulations/taar");
});

test("runs a registered TAAR reader without accepting browser authority inputs", async () => {
  const run = { run_id: "run-1", agent_id: "heartbeat-reader", task_id: "heartbeat-check", classification: "OPEN", status: "succeeded", branch: "main", commit: "a".repeat(40), dirty_state_before: "clean", start_time: "2026-07-16T01:00:00Z", end_time: "2026-07-16T01:00:01Z", duration_ms: 42, command_count: 1, finding_count: 0, evidence_hash: "b".repeat(64), evidence_hash_valid: true, audit_record_hash: "c".repeat(64), audit_record_hash_valid: true, details_redacted: false, findings: [], commands: [{ command: "builtin:heartbeat_check", exit_code: 0, duration_ms: 0 }], uncertainty: [], human_action_required: false, report_only: true, source_mutation_capability: false, governance_verdict_created: false, project_ai_execution_started: false };
  let created = false;
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
    const url = String(input);
    if (url.endsWith("/api/v1/modules/taar/runs")) { created = true; return response({ run, reused_existing_receipt: false }, 201); }
    if (url.includes("/api/v1/modules/taar/runs?")) return response({ runs: created ? [run] : [], redaction_boundary: "Sensitive or hash-invalid evidence is withheld." });
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  window.history.pushState({}, "", "/simulations/taar");
  render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "TAAR Inspection Console" })).toBeInTheDocument();
  expect(await screen.findByText("Project-AI-Beginnings")).toBeInTheDocument();
  expect(screen.queryByLabelText(/repository path/i)).not.toBeInTheDocument();
  expect(screen.queryByLabelText(/command/i)).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Run inspection" }));
  expect(await screen.findByText("Latest evidence")).toBeInTheDocument();
  expect(await screen.findAllByText("Verified")).not.toHaveLength(0);
  expect(screen.getByText(/No source-mutation capability/)).toBeInTheDocument();
  const post = vi.mocked(fetch).mock.calls.find(([input]) => String(input).endsWith("/api/v1/modules/taar/runs"));
  expect(JSON.parse(String(post?.[1]?.body))).toEqual({ agent_id: "heartbeat-reader", idempotency_key: expect.any(String) });
  await expectNoAutomatedAccessibilityViolations();
});

test("creates an Atlas projection and exposes its durable analysis receipt", async () => {
  const projection = {
    id: "projection-receipt-1", initiated_by: "account-1", claim_id: "claim-projection-1",
    statement: "Source-backed controls remain effective under the evaluated conditions.", claim_type: "predictive", stack: "RS",
    evidence: [{ source: "control-test", tier: "A", confidence: 0.9 }, { source: "replay-test", tier: "B", confidence: 0.8 }],
    drivers: [{ name: "control_strength", value: 0.85 }, { name: "source_quality", value: 0.95 }],
    posterior: 0.711, uncertainty: 0.289, evidence_count: 2, projection_sha256: "p".repeat(64),
    input_sha256: "i".repeat(64), output_sha256: "o".repeat(64), audit_hash: "a".repeat(64),
    created_at: "2026-07-16T12:00:00Z", subordination_notice: "Atlas output is analytical evidence only.",
    authority: "analysis_only", recommendation_created: false, governance_verdict_created: false, execution_started: false,
  };
  let created = false;
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.includes("/api/v1/modules/atlas/projections?")) return response({ projections: created ? [projection] : [] });
    if (url.endsWith("/api/v1/modules/atlas/projections") && init?.method === "POST") {
      const body = JSON.parse(String(init.body)) as { claim_id: string; evidence: unknown[]; drivers: unknown[] };
      expect(body).toMatchObject({ claim_id: "claim-projection-1" });
      expect(body.evidence).toHaveLength(2); expect(body.drivers).toHaveLength(2);
      expect(new Headers(init.headers).get("X-CSRF-Token")).toBe("csrf-test");
      created = true; return response({ projection, reused_existing_receipt: false }, 201);
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup(); window.history.pushState({}, "", "/simulations/atlas-projections"); render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Atlas Projections" })).toBeInTheDocument();
  expect(screen.getByText("Not a recommendation")).toBeInTheDocument();
  expect(await screen.findByText("No projections yet")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Create projection" }));
  expect(await screen.findByRole("heading", { name: "Projection result" })).toBeInTheDocument();
  expect(screen.getAllByText("0.711")).toHaveLength(2);
  expect(screen.getByText("This projection is analytical evidence only. It is not a decision or authority grant.")).toBeInTheDocument();
  expect(await screen.findByText("claim-projection-1")).toBeInTheDocument();
  expect(screen.getByText("Analysis only", { selector: "dd" })).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("verifies and reconstructs an Atlas bundle without claiming authority", async () => {
  const replay = { status: "verified", bundle_id: "bundle-1", bundle_hash: "b".repeat(64), reconstructed_state_hash: "r".repeat(64), item_counts: { audit_events: 1, checkpoints: 1, claims: 1, graph_snapshots: 1, projections: 1 }, audit_receipt_sha256: "a".repeat(64), audited_at: "2026-07-16T12:00:00Z", subordination_notice: "Atlas analysis is not a decision, authority grant, or actuation.", authority: "analysis_only", governance_verdict_created: false, execution_started: false };
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/v1/modules/atlas/replay") && init?.method === "POST") {
      const body = JSON.parse(String(init.body)) as { bundle: { bundle_id: string } };
      expect(body.bundle.bundle_id).toBe("bundle-1");
      expect(new Headers(init.headers).get("X-CSRF-Token")).toBe("csrf-test");
      return response(replay);
    }
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  window.history.pushState({}, "", "/simulations/atlas-replay");
  render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Atlas Replay" })).toBeInTheDocument();
  expect(screen.getByText("No governance verdict")).toBeInTheDocument();
  expect(screen.queryByLabelText(/token/i)).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Verify and replay" }));
  expect(await screen.findByRole("heading", { name: "Verification passed" })).toBeInTheDocument();
  expect(screen.getByText("Bundle ID · bundle-1")).toBeInTheDocument();
  expect(screen.getByText("This reconstruction is evidence only. It is not a decision or authority grant.")).toBeInTheDocument();
  expect(screen.getByText("a".repeat(64))).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("runs a reviewed SWR request and presents the durable execution receipt", async () => {
  const scenario = { scenario_id: "s".repeat(32), name: "Triage under uncertainty", description: "Allocate scarce care safely.", scenario_type: "ethical_dilemma", difficulty: 4, round_number: 1, expected_decision: "escalate_for_human_triage", tags: ["ethics", "triage"] };
  const request = { id: "request-swr", created_by: "account-1", title: "Run SWR triage", operation: "scenario.prepare", resource: `scenario:${scenario.scenario_id}`, rationale: "Bounded analysis", state: "reviewed_approve", created_at: "2026-07-15T12:00:00Z", updated_at: "2026-07-15T12:05:00Z" };
  const receipt = { request_id: request.id, attempt_id: "attempt-1", module_id: "swr", initiated_by: "account-1", status: "executed", action_id: "swr:action", outcome: "ALLOW", reason: "", output: { recorded: true, score: 100 }, governance_evidence_sha256: "e".repeat(64), event_hash: "f".repeat(64), audit_hash: "a".repeat(64), created_at: "2026-07-15T12:06:00Z", completed_at: "2026-07-15T12:06:01Z" };
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/v1/modules/swr/scenarios")) return response({ scenarios: [scenario], execution_gate_configured: true, authority_boundary: "The browser never receives a capability token." });
    if (url.endsWith("/api/v1/work/requests/request-swr/execute/swr") && init?.method === "POST") return response({ receipt, reused_existing_receipt: false });
    if (url.endsWith("/api/v1/auth/mfa/step-up")) return response({ message: "MFA verified" });
    if (url.endsWith("/api/v1/work/requests")) return response({ requests: [request], review_is_not_governance: true });
    return defaultFetch(input);
  }));
  const user = userEvent.setup();
  window.history.pushState({}, "", "/simulations/swr");
  render(<ControlCenterApp />);
  expect(await screen.findByRole("heading", { name: "Sovereign War Room" })).toBeInTheDocument();
  await screen.findByRole("option", { name: "Run SWR triage · scenario:" + scenario.scenario_id });
  await user.selectOptions(screen.getByLabelText("Approved request"), request.id);
  await user.selectOptions(screen.getByLabelText("Scenario"), scenario.scenario_id);
  await user.type(screen.getByLabelText("Authenticator code (if step-up is not recent)"), "123456");
  await user.click(screen.getByRole("button", { name: "Submit through execution gate" }));
  expect(await screen.findByRole("heading", { name: "Durable execution receipt" })).toBeInTheDocument();
  expect(screen.getByText("a".repeat(64))).toBeInTheDocument();
  expect(screen.getByText("The server submitted the bounded scenario record through the execution gate.")).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
});

test("records a human request without claiming governance or execution", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/v1/work/requests") && init?.method === "POST") { expect(JSON.parse(String(init.body))).toMatchObject({ inputs: { bundle_id: "42" } }); return response({ id: "request-1", created_by: "account-1", title: "Inspect evidence", operation: "evidence.inspect", resource: "bundle:42", input_schema_version: "evidence.inspect/v1", inputs: { bundle_id: "42" }, input_sha256: "b".repeat(64), rationale: "Verify provenance", state: "submitted", created_at: "2026-07-15T12:00:00Z", updated_at: "2026-07-15T12:00:00Z" }); }
    if (url.endsWith("/api/v1/work/requests/request-1") && init?.method === "GET") return response({ request: { id: "request-1", created_by: "account-1", title: "Inspect evidence", operation: "evidence.inspect", resource: "bundle:42", input_schema_version: "evidence.inspect/v1", inputs: { bundle_id: "42" }, input_sha256: "b".repeat(64), rationale: "Verify provenance", state: "submitted", created_at: "2026-07-15T12:00:00Z", updated_at: "2026-07-15T12:00:00Z" }, reviews: [{ id: "review-1", request_id: "request-1", reviewer_account_id: "reviewer-1", decision: "approve_for_governance", rationale: "Evidence is sufficient", created_at: "2026-07-15T12:05:00Z", receipt_sha256: "a".repeat(64), governance_verdict_created: false, execution_started: false }], execution_receipt: null, execution_status: "not_started" });
    if (url.endsWith("/api/v1/work/requests/request-1/cancel")) return response({ id: "request-1", created_by: "account-1", title: "Inspect evidence", operation: "evidence.inspect", resource: "bundle:42", input_schema_version: "evidence.inspect/v1", inputs: { bundle_id: "42" }, input_sha256: "b".repeat(64), rationale: "Verify provenance", state: "cancelled", created_at: "2026-07-15T12:00:00Z", updated_at: "2026-07-15T12:01:00Z" });
    return defaultFetch(input);
  }));
  const user = userEvent.setup(); window.history.pushState({}, "", "/requests"); render(<ControlCenterApp />);
  await user.type(await screen.findByLabelText("Title"), "Inspect evidence");
  await user.selectOptions(screen.getByLabelText("Operation"), "evidence.inspect");
  expect(screen.getByText("Input contract: evidence.inspect/v1")).toBeInTheDocument();
  await user.type(screen.getByLabelText(/Evidence bundle identifier/), "42");
  await user.type(screen.getByLabelText("Rationale"), "Verify provenance");
  await user.click(screen.getByRole("button", { name: "Record request" }));
  expect(await screen.findByText("Request recorded. No governance verdict was created and no execution started.")).toBeInTheDocument();
  expect(screen.getByText("submitted")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "View detail" }));
  expect(await screen.findByText("None — the execution gate has not run.")).toBeInTheDocument();
  expect(screen.getByText("evidence.inspect/v1")).toBeInTheDocument();
  expect(screen.getByText("b".repeat(64))).toBeInTheDocument();
  expect(screen.getByText("a".repeat(64))).toBeInTheDocument();
  expect(screen.getByText("Human review only · no governance verdict · no execution")).toBeInTheDocument();
  await expectNoAutomatedAccessibilityViolations();
  await user.click(screen.getByRole("button", { name: "Cancel request" }));
  expect(await screen.findByText("Request cancelled. No governance verdict was created and no execution started.")).toBeInTheDocument();
  expect(screen.getByText("cancelled")).toBeInTheDocument();
});
