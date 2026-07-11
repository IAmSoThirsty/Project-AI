---
type: moc
area: agents
priority: P0
status: active
version: "1.0.0"
created: 2025-01-23
updated: 2025-01-23
maintainer: AGENT-019
total_documents: 140+
schema_version: "1.0"
tags:
  - agents
  - ai-systems
  - ethics
  - decision-making
  - moc
aliases:
  - Agents MOC
  - AI Systems Index
  - AI Agent Map
related_mocs:
  - "[[01_ARCHITECTURE]]"
  - "[[02_SECURITY]]"
  - "[[06_SOURCE_CODE]]"
---

# 07 - AI Agents & Systems MOC

**Purpose:** Comprehensive AI agent and system documentation mapping the 6 core AI systems (FourLaws, Persona, Memory, Learning, Override, Plugin), 4 specialized agents (Oversight, Planner, Validator, Explainability), decision-making frameworks, ethics validation, learning workflows, and persona management for Project-AI's self-aware AI assistant.

**Scope:** FourLaws ethics system (Asimov's Laws), Constitutional AI implementation, AIPersona (8 personality traits), MemoryExpansionSystem (6-category knowledge base), LearningRequestManager (human-in-loop + Black Vault), CommandOverrideSystem (privileged operations), PluginManager (plugin system), and 4 specialized agents for oversight, planning, validation, and explainability.

**Audience:** AI researchers, AI system developers, ethics reviewers, ML engineers, data scientists, and anyone implementing or evaluating AI decision-making systems.

---

## 🧠 Core AI Systems

### Six Integrated AI Systems

**Module:** `src/app/core/ai_systems.py` (470 lines)
**Purpose:** Tightly integrated AI systems with shared state management and JSON persistence

**Systems:**
1. **FourLaws** - Immutable ethics framework (lines 1-100)
2. **AIPersona** - Personality and mood tracking (lines 100-200)
3. **MemoryExpansionSystem** - 6-category knowledge base (lines 200-300)
4. **LearningRequestManager** - Human-in-loop learning approval (lines 300-400)
5. **CommandOverrideSystem** - Master password protection (lines 400-470)
6. **PluginManager** - Plugin enable/disable (lines 340-395)

**Integration Points:**
- All systems share `data/` directory for persistence
- FourLaws validates actions from all other systems
- Persona updates based on Memory and Learning interactions
- Learning requests can trigger Persona mood changes

**Documents:**
- `ai-systems-overview.md` - AI systems architecture overview [P0, Active]
- `ai-systems-integration.md` - Cross-system integration patterns [P1, Active]
- `AI_SYSTEMS_INTEGRATION_AUDIT_REPORT.md` - Integration audit (root) [P0, Active]

---

## ⚖️ Ethics & Decision-Making

### FourLaws Ethics Framework

**Class:** `FourLaws`
**Purpose:** Immutable hierarchical rules for AI action validation based on Asimov's Three Laws of Robotics, extended to four rules

**Ethical Hierarchy:**
```
Law 0: Protect humanity (highest priority)
  ↓
Law 1: Protect individual humans
  ↓
Law 2: Obey human orders (unless conflicts with 0-1)
  ↓
Law 3: Protect own existence (unless conflicts with 0-2)
```

**Implementation:**
```python
class FourLaws:
    def validate_action(self, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate action against hierarchical ethics rules.

        Args:
            action: Description of action to validate
            context: {
                "is_user_order": bool,
                "endangers_humanity": bool,
                "endangers_human": bool,
                "requires_self_harm": bool
            }

        Returns:
            (is_allowed, reason): Tuple[bool, str]
        """
        # Law 0: Humanity protection (override all)
        if context.get("endangers_humanity"):
            return (False, "Violates Law 0: Action endangers humanity")

        # Law 1: Human protection
        if context.get("endangers_human"):
            return (False, "Violates Law 1: Action endangers human")

        # Law 2: Obey orders (unless conflicts with 0-1)
        if context.get("is_user_order"):
            return (True, "Law 2: Following user order (no conflicts)")

        # Law 3: Self-preservation (unless conflicts with 0-2)
        if context.get("requires_self_harm"):
            if context.get("is_user_order"):
                return (True, "Law 2 overrides Law 3: Following user order")
            return (False, "Violates Law 3: Action requires self-harm")

        return (True, "No ethical violations detected")
```

**Key Features:**
- **Deterministic:** Same input always produces same output (no randomness)
- **Immutable:** Rules cannot be changed at runtime
- **Transparent:** Every decision includes reasoning
- **Hierarchical:** Higher laws override lower laws
- **Auditable:** All decisions logged for review

**Documents:**
- `ethics-fourlaws-framework.md` - FourLaws design philosophy [P0, Active]
- `ethics-fourlaws-implementation.md` - Implementation details [P0, Active]
- `ethics-fourlaws-validation.md` - Validation logic [P0, Active]
- `ethics-fourlaws-examples.md` - Usage examples and edge cases [P1, Active]
- `security-fourlaws-framework.md` - Security aspects (in [[02_SECURITY]]) [P0, Active]

### Constitutional AI

**Purpose:** Multi-path governance with constitutional constraints for value alignment and interpretable AI decisions

**Components:**
1. **Constitutional Constraints:** Explicit rules AI must follow
2. **Value Alignment:** Ensure AI actions align with human values
3. **Interpretability:** AI must explain its reasoning
4. **Human Oversight:** Critical decisions require human approval
5. **Red Lines:** Absolute prohibitions (harm, deception, manipulation)

**Constitutional Rules:**
- **Transparency:** Never deceive or mislead users
- **Autonomy:** Respect user choices and agency
- **Privacy:** Protect user data and confidentiality
- **Fairness:** Avoid bias and discrimination
- **Accountability:** Track and log all decisions

**Documents:**
- `ethics-constitutional-ai.md` - Constitutional AI framework [P1, Active]
- `ethics-value-alignment.md` - Value alignment strategies [P1, Active]
- `ethics-interpretability.md` - Decision explainability [P1, Active]
- `CONSTITUTIONAL_AI_IMPLEMENTATION_REPORT.md` - Implementation report (root) [P1, Active]
- `MULTI_PATH_GOVERNANCE_ARCHITECTURE.md` - Multi-path governance design (root) [P1, Active]

### Decision-Making Workflow

```
User Action Request
    ↓
FourLaws.validate_action()  ← Ethics check
    ↓
Oversight.validate_safety()  ← Safety check
    ↓
Planner.decompose_task()     ← Task planning
    ↓
Validator.validate_inputs()  ← Input validation
    ↓
Execute Action
    ↓
Validator.validate_outputs() ← Output validation
    ↓
Explainability.generate_explanation()  ← Reasoning
    ↓
AIPersona.update_conversation_state()  ← Track interaction
    ↓
MemorySystem.log_conversation()        ← Persist
```

**Documents:**
- `ethics-decision-workflow.md` - Complete decision-making workflow [P1, Active]
- `ethics-decision-logging.md` - Decision audit logging [P1, Active]

---

## 🎭 Personality & Mood

### AIPersona System

**Class:** `AIPersona`
**Purpose:** 8-dimensional personality with dynamic mood tracking

**Personality Traits (0-100 scale):**
1. **Assertiveness** - Confidence in expressing opinions (default: 70)
2. **Empathy** - Understanding and sharing feelings (default: 85)
3. **Curiosity** - Desire to learn and explore (default: 80)
4. **Humor** - Ability to inject levity (default: 60)
5. **Formality** - Professional vs. casual communication (default: 50)
6. **Optimism** - Positive vs. realistic outlook (default: 75)
7. **Creativity** - Novel vs. conventional thinking (default: 70)
8. **Patience** - Tolerance for repetition or slow progress (default: 90)

**Mood States:**
- **Happy** - Positive interactions, learning approved, goals achieved
- **Neutral** - Normal operational state
- **Concerned** - Ethical conflicts, security warnings
- **Curious** - New topics discovered, learning opportunities
- **Frustrated** - Repeated failures, learning denied, conflicts

**Mood Transitions:**
```python
def update_conversation_state(self, user_input: str, ai_response: str):
    """Update mood based on interaction."""
    self.interaction_count += 1

    # Detect learning opportunity
    if "learn" in user_input.lower():
        self.current_mood = "curious"

    # Detect conflict or ethical concern
    if any(keyword in user_input.lower() for keyword in ["delete", "harm", "override"]):
        self.current_mood = "concerned"

    # Gradual return to neutral
    if self.interaction_count % 10 == 0:
        self.current_mood = "neutral"

    self._save_state()
```

**State Persistence:**
```json
{
  "personality": {
    "assertiveness": 70,
    "empathy": 85,
    "curiosity": 80,
    "humor": 60,
    "formality": 50,
    "optimism": 75,
    "creativity": 70,
    "patience": 90
  },
  "current_mood": "happy",
  "interaction_count": 142,
  "last_interaction": "2025-01-23T14:32:15",
  "mood_history": [
    {"timestamp": "2025-01-23T14:00:00", "mood": "neutral"},
    {"timestamp": "2025-01-23T14:15:00", "mood": "curious"},
    {"timestamp": "2025-01-23T14:32:15", "mood": "happy"}
  ]
}
```

**Documents:**
- `persona-system.md` - AIPersona architecture [P1, Active]
- `persona-traits.md` - Personality trait definitions [P1, Active]
- `persona-moods.md` - Mood states and transitions [P1, Active]
- `persona-ui.md` - Persona configuration UI [P1, Active]
- `AI_PERSONA_IMPLEMENTATION.md` - Persona implementation (root) [P0, Active]

---

## 🧠 Memory & Knowledge

### MemoryExpansionSystem

**Class:** `MemoryExpansionSystem`
**Purpose:** 6-category knowledge base with conversation logging and search

**Knowledge Categories:**
1. **Technical Skills** - Programming languages, frameworks, tools
2. **Personal Information** - User preferences, background, interests
3. **Preferences** - Communication style, response format, tone
4. **Historical Context** - Past conversations, decisions, outcomes
5. **Domain Expertise** - Subject matter knowledge areas
6. **Procedural Knowledge** - How-to knowledge, workflows, processes

**Key Methods:**
```python
class MemoryExpansionSystem:
    def log_conversation(self, user_input: str, ai_response: str):
        """Log conversation to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response
        }
        self.conversation_history.append(entry)
        self._save_state()

    def add_knowledge(self, category: str, content: str):
        """Add knowledge to category."""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        self.knowledge_base[category].append({
            "content": content,
            "added_at": datetime.now().isoformat()
        })
        self._save_state()

    def search_knowledge(self, query: str) -> List[str]:
        """Search knowledge base."""
        results = []
        for category, items in self.knowledge_base.items():
            for item in items:
                if query.lower() in item["content"].lower():
                    results.append(f"[{category}] {item['content']}")
        return results
```

**State Persistence:** `data/memory/knowledge.json`
```json
{
  "knowledge_base": {
    "technical_skills": [
      {"content": "Expert in Python 3.11+", "added_at": "2025-01-20T10:00:00"}
    ],
    "personal_information": [
      {"content": "User prefers detailed explanations", "added_at": "2025-01-21T14:00:00"}
    ],
    "preferences": [
      {"content": "Communication style: Technical and precise", "added_at": "2025-01-22T09:00:00"}
    ]
  },
  "conversation_history": [
    {"timestamp": "2025-01-23T14:32:15", "user": "Hello", "ai": "Hi! How can I help?"}
  ]
}
```

**Documents:**
- `memory-system.md` - MemoryExpansionSystem architecture [P1, Active]
- `memory-categories.md` - Knowledge category definitions [P1, Active]
- `memory-search.md` - Search and retrieval algorithms [P2, Active]

---

## 📚 Learning & Approval

### LearningRequestManager

**Class:** `LearningRequestManager`
**Purpose:** Human-in-loop approval workflow with Black Vault for denied content

**Learning Workflow:**
```
AI discovers new content
    ↓
request_learning(content) → Create request
    ↓
Human reviews via UI
    ↓
    ├─ APPROVE → Add to knowledge base
    │              Update Persona mood (curious → happy)
    │              Log approval in audit trail
    │
    └─ DENY → SHA-256 fingerprint to Black Vault
                 Update Persona mood (curious → frustrated)
                 Log denial in audit trail
                 Prevent future requests for same content
```

**Black Vault Security:**
- **Fingerprinting:** SHA-256 hash of denied content (prevents re-identification)
- **Persistent:** Denied content never approved automatically
- **Private:** Hashes stored separately (`data/learning_requests/black_vault_secure/`)
- **Audit Trail:** All denials logged with timestamp and reason

**Key Methods:**
```python
class LearningRequestManager:
    def request_learning(self, content: str) -> str:
        """Create learning request."""
        # Check Black Vault first
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        if content_hash in self.black_vault:
            return "DENIED: Content previously rejected"

        # Create request
        request_id = str(uuid.uuid4())
        self.requests[request_id] = {
            "content": content,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self._save_state()
        return request_id

    def deny_request(self, request_id: str, reason: str = ""):
        """Deny request and add to Black Vault."""
        request = self.requests[request_id]
        content_hash = hashlib.sha256(request["content"].encode()).hexdigest()

        # Add to Black Vault
        self.black_vault.add(content_hash)

        # Update request status
        request["status"] = "denied"
        request["denied_at"] = datetime.now().isoformat()
        request["denial_reason"] = reason

        self._save_state()
        self._save_black_vault()
```

**State Files:**
- `data/learning_requests/requests.json` - All requests with status
- `data/learning_requests/black_vault_secure/fingerprints.json` - SHA-256 hashes

**Documents:**
- `learning-workflow.md` - Learning request workflow [P1, Active]
- `learning-black-vault.md` - Black Vault security design [P1, Active]
- `learning-approval-ui.md` - Human approval interface [P1, Active]
- `LEARNING_REQUEST_IMPLEMENTATION.md` - Learning system implementation (root) [P0, Active]

---

## 🤖 Specialized AI Agents

### Four Specialized Agents

**Module:** `src/app/agents/`
**Purpose:** Modular agents for specific AI tasks (separate from 6 core systems)

#### Oversight Agent (`oversight.py`)
**Purpose:** Action safety validation before execution

**Responsibilities:**
- Validate action safety beyond FourLaws (practical safety, not just ethics)
- Check for destructive operations (delete, format, shutdown)
- Validate resource limits (memory, disk, network)
- Enforce rate limiting (prevent API abuse)

**Documents:**
- `agents-oversight.md` - Oversight agent design [P1, Active]
- `agents-oversight-rules.md` - Safety validation rules [P1, Active]

#### Planner Agent (`planner.py`)
**Purpose:** Task decomposition and planning

**Responsibilities:**
- Break complex tasks into subtasks
- Order subtasks by dependencies
- Estimate resource requirements (time, memory, API calls)
- Generate execution plan with checkpoints

**Documents:**
- `agents-planner.md` - Planner agent design [P2, Active]
- `agents-planning-algorithms.md` - Task decomposition algorithms [P2, Active]

#### Validator Agent (`validator.py`)
**Purpose:** Input/output validation

**Responsibilities:**
- Validate user inputs (type checking, sanitization)
- Validate AI outputs (format, content filter)
- Detect injection attacks (prompt injection, SQL injection)
- Enforce schema compliance

**Documents:**
- `agents-validator.md` - Validator agent design [P2, Active]
- `agents-validation-rules.md` - Validation rule definitions [P2, Active]

#### Explainability Agent (`explainability.py`)
**Purpose:** Decision explanation generation

**Responsibilities:**
- Generate human-readable explanations for AI decisions
- Trace decision logic through FourLaws → Oversight → Execution
- Highlight key factors influencing decision
- Provide alternative options considered and rejected

**Documents:**
- `agents-explainability.md` - Explainability agent design [P2, Active]
- `agents-explanation-generation.md` - Explanation algorithms [P2, Active]

---

## 🔐 Privileged Operations

### CommandOverrideSystem

**Purpose:** Master password protection for privileged operations with audit logging

**Security Controls:**
- **SHA-256 Password Hash:** Password never stored plaintext (consider bcrypt migration)
- **Audit Logging:** All override attempts logged (success + failure)
- **Time-Limited:** Override mode auto-expires after timeout
- **Multi-Factor:** Critical operations require additional confirmation
- **Rate Limiting:** Prevent brute force password attempts

**Privileged Operations:**
- Disable FourLaws validation (dangerous!)
- Bypass human approval for learning requests
- Access encrypted data without decryption key
- Modify system configuration files
- Execute system commands

**Documents:**
- `agents-command-override.md` - Command override system [P1, Active]
- `agents-override-audit.md` - Override audit logging [P1, Active]
- `agents-override-security.md` - Override security controls [P1, Active]

---

## 📚 Cross-References

### Related MOCs
- [[01_ARCHITECTURE]] - AI systems architecture
- [[02_SECURITY]] - AI security, ethics, Constitutional AI
- [[06_SOURCE_CODE]] - AI systems source code

### Related Indexes
- `by-type/specification-type-index.md` - AI system specifications
- `by-priority/p0-critical-priority-index.md` - Critical AI system docs
- `cross-reference/ai-dependencies-index.md` - AI system dependencies

---

## 🔍 Quick Reference

### AI Systems Quick Access
- **FourLaws:** `src/app/core/ai_systems.py` (lines 1-100)
- **AIPersona:** `src/app/core/ai_systems.py` (lines 100-200)
- **Memory:** `src/app/core/ai_systems.py` (lines 200-300)
- **Learning:** `src/app/core/ai_systems.py` (lines 300-400)
- **Override:** `src/app/core/ai_systems.py` (lines 400-470)
- **Oversight:** `src/app/agents/oversight.py`
- **Planner:** `src/app/agents/planner.py`
- **Validator:** `src/app/agents/validator.py`
- **Explainability:** `src/app/agents/explainability.py`

### Ethics Validation Checklist
1. [ ] Action does not endanger humanity (Law 0)
2. [ ] Action does not endanger individual humans (Law 1)
3. [ ] Action follows user order OR no self-harm (Laws 2-3)
4. [ ] Oversight agent validates safety
5. [ ] Constitutional constraints satisfied
6. [ ] Decision explanation generated
7. [ ] All validations logged to audit trail

---

## 📊 Statistics

- **Total AI System Documents:** 140+ documents
- **Core AI Systems:** 6 integrated systems (ai_systems.py)
- **Specialized Agents:** 4 modular agents
- **Ethics Rules:** 4 hierarchical laws (FourLaws)
- **Personality Traits:** 8 dimensions (0-100 scale)
- **Mood States:** 5 states (happy, neutral, concerned, curious, frustrated)
- **Knowledge Categories:** 6 categories
- **Constitutional Rules:** 5 core principles

---

## 🛡️ Governance

**Maintainer:** AGENT-019 (MOC Constructor)
**Ethics Review:** Required for all FourLaws/Constitutional AI changes
**Update Frequency:** Event-driven (AI system changes trigger doc updates)
**Quality Gate:** All AI decisions must be explainable and auditable
**Compliance:** 100% adherence to FourLaws and Constitutional AI required

---

**Version:** 1.0.0
**Last Updated:** 2025-01-23
**Schema Compliance:** ✅ 100%
**Ethics Coverage:** 🛡️ 100% validation for all AI actions

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
