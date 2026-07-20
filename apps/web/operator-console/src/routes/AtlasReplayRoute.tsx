import { gateway, type AtlasReplayResponse } from "@project-ai/web-shared/api";
import { useQuery } from "@tanstack/react-query";
import {
  Braces,
  CheckCircle2,
  Clipboard,
  FileJson,
  FlaskConical,
  Info,
  Play,
  RotateCcw,
  ShieldCheck,
} from "lucide-react";
import { useState, type FormEvent } from "react";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

const MAX_REPLAY_BYTES = 256 * 1024;
const EXAMPLE_BUNDLE = JSON.stringify(
  {
    bundle_id: "bundle-1",
    created_at: "2026-07-16T00:00:00+00:00",
    atlas_version: "0.0.3",
    config_hashes: { atlas: "a".repeat(64) },
    data_hashes: { source: "b".repeat(64) },
    seeds: { projection: "seed-1" },
    checkpoints: [{ state: "baseline", revision: 0 }],
    graph_snapshots: [{ graph_id: "g1", nodes: 2 }],
    audit_events: [{ sequence: 0, event: "analysis.recorded" }],
    projections: [{ claim_id: "claim-1", posterior: 0.42 }],
    claims: [{ claim_id: "claim-1", statement: "source-backed" }],
  },
  null,
  2,
);

const countLabels: Array<[keyof AtlasReplayResponse["item_counts"], string]> = [
  ["audit_events", "Audit events"],
  ["checkpoints", "Checkpoints"],
  ["claims", "Claims"],
  ["graph_snapshots", "Graph snapshots"],
  ["projections", "Projections"],
];

function CopyHash({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
  }
  return (
    <div className="atlas-hash-row">
      <span>{label}</span>
      <code>{value}</code>
      <button type="button" onClick={copy} aria-label={`Copy ${label.toLowerCase()}`}>
        <Clipboard aria-hidden="true" />
      </button>
      <small aria-live="polite">{copied ? "Copied" : ""}</small>
    </div>
  );
}

export function AtlasReplayRoute() {
  const auth = useAuth();
  const atlas = useQuery({ queryKey: ["atlas-status"], queryFn: gateway.atlas.status });
  const [source, setSource] = useState(EXAMPLE_BUNDLE);
  const [result, setResult] = useState<AtlasReplayResponse | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setResult(null);
    let bundle: Record<string, unknown>;
    try {
      const parsed: unknown = JSON.parse(source);
      if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
        throw new Error("Replay bundle must be a JSON object.");
      }
      bundle = parsed as Record<string, unknown>;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Replay bundle is not valid JSON.");
      return;
    }
    if (new TextEncoder().encode(JSON.stringify({ bundle })).length > MAX_REPLAY_BYTES) {
      setError("Atlas replay request must not exceed 256 KB.");
      return;
    }
    setSubmitting(true);
    try {
      setResult(await gateway.atlas.replay(bundle, auth.csrf));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Atlas replay failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="console-page atlas-replay-page">
      <PageHeading
        title="Atlas Replay"
        description="Verify and reconstruct a portable Atlas evidence bundle without granting authority or executing actions."
      />
      <div className="atlas-boundary" role="note">
        <Info aria-hidden="true" />
        <strong>Analysis only</strong><span>·</span><span>No governance verdict</span><span>·</span><span>No execution</span>
      </div>
      {atlas.isError ? <StatePanel title="Atlas status unavailable" tone="error">{atlas.error.message}</StatePanel> : null}
      {error ? <StatePanel title="Replay rejected" tone="error">{error}</StatePanel> : null}

      <div className="atlas-workspace">
        <form className="atlas-editor-panel" onSubmit={submit}>
          <header>
            <div><FileJson aria-hidden="true" /><h2>Replay bundle</h2></div>
            <div className="atlas-editor-actions">
              <button type="button" onClick={() => { setSource(EXAMPLE_BUNDLE); setResult(null); setError(""); }}><RotateCcw aria-hidden="true" />Load example</button>
              <button type="button" onClick={() => { setSource(""); setResult(null); setError(""); }}>Clear</button>
            </div>
          </header>
          <label htmlFor="atlas-replay-source">Portable Atlas bundle JSON</label>
          <textarea
            id="atlas-replay-source"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            spellCheck={false}
            required
          />
          <footer>
            <span>{new TextEncoder().encode(source).length.toLocaleString()} bytes entered</span>
            <button className="atlas-submit" type="submit" disabled={submitting || !source.trim()}>
              <Play aria-hidden="true" />{submitting ? "Verifying…" : "Verify and replay"}
            </button>
          </footer>
        </form>

        <aside className="atlas-context" aria-label="Atlas replay boundaries">
          <section>
            <h2>Atlas status</h2>
            <ul>
              <li><FlaskConical aria-hidden="true" /><div><strong>Experimental</strong><span>Atlas Replay remains an experimental analytical capability.</span></div></li>
              <li><Info aria-hidden="true" /><div><strong>Analysis only</strong><span>No governance verdicts are produced.</span></div></li>
              <li><Braces aria-hidden="true" /><div><strong>Deterministic replay</strong><span>The same valid bundle reconstructs the same evidence hash.</span></div></li>
              <li><ShieldCheck aria-hidden="true" /><div><strong>Subordination</strong><span>{atlas.data?.subordination_notice ?? "Reading the canonical Atlas boundary…"}</span></div></li>
            </ul>
          </section>
          <section>
            <h2>Input boundary</h2>
            <ul>
              <li><Braces aria-hidden="true" /><div><strong>JSON object</strong><span>Bundle input must be a valid JSON object.</span></div></li>
              <li><FileJson aria-hidden="true" /><div><strong>256 KB maximum</strong><span>Oversized requests fail before analysis.</span></div></li>
              <li><ShieldCheck aria-hidden="true" /><div><strong>Browser token not used</strong><span>No machine or capability token is accepted here.</span></div></li>
              <li><CheckCircle2 aria-hidden="true" /><div><strong>Server session required</strong><span>Permission and CSRF checks run on the server.</span></div></li>
            </ul>
          </section>
        </aside>
      </div>

      {result ? (
        <section className="atlas-result" aria-live="polite">
          <header><CheckCircle2 aria-hidden="true" /><div><h2>Verification passed</h2><span>Bundle ID · {result.bundle_id}</span></div></header>
          <div className="atlas-hashes">
            <CopyHash label="Bundle hash" value={result.bundle_hash} />
            <CopyHash label="Reconstructed state hash" value={result.reconstructed_state_hash} />
          </div>
          <div className="atlas-counts">
            {countLabels.map(([key, label]) => <div key={key}><span>{label}</span><strong>{result.item_counts[key]}</strong></div>)}
          </div>
          <p><Info aria-hidden="true" />This reconstruction is evidence only. It is not a decision or authority grant.</p>
          <footer><span>Verified audit receipt</span><time dateTime={result.audited_at}>{new Date(result.audited_at).toLocaleString()}</time><code>{result.audit_receipt_sha256}</code></footer>
        </section>
      ) : null}
    </div>
  );
}
