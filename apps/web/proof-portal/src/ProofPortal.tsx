import { Activity, FileKey, Fingerprint, ShieldAlert, ShieldCheck } from "lucide-react";
import { type FormEvent, useEffect, useMemo, useState } from "react";
import {
  type AuditResponse,
  ErrorPanel,
  type Health,
  LoadingPanel,
  PortalShell,
  type ReplayStatus,
  StatusPill,
  gateway,
} from "@project-ai/web-shared";

const nav = [
  { id: "status", label: "System status" },
  { id: "audit", label: "Audit evidence" },
];

export function ProofPortal() {
  const [active, setActive] = useState("status");
  const [health, setHealth] = useState<Health | null>(null);
  const [replay, setReplay] = useState<ReplayStatus | null>(null);
  const [publicError, setPublicError] = useState("");
  const [token, setToken] = useState("");
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [auditError, setAuditError] = useState("");
  const [auditLoading, setAuditLoading] = useState(false);

  useEffect(() => {
    let current = true;
    Promise.all([gateway.health(), gateway.replay()])
      .then(([nextHealth, nextReplay]) => {
        if (current) { setHealth(nextHealth); setReplay(nextReplay); }
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
    try { setAudit(await gateway.audit(credential)); }
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
                <p className="hero-copy">Inspect current liveness and canonical replay state. Protected evidence remains token-bound and read-only in this portal.</p>
                <div className="hero-actions"><button className="button primary" onClick={() => setActive("audit")}>Inspect audit chain</button></div>
              </div>
              <aside className="hero-panel" aria-label="Proof status">
                <div className="panel-topline"><span className="status-dot" /> evidence boundary</div>
                {publicError ? <ErrorPanel message={publicError} /> : health && replay ? (
                  <div className="command-list">
                    <div className="command-row"><Activity size={17} /><code>gateway</code><StatusPill status="pass" label={health.status} /></div>
                    <div className="command-row"><ShieldCheck size={17} /><code>replay</code><StatusPill status={replay.status} label={replay.status} /></div>
                    <div className="command-row"><Fingerprint size={17} /><code>invariants</code><span>{replay.invariants_passed} / {replay.invariants_total}</span></div>
                  </div>
                ) : <LoadingPanel label="Reading proof status" />}
              </aside>
            </div>
          </section>
          <section className="section dark-ridge"><div className="wrap"><div className="section-head centered"><div className="eyebrow">Current checkpoint</div><h2>Evidence says only what has actually run.</h2><p>A not-run replay remains not-run. A protected audit remains unavailable until scoped operator credentials are presented.</p></div><div className="proof-stats"><article className="proof-stat"><span className="record-meta">Gateway</span><strong>{health?.status ?? "--"}</strong><span>Public liveness only</span></article><article className="proof-stat"><span className="record-meta">Replay</span><strong>{replay ? `${replay.invariants_passed}/${replay.invariants_total}` : "--"}</strong><span>{replay?.status ?? "Awaiting API"}</span></article><article className="proof-stat"><span className="record-meta">Audit</span><strong>{audit?.count ?? "--"}</strong><span>{audit ? "Verified chain entries" : "Token required"}</span></article></div></div></section>
        </>
      )}

      {active === "audit" && (
        <section className="section proof-surface">
          <div className="wrap">
            <div className="section-head"><div><div className="eyebrow">Protected evidence</div><h1>Chimera audit viewer.</h1><p>The token is held only for the request, sent to the configured API, and then cleared.</p></div>{audit && <StatusPill status="pass" label="Chain verified" />}</div>
            <form className="token-form" onSubmit={loadAudit}><label><span className="sr-only">API token</span><input type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} placeholder="PROJECT_AI_API_TOKEN" aria-label="API token" /></label><button type="submit" disabled={auditLoading}>{auditLoading ? "Verifying" : "Load evidence"}</button></form>
            {auditError && <div style={{ marginTop: 18 }}><ErrorPanel message={auditError} /></div>}
            {auditLoading && <div style={{ marginTop: 18 }}><LoadingPanel label="Verifying audit chain" /></div>}
            {audit && (
              <><div className="proof-stats" style={{ marginTop: 28 }}><article className="proof-stat"><ShieldAlert size={20} /><strong>{counts.denials}</strong><span>Governance denials</span></article><article className="proof-stat"><Fingerprint size={20} /><strong>{counts.canaries}</strong><span>Canary fingerprints</span></article><article className="proof-stat"><FileKey size={20} /><strong>{counts.verdicts}</strong><span>Canonical verdicts</span></article></div><div className="section-head" style={{ marginTop: 42 }}><div><div className="eyebrow">Append-only records</div><h2>{audit.count} verified entries</h2><p>Re-enter the operator token above to refresh this view.</p></div></div><div className="audit-list">{audit.records.map((record) => <article className="audit-row" key={String(record.hash)}><strong>{String(record.event)}</strong><code>{String(record.action_id ?? record.canary_sha256 ?? "evidence")}</code><span>{String(record.timestamp)}</span></article>)}</div>{audit.records.length === 0 && <div className="empty-panel">The verified chain is empty.</div>}</>
            )}
          </div>
        </section>
      )}
    </PortalShell>
  );
}
