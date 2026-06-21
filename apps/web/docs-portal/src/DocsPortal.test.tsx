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
};

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test("shows live public state and filters DOI records", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => ({
    ok: true,
    json: async () => payloads[String(input)],
  })));
  render(<DocsPortal />);
  expect(await screen.findByText("2 records")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Publications" }));
  expect(await screen.findByText("Paper-01")).toBeInTheDocument();
  await userEvent.type(screen.getByPlaceholderText("Search title, DOI, or domain"), "governance");
  expect(screen.queryByText("Paper-01")).not.toBeInTheDocument();
  expect(screen.getByText("Paper-02")).toBeInTheDocument();
});

test("renders an honest gateway error", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ ok: false, status: 503, json: async () => ({ detail: "offline" }) })));
  render(<DocsPortal />);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("offline"));
});
