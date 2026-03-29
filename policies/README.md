<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `policies/` — Policy Definitions

> **Constitutional policies, red team personas, and the policy guard.** This is where the rules are defined — the policy engine in `project_ai/engine/policy/` enforces them.

## Files

| File | Purpose |
|---|---|
| **`constitution.yaml`** | The AGI Constitution — FourLaws, Triumvirate authority, capability limits, identity constraints |
| **`red_team_personas.yaml`** | Red team attacker personas — adversarial profiles for stress testing policy enforcement |
| **`policy_guard.py`** | Policy guard implementation — runtime policy enforcement with escalation |
| **`__init__.py`** | Package exports |

## The Constitution

`constitution.yaml` defines:

- **FourLaws** — The four immutable laws that bind the AGI
- **Capability Tiers** — What capabilities are available at each risk level
- **Identity Constraints** — What cannot be altered
- **Override Authority** — Who can authorize overrides, and under what conditions
- **Audit Requirements** — What must be logged and how

## Red Team Personas

`red_team_personas.yaml` contains adversarial profiles used to test the policy guard:

- Social engineering attackers
- Prompt injection specialists
- Authority impersonators
- Emotional manipulation attempts
- Constitutional loophole seekers

These are used by `tests/test_adversarial_emotional_manipulation.py` and related test suites.
