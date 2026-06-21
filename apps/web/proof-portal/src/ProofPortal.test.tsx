import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";

import { ProofPortal } from "./ProofPortal";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test("shows public replay status and loads authenticated audit evidence", async () => {
  const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    const payload = url.endsWith("/health/live")
      ? { status: "live", version: "0.0.0.dev0" }
      : url.endsWith("/replay/status")
        ? { status: "pass", invariants_passed: 5, invariants_total: 5, updated_at: "now" }
        : { chain_valid: true, count: 1, records: [{ event: "chimera.canary_hit", canary_sha256: "abc", timestamp: "now", hash: "hash" }] };
    return { ok: true, json: async () => payload, capturedHeaders: init?.headers };
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<ProofPortal />);
  expect(await screen.findByText("5 / 5")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Audit evidence" }));
  await userEvent.type(screen.getByLabelText("API token"), "operator-token");
  await userEvent.click(screen.getByRole("button", { name: "Load evidence" }));
  expect(await screen.findByText("chimera.canary_hit")).toBeInTheDocument();
  expect(screen.getByLabelText("API token")).toHaveValue("");
  expect(fetchMock).toHaveBeenLastCalledWith("/api/audit?limit=100", { headers: { Authorization: "Bearer operator-token" } });
});

test("requires a token before requesting protected evidence", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => ({ ok: true, json: async () => String(input).includes("replay") ? { status: "not_run", invariants_passed: 0, invariants_total: 5, updated_at: "" } : { status: "live", version: "0.0.0.dev0" } })));
  render(<ProofPortal />);
  await userEvent.click(screen.getByRole("button", { name: "Audit evidence" }));
  await userEvent.click(screen.getByRole("button", { name: "Load evidence" }));
  expect(screen.getByRole("alert")).toHaveTextContent("Enter an API token");
});
