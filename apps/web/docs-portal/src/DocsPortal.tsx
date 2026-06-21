import {
  ArrowUpRight,
  BookOpenText,
  Braces,
  KeyRound,
  Scale,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  type DoiRecord,
  ErrorPanel,
  type Health,
  LoadingPanel,
  PortalShell,
  type ReplayStatus,
  StatusPill,
  gateway,
} from "@project-ai/web-shared";

const nav = [
  { id: "overview", label: "Overview" },
  { id: "architecture", label: "Architecture" },
  { id: "publications", label: "Publications" },
];

const stages = [
  ["01", "Normalize", "Reduce the request to actor, operation, resource, and payload."],
  ["02", "Govern", "Evaluate invariants and preserve unilateral veto authority."],
  ["03", "Authorize", "Require exact, scoped, signed, and unexpired capability."],
  ["04", "Execute", "Act only after ALLOW and append reconstructable evidence."],
] as const;

export function DocsPortal() {
  const [active, setActive] = useState("overview");
  const [health, setHealth] = useState<Health | null>(null);
  const [replay, setReplay] = useState<ReplayStatus | null>(null);
  const [dois, setDois] = useState<DoiRecord[]>([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("all");

  useEffect(() => {
    let current = true;
    Promise.all([gateway.health(), gateway.replay(), gateway.dois()])
      .then(([nextHealth, nextReplay, nextDois]) => {
        if (!current) return;
        setHealth(nextHealth);
        setReplay(nextReplay);
        setDois(nextDois);
      })
      .catch((reason: unknown) => {
        if (current) setError(reason instanceof Error ? reason.message : "Gateway unavailable");
      });
    return () => {
      current = false;
    };
  }, []);

  const domains = useMemo(() => [...new Set(dois.map((record) => record.domain))].sort(), [dois]);
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return dois.filter(
      (record) =>
        (domain === "all" || record.domain === domain) &&
        (!needle || `${record.title} ${record.doi} ${record.domain}`.toLowerCase().includes(needle)),
    );
  }, [dois, domain, query]);

  return (
    <PortalShell lane="Documentation" active={active} items={nav} onNavigate={setActive}>
      {active === "overview" && (
        <>
          <section className="hero portal-hero">
            <div className="wrap hero-grid">
              <div className="hero-copy-block reveal in">
                <div className="eyebrow">Architecture / interfaces / public record</div>
                <h1>
                  <span className="gradient-text">Read the system</span> from proof to execution.
                </h1>
                <p className="hero-copy">
                  A development documentation surface for the governed runtime, its downward-only
                  package graph, canonical outcomes, and DOI-backed research record.
                </p>
                <div className="hero-actions">
                  <button className="button primary" onClick={() => setActive("architecture")}>
                    Map the execution path
                  </button>
                  <button className="button ghost" onClick={() => setActive("publications")}>
                    Browse DOI evidence
                  </button>
                </div>
              </div>
              <aside className="hero-panel reveal in" aria-label="Gateway status">
                <div className="panel-topline">
                  <span className="status-dot" /> documentation gateway
                </div>
                {error ? (
                  <ErrorPanel message={error} />
                ) : health && replay ? (
                  <div className="command-list">
                    <div className="command-row">
                      <ShieldCheck size={17} /> <code>/health/live</code>
                      <StatusPill status="pass" label={health.status} />
                    </div>
                    <div className="command-row">
                      <Braces size={17} /> <code>/replay/status</code>
                      <StatusPill status={replay.status} label={`${replay.invariants_passed}/${replay.invariants_total}`} />
                    </div>
                    <div className="command-row">
                      <BookOpenText size={17} /> <code>/dois</code>
                      <span>{dois.length} records</span>
                    </div>
                  </div>
                ) : (
                  <LoadingPanel label="Reading public surfaces" />
                )}
              </aside>
            </div>
          </section>
          <section className="section dark-ridge">
            <div className="wrap">
              <div className="section-head centered">
                <div className="eyebrow">System contract</div>
                <h2>Authority flows downward. Evidence flows outward.</h2>
                <p>Clients observe state; only the execution gate can turn an authorized request into an effect.</p>
              </div>
              <div className="triad">
                <article className="glass-card"><Scale className="card-index" /><h3>Three outcomes</h3><p>ALLOW, DENY, and ESCALATE remain the only canonical governance results.</p></article>
                <article className="glass-card"><KeyRound className="card-index" /><h3>Scoped authority</h3><p>Capability binds actor, operation, resource, expiry, signature, and replay state.</p></article>
                <article className="glass-card"><ShieldCheck className="card-index" /><h3>Fail closed</h3><p>Missing policy, authority, verification, or runtime support cannot become execution.</p></article>
              </div>
            </div>
          </section>
        </>
      )}

      {active === "architecture" && (
        <section className="section">
          <div className="wrap">
            <div className="section-head">
              <div><div className="eyebrow">Narrow bridge</div><h1>Every actuation enters one gate.</h1></div>
              <StatusPill status="pass" label="Downward-only graph" />
            </div>
            <div className="timeline">
              {stages.map(([index, title, copy]) => (
                <article className="timeline-item" key={index}><span>{index}</span><h3>{title}</h3><p>{copy}</p></article>
              ))}
            </div>
            <div className="proof-shell" style={{ marginTop: 32 }}>
              <div><div className="eyebrow">Package direction</div><h2>kernel / security to API / CLI</h2><p>Governance and capability depend downward; applications consume constrained surfaces and never carry authority.</p></div>
              <pre className="terminal"><code>kernel + security{"\n"}  governance + capability{"\n"}    execution{"\n"}      companion / SWR / Atlas{"\n"}        API / CLI / clients</code></pre>
            </div>
          </div>
        </section>
      )}

      {active === "publications" && (
        <section className="section">
          <div className="wrap">
            <div className="section-head">
              <div><div className="eyebrow">Publication layer</div><h1>DOI-backed system record.</h1><p>Filter the authoritative Stage -1 catalog served by the read-only API.</p></div>
              <StatusPill status={error ? "error" : dois.length ? "pass" : "loading"} label={error ? "Unavailable" : `${filtered.length} shown`} />
            </div>
            <div className="filters">
              <label><span className="sr-only">Search publications</span><input className="control" style={{ width: "100%" }} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search title, DOI, or domain" /></label>
              <label><span className="sr-only">Filter domain</span><select className="control" style={{ width: "100%" }} value={domain} onChange={(event) => setDomain(event.target.value)}><option value="all">All domains</option>{domains.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
            </div>
            {error ? <ErrorPanel message={error} /> : !dois.length ? <LoadingPanel label="Loading DOI registry" /> : (
              <div className="records-grid">
                {filtered.map((record) => (
                  <article className="record-card" key={record.doi}><div className="record-meta">{record.domain}</div><h3>{record.title}</h3><p>Permanent Project-AI publication evidence.</p><a href={record.url} target="_blank" rel="noreferrer">{record.doi}<ArrowUpRight size={14} /></a></article>
                ))}
              </div>
            )}
            {!error && dois.length > 0 && filtered.length === 0 && <div className="empty-panel"><Search size={18} /> No DOI records match this filter.</div>}
          </div>
        </section>
      )}
    </PortalShell>
  );
}
