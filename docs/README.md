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
| **Operator**        | [Operator Quickstart](developer/OPERATOR_QUICKSTART.md) - Guardian mindset, operational safety, incident response         |
| **Infrastructure Engineer** | [Infrastructure Production Guide](developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md) - Deployment checklist, Prometheus monitoring, Kubernetes guide<br>[Example Deployments](developer/EXAMPLE_DEPLOYMENTS.md) - Minimal, secured, and research sandbox configurations|
| **AI Safety/Research** | [AI Safety Overview](developer/AI_SAFETY_OVERVIEW.md) - Corrigibility, interpretability, robustness metrics<br>[AGI Charter](governance/AGI_CHARTER.md) - Rights, dignity, and Four Laws framework|
| **Contributor**     | [Code & Docs Contribution Guide](developer/CONTRIBUTING.md) - Standards, governance, philosophical framework<br>[Documentation Structure Guide](DOCUMENTATION_STRUCTURE_GUIDE.md) - Where to place new docs |

---

## Overview & Roadmap

- [Project Vision & Roadmap](developer/ROADMAP.md) - AGI for collective flourishing, organizational theory, philosophical framework
- [Identity, Security & Infrastructure](developer/IDENTITY_SECURITY_INFRASTRUCTURE.md) - Self-sovereign identity, security principles, infrastructure philosophy

---

## Example Deployments (Production-Ready Patterns)

*See [Example Deployments Guide](developer/EXAMPLE_DEPLOYMENTS.md) for complete configurations*

- **Minimal Deployment:** Simple, single-server setup for development and PoC
- **Secured Advanced Deployment:** Production-grade with defense-in-depth, HA, monitoring
- **Research Sandbox:** Isolated environment for testing risky capabilities
- [Temporal Workflow Setup](developer/TEMPORAL_SETUP.md) + [Integration Guide](developer/INTEGRATION_GUIDE.md)

---

## Document Taxonomy / Index

**Identity Docs:**  

- [AGI Identity Specification](governance/AGI_IDENTITY_SPECIFICATION.md)
- [Identity System Full Spec](governance/IDENTITY_SYSTEM_FULL_SPEC.md)
- [Identity, Security & Infrastructure Framework](developer/IDENTITY_SECURITY_INFRASTRUCTURE.md)

**Security Docs:**  

- [AI Security Framework](security_compliance/AI_SECURITY_FRAMEWORK.md)
- [Security Policy](security_compliance/SECURITY.md)
- [Incident Playbook](security_compliance/INCIDENT_PLAYBOOK.md)
- [AI Safety Overview](developer/AI_SAFETY_OVERVIEW.md) - Robustness metrics, red-teaming, corrigibility

**Infrastructure Docs:**  

- [Infrastructure Production Guide](developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md) - Deployment, Prometheus, Kubernetes
- [Example Deployments](developer/EXAMPLE_DEPLOYMENTS.md) - Minimal, secured, research sandbox
- [Deployment Guide](developer/DEPLOYMENT_GUIDE.md)
- [Kubernetes Monitoring Guide](developer/KUBERNETES_MONITORING_GUIDE.md)

**Governance & Ethics:**

- [AGI Charter](governance/AGI_CHARTER.md) - Rights, dignity, Four Laws
- [Project Vision & Roadmap](developer/ROADMAP.md) - Mission, organizational theory
- [Contributing Guide](developer/CONTRIBUTING.md) - Code/docs contribution philosophy

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