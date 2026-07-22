import {
  ApiError,
  gateway,
  type AtlasProjection,
  type AtlasProjectionDriver,
  type AtlasProjectionEvidence,
  type AtlasProjectionInput,
} from "@project-ai/web-shared/api";
import { useQuery } from "@tanstack/react-query";
import { Activity, CheckCircle2, ChevronDown, ChevronRight, Clipboard, FileCheck2, Info, Plus, Sparkles, Trash2 } from "lucide-react";
import { useState, type FormEvent } from "react";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

const claimTypes: AtlasProjectionInput["claim_type"][] = ["factual", "predictive", "agency", "causal", "correlational"];
const shortHash = (value: string) => `${value.slice(0, 10)}…${value.slice(-8)}`;

function HashValue({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() { await navigator.clipboard.writeText(value); setCopied(true); }
  return <div className="projection-hash"><span>{label}</span><code title={value}>{value}</code><button type="button" onClick={copy} aria-label={`Copy ${label.toLowerCase()}`}><Clipboard aria-hidden="true" /></button><small aria-live="polite">{copied ? "Copied" : ""}</small></div>;
}

function ProjectionResult({ projection }: { projection: AtlasProjection }) {
  return <section className="projection-result" aria-live="polite">
    <header><CheckCircle2 aria-hidden="true" /><div><h2>Projection result</h2><span>Durable analytical receipt</span></div></header>
    <div className="projection-metrics"><div><span>Posterior</span><strong>{projection.posterior.toFixed(3)}</strong></div><div><span>Uncertainty</span><strong>{projection.uncertainty.toFixed(3)}</strong></div><div><span>Evidence</span><strong>{projection.evidence_count}</strong></div><div><span>Stack</span><strong>{projection.stack}</strong></div></div>
    <HashValue label="Projection SHA-256" value={projection.projection_sha256} />
    <p><Info aria-hidden="true" />This projection is analytical evidence only. It is not a decision or authority grant.</p>
    <footer><FileCheck2 aria-hidden="true" /><span>Audit receipt</span><code>{shortHash(projection.audit_hash)}</code><time dateTime={projection.created_at}>{new Date(projection.created_at).toLocaleString()}</time></footer>
  </section>;
}

export function AtlasProjectionsRoute() {
  const auth = useAuth();
  const history = useQuery({ queryKey: ["atlas-projections"], queryFn: () => gateway.atlas.projections(), retry: false });
  const [claimId, setClaimId] = useState("claim-projection-1");
  const [claimType, setClaimType] = useState<AtlasProjectionInput["claim_type"]>("predictive");
  const [stack, setStack] = useState("RS");
  const [statement, setStatement] = useState("Source-backed controls remain effective under the evaluated conditions.");
  const [evidence, setEvidence] = useState<AtlasProjectionEvidence[]>([{ source: "control-test", tier: "A", confidence: 0.9 }, { source: "replay-test", tier: "B", confidence: 0.8 }]);
  const [drivers, setDrivers] = useState<AtlasProjectionDriver[]>([{ name: "control_strength", value: 0.85 }, { name: "source_quality", value: 0.95 }]);
  const [result, setResult] = useState<AtlasProjection | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateEvidence(index: number, patch: Partial<AtlasProjectionEvidence>) { setEvidence((items) => items.map((item, position) => position === index ? { ...item, ...patch } : item)); }
  function updateDriver(index: number, patch: Partial<AtlasProjectionDriver>) { setDrivers((items) => items.map((item, position) => position === index ? { ...item, ...patch } : item)); }
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setSubmitting(true);
    try {
      const response = await gateway.atlas.createProjection({ claim_id: claimId, statement, claim_type: claimType, stack, evidence, drivers, idempotency_key: crypto.randomUUID() }, auth.csrf);
      setResult(response.projection); setExpanded(response.projection.id); await history.refetch();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Atlas projection failed."); }
    finally { setSubmitting(false); }
  }

  const projections = history.data?.projections ?? [];
  const initialReady = !history.isLoading && !history.isError;
  const accessDenied = history.error instanceof ApiError && history.error.status === 403;
  return <div className="console-page atlas-projections-page">
    <PageHeading title="Atlas Projections" description="Create deterministic evidence-weighted projections and inspect durable analysis receipts." />
    <div className="atlas-boundary" role="note"><Info aria-hidden="true" /><strong>Analysis only</strong><span>·</span><span>Not a recommendation</span><span>·</span><span>No governance verdict</span><span>·</span><span>No execution</span></div>
    {error ? <StatePanel title="Projection rejected" tone="error">{error}</StatePanel> : null}
    {history.isLoading ? <StatePanel title="Loading Atlas projections">Reading durable analysis receipts before exposing projection controls.</StatePanel> : null}
    {history.isError ? <StatePanel title={accessDenied ? "Atlas access restricted" : "Projection history unavailable"} tone="error">{accessDenied ? "Your interface role is not authorized to run Atlas analysis. No projection inputs, history, or creation controls are shown." : "No projection inputs, history, or creation controls are shown because the initial read failed."} {history.error.message}</StatePanel> : null}
    {initialReady ? <div className="projection-workspace">
      <form className="projection-form" onSubmit={submit}>
        <header><Sparkles aria-hidden="true" /><div><h2>Projection inputs</h2><span>All inputs are sealed into the durable receipt.</span></div></header>
        <div className="projection-core-fields"><label>Claim ID<input value={claimId} onChange={(event) => setClaimId(event.target.value)} pattern="[A-Za-z0-9][A-Za-z0-9_.\-]*" maxLength={128} required /></label><label>Claim type<select value={claimType} onChange={(event) => setClaimType(event.target.value as AtlasProjectionInput["claim_type"])}>{claimTypes.map((item) => <option key={item}>{item}</option>)}</select></label><label>Stack<select value={stack} onChange={(event) => setStack(event.target.value)}><option>RS</option><option>SS</option><option>TS-analysis</option></select></label></div>
        <label>Claim statement<textarea value={statement} onChange={(event) => setStatement(event.target.value)} maxLength={4096} required /></label>
        <fieldset><legend>Evidence</legend>{evidence.map((item, index) => <div className="projection-row projection-evidence-row" key={index}><label>Source<input value={item.source} onChange={(event) => updateEvidence(index, { source: event.target.value })} maxLength={256} required /></label><label>Tier<select value={item.tier} onChange={(event) => updateEvidence(index, { tier: event.target.value as AtlasProjectionEvidence["tier"] })}>{["A", "B", "C", "D"].map((tier) => <option key={tier}>{tier}</option>)}</select></label><label>Confidence<input type="number" min="0" max="1" step="0.01" value={item.confidence} onChange={(event) => updateEvidence(index, { confidence: Number(event.target.value) })} required /></label><button type="button" onClick={() => setEvidence((items) => items.filter((_, position) => position !== index))} aria-label={`Remove evidence ${index + 1}`}><Trash2 aria-hidden="true" /></button></div>)}<button className="projection-add" type="button" disabled={evidence.length >= 12} onClick={() => setEvidence((items) => [...items, { source: "", tier: "B", confidence: 0.5 }])}><Plus aria-hidden="true" />Add evidence</button></fieldset>
        <fieldset><legend>Drivers</legend>{drivers.map((item, index) => <div className="projection-row projection-driver-row" key={index}><label>Name<input value={item.name} onChange={(event) => updateDriver(index, { name: event.target.value })} pattern="[A-Za-z][A-Za-z0-9_.\-]*" maxLength={64} required /></label><label>Value<input type="number" min="0" max="1" step="0.01" value={item.value} onChange={(event) => updateDriver(index, { value: Number(event.target.value) })} required /></label><button type="button" disabled={drivers.length === 1} onClick={() => setDrivers((items) => items.filter((_, position) => position !== index))} aria-label={`Remove driver ${index + 1}`}><Trash2 aria-hidden="true" /></button></div>)}<button className="projection-add" type="button" disabled={drivers.length >= 12} onClick={() => setDrivers((items) => [...items, { name: "", value: 0.5 }])}><Plus aria-hidden="true" />Add driver</button></fieldset>
        <button className="atlas-submit" type="submit" disabled={submitting}><Activity aria-hidden="true" />{submitting ? "Creating projection…" : "Create projection"}</button>
      </form>
      <aside>{result ? <ProjectionResult projection={result} /> : <section className="projection-empty"><Activity aria-hidden="true" /><h2>Projection result</h2><p>Submit the evidence model to create a deterministic, analysis-only receipt.</p></section>}</aside>
    </div> : null}
    {initialReady ? <section className="projection-history"><header><FileCheck2 aria-hidden="true" /><div><h2>Projection history</h2><span>Durable receipts from the configured human-state store</span></div></header>{projections.length === 0 ? <StatePanel title="No projections yet">Created projections will appear here with their evidence hashes.</StatePanel> : null}{projections.length ? <div className="projection-table-wrap"><table><thead><tr><th>Claim ID</th><th>Type</th><th>Posterior</th><th>Uncertainty</th><th>Evidence</th><th>Stack</th><th>Created</th><th>Receipt</th><th><span className="sr-only">Detail</span></th></tr></thead><tbody>{projections.map((projection) => <ProjectionHistoryRow key={projection.id} projection={projection} expanded={expanded === projection.id} onToggle={() => setExpanded((current) => current === projection.id ? null : projection.id)} />)}</tbody></table></div> : null}</section> : null}
  </div>;
}

function ProjectionHistoryRow({ projection, expanded, onToggle }: { projection: AtlasProjection; expanded: boolean; onToggle: () => void }) {
  return <><tr><td><strong>{projection.claim_id}</strong></td><td>{projection.claim_type}</td><td>{projection.posterior.toFixed(3)}</td><td>{projection.uncertainty.toFixed(3)}</td><td>{projection.evidence_count}</td><td>{projection.stack}</td><td><time dateTime={projection.created_at}>{new Date(projection.created_at).toLocaleDateString()}</time></td><td><code>{shortHash(projection.audit_hash)}</code></td><td><button type="button" onClick={onToggle} aria-expanded={expanded} aria-label={`${expanded ? "Hide" : "View"} detail for ${projection.claim_id}`}>{expanded ? <ChevronDown aria-hidden="true" /> : <ChevronRight aria-hidden="true" />}</button></td></tr>{expanded ? <tr className="projection-detail-row"><td colSpan={9}><div><section><h3>Claim statement</h3><p>{projection.statement}</p><h3>Evidence</h3><ul>{projection.evidence.map((item) => <li key={`${item.source}-${item.tier}`}>{item.source} · Tier {item.tier} · {item.confidence.toFixed(2)}</li>)}</ul><h3>Drivers</h3><ul>{projection.drivers.map((item) => <li key={item.name}>{item.name} · {item.value.toFixed(2)}</li>)}</ul></section><section><HashValue label="Input SHA-256" value={projection.input_sha256} /><HashValue label="Output SHA-256" value={projection.output_sha256} /><HashValue label="Projection SHA-256" value={projection.projection_sha256} /><HashValue label="Audit hash" value={projection.audit_hash} /><dl><dt>Created by</dt><dd>{projection.initiated_by}</dd><dt>Authority</dt><dd>Analysis only</dd></dl></section></div></td></tr> : null}</>;
}
