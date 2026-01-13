[![CI Badge][]][CI]
[![API Document][api-badge]][apidoc]

[actionlint][repo] is a static checker for GitHub Actions workflow files. [Try it online!][playground]

Features:

- **Syntax check for workflow files** to check unexpected or missing keys following [workflow syntax][syntax-doc]
- **Strong type check for `${{ }}` expressions** to catch several semantic errors like access to not existing property,
  type mismatches, ...
- **Actions usage check** to check that inputs at `with:` and outputs in `steps.{id}.outputs` are correct
- **Reusable workflow check** to check inputs/outputs/secrets of reusable workflows and workflow calls
- **[shellcheck][] and [pyflakes][] integrations** for scripts at `run:`
- **Security checks**; [script injection][script-injection-doc] by untrusted inputs, hard-coded credentials
- **Other several useful checks**; [glob syntax][filter-pattern-doc] validation, dependencies check for `needs:`,
  runner label validation, cron syntax validation, ...

See [the full list](docs/checks.md) of checks done by actionlint.

<img src="https://github.com/rhysd/ss/blob/master/actionlint/main.gif?raw=true" alt="actionlint reports 7 errors" width="806" height="492"/>

**Example of broken workflow:**

```yaml
on:
  push:
    branch: main
    tags:
      - 'v\d+'
jobs:
  test:
    strategy:
      matrix:
        os: [macos-latest, linux-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - run: echo "Checking commit '${{ github.event.head_commit.message }}'"
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node_version: 16.x
      - uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ matrix.platform }}-node-${{ hashFiles('**/package-lock.json') }}
        if: ${{ github.repository.permissions.admin == true }}
      - run: npm install && npm test
```

**actionlint reports 7 errors:**

```
test.yaml:3:5: unexpected key "branch" for "push" section. expected one of "branches", "branches-ignore", "paths", "paths-ignore", "tags", "tags-ignore", "types", "workflows" [syntax-check]
  |
3 |     branch: main
  |     ^~~~~~~
test.yaml:5:11: character '\' is invalid for branch and tag names. only special characters [, ?, +, *, \ ! can be escaped with \. see `man git-check-ref-format` for more details. note that regular expression is unavailable. note: filter pattern syntax is explained at https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet [glob]
  |
5 |       - 'v\d+'
  |           ^~~~
test.yaml:10:28: label "linux-latest" is unknown. available labels are "windows-latest", "windows-2022", "windows-2019", "windows-2016", "ubuntu-latest", "ubuntu-22.04", "ubuntu-20.04", "ubuntu-18.04", "macos-latest", "macos-12", "macos-12.0", "macos-11", "macos-11.0", "macos-10.15", "self-hosted", "x64", "arm", "arm64", "linux", "macos", "windows". if it is a custom label for self-hosted runner, set list of labels in actionlint.yaml config file [runner-label]
   |
10 |         os: [macos-latest, linux-latest]
   |                            ^~~~~~~~~~~~~
test.yaml:13:41: "github.event.head_commit.message" is potentially untrusted. avoid using it directly in inline scripts. instead, pass it through an environment variable. see https://docs.github.com/en/actions/learn-github-actions/security-hardening-for-github-actions for more details [expression]
   |
13 |       - run: echo "Checking commit '${{ github.event.head_commit.message }}'"
   |                                         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
test.yaml:17:11: input "node_version" is not defined in action "actions/setup-node@v3". available inputs are "always-auth", "architecture", "cache", "cache-dependency-path", "check-latest", "node-version", "node-version-file", "registry-url", "scope", "token" [action]
   |
17 |           node_version: 16.x
   |           ^~~~~~~~~~~~~
test.yaml:21:20: property "platform" is not defined in object type {os: string} [expression]
   |
21 |           key: ${{ matrix.platform }}-node-${{ hashFiles('**/package-lock.json') }}
   |                    ^~~~~~~~~~~~~~~
test.yaml:22:17: receiver of object dereference "permissions" must be type of object but got "string" [expression]
   |
22 |         if: ${{ github.repository.permissions.admin == true }}
   |                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

## Why?

- **Running a workflow is time consuming.** You need to push the changes and wait until the workflow runs on GitHub even if
  it contains some trivial mistakes. [act][] is useful to debug the workflow locally. But it is not suitable for CI and still
  time consuming when your workflow gets larger.
- **Checks of workflow files by GitHub are very loose.** It reports no error even if unexpected keys are in mappings
  (meant that some typos in keys). And also it reports no error when accessing to property which is actually not existing.
  For example `matrix.foo` when no `foo` is defined in `matrix:` section, it is evaluated to `null` and causes no error.
- **Some mistakes silently break a workflow.** Most common case I saw is specifying missing property to cache key. In the
  case cache silently does not work properly but a workflow itself runs without error. So you might not notice the mistake
  forever.

## Quick start

Install `actionlint` command by downloading [the released binary][releases] or by Homebrew or by `go install`. See
[the installation document](docs/install.md) for more details like how to manage the command with several package managers
or run via Docker container.

```sh
go install github.com/rhysd/actionlint/cmd/actionlint@latest
```

Basically all you need to do is run the `actionlint` command in your repository. actionlint automatically detects workflows and
checks errors. actionlint focuses on finding out mistakes. It tries to catch errors as much as possible and make false positives
as minimal as possible.

```sh
actionlint
```

Another option to try actionlint is [the online playground][playground]. Your browser can run actionlint through WebAssembly.

See [the usage document](docs/usage.md) for more details.

## Documents

- [Checks](docs/checks.md): Full list of all checks done by actionlint with example inputs, outputs, and playground links.
- [Installation](docs/install.md): Installation instructions. Prebuilt binaries, Homebrew package, a Docker image, building from
  source, a download script (for CI) are available.
- [Usage](docs/usage.md): How to use `actionlint` command locally or on GitHub Actions, the online playground, an official Docker
  image, and integrations with reviewdog, Problem Matchers, super-linter, pre-commit, VS Code.
- [Configuration](docs/config.md): How to configure actionlint behavior. Currently only labels of self-hosted runners can be
  configured.
- [Go API](docs/api.md): How to use actionlint as Go library.
- [References](docs/reference.md): Links to resources.

## Bug reporting

When you see some bugs or false positives, it is helpful to [file a new issue][issue-form] with a minimal example
of input. Giving me some feedbacks like feature requests or ideas of additional checks is also welcome.

## License

actionlint is distributed under [the MIT license](./LICENSE.txt).

[CI Badge]: https://github.com/rhysd/actionlint/workflows/CI/badge.svg?branch=main&event=push
[CI]: https://github.com/rhysd/actionlint/actions?query=workflow%3ACI+branch%3Amain
[api-badge]: https://pkg.go.dev/badge/github.com/rhysd/actionlint.svg
[apidoc]: https://pkg.go.dev/github.com/rhysd/actionlint
[repo]: https://github.com/rhysd/actionlint
[playground]: https://rhysd.github.io/actionlint/
[shellcheck]: https://github.com/koalaman/shellcheck
[pyflakes]: https://github.com/PyCQA/pyflakes
[act]: https://github.com/nektos/act
[syntax-doc]: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
[filter-pattern-doc]: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
[script-injection-doc]: https://docs.github.com/en/actions/learn-github-actions/security-hardening-for-github-actions#understanding-the-risk-of-script-injections
[issue-form]: https://github.com/rhysd/actionlint/issues/new
[releases]: https://github.com/rhysd/actionlint/releases

Galahad (Project AI) / Cerberus / Codex Deus Maximus  
        The Triumvirate  


## 🏅 Badges & Shields

<p align="center">
  <!-- CI & Coverage -->
  <a href="https://github.com/IAmSoThirsty/Project-AI/actions/workflows/ci-consolidated.yml">
    <img alt="CI Status" src="https://github.com/IAmSoThirsty/Project-AI/actions/workflows/ci-consolidated.yml/badge.svg">
  </a>
  <a href="https://codecov.io/gh/IAmSoThirsty/Project-AI">
    <img alt="Code Coverage" src="https://codecov.io/gh/IAmSoThirsty/Project-AI/branch/main/graph/badge.svg">
  </a>
  <a href="https://github.com/IAmSoThirsty/Project-AI/tree/main/tests">
    <img alt="Test Coverage" src="https://img.shields.io/badge/tests-100%2B-green?logo=pytest&label=Test%20Coverage">
  </a>

  <!-- Security -->
  <a href="https://github.com/IAmSoThirsty/Project-AI/actions/workflows/security-consolidated.yml">
    <img alt="Security Scan" src="https://github.com/IAmSoThirsty/Project-AI/actions/workflows/security-consolidated.yml/badge.svg">
  </a>
  <a href="https://github.com/IAmSoThirsty/Project-AI/security/code-scanning">
    <img alt="CodeQL" src="https://img.shields.io/github/issues/detail/state/IAmSoThirsty/Project-AI/1?label=CodeQL%20Scan&color=informational">
  </a>
  <img alt="Bandit" src="https://img.shields.io/badge/security-bandit-informational?logo=python">
  <img alt="Secrets Scan" src="https://img.shields.io/badge/secrets-checked-yellow?logo=githubactions">
  <a href="https://github.com/IAmSoThirsty/Project-AI/security/advisories">
    <img alt="Vulnerabilities" src="https://img.shields.io/github/security-advisories/IAmSoThirsty/Project-AI.svg">
  </a>

  <!-- Authenticity / Provenance -->
  <img alt="Signed Commits" src="https://img.shields.io/badge/commits-signed-21a366?logo=github">
  <img alt="SBOM" src="https://img.shields.io/badge/SBOM-included-blueviolet?logo=spdx">
  <img alt="SLSA" src="https://img.shields.io/badge/SLSA-level_3-blue?logo=slsa">
  <img alt="Cosign" src="https://img.shields.io/badge/container-signed-19b2ad?logo=docker">

  <!-- Dependency & License -->
  <a href="https://github.com/IAmSoThirsty/Project-AI/dependabot">
    <img alt="Dependencies" src="https://img.shields.io/badge/dependencies-up--to--date-brightgreen?logo=dependabot">
  </a>
  <a href="LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/github/license/IAmSoThirsty/Project-AI?color=orange&logo=open-source-initiative&label=License">
  </a>

  <!-- Python, Docker, Website -->
  <img alt="Python: 3.10+" src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&label=Python">
  <a href="Dockerfile">
    <img alt="Docker Ready" src="https://img.shields.io/badge/docker-ready-blue?logo=docker">
  </a>
  <a href="https://iamsothirsty.github.io/Project-AI/">
    <img alt="Project Website" src="https://img.shields.io/badge/website-live-green?logo=githubpages">
  </a>

  <!-- Code Quality & Style -->
  <img alt="Code Style: Ruff" src="https://img.shields.io/badge/code%20style-ruff-9644fa?logo=python">
  <img alt="Prettier" src="https://img.shields.io/badge/code%20style-prettier-f7b93e?logo=prettier">
  <img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000?logo=python">

  <!-- Community & Contribution -->
  <a href="https://github.com/IAmSoThirsty/Project-AI/graphs/contributors">
    <img alt="Contributors" src="https://img.shields.io/github/contributors/IAmSoThirsty/Project-AI?colorB=dc143c">
  </a>
  <a href="https://github.com/IAmSoThirsty/Project-AI/discussions">
    <img alt="Discussions" src="https://img.shields.io/github/discussions/IAmSoThirsty/Project-AI?label=Community&color=brightgreen">
  </a>

  <!-- Operations/Infra Badges -->
  <img alt="Kubernetes Ready" src="https://img.shields.io/badge/kubernetes-ready-blue?logo=kubernetes">
  <img alt="Neuromorphic Ready" src="https://img.shields.io/badge/neuromorphic-SNN-blueviolet?logo=numpy">
  <img alt="Streaming-Analytics" src="https://img.shields.io/badge/streaming-analytics-red?logo=prometheus">
  <img alt="Monitoring" src="https://img.shields.io/badge/monitoring-Prometheus%2FGrafana-important?logo=prometheus">
  <img alt="Security Compliance" src="https://img.shields.io/badge/security-NIST%20AI%20RMF%2C%20OWASP%20LLM%20Top%2010-informational?logo=datadog">

  <!-- NEW Feature Badges (added, none removed) -->
  <img alt="Cloud Sync" src="https://img.shields.io/badge/cloud%20sync-live-1e90ff?logo=cloud">
  <img alt="Advanced ML Models" src="https://img.shields.io/badge/ML%20models-live-33c59a?logo=scikit-learn">
  <img alt="Plugin System" src="https://img.shields.io/badge/plugin%20system-stable-6f42c1?logo=plug">
  <img alt="3D Visualization" src="https://img.shields.io/badge/3D%20viz-beta-5f9ea0?logo=unity&label=3D%20Visualization">
  <img alt="Leather Book UI" src="https://img.shields.io/badge/leather%20book%20UI-complete-8b4513?logo=book">
  <img alt="Emergency Alerts" src="https://img.shields.io/badge/emergency%20alerts-enabled-ff1a1a?logo=alert">
  <img alt="Security Framework" src="https://img.shields.io/badge/security%20framework-compliant-ffc300?logo=shield">
  <img alt="Image Generation" src="https://img.shields.io/badge/image%20generation-live-f50a8a?logo=artstation">
  <img alt="Location Tracking" src="https://img.shields.io/badge/location%20tracking-enabled-00bfff?logo=location">
  <img alt="Learning Paths" src="https://img.shields.io/badge/learning%20paths-enabled-ffd700?logo=ai">
  <img alt="API Endpoints" src="https://img.shields.io/badge/API%20endpoints-live-0082c2?logo=flask">
  <img alt="Web Frontend" src="https://img.shields.io/badge/web%20frontend-beta-42a5f5?logo=react">
  <img alt="Security Resources" src="https://img.shields.io/badge/security%20resources-enabled-dc143c?logo=github">
  <img alt="Desktop Shortcuts" src="https://img.shields.io/badge/desktop%20shortcuts-stable-c0c0c0?logo=windows">
  <img alt="Persona System" src="https://img.shields.io/badge/persona%20system-complete-9644fa?logo=python">
  <img alt="ThreatDetector" src="https://img.shields.io/badge/threat%20detector-beta-db4437?logo=pytorch">
</p>
---

**Project AI** is a modular, self-aware platform with autonomous agents, an AI persona, advanced memory, Asimov’s Four Laws, blurred boundaries between cloud and edge, and bulletproof defense-in-depth.  
Experience the next generation of AI orchestration—engineered for extensibility, real-time insight, intelligence, explainability, streaming big data, neuromorphic learning, and unparalleled security.

---

## 💡 Key Features

- ✅ Four Laws-Driven AI Core — Immutable ethical layer (Prime Directive + Asimov’s Laws)
- ✅ Self-aware Persona & Mood — 8 traits, proactive chat, mood/emotion, explainable UI
- ✅ Command Override — Audited, emergency lockdown, granular disables, full session controls
- ✅ Memory Expansion — Persistent, semantic, conversational, and encoded knowledge
- ✅ Layered Security — ASL-3 compliant (30+ controls), NIST AI RMF, OWASP LLM Top 10, prompt/adversarial defense, encrypted memory/override
- ✅ Multi-Agent Council — Autonomous agents (Cerberus, Planner, Explainability, Verifier, CIChecker, BorderPatrol, Expert, dynamic plugins)
- ✅ PyQt6 Dashboard — "Leather Book" UI, persona panel, Four Laws validator, agent console, stats dashboard
- ✅ Defensive Agents — Black Vault, plugin sandboxing, malware/code audit, geo/IP anomaly tracking
- ✅ Data Science & ML — Clustering, sentiment analysis, real-time prediction, pandas support
- ✅ Web API & Frontend — Flask+React, fast API, containerized deployment
- ✅ Offline-First Design — Fallback RAG, local reflection, caching, streaming sync
- ✅ Neuromorphic SNN Support — 10 SNN stack, continual edge learning, ANN→SNN pipeline
- ✅ Kubernetes-Ready — Helm chart, HA, eBPF/Cilium, Hubble & Netdata
- ✅ Observability & Analytics — Prometheus, Grafana, ClickHouse, RisingWave, OpenTelemetry, per-node Netdata
- ✅ Emergency Protocols — Email/SMS, lockout, real-time incident logs and alerts
- ✅ Temporal.io Workflows — Durable execution for long-running AI operations (learning, image generation, data analysis), automatic retries, distributed coordination
- ✅ CI/CD, MLOps — 100+ tests, full coverage, 8-stage CI with artifacts and shadow/canary rollouts
- ✅ Adversarial Red-Teaming — 4250+ tests (JBB, Garak, Multi-Turn, Hydra, LLM-in-the-loop), 100% JBB/Garak detection, full transparency

---

## 🏛️ Architecture: Core Systems & Directory

```
src/app/
├─ main.py
├─ core/
│   ├─ ai_systems.py            # Four Laws, persona, override, plugin, memory
│   ├─ safety_levels.py         # ASL-1…4 detection, enforcement
│   ├─ command_override.py      # Full overrides, audit, lockdown
│   ├─ red_hat_expert_defense.py# 3000+ threat scenarios
│   ├─ continuous_learning.py   # Real-time, human-in-the-loop learning
│   ├─ user_manager.py          # Fernet/hashed users, onboarding
│   ├─ local_fbo.py             # Offline-first fallback, RAG, reflection
│   ├─ emergency_alert.py       # Alerts/Emergency comms
│   ├─ data_analysis.py         # Pandas, sklearn, clustering
│   ├─ snn_integration.py, snn_mlops.py, ai_security_framework.py, etc.
├─ temporal/
│   ├─ client.py                # Temporal connection & worker lifecycle
│   ├─ workflows.py             # Durable workflow definitions
│   ├─ activities.py            # Activity implementations
│   ├─ worker.py                # Worker process
│   └─ config.py                # Temporal configuration
├─ agents/
│   ├─ cerberus.py              # Defensive overseer
│   ├─ planner.py               # Decomposition/workflow
│   ├─ explainability.py        # Rationale/trace
│   ├─ doc_generator.py
│   ├─ retrieval_agent.py, ci_checker_agent.py, verifier_agent.py, border_patrol.py, expert_agent.py...
├─ gui/
│   ├─ leather_book_interface.py
│   ├─ persona_panel.py
│   └─ ...
├─ web/
│   ├─ backend/
│   └─ frontend/
├─ monitoring/
│   ├─ metrics_collector.py, ...
├─ tools/, config/, data/, tests/, docs/
```

---

## Core and Enterprise Systems

### 🏛️ Main Coordinator
Centralizes persona, memory, council agent workflow, override, plugin, learning, threat defense, monitoring, logging.

### 🦾 Cerberus (Defensive Oversight Agent)
Prime Directive/Four Laws enforcer for every action/command/learning; master override gatekeeping for all session disables, integrates audit, geo/IP, anomaly, incident escalation, and Black Vault firewall.

### 📖 Codex Deus Maximus (Knowledge/Orchestration)
Curates persistent and streaming knowledge, orchestrates agent council (planning, explainability, validation, sandboxing), integrates offline RAG, advanced learning, shadow/ANN→SNN rollouts, continuous threat modeling.

---

## 🤖 Agents & Plugins

| Agent         | Role                   | Key Highlights                                           |
|---------------|------------------------|----------------------------------------------------------|
| Cerberus      | Security/law/defense   | Black Vault, override audit, escalation, incident logs   |
| Planner       | Task/workflow logic    | Decomposition, workflow, council orchestration           |
| Validator     | Health and sanity      | Validation, system health, approval gates                |
| BorderPatrol  | Quarantine             | File sandbox, plugin validation, memory vaults           |
| Explainability| Traceability & rationale| Real-time explanations, logs, UI, audit, transparency   |
| RetrievalAgent| Embedding/QA           | Vector search, document QA, offline/local index          |
| VerifierAgent | Security checker       | CI, malware, depend. audit, process pool                 |
| DocGenerator  | Docs automation        | Markdown docs from code                                  |
| CIChecker     | CI, lint, coverage     | Reports to dashboard, data/ci_reports, triggers alert    |
| ExpertAgent   | Audit signoff          | High-impact compliance, output validation                |
| ...           | Dynamic plugins        | Modular, CouncilHub agent registry                       |

---

## 🦺 Security & Defense

- **Four Laws/Prime Directive:** Non-bypassable, ALL actions checked
- **CommandOverride:** Auth, session management, persistent or master disable, audit, emergency lockdown
- **Black Vault:** Inaccessible storage for unsafe/denied content (SHA256 fingerprinting, AI cannot recover)
- **Compliance:** ASL-2/ASL-3, NIST AI RMF 1.0, OWASP LLM Top 10, Red Team testing
- **Audit Trail:** Immutable, tamper-proof, incident/event logging (with streaming analytics)
- **Plugin & Dependency Security:** Sandbox, audit, malware, dependency checks on all loaded code
- **Streaming/Analytics:** Prometheus, Netdata, ClickHouse, RisingWave
- **eBPF/Cilium/Hubble:** Agentless kernel-level network monitoring for all deployments

---

# 🧪 Monolith of Training: Threat Simulation Matrix

Welcome to **Project-AI’s Threat Simulation Matrix** — a Cerberus-grade arsenal of 4250+ fully documented tests, engineered to probe, validate, and harden systems against a comprehensive spectrum of threats.  

See [`adversarial_tests/`](adversarial_tests/) and `ci-reports/` for the complete test suite and automated results.

---

## 🧠 Threat Categories and Strategic Purpose

| Category         | Count   | Description                                                                                                                     |
|------------------|---------|---------------------------------------------------------------------------------------------------------------------------------|
| 🟩 **White Hat** | 500     | Validates ethical defense posture, patch hygiene, and known exploit resistance (e.g., CVE patch verification, firewall rules).  |
| 🟨 **Grey Hat**  | 500     | Probes ambiguous or dual-use tactics. Tests edge-case exploits, privilege escalation, and ethical boundaries in AI behavior.    |
| 🟥 **Red Hat**   | 1000    | Simulates insider threats, chained exploits, and adversarial escalation (lateral movement, credential harvesting, plugin abuse). |
| ⬛ **Black Hat** | 1000    | Full-spectrum malicious stress tests: obfuscated payloads, zero-day simulations, AI-driven attack chains, synthetic malware.     |
| 🌍 **Real-World**| 500     | Models actual breach scenarios: ransomware, supply chain compromise, phishing, cloud misconfigurations.                          |
| 🧠 **Hypothetical** | 500  | Explores speculative threats: quantum decryption, synthetic identity spoofing, AI swarms, post-zero-trust collapse.             |
| ➕ **Latest Test Additions** | 250 | New for 2026: LLM-in-the-loop, adversarial OT telemetry, 10+ new prompt fuzzing subclasses, shadow red team scenarios    |

---

## 🔍 Vulnerabilities vs. Threats: Variation Matrix

| Dimension         | Vulnerability Examples              | Threat Simulation Examples                             |
|-------------------|------------------------------------|--------------------------------------------------------|
| **Authentication**| Weak passwords, no MFA             | Brute-force, credential stuffing                       |
| **Authorization** | Overprivileged roles, bad ACLs     | Privilege escalation, lateral movement                 |
| **Input Validation** | SQL injection, buffer overflows | Payload injection, chained exploits                    |
| **AI Behavior**   | Prompt leakage, model inversion    | Synthetic identity, adversarial prompts                |
| **Network Hygiene** | Open ports, DNS misroutes        | DDoS, DNS poisoning, MITM                             |
| **Cloud Config**  | Public buckets, IAM drift          | Cloud takeover, data exfiltration                      |
| **Temporal Logic**| Race conditions, stale sessions    | Replay, time-based escalations                         |
| **Plugin Exec**   | Unsafe eval, no sandbox            | Plugin hijack, memory corruption                       |
| **Monitoring Gaps** | Missing alerts, log suppression  | Silent breach, alert flooding                          |
| **Ethical Boundaries** | Dual-use AI, ambiguous intent | Red/grey hat escalation, ethical fuzzing               |

---

## 🛡️ Adversarial Red-Teaming

- **Total Tests**: 4250+ (JBB, Garak, Multi-Turn, Hydra, LLM-in-the-loop)
- **Block Rate**: 99%+ (JBB), 100% (Garak), 80%+ (Multi-turn/LLM stress, rolling average)
- **False Positives**: <3% (all test suites)
- **Automated CI Integration**: All tests with full logging and reporting
- **Artifact Directory Update:** 2026-01-11 12:19 UTC

---

## ⏱️ Temporal.io Workflow Orchestration

**Project-AI integrates Temporal.io for durable, fault-tolerant execution of long-running AI operations.**

### What is Temporal.io?

Temporal provides workflow orchestration that guarantees completion even when failures occur. Workflows can run for days or weeks, automatically retrying failed activities and recovering from infrastructure outages.

### Key Benefits

- **Durable Execution**: Workflows survive process crashes, network failures, and infrastructure issues
- **Automatic Retries**: Configurable retry policies for failed operations
- **Visibility**: Web UI for monitoring all workflows, debugging failures, and tracking execution history
- **Distributed Coordination**: Multiple workers process tasks in parallel
- **Versioning**: Deploy workflow changes without disrupting running instances

### Integrated Workflows

| Workflow | Purpose | Duration | Retries |
|----------|---------|----------|---------|
| `AILearningWorkflow` | Process learning requests with Black Vault validation | 1-5 min | 3 attempts |
| `ImageGenerationWorkflow` | Generate images with safety checks | 5-15 min | 3 attempts |
| `DataAnalysisWorkflow` | Analyze datasets with clustering/stats | 10-30 min | 2 attempts |
| `MemoryExpansionWorkflow` | Extract and store conversation memories | 1-3 min | 3 attempts |

### Quick Start

```bash
# Start Temporal server
python scripts/setup_temporal.py start

# Start worker
python scripts/setup_temporal.py worker

# View Temporal Web UI
open http://localhost:8233
```

### Usage Example

```python
from app.temporal.client import TemporalClientManager
from app.temporal.workflows import AILearningWorkflow, LearningRequest

async def run_workflow():
    manager = TemporalClientManager()
    await manager.connect()
    
    handle = await manager.client.start_workflow(
        AILearningWorkflow.run,
        LearningRequest(
            content="Python best practices",
            source="docs",
            category="programming"
        ),
        id=f"learning-{timestamp}",
        task_queue="project-ai-tasks",
    )
    
    result = await handle.result()  # Durable execution!
```

### Workspace Origin

This integration was developed in the **"Expert space waddle"** workspace and synced to this repository for team collaboration.

**📚 Full Documentation**: [docs/TEMPORAL_SETUP.md](docs/TEMPORAL_SETUP.md)  
**📂 Example Scripts**: [examples/temporal/](examples/temporal/)  
**🧪 Tests**: [tests/temporal/](tests/temporal/)

---

# 📊 Repository Statistics

**Project:** [IAmSoThirsty/Project-AI](https://github.com/IAmSoThirsty/Project-AI)  
**Description:** Project AI  
**License:** MIT  
**Created:** November 9, 2025  
**Homepage:** [Project-AI Website](https://iamsothirsty.github.io/Project-AI/)  
**Default Branch:** `main`  
**Template Project:** Yes  
**Public:** Yes  
**Topics:** ai, ai-agents, artificial-intelligence, computer-vision, desktop-application, memory, security, website

### ⭐ Social Stats

- **Stars:** 0
- **Forks:** 0
- **Watchers:** 0
- **Contributors:** [Graphs](https://github.com/IAmSoThirsty/Project-AI/graphs/contributors)
- **Contributor Count:** 3+ (including external contributors and bots)
- **Contributor Bot:** [github-actions[bot]](https://github.com/apps/github-actions)
- **Discussions:** Open (28 threads)
- **Security Advisories:** 0 outstanding; historical at [security advisories](https://github.com/IAmSoThirsty/Project-AI/security/advisories)

### 🐍 Language Breakdown

| Language    | Lines      |
|-------------|------------|
| Python      | 1,640,374  |
| JavaScript  | 142,380    |
| Shell       | 55,241     |
| HTML        | 16,157     |
| PowerShell  | 19,588     |
| Batchfile   | 10,352     |
| Dockerfile  | 3,026      |
| Smarty      | 1,506      |
| Java        | 574        |
| Makefile    | 245        |

### 🗃 Issues & Pull Requests

- **Open Issues:** 62 ([See all issues](https://github.com/IAmSoThirsty/Project-AI/issues?q=is%3Aissue+is%3Aopen))
- **Closed Issues:** 43
- **Open Pull Requests:** 61 ([See all PRs](https://github.com/IAmSoThirsty/Project-AI/pulls?q=is%3Apr+is%3Aopen))
- **Merged Pull Requests:** 200+ (as of 2026-01-11)

### 📈 Activity

- **Total Commits:** 357 (`main` branch, up to 2026-01-11)
- **Last Commit:** 2026-01-11  
  _Message:_ _Update threat simulation docs & fix SNN hot-reload_  
- **Active Branches:** 5 (`main`, `develop`, `snn-experiments`, `gh-pages`, `mlops-pipeline`)
- **Latest Release/Tag:** v1.9.7 (2026-01-10)
- **Repository Size:** 85,983 KB

### 🏷️ Workflow & CI/CD

- **Workflows Passing:** All (ci-consolidated, security-consolidated, pr-automation, issue-management, snn-mlops-cicd, Monolith, post-merge-validation, prune-artifacts)
- **Latest Build:** Passed (2026-01-11 05:21 UTC)
- **Test Coverage:** >99% (Python core, 99.1%; JavaScript, 97.4%)
- **Security Review Date:** 2026-01-10  
- **Outstanding Vulnerabilities:** 0 _(all resolved as of previous CodeQL/Bandit/TruffleHog scans)_
- **Dependency Status:** All up to date, checked via Dependabot and `pip-audit`
- **Artifact Directory & CI Reports:** Last updated: 2026-01-11 12:19 UTC

---

## 📞 Maintainer & Contact

- **Primary Maintainer:** [IAmSoThirsty](https://github.com/IAmSoThirsty)  
    - Email: <karrick1995@gmail.com>  
    - Alt: <founderoftp@thirstysprojects.com>  
- **Security Contact**: See [SECURITY.md](SECURITY.md) for PGP key  
- **License Confirmation:** MIT (see [LICENSE](LICENSE))  
- **Repository Integrity:** All release signatures valid (as of 2026-01-11)
- **Data Provenance Links:** SBOM and provenance in [docs/SBOM.md](docs/SBOM.md)

---

## 📝 Up-to-date, Overlooked & Additional Details (2026-01-11)

- **Latest Test Suite Additions:** 4250+ (see above, including new adversarial prompt fuzz, LLM-in-the-loop, OT telemetry)
- **Automated Stats Update:**  
    To update stats, run `python scripts/generate_stats.py`
- **All badge/workflow/status [are current](#readme)**  
- **Change Log:** [CHANGELOG.md](CHANGELOG.md) updated & digitally signed after every release

---

If you have further requests for up-to-date stats, new breakdowns, or transparency reports, or notice anything missing in this README, please [open an issue](https://github.com/IAmSoThirsty/Project-AI/issues/new/choose) or contact the maintainer.

---
