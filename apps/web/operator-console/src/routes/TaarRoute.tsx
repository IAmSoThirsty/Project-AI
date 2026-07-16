import { gateway, type TaarEvidence } from "@project-ai/web-shared/api";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clipboard,
  FileSearch,
  Fingerprint,
  Info,
  LockKeyhole,
  Server,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

const shortHash = (value: string) => `${value.slice(0, 10)}…${value.slice(-8)}`;

function IntegrityHash({ label, value, valid }: { label: string; value: string | null; valid: boolean }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
  }
  return <div className="taar-hash"><div><span>{label}</span><strong className={valid ? "is-valid" : "is-invalid"}>{valid ? "Verified" : "Unverified"}</strong></div><code title={value ?? "No audit record"}>{value ? shortHash(value) : "Not available"}</code><button type="button" disabled={!value} onClick={copy} aria-label={`Copy ${label.toLowerCase()}`}><Clipboard aria-hidden="true" /></button><small aria-live="polite">{copied ? "Copied" : ""}</small></div>;
}

function LatestEvidence({ run }: { run: TaarEvidence | null }) {
  if (!run) return <section className="taar-latest taar-empty"><FileSearch aria-hidden="true" /><h2>Latest evidence</h2><p>Run a registered reader to create a hash-sealed evidence bundle.</p></section>;
  return <section className="taar-latest" aria-live="polite">
    <header><CheckCircle2 aria-hidden="true" /><div><h2>Latest evidence</h2><span>{run.agent_id}</span></div><strong className={`taar-status taar-status-${run.status}`}>{run.status}</strong></header>
    <div className="taar-result-metrics"><div><span>Classification</span><strong>{run.classification}</strong></div><div><span>Findings</span><strong>{run.finding_count}</strong></div><div><span>Commands</span><strong>{run.command_count}</strong></div><div><span>Duration</span><strong>{run.duration_ms} ms</strong></div></div>
    <IntegrityHash label="Evidence SHA-256" value={run.evidence_hash} valid={run.evidence_hash_valid} />
    <IntegrityHash label="TAAR audit hash" value={run.audit_record_hash} valid={run.audit_record_hash_valid} />
    <div className="taar-result-boundary"><LockKeyhole aria-hidden="true" /><p><strong>Report-only boundary</strong>No source-mutation capability, governance verdict, or Project-AI execution was created.</p></div>
  </section>;
}

export function TaarRoute() {
  const auth = useAuth();
  const statusQuery = useQuery({ queryKey: ["taar-status"], queryFn: gateway.taar.status });
  const historyQuery = useQuery({ queryKey: ["taar-runs"], queryFn: () => gateway.taar.runs() });
  const [agentId, setAgentId] = useState("");
  const [latest, setLatest] = useState<TaarEvidence | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const status = statusQuery.data;
  const runs = historyQuery.data?.runs ?? [];
  const selected = status?.readers.find((reader) => reader.id === agentId);
  const canRun = ["owner", "administrator", "operator"].includes(auth.session?.account.role ?? "");

  useEffect(() => {
    if (!agentId && status?.readers[0]) setAgentId(status.readers[0].id);
  }, [agentId, status]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!agentId) return;
    setError("");
    setSubmitting(true);
    try {
      const response = await gateway.taar.createRun(agentId, crypto.randomUUID(), auth.csrf);
      setLatest(response.run);
      setExpanded(response.run.run_id);
      await historyQuery.refetch();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "TAAR inspection failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return <div className="console-page taar-page">
    <PageHeading title="TAAR Inspection Console" description="Run registered report-only readers and inspect hash-sealed evidence without granting repository mutation authority." />
    <div className="taar-boundary" role="note"><ShieldCheck aria-hidden="true" /><strong>Report only</strong><span>·</span><span>Server-configured target</span><span>·</span><span>No source mutation</span><span>·</span><span>No Project-AI governance verdict</span></div>
    {error ? <StatePanel title="Inspection rejected" tone="error">{error}</StatePanel> : null}
    {statusQuery.isError ? <StatePanel title="TAAR target unavailable" tone="error">{statusQuery.error.message}</StatePanel> : null}
    {historyQuery.isError ? <StatePanel title="Evidence history unavailable" tone="error">{historyQuery.error.message}</StatePanel> : null}
    <div className="taar-workspace">
      <form className="taar-request" onSubmit={submit}>
        <header><Activity aria-hidden="true" /><div><h2>Inspection request</h2><span>Only server-registered reader agents are available.</span></div></header>
        {status ? <div className="taar-target"><Server aria-hidden="true" /><div><span>Read-only target</span><strong>{status.target_repository}</strong><code title={status.target_path}>{status.target_path}</code></div><span className={`taar-facility facility-${status.facility_mode.toLowerCase()}`}>{status.facility_mode} facility</span></div> : <div className="taar-target-loading">Reading server target…</div>}
        <label>Registered reader<select value={agentId} onChange={(event) => setAgentId(event.target.value)} disabled={!status?.readers.length || submitting} required><option value="">Select a reader</option>{status?.readers.map((reader) => <option value={reader.id} key={reader.id}>{reader.id}</option>)}</select></label>
        {selected ? <div className="taar-reader-detail"><p>{selected.description}</p><dl><dt>Task</dt><dd>{selected.task_id}</dd><dt>Default classification</dt><dd>{selected.classification_default}</dd><dt>Timeout</dt><dd>{selected.timeout_seconds} seconds</dd></dl><div><span>Evidence scope</span>{selected.evidence_scope.map((scope) => <code key={scope}>{scope}</code>)}</div></div> : null}
        <button className="taar-submit" type="submit" disabled={!agentId || submitting || !canRun || !status?.registry_valid}><FileSearch aria-hidden="true" />{submitting ? "Running inspection…" : canRun ? "Run inspection" : "View only"}</button>
        <p className="taar-request-note"><Info aria-hidden="true" />This browser cannot submit repository paths, commands, capabilities, writers, or execution instructions.</p>
      </form>
      <LatestEvidence run={latest ?? runs[0] ?? null} />
    </div>
    <section className="taar-history">
      <header><Fingerprint aria-hidden="true" /><div><h2>Inspection history</h2><span>Hash-sealed evidence discovered in the configured TAAR store</span></div></header>
      {historyQuery.isLoading ? <StatePanel title="Loading inspection history">Verifying TAAR evidence and audit records…</StatePanel> : null}
      {!historyQuery.isLoading && !runs.length ? <StatePanel title="No inspections yet">Registered reader evidence will appear here after a successful run.</StatePanel> : null}
      {runs.length ? <div className="taar-table-wrap"><table><thead><tr><th>Reader</th><th>Status</th><th>Class</th><th>Findings</th><th>Integrity</th><th>Completed</th><th><span className="sr-only">Detail</span></th></tr></thead><tbody>{runs.map((run) => <EvidenceRow key={run.run_id} run={run} expanded={expanded === run.run_id} onToggle={() => setExpanded((current) => current === run.run_id ? null : run.run_id)} />)}</tbody></table></div> : null}
      {historyQuery.data ? <p className="taar-redaction"><LockKeyhole aria-hidden="true" />{historyQuery.data.redaction_boundary}</p> : null}
    </section>
  </div>;
}

function EvidenceRow({ run, expanded, onToggle }: { run: TaarEvidence; expanded: boolean; onToggle: () => void }) {
  const integrity = run.evidence_hash_valid && run.audit_record_hash_valid;
  return <><tr><td><strong>{run.agent_id}</strong><small>{run.task_id}</small></td><td><span className={`taar-status taar-status-${run.status}`}>{run.status}</span></td><td>{run.classification}</td><td>{run.finding_count}</td><td><span className={integrity ? "integrity-good" : "integrity-bad"}>{integrity ? "Verified" : "Review"}</span></td><td><time dateTime={run.end_time}>{new Date(run.end_time).toLocaleString()}</time></td><td><button type="button" onClick={onToggle} aria-expanded={expanded} aria-label={`${expanded ? "Hide" : "View"} evidence for ${run.agent_id}`}>{expanded ? <ChevronDown aria-hidden="true" /> : <ChevronRight aria-hidden="true" />}</button></td></tr>{expanded ? <tr className="taar-detail-row"><td colSpan={7}><div>{run.details_redacted ? <section className="taar-redacted"><LockKeyhole aria-hidden="true" /><h3>Evidence details withheld</h3><p>Classification or integrity policy prevents this interface from showing commands, findings, and uncertainty.</p></section> : <section><h3>Findings</h3>{run.findings.length ? <ul>{run.findings.map((finding) => <li key={finding.finding_id}><strong>{finding.severity}</strong><span>{finding.message}</span><code>{finding.path ?? "repository"}{finding.line ? `:${finding.line}` : ""}</code></li>)}</ul> : <p>No findings were reported.</p>}<h3>Commands</h3><ul>{run.commands.map((command) => <li key={command.command}><code>{command.command}</code><span>Exit {command.exit_code} · {command.duration_ms} ms</span></li>)}</ul></section>}<section><h3>Run context</h3><dl><dt>Branch</dt><dd>{run.branch}</dd><dt>Commit</dt><dd><code>{run.commit}</code></dd><dt>Starting state</dt><dd>{run.dirty_state_before}</dd><dt>Run ID</dt><dd><code>{run.run_id}</code></dd></dl><IntegrityHash label="Evidence SHA-256" value={run.evidence_hash} valid={run.evidence_hash_valid} /><IntegrityHash label="TAAR audit hash" value={run.audit_record_hash} valid={run.audit_record_hash_valid} /></section></div></td></tr> : null}</>;
}
