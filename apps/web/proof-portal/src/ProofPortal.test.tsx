import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";

import { ProofPortal } from "./ProofPortal";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const dashboardPayload = {
  status: "ready",
  version: "0.0.3",
  maturity: "development",
  authority_boundary: "This dashboard reports evidence; it grants no authority.",
  surfaces: [
    { id: "gateway", label: "Gateway", status: "healthy", metric: "live", detail: "Public liveness only" },
    { id: "replay", label: "Canonical replay", status: "healthy", metric: "5/5", detail: "Invariants passed" },
    { id: "audit_chain", label: "Audit chain", status: "healthy", metric: "3 entries", detail: "Chain verified" },
    { id: "evidence", label: "Evidence", status: "healthy", metric: "21", detail: "DOI records" },
  ],
  doi_records: 21,
  work_items: [],
};

const instancePayload = {
  display_name: "PROJECT-AI-LOCAL",
  deployment: "local_sovereign",
  cloud_login: false,
  browser_machine_identity: false,
  browser_execution_capability: false,
  human_access_path: ["identity", "authentication", "server_session", "workspace"],
  governed_execution_path: [
    "server_service_identity",
    "governance_policy",
    "scoped_capability",
    "execution_gate",
  ],
};

const modulesPayload = {
  modules: [
    {
      id: "swr",
      label: "Sovereign War Room",
      category: "simulation",
      maturity: "implemented",
      interface_status: "available",
      authority: "Execution through the canonical gate only",
      summary: "Scenario preparation",
    },
  ],
};

function stubGateway() {
  const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    const payload = url.includes("/api/v1/dashboard")
      ? dashboardPayload
      : url.includes("/api/v1/instance")
        ? instancePayload
        : url.includes("/api/v1/modules")
          ? modulesPayload
          : url.includes("/audit")
            ? { chain_valid: true, count: 3, filtered_count: 1, offset: 0, limit: 100, records: [{ event: "chimera.canary_hit", canary_sha256: "abc", timestamp: "now", hash: "hash" }] }
            : { status: "live", version: "0.0.3" };
    return { ok: true, json: async () => payload, capturedHeaders: init?.headers };
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

test("status screen renders live dashboard surfaces and the gateway's own authority text", async () => {
  stubGateway();
  render(<ProofPortal />);
  expect(await screen.findByText("Audit chain")).toBeInTheDocument();
  expect(screen.getByText("This dashboard reports evidence; it grants no authority.")).toBeInTheDocument();
  expect(screen.getAllByText("3 entries").length).toBeGreaterThanOrEqual(1);
  expect(screen.getByText("Published research records")).toBeInTheDocument();
});

test("boundaries screen renders instance negative capabilities, paths, and module matrix", async () => {
  stubGateway();
  render(<ProofPortal />);
  await userEvent.click(screen.getByRole("button", { name: "Authority boundaries" }));
  expect(await screen.findByText("cloud_login: false")).toBeInTheDocument();
  expect(screen.getByText("browser_execution_capability: false")).toBeInTheDocument();
  expect(screen.getByText("identity -> authentication -> server_session -> workspace")).toBeInTheDocument();
  expect(screen.getByText("Sovereign War Room")).toBeInTheDocument();
  expect(screen.getByText("implemented / available")).toBeInTheDocument();
  expect(screen.getByText("Execution through the canonical gate only")).toBeInTheDocument();
});

test("audit viewer sends token, event filter, and offset, then clears the token", async () => {
  const fetchMock = stubGateway();
  render(<ProofPortal />);
  await userEvent.click(screen.getByRole("button", { name: "Audit evidence" }));
  await userEvent.type(screen.getByLabelText("API token"), "operator-token");
  await userEvent.selectOptions(screen.getByLabelText("Event filter"), "chimera.canary_hit");
  await userEvent.click(screen.getByRole("button", { name: "Load evidence" }));
  expect(await screen.findByText("chimera.canary_hit")).toBeInTheDocument();
  expect(screen.getByText("1 matching of 3 verified entries")).toBeInTheDocument();
  expect(screen.getByLabelText("API token")).toHaveValue("");
  const [auditUrl, auditInit] = fetchMock.mock.calls.at(-1) ?? [];
  expect(auditUrl).toBe("/api/audit?limit=100&event=chimera.canary_hit");
  expect(auditInit?.credentials).toBe("same-origin");
  expect((auditInit?.headers as Headers).get("Authorization")).toBe("Bearer operator-token");
});

test("requires a token before requesting protected evidence", async () => {
  stubGateway();
  render(<ProofPortal />);
  await userEvent.click(screen.getByRole("button", { name: "Audit evidence" }));
  await userEvent.click(screen.getByRole("button", { name: "Load evidence" }));
  expect(screen.getByRole("alert")).toHaveTextContent("Enter an API token");
});
