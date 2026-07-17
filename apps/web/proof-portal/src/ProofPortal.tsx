import { Activity, FileKey, Fingerprint, Lock, ShieldAlert, ShieldCheck } from "lucide-react";
import { type FormEvent, useEffect, useMemo, useState } from "react";
import {
  type AuditResponse,
  type DashboardResponse,
  ErrorPanel,
  type InstanceIdentity,
  LoadingPanel,
  type ModuleSurface,
  PortalShell,
  StatusPill,
  gateway,
} from "@project-ai/web-shared";

const nav = [
  { id: "status", label: "Live evidence" },
  { id: "boundaries", label: "Authority boundaries" },
  { id: "audit", label: "Audit evidence" },
];

const AUDIT_EVENTS = [
  { value: "", label: "All events" },
  { value: "chimera.governance_denial", label: "Governance denials" },
  { value: "chimera.canary_hit", label: "Canary fingerprints" },
  { value: "chimera.verdict", label: "Canonical verdicts" },
  { value: "atlas.sludge_narrative", label: "Sludge generation metadata" },
];

const surfaceIcons = {
  gateway: Activity,
  replay: ShieldCheck,
  audit_chain: Fingerprint,
  evidence: FileKey,
} as const;

function pillStatus(status: DashboardResponse["surfaces"][number]["status"]): string {
  if (status === "healthy") return "pass";
  if (status === "not_run") return "not_run";
  return "fail";
}

export function ProofPortal() {
  const [active, setActive] = useState("status");
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [instance, setInstance] = useState<InstanceIdentity | null>(null);
  const [modules, setModules] = useState<ModuleSurface[] | null>(null);
  const [publicError, setPublicError] = useState("");
  const [token, setToken] = useState("");
  const [eventFilter, setEventFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [auditError, setAuditError] = useState("");
  const [auditLoading, setAuditLoading] = useState(false);

  useEffect(() => {
    let current = true;
    Promise.all([gateway.dashboard(), gateway.instance(), gateway.modules()])
      .then(([nextDashboard, nextInstance, nextModules]) => {
        if (current) {
          setDashboard(nextDashboard);
          setInstance(nextInstance);
          setModules(nextModules.modules);
        }
      })
      .catch((reason: unknown) => {
        if (current) setPublicError(reason instanceof Error ? reason.message : "Gateway unavailable");
      });
    return () => { current = false; };
  }, []);

  const counts = useMemo(() => {
    const result = { denials: 0, canaries: 0, verdicts: 0 };
    for (const record of audit?.records ?? []) {
      if (record.event === "chimera.governance_denial") result.denials += 1;
      if (record.event === "chimera.canary_hit") result.canaries += 1;
      if (record.event === "chimera.verdict") result.verdicts += 1;
    }
    return result;
  }, [audit]);

  async function loadAudit(event?: FormEvent) {
    event?.preventDefault();
    const credential = token.trim();
    if (!credential) { setAuditError("Enter an API token to read protected audit evidence."); return; }
    setToken("");
    setAuditLoading(true);
    setAuditError("");
    try { setAudit(await gateway.audit(credential, 100, { offset, event: eventFilter })); }
    catch (reason) { setAudit(null); setAuditError(reason instanceof Error ? reason.message : "Audit unavailable"); }
    finally { setAuditLoading(false); }
  }

  return (
    <PortalShell lane="Proof" active={active} items={nav} onNavigate={setActive}>
      {active === "status" && (
        <>
          <section className="hero portal-hero proof-surface">
            <div className="wrap hero-grid">
              <div className="hero-copy-block">
                <div className="eyebrow">Replay / audit / denial evidence</div>
                <h1><span className="gradient-text">Proof is a runtime surface.</span> Not a release claim.</h1>
                <p className="hero-copy">Every figure on this page is a live gateway response. A surface that has not run says so; nothing here is narrated.</p>
                <div className="hero-actions">
                  <button className="button primary" onClick={() => setActive("boundaries")}>Inspect authority boundaries</button>
                  <button className="button" onClick={() => setActive("audit")}>Inspect audit chain</button>
                </div>
              </div>
              <aside className="hero-panel" aria-label="Proof status">
                <div className="panel-topline"><span className="status-dot" /> evidence boundary</div>
                {publicError ? <ErrorPanel message={publicError} /> : dashboard ? (
                  <div className="command-list">
                    {dashboard.surfaces.map((surface) => {
                      const Icon = surfaceIcons[surface.id];
                      return (
                        <div className="command-row" key={surface.id}>
                          <Icon size={17} />
                          <code>{surface.id}</code>
                          <StatusPill status={pillStatus(surface.status)} label={surface.metric} />
                        </div>
                      );
                    })}
                  </div>
                ) : <LoadingPanel label="Reading proof status" />}
              </aside>
            </div>
          </section>
          <section className="section dark-ridge">
            <div className="wrap">
              <div className="section-head centered">
                <div className="eyebrow">Current checkpoint</div>
                <h2>Evidence says only what has actually run.</h2>
                <p>{dashboard?.authority_boundary ?? "Awaiting the gateway's own authority statement."}</p>
              </div>
              <div className="proof-stats">
                {(dashboard?.surfaces ?? []).map((surface) => (
                  <article className="proof-stat" key={surface.id}>
                    <span className="record-meta">{surface.label}</span>
                    <strong>{surface.metric}</strong>
                    <span>{surface.detail}</span>
                  </article>
                ))}
                <article className="proof-stat">
                  <span className="record-meta">DOI evidence</span>
                  <strong>{dashboard?.doi_records ?? "--"}</strong>
                  <span>Published research records</span>
                </article>
              </div>
            </div>
          </section>
        </>
      )}

      {active === "boundaries" && (
        <section className="section proof-surface">
          <div className="wrap">
            <div className="section-head">
              <div>
                <div className="eyebrow">Authority boundary</div>
                <h1>What the browser can never hold.</h1>
                <p>These constants come from the gateway's own instance contract, not from copy. The negative capabilities are frozen response fields.</p>
              </div>
              {instance && <StatusPill status="pass" label={instance.deployment} />}
            </div>
            {publicError && <ErrorPanel message={publicError} />}
            {!publicError && !instance && <LoadingPanel label="Reading instance contract" />}
            {instance && (
              <>
                <div className="proof-stats" style={{ marginTop: 28 }}>
                  <article className="proof-stat"><Lock size={20} /><strong>cloud_login: false</strong><span>No cloud identity exists</span></article>
                  <article className="proof-stat"><Lock size={20} /><strong>browser_machine_identity: false</strong><span>Sessions are human identity only</span></article>
                  <article className="proof-stat"><Lock size={20} /><strong>browser_execution_capability: false</strong><span>No capability token ever reaches a browser</span></article>
                </div>
                <div className="section-head" style={{ marginTop: 42 }}>
                  <div><div className="eyebrow">Human access path</div><h2>Identity never becomes authority.</h2></div>
                </div>
                <div className="command-list">
                  <div className="command-row"><code>{instance.human_access_path.join(" -> ")}</code></div>
                  <div className="command-row"><code>{instance.governed_execution_path.join(" -> ")}</code><StatusPill status="pass" label="server-side only" /></div>
                </div>
                <div className="section-head" style={{ marginTop: 42 }}>
                  <div><div className="eyebrow">Module authority matrix</div><h2>{modules?.length ?? 0} modules, each with its stated authority.</h2><p>Live from the gateway catalog: maturity and interface status are reported, never assumed.</p></div>
                </div>
                <div className="audit-list">
                  {(modules ?? []).map((module) => (
                    <article className="audit-row" key={module.id}>
                      <strong>{module.label}</strong>
                      <code>{module.maturity} / {module.interface_status}</code>
                      <span>{module.authority}</span>
                    </article>
                  ))}
                </div>
              </>
            )}
          </div>
        </section>
      )}

      {active === "audit" && (
        <section className="section proof-surface">
          <div className="wrap">
            <div className="section-head"><div><div className="eyebrow">Protected evidence</div><h1>Chimera audit viewer.</h1><p>The token is held only for the request, sent to the configured API, and then cleared.</p></div>{audit && <StatusPill status="pass" label="Chain verified" />}</div>
            <form className="token-form" onSubmit={loadAudit}>
              <label><span className="sr-only">API token</span><input type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} placeholder="PROJECT_AI_API_TOKEN" aria-label="API token" /></label>
              <label><span className="sr-only">Event filter</span>
                <select aria-label="Event filter" value={eventFilter} onChange={(event) => setEventFilter(event.target.value)}>
                  {AUDIT_EVENTS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                </select>
              </label>
              <label><span className="sr-only">Result offset</span><input type="number" min={0} step={100} value={offset} onChange={(event) => setOffset(Math.max(0, Number(event.target.value) || 0))} aria-label="Result offset" /></label>
              <button type="submit" disabled={auditLoading}>{auditLoading ? "Verifying" : "Load evidence"}</button>
            </form>
            {auditError && <div style={{ marginTop: 18 }}><ErrorPanel message={auditError} /></div>}
            {auditLoading && <div style={{ marginTop: 18 }}><LoadingPanel label="Verifying audit chain" /></div>}
            {audit && (
              <><div className="proof-stats" style={{ marginTop: 28 }}><article className="proof-stat"><ShieldAlert size={20} /><strong>{counts.denials}</strong><span>Governance denials</span></article><article className="proof-stat"><Fingerprint size={20} /><strong>{counts.canaries}</strong><span>Canary fingerprints</span></article><article className="proof-stat"><FileKey size={20} /><strong>{counts.verdicts}</strong><span>Canonical verdicts</span></article></div><div className="section-head" style={{ marginTop: 42 }}><div><div className="eyebrow">Append-only records</div><h2>{audit.filtered_count} matching of {audit.count} verified entries</h2><p>Showing up to {audit.limit} from offset {audit.offset}. Re-enter the operator token to change the filter or page.</p></div></div><div className="audit-list">{audit.records.map((record) => <article className="audit-row" key={String(record.hash)}><strong>{String(record.event)}</strong><code>{String(record.action_id ?? record.canary_sha256 ?? record.narrative_id ?? "evidence")}</code><span>{String(record.timestamp)}</span></article>)}</div>{audit.records.length === 0 && <div className="empty-panel">No verified entries match this filter and offset.</div>}</>
            )}
          </div>
        </section>
      )}
    </PortalShell>
  );
}
