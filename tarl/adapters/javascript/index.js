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
