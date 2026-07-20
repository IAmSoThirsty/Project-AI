# Project-AI Thirstys Waterfall rebuild

This workspace package is a provenance-preserving rebuild of the standalone
product at `T:\\01-Projects\\Thirstys-waterfall`. The standalone repository
remains the independently usable product; this copy is the Project-AI-owned
integration surface.

The copied runtime modules are kept under `src/thirstys_waterfall/` and the
standalone web/configuration/deployment assets are retained under
`legacy-assets/`. Project-AI callers must use `project_ai_waterfall` and submit
consequential operations through the canonical `ExecutionGate`; direct runtime
mutation is not the Project-AI production interface.

V3Q is an additional fail-closed pre-check on the gate in production. The
Waterfall kill switch and Project-AI use the same authority contract; the copied
runtime retains its implementation boundary, while Project-AI requests still
enter through the governed gate.

The copied `thirstys_waterfall` tree is a provenance-preserving rebuild lane,
not a second authority implementation. Its original standalone tests and
examples are retained in this package so behavior can be replayed against the
Project-AI copy. The copied source/tests/examples pass direct Ruff validation;
strict Mypy remains enforced on the typed `project_ai_waterfall` transport and
governed adapter surface. The legacy tree is additionally validated by its
replay suite and compilation.

The copied browser components are compatibility/test surfaces, not an OS-level
sandbox or a bundled search service. `BrowserSandbox` reports current Python
process measurements but does not claim kernel isolation. Encrypted search
returns an explicit `unavailable` status unless the caller injects an encrypted
provider; it never fabricates search results. Neither component is on the
Project-AI production request path.
