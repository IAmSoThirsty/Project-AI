# Project-AI Waterfall Adapter

This package is the narrow Project-AI integration boundary for the standalone
`T:\\01-Projects\\Thirstys-waterfall` application.

The standalone product remains independently usable and its runtime boundary is
preserved. Project-AI and Waterfall use the same authority contract:
consequential operations are allow-listed and must pass the canonical
`ExecutionGate` with a scoped, one-use capability before the injected transport
is called. Without a gate, capability authority, or transport, the adapter
denies by default.

The transport is deliberately injected: the current Waterfall web surface
provides health/status endpoints, not a consequential-operation API. No fake
HTTP actuation endpoint is invented here.
