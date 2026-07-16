import { ApiError, gateway } from "@project-ai/web-shared/api";
import { useQuery } from "@tanstack/react-query";
import { Eye, EyeOff, Info, KeyRound, LockKeyhole, Network, ShieldCheck, UserRound } from "lucide-react";
import { useState, type FormEvent, type ReactNode } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../auth-store";

function AuthFrame({ children }: { children: ReactNode }) {
  const instance = useQuery({
    queryKey: ["instance-identity"],
    queryFn: gateway.instance,
    staleTime: Number.POSITIVE_INFINITY,
  });
  const instanceName = instance.data?.display_name ?? (
    instance.isError ? "Instance identity unavailable" : "Identifying local instance…"
  );
  return <main className="auth-shell">
    <section className="auth-assurance" aria-label="Authentication assurances">
      <div className="auth-brand"><span><ShieldCheck aria-hidden="true" /></span><div><strong>Project-AI</strong><small>Control Center</small></div></div>
      <div className="auth-promise"><h1>Human access. Governed execution.</h1><p>Authentication establishes identity. Authority is evaluated independently by governance policy.</p></div>
      <div className="assurance-list">
        <div><span><ShieldCheck aria-hidden="true" /></span><p><strong>Server-authenticated session</strong><small>Identity → authentication → server session</small></p></div>
        <div><span><LockKeyhole aria-hidden="true" /></span><p><strong>Governance gate remains authoritative</strong><small>Policy evaluates authority independently</small></p></div>
        <div><span><Network aria-hidden="true" /></span><p><strong>Capabilities resolve per request</strong><small>Server identity → scoped capability → execution gate</small></p></div>
      </div>
      <div className="auth-environment"><Info aria-hidden="true" /><p><strong>Local sovereign instance</strong><span>Connected to: <code>{instanceName}</code></span><small>Not a cloud login. No machine identity or execution token is stored in this browser.</small></p></div>
    </section>
    <section className="auth-workspace">{children}</section>
  </main>;
}

function PasswordField({ id, label, value, onChange, autoComplete = "current-password" }: { id: string; label: string; value: string; onChange(value: string): void; autoComplete?: string }) {
  const [visible, setVisible] = useState(false);
  return <div className="auth-field"><label htmlFor={id}>{label}</label><div className="auth-input"><LockKeyhole aria-hidden="true" /><input id={id} type={visible ? "text" : "password"} autoComplete={autoComplete} placeholder={label} value={value} onChange={(event) => onChange(event.target.value)} required /><button type="button" aria-label={visible ? "Hide password" : "Show password"} onClick={() => setVisible((state) => !state)}>{visible ? <EyeOff /> : <Eye />}</button></div></div>;
}

export function SignInRoute() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  if (auth.session) return <Navigate to="/command-center" replace />;
  if (auth.bootstrapStatus?.status === "required") return <Navigate to="/setup" replace />;
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setSubmitting(true);
    try { await auth.login(username, password, totpCode || undefined); navigate("/command-center", { replace: true }); }
    catch (reason) {
      if (reason instanceof ApiError && reason.status === 428) { setMfaRequired(true); setError(""); }
      else setError(reason instanceof Error ? reason.message : "Sign-in failed");
    }
    finally { setSubmitting(false); }
  }
  return <AuthFrame><form className="auth-form" onSubmit={submit}><header><h2>Sign in</h2><p>Use your local Project-AI account.</p></header>
    <div className="auth-field"><label htmlFor="username">Username</label><div className="auth-input"><UserRound aria-hidden="true" /><input id="username" autoComplete="username" placeholder="Username" value={username} onChange={(event) => setUsername(event.target.value)} required /></div></div>
    <PasswordField id="password" label="Password" value={password} onChange={setPassword} />
    {mfaRequired ? <div className="auth-field"><label htmlFor="totp-code">Authenticator code</label><div className="auth-input"><KeyRound aria-hidden="true" /><input id="totp-code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} value={totpCode} onChange={(event) => setTotpCode(event.target.value.replace(/\D/g, ""))} required autoFocus /></div></div> : null}
    {error ? <p className="auth-error" role="alert">{error}</p> : null}
    <button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Checking account…" : "Continue"}</button>
    <Link className="auth-link" to="/recover"><KeyRound /> Recover access</Link>
  </form></AuthFrame>;
}

export function SetupRoute() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [values, setValues] = useState({ setup_secret: "", username: "", display_name: "", actor_id: "", password: "", confirm: "" });
  const [codes, setCodes] = useState<string[]>([]);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  if (!auth.loading && auth.bootstrapStatus?.status === "closed" && !codes.length) return <Navigate to={auth.session ? "/command-center" : "/sign-in"} replace />;
  function set(name: keyof typeof values, value: string) { setValues((current) => ({ ...current, [name]: value })); }
  async function submit(event: FormEvent) {
    event.preventDefault(); setError("");
    if (values.password !== values.confirm) { setError("Passwords do not match"); return; }
    setSubmitting(true);
    try {
      const result = await auth.bootstrap({ setup_secret: values.setup_secret, username: values.username, display_name: values.display_name, password: values.password, actor_id: values.actor_id || undefined });
      setCodes(result.recovery_codes);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Setup failed"); }
    finally { setSubmitting(false); }
  }
  function downloadCodes() {
    const url = URL.createObjectURL(new Blob([`Project-AI recovery codes\n\n${codes.join("\n")}\n`], { type: "text/plain" }));
    const link = document.createElement("a"); link.href = url; link.download = "project-ai-recovery-codes.txt"; link.click(); URL.revokeObjectURL(url);
  }
  if (codes.length) return <AuthFrame><section className="auth-form recovery-codes"><header><h2>Save recovery codes</h2><p>Each code works once. They cannot be shown again.</p></header><ol>{codes.map((code) => <li key={code}><code>{code}</code></li>)}</ol><button className="auth-secondary" type="button" onClick={downloadCodes}>Download codes</button><label className="auth-checkbox"><input type="checkbox" checked={saved} onChange={(event) => setSaved(event.target.checked)} /> I saved these codes somewhere safe.</label><button className="auth-primary" type="button" disabled={!saved} onClick={() => navigate("/command-center", { replace: true })}>Enter Control Center</button></section></AuthFrame>;
  return <AuthFrame><form className="auth-form auth-form-wide" onSubmit={submit}><header><h2>Create the Owner account</h2><p>First-run setup closes permanently after this account is created.</p></header>
    <div className="auth-grid"><div className="auth-field"><label htmlFor="setup-secret">One-time setup secret</label><div className="auth-input"><KeyRound /><input id="setup-secret" type="password" autoComplete="off" value={values.setup_secret} onChange={(event) => set("setup_secret", event.target.value)} required /></div></div><div className="auth-field"><label htmlFor="display-name">Display name</label><div className="auth-input"><UserRound /><input id="display-name" autoComplete="name" value={values.display_name} onChange={(event) => set("display_name", event.target.value)} required /></div></div><div className="auth-field"><label htmlFor="setup-username">Username</label><div className="auth-input"><UserRound /><input id="setup-username" autoComplete="username" value={values.username} onChange={(event) => set("username", event.target.value)} required /></div></div><div className="auth-field"><label htmlFor="actor-id">Actor binding <span>optional</span></label><div className="auth-input"><Network /><input id="actor-id" value={values.actor_id} onChange={(event) => set("actor_id", event.target.value)} /></div></div><PasswordField id="setup-password" label="Password" value={values.password} onChange={(value) => set("password", value)} autoComplete="new-password" /><PasswordField id="confirm-password" label="Confirm password" value={values.confirm} onChange={(value) => set("confirm", value)} autoComplete="new-password" /></div>
    <p className="password-hint">At least 14 characters with uppercase, lowercase, number, and special character.</p>{error ? <p className="auth-error" role="alert">{error}</p> : null}<button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Creating protected account…" : "Create Owner account"}</button>
  </form></AuthFrame>;
}

export function RecoveryRoute() {
  const auth = useAuth(); const navigate = useNavigate();
  const [username, setUsername] = useState(""); const [code, setCode] = useState(""); const [password, setPassword] = useState(""); const [confirm, setConfirm] = useState(""); const [message, setMessage] = useState(""); const [error, setError] = useState("");
  async function submit(event: FormEvent) { event.preventDefault(); setError(""); if (password !== confirm) { setError("Passwords do not match"); return; } try { await auth.recover(username, code, password); setMessage("Recovery complete. Sign in with your new password."); } catch (reason) { setError(reason instanceof Error ? reason.message : "Recovery failed"); } }
  return <AuthFrame><form className="auth-form" onSubmit={submit}><header><h2>Recover access</h2><p>Use one of the recovery codes saved during Owner setup.</p></header><div className="auth-field"><label htmlFor="recovery-username">Username</label><div className="auth-input"><UserRound /><input id="recovery-username" autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required /></div></div><div className="auth-field"><label htmlFor="recovery-code">Recovery code</label><div className="auth-input"><KeyRound /><input id="recovery-code" autoComplete="one-time-code" value={code} onChange={(event) => setCode(event.target.value.toUpperCase())} required /></div></div><PasswordField id="recovery-password" label="New password" value={password} onChange={setPassword} autoComplete="new-password" /><PasswordField id="recovery-confirm" label="Confirm new password" value={confirm} onChange={setConfirm} autoComplete="new-password" />{error ? <p className="auth-error" role="alert">{error}</p> : null}{message ? <p className="auth-success" role="status">{message}</p> : null}<button className="auth-primary" type="submit">Reset password</button><button className="auth-link auth-link-button" type="button" onClick={() => navigate("/sign-in")}>Back to sign in</button></form></AuthFrame>;
}
