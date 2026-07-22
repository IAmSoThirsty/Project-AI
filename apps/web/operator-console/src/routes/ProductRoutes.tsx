import { gateway, type DashboardResponse, type ModuleSurface, type WorkOperation, type WorkRequest, type WorkRequestDetail } from "@project-ai/web-shared/api";
import { Activity, Boxes, ClipboardList, Inbox } from "lucide-react";
import { Fragment, useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel, SurfaceStatus } from "../components";

export function WorkQueueRoute({ mode }: { mode: "inbox" | "requests" }) {
  const auth = useAuth();
  const [requests, setRequests] = useState<WorkRequest[]>([]);
  const [operations, setOperations] = useState<WorkOperation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [detail, setDetail] = useState<WorkRequestDetail | null>(null);
  const [form, setForm] = useState({ title: "", operation: "", inputs: {} as Record<string, string>, rationale: "" });
  const [review, setReview] = useState({ requestId: "", decision: "approve_for_governance" as "approve_for_governance" | "reject" | "return_for_information" | "abstain", rationale: "" });
  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setLoadError("");
    setError("");
    setNotice("");
    setRequests([]);
    setOperations([]);
    setDetail(null);
    const operationRequest = mode === "requests"
      ? gateway.work.operations()
      : Promise.resolve({ operations: [] as WorkOperation[], execution_started: false as const });
    Promise.all([gateway.work.requests(), operationRequest])
      .then(([requestResult, operationResult]) => {
        if (!active) return;
        setRequests(requestResult.requests);
        setOperations(operationResult.operations);
      })
      .catch((reason) => {
        if (active) setLoadError(reason instanceof Error ? reason.message : "Work queue unavailable");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => { active = false; };
  }, [mode]);
  const title = mode === "inbox" ? "My Inbox" : "Execution requests";
  const Icon = mode === "inbox" ? Inbox : ClipboardList;
  const selectedOperation = operations.find((operation) => operation.id === form.operation);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setNotice("");
    try {
      const created = await gateway.work.create({ ...form, idempotency_key: crypto.randomUUID() }, auth.csrf);
      setRequests((current) => [created, ...current]);
      setForm({ title: "", operation: "", inputs: {}, rationale: "" });
      setNotice("Request recorded. No governance verdict was created and no execution started.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Request submission failed"); }
  }
  async function decide(event: FormEvent) {
    event.preventDefault(); setError(""); setNotice("");
    try {
      await gateway.work.review(review.requestId, review.decision, review.rationale, auth.csrf);
      const refreshed = await gateway.work.requests(); setRequests(refreshed.requests);
      setReview({ requestId: "", decision: "approve_for_governance", rationale: "" });
      setNotice("Human review recorded. It is not a governance verdict and did not execute anything.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Review failed"); }
  }
  async function cancel(requestId: string) {
    setError(""); setNotice("");
    try {
      const updated = await gateway.work.cancel(requestId, auth.csrf);
      setRequests((current) => current.map((item) => item.id === updated.id ? updated : item));
      setNotice("Request cancelled. No governance verdict was created and no execution started.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Cancellation failed"); }
  }
  async function showDetail(requestId: string) {
    setError("");
    try { setDetail(await gateway.work.detail(requestId)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Request detail unavailable"); }
  }
  return <div className="console-page"><PageHeading title={title} description={mode === "inbox" ? "Reviews and escalations assigned to your human account." : "Governed requests remain distinct from ALLOW decisions and executed effects."} />
    {isLoading ? <StatePanel title="Loading work queue">Reading durable requests and available operations.</StatePanel> : null}
    {loadError ? <StatePanel title="Work queue unavailable" tone="error">No request count or workflow actions are shown because the initial read failed. {loadError}</StatePanel> : null}
    {error ? <StatePanel title="Workflow action failed" tone="error">{error}</StatePanel> : null}
    {notice ? <StatePanel title="Workflow updated">{notice}</StatePanel> : null}
    {!isLoading && !loadError && mode === "requests" ? <section className="records-panel workflow-composer"><div className="panel-heading"><div><h2>Record a request</h2><p>This submits a human work record only. The execution gate is not called.</p></div><ClipboardList /></div><form className="security-form" onSubmit={submit}><label>Title<input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required /></label><label>Operation<select value={form.operation} onChange={(event) => setForm({ ...form, operation: event.target.value, inputs: {} })} required><option value="">Select an allowlisted operation</option>{operations.map((operation) => <option key={operation.id} value={operation.id}>{operation.label}</option>)}</select></label>{selectedOperation ? <><p className="operation-boundary">{selectedOperation.description} {selectedOperation.consequence}<small>Input contract: {selectedOperation.schema_version}</small></p>{selectedOperation.fields.map((field) => <label key={field.id}>{field.label}<span>{field.description}</span><div className="schema-input"><code>{field.resource_prefix}</code><input value={form.inputs[field.id] ?? ""} onChange={(event) => setForm({ ...form, inputs: { ...form.inputs, [field.id]: event.target.value } })} placeholder={field.placeholder} minLength={field.min_length} maxLength={field.max_length} pattern={field.pattern} required /></div></label>)}</> : null}<label>Rationale<textarea value={form.rationale} onChange={(event) => setForm({ ...form, rationale: event.target.value })} required /></label><button type="submit">Record request</button></form></section> : null}
    {!isLoading && !loadError && mode === "inbox" && requests.some((item) => item.state === "submitted" && item.created_by !== auth.session?.account.id) ? <section className="records-panel workflow-composer"><div className="panel-heading"><div><h2>Record human review</h2><p>Recent MFA step-up is required. Approval forwards for governance; it is not ALLOW.</p></div><Inbox /></div><form className="security-form" onSubmit={decide}><label>Request<select value={review.requestId} onChange={(event) => setReview({ ...review, requestId: event.target.value })} required><option value="">Select request</option>{requests.filter((item) => item.state === "submitted" && item.created_by !== auth.session?.account.id).map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><label>Decision<select value={review.decision} onChange={(event) => setReview({ ...review, decision: event.target.value as typeof review.decision })}><option value="approve_for_governance">Approve for governance evaluation</option><option value="reject">Reject</option><option value="return_for_information">Return for information</option><option value="abstain">Abstain</option></select></label><label>Rationale<textarea value={review.rationale} onChange={(event) => setReview({ ...review, rationale: event.target.value })} required /></label><button type="submit">Record review</button></form></section> : null}
    {!isLoading && !loadError ? <section className={`records-panel ${requests.length ? "workflow-list" : "empty-workflow"}`}><Icon />{requests.length ? <div>{requests.map((item) => <article key={item.id}><div><strong>{item.title}</strong><span>{item.operation} · {item.resource}</span><small>Requested {new Date(item.created_at).toLocaleString()}</small></div><div className="workflow-state-actions"><span className="workflow-state">{item.state.replaceAll("_", " ")}</span><button type="button" onClick={() => showDetail(item.id)}>View detail</button>{item.created_by === auth.session?.account.id && (item.state === "submitted" || item.state === "needs_information") ? <button type="button" onClick={() => cancel(item.id)}>Cancel request</button> : null}</div><p>{item.rationale}</p></article>)}</div> : <><h2>No requests are visible</h2><p>The durable workflow store returned zero records for this account.</p></>}</section> : null}
    {!isLoading && !loadError && detail ? <section className="records-panel request-detail" aria-label="Request detail"><div className="panel-heading"><div><h2>{detail.request.title}</h2><p>{detail.request.operation} · {detail.request.resource}</p></div><button type="button" onClick={() => setDetail(null)}>Close detail</button></div><dl><dt>Input contract</dt><dd>{detail.request.input_schema_version}</dd>{Object.entries(detail.request.inputs).map(([key, value]) => <Fragment key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{value}</dd></Fragment>)}<dt>Input receipt</dt><dd><code>{detail.request.input_sha256 || "Legacy request — no structured input digest"}</code></dd><dt>Human workflow state</dt><dd>{detail.request.state.replaceAll("_", " ")}</dd><dt>Execution status</dt><dd>{detail.execution_status.replaceAll("_", " ")}</dd><dt>Execution receipt</dt><dd>{detail.execution_receipt ? detail.execution_receipt.attempt_id : "None — the execution gate has not run."}</dd>{detail.execution_receipt ? <><dt>Governance evidence</dt><dd><code>{detail.execution_receipt.governance_evidence_sha256 || "Unavailable"}</code></dd><dt>Durable audit</dt><dd><code>{detail.execution_receipt.audit_hash || "Unavailable"}</code></dd></> : null}</dl><h3>Immutable human decision receipts</h3>{detail.reviews.length ? detail.reviews.map((item) => <article key={item.id} className="decision-receipt"><strong>{item.decision.replaceAll("_", " ")}</strong><p>{item.rationale}</p><code>{item.receipt_sha256}</code><small>Human review only · no governance verdict · no execution</small></article>) : <p>No human review has been recorded.</p>}</section> : null}
  </div>;
}

export function ModuleCatalogRoute({ title, description, categories }: { title: string; description: string; categories: ModuleSurface["category"][] }) {
  const [modules, setModules] = useState<ModuleSurface[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError("");
    setModules([]);
    gateway.modules()
      .then((result) => {
        if (active) setModules(result.modules.filter((item) => categories.includes(item.category)));
      })
      .catch((reason) => {
        if (active) setError(reason instanceof Error ? reason.message : "Module catalog unavailable");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => { active = false; };
  }, [categories]);
  return <div className="console-page"><PageHeading title={title} description={description} />{isLoading ? <StatePanel title="Loading module catalog">Reading registered modules and their interface boundaries.</StatePanel> : null}{error ? <StatePanel title="Catalog unavailable" tone="error">No module count or interface state is shown because the catalog read failed. {error}</StatePanel> : null}{!isLoading && !error && modules.length > 0 ? <div className="module-grid">{modules.map((item) => <article className="module-card" key={item.id}><div><Boxes /><span>{item.maturity.replace("_", " ")}</span></div><h2>{item.label}</h2><p>{item.summary}</p><dl><dt>Interface</dt><dd>{item.interface_status.replace("_", " ")}</dd><dt>Authority boundary</dt><dd>{item.authority}</dd></dl>{item.id === "swr" && item.interface_status === "available" ? <Link to="/simulations/swr">Open governed workflow</Link> : null}{item.id === "atlas" && item.interface_status === "available" ? <div className="module-links"><Link to="/simulations/atlas-projections">Open projections</Link><Link to="/simulations/atlas-replay">Open replay workspace</Link></div> : null}{item.id === "taar" && item.interface_status === "available" ? <Link to="/simulations/taar">Open inspection console</Link> : null}{item.interface_status === "backend_only" ? <small>No human action is exposed.</small> : null}</article>)}</div> : null}{!isLoading && !error && modules.length === 0 ? <StatePanel title="No registered modules">The successful catalog response contained no modules in this category.</StatePanel> : null}</div>;
}

export function SystemHealthRoute() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { gateway.dashboard().then(setDashboard).catch((reason) => setError(reason instanceof Error ? reason.message : "System health unavailable")); }, []);
  const nonHealthySurfaces = dashboard?.surfaces.filter((surface) => surface.status !== "healthy") ?? [];
  return <div className="console-page"><PageHeading title="System health" description="Current gateway evidence, not a production-readiness claim." />{error ? <StatePanel title="Health unavailable" tone="error">No system state is shown because the dashboard read failed. {error}</StatePanel> : null}{dashboard ? <>{nonHealthySurfaces.length > 0 ? <StatePanel title="Partial system evidence" tone="warning">{nonHealthySurfaces.map((surface) => `${surface.label}: ${surface.status.replace("_", " ")}`).join(" · ")}. Inspect each surface before relying on this snapshot.</StatePanel> : null}<div className="surface-band">{dashboard.surfaces.map((surface) => <SurfaceStatus surface={surface} key={surface.id} />)}</div><section className="records-panel health-boundary"><Activity /><div><h2>Development gateway</h2><p>Version {dashboard.version}. Deployment identity, SLO history, background jobs, and restart controls are unavailable until backed by governed operational APIs.</p></div></section></> : !error ? <StatePanel title="Reading health">Waiting for the gateway response.</StatePanel> : null}</div>;
}

const authorityCategories: ModuleSurface["category"][] = ["authority"];
const securityCategories: ModuleSurface["category"][] = ["security"];
const simulationCategories: ModuleSurface["category"][] = ["simulation", "analysis"];

export const GovernanceCatalogRoute = () => <ModuleCatalogRoute title="Governance and authority" description="Runtime authority components and their current human-interface boundaries." categories={authorityCategories} />;
export const SecurityCatalogRoute = () => <ModuleCatalogRoute title="Security and Chimera" description="Verified security surfaces and explicit gaps; no decorative secure claims." categories={securityCategories} />;
export const SimulationCatalogRoute = () => <ModuleCatalogRoute title="Simulations and analysis" description="Registered engines, maturity, and whether a governed human run contract exists." categories={simulationCategories} />;
