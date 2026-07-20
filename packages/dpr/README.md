# project-ai-dpr

Deliberation Pipeline with Provenance (DPR) governance pipeline.

Ported from `T:\00-Active\thirsty_governance_framework_0722\governance_core\dpr`.
Phases: verifiable authority (Ed25519, TrustRoot), deny-by-default policy engine,
deliberation engine (Phase 3 counter-propose governance burden), Constitutional
Purpose Reflection (Phase 7). Ed25519 signing + SHA-256 hash-linked audit chain.

See `dpr/__init__.py` for the public surface.

`PurposeTriggerDetector` and `PurposeFailureDetector` are callable Phase 7
analysis surfaces, but the main `DPRPipeline` does not automatically invoke
them or translate `PurposeConstraint` objects into `DeliberationContext` yet.
The package classifier remains **Pre-Alpha**, and DPR is not a deployed
Project-AI service in the v0.0.3 Helm/Compose topology. That integration is a
separate behavior-design task, not production evidence for the current API.
