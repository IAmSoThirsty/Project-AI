import { type FormEvent, useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Download, Filter, ShieldCheck } from "lucide-react";
import { gateway, type AuditRecord, type AuditResponse } from "@project-ai/web-shared/api";

import { PageHeading, StatePanel } from "../components";

export function AuditRoute() {
  const pageSize = 25;
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [event, setEvent] = useState("");
  const [filters, setFilters] = useState({ query: "", event: "", offset: 0 });

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    gateway.audit(undefined, pageSize, filters)
      .then(setAudit)
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Audit unavailable"))
      .finally(() => setLoading(false));
  }, [filters]);

  useEffect(load, [load]);

  function applyFilters(submission: FormEvent) {
    submission.preventDefault();
    setFilters({ query, event, offset: 0 });
  }

  function exportRecords(records: AuditRecord[]) {
    const payload = JSON.stringify({
      exported_at: new Date().toISOString(),
      chain_valid: audit?.chain_valid ?? false,
      total_chain_records: audit?.count ?? 0,
      filters: { query: filters.query, event: filters.event },
      records,
    }, null, 2);
    const url = URL.createObjectURL(new Blob([payload], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `project-ai-audit-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return <div className="console-page"><PageHeading title="Audit explorer" description="Protected, read-only evidence authorized by your human session." />
    <div className="audit-boundary"><ShieldCheck aria-hidden="true" /><div><strong>Human session boundary</strong><p>No machine credential is entered or stored in the browser. This read-only view does not grant execution authority.</p></div></div>
    <form className="audit-filters" onSubmit={applyFilters}>
      <label><span>Search evidence</span><input value={query} onChange={(change) => setQuery(change.target.value)} placeholder="Action, hash, actor, or value" /></label>
      <label><span>Event type</span><input value={event} onChange={(change) => setEvent(change.target.value)} placeholder="Exact event name" /></label>
      <button className="button-link" type="submit"><Filter /> Apply filters</button>
    </form>
    {loading ? <StatePanel title="Verifying audit chain">Loading protected evidence…</StatePanel> : null}
    {error ? <StatePanel title="Audit unavailable" tone="error">{error}</StatePanel> : null}
    {audit ? <section className="records-panel"><div className="panel-heading"><div><h2>Verified append-only records</h2><p>{audit.filtered_count} matching of {audit.count} total entries</p></div><div className="audit-actions"><button type="button" onClick={() => exportRecords(audit.records)} disabled={audit.records.length === 0}><Download /> Export page</button><span className="verified-label"><ShieldCheck /> Chain verified</span></div></div><div className="audit-records">{audit.records.length === 0 ? <StatePanel title="No matching records">The chain is valid, but no audit records match these filters.</StatePanel> : audit.records.map((record, index) => <article key={`${String(record.hash ?? record.timestamp ?? "record")}-${index}`}><strong>{String(record.event ?? "audit.record")}</strong><code>{String(record.action_id ?? record.canary_sha256 ?? record.hash ?? "evidence")}</code><span>{String(record.timestamp ?? "")}</span></article>)}</div><nav className="audit-pagination" aria-label="Audit result pages"><button type="button" disabled={filters.offset === 0 || loading} onClick={() => setFilters((current) => ({ ...current, offset: Math.max(0, current.offset - pageSize) }))}><ChevronLeft /> Newer</button><span>{audit.filtered_count === 0 ? 0 : audit.offset + 1}–{Math.min(audit.offset + audit.records.length, audit.filtered_count)} of {audit.filtered_count}</span><button type="button" disabled={audit.offset + audit.records.length >= audit.filtered_count || loading} onClick={() => setFilters((current) => ({ ...current, offset: current.offset + pageSize }))}>Older <ChevronRight /></button></nav></section> : null}
  </div>;
}
