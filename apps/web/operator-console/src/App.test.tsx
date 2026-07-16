import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { ControlCenterApp } from "./App";

const dashboard = {
  status: "ready", version: "0.0.0.dev0", maturity: "development",
  authority_boundary: "The Control Center does not grant authority.", doi_records: 2, work_items: [],
  surfaces: [
    { id: "gateway", label: "Gateway", status: "healthy", metric: "0.0.0.dev0", detail: "Live" },
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
  if (url.endsWith("/atlas/status")) return Promise.resolve(response({ status: "available", version: "0.0.0.dev0", stack: "Atlas", authority: "analysis_only", protected_operations: ["sludge_narrative"], subordination_notice: "Atlas analysis is not a decision, authority grant, or actuation." }));
  if (url.endsWith("/dois")) return Promise.resolve(response({ dois: [{ title: "Paper-01", doi: "10.1/example", domain: "security", url: "https://doi.org/10.1/example" }] }));
  if (url.includes("/audit?")) return Promise.resolve(response({ chain_valid: true, count: 0, filtered_count: 0, offset: 0, limit: 25, records: [] }));
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
  localStorage.removeItem("project-ai-density");
  localStorage.removeItem("project-ai-reduced-motion");
  delete document.documentElement.dataset.density;
  delete document.documentElement.dataset.reducedMotion;
  vi.unstubAllGlobals();
});

test("renders truthful dashboard data for an authenticated human session", async () => {
  render(<ControlCenterApp />);
  expect(await screen.findByText("5/5 invariants")).toBeInTheDocument();
  expect(screen.getByText("No work-item API is available yet.")).toBeInTheDocument();
  expect(screen.getByText("The Control Center does not grant authority.")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Open account security" })).toHaveTextContent("Local Owner");
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
  expect(screen.getByText(/No machine credential is entered/)).toBeInTheDocument();
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

test("opens and closes narrow-screen navigation without changing routes", async () => {
  const user = userEvent.setup(); render(<ControlCenterApp />);
  await screen.findByText("5/5 invariants");
  await user.click(screen.getByRole("button", { name: "Open navigation" }));
  expect(screen.getByRole("button", { name: "Close navigation overlay" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Close navigation overlay" }));
  expect(screen.queryByRole("button", { name: "Close navigation overlay" })).not.toBeInTheDocument();
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
