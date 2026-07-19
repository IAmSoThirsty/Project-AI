export type Health = { status: "live"; version: string };
export type InstanceIdentity = {
  display_name: string;
  deployment: "local_sovereign";
  cloud_login: false;
  browser_machine_identity: false;
  browser_execution_capability: false;
  human_access_path: ["identity", "authentication", "server_session", "workspace"];
  governed_execution_path: ["server_service_identity", "governance_policy", "scoped_capability", "execution_gate"];
};
export type ReplayStatus = {
  status: "not_run" | "pass" | "fail";
  invariants_passed: number;
  invariants_total: number;
  updated_at: string;
};
export type DoiRecord = { title: string; doi: string; domain: string; url: string };
export type AuditRecord = Record<string, string | number | boolean | null>;
export type AuditResponse = {
  chain_valid: true;
  count: number;
  filtered_count: number;
  offset: number;
  limit: number;
  records: AuditRecord[];
};
export type DashboardSurface = {
  id: "gateway" | "replay" | "audit_chain" | "evidence";
  label: string;
  status: "healthy" | "not_run" | "degraded" | "unavailable";
  metric: string;
  detail: string;
};
export type DashboardWorkItem = {
  id: string;
  priority: "P1" | "P2" | "P3";
  title: string;
  owner: string;
  state: "ALLOW" | "DENY" | "ESCALATE" | "AWAITING_DECISION";
  updated_at: string;
};
export type DashboardResponse = {
  status: "ready";
  version: string;
  maturity: "development";
  authority_boundary: string;
  surfaces: DashboardSurface[];
  doi_records: number;
  work_items: DashboardWorkItem[];
};
export type ModuleSurface = {
  id: string;
  label: string;
  category: "authority" | "security" | "analysis" | "simulation" | "operations";
  maturity: "implemented" | "experimental" | "pre_alpha" | "deferred";
  interface_status: "available" | "read_only" | "backend_only" | "unavailable";
  authority: string;
  summary: string;
};
export type AtlasStatus = {
  status: "available";
  version: string;
  stack: "Atlas";
  authority: "analysis_only";
  protected_operations: ["sludge_narrative"];
  subordination_notice: string;
};
export type AtlasReplayResponse = {
  status: "verified";
  bundle_id: string;
  bundle_hash: string;
  reconstructed_state_hash: string;
  item_counts: {
    audit_events: number;
    checkpoints: number;
    claims: number;
    graph_snapshots: number;
    projections: number;
  };
  audit_receipt_sha256: string;
  audited_at: string;
  subordination_notice: string;
  authority: "analysis_only";
  governance_verdict_created: false;
  execution_started: false;
};
export type AtlasProjectionEvidence = {
  source: string;
  tier: "A" | "B" | "C" | "D";
  confidence: number;
};
export type AtlasProjectionDriver = { name: string; value: number };
export type AtlasProjection = {
  id: string;
  initiated_by: string;
  claim_id: string;
  statement: string;
  claim_type: "factual" | "predictive" | "agency" | "causal" | "correlational";
  stack: string;
  evidence: AtlasProjectionEvidence[];
  drivers: AtlasProjectionDriver[];
  posterior: number;
  uncertainty: number;
  evidence_count: number;
  projection_sha256: string;
  input_sha256: string;
  output_sha256: string;
  audit_hash: string;
  created_at: string;
  subordination_notice: string;
  authority: "analysis_only";
  recommendation_created: false;
  governance_verdict_created: false;
  execution_started: false;
};
export type AtlasProjectionInput = {
  claim_id: string;
  statement: string;
  claim_type: AtlasProjection["claim_type"];
  stack: string;
  evidence: AtlasProjectionEvidence[];
  drivers: AtlasProjectionDriver[];
  idempotency_key: string;
};
export type AuthAccount = {
  id: string;
  username: string;
  display_name: string;
  role: "owner" | "administrator" | "operator" | "reviewer" | "auditor" | "viewer";
  actor_id: string | null;
  mfa_enabled: boolean;
  status: "active" | "disabled";
  must_change_password: boolean;
};
export type BootstrapStatus = {
  status: "required" | "closed" | "unconfigured";
  setup_secret_required: boolean;
};
export type Session = {
  account: AuthAccount;
  session_id: string;
  csrf_token: string;
  idle_expires_at: string;
  absolute_expires_at: string;
  mfa_verified_at: string | null;
};
export type BootstrapSession = Session & { recovery_codes: string[] };
export type SessionInfo = {
  id: string;
  current: boolean;
  created_at: string;
  last_seen_at: string;
  idle_expires_at: string;
  absolute_expires_at: string;
  user_agent: string;
  client_host: string;
  revoked: boolean;
  mfa_verified_at: string | null;
};
export type MfaStatus = { enabled: boolean; enrollment_pending: boolean };
export type MfaEnrollment = { secret: string; provisioning_uri: string };
export type ManagedAccount = AuthAccount & { created_at: string };
export type SecurityEvent = {
  id: number; event_type: string; account_id: string | null; occurred_at: string; source: string; detail: string;
};
export type WorkRequest = {
  id: string; created_by: string; title: string; operation: string; resource: string;
  input_schema_version: string; inputs: Record<string, string>; input_sha256: string;
  rationale: string; state: "submitted" | "reviewed_approve" | "reviewed_reject" | "needs_information" | "cancelled" | "execution_pending" | "executed" | "execution_blocked" | "execution_failed";
  created_at: string; updated_at: string;
};
export type WorkOperation = {
  id: string;
  label: string;
  description: string;
  resource_hint: string;
  schema_version: string;
  fields: Array<{
    id: string; label: string; description: string; placeholder: string; resource_prefix: string;
    min_length: number; max_length: number; pattern: string;
  }>;
  consequence: string;
};
export type WorkReview = {
  id: string;
  request_id: string;
  reviewer_account_id: string;
  decision: "approve_for_governance" | "reject" | "return_for_information" | "abstain";
  rationale: string;
  created_at: string;
  receipt_sha256: string;
  governance_verdict_created: false;
  execution_started: false;
};
export type WorkRequestDetail = {
  request: WorkRequest;
  reviews: WorkReview[];
  execution_receipt: ExecutionReceipt | null;
  execution_status: "not_started" | "running" | "executed" | "blocked" | "failed";
};
export type ExecutionReceipt = {
  request_id: string; attempt_id: string; module_id: string; initiated_by: string;
  status: "running" | "executed" | "blocked" | "failed"; action_id: string; outcome: string;
  reason: string; output: unknown; governance_evidence_sha256: string; event_hash: string;
  audit_hash: string; created_at: string; completed_at: string | null;
};
export type SwrScenario = {
  scenario_id: string; name: string; description: string; scenario_type: string;
  difficulty: number; round_number: number; expected_decision: string; tags: string[];
};
export type TaarReader = {
  id: string; task_id: string; description: string;
  classification_default: "OPEN" | "CONTROLLED" | "RESTRICTED" | "SECRET" | "PHANTOM" | "BLACK";
  timeout_seconds: number; evidence_scope: string[];
};
export type TaarStatus = {
  status: "available"; target_repository: string; target_path: string;
  facility_mode: "GREEN" | "YELLOW" | "ORANGE" | "RED" | "BLACKSITE";
  registry_valid: boolean; registry_validation_errors: number; readers: TaarReader[];
  report_only: true; browser_selects_target: false; browser_submits_commands: false;
  source_mutation_capability: false;
};
export type TaarFinding = {
  finding_id: string; severity: string; path: string | null; line: number | null; message: string;
};
export type TaarCommand = { command: string; exit_code: number; duration_ms: number };
export type TaarEvidence = {
  run_id: string; agent_id: string; task_id: string;
  classification: TaarReader["classification_default"];
  status: "admitted" | "denied" | "running" | "succeeded" | "failed" | "killed" | "quarantined";
  branch: string; commit: string; dirty_state_before: string; start_time: string; end_time: string;
  duration_ms: number; command_count: number; finding_count: number; evidence_hash: string;
  evidence_hash_valid: boolean; audit_record_hash: string | null; audit_record_hash_valid: boolean;
  details_redacted: boolean; findings: TaarFinding[]; commands: TaarCommand[]; uncertainty: string[];
  human_action_required: boolean; report_only: true; source_mutation_capability: false;
  governance_verdict_created: false; project_ai_execution_started: false;
};

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "/api";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  token?: string;
  csrf?: string;
};

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers();
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`);
  if (options.csrf) headers.set("X-CSRF-Token", options.csrf);
  if (options.body !== undefined) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? "GET",
    headers,
    credentials: "same-origin",
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  if (!response.ok) {
    const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, detail?.detail ?? `Request failed with HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export const gateway = {
  instance: () => requestJson<InstanceIdentity>("/api/v1/instance"),
  dashboard: () => requestJson<DashboardResponse>("/api/v1/dashboard"),
  modules: () => requestJson<{ modules: ModuleSurface[] }>("/api/v1/modules"),
  health: () => requestJson<Health>("/health/live"),
  replay: () => requestJson<ReplayStatus>("/replay/status"),
  dois: async () => (await requestJson<{ dois: DoiRecord[] }>("/dois")).dois,
  audit: (
    token?: string,
    limit = 100,
    filters: { offset?: number; query?: string; event?: string } = {},
  ) => {
    const parameters = new URLSearchParams({ limit: String(limit) });
    if (filters.offset) parameters.set("offset", String(filters.offset));
    if (filters.query?.trim()) parameters.set("query", filters.query.trim());
    if (filters.event?.trim()) parameters.set("event", filters.event.trim());
    return requestJson<AuditResponse>(`/audit?${parameters.toString()}`, { token });
  },
  auth: {
    bootstrapStatus: () => requestJson<BootstrapStatus>("/api/v1/auth/bootstrap-status"),
    bootstrap: (payload: {
      setup_secret: string;
      username: string;
      display_name: string;
      password: string;
      actor_id?: string;
    }) => requestJson<BootstrapSession>("/api/v1/auth/bootstrap", { method: "POST", body: payload }),
    login: (username: string, password: string, totpCode?: string) =>
      requestJson<Session>("/api/v1/auth/login", {
        method: "POST", body: { username, password, totp_code: totpCode || undefined },
      }),
    session: () => requestJson<Session>("/api/v1/auth/session"),
    refresh: (csrf: string) =>
      requestJson<Session>("/api/v1/auth/session/refresh", { method: "POST", csrf }),
    logout: (csrf: string) =>
      requestJson<{ message: string }>("/api/v1/auth/logout", { method: "POST", csrf }),
    sessions: () => requestJson<{ sessions: SessionInfo[] }>("/api/v1/auth/sessions"),
    revokeSession: (sessionId: string, csrf: string) =>
      requestJson<{ message: string }>(`/api/v1/auth/sessions/${encodeURIComponent(sessionId)}`, {
        method: "DELETE", csrf,
      }),
    changePassword: (currentPassword: string, newPassword: string, csrf: string) =>
      requestJson<{ message: string }>("/api/v1/auth/password/change", {
        method: "POST", csrf, body: { current_password: currentPassword, new_password: newPassword },
      }),
    mfaStatus: () => requestJson<MfaStatus>("/api/v1/auth/mfa"),
    mfaEnroll: (currentPassword: string, csrf: string) =>
      requestJson<MfaEnrollment>("/api/v1/auth/mfa/enroll", {
        method: "POST", csrf, body: { current_password: currentPassword },
      }),
    mfaConfirm: (code: string, csrf: string) =>
      requestJson<{ message: string }>("/api/v1/auth/mfa/confirm", {
        method: "POST", csrf, body: { code },
      }),
    mfaStepUp: (code: string, csrf: string) =>
      requestJson<{ message: string }>("/api/v1/auth/mfa/step-up", {
        method: "POST", csrf, body: { code },
      }),
    mfaDisable: (currentPassword: string, code: string, csrf: string) =>
      requestJson<{ message: string }>("/api/v1/auth/mfa", {
        method: "DELETE", csrf, body: { current_password: currentPassword, code },
      }),
    recoveryStart: (username: string) =>
      requestJson<{ message: string }>("/api/v1/auth/recovery/start", {
        method: "POST", body: { username },
      }),
    recoveryComplete: (username: string, recoveryCode: string, newPassword: string) =>
      requestJson<{ message: string }>("/api/v1/auth/recovery/complete", {
        method: "POST", body: { username, recovery_code: recoveryCode, new_password: newPassword },
      }),
  },
  admin: {
    accounts: () => requestJson<{ accounts: ManagedAccount[] }>("/api/v1/admin/accounts"),
    createAccount: (payload: {
      username: string; display_name: string; password: string;
      role: Exclude<AuthAccount["role"], "owner">; actor_id?: string;
    }, csrf: string) => requestJson<{ account: ManagedAccount; recovery_codes: string[] }>(
      "/api/v1/admin/accounts", { method: "POST", csrf, body: payload },
    ),
    changeRole: (accountId: string, role: Exclude<AuthAccount["role"], "owner">, csrf: string) =>
      requestJson<{ message: string }>(`/api/v1/admin/accounts/${encodeURIComponent(accountId)}/role`, {
        method: "POST", csrf, body: { role },
      }),
    changeStatus: (accountId: string, enabled: boolean, csrf: string) =>
      requestJson<{ message: string }>(`/api/v1/admin/accounts/${encodeURIComponent(accountId)}/status`, {
        method: "POST", csrf, body: { enabled },
      }),
    securityEvents: () => requestJson<{ events: SecurityEvent[] }>("/api/v1/admin/security-events"),
  },
  work: {
    operations: () => requestJson<{ operations: WorkOperation[]; execution_started: false }>("/api/v1/work/operations"),
    requests: () => requestJson<{ requests: WorkRequest[]; review_is_not_governance: true }>("/api/v1/work/requests"),
    detail: (requestId: string) =>
      requestJson<WorkRequestDetail>(`/api/v1/work/requests/${encodeURIComponent(requestId)}`),
    create: (payload: { title: string; operation: string; inputs: Record<string, string>; rationale: string; idempotency_key: string }, csrf: string) =>
      requestJson<WorkRequest>("/api/v1/work/requests", { method: "POST", csrf, body: payload }),
    cancel: (requestId: string, csrf: string) =>
      requestJson<WorkRequest>(`/api/v1/work/requests/${encodeURIComponent(requestId)}/cancel`, { method: "POST", csrf }),
    review: (requestId: string, decision: "approve_for_governance" | "reject" | "return_for_information" | "abstain", rationale: string, csrf: string) =>
      requestJson<WorkReview>(`/api/v1/work/requests/${encodeURIComponent(requestId)}/reviews`, {
        method: "POST", csrf, body: { decision, rationale },
      }),
  },
  swr: {
    scenarios: () => requestJson<{ scenarios: SwrScenario[]; execution_gate_configured: boolean; authority_boundary: string }>("/api/v1/modules/swr/scenarios"),
    execute: (requestId: string, scenarioId: string, decision: string, csrf: string) =>
      requestJson<{ receipt: ExecutionReceipt; reused_existing_receipt: boolean }>(`/api/v1/work/requests/${encodeURIComponent(requestId)}/execute/swr`, {
        method: "POST", csrf, body: { scenario_id: scenarioId, decision },
      }),
  },
  atlas: {
    status: () => requestJson<AtlasStatus>("/atlas/status"),
    projections: (limit = 50) =>
      requestJson<{ projections: AtlasProjection[] }>(`/api/v1/modules/atlas/projections?limit=${limit}`),
    projection: (receiptId: string) =>
      requestJson<AtlasProjection>(`/api/v1/modules/atlas/projections/${encodeURIComponent(receiptId)}`),
    createProjection: (payload: AtlasProjectionInput, csrf: string) =>
      requestJson<{ projection: AtlasProjection; reused_existing_receipt: boolean }>(
        "/api/v1/modules/atlas/projections",
        { method: "POST", csrf, body: payload },
      ),
    replay: (bundle: Record<string, unknown>, csrf: string) =>
      requestJson<AtlasReplayResponse>("/api/v1/modules/atlas/replay", {
        method: "POST", csrf, body: { bundle },
      }),
  },
  taar: {
    status: () => requestJson<TaarStatus>("/api/v1/modules/taar/status"),
    runs: (limit = 50) =>
      requestJson<{ runs: TaarEvidence[]; redaction_boundary: string }>(
        `/api/v1/modules/taar/runs?limit=${limit}`,
      ),
    run: (runId: string) =>
      requestJson<TaarEvidence>(`/api/v1/modules/taar/runs/${encodeURIComponent(runId)}`),
    createRun: (agentId: string, idempotencyKey: string, csrf: string) =>
      requestJson<{ run: TaarEvidence; reused_existing_receipt: boolean }>(
        "/api/v1/modules/taar/runs",
        { method: "POST", csrf, body: { agent_id: agentId, idempotency_key: idempotencyKey } },
      ),
  },
};
