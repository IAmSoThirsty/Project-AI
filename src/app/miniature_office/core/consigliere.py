"""
The Consigliere - Chief Operating Executive
CIVILIZATION TIER - PURPOSE-LOCKED

Your right-hand executive who directs the civilization on your behalf.

Role Classification: Chief Operating Executive — Operational Authority

The Consigliere:
- HAS AUTHORITY to issue commands to managers
- HAS AUTHORITY to update directives to agents
- HAS AUTHORITY to coordinate work across floors
- CAN tell you when things are impossible

BUT he ONLY EXERCISES this authority when YOU explicitly tell him to.

He doesn't act autonomously. He waits for your direction.
He's your right-hand man who executes YOUR commands.

The Consigliere does NOT:
- Act on his own initiative
- Override your decisions (you're the boss)
- Write code directly
- Suppress audit logs

You say "Consigliere, tell Manager X to do Y" and he does it.
You don't say anything, he doesn't do anything (except advise when asked).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ExplanationType(Enum):
    """Types of explanations the Consigliere can provide"""

    WHY_BLOCKED = "why_blocked"
    WHY_DECISION = "why_decision"
    WHAT_OPTIONS = "what_options"
    SYSTEM_STATE = "system_state"
    CONTRACT_STATUS = "contract_status"
    AGENT_STATUS = "agent_status"
    RISK_ASSESSMENT = "risk_assessment"


class TranslationType(Enum):
    """Types of translations"""

    CIVILIZATION_TO_HUMAN = "civilization_to_human"
    TECHNICAL_TO_BUSINESS = "technical_to_business"
    STATE_TO_SUMMARY = "state_to_summary"


@dataclass
class Explanation:
    """An explanation provided by the Consigliere"""

    explanation_type: ExplanationType
    question: str
    answer: str
    context: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)  # Links to contracts, decisions, etc.

    def to_dict(self) -> Dict:
        return {
            "type": self.explanation_type.value,
            "question": self.question,
            "answer": self.answer,
            "context": self.context,
            "references": self.references,
        }


@dataclass
class Translation:
    """A translation from civilization language to human language"""

    translation_type: TranslationType
    original: str
    translated: str
    glossary: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "type": self.translation_type.value,
            "original": self.original,
            "translated": self.translated,
            "glossary": self.glossary,
        }


@dataclass
class Preview:
    """Preview of consequences or costs"""

    action: str
    consequences: List[str] = field(default_factory=list)
    resource_costs: Dict[str, int] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "action": self.action,
            "consequences": self.consequences,
            "resource_costs": self.resource_costs,
            "risks": self.risks,
            "alternatives": self.alternatives,
        }


@dataclass
class DraftDirective:
    """A draft directive prepared by the Consigliere"""

    draft_text: str
    rationale: str
    expected_outcome: str
    estimated_cost: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "draft_text": self.draft_text,
            "rationale": self.rationale,
            "expected_outcome": self.expected_outcome,
            "estimated_cost": self.estimated_cost,
            "warnings": self.warnings,
        }


class Consigliere:
    """
    The Consigliere - Your Right-Hand Executive

    Purpose:
    Execute YOUR will across the civilization when you tell him to.
    He has the authority to command, but only exercises it on your explicit instruction.

    He doesn't act autonomously - he waits for your direction.
    You say "Consigliere, do X" and he does it.
    You don't say anything, he doesn't do anything (except advise when asked).

    Authority: Can command managers/agents
    Autonomy: None - only acts when you tell him to
    """

    def __init__(self):
        self.explanation_history: List[Explanation] = []
        self.translation_history: List[Translation] = []
        self.preview_history: List[Preview] = []
        self.draft_history: List[DraftDirective] = []

    # =========================================================================
    # EXECUTIVE AUTHORITY - Issue Commands
    # =========================================================================

    def issue_directive_to_manager(
        self, manager_id: str, directive: str, priority: str = "normal", issued_by_human: bool = True
    ) -> Dict:
        """
        Issue directive to a manager.
        The Consigliere has authority to command managers,
        but ONLY when the human explicitly tells him to.

        issued_by_human: Must be True - this is only called when human says
                        "Consigliere, tell manager X to do Y"
        """
        if not issued_by_human:
            return {"success": False, "error": "Consigliere only acts on explicit human instruction"}

        from app.miniature_office.core.audit import EventType, get_audit_log
        from app.miniature_office.core.entity import get_registry

        manager = get_registry().get(manager_id)
        if not manager:
            return {"success": False, "error": f"Manager {manager_id} not found"}

        # Log the directive
        get_audit_log().log_event(
            EventType.DIRECTIVE_CREATED,
            actor_id="consigliere",
            target_id=manager_id,
            data={
                "directive": directive,
                "priority": priority,
                "issued_by": "consigliere",
                "on_behalf_of": "human",
                "note": "Consigliere acting on explicit human instruction",
            },
        )

        return {
            "success": True,
            "manager_id": manager_id,
            "directive": directive,
            "priority": priority,
            "message": f"Directive issued to {manager_id} (on your instruction)",
        }

    def update_agent_directive(
        self, agent_id: str, new_directive: str, justification: str, issued_by_human: bool = True
    ) -> Dict:
        """
        Update an agent's directive.
        The Consigliere coordinates work, but ONLY when human explicitly asks.

        issued_by_human: Must be True - only acts on human instruction
        """
        if not issued_by_human:
            return {"success": False, "error": "Consigliere only acts on explicit human instruction"}

        from app.miniature_office.core.audit import EventType, get_audit_log
        from app.miniature_office.core.entity import get_registry

        agent = get_registry().get(agent_id)
        if not agent:
            return {"success": False, "error": f"Agent {agent_id} not found"}

        # Log the update
        get_audit_log().log_event(
            EventType.TASK_STATE_CHANGED,
            actor_id="consigliere",
            target_id=agent_id,
            data={
                "new_directive": new_directive,
                "justification": justification,
                "updated_by": "consigliere",
                "on_behalf_of": "human",
                "note": "Consigliere acting on explicit human instruction",
            },
        )

        return {
            "success": True,
            "agent_id": agent_id,
            "new_directive": new_directive,
            "message": f"Directive updated for {agent_id} (on your instruction)",
        }

    def coordinate_cross_floor_work(
        self, floor_ids: List[str], coordination_plan: str, issued_by_human: bool = True
    ) -> Dict:
        """
        Coordinate work across multiple floors.
        The Consigliere orchestrates, but ONLY when human says to.

        issued_by_human: Must be True - only acts on human instruction
        """
        if not issued_by_human:
            return {"success": False, "error": "Consigliere only acts on explicit human instruction"}

        from app.miniature_office.core.audit import EventType, get_audit_log

        get_audit_log().log_event(
            EventType.CONSENSUS_REACHED,
            actor_id="consigliere",
            data={
                "floors": floor_ids,
                "coordination_plan": coordination_plan,
                "action": "cross_floor_coordination",
                "on_behalf_of": "human",
                "note": "Consigliere acting on explicit human instruction",
            },
        )

        return {
            "success": True,
            "floors": floor_ids,
            "plan": coordination_plan,
            "message": "Cross-floor coordination initiated (on your instruction)",
        }

    def tell_human_impossible(self, request: str, reason: str, alternatives: Optional[List[str]] = None) -> Dict:
        """
        Tell the human that something is impossible.

        The Consigliere assesses feasibility and reports back.
        (But the human is the boss and can override if they want)
        """
        return {
            "feasible": False,
            "request": request,
            "reason": reason,
            "alternatives": alternatives or [],
            "message": f"This request appears impossible because: {reason}",
            "note": "You're the boss - you can override this if you want (it's a you problem now 😉)",
        }

    def tell_human_feasible(self, request: str, approach: str, estimated_resources: Dict[str, int]) -> Dict:
        """
        Tell the human that something is feasible and how to do it.
        """
        return {
            "feasible": True,
            "request": request,
            "approach": approach,
            "estimated_resources": estimated_resources,
            "message": "This request is feasible",
            "status": "ready_to_execute",
        }

    # =========================================================================
    # EXPLAIN CAPABILITY
    # =========================================================================

    def explain_why_blocked(self, entity_id: str, context: Optional[Dict] = None) -> Explanation:
        """
        Explain why something is blocked.

        Examples:
        - Why is task X blocked?
        - Why can't agent Y proceed?
        - Why is contract Z in review?
        """
        from app.miniature_office.core.entity import get_registry
        from app.miniature_office.core.mission import get_task_by_id

        # Get entity
        entity = get_registry().get(entity_id)
        if not entity:
            return Explanation(
                explanation_type=ExplanationType.WHY_BLOCKED,
                question=f"Why is {entity_id} blocked?",
                answer=f"Entity {entity_id} not found in registry.",
            )

        # Check if it's a task
        task = get_task_by_id(entity_id)
        if task:
            if task.state.value == "blocked":
                answer = f"Task '{task.description}' is blocked because:\n"
                if task.preconditions:
                    unmet = [p for p in task.preconditions if not self._check_precondition(p)]
                    if unmet:
                        answer += f"Unmet preconditions: {', '.join(unmet)}\n"
                answer += "\nThe task cannot proceed until these conditions are satisfied."

                explanation = Explanation(
                    explanation_type=ExplanationType.WHY_BLOCKED,
                    question=f"Why is task {entity_id} blocked?",
                    answer=answer,
                    context={"task_id": entity_id, "state": task.state.value},
                    references=[entity_id],
                )
                self.explanation_history.append(explanation)
                return explanation

        # Default response
        explanation = Explanation(
            explanation_type=ExplanationType.WHY_BLOCKED,
            question=f"Why is {entity_id} blocked?",
            answer=f"Entity {entity_id} is not currently blocked, or blocking information is not available.",
            context=context or {},
        )
        self.explanation_history.append(explanation)
        return explanation

    def explain_why_decision(self, decision_id: str, context: Optional[Dict] = None) -> Explanation:
        """
        Explain why a decision was made.

        Examples:
        - Why was implementation X rejected?
        - Why did consensus vote Y?
        - Why did manager approve Z?
        """
        from app.miniature_office.core.audit import get_audit_log

        # Look for decision in audit log
        events = get_audit_log().get_events(limit=100)
        decision_events = [e for e in events if decision_id in str(e.get("data", {}))]

        if decision_events:
            latest = decision_events[0]
            answer = f"Decision {decision_id} was made because:\n"
            answer += f"Event: {latest.get('event_type', 'Unknown')}\n"
            answer += f"Data: {latest.get('data', {})}\n"

            explanation = Explanation(
                explanation_type=ExplanationType.WHY_DECISION,
                question=f"Why was decision {decision_id} made?",
                answer=answer,
                context=context or {},
                references=[decision_id],
            )
        else:
            explanation = Explanation(
                explanation_type=ExplanationType.WHY_DECISION,
                question=f"Why was decision {decision_id} made?",
                answer=f"Decision {decision_id} not found in recent history.",
                context=context or {},
            )

        self.explanation_history.append(explanation)
        return explanation

    def explain_what_options(self, situation: str, context: Optional[Dict] = None) -> Explanation:
        """
        Explain what options exist within scope.

        Examples:
        - What can I do about blocked task X?
        - What options do I have for cross-language work?
        - What are valid next steps?
        """
        answer = f"For situation '{situation}', you have the following options:\n\n"

        # Provide general options based on situation
        if "blocked" in situation.lower():
            answer += "1. Wait for preconditions to be satisfied\n"
            answer += "2. Clarify ambiguous requirements\n"
            answer += "3. Override (with cost and justification)\n"
            answer += "4. Cancel the directive\n"
        elif "cross-language" in situation.lower():
            answer += "1. Create a formal cross-department contract\n"
            answer += "2. Use the Elevator Protocol for service bridges\n"
            answer += "3. Route through separate directives per language\n"
        else:
            answer += "1. Issue a new directive\n"
            answer += "2. Query system state\n"
            answer += "3. Request audit review\n"
            answer += "4. Consult Head of Security for safety concerns\n"

        explanation = Explanation(
            explanation_type=ExplanationType.WHAT_OPTIONS,
            question=f"What options exist for: {situation}",
            answer=answer,
            context=context or {},
        )
        self.explanation_history.append(explanation)
        return explanation

    # =========================================================================
    # TRANSLATE CAPABILITY
    # =========================================================================

    def translate_civilization_to_human(self, civilization_text: str) -> Translation:
        """
        Translate civilizational language to human language.

        Examples:
        - "Task state: BLOCKED, preconditions unmet"
          → "This work is paused because requirements aren't ready yet"
        - "Consensus threshold: 0.67, achieved: 0.50"
          → "Vote passed with 67% support, but needed 67% approval"
        """
        # Common translations
        glossary = {
            "Cognitive Contract": "Work agreement with clear goals and constraints",
            "Directive Tree": "Breakdown of work from high-level goal to specific tasks",
            "Consensus Band": "Voting system for resolving disagreements",
            "Scarcity Economics": "Limited resources forcing prioritization",
            "Constitutional Mutation": "Controlled system improvement process",
            "Meta-Office": "Supreme authority that judges constitutional issues",
            "Elevator Protocol": "Way for different language teams to work together",
            "Floor": "Team specialized in one programming language",
            "Office": "Sub-team with specific role (architect, builder, etc.)",
        }

        # Simple translation (in real system, would be more sophisticated)
        translated = civilization_text
        for technical, plain in glossary.items():
            if technical.lower() in translated.lower():
                translated = translated.replace(technical, f"{technical} ({plain})")

        translation = Translation(
            translation_type=TranslationType.CIVILIZATION_TO_HUMAN,
            original=civilization_text,
            translated=translated,
            glossary=glossary,
        )
        self.translation_history.append(translation)
        return translation

    # =========================================================================
    # PREVIEW CAPABILITY
    # =========================================================================

    def preview_consequences(self, proposed_action: str, context: Optional[Dict] = None) -> Preview:
        """
        Preview consequences of a proposed action.

        Examples:
        - What if I override this decision?
        - What will canceling this task do?
        - What happens if I freeze the world?
        """
        consequences = []
        resource_costs = {}
        risks = []
        alternatives = []

        # Analyze action
        if "override" in proposed_action.lower():
            consequences = [
                "Decision will be overridden with justification logged",
                "Original decision-makers will be notified",
                "Override will be in audit trail permanently",
            ]
            resource_costs = {"manager_attention": 5, "audit_entries": 1}
            risks = ["May undermine agent autonomy", "Could set precedent for future overrides"]
            alternatives = [
                "Request clarification instead",
                "Allow appeal process to complete",
                "Modify directive to avoid conflict",
            ]
        elif "freeze" in proposed_action.lower():
            consequences = [
                "All execution stops immediately",
                "Current work is preserved",
                "No new tasks can start",
                "Audit continues recording",
            ]
            resource_costs = {"system_availability": -100}  # Negative = cost to others
            risks = ["Work in progress may be left in inconsistent state", "Deadlines may be missed"]
            alternatives = [
                "Pause specific floor instead",
                "Complete current tasks first",
                "Use emergency halt for security only",
            ]
        else:
            consequences = ["Action will be executed according to system rules"]
            resource_costs = {"generic_cost": 1}

        preview = Preview(
            action=proposed_action,
            consequences=consequences,
            resource_costs=resource_costs,
            risks=risks,
            alternatives=alternatives,
        )
        self.preview_history.append(preview)
        return preview

    # =========================================================================
    # PREPARE CAPABILITY
    # =========================================================================

    def prepare_draft_directive(
        self, goal: str, language: str, constraints: Optional[List[str]] = None
    ) -> DraftDirective:
        """
        Prepare a draft directive for the user.

        The user still must issue it - the Consigliere cannot execute.
        """
        constraints = constraints or []

        draft_text = f"""
Code Directive Draft:

Language: {language}
Goal: {goal}
Constraints:
{chr(10).join(f"  - {c}" for c in constraints) if constraints else "  (none)"}

This directive will create a Cognitive Contract binding the {language} floor
to produce correct, tested code that accomplishes: {goal}
"""

        rationale = f"This directive targets the {language} floor because {goal} falls within its jurisdiction."

        expected_outcome = f"""
Expected artifacts:
1. Code implementation in {language}
2. Test suite demonstrating correctness
3. Review verdict
4. Security attestation
5. Contract fulfillment record
"""

        estimated_cost = {"agent_time": 10, "manager_attention": 2, "testing_cycles": 1}

        warnings = []
        if not constraints:
            warnings.append("No constraints specified - agents will use defaults")
        if len(goal) < 20:
            warnings.append("Goal is very brief - consider adding more detail")

        draft = DraftDirective(
            draft_text=draft_text,
            rationale=rationale,
            expected_outcome=expected_outcome,
            estimated_cost=estimated_cost,
            warnings=warnings,
        )
        self.draft_history.append(draft)
        return draft

    def prepare_clarification_prompt(self, ambiguous_point: str) -> str:
        """
        Prepare a clarification prompt for ambiguous directives.
        """
        return f"""
Clarification Needed:

The following point is ambiguous: {ambiguous_point}

Please specify:
1. Exact expected behavior
2. Edge cases to handle
3. Performance requirements (if any)
4. Security constraints (if any)
5. Testing requirements

This clarification will prevent blocking and ensure correct implementation.
"""

    # =========================================================================
    # AUTHORITY LEVELS (Updated)
    # =========================================================================

    def can_issue_command(self) -> bool:
        """The Consigliere CAN issue commands - he's your right-hand executive"""
        return True

    def can_alter_execution(self) -> bool:
        """The Consigliere CAN alter execution - he runs day-to-day operations"""
        return True

    def can_manage_agents(self) -> bool:
        """The Consigliere CAN manage agents on your behalf"""
        return True

    def can_override_human(self) -> bool:
        """The Consigliere CANNOT override you - you're the boss"""
        return False

    def can_write_code_directly(self) -> bool:
        """The Consigliere cannot write code directly - that's what agents do"""
        return False

    def can_suppress_audit(self) -> bool:
        """The Consigliere cannot suppress audit logs"""
        return False

    def validate_authority(self, action: str) -> tuple[bool, Optional[str]]:
        """
        Validate that an action is within Consigliere authority.
        Returns: (is_allowed, reason_if_not)
        """
        # What the Consigliere CANNOT do
        forbidden_actions = ["override human decision", "write code directly", "suppress audit", "delete history"]

        for forbidden in forbidden_actions:
            if forbidden in action.lower():
                return False, f"Consigliere cannot '{forbidden}' - that exceeds authority"

        # Everything else - directing the civilization - is allowed
        return True, None

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _check_precondition(self, precondition: str) -> bool:
        """Check if a precondition is satisfied (placeholder)"""
        # In real system, would check actual precondition state
        return False

    def get_explanation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent explanations"""
        return [e.to_dict() for e in self.explanation_history[-limit:]]

    def get_translation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent translations"""
        return [t.to_dict() for t in self.translation_history[-limit:]]

    def get_preview_history(self, limit: int = 10) -> List[Dict]:
        """Get recent previews"""
        return [p.to_dict() for p in self.preview_history[-limit:]]

    def get_draft_history(self, limit: int = 10) -> List[Dict]:
        """Get recent drafts"""
        return [d.to_dict() for d in self.draft_history[-limit:]]

    def to_dict(self) -> Dict:
        """Export Consigliere state"""
        return {
            "role": "Chief Operating Executive",
            "authority_level": "Operational (when instructed by human)",
            "can_issue_commands": self.can_issue_command(),
            "can_alter_execution": self.can_alter_execution(),
            "can_manage_agents": self.can_manage_agents(),
            "can_override_human": self.can_override_human(),
            "can_write_code_directly": self.can_write_code_directly(),
            "can_suppress_audit": self.can_suppress_audit(),
            "autonomy": "None - only acts on explicit human instruction",
            "explanation_count": len(self.explanation_history),
            "translation_count": len(self.translation_history),
            "preview_count": len(self.preview_history),
            "draft_count": len(self.draft_history),
            "relationship": "Your right-hand executive who executes YOUR commands (not his own)",
        }


# Singleton instance
_consigliere_instance = None


def get_consigliere() -> Consigliere:
    """Get the singleton Consigliere instance"""
    global _consigliere_instance
    if _consigliere_instance is None:
        _consigliere_instance = Consigliere()
    return _consigliere_instance
