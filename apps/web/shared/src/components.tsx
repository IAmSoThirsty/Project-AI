import { BookOpenText, Menu, ShieldCheck, X } from "lucide-react";
import { type ReactNode, useState } from "react";

type NavItem = { id: string; label: string };

export function PortalShell({
  lane,
  active,
  items,
  onNavigate,
  children,
}: {
  lane: "Documentation" | "Proof";
  active: string;
  items: NavItem[];
  onNavigate: (id: string) => void;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const LaneIcon = lane === "Documentation" ? BookOpenText : ShieldCheck;
  return (
    <div className="app-root">
      <div className="site-noise" aria-hidden="true" />
      <div className="site-grid" aria-hidden="true" />
      <header className="topbar scrolled">
        <button className="brand brand-button" onClick={() => onNavigate(items[0].id)}>
          <span className="brand-mark">PAI</span>
          <span className="brand-copy">
            <strong>Project-AI</strong>
            <em>{lane} portal</em>
          </span>
        </button>
        <button
          className="nav-toggle"
          aria-label={open ? "Close navigation" : "Open navigation"}
          aria-expanded={open}
          onClick={() => setOpen((current) => !current)}
        >
          {open ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
        </button>
        <nav className={`nav ${open ? "open" : ""}`} aria-label={`${lane} navigation`}>
          {items.map((item) => (
            <button
              className={active === item.id ? "active" : ""}
              key={item.id}
              onClick={() => {
                onNavigate(item.id);
                setOpen(false);
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="lane-chip">
          <LaneIcon size={15} aria-hidden="true" />
          {lane}
        </div>
      </header>
      <main>{children}</main>
      <footer className="footer">
        <div className="wrap footer-inner">
          <span>Project-AI / {lane}</span>
          <span>Release candidate 0.0.3</span>
        </div>
      </footer>
    </div>
  );
}

export function StatusPill({ status, label }: { status: string; label: string }) {
  return (
    <span className={`status-pill status-${status}`}>
      <span className="status-dot" aria-hidden="true" />
      {label}
    </span>
  );
}

export function LoadingPanel({ label }: { label: string }) {
  return (
    <div className="loading-panel" role="status">
      <span className="loading-line" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="error-panel" role="alert">
      <strong>Surface unavailable</strong>
      <span>{message}</span>
    </div>
  );
}
