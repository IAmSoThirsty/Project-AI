# Plugin Marketplace Guide

Project-AI ships with a plugin system that accepts third-party extensions as long as they respect the Four Laws and do not tamper with core safety controls. This document explains the metadata contract, QA checks, and publication workflow for every plugin before it can be listed in the marketplace.

## Metadata requirements

Each plugin must include a JSON descriptor located alongside the plugin entry point called `plugin.json` with the following schema:

```json
{
  "name": "UniquePluginName",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Short summary of what the plugin does.",
  "hooks": ["before_action", "message_received"],
  "four_laws_safe": true,
  "safe_for_learning": true
}
```

The marketplace UI filters plugins by `hooks` and the `description` string. `four_laws_safe` must be `true` for approval, while `safe_for_learning` indicates whether the plugin may process raw user prompts.

## QA checklist

1. **Import guard**: Plugins must wrap imports in `try/except` blocks so missing dependencies do not crash the host.
1. **Signal handling**: Every Qt signal or hook subscription must disconnect on shutdown to avoid leaks.
1. **Four Laws validation**: Plugins that make decisions (e.g., intercepting commands) must call `FourLaws.validate_action` before proceeding.
1. **Telemetry**: Plugins should log their actions via `app.core.observability.emit_event` (see Observability guide) so they appear in the audit log.
1. **Test coverage**: Provide at least one pytest file that calls the plugin entry point with a mock context.

## QA guidance

Follow these steps when validating a new marketplace plugin:

1. Reference `src/app/plugins/sample_plugin.py` as a runnable example that validates the Four Laws, emits telemetry, and falls back to a stubbed `emit_event` implementation when `app.core.observability` is unavailable.
1. Ensure the accompanying `plugin.json` describes `name`, `version`, `hooks`, `four_laws_safe`, and `safe_for_learning`, mirroring what `src/app/plugins/plugin.json` provides for the demo plugin.
1. Run `python -m pytest tests/test_plugin_sample.py` (or incorporate the same assertions into your own tests) to prove the plugin initializes safely, blocks disallowed contexts, and keeps its metadata in sync with the descriptor.
1. Double-check that any Qt signals or hooks the plugin registers are disconnected during teardown so they do not leak into the runtime dashboard.

## Marketplace submission flow

1. Fork the repository and add the plugin module under `src/app/plugins/<plugin_name>.py`.
1. Include `plugin.json` with metadata and ensure the module exposes an `initialize(context)` function returning `True/False`.
1. Submit a pull request that adds the plugin descriptor to `docs/developer/PLUGIN_MARKETPLACE.md` in the `Marketplace Catalog` section (see below).
1. The reviewer runs the QA checklist, ensures `FourLaws` validation reports no issues, and confirms the plugin is disabled-by-default.
1. Once merged, the plugin appears in the marketplace UI under the categorized list.

## Marketplace Catalog

| Plugin | Status | Hook targets |
| --- | --- | --- |
| Plugin example (core) | Enabled | message_received, before_action |

Add your plugin entry to the catalog table after it ships so downstream users can discover it easily.
