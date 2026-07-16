import {
  Bell,
  Activity,
  BookOpenCheck,
  Boxes,
  ChevronDown,
  CircleHelp,
  ClipboardList,
  Command,
  FileClock,
  FlaskConical,
  Gauge,
  Inbox,
  Menu,
  Search,
  Settings,
  Shield,
  ShieldCheck,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { gateway, type WorkRequest } from "@project-ai/web-shared/api";

import { useAuth } from "./auth-store";

const availableNavigation = [
  { to: "/command-center", label: "Command Center", icon: Gauge },
  { to: "/inbox", label: "My Inbox", icon: Inbox },
  { to: "/requests", label: "Requests", icon: ClipboardList },
  { to: "/evidence", label: "Evidence", icon: BookOpenCheck },
  { to: "/evidence/audit", label: "Audit explorer", icon: FileClock },
  { to: "/governance", label: "Governance", icon: ShieldCheck },
  { to: "/security", label: "Security", icon: Shield },
  { to: "/simulations", label: "Simulations", icon: FlaskConical },
  { to: "/system/health", label: "System health", icon: Activity },
];

export function ControlCenterShell() {
  const [navigationOpen, setNavigationOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<WorkRequest[]>([]);
  const [notificationError, setNotificationError] = useState("");
  const { session } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen((current) => !current);
      }
      if (event.key === "Escape") {
        setSearchOpen(false);
        setNotificationsOpen(false);
      }
    }
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);
  const destinations = useMemo(() => {
    const items = [
      ...availableNavigation,
      { to: "/profile/security", label: "Account security", icon: Shield },
      { to: "/profile/preferences", label: "Display preferences", icon: Settings },
    ];
    if (session?.account.role === "owner" || session?.account.role === "administrator") {
      items.push({ to: "/administration/accounts", label: "Account administration", icon: Settings });
    }
    return items.filter((item) => item.label.toLowerCase().includes(searchQuery.trim().toLowerCase()));
  }, [searchQuery, session?.account.role]);

  function openNotifications() {
    const next = !notificationsOpen;
    setNotificationsOpen(next);
    setSearchOpen(false);
    if (!next) return;
    setNotificationError("");
    gateway.work.requests()
      .then((response) => setNotifications(response.requests.filter((item) => item.state === "submitted")))
      .catch((reason) => setNotificationError(reason instanceof Error ? reason.message : "Notifications unavailable"));
  }

  function chooseDestination(path: string) {
    setSearchOpen(false);
    setSearchQuery("");
    navigate(path);
  }
  if (session?.account.must_change_password && location.pathname !== "/profile/security") {
    return <Navigate to="/profile/security" replace />;
  }
  const initials = session?.account.display_name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "?";
  return (
    <div className="control-center-shell">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <aside
        className={`console-sidebar ${navigationOpen ? "is-open" : ""}`}
        aria-label="Control Center sidebar"
      >
        <div className="console-brand">
          <span className="console-brand-mark"><ShieldCheck aria-hidden="true" /></span>
          <span><strong>Project-AI</strong><small>Control Center</small></span>
          <button className="mobile-close" type="button" aria-label="Close navigation" onClick={() => setNavigationOpen(false)}><X /></button>
        </div>
        <nav className="console-nav" aria-label="Primary navigation">
          {availableNavigation.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} onClick={() => setNavigationOpen(false)}>
              <Icon aria-hidden="true" /> <span>{label}</span>
            </NavLink>
          ))}
          <div className="nav-divider" />
          {session?.account.role === "owner" || session?.account.role === "administrator" ? <NavLink to="/administration/accounts" onClick={() => setNavigationOpen(false)}><Settings aria-hidden="true" /><span>Administration</span></NavLink> : null}
          <NavLink to="/profile/preferences" onClick={() => setNavigationOpen(false)}><Settings aria-hidden="true" /><span>Preferences</span></NavLink>
        </nav>
        <div className="sidebar-foot"><Boxes aria-hidden="true" /><span>Development surface</span></div>
      </aside>

      <div className="console-stage">
        <header className="console-topbar">
          <button className="mobile-menu" type="button" aria-label="Open navigation" onClick={() => setNavigationOpen(true)}><Menu /></button>
          <button className="environment-control" type="button" aria-label="Environment: local development">
            <span>Environment</span><strong>Local development</strong><ChevronDown aria-hidden="true" />
          </button>
          <div className="freshness"><span className="healthy-dot" /><span><small>Gateway freshness</small><strong>Live query</strong></span></div>
          <button className="command-search" type="button" onClick={() => { setSearchOpen(true); setNotificationsOpen(false); }}>
            <Search aria-hidden="true" /><span>Search Control Center screens…</span><kbd><Command /> K</kbd>
          </button>
          <div className="topbar-actions">
            <button type="button" aria-label="Open work notifications" aria-expanded={notificationsOpen} onClick={openNotifications}><Bell /></button>
            <button type="button" aria-label="Open help"><CircleHelp /></button>
            <NavLink className="profile-control" to="/profile/security" aria-label="Open account security">
              <span className="avatar">{initials}</span><span><strong>{session?.account.display_name}</strong><small>{session?.account.role}</small></span>
            </NavLink>
          </div>
        </header>
        {notificationsOpen ? <aside className="notification-popover" aria-label="Work notifications"><div><strong>Awaiting review</strong><button type="button" aria-label="Close notifications" onClick={() => setNotificationsOpen(false)}><X /></button></div>{notificationError ? <p role="alert">{notificationError}</p> : notifications.length === 0 ? <p>No submitted requests are visible to this account.</p> : notifications.slice(0, 6).map((item) => <button type="button" key={item.id} onClick={() => { setNotificationsOpen(false); navigate("/requests"); }}><strong>{item.title}</strong><span>{item.operation} · {item.resource}</span></button>)}</aside> : null}
        <main id="main-content" tabIndex={-1}><Outlet /></main>
      </div>
      {navigationOpen ? <button className="nav-scrim" aria-label="Close navigation overlay" onClick={() => setNavigationOpen(false)} /> : null}
      {searchOpen ? <div className="command-overlay" role="presentation" onMouseDown={() => setSearchOpen(false)}><section className="command-dialog" role="dialog" aria-modal="true" aria-label="Search Control Center screens" onMouseDown={(event) => event.stopPropagation()}><label><Search aria-hidden="true" /><input autoFocus value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Type a screen name" aria-label="Screen search" /><kbd>Esc</kbd></label><div>{destinations.length === 0 ? <p>No matching screen.</p> : destinations.map(({ to, label, icon: Icon }) => <button type="button" key={to} onClick={() => chooseDestination(to)}><Icon aria-hidden="true" /><span>{label}</span></button>)}</div></section></div> : null}
    </div>
  );
}
