<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / architecture.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / architecture.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Cerberus Guard Bot Architecture

## Overview

Cerberus Guard Bot is a multi-agent security system designed to protect AI/AGI systems from various attack vectors including jailbreaks, prompt injections, and bot attacks.

## Core Components

### 1. Hub Coordinator (`cerberus.hub.HubCoordinator`)

The central coordination hub manages all guardian agents. It:
- Initializes and manages the guardian pool
- Distributes analysis tasks to all active guardians
- Aggregates results and makes final decisions
- Handles the exponential growth mechanism when threats are detected

### 2. Guardian Agents (`cerberus.guardians`)

Three types of guardians with different analysis styles:

#### StrictGuardian
- Rule-based analysis with explicit pattern matching
- Uses blocklists and keyword detection
- Conservative approach (prefers false positives over false negatives)

#### HeuristicGuardian
- Statistical scoring across multiple factors
- Weighted analysis of command structure, capitalization, and instruction phrases
- Configurable thresholds for threat levels

#### PatternGuardian
- Contextual pattern analysis
- Focuses on semantic relationships and manipulation patterns
- Extracts context windows around trigger phrases

## Security Model

### Exponential Guardian Growth

When a high or critical threat is detected:
1. The hub spawns 3 new random guardians
2. If total guardians exceed 27, total shutdown is initiated
3. In shutdown mode, all requests are blocked

This provides:
- Rapid response to persistent attacks
- Eventual automatic shutdown for sustained attacks
- Diverse defensive coverage through random guardian types

## Flow Diagram

```
Content Input
      │
      ▼
┌──────────────────┐
│  Hub Coordinator │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌──────────┐ ┌─────────┐
│Strict  │ │Heuristic │ │Pattern  │
│Guardian│ │Guardian  │ │Guardian │
└────┬───┘ └────┬─────┘ └────┬────┘
     │          │            │
     └─────────┬┴────────────┘
               ▼
        ┌──────────────┐
        │  Aggregate   │
        │   Results    │
        └──────┬───────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
Threat Detected?    No Threat
    │                     │
    ▼                     ▼
Spawn 3 More         Allow
Guardians            Content
    │
    ▼
Max Reached?
    │
    ▼
SHUTDOWN
```
