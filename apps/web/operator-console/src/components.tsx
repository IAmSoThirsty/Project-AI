import { AlertTriangle, CheckCircle2, CircleOff, Clock3 } from "lucide-react";
import type { ReactNode } from "react";
import type { DashboardSurface } from "@project-ai/web-shared/api";

const statusIcon = {
  healthy: CheckCircle2,
  not_run: Clock3,
  degraded: AlertTriangle,
  unavailable: CircleOff,
};

export function SurfaceStatus({ surface }: { surface: DashboardSurface }) {
  const Icon = statusIcon[surface.status];
  return (
    <article className={`surface-status status-${surface.status}`}>
      <div className="surface-title"><Icon aria-hidden="true" /><strong>{surface.label}</strong><span>{surface.status.replace("_", " ")}</span></div>
      <p className="surface-metric">{surface.metric}</p>
      <p>{surface.detail}</p>
    </article>
  );
}

export function StatePanel({ title, children, tone = "neutral" }: { title: string; children: ReactNode; tone?: "neutral" | "warning" | "error" }) {
  return <div className={`state-panel state-${tone}`} role={tone === "error" ? "alert" : "status"} aria-label={title}><strong>{title}</strong><span>{children}</span></div>;
}

export function PageHeading({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <header className="page-heading"><div><h1>{title}</h1><p>{description}</p></div>{action}</header>;
}
