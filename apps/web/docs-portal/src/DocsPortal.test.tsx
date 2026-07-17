import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";

import { DocsPortal } from "./DocsPortal";

const payloads: Record<string, unknown> = {
  "/api/health/live": { status: "live", version: "0.0.0.dev0" },
  "/api/replay/status": { status: "pass", invariants_passed: 5, invariants_total: 5, updated_at: "now" },
  "/api/dois": { dois: [
    { title: "Paper-01", doi: "10.1/security", domain: "security", url: "https://doi.org/10.1/security" },
    { title: "Paper-02", doi: "10.1/governance", domain: "governance", url: "https://doi.org/10.1/governance" },
  ] },
  "/api/api/v1/modules": { modules: [
    {
      id: "swr",
      label: "Sovereign War Room",
      category: "simulation",
      maturity: "implemented",
      interface_status: "available",
      authority: "Execution through the canonical gate only",
      summary: "Scenario preparation",
    },
  ] },
};

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function stubGateway() {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => ({
    ok: true,
    json: async () => payloads[String(input)],
  })));
}

test("shows live public state and filters DOI records", async () => {
  stubGateway();
  render(<DocsPortal />);
  expect(await screen.findByText("2 records")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Publications" }));
  expect(await screen.findByText("Paper-01")).toBeInTheDocument();
  await userEvent.type(screen.getByPlaceholderText("Search title, DOI, or domain"), "governance");
  expect(screen.queryByText("Paper-01")).not.toBeInTheDocument();
  expect(screen.getByText("Paper-02")).toBeInTheDocument();
});

test("architecture screen renders the gateway's own module catalog", async () => {
  stubGateway();
  render(<DocsPortal />);
  await userEvent.click(screen.getByRole("button", { name: "Architecture" }));
  expect(await screen.findByText("Sovereign War Room")).toBeInTheDocument();
  expect(screen.getByText("implemented / available")).toBeInTheDocument();
  expect(screen.getByText("Execution through the canonical gate only")).toBeInTheDocument();
});

test("contract screen renders the frozen baseline with per-operation auth", async () => {
  stubGateway();
  render(<DocsPortal />);
  await userEvent.click(screen.getByRole("button", { name: "API contract" }));
  expect(await screen.findByText("GET /health/live")).toBeInTheDocument();
  expect(screen.getByText("GET /audit")).toBeInTheDocument();
  expect(screen.getAllByText("machineBearer | sessionCookie").length).toBeGreaterThanOrEqual(2);
  expect(screen.getByText("POST /chimera/verdict")).toBeInTheDocument();
  expect(screen.getByText("GET /api/v1/modules/atlas/sludge")).toBeInTheDocument();
  expect(screen.getAllByText("machineBearer").length).toBeGreaterThanOrEqual(1);
  expect(screen.getAllByText("sessionCookie").length).toBeGreaterThanOrEqual(1);
  expect(screen.getByText(/test_openapi_baseline_matches_runtime/)).toBeInTheDocument();
});

test("decisions screen renders ADR-001 from the repository markdown", async () => {
  stubGateway();
  render(<DocsPortal />);
  await userEvent.click(screen.getByRole("button", { name: "Decisions" }));
  expect(
    await screen.findByText("ADR-001: Human interface delivery and authority boundaries"),
  ).toBeInTheDocument();
  expect(screen.getByText("Consequences")).toBeInTheDocument();
});

test("renders an honest gateway error", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ ok: false, status: 503, json: async () => ({ detail: "offline" }) })));
  render(<DocsPortal />);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("offline"));
});
