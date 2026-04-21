# Project-AI Documentation

Welcome to **Project-AI** — an extensible, secure AGI operations stack for building, running, and monitoring advanced intelligent agents with robust safety and identity management.

## 🔗 NEW: Complete Architecture Traceability

**[[AGENT-080-CONCEPT-CODE-MAP|Architecture Concept-to-Code Traceability Matrix]]** - 421 bidirectional wiki links connecting architecture concepts to implementing code. Use this to navigate from design to implementation and back.

**Quick Links:**
- [[AGENT-080-SUMMARY|Mission Summary]] - Overview of traceability matrix
- [[AGENT-080-COMPLETION-REPORT|Full Report]] - Complete details and statistics
- [[BIDIRECTIONAL_LINKS|Wiki Linking Guide]] - Standards for bidirectional documentation

---

## 📁 Documentation Structure

Project-AI documentation is organized into **six main categories** to help you find what you need quickly:

| Folder | Audience | Content |
|--------|----------|---------|
| **[[executive/|executive/]]** | Executives, investors, auditors | Business overviews, whitepapers, compliance guides, user guides |
| **[[architecture/|architecture/]]** | Architects, senior engineers | System architecture, technical diagrams, design documents |
| **[[governance/|governance/]]** | Ethics teams, legal, compliance | Ethics frameworks, AGI rights, policy documents, licensing |
| **[[security_compliance/|security_compliance/]]** | Security engineers, auditors | Security policies, incident playbooks, compliance guides, RBAC |
| **[[developer/|developer/]]** | Developers, DevOps, SRE | Installation, APIs, CLI docs, deployment guides, quickstarts |
| **[[internal/|internal/]]** | Engineering team | Implementation notes, session records, legacy docs, WIP |

📖 **[[DOCUMENTATION_STRUCTURE_GUIDE.md|Documentation Structure Guide]]** - Complete guide for adding new documentation

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
| **Operator**        | [[developer/OPERATOR_QUICKSTART.md|Operator Quickstart]] - Guardian mindset, operational safety, incident response         |
| **Infrastructure Engineer** | [[developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md|Infrastructure Production Guide]] - Deployment checklist, Prometheus monitoring, Kubernetes guide<br>[[developer/EXAMPLE_DEPLOYMENTS.md|Example Deployments]] - Minimal, secured, and research sandbox configurations|
| **AI Safety/Research** | [[developer/AI_SAFETY_OVERVIEW.md|AI Safety Overview]] - Corrigibility, interpretability, robustness metrics<br>[[governance/AGI_CHARTER.md|AGI Charter]] - Rights, dignity, and Four Laws framework|
| **Contributor**     | [[developer/CONTRIBUTING.md|Code & Docs Contribution Guide]] - Standards, governance, philosophical framework<br>[[DOCUMENTATION_STRUCTURE_GUIDE.md|Documentation Structure Guide]] - Where to place new docs |

---

## Overview & Roadmap

- [[developer/ROADMAP.md|Project Vision & Roadmap]] - AGI for collective flourishing, organizational theory, philosophical framework
- [[developer/IDENTITY_SECURITY_INFRASTRUCTURE.md|Identity, Security & Infrastructure]] - Self-sovereign identity, security principles, infrastructure philosophy

---

## Example Deployments (Production-Ready Patterns)

*See [[developer/EXAMPLE_DEPLOYMENTS.md|Example Deployments Guide]] for complete configurations*

- **Minimal Deployment:** Simple, single-server setup for development and PoC
- **Secured Advanced Deployment:** Production-grade with defense-in-depth, HA, monitoring
- **Research Sandbox:** Isolated environment for testing risky capabilities
- [[developer/TEMPORAL_SETUP.md|Temporal Workflow Setup]] + [[developer/INTEGRATION_GUIDE.md|Integration Guide]]

---

## Document Taxonomy / Index

**Identity Docs:**  

- [[governance/AGI_IDENTITY_SPECIFICATION.md|AGI Identity Specification]]
- [[governance/IDENTITY_SYSTEM_FULL_SPEC.md|Identity System Full Spec]]
- [[developer/IDENTITY_SECURITY_INFRASTRUCTURE.md|Identity, Security & Infrastructure Framework]]

**Security Docs:**  

- [[security_compliance/AI_SECURITY_FRAMEWORK.md|AI Security Framework]]
- [[security_compliance/SECURITY.md|Security Policy]]
- [[security_compliance/INCIDENT_PLAYBOOK.md|Incident Playbook]]
- [[developer/AI_SAFETY_OVERVIEW.md|AI Safety Overview]] - Robustness metrics, red-teaming, corrigibility

**Infrastructure Docs:**  

- [[developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md|Infrastructure Production Guide]] - Deployment, Prometheus, Kubernetes
- [[developer/EXAMPLE_DEPLOYMENTS.md|Example Deployments]] - Minimal, secured, research sandbox
- [[developer/DEPLOYMENT_GUIDE.md|Deployment Guide]]
- [[developer/KUBERNETES_MONITORING_GUIDE.md|Kubernetes Monitoring Guide]]

**Governance & Ethics:**

- [[governance/AGI_CHARTER.md|AGI Charter]] - Rights, dignity, Four Laws
- [[developer/ROADMAP.md|Project Vision & Roadmap]] - Mission, organizational theory
- [[developer/CONTRIBUTING.md|Contributing Guide]] - Code/docs contribution philosophy

---

## Reference (`actionlint` Docs)

- [Checks](checks.md): Full list of all checks done by actionlint with example inputs, outputs, and playground links.
- [Installation](install.md): Installation instructions for prebuilt binaries, Homebrew, Docker image, building from source, or CI script.
- [Usage](usage.md): How to use `actionlint` locally, in CI, or with Docker and integrations (reviewdog, Problem Matchers, pre-commit, etc.).
- [Configuration](config.md): How to configure `actionlint`. (Currently only self-hosted runner labels.)
- [Go API](api.md): Using actionlint as a Go library.
- [References](reference.md): Further resources.

---

**See the [[../README.md|project root README]] for repo-wide notes and status.**

---

_This README provides narrative structure and discoverable entry points. As more guides/docs are added, update the links above to remove "_(Coming soon)_" and set desired onboarding flow._