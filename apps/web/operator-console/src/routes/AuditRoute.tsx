import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  FileJson,
  Filter,
  LockKeyhole,
  ShieldCheck,
  X,
} from "lucide-react";
import {
  gateway,
  type AuditDetailResponse,
  type AuditFilters,
  type HumanAuditRecordSummary,
  type HumanAuditResponse,
} from "@project-ai/web-shared/api";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

type AuditFilterDraft = {
  query: string;
  event: string;
  actor: string;
  account: string;
  operation: string;
  resource: string;
  verdict: "" | "ALLOW" | "DENY" | "ESCALATE";
  severity: string;
  fromTime: string;
  toTime: string;
};

const EMPTY_FILTERS: AuditFilterDraft = {
  query: "",
  event: "",
  actor: "",
  account: "",
  operation: "",
  resource: "",
  verdict: "",
  severity: "",
  fromTime: "",
  toTime: "",
};

function compact(value: string): string | undefined {
  return value.trim() || undefined;
}

function dateTimeToIso(value: string): string | undefined {
  return value ? new Date(value).toISOString() : undefined;
}

function appliedFilters(draft: AuditFilterDraft): Omit<AuditFilters, "cursor" | "offset"> {
  return {
    query: compact(draft.query),
    event: compact(draft.event),
    actor: compact(draft.actor),
    account: compact(draft.account),
    operation: compact(draft.operation),
    resource: compact(draft.resource),
    verdict: draft.verdict || undefined,
    severity: compact(draft.severity),
    from_time: dateTimeToIso(draft.fromTime),
    to_time: dateTimeToIso(draft.toTime),
  };
}

function displayAuditValue(value: string | number | boolean | null): string {
  if (value === null) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
}

function recordLabel(record: HumanAuditRecordSummary): string {
  return `${record.event}, record ${record.source_hash.slice(0, 12)}`;
}

export function AuditRoute() {
  const auth = useAuth();
  const pageSize = 25;
  const [audit, setAudit] = useState<HumanAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [draft, setDraft] = useState<AuditFilterDraft>(EMPTY_FILTERS);
  const [filters, setFilters] = useState<Omit<AuditFilters, "cursor" | "offset">>({});
  const [cursor, setCursor] = useState<string | undefined>();
  const [cursorHistory, setCursorHistory] = useState<(string | undefined)[]>([]);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");
  const [exportStatus, setExportStatus] = useState("");
  const [selectedSourceHash, setSelectedSourceHash] = useState<string | null>(null);
  const [detail, setDetail] = useState<AuditDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");
  const loadSequence = useRef(0);
  const detailSequence = useRef(0);
  const detailHeading = useRef<HTMLHeadingElement>(null);
  const detailTrigger = useRef<HTMLButtonElement | null>(null);
  const canViewRaw = ["owner", "administrator", "auditor"].includes(
    auth.session?.account.role ?? "",
  );
  const canExport = ["owner", "administrator", "reviewer", "auditor"].includes(
    auth.session?.account.role ?? "",
  );
  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  const load = useCallback(() => {
    const sequence = ++loadSequence.current;
    setLoading(true);
    setError("");
    setAudit(null);
    setSelectedSourceHash(null);
    setDetail(null);
    setDetailError("");
    setDetailLoading(false);
    gateway.auditSearch({ ...filters, cursor }, pageSize)
      .then((result) => {
        if (sequence === loadSequence.current) setAudit(result);
      })
      .catch((reason) => {
        if (sequence === loadSequence.current) {
          setError(reason instanceof Error ? reason.message : "Audit unavailable");
        }
      })
      .finally(() => {
        if (sequence === loadSequence.current) setLoading(false);
      });
  }, [cursor, filters]);

  useEffect(load, [load]);

  useEffect(() => {
    if (detail || detailError) detailHeading.current?.focus();
  }, [detail, detailError]);

  function resetCursor() {
    setCursor(undefined);
    setCursorHistory([]);
  }

  function applyFilterDraft(submission: FormEvent) {
    submission.preventDefault();
    setFilters(appliedFilters(draft));
    resetCursor();
    setExportError("");
    setExportStatus("");
  }

  function clearFilters() {
    setDraft(EMPTY_FILTERS);
    setFilters({});
    resetCursor();
    setExportError("");
    setExportStatus("");
  }

  function showOlder() {
    if (!audit?.next_cursor) return;
    setCursorHistory((current) => [...current, cursor]);
    setCursor(audit.next_cursor);
  }

  function showNewer() {
    if (cursorHistory.length === 0) return;
    setCursor(cursorHistory[cursorHistory.length - 1]);
    setCursorHistory((current) => current.slice(0, -1));
  }

  function closeDetail() {
    ++detailSequence.current;
    setSelectedSourceHash(null);
    setDetail(null);
    setDetailError("");
    setDetailLoading(false);
    detailTrigger.current?.focus();
  }

  function openDetail(record: HumanAuditRecordSummary, trigger: HTMLButtonElement) {
    if (selectedSourceHash === record.source_hash) {
      closeDetail();
      return;
    }
    const sequence = ++detailSequence.current;
    detailTrigger.current = trigger;
    setSelectedSourceHash(record.source_hash);
    setDetail(null);
    setDetailError("");
    setDetailLoading(true);
    gateway.auditDetail(record.source_hash)
      .then((result) => {
        if (sequence === detailSequence.current) setDetail(result);
      })
      .catch((reason) => {
        if (sequence === detailSequence.current) {
          setDetailError(
            reason instanceof Error ? reason.message : "Audit record detail unavailable",
          );
        }
      })
      .finally(() => {
        if (sequence === detailSequence.current) setDetailLoading(false);
      });
  }

  async function exportRecords() {
    if (!auth.csrf) {
      setExportError("CSRF token unavailable; refresh the page before exporting audit evidence.");
      return;
    }
    setExporting(true);
    setExportError("");
    setExportStatus("");
    try {
      const exported = await gateway.auditExport(
        { limit: 500, offset: 0, ...filters },
        auth.csrf,
      );
      const payload = JSON.stringify(exported, null, 2);
      const url = URL.createObjectURL(new Blob([payload], { type: "application/json" }));
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `project-ai-audit-${exported.generated_at.slice(0, 10)}-${exported.records_sha256.slice(0, 8)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      setExportStatus(
        `Exported ${exported.exported_records} of ${exported.matched_records} matching records with redaction. Receipt ${exported.export_audit_hash.slice(0, 12)}.`,
      );
    } catch (reason) {
      setExportError(reason instanceof Error ? reason.message : "Audit export unavailable");
    } finally {
      setExporting(false);
    }
  }

  return <div className="console-page">
    <PageHeading title="Audit explorer" description="Protected, read-only evidence authorized by your human session." />
    <div className="audit-boundary"><ShieldCheck aria-hidden="true" /><div><strong>Human session boundary</strong><p>Search results expose normalized summaries only. Record detail is permission-filtered by the server and never grants execution authority.</p></div></div>
    <form className="audit-filters" onSubmit={applyFilterDraft}>
      <div className="audit-filter-primary">
        <label><span>Search evidence</span><input value={draft.query} onChange={(change) => setDraft((current) => ({ ...current, query: change.target.value }))} placeholder={canViewRaw ? "Action, hash, actor, or value" : "Event, hash, verdict, or severity"} /></label>
        <label><span>Event type</span><input value={draft.event} onChange={(change) => setDraft((current) => ({ ...current, event: change.target.value }))} placeholder="Exact event name" /></label>
      </div>
      <details className="audit-advanced-filters">
        <summary>More filters{activeFilterCount > 0 ? <span>{activeFilterCount} active</span> : null}</summary>
        <div className="audit-filter-grid">
          {canViewRaw ? <>
            <label><span>Actor</span><input value={draft.actor} onChange={(change) => setDraft((current) => ({ ...current, actor: change.target.value }))} placeholder="Exact actor ID" /></label>
            <label><span>Account</span><input value={draft.account} onChange={(change) => setDraft((current) => ({ ...current, account: change.target.value }))} placeholder="Exact account ID" /></label>
            <label><span>Operation</span><input value={draft.operation} onChange={(change) => setDraft((current) => ({ ...current, operation: change.target.value }))} placeholder="Exact operation" /></label>
            <label><span>Resource</span><input value={draft.resource} onChange={(change) => setDraft((current) => ({ ...current, resource: change.target.value }))} placeholder="Exact resource" /></label>
          </> : <p className="audit-filter-permission"><LockKeyhole aria-hidden="true" />Actor, account, operation, and resource filters require raw-audit permission. Your searches are limited to visible summary fields.</p>}
          <label><span>Verdict</span><select value={draft.verdict} onChange={(change) => setDraft((current) => ({ ...current, verdict: change.target.value as AuditFilterDraft["verdict"] }))}><option value="">Any verdict</option><option value="ALLOW">ALLOW</option><option value="DENY">DENY</option><option value="ESCALATE">ESCALATE</option></select></label>
          <label><span>Severity</span><input value={draft.severity} onChange={(change) => setDraft((current) => ({ ...current, severity: change.target.value }))} placeholder="Exact severity" /></label>
          <label><span>From time <small>(local)</small></span><input type="datetime-local" value={draft.fromTime} onChange={(change) => setDraft((current) => ({ ...current, fromTime: change.target.value }))} /></label>
          <label><span>To time <small>(local)</small></span><input type="datetime-local" value={draft.toTime} onChange={(change) => setDraft((current) => ({ ...current, toTime: change.target.value }))} /></label>
        </div>
      </details>
      <div className="audit-filter-actions">
        <button className="button-link" type="submit"><Filter /> Apply filters</button>
        <button className="button-link is-secondary" type="button" onClick={clearFilters} disabled={activeFilterCount === 0 && Object.values(draft).every((value) => value === "")}><X /> Clear</button>
      </div>
    </form>
    {loading ? <StatePanel title="Verifying audit chain">Loading protected evidence…</StatePanel> : null}
    {error ? <StatePanel title="Audit locked down" tone="error">{error}. No cached records are displayed.</StatePanel> : null}
    {audit ? <section className="records-panel">
      <div className="panel-heading"><div><h2>Verified append-only records</h2><p>{audit.filtered_count} matching of {audit.count} total entries · {activeFilterCount === 0 ? "No filters" : `${activeFilterCount} active ${activeFilterCount === 1 ? "filter" : "filters"}`}</p></div><div className="audit-actions">{canExport ? <button type="button" onClick={() => void exportRecords()} disabled={audit.filtered_count === 0 || loading || exporting}><Download /> {exporting ? "Preparing redacted export…" : "Export redacted results"}</button> : null}<span className="verified-label"><ShieldCheck /> Chain verified</span></div></div>
      {canExport ? <p className="audit-export-boundary">Exports are generated by the server, capped at 500 matching records, redacted, digested, and audit-recorded.</p> : <p className="audit-export-boundary">Your role can view approved audit evidence but cannot request bulk exports.</p>}
      {exportError ? <p className="audit-export-message is-error" role="alert">{exportError}</p> : null}
      {exportStatus ? <p className="audit-export-message" role="status">{exportStatus}</p> : null}
      <div className="audit-records">
        {audit.records.length === 0 ? <StatePanel title="No matching records">The chain is valid, but no audit records match these filters.</StatePanel> : audit.records.map((record) => <article key={record.source_hash}>
          <button
            type="button"
            className="audit-record-card"
            aria-expanded={selectedSourceHash === record.source_hash}
            aria-controls="audit-record-detail"
            onClick={(event) => openDetail(record, event.currentTarget)}
          >
            <span className="audit-record-event"><strong>{record.event}</strong><small>{record.verdict ?? record.severity ?? "Evidence record"}</small></span>
            <code>{record.source_hash.slice(0, 12)}…</code>
            <time dateTime={record.timestamp}>{record.timestamp}</time>
            <span className="audit-record-status"><ShieldCheck aria-hidden="true" />Verified</span>
            <Eye aria-hidden="true" />
            <span className="sr-only">View detail for {recordLabel(record)}</span>
          </button>
        </article>)}
      </div>
      {selectedSourceHash ? <section id="audit-record-detail" className="audit-detail-panel" aria-labelledby="audit-detail-heading">
        <header>
          <div><span className="audit-detail-eyebrow"><FileJson aria-hidden="true" />Normalized record detail</span><h3 id="audit-detail-heading" ref={detailHeading} tabIndex={-1}>{detail?.event ?? (detailError ? "Record detail unavailable" : "Loading record detail")}</h3></div>
          <button type="button" onClick={closeDetail} aria-label="Close audit record detail"><X aria-hidden="true" /></button>
        </header>
        {detailLoading ? <StatePanel title="Verifying record">Checking the complete chain before releasing fields…</StatePanel> : null}
        {detailError ? <StatePanel title="Detail locked down" tone="error">{detailError}. No record fields are displayed.</StatePanel> : null}
        {detail ? <div className="audit-detail-content">
          <div className={`audit-visibility audit-visibility-${detail.visibility}`}><LockKeyhole aria-hidden="true" /><div><strong>{detail.visibility === "privileged" ? "Privileged safe view" : "Permission-filtered view"}</strong><p>{detail.visibility === "privileged" ? "Your server-authorized role can inspect the sanitized raw record. Credential-bearing fields remain redacted." : "Raw JSON and arbitrary fields are withheld. Identifiers are represented by SHA-256 digests."}</p></div></div>
          <section className="audit-integrity" aria-label="Record integrity">
            <h4>Chain position</h4>
            <dl><dt>Status</dt><dd><span className="audit-chain-good"><ShieldCheck aria-hidden="true" />Verified</span></dd><dt>Position</dt><dd>{detail.chain_position} of {detail.chain_records}</dd><dt>Record SHA-256</dt><dd><code>{detail.source_hash}</code></dd><dt>Previous SHA-256</dt><dd><code>{detail.previous_hash}</code></dd><dt>Timestamp</dt><dd><time dateTime={detail.timestamp}>{detail.timestamp}</time></dd></dl>
          </section>
          <section className="audit-normalized-fields" aria-label="Normalized record fields">
            <h4>Normalized fields</h4>
            {Object.keys(detail.fields).length ? <dl>{Object.entries(detail.fields).sort(([left], [right]) => left.localeCompare(right)).map(([field, value]) => <div key={field}><dt>{field}</dt><dd><code>{displayAuditValue(value)}</code></dd></div>)}</dl> : <p>No additional fields are visible to this role.</p>}
            {detail.redacted_fields.length ? <p className="audit-redacted-fields"><LockKeyhole aria-hidden="true" /><span><strong>Withheld fields</strong>{detail.redacted_fields.join(", ")}</span></p> : <p className="audit-redacted-fields is-clear"><ShieldCheck aria-hidden="true" /><span><strong>Credential redaction</strong>No credential-bearing fields were present.</span></p>}
          </section>
          {detail.raw_record ? <details className="audit-raw-json"><summary><FileJson aria-hidden="true" />Safe raw JSON</summary><p>Rendered as escaped text. Credential-bearing values remain redacted by the server.</p><pre tabIndex={0} aria-label="Safe raw audit JSON"><code>{JSON.stringify(detail.raw_record, null, 2)}</code></pre></details> : <div className="audit-raw-withheld"><LockKeyhole aria-hidden="true" /><div><strong>Raw JSON withheld</strong><p>Your interface role can inspect normalized, redacted evidence only.</p></div></div>}
        </div> : null}
      </section> : null}
      <nav className="audit-pagination" aria-label="Audit result pages"><button type="button" disabled={cursorHistory.length === 0 || loading} onClick={showNewer}><ChevronLeft /> Newer</button><span>{audit.filtered_count === 0 ? 0 : audit.offset + 1}–{Math.min(audit.offset + audit.records.length, audit.filtered_count)} of {audit.filtered_count}</span><button type="button" disabled={!audit.has_more || !audit.next_cursor || loading} onClick={showOlder}>Older <ChevronRight /></button></nav>
    </section> : null}
  </div>;
}
