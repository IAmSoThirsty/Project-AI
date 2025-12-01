# Project Roadmap

This living document highlights the next areas of focus for Project-AI and captures the outstanding items that were surfaced during the latest review cycle.

## Immediate Priorities

| Area | Notes |
| --- | --- |
| Plugin Expansion | Build a marketplace for third-party plugins, document hook contracts, and add CI tests that ensure each plugin respects the Four Laws before enabling it. |
| Continuous Learning | Surface historical `LearningReport` entries in the persona UI, enable filtering by topic, and add CLI access to pull reports for auditing. |
| Web Stack | Flesh out the Flask backend with authenticated endpoints and replace the static frontend placeholder with the planned React/Vite UI. Add Playwright or Cypress tests for automated coverage. |

## Secondary Goals

1. **Desktop Packaging**: Automate the PyInstaller build, sign binaries, and publish installers via GitHub Releases or an internal share.
1. **Security & Compliance**: Schedule regular Bandit scans, dependency audits (Trivy/Dependabot), and document the incident response/training flow.
1. **Mobile Friendliness**: Create a lightweight React Native/Web version that reuses the core APIs and ensures the `LearningRequest` system remains synchronous across clients.
1. **Observability**: Add structured logging + telemetry for chat flow, plugin usage, and learning updates. Integrate those logs with the memory system for debugging.

## Long-term Initiatives

- **AI Governance Dashboard**: Provide a multi-tab dashboard showing override history, learning approvals, and Four Laws compliance stats.
- **Automated Retraining Pipeline**: Turn the manual retraining steps into scheduled jobs that fetch new labeled data, validate it, and prompt for approval before pushing updated ML detectors.
- **Community Contributions**: Publish a contributor guide, code of conduct, and example plugin so new collaborators can ramp up quickly.
