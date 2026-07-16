import type { BootstrapSession, BootstrapStatus, Session } from "@project-ai/web-shared/api";
import { createContext, useContext } from "react";

export type BootstrapPayload = {
  setup_secret: string;
  username: string;
  display_name: string;
  password: string;
  actor_id?: string;
};

export type AuthContextValue = {
  loading: boolean;
  bootstrapStatus: BootstrapStatus | null;
  session: Session | null;
  csrf: string;
  error: string;
  bootstrap(payload: BootstrapPayload): Promise<BootstrapSession>;
  login(username: string, password: string, totpCode?: string): Promise<void>;
  recover(username: string, recoveryCode: string, newPassword: string): Promise<void>;
  logout(): Promise<void>;
  changePassword(currentPassword: string, newPassword: string): Promise<void>;
  revokeSession(sessionId: string): Promise<void>;
  disableMfa(currentPassword: string, code: string): Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
