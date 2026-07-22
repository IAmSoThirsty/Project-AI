import {
  Bell,
  Activity,
  BookOpenCheck,
  Boxes,
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
import { useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { gateway, type WorkRequest } from "@project-ai/web-shared/api";

import { useAuth } from "./auth-store";
import { useBrowserOnline } from "./browser-status";

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

const focusableSelector = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

function trapFocusWithin(container: HTMLElement, event: KeyboardEvent) {
  if (event.key !== "Tab") return;
  const focusable = Array.from(container.querySelectorAll<HTMLElement>(focusableSelector));
  if (!focusable.length) {
    event.preventDefault();
    return;
  }
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const active = document.activeElement;
  if (event.shiftKey && (active === first || !container.contains(active))) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && (active === last || !container.contains(active))) {
    event.preventDefault();
    first.focus();
  }
}

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(
    () => typeof window.matchMedia === "function" && window.matchMedia(query).matches,
  );
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const media = window.matchMedia(query);
    const update = () => setMatches(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [query]);
  return matches;
}

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
  const instance = useQuery({ queryKey: ["instance"], queryFn: gateway.instance, staleTime: Infinity });
  const health = useQuery({
    queryKey: ["gateway-health"],
    queryFn: gateway.health,
    refetchInterval: 15_000,
    retry: false,
  });
  const browserOnline = useBrowserOnline();
  const isNarrowNavigation = useMediaQuery("(max-width: 920px)");
  const mainContentRef = useRef<HTMLElement>(null);
  const navigationCloseRef = useRef<HTMLButtonElement>(null);
  const navigationDialogRef = useRef<HTMLDivElement>(null);
  const navigationTriggerRef = useRef<HTMLButtonElement>(null);
  const notificationCloseRef = useRef<HTMLButtonElement>(null);
  const notificationTriggerRef = useRef<HTMLButtonElement>(null);
  const searchDialogRef = useRef<HTMLElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchReturnFocusRef = useRef<HTMLElement | null>(null);
  const searchTriggerRef = useRef<HTMLButtonElement>(null);
  const previousPathRef = useRef(location.pathname);
  const closeNavigation = useCallback((restoreFocus = true) => {
    setNavigationOpen(false);
    if (restoreFocus) {
      window.requestAnimationFrame(() => navigationTriggerRef.current?.focus());
    }
  }, []);
  const closeNotifications = useCallback((restoreFocus = true) => {
    setNotificationsOpen(false);
    if (restoreFocus) {
      window.requestAnimationFrame(() => notificationTriggerRef.current?.focus());
    }
  }, []);
  const openNavigation = useCallback(() => {
    setSearchOpen(false);
    closeNotifications(false);
    setNavigationOpen(true);
  }, [closeNotifications]);
  const closeSearch = useCallback((restoreFocus = true) => {
    setSearchOpen(false);
    if (restoreFocus) {
      window.requestAnimationFrame(() => searchReturnFocusRef.current?.focus());
    }
  }, []);
  const openSearch = useCallback(() => {
    searchReturnFocusRef.current = document.activeElement instanceof HTMLElement
      ? document.activeElement
      : searchTriggerRef.current;
    closeNotifications(false);
    setNavigationOpen(false);
    setSearchOpen(true);
  }, [closeNotifications]);
  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (searchOpen) closeSearch();
        else openSearch();
      }
      if (event.key === "Escape") {
        if (searchOpen) closeSearch();
        else if (isNarrowNavigation && navigationOpen) closeNavigation();
        else if (notificationsOpen) closeNotifications();
      }
    }
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, [closeNavigation, closeNotifications, closeSearch, isNarrowNavigation, navigationOpen, notificationsOpen, openSearch, searchOpen]);
  useEffect(() => {
    if (!isNarrowNavigation || !navigationOpen) return;
    const navigation = navigationDialogRef.current;
    if (!navigation) return;
    const frame = window.requestAnimationFrame(() => navigationCloseRef.current?.focus());
    const trap = (event: KeyboardEvent) => trapFocusWithin(navigation, event);
    navigation.addEventListener("keydown", trap);
    return () => {
      window.cancelAnimationFrame(frame);
      navigation.removeEventListener("keydown", trap);
    };
  }, [isNarrowNavigation, navigationOpen]);
  useEffect(() => {
    if (!isNarrowNavigation) setNavigationOpen(false);
  }, [isNarrowNavigation]);
  useEffect(() => {
    if (!searchOpen) return;
    const dialog = searchDialogRef.current;
    if (!dialog) return;
    const activeDialog = dialog;
    const frame = window.requestAnimationFrame(() => searchInputRef.current?.focus());
    const trap = (event: KeyboardEvent) => trapFocusWithin(activeDialog, event);
    activeDialog.addEventListener("keydown", trap);
    return () => {
      window.cancelAnimationFrame(frame);
      activeDialog.removeEventListener("keydown", trap);
    };
  }, [searchOpen]);
  useEffect(() => {
    if (!notificationsOpen) return;
    const frame = window.requestAnimationFrame(() => notificationCloseRef.current?.focus());
    return () => window.cancelAnimationFrame(frame);
  }, [notificationsOpen]);
  useEffect(() => {
    if (previousPathRef.current === location.pathname) return;
    previousPathRef.current = location.pathname;
    setNavigationOpen(false);
    setSearchOpen(false);
    closeNotifications(false);
    const frame = window.requestAnimationFrame(() => mainContentRef.current?.focus());
    return () => window.cancelAnimationFrame(frame);
  }, [closeNotifications, location.pathname]);
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
    setSearchOpen(false);
    setNavigationOpen(false);
    if (!next) {
      closeNotifications();
      return;
    }
    setNotificationsOpen(true);
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
  const instanceLabel = instance.data?.display_name ?? "Instance unavailable";
  const connection = !browserOnline
    ? { key: "offline", label: "Browser offline", detail: "The browser reports no network connection." }
    : health.isRefetchError
      ? { key: "stale", label: "Gateway stale", detail: "The last successful liveness response is retained." }
      : health.isError
        ? { key: "unavailable", label: "Gateway unavailable", detail: "No liveness response was received." }
        : health.isPending
          ? { key: "checking", label: "Checking gateway", detail: "Waiting for the liveness endpoint." }
          : { key: "live", label: "Gateway live", detail: `Liveness verified for version ${health.data.version}.` };
  const lastLiveAt = health.dataUpdatedAt > 0 ? new Date(health.dataUpdatedAt) : null;
  const docsHref = import.meta.env.VITE_DOCS_URL || (import.meta.env.DEV ? "http://127.0.0.1:4173/" : "/docs/");
  const navigationHidden = isNarrowNavigation && !navigationOpen;
  return (
    <div className="control-center-shell">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <div
        ref={navigationDialogRef}
        className={`console-sidebar ${navigationOpen ? "is-open" : ""}`}
        aria-label="Control Center sidebar"
        aria-hidden={navigationHidden || undefined}
        aria-modal={isNarrowNavigation && navigationOpen ? true : undefined}
        inert={navigationHidden || undefined}
        role={isNarrowNavigation ? "dialog" : "complementary"}
      >
        <div className="console-brand">
          <span className="console-brand-mark"><ShieldCheck aria-hidden="true" /></span>
          <span><strong>Project-AI</strong><small>Control Center</small></span>
          <button ref={navigationCloseRef} className="mobile-close" type="button" aria-label="Close navigation" onClick={() => closeNavigation()}><X /></button>
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
      </div>

      <div className="console-stage" aria-hidden={isNarrowNavigation && navigationOpen || undefined} inert={isNarrowNavigation && navigationOpen || undefined}>
        <header className="console-topbar">
          <button ref={navigationTriggerRef} className="mobile-menu" type="button" aria-label="Open navigation" aria-haspopup="dialog" aria-expanded={navigationOpen} onClick={openNavigation}><Menu /></button>
          <div className="environment-control" role="status" aria-label={`Environment: ${instanceLabel}`} title={instanceLabel}>
            <span>Environment</span><strong>{instanceLabel}</strong><small className={`mobile-gateway-state connection-${connection.key}`} aria-hidden="true">{connection.label}</small>
          </div>
          <div className={`freshness connection-${connection.key}`} role="status" aria-label={`${connection.label}. ${connection.detail}`} title={connection.detail}>
            <span className="connection-dot" aria-hidden="true" /><span><small>Gateway connection</small><strong>{connection.label}</strong>{connection.key === "stale" && lastLiveAt ? <time dateTime={lastLiveAt.toISOString()}>Last live {lastLiveAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time> : null}</span>
          </div>
          <button ref={searchTriggerRef} className="command-search" type="button" aria-label="Search Control Center screens" aria-haspopup="dialog" aria-expanded={searchOpen} onClick={openSearch}>
            <Search aria-hidden="true" /><span>Search Control Center screens…</span><kbd><Command /> K</kbd>
          </button>
          <div className="topbar-actions">
            <button ref={notificationTriggerRef} type="button" aria-label="Open work notifications" aria-controls="work-notifications" aria-expanded={notificationsOpen} onClick={openNotifications}><Bell /></button>
            <a className="help-link" href={docsHref} target="_blank" rel="noreferrer" aria-label="Open operator documentation"><CircleHelp aria-hidden="true" /></a>
            <NavLink className="profile-control" to="/profile/security" aria-label="Open account security">
              <span className="avatar">{initials}</span><span><strong>{session?.account.display_name}</strong><small>{session?.account.role}</small></span>
            </NavLink>
          </div>
        </header>
        {notificationsOpen ? <aside id="work-notifications" className="notification-popover" role="dialog" aria-label="Work notifications"><div><strong>Awaiting review</strong><button ref={notificationCloseRef} type="button" aria-label="Close notifications" onClick={() => closeNotifications()}><X /></button></div>{notificationError ? <p role="alert">{notificationError}</p> : notifications.length === 0 ? <p>No submitted requests are visible to this account.</p> : notifications.slice(0, 6).map((item) => <button type="button" key={item.id} onClick={() => { closeNotifications(false); navigate("/requests"); }}><strong>{item.title}</strong><span>{item.operation} · {item.resource}</span></button>)}</aside> : null}
        <main ref={mainContentRef} id="main-content" tabIndex={-1}><Outlet /></main>
      </div>
      {navigationOpen ? <button className="nav-scrim" type="button" tabIndex={-1} aria-label="Close navigation overlay" onClick={() => closeNavigation()} /> : null}
      {searchOpen ? <div className="command-overlay" role="presentation" onMouseDown={() => closeSearch()}><section ref={searchDialogRef} className="command-dialog" role="dialog" aria-modal="true" aria-label="Search Control Center screens" onMouseDown={(event) => event.stopPropagation()}><label><Search aria-hidden="true" /><input ref={searchInputRef} value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Type a screen name" aria-label="Screen search" /><kbd>Esc</kbd></label><div>{destinations.length === 0 ? <p>No matching screen.</p> : destinations.map(({ to, label, icon: Icon }) => <button type="button" key={to} onClick={() => chooseDestination(to)}><Icon aria-hidden="true" /><span>{label}</span></button>)}</div></section></div> : null}
    </div>
  );
}
