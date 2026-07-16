import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BookOpenCheck, Clock3, RefreshCw, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { gateway } from "@project-ai/web-shared/api";

import { PageHeading, StatePanel, SurfaceStatus } from "../components";

export function CommandCenterRoute() {
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: gateway.dashboard, refetchInterval: 30_000 });

  return (
    <div className="console-page command-center-page">
      <PageHeading
        title="Command Center"
        description="Evidence-driven operations. Governed decisions. Immutable audit."
        action={<button className="icon-button" type="button" onClick={() => void dashboard.refetch()} disabled={dashboard.isFetching}><RefreshCw aria-hidden="true" /> Refresh</button>}
      />
      {dashboard.isPending ? <StatePanel title="Reading current state">The gateway dashboard contract is loading.</StatePanel> : null}
      {dashboard.isError ? <StatePanel title="Dashboard unavailable" tone="error">{dashboard.error.message}</StatePanel> : null}
      {dashboard.data ? (
        <>
          <section className="surface-band" aria-label="Current system state">
            {dashboard.data.surfaces.map((surface) => <SurfaceStatus key={surface.id} surface={surface} />)}
          </section>

          <section className="work-panel" aria-labelledby="work-queue-heading">
            <div className="panel-heading"><div><h2 id="work-queue-heading">Work queue</h2><p>Only server-provided work appears here.</p></div><span className="count-label">{dashboard.data.work_items.length} items</span></div>
            <div className="table-scroll">
              <table><thead><tr><th>Priority</th><th>Request</th><th>Owner</th><th>State</th><th>Updated</th></tr></thead>
                <tbody>{dashboard.data.work_items.length === 0 ? <tr><td colSpan={5}><div className="empty-work"><Clock3 aria-hidden="true" /><strong>No work-item API is available yet.</strong><span>The console will not invent assignments or governance outcomes.</span></div></td></tr> : dashboard.data.work_items.map((item) => <tr key={item.id}><td>{item.priority}</td><td>{item.title}</td><td>{item.owner}</td><td>{item.state}</td><td>{item.updated_at}</td></tr>)}</tbody>
              </table>
            </div>
          </section>

          <div className="dashboard-lower-grid">
            <section className="evidence-summary"><div className="panel-heading"><div><h2>Evidence registry</h2><p>DOI-backed records exposed by the gateway.</p></div><BookOpenCheck aria-hidden="true" /></div><strong className="hero-number">{dashboard.data.doi_records}</strong><span>current records</span><Link to="/evidence">Browse evidence <ArrowRight aria-hidden="true" /></Link></section>
            <section className="activity-panel"><div className="panel-heading"><div><h2>Recent evidence / activity</h2><p>No activity-feed contract exists yet.</p></div></div><div className="activity-empty"><ShieldCheck aria-hidden="true" /><span>Activity remains empty until a provenance-safe API is implemented.</span></div></section>
            <aside className="authority-panel" aria-label="Authority boundary"><h2>Authority boundary</h2><p>{dashboard.data.authority_boundary}</p><dl><div><dt>ALLOW</dt><dd>Recommendation to allow a request.</dd></div><div><dt>DENY</dt><dd>Recommendation to deny a request.</dd></div><div><dt>ESCALATE</dt><dd>Requires review beyond current authority.</dd></div></dl></aside>
          </div>
        </>
      ) : null}
    </div>
  );
}
