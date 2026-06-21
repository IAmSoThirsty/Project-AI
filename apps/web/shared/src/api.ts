export type Health = { status: "live"; version: "0.0.0.dev0" };
export type ReplayStatus = {
  status: "not_run" | "pass" | "fail";
  invariants_passed: number;
  invariants_total: number;
  updated_at: string;
};
export type DoiRecord = { title: string; doi: string; domain: string; url: string };
export type AuditRecord = Record<string, string | number | boolean | null>;
export type AuditResponse = { chain_valid: true; count: number; records: AuditRecord[] };

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "/api";

async function requestJson<T>(path: string, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!response.ok) {
    const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(detail?.detail ?? `Request failed with HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export const gateway = {
  health: () => requestJson<Health>("/health/live"),
  replay: () => requestJson<ReplayStatus>("/replay/status"),
  dois: async () => (await requestJson<{ dois: DoiRecord[] }>("/dois")).dois,
  audit: (token: string, limit = 100) =>
    requestJson<AuditResponse>(`/audit?limit=${encodeURIComponent(limit)}`, token),
};
