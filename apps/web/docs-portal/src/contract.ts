import baselineRaw from "../../../../docs/api/openapi-baseline.json?raw";

/**
 * The frozen OpenAPI baseline, imported at build time from the exact file
 * enforced by `packages/api/tests/test_api.py::test_openapi_baseline_matches_runtime`.
 * The docs page and the test suite therefore share one source of truth;
 * nothing here is hand-maintained.
 */

type OpenApiOperation = {
  summary?: string;
  security?: Record<string, unknown>[];
};

type OpenApiDocument = {
  openapi: string;
  info: { title: string; version: string };
  paths: Record<string, Record<string, OpenApiOperation>>;
  components?: { securitySchemes?: Record<string, { description?: string }> };
};

export type ContractOperation = {
  method: string;
  path: string;
  summary: string;
  auth: string[];
};

export type ContractGroup = {
  prefix: string;
  operations: ContractOperation[];
};

const METHOD_ORDER = ["get", "post", "put", "patch", "delete"];

export const contract = JSON.parse(baselineRaw) as OpenApiDocument;

export const securitySchemes: { name: string; description: string }[] = Object.entries(
  contract.components?.securitySchemes ?? {},
).map(([name, scheme]) => ({ name, description: scheme.description ?? "" }));

function groupPrefix(path: string): string {
  const segments = path.split("/").filter(Boolean);
  if (segments[0] === "api" && segments[1] === "v1" && segments.length > 2) {
    return `/api/v1/${segments[2]}`;
  }
  return `/${segments[0] ?? ""}`;
}

export const contractGroups: ContractGroup[] = (() => {
  const groups = new Map<string, ContractOperation[]>();
  for (const [path, operations] of Object.entries(contract.paths)) {
    for (const [method, operation] of Object.entries(operations)) {
      if (!METHOD_ORDER.includes(method)) continue;
      const auth = [
        ...new Set(
          (operation.security ?? []).flatMap((requirement) => Object.keys(requirement)),
        ),
      ].sort();
      const entry: ContractOperation = {
        method: method.toUpperCase(),
        path,
        summary: operation.summary ?? "",
        auth,
      };
      const prefix = groupPrefix(path);
      const existing = groups.get(prefix);
      if (existing) existing.push(entry);
      else groups.set(prefix, [entry]);
    }
  }
  return [...groups.entries()]
    .map(([prefix, operations]) => ({
      prefix,
      operations: operations.sort(
        (left, right) =>
          left.path.localeCompare(right.path) ||
          METHOD_ORDER.indexOf(left.method.toLowerCase()) -
            METHOD_ORDER.indexOf(right.method.toLowerCase()),
      ),
    }))
    .sort((left, right) => left.prefix.localeCompare(right.prefix));
})();

export const operationCount = contractGroups.reduce(
  (total, group) => total + group.operations.length,
  0,
);

export const pathCount = Object.keys(contract.paths).length;
