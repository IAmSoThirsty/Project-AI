import { useQuery } from "@tanstack/react-query";
import { ExternalLink, FileKey2, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { gateway } from "@project-ai/web-shared/api";

import { PageHeading, StatePanel } from "../components";

export function EvidenceRoute() {
  const replay = useQuery({ queryKey: ["replay"], queryFn: gateway.replay });
  const dois = useQuery({ queryKey: ["dois"], queryFn: gateway.dois });
  return <div className="console-page"><PageHeading title="Evidence" description="Public replay state and DOI-backed records from the current gateway." action={<Link className="button-link" to="/evidence/audit"><ShieldCheck /> Open protected audit</Link>} />
    {replay.isError || dois.isError ? <StatePanel title="Evidence unavailable" tone="error">{replay.error?.message ?? dois.error?.message}</StatePanel> : null}
    <section className="replay-strip"><FileKey2 aria-hidden="true" /><div><span>Canonical replay</span><strong>{replay.data ? `${replay.data.invariants_passed}/${replay.data.invariants_total} invariants` : "Loading"}</strong></div><span className={`status-label status-${replay.data?.status ?? "not_run"}`}>{replay.data?.status.replace("_", " ") ?? "loading"}</span></section>
    <section className="records-panel"><div className="panel-heading"><div><h2>DOI registry</h2><p>{dois.data?.length ?? 0} current records</p></div></div><div className="record-list">{dois.data?.map((record) => <article key={record.doi}><div><span>{record.domain}</span><h3>{record.title}</h3><code>{record.doi}</code></div><a href={record.url} target="_blank" rel="noreferrer">Open DOI <ExternalLink aria-hidden="true" /></a></article>)}</div></section>
  </div>;
}
