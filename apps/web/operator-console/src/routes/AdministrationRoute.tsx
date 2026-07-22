import { ApiError, gateway, type AuthAccount, type ManagedAccount, type SecurityEvent } from "@project-ai/web-shared/api";
import { KeyRound, ShieldCheck, UserPlus, Users } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

type ManagedRole = Exclude<AuthAccount["role"], "owner">;
const roles: ManagedRole[] = ["administrator", "operator", "reviewer", "auditor", "viewer"];

export function AdministrationRoute() {
  const auth = useAuth();
  const [accounts, setAccounts] = useState<ManagedAccount[]>([]);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [form, setForm] = useState({ username: "", display_name: "", password: "", role: "operator" as ManagedRole, actor_id: "" });
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [creatingAccount, setCreatingAccount] = useState(false);
  const [accountAction, setAccountAction] = useState<{ id: string; kind: "role" | "status" } | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([gateway.admin.accounts(), gateway.admin.securityEvents()])
      .then(([accountResult, eventResult]) => {
        if (!active) return;
        setAccounts(accountResult.accounts);
        setEvents(eventResult.events.slice(-50).reverse());
      })
      .catch((reason) => {
        if (!active) return;
        if (reason instanceof ApiError && reason.status === 403) {
          setAccessDenied(true);
          return;
        }
        setLoadError(reason instanceof Error ? reason.message : "Administration unavailable");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => { active = false; };
  }, []);

  function clearMessages() { setError(""); setNotice(""); }

  async function createAccount(event: FormEvent) {
    event.preventDefault();
    if (creatingAccount) return;
    setCreatingAccount(true); clearMessages();
    try {
      const result = await gateway.admin.createAccount({ ...form, actor_id: form.actor_id || undefined }, auth.csrf);
      setAccounts((current) => [...current, result.account]);
      setRecoveryCodes(result.recovery_codes);
      setForm({ username: "", display_name: "", password: "", role: "operator", actor_id: "" });
      setNotice("Account created. Transfer the temporary password and recovery codes through separate secure channels.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Account creation failed"); }
    finally { setCreatingAccount(false); }
  }

  async function changeRole(account: ManagedAccount, role: ManagedRole) {
    if (accountAction) return;
    setAccountAction({ id: account.id, kind: "role" }); clearMessages();
    try {
      await gateway.admin.changeRole(account.id, role, auth.csrf);
      setAccounts((current) => current.map((item) => item.id === account.id ? { ...item, role } : item));
      setNotice("Role changed and the account's active sessions were revoked.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Role change failed"); }
    finally { setAccountAction(null); }
  }

  async function toggleStatus(account: ManagedAccount) {
    if (accountAction) return;
    setAccountAction({ id: account.id, kind: "status" }); clearMessages(); const enabled = account.status !== "active";
    try {
      await gateway.admin.changeStatus(account.id, enabled, auth.csrf);
      setAccounts((current) => current.map((item) => item.id === account.id ? { ...item, status: enabled ? "active" : "disabled" } : item));
      setNotice(enabled ? "Account enabled." : "Account disabled and its sessions revoked.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Status change failed"); }
    finally { setAccountAction(null); }
  }

  return <div className="console-page">
    <PageHeading title="Administration" description="Manage human interface access. These roles do not grant execution authority." />
    {isLoading ? <StatePanel title="Loading administration">Reading human accounts and account-security events.</StatePanel> : null}
    {accessDenied ? <StatePanel title="Administration access restricted" tone="warning">Your current interface role cannot manage human accounts. Account controls and security events are hidden.</StatePanel> : null}
    {loadError ? <StatePanel title="Administration unavailable" tone="error">Account controls and event lists are hidden because the initial read failed. {loadError}</StatePanel> : null}
    {error ? <StatePanel title="Administrative action failed" tone="error">{error}</StatePanel> : null}
    {notice ? <StatePanel title="Administration updated">{notice}</StatePanel> : null}
    {!isLoading && !accessDenied && !loadError ? <>{recoveryCodes.length ? <section className="records-panel recovery-handoff"><div className="panel-heading"><div><h2>One-time recovery codes</h2><p>These cannot be retrieved after you dismiss them.</p></div><KeyRound /></div><ol>{recoveryCodes.map((code) => <li key={code}><code>{code}</code></li>)}</ol><button type="button" onClick={() => setRecoveryCodes([])}>I transferred these codes securely</button></section> : null}
    <div className="admin-grid">
      <section className="records-panel security-panel">
        <div className="panel-heading"><div><h2>Create account</h2><p>The user must change the temporary password before using protected product surfaces.</p></div><UserPlus /></div>
        <form className="security-form" onSubmit={createAccount}><label>Display name<input value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} required /></label><label>Username<input autoComplete="off" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} required /></label><label>Temporary password<input type="password" autoComplete="new-password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required /></label><label>Interface role<select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as ManagedRole })}>{roles.map((role) => <option key={role} value={role}>{role}</option>)}</select></label><label>Actor binding (optional)<input value={form.actor_id} onChange={(event) => setForm({ ...form, actor_id: event.target.value })} /></label><button type="submit" disabled={creatingAccount}><UserPlus /> {creatingAccount ? "Creating account…" : "Create account"}</button></form>
      </section>
      <section className="records-panel accounts-panel">
        <div className="panel-heading"><div><h2>Human accounts</h2><p>Role and status changes are server-authorized and audit-recorded.</p></div><Users /></div>
        <div className="account-list">{accounts.length > 0 ? accounts.map((account) => <article key={account.id}><div><strong>{account.display_name}</strong><span>@{account.username} · {account.actor_id ?? "No actor binding"}</span><small>{account.must_change_password ? "Password change required" : account.mfa_enabled ? "MFA enabled" : "MFA not enabled"}</small></div><span className={account.status === "active" ? "session-active" : "session-revoked"}>{account.status}</span>{account.role === "owner" ? <strong>Owner</strong> : <><select aria-label={`Role for ${account.display_name}`} disabled={Boolean(accountAction)} value={account.role} onChange={(event) => changeRole(account, event.target.value as ManagedRole)}>{roles.map((role) => <option key={role} value={role}>{role}</option>)}</select><button type="button" disabled={Boolean(accountAction)} onClick={() => toggleStatus(account)}>{accountAction?.id === account.id && accountAction.kind === "status" ? "Updating status…" : account.status === "active" ? "Disable" : "Enable"}</button></>}</article>) : <p>No human accounts were returned by the server.</p>}</div>
      </section>
    </div>
    <section className="records-panel events-panel"><div className="panel-heading"><div><h2>Recent account security events</h2><p>Append-only local authentication evidence.</p></div><ShieldCheck /></div><div className="event-list">{events.length > 0 ? events.map((event) => <article key={event.id}><strong>{event.event_type}</strong><span>{event.source}</span><time>{new Date(event.occurred_at).toLocaleString()}</time></article>) : <p>No account security events were returned.</p>}</div></section></> : null}
  </div>;
}
