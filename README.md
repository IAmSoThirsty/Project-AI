# Project AI

<p align="center">
  <img src="![image1](image1)" alt="Project-AI Hero Image" width="500"/><br>
  <b>Project AI • Codex Deus Maximus • Founder/Architect</b>
</p>

---

### 🏅 Badges & Logos

<p align="center">
  <a href="https://github.com/IAmSoThirsty/Project-AI/actions">
    <img alt="CI Status" src="https://img.shields.io/github/actions/workflow/status/IAmSoThirsty/Project-AI/ci.yml?branch=main&logo=githubactions&label=CI%20Pipeline">
  </a>
  <a href="https://github.com/IAmSoThirsty/Project-AI/tree/main/tests">
    <img alt="Test Coverage" src="https://img.shields.io/badge/tests-100%2B-green?logo=pytest&label=Test%20Coverage">
  </a>
  <a href="LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/github/license/IAmSoThirsty/Project-AI?color=orange&logo=open-source-initiative&label=License">
  </a>
  <img alt="Python: 3.10+" src="https://img.shields.io/badge/python-3.10+-blue?logo=python&label=Python">
  <a href="Dockerfile">
    <img alt="Docker Ready" src="https://img.shields.io/badge/docker-ready-blue?logo=docker">
  </a>
  <a href="https://iamsothirsty.github.io/Project-AI/">
    <img alt="Project Website" src="https://img.shields.io/badge/website-live-green?logo=githubpages">
  </a>
  <a href="https://github.com/IAmSoThirsty/Project-AI/discussions">
    <img alt="Discussions" src="https://img.shields.io/github/discussions/IAmSoThirsty/Project-AI?label=Join%20Community&color=brightgreen">
  </a>
  <a href="SECURITY.md">
    <img alt="Security Policy" src="https://img.shields.io/badge/security-Policy-blueviolet?logo=security">
  </a>
  <img alt="Code Style: Ruff" src="https://img.shields.io/badge/code%20style-ruff-9644fa?logo=python">
  <a href="https://github.com/IAmSoThirsty/Project-AI/graphs/contributors">
    <img alt="Contributors" src="https://img.shields.io/github/contributors/IAmSoThirsty/Project-AI?colorB=dc143c">
  </a>
</p>

---

**Project AI** is a modular, self-aware AI platform with autonomous agent orchestration, AI persona, advanced memory, ethics via Asimov’s Four Laws, and defense-in-depth security.  
Experience the engineered fusion of “Project” — the agent core, Cerberus — the defensive overseer, and “Codex Deus Maximus” — the grand knowledge engine.  
Built for extensibility, robustness, explainability, and uncompromising defensive posture.

---

## 💡 Key Features

- ✅ Four Laws-Driven AI Core (Prime Directive + Asimov’s Laws)
- ✅ Self-aware Persona & Mood (8 traits, proactive chat, mood, stats)
- ✅ Command Override (Full audit, emergency lockdown, privileged controls)
- ✅ Memory Expansion (Long-term, conversational, encoded knowledge)
- ✅ Security Layers (30+ managed controls, ASL-3 compliance, encryption)
- ✅ Agent/Plugin Framework (Cerberus, Verifier, Explainability, CI, dynamic plugins)
- ✅ PyQt6 Dashboard UI ("Leather Book", Four Laws, persona editor, agent console)
- ✅ Defensive Agents (Black Vault, plugin sandboxing, malware/code audit)
- ✅ Data Science Tools (CSV/XLSX/JSON analysis, clustering, viz)
- ✅ Web API & Frontend (Flask+React, Docker-ready)
- ✅ Offline/Resilience (Local RAG, reflection, sync, mobile-friendly)
- ✅ Emergency Protocols (Email/SMS alerts, lockout, incident logs)
- ✅ CI/CD, Test, & Code Quality (100+ tests, Github Actions, full coverage, ruff)

---

## 🏛️ Architecture Overview

```
src/app/
├── main.py
├── core/
│   ├── ai_systems.py
│   ├── safety_levels.py
│   ├── command_override.py
│   ├── red_hat_expert_defense.py
│   ├── data_analysis.py
│   ├── security_enforcer.py
│   ├── continuous_learning.py
│   ├── user_manager.py
│   ├── local_fbo.py
│   ├── emergency_alert.py
│   └── ... more ...
├── agents/
│   ├── cerberus.py
│   ├── border_patrol.py
│   ├── planner.py
│   ├── doc_generator.py
│   ├── dependency_auditor.py
│   ├── retrieval_agent.py
│   ├── sandbox_worker.py
│   ├── ci_checker_agent.py
│   └── ... extra ...
├── gui/
│   ├── leather_book_interface.py
│   ├── persona_panel.py
│   └── ... dialogs, event handlers, image ui ...
├── web/  # Flask backend, React frontend
├── data/, config/, tools/, examples/
```

---

## 🏛️ Core Systems

- **Main Coordinator:** Integrates memory, persona, agent, UI, security
- **FourLaws Module:** Immutable ethical decision at every privileged/agent operation
- **MemoryExpansion:** Multi-category, persistent, smart knowledge
- **LearningRequests:** Human-in-the-loop, Black Vault for blocked
- **AIPersona:** 8 traits with mood, proactive chat, real-time UI, explainability
- **PluginManager:** Sandboxed, hooks, isolation, error recovery
- **CommandOverride:** Password-protected, full audit, master override, lockdown

---

## 🦾 Cerberus (Defensive Overseer Agent)

- Blocks unsafe actions, enforces Prime Directive and Four Laws
- Monitors and approves/disapproves command overrides
- Guards Black Vault (denied content is inaccessible)
- Integrates threat detection, plugin scan, geo/IP history
- Maintains tamper-proof audit log, triggers emergency protocols

---

## 📖 Codex Deus Maximus (Knowledge Engine)

- Curates memory, learning, orchestrates agent council
- Ranks and approves/denies learning via agent/human review
- Exports knowledge/decision audit for compliant integrations
- Explainability engine: rationales in UI/log/response

---

## 🤖 Agents

| Agent         | Role                     | Features                         |
|---------------|--------------------------|-----------------------------------|
| Cerberus      | Defensive/Priority check | Four Laws, override/audit, vault  |
| Planner       | Task/workflow builder    | Decomposition, scheduling         |
| Validator     | Input/output sanity      | Health/pre-action validation      |
| Explainability| Reasoning & transparency | UI/log rationales, audit trail    |
| DocGenerator  | Markdown docs            | Code structure/usage pipelines    |
| RetrievalAgent| Embedding/QA             | Vector search, document QA        |
| VerifierAgent | Sandbox checker          | Plugin, malware, dep, CI audits   |
| BorderPatrol  | Quarantine/audit         | Vault escalation, file quarantine |
| ExpertAgent   | Integration signoff      | Review & compliance, expert role  |
| CIChecker     | CI/test/lint/audit       | GH Actions, ci_reports            |
| ...           | Extendable plugins       | Extensible, modular architecture  |

---

## 🦺 Defensive & Security Layer Highlights

- Four Laws enforced everywhere, prime check
- CommandOverride system: hashed auth, lockdown, audit, session
- Black Vault: unreachable storage for denied/unsafe content
- ASL-2/3 compliance enforced, threat monitor, quarterly report
- Emergency triggers: email/SMS, fail-safe reset, geo/IP logs
- Full audit trail, tamper-evident, incident tracking
- Plugins sandboxed + audited prior to execution (CI, dependency auditor)
- Comprehensive security tooling: pip-audit, bandit, detect-secrets, truffleHog
- Test coverage: 100+ full-feature tests, CI generates artifacts
- Documentation: SECURITY.md, CONTRIBUTING.md, full docs

---

## 📚 Memory, Persona & Learning

- JSON-based, modular knowledge with categories, smart retrieval
- Persona: 8 traits, mood state, proactive suggestions, dashboard, explainability
- Learning: Human-in-loop for all new requests, Black Vault for denial
- Learning fingerprinting: SHA256 for denied, status for audit

---

## 🖥️ User Interface & CLI

- PyQt6 "Leather Book": persona panel, Four Laws tab, trait sliders, stats
- Action validator: Four Laws tested before execution (UI field)
- Async management: thread pooling, performance alerts, input validation
- Error handling: central logs, incident dashboard
- Migration utilities for users/settings/plugins (helpers/scripts)
- Flask backend/React frontend for web deployment
- Fully local, cloud, and Docker-ready options

---

## ML & Data Science Highlights

- Scikit-learn, PyTorch, pandas, MLPClassifier, GradientBoosting, clustering
- Optional ThreatDetector using neural nets with retraining CLI/UI
- Plugin system hooks: message/validation/action/conversation/errors
- Pattern recognition and autonomous learning expansion

---

## Install & Run

**Requirements:**  
- Python 3.10+  
- Node.js (web UI optional)  
- Docker/docker-compose (optional)

### Quickstart

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
pip install -r requirements.txt
npm install && npm run build
python -m src.app.main             # launch PyQt UI
docker compose up                  # full stack
pytest -v                          # tests
```

**Config:**  
- All state: data/, config/, .env (never commit secrets; use `.env.example`!)  
- Plugins: src/app/core/plugins/

**Designer:**  
- PyQt6 & PySide6 supported (Designer scripts available for rapid UI prototyping)

---

## Testing, CI & Linting

- Pytest, hypothesis, code coverage (ci_reports, junit XML)
- ruff, black, isort, markdownlint, prettier, ESLint
- Full test artifacts for local and CI inspection

---

## Security & Advanced Features

- Full-featured command override/audit/lockdown
- Extensive scenario/fuzz/adversarial test suite (8,850+ security tests)
- Bandit/static/dynamic/secret/coverage scan
- Plugin quarantine, Vault enforcement
- AI Persona threat detection: explainability, emotion scoring, retraining
- Guided retraining, CLI helper scripts, plugin and system audit

---

## Offline-First Architecture

- Local knowledge base, RAG, Reflection & Learning
- Query/analysis, video motion/optical flow, offline memory/response cache
- Smart sync for online/offline cross-device transitions

---

## Best Practices

- Always save state after edits
- Use official plugin directory for add-ons
- Rotate keys, audit override logs often
- Use CI, pre-commit, and security scan tools before merge
- Prioritize human-in-the-loop and Black Vault workflows for all learning and persistent data

---

## Contributor Notes

- Please see CONTRIBUTING.md, CODE_OF_CONDUCT.md, open Issues

---

## License
MIT License. See LICENSE.

---

> For docs, onboarding, and architecture, see:
> - COMMAND_MEMORY_FEATURES.md
> - LEARNING_REQUEST_LOG.md
> - AI_PERSONA_FOUR_LAWS.md
> - QUICK_START.md
> - INTEGRATION_SUMMARY.md
> - Docs: https://iamsothirsty.github.io/Project-AI/

---

<sub>
<sup>
*This README is reorganized for clarity, completeness, and developer onboarding. It merges every detail from prior versions, and adds new badge/demo support for full technical, security, and feature reference.*
</sup>
</sub>
