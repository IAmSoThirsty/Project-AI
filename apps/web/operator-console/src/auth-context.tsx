import { ApiError, gateway, type BootstrapStatus, type Session } from "@project-ai/web-shared/api";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { AuthContext, type AuthContextValue, useAuth } from "./auth-store";

function cookie(name: string): string {
  const prefix = `${encodeURIComponent(name)}=`;
  const item = document.cookie.split("; ").find((value) => value.startsWith(prefix));
  return item ? decodeURIComponent(item.slice(prefix.length)) : "";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [bootstrapStatus, setBootstrapStatus] = useState<BootstrapStatus | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [csrf, setCsrf] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const status = await gateway.auth.bootstrapStatus();
        if (!active) return;
        setBootstrapStatus(status);
        if (status.status === "closed") {
          try {
            const current = await gateway.auth.session();
            if (!active) return;
            setSession(current);
            setCsrf(current.csrf_token || cookie("project_ai_csrf"));
          } catch (reason) {
            if (!(reason instanceof ApiError) || reason.status !== 401) throw reason;
          }
        }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "Authentication service unavailable");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    loading,
    bootstrapStatus,
    session,
    csrf,
    error,
    async bootstrap(payload) {
      const created = await gateway.auth.bootstrap(payload);
      setBootstrapStatus({ status: "closed", setup_secret_required: false });
      setSession(created);
      setCsrf(created.csrf_token || cookie("project_ai_csrf"));
      return created;
    },
    async login(username, password, totpCode) {
      const signedIn = await gateway.auth.login(username, password, totpCode);
      setSession(signedIn);
      setCsrf(signedIn.csrf_token || cookie("project_ai_csrf"));
    },
    async recover(username, recoveryCode, newPassword) {
      await gateway.auth.recoveryComplete(username, recoveryCode, newPassword);
      setSession(null);
      setCsrf("");
    },
    async logout() {
      if (!csrf) throw new Error("CSRF token unavailable; refresh the page before signing out.");
      await gateway.auth.logout(csrf);
      setSession(null);
      setCsrf("");
    },
    async changePassword(currentPassword, newPassword) {
      if (!csrf) throw new Error("CSRF token unavailable; refresh the page before changing the password.");
      await gateway.auth.changePassword(currentPassword, newPassword, csrf);
      setSession(null);
      setCsrf("");
    },
    async revokeSession(sessionId) {
      if (!csrf) throw new Error("CSRF token unavailable; refresh the page before revoking a session.");
      await gateway.auth.revokeSession(sessionId, csrf);
      if (sessionId === session?.session_id) {
        setSession(null);
        setCsrf("");
      }
    },
    async disableMfa(currentPassword, code) {
      if (!csrf) throw new Error("CSRF token unavailable; refresh the page before changing MFA.");
      await gateway.auth.mfaDisable(currentPassword, code, csrf);
      setSession(null);
      setCsrf("");
    },
  }), [bootstrapStatus, csrf, error, loading, session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AuthGate({ children }: { children: ReactNode }) {
  const auth = useAuth();
  if (auth.loading) return <AuthLoading />;
  if (auth.bootstrapStatus?.status === "required") return <Navigate to="/setup" replace />;
  if (auth.bootstrapStatus?.status === "unconfigured" || auth.error) {
    return <AuthUnavailable detail={auth.error || "Human account storage is not configured."} />;
  }
  if (!auth.session) return <Navigate to="/sign-in" replace />;
  return children;
}

export function EntryRedirect() {
  const auth = useAuth();
  if (auth.loading) return <AuthLoading />;
  if (auth.bootstrapStatus?.status === "required") return <Navigate to="/setup" replace />;
  if (auth.session) return <Navigate to="/command-center" replace />;
  return <Navigate to="/sign-in" replace />;
}

export function AuthLoading() {
  return <main className="auth-status" aria-live="polite"><span className="auth-spinner" /><strong>Checking local session</strong></main>;
}

export function AuthUnavailable({ detail }: { detail: string }) {
  return <main className="auth-status"><strong>Human account service unavailable</strong><p>{detail}</p><code>Set PROJECT_AI_ACCOUNT_DB and PROJECT_AI_SETUP_SECRET on the local gateway.</code></main>;
}
