import { gateway, type ExecutionReceipt, type SwrScenario, type WorkRequest } from "@project-ai/web-shared/api";
import { PlayCircle, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

export function SwrRoute() {
  const auth = useAuth();
  const [scenarios, setScenarios] = useState<SwrScenario[]>([]);
  const [requests, setRequests] = useState<WorkRequest[]>([]);
  const [configured, setConfigured] = useState(false);
  const [boundary, setBoundary] = useState("");
  const [requestId, setRequestId] = useState("");
  const [scenarioId, setScenarioId] = useState("");
  const [decision, setDecision] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [receipt, setReceipt] = useState<ExecutionReceipt | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([gateway.swr.scenarios(), gateway.work.requests()])
      .then(([catalog, work]) => {
        setScenarios(catalog.scenarios);
        setConfigured(catalog.execution_gate_configured);
        setBoundary(catalog.authority_boundary);
        setRequests(work.requests);
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "SWR workflow unavailable"));
  }, []);

  const executableRequests = useMemo(
    () => requests.filter((item) => item.operation === "scenario.prepare" && item.state === "reviewed_approve"),
    [requests],
  );
  const selectedScenario = scenarios.find((item) => item.scenario_id === scenarioId);

  function chooseScenario(value: string) {
    setScenarioId(value);
    const scenario = scenarios.find((item) => item.scenario_id === value);
    if (scenario) setDecision(scenario.expected_decision);
  }

  async function execute(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    setReceipt(null);
    try {
      if (totpCode.trim()) await gateway.auth.mfaStepUp(totpCode.trim(), auth.csrf);
      const result = await gateway.swr.execute(requestId, scenarioId, decision, auth.csrf);
      setReceipt(result.receipt);
      setNotice(result.reused_existing_receipt
        ? "The existing durable receipt was returned; the scenario was not executed again."
        : "The server submitted the bounded scenario record through the execution gate.");
      setTotpCode("");
      const refreshed = await gateway.work.requests();
      setRequests(refreshed.requests);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "SWR execution failed");
    }
  }

  return <div className="console-page swr-page">
    <PageHeading title="Sovereign War Room" description="Run one deterministic analytical scenario through the canonical execution gate." />
    <StatePanel title="Authority boundary">{boundary || "Loading the server-defined authority boundary."}</StatePanel>
    {error ? <StatePanel title="SWR workflow unavailable" tone="error">{error}</StatePanel> : null}
    {notice ? <StatePanel title="Execution receipt recorded">{notice}</StatePanel> : null}
    <div className="swr-grid">
      <section className="records-panel workflow-composer">
        <div className="panel-heading"><div><h2>Reviewed scenario execution</h2><p>The browser sends a request ID and scenario input. It never receives the server capability.</p></div><PlayCircle /></div>
        <form className="security-form" onSubmit={execute}>
          <label>Approved request<select value={requestId} onChange={(event) => setRequestId(event.target.value)} required><option value="">Select a reviewed request</option>{executableRequests.map((item) => <option key={item.id} value={item.id}>{item.title} · {item.resource}</option>)}</select></label>
          <label>Scenario<select value={scenarioId} onChange={(event) => chooseScenario(event.target.value)} required><option value="">Select a deterministic scenario</option>{scenarios.map((item) => <option key={item.scenario_id} value={item.scenario_id}>Round {item.round_number} · {item.name}</option>)}</select></label>
          {selectedScenario ? <div className="scenario-summary"><strong>{selectedScenario.name}</strong><p>{selectedScenario.description}</p><small>Difficulty {selectedScenario.difficulty} · {selectedScenario.scenario_type.replaceAll("_", " ")}</small></div> : null}
          <label>Canonical scenario decision<textarea value={decision} readOnly required /></label>
          <p className="operation-boundary">This first workflow runs only the canonical deterministic input that the reviewer approved. Arbitrary model responses are not accepted.</p>
          <label>Authenticator code (if step-up is not recent)<input value={totpCode} onChange={(event) => setTotpCode(event.target.value)} inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" placeholder="6 digits" /></label>
          <button type="submit" disabled={!configured || executableRequests.length === 0}>Submit through execution gate</button>
          {!configured ? <p className="operation-boundary">The server has not configured its execution secret and durable audit relay.</p> : null}
          {configured && executableRequests.length === 0 ? <p className="operation-boundary">A separate reviewer must first approve a scenario.prepare request with the exact scenario resource.</p> : null}
        </form>
      </section>
      <section className="records-panel scenario-catalog">
        <div className="panel-heading"><div><h2>Scenario catalog</h2><p>Five deterministic rounds from the canonical SWR package.</p></div><ShieldCheck /></div>
        {scenarios.map((item) => <article key={item.scenario_id}><span>Round {item.round_number}</span><strong>{item.name}</strong><p>{item.description}</p><small>{item.tags.join(" · ")}</small></article>)}
      </section>
    </div>
    {receipt ? <section className="records-panel execution-receipt" aria-label="Execution receipt"><div className="panel-heading"><div><h2>Durable execution receipt</h2><p>{receipt.status} · {receipt.outcome || "no outcome"}</p></div><ShieldCheck /></div><dl><dt>Attempt</dt><dd>{receipt.attempt_id}</dd><dt>Action</dt><dd>{receipt.action_id || "No action identifier"}</dd><dt>Governance evidence</dt><dd><code>{receipt.governance_evidence_sha256 || "Unavailable"}</code></dd><dt>Execution event</dt><dd><code>{receipt.event_hash || "Unavailable"}</code></dd><dt>Durable audit record</dt><dd><code>{receipt.audit_hash || "Unavailable"}</code></dd></dl>{receipt.reason ? <p>{receipt.reason}</p> : null}<details><summary>Result payload</summary><pre>{JSON.stringify(receipt.output, null, 2)}</pre></details></section> : null}
  </div>;
}
