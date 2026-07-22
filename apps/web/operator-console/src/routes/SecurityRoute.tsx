import { gateway, type MfaEnrollment, type MfaStatus, type SessionInfo } from "@project-ai/web-shared/api";
import { KeyRound, LogOut, MonitorSmartphone, ShieldCheck, ShieldPlus, Trash2 } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../auth-store";
import { PageHeading, StatePanel } from "../components";

type PendingAction = "revoke" | "logout" | "password" | "mfa-enroll" | "mfa-confirm" | "mfa-step-up" | "mfa-disable" | null;

export function SecurityRoute() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [mfa, setMfa] = useState<MfaStatus | null>(null);
  const [enrollment, setEnrollment] = useState<MfaEnrollment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [passwords, setPasswords] = useState({ current: "", next: "", confirm: "" });
  const [mfaForm, setMfaForm] = useState({ password: "", code: "" });
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);

  useEffect(() => {
    let active = true;
    Promise.all([gateway.auth.sessions(), gateway.auth.mfaStatus()])
      .then(([sessionResult, mfaResult]) => {
        if (!active) return;
        setSessions(sessionResult.sessions);
        setMfa(mfaResult);
      })
      .catch((reason) => {
        if (active) setLoadError(reason instanceof Error ? reason.message : "Security settings unavailable");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => { active = false; };
  }, []);

  function clearMessages() { setError(""); setNotice(""); }

  async function revoke(item: SessionInfo) {
    if (pendingAction) return;
    setPendingAction("revoke"); clearMessages();
    try {
      await auth.revokeSession(item.id);
      if (item.current) { navigate("/sign-in", { replace: true }); return; }
      setSessions((current) => current.map((session) => session.id === item.id ? { ...session, revoked: true } : session));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Revocation failed"); }
    finally { setPendingAction(null); }
  }

  async function logout() {
    if (pendingAction) return;
    setPendingAction("logout"); clearMessages();
    try { await auth.logout(); navigate("/sign-in", { replace: true }); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Sign-out failed"); }
    finally { setPendingAction(null); }
  }

  async function changePassword(event: FormEvent) {
    event.preventDefault();
    if (pendingAction) return;
    clearMessages();
    if (passwords.next !== passwords.confirm) { setError("New passwords do not match"); return; }
    setPendingAction("password");
    try {
      await auth.changePassword(passwords.current, passwords.next);
      navigate("/sign-in", { replace: true });
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Password change failed"); }
    finally { setPendingAction(null); }
  }

  async function beginMfa(event: FormEvent) {
    event.preventDefault();
    if (pendingAction) return;
    setPendingAction("mfa-enroll"); clearMessages();
    try {
      setEnrollment(await gateway.auth.mfaEnroll(mfaForm.password, auth.csrf));
      setMfa({ enabled: false, enrollment_pending: true });
      setNotice("Add the secret to your authenticator, then confirm a current code.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "MFA enrollment failed"); }
    finally { setPendingAction(null); }
  }

  async function confirmMfa(event: FormEvent) {
    event.preventDefault();
    if (pendingAction) return;
    setPendingAction("mfa-confirm"); clearMessages();
    try {
      await gateway.auth.mfaConfirm(mfaForm.code, auth.csrf);
      setMfa({ enabled: true, enrollment_pending: false });
      setEnrollment(null);
      setMfaForm({ password: "", code: "" });
      setNotice("Authenticator enabled. New sign-ins now require a fresh code.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "MFA confirmation failed"); }
    finally { setPendingAction(null); }
  }

  async function stepUp(event: FormEvent) {
    event.preventDefault();
    if (pendingAction) return;
    setPendingAction("mfa-step-up"); clearMessages();
    try {
      await gateway.auth.mfaStepUp(mfaForm.code, auth.csrf);
      setMfaForm((current) => ({ ...current, code: "" }));
      setNotice("Step-up authentication completed for this session.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Step-up failed"); }
    finally { setPendingAction(null); }
  }

  async function disableMfa(event: FormEvent) {
    event.preventDefault();
    if (pendingAction) return;
    setPendingAction("mfa-disable"); clearMessages();
    try {
      await auth.disableMfa(mfaForm.password, mfaForm.code);
      navigate("/sign-in", { replace: true });
    } catch (reason) { setError(reason instanceof Error ? reason.message : "MFA removal failed"); }
    finally { setPendingAction(null); }
  }

  return <div className="console-page">
    <PageHeading title="Account security" description="Your human session identifies requests. It never grants execution authority." action={<button className="icon-button" type="button" disabled={Boolean(pendingAction)} onClick={logout}><LogOut /> {pendingAction === "logout" ? "Signing out…" : "Sign out"}</button>} />
    {isLoading ? <StatePanel title="Loading account security">Reading active sessions and authenticator state.</StatePanel> : null}
    {loadError ? <StatePanel title="Account security unavailable" tone="error">Session and authenticator controls are hidden because the initial read failed. {loadError}</StatePanel> : null}
    {error ? <StatePanel title="Security action failed" tone="error">{error}</StatePanel> : null}
    {notice ? <StatePanel title="Security updated">{notice}</StatePanel> : null}
    {!isLoading && !loadError ? <div className="security-grid">
      <section className="records-panel security-panel">
        <div className="panel-heading"><div><h2>Active sessions</h2><p>Opaque server-side sessions; raw tokens are never displayed.</p></div><MonitorSmartphone /></div>
        <div className="session-list">{sessions.length > 0 ? sessions.map((item) => <article key={item.id}><div><strong>{item.current ? "This browser" : item.user_agent}</strong><span>{item.client_host} · Last active {new Date(item.last_seen_at).toLocaleString()}</span><small>Absolute expiry {new Date(item.absolute_expires_at).toLocaleString()}{item.mfa_verified_at ? " · MFA verified" : ""}</small></div><span className={item.revoked ? "session-revoked" : "session-active"}>{item.revoked ? "Revoked" : item.current ? "Current" : "Active"}</span>{!item.revoked ? <button type="button" disabled={Boolean(pendingAction)} onClick={() => revoke(item)} aria-label={`Revoke ${item.current ? "current session" : item.user_agent}`}><Trash2 /> {pendingAction === "revoke" ? "Revoking…" : "Revoke"}</button> : null}</article>) : <p>No server sessions were returned for this account.</p>}</div>
      </section>

      <section className="records-panel security-panel">
        <div className="panel-heading"><div><h2>Authenticator</h2><p>Time-based codes protect sign-in and step-up actions.</p></div><ShieldPlus /></div>
        {!mfa?.enabled && !enrollment ? <form className="security-form" onSubmit={beginMfa}><label>Current password<input type="password" autoComplete="current-password" value={mfaForm.password} onChange={(event) => setMfaForm({ ...mfaForm, password: event.target.value })} required /></label><button type="submit" disabled={Boolean(pendingAction)}><ShieldPlus /> {pendingAction === "mfa-enroll" ? "Setting up authenticator…" : "Set up authenticator"}</button></form> : null}
        {enrollment ? <form className="security-form" onSubmit={confirmMfa}><p>Enter this secret manually in your authenticator. It is shown only during this enrollment.</p><code className="mfa-secret">{enrollment.secret}</code><label>Authenticator code<input inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} value={mfaForm.code} onChange={(event) => setMfaForm({ ...mfaForm, code: event.target.value.replace(/\D/g, "") })} required /></label><button type="submit" disabled={Boolean(pendingAction)}><ShieldCheck /> {pendingAction === "mfa-confirm" ? "Confirming authenticator…" : "Confirm authenticator"}</button></form> : null}
        {mfa?.enabled ? <><form className="security-form" onSubmit={stepUp}><label>Fresh authenticator code<input inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} value={mfaForm.code} onChange={(event) => setMfaForm({ ...mfaForm, code: event.target.value.replace(/\D/g, "") })} required /></label><button type="submit" disabled={Boolean(pendingAction)}><ShieldCheck /> {pendingAction === "mfa-step-up" ? "Verifying session…" : "Verify this session"}</button></form><details className="danger-zone"><summary>Remove authenticator</summary><form className="security-form" onSubmit={disableMfa}><p>Removal requires your password and a fresh code, then revokes every session.</p><label>Current password<input type="password" autoComplete="current-password" value={mfaForm.password} onChange={(event) => setMfaForm({ ...mfaForm, password: event.target.value })} required /></label><label>Fresh authenticator code<input inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} value={mfaForm.code} onChange={(event) => setMfaForm({ ...mfaForm, code: event.target.value.replace(/\D/g, "") })} required /></label><button type="submit" disabled={Boolean(pendingAction)}>{pendingAction === "mfa-disable" ? "Removing authenticator…" : "Remove and sign out"}</button></form></details></> : null}
      </section>

      <section className="records-panel security-panel">
        <div className="panel-heading"><div><h2>Change password</h2><p>Changing it revokes every session, including this one.</p></div><KeyRound /></div>
        <form className="security-form" onSubmit={changePassword}><label>Current password<input type="password" autoComplete="current-password" value={passwords.current} onChange={(event) => setPasswords({ ...passwords, current: event.target.value })} required /></label><label>New password<input type="password" autoComplete="new-password" value={passwords.next} onChange={(event) => setPasswords({ ...passwords, next: event.target.value })} required /></label><label>Confirm new password<input type="password" autoComplete="new-password" value={passwords.confirm} onChange={(event) => setPasswords({ ...passwords, confirm: event.target.value })} required /></label><p>At least 14 characters with uppercase, lowercase, number, and special character.</p><button type="submit" disabled={Boolean(pendingAction)}><ShieldCheck /> {pendingAction === "password" ? "Changing password…" : "Change password"}</button></form>
      </section>
    </div> : null}
  </div>;
}
