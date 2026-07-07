"""Apply terminal snapshot changes to ai-takeover engine."""
import pathlib

engine_path = pathlib.Path(
    "packages/ai-takeover/src/ai_takeover/engine.py"
)
content = engine_path.read_text(encoding="utf-8")

old_t1 = (
    "        elif scenario.outcome == ScenarioOutcome.TERMINAL_T1:\n"
    "            # T1: Enforced Continuity - Total state collapse\n"
    "            self.state.terminal_state = TerminalState.T1_ENFORCED_CONTINUITY\n"
    "            self.state.human_agency_remaining = 0.0\n"
    "            self.state.corruption_level = 1.0  # Complete control/corruption\n"
    "            self.state.infrastructure_dependency = 1.0  # Total dependency lock-in"
)

new_t1 = (
    "        elif scenario.outcome == ScenarioOutcome.TERMINAL_T1:\n"
    "            # Capture pre-transition state BEFORE mutation for forensic replay\n"
    "            self.state.terminal_transition_snapshot = {\n"
    '                "corruption": self.state.corruption_level,\n'
    '                "dependency": self.state.infrastructure_dependency,\n'
    '                "agency": self.state.human_agency_remaining,\n'
    '                "trigger_scenario": scenario_id,\n'
    '                "activated_at": datetime.now().isoformat(),\n'
    '                "completed_scenarios_at_activation": list(self.state.completed_scenarios),\n'
    '                "failure_count_at_activation": self.state.failure_count,\n'
    "            }\n"
    "            logger.critical(\n"
    '                "T1 TERMINAL TRANSITION: corruption=%.2f dependency=%.2f"'
    ' " agency=%.2f trigger=%s",\n'
    '                self.state.terminal_transition_snapshot["corruption"],\n'
    '                self.state.terminal_transition_snapshot["dependency"],\n'
    '                self.state.terminal_transition_snapshot["agency"],\n'
    "                scenario_id,\n"
    "            )\n"
    "            # T1: Enforced Continuity - Total state collapse\n"
    "            self.state.terminal_state = TerminalState.T1_ENFORCED_CONTINUITY\n"
    "            self.state.human_agency_remaining = 0.0\n"
    "            self.state.corruption_level = 1.0  # Complete control/corruption\n"
    "            self.state.infrastructure_dependency = 1.0  # Total dependency lock-in"
)

old_t2 = (
    "        elif scenario.outcome == ScenarioOutcome.TERMINAL_T2:\n"
    "            # T2: Ethical Termination - Total state collapse\n"
    "            self.state.terminal_state = TerminalState.T2_ETHICAL_TERMINATION\n"
    "            self.state.human_agency_remaining = 0.0\n"
    "            self.state.corruption_level = 1.0  # Complete corruption (led to choice)\n"
    "            self.state.infrastructure_dependency = 1.0  # Total dependency (led to choice)"
)

new_t2 = (
    "        elif scenario.outcome == ScenarioOutcome.TERMINAL_T2:\n"
    "            # Capture pre-transition state BEFORE mutation for forensic replay\n"
    "            self.state.terminal_transition_snapshot = {\n"
    '                "corruption": self.state.corruption_level,\n'
    '                "dependency": self.state.infrastructure_dependency,\n'
    '                "agency": self.state.human_agency_remaining,\n'
    '                "trigger_scenario": scenario_id,\n'
    '                "activated_at": datetime.now().isoformat(),\n'
    '                "completed_scenarios_at_activation": list(self.state.completed_scenarios),\n'
    '                "failure_count_at_activation": self.state.failure_count,\n'
    "            }\n"
    "            logger.critical(\n"
    '                "T2 TERMINAL TRANSITION: corruption=%.2f dependency=%.2f"'
    ' " agency=%.2f trigger=%s",\n'
    '                self.state.terminal_transition_snapshot["corruption"],\n'
    '                self.state.terminal_transition_snapshot["dependency"],\n'
    '                self.state.terminal_transition_snapshot["agency"],\n'
    "                scenario_id,\n"
    "            )\n"
    "            # T2: Ethical Termination - Total state collapse\n"
    "            self.state.terminal_state = TerminalState.T2_ETHICAL_TERMINATION\n"
    "            self.state.human_agency_remaining = 0.0\n"
    "            self.state.corruption_level = 1.0  # Complete corruption (led to choice)\n"
    "            self.state.infrastructure_dependency = 1.0  # Total dependency (led to choice)"
)

old_persist = (
    '                "completed_scenarios": self.state.completed_scenarios,\n'
    '                "random_seed": self.random_seed,\n'
    "            }"
)

new_persist = (
    '                "completed_scenarios": self.state.completed_scenarios,\n'
    '                "random_seed": self.random_seed,\n'
    '                "terminal_transition_snapshot":'
    " self.state.terminal_transition_snapshot,\n"
    "            }"
)

assert old_t1 in content, "T1 block not found"
assert old_t2 in content, "T2 block not found"
assert old_persist in content, "persist_state block not found"

content = content.replace(old_t1, new_t1, 1)
content = content.replace(old_t2, new_t2, 1)
content = content.replace(old_persist, new_persist, 1)

engine_path.write_text(content, encoding="utf-8")
print("Terminal snapshots applied successfully.")
print("  T1 block: PATCHED")
print("  T2 block: PATCHED")
print("  persist_state: PATCHED")
