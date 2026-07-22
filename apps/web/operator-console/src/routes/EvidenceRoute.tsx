import { useQuery } from "@tanstack/react-query";
import { ExternalLink, FileKey2, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { gateway } from "@project-ai/web-shared/api";

import { PageHeading, StatePanel } from "../components";

export function EvidenceRoute() {
  const replay = useQuery({ queryKey: ["replay"], queryFn: gateway.replay, retry: false });
  const dois = useQuery({ queryKey: ["dois"], queryFn: gateway.dois, retry: false });
  const partialEvidence = (replay.isError && dois.data !== undefined) || (dois.isError && replay.data !== undefined);
  return <div className="console-page"><PageHeading title="Evidence" description="Public replay state and DOI-backed records from the current gateway." action={<Link className="button-link" to="/evidence/audit"><ShieldCheck /> Open protected audit</Link>} />
    {partialEvidence ? <StatePanel title="Partial evidence" tone="warning">One evidence source loaded and another failed. Treat the visible source as a partial snapshot.</StatePanel> : null}
    {replay.isPending ? <StatePanel title="Loading replay evidence">Reading the canonical replay result.</StatePanel> : null}
    {replay.isError ? <StatePanel title="Replay evidence unavailable" tone="error">No replay status or invariant count is shown because the read failed. {replay.error.message}</StatePanel> : null}
    {replay.data ? <section className="replay-strip"><FileKey2 aria-hidden="true" /><div><span>Canonical replay</span><strong>{`${replay.data.invariants_passed}/${replay.data.invariants_total} invariants`}</strong></div><span className={`status-label status-${replay.data.status}`}>{replay.data.status.replace("_", " ")}</span></section> : null}
    {dois.isPending ? <StatePanel title="Loading DOI registry">Reading DOI-backed evidence records.</StatePanel> : null}
    {dois.isError ? <StatePanel title="DOI registry unavailable" tone="error">No DOI record count is shown because the read failed. {dois.error.message}</StatePanel> : null}
    {dois.data && dois.data.length > 0 ? <section className="records-panel"><div className="panel-heading"><div><h2>DOI registry</h2><p>{dois.data.length} current records</p></div></div><div className="record-list">{dois.data.map((record) => <article key={record.doi}><div><span>{record.domain}</span><h3>{record.title}</h3><code>{record.doi}</code></div><a href={record.url} target="_blank" rel="noreferrer">Open DOI <ExternalLink aria-hidden="true" /></a></article>)}</div></section> : null}
    {dois.data && dois.data.length === 0 ? <StatePanel title="No DOI records">The successful registry response contained zero records.</StatePanel> : null}
  </div>;
}
