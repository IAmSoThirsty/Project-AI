//                                           [2026-03-03 13:45]
//                                          Productivity: Active
export function createTARL({ intent, scope, authority, constraints = [] }) {
  if (!intent || !scope || !authority) {
    throw new Error("Invalid TARL");
  }
  return Object.freeze({
    version: "2.0",
    intent,
    scope,
    authority,
    constraints
  });
}
