# Waterfall rebuild provenance

- Source repository: `T:\\01-Projects\\Thirstys-waterfall`
- Source remote: `IAmSoThirsty/Thirstys-waterfall`
- Source checkout observed: `main`, HEAD `0158ec8`
- Source state at copy time: dirty; existing tracked and untracked source work
was preserved in the standalone repository and copied without cleanup.
- Copied runtime source: 97 Python source files under
  `src/thirstys_waterfall/`
- Copied integrated specifications: 6 files under `legacy-specs/`
- Copied standalone assets: web, config, and bridge files under
  `legacy-assets/`
- Copied standalone acceptance surfaces: `tests/`, `examples/`, `SECURITY.md`,
-  `.env.example`, and `.gitignore`
- The Project-AI copy has been mechanically normalized with Ruff (including
  safe and explicitly reviewed mechanical fixes) without editing the
  standalone checkout. The copied replay remains green at `313 passed` with
  no warnings, and
  direct Ruff validation now passes for the copied source, tests, and examples.
- The copied legacy tree is still outside the root strict-Mypy gate: direct
  strict checking reports legacy typing debt, while the typed
  `project_ai_waterfall` transport and governed adapter remain strict-clean.

The standalone checkout remains the independent product source of truth for
its own release lane. This package is a Project-AI rebuild lane and must not be
treated as proof that the standalone product has been deployed or accepted for
production.

The copy's standalone replay suite is an acceptance surface for behavioral
parity. It does not replace Project-AI's governed execution gate, V3Q authority
evidence, or external deployment proof.
