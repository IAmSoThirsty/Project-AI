# Project-AI Documentation

Welcome to **Project-AI** — an extensible, secure AGI operations stack for building, running, and monitoring advanced intelligent agents with robust safety and identity management.

## 📁 Documentation Structure

Project-AI documentation is organized into **six main categories** to help you find what you need quickly:

| Folder | Audience | Content |
|--------|----------|---------|
| **[executive/](executive/)** | Executives, investors, auditors | Business overviews, whitepapers, compliance guides, user guides |
| **[architecture/](architecture/)** | Architects, senior engineers | System architecture, technical diagrams, design documents |
| **[governance/](governance/)** | Ethics teams, legal, compliance | Ethics frameworks, AGI rights, policy documents, licensing |
| **[security_compliance/](security_compliance/)** | Security engineers, auditors | Security policies, incident playbooks, compliance guides, RBAC |
| **[developer/](developer/)** | Developers, DevOps, SRE | Installation, APIs, CLI docs, deployment guides, quickstarts |
| **[internal/](internal/)** | Engineering team | Implementation notes, session records, legacy docs, WIP |

📖 **[Documentation Structure Guide](DOCUMENTATION_STRUCTURE_GUIDE.md)** - Complete guide for adding new documentation

---

## What is Project-AI?

_Project-AI is an open, extensible platform for operating, securing, and researching AGI systems. It integrates state-of-the-art scheduling (Temporal), monitoring, modular cognitive processing (MCP tools), Spiking Neural Network co-processors, and end-to-end security/identity for both production and experimental deployments._

## What Can You Do With Project-AI?

- **Run a full AGI stack** with guarded workflows, SNN co-processors, MCP tools, and built-in monitoring.
- **Deploy and monitor** production or research systems with layered safety, identity, and observability.
- **Prototype and extend** new AGI modules, security policies, or research ideas in a modular, testable sandbox.

---

## Start Here (Choose Your Role)

| If you're an...     | Start Here                                                                  |
|---------------------|-----------------------------------------------------------------------------|
| **Operator**        | [Quickstart for Operators](../QUICKSTART_NONDEV.md) _(Coming soon)_         |
| **Infrastructure Engineer** | [Production Deployment Checklist](../DEPLOYMENT_GUIDE.md) _(Coming soon)_<br>[Prometheus Monitoring](../PROMETHEUS_INTEGRATION.md) _(Coming soon)_<br>[Kubernetes Guide](../KUBERNETES_MONITORING_GUIDE.md) _(Coming soon)_|
| **AI Safety/Research** | [AI Safety Overview](../AI_SECURITY_FRAMEWORK.md) _(Coming soon)_<br>[Robustness Metrics](../ROBUSTNESS_METRICS.md) _(Coming soon)_<br>[Read the AGI Charter](../AGI_CHARTER.md) _(Coming soon)_|
| **Contributor**     | [Code Contribution Guide](../CONTRIBUTING.md) _(Coming soon)_<br>[Docs Contribution Guide](CONTRIBUTING_DOCS.md) _(Coming soon)_ |

---

## Overview & Roadmap

- [Project Vision & Roadmap](overview/ROADMAP.md) _(Coming soon)_

---

## Example Deployments (Happy Paths)

**(All coming soon — see `examples/` directory)**

- Minimal deployment example
- Advanced secured deployment
- Research sandbox
- [First Workflow: Temporal → Monitoring](../TEMPORAL_SETUP.md) + [Integration Steps](../NEW_TEMPORAL_INTEGRATION_SUMMARY.md) _(Coming soon)_

---

## Document Taxonomy / Index

**Identity Docs:**  

- AGI Identity Spec _(Coming soon)_

**Security Docs:**  

- Security Frameworks, Red Team Results, Robustness Metrics _(Coming soon)_

**Infrastructure Docs:**  

- Deployment, Monitoring, Cloud/Offline Sync _(Coming soon)_

---

## Reference (`actionlint` Docs)

- [Checks](checks.md): Full list of all checks done by actionlint with example inputs, outputs, and playground links.
- [Installation](install.md): Installation instructions for prebuilt binaries, Homebrew, Docker image, building from source, or CI script.
- [Usage](usage.md): How to use `actionlint` locally, in CI, or with Docker and integrations (reviewdog, Problem Matchers, pre-commit, etc.).
- [Configuration](config.md): How to configure `actionlint`. (Currently only self-hosted runner labels.)
- [Go API](api.md): Using actionlint as a Go library.
- [References](reference.md): Further resources.

---

**See the [project root README](../README.md) for repo-wide notes and status.**

---

_This README provides narrative structure and discoverable entry points. As more guides/docs are added, update the links above to remove "_(Coming soon)_" and set desired onboarding flow._