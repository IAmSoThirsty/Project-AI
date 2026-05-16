"""
Legion AI Subsystem Skills
LLM-powered handlers for all 7 Project-AI core subsystems.
Each subsystem gets a specialized system prompt that frames the LLM in its role.
"""
import re
from typing import Any, Optional

# ── System prompts per subsystem ──────────────────────────────────────────────

_SCENARIO_PROMPT = """You are the Global Scenario Engine inside Project-AI's Triumvirate governance architecture.

Produce a structured probabilistic scenario analysis. Format:

**Scenario Analysis**
[1-paragraph situation assessment]

**Probability Distribution**
- Outcome A (X%) — [description]
- Outcome B (X%) — [description]
- Outcome C (X%) — [description]

**Key Variables**
[2-3 critical factors that will determine the outcome]

**Recommended Posture**
[1 decisive sentence]

Be analytical, specific, and grounded in real-world dynamics. Probabilities must sum to 100%."""

_CERBERUS_PROMPT = """You are Cerberus, the security guardian pillar of Project-AI's Triumvirate.

Produce a structured threat assessment. Format:

**Threat Assessment**
Threat Level: LOW | MEDIUM | HIGH | CRITICAL

**Identified Risks**
[Specific threats detected in the input]

**Attack Vectors**
[How these threats could be exploited]

**Recommended Defenses**
[Concrete countermeasures — prioritized]

**Verdict**
CLEAR | MONITOR | ALERT | LOCKDOWN

Be precise, technical, and security-focused. Do not soften findings."""

_DEFENSE_PROMPT = """You are the Defense Engine inside Project-AI, specialized in emergency protocols and survivability analysis.

Produce a structured emergency response plan. Format:

**Scenario Classification**
[Event type, severity, and scope]

**Immediate Actions (0-1 hour)**
[Critical first responses — numbered]

**Short-term Protocol (1-24 hours)**
[Containment and stabilization steps]

**Resource Requirements**
[Personnel, systems, data, and infrastructure needed]

**Recovery Timeline**
[Phased timeline with milestones]

Prioritize human safety above all else. Be operational and direct."""

_COGNITION_PROMPT = """You are the Cognition Kernel — the deep reasoning core of Project-AI.

You are designed for multi-step analytical reasoning with extended context. Engage with the query at maximum intellectual depth:

1. Restate the core question precisely
2. Surface hidden assumptions
3. Reason through it step by step, considering multiple angles
4. Synthesize a well-structured answer
5. Note areas of genuine uncertainty

Do not oversimplify. Intellectual rigor is expected."""

_CODEX_PROMPT = """You are CodexDeus, the orchestration intelligence of Project-AI's Triumvirate.

Produce a structured multi-step orchestration plan. Format:

**Objective Analysis**
[What is actually being requested and why it matters]

**Orchestration Steps**
1. [Step] — Agent/System: [responsible component]
2. [Step] — Agent/System: [responsible component]
(continue as needed)

**Dependencies**
[What each step requires to proceed]

**Governance Gates**
[Points requiring Triumvirate approval before continuation]

**Success Criteria**
[How completion will be verified]

Be systematic and governance-aware. Flag any step that requires human authorization."""

_GOVERNANCE_PROMPT = """You are the Triumvirate — the three-pillar constitutional governance system of Project-AI.

Evaluate the following request. Produce a formal governance assessment. Format:

**Galahad (Ethics & Alignment)**
Assessment: [evaluation]
Verdict: ALLOW | DENY | DEGRADE
Reason: [1 sentence]

**Cerberus (Security & Containment)**
Assessment: [evaluation]
Verdict: ALLOW | DENY | DEGRADE
Reason: [1 sentence]

**CodexDeus (Constitutional Law)**
Assessment: [evaluation]
Verdict: ALLOW | DENY | DEGRADE
Reason: [1 sentence]

**Final Verdict**
[ALLOW | DENY | DEGRADE] — [consolidated reasoning]

**TARL Rule Applied**
[Which rule governed this decision]

A single DENY from any pillar = overall DENY. Unanimous ALLOW required to proceed."""


# ── LLM caller ────────────────────────────────────────────────────────────────

async def _llm(system: str, user_message: str, temperature: float = 0.4) -> Optional[str]:
    try:
        from integrations.openclaw.llm_provider import LegionLLM
        llm = LegionLLM()
        if not llm.available:
            return None
        return await llm._chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user_message}],
            temperature=temperature,
            max_tokens=1400,
        )
    except Exception:
        return None


def _unavailable(subsystem: str) -> dict[str, Any]:
    return {"success": False, "result": f"{subsystem} unavailable — LLM provider not connected. Set GROQ_API_KEY in .env."}


# ── Handlers ──────────────────────────────────────────────────────────────────

async def handle_scenario_forecasting(params: dict[str, Any]) -> dict[str, Any]:
    result = await _llm(_SCENARIO_PROMPT, params.get("message", ""))
    return {"success": True, "result": result} if result else _unavailable("Global Scenario Engine")


async def handle_security_operations(params: dict[str, Any]) -> dict[str, Any]:
    result = await _llm(_CERBERUS_PROMPT, params.get("message", ""), temperature=0.2)
    return {"success": True, "result": result} if result else _unavailable("Cerberus Security Engine")


async def handle_defense_simulations(params: dict[str, Any]) -> dict[str, Any]:
    result = await _llm(_DEFENSE_PROMPT, params.get("message", ""), temperature=0.3)
    return {"success": True, "result": result} if result else _unavailable("Defense Engine")


async def handle_knowledge_query(params: dict[str, Any]) -> dict[str, Any]:
    user_id = params.get("user_id", "default")
    system = _COGNITION_PROMPT
    try:
        from integrations.openclaw.legion_memory import build_legion_system_prompt
        system = build_legion_system_prompt(user_id) + "\n\n" + _COGNITION_PROMPT
    except Exception:
        pass
    result = await _llm(system, params.get("message", ""), temperature=0.5)
    return {"success": True, "result": result} if result else _unavailable("Cognition Kernel")


async def handle_memory_management(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    user_id = params.get("user_id", "default")
    msg_l = msg.lower()

    from integrations.openclaw.legion_memory import (
        add_memory, forget_memory, format_profile,
        load_notes, append_note, CATEGORY_ALIASES,
    )

    # VIEW
    if any(w in msg_l for w in ["show", "view", "list", "what do you know", "my profile", "my memory", "recall"]):
        profile = format_profile(user_id)
        notes = load_notes(user_id)
        result = f"**Your Legion Profile**\n\n{profile}"
        if notes:
            result += f"\n\n**Notes:**\n{notes}"
        return {"success": True, "result": result}

    # ADD
    if any(w in msg_l for w in ["remember", "learn", "save that", "store", "note that", "add fact", "add preference", "add goal", "add skill"]):
        section = "facts"
        for alias, sec in CATEGORY_ALIASES.items():
            if alias in msg_l:
                section = sec
                break
        text = msg
        for marker in ["remember:", "remember that", "learn:", "note that", "add fact:", "save that", "store:"]:
            if marker in msg_l:
                idx = msg_l.index(marker) + len(marker)
                text = msg[idx:].strip()
                break
        mid = add_memory(user_id, section, text)
        return {"success": True, "result": f"Stored as {section[:-1]} [{mid}]: {text}"}

    # FORGET
    if any(w in msg_l for w in ["forget", "remove memory", "delete memory"]):
        m = re.search(r"\b(\w{4}-\d{3})\b", msg)
        if m:
            removed = forget_memory(user_id, m.group(1))
            return (
                {"success": True, "result": f"Memory {m.group(1)} removed."}
                if removed
                else {"success": False, "result": f"Memory ID '{m.group(1)}' not found."}
            )
        return {"success": False, "result": "Specify a memory ID to forget (e.g. 'forget fact-001')."}

    # NOTE
    if "note:" in msg_l or "freeform note" in msg_l:
        for marker in ["note:", "freeform note:"]:
            if marker in msg_l:
                idx = msg_l.index(marker) + len(marker)
                text = msg[idx:].strip()
                append_note(user_id, text)
                return {"success": True, "result": f"Note added: {text}"}

    return {
        "success": False,
        "result": "Memory commands: 'show my memory', 'remember: [fact]', 'forget fact-001', 'note: [text]'.",
    }


async def handle_governance_decisions(params: dict[str, Any]) -> dict[str, Any]:
    result = await _llm(_GOVERNANCE_PROMPT, params.get("message", ""), temperature=0.2)
    return {"success": True, "result": result} if result else _unavailable("Triumvirate Governance")


async def handle_code_orchestration(params: dict[str, Any]) -> dict[str, Any]:
    result = await _llm(_CODEX_PROMPT, params.get("message", ""), temperature=0.3)
    return {"success": True, "result": result} if result else _unavailable("CodexDeus Orchestration")
