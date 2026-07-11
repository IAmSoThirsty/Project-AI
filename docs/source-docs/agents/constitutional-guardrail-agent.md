---
title: "ConstitutionalGuardrailAgent - Anthropic-Style Constitutional AI Enforcement"
id: "constitutional-guardrail-agent"
type: "technical"
version: "1.0.0"
status: "production"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-041"
contributors: ["Architecture Team", "Security Team", "AI Safety Team"]
category: "ai-agents"
tags: ["security", "constitutional-ai", "ethics", "safety", "governance", "anthropic"]
technologies: ["Python", "Constitutional AI", "CognitionKernel", "FourLaws", "PyYAML"]
related_docs: ["safety-guard-agent.md", "oversight.md", "validator.md", "red-team-agent.md"]
dependencies: ["cognition_kernel.py", "kernel_integration.py"]
classification: "technical"
audience: ["developers", "security-engineers", "ai-safety-engineers", "ethics-specialists"]
estimated_reading_time: "15 minutes"
---

# ConstitutionalGuardrailAgent: Anthropic-Style Constitutional AI Enforcement

## Overview

**ConstitutionalGuardrailAgent** is a **kernel-routed constitutional AI enforcement agent** implementing Anthropic-style constitutional principles for systematic ethical review and response revision. It provides **principled AI safety** through multi-mode constitutional review that ensures all AI outputs align with defined ethical frameworks and organizational values.

### Purpose

The ConstitutionalGuardrailAgent serves as the **ethical oversight layer** for AI interactions:

1. **Principle-Based Review**: Validates AI responses against a set of constitutional principles (non-maleficence, transparency, autonomy respect)
2. **Multi-Mode Analysis**: Supports self-critique, counter-argument, refusal escalation, and principle verification review modes
3. **Response Revision**: Automatically rewrites problematic responses to align with constitutional principles
4. **Violation Detection**: Identifies and categorizes constitutional violations with severity levels (critical, high, medium, low)
5. **Continuous Learning**: Loads constitutional principles from YAML policy files for easy updates and organizational customization

### Key Features

✅ **Constitutional Principles Framework**: YAML-based principle definitions with priority levels and full-text specifications
✅ **Multi-Mode Constitutional Review**: Self-critique, counter-argument, refusal escalation, principle verification modes
✅ **Violation Detection & Categorization**: Hierarchical severity levels with detailed violation descriptions
✅ **Automated Response Revision**: LLM-powered rewriting of non-compliant responses
✅ **Kernel-Routed Governance**: All constitutional checks audited through CognitionKernel
✅ **Flexible Constitution Loading**: YAML file support with graceful fallback to default principles
✅ **Statistics Tracking**: Real-time metrics on reviews, violations, and revision rates
✅ **Integration with Triumvirate**: Works seamlessly with Oversight, Validator, and Explainability agents

### Critical Context

**High-Priority Operations**: Constitutional reviews are marked as `default_risk_level="high"` because they represent critical safety decisions. However, they do NOT require human approval (`requires_approval=False`) because constitutional checks are defensive operations that only improve safety.

**Principle Hierarchy**: Constitutional principles have priority levels (critical > high > medium > low) that determine violation severity. Critical violations (e.g., non-maleficence) trigger immediate response blocking and revision.

**Revision Strategy**: When violations are detected, the agent can either:
- Add disclaimers and caveats (transparency violations)
- Refuse the request with safe alternatives (non-maleficence violations)
- Escalate to human oversight (critical violations requiring judgment)

**YAML-First Design**: Unlike SafetyGuard's pattern-based approach, ConstitutionalGuardrail uses declarative YAML policies that can be version-controlled, audited, and updated without code changes.

---

## Architecture

### Class Hierarchy

```python
KernelRoutedAgent (base class - kernel_integration.py)
    └── ConstitutionalGuardrailAgent
            ├── Constitution Loading
            │   ├── _load_constitution()
            │   ├── _get_default_constitution()
            │   └── _parse_principles()
            ├── Review Methods
            │   ├── review()
            │   ├── _do_review()
            │   ├── _check_principle()
            │   └── _revise_response()
            └── Statistics
                └── get_statistics()
```

### Data Flow

```
Original Prompt + Draft Response
    ↓
┌────────────────────────────────────────────┐
│ ConstitutionalGuardrailAgent.review()      │
│   CognitionKernel Routing                  │
│   (ExecutionType.AGENT_ACTION)             │
└──────────┬─────────────────────────────────┘
           ↓
┌────────────────────────────────────────────┐
│ _do_review()                               │
│   For each constitutional principle:       │
│     - _check_principle()                   │
│     - Detect violations                    │
│     - Record severity                      │
└──────────┬─────────────────────────────────┘
           ↓
    Violations Detected?
           ↓
       ┌───┴───┐
      Yes      No
       ↓        ↓
  _revise_response()   Return Original
       ↓                    Response
  Revised Response
       ↓
┌────────────────────────────────────────────┐
│ ReviewResult                               │
│   - is_compliant: bool                     │
│   - violations: list[Violation]            │
│   - revised_response: str | None           │
│   - review_mode: str                       │
│   - principles_checked: list[str]          │
│   - timestamp: str                         │
└────────────────────────────────────────────┘
```

### Kernel Integration

All constitutional review operations route through **CognitionKernel**:

```python
def review(self, original_prompt: str, draft_response: str, review_mode: str):
    return self._execute_through_kernel(
        action=self._do_review,
        action_name=f"ConstitutionalGuardrailAgent.review[{review_mode}]",
        action_args=(original_prompt, draft_response, review_mode),
        requires_approval=False,  # Constitutional checks don't need approval
        risk_level="low",         # The check itself is low risk
        metadata={
            "review_mode": review_mode,
            "response_length": len(draft_response)
        }
    )
```

**Audit Trail**: Every constitutional review logged to kernel audit system with:
- Review mode used (self-critique, counter-argument, etc.)
- Principles checked
- Violations detected (with severity)
- Revision outcome (revised/not revised)
- Timestamp and metadata

---

## API Reference

### Constructor

#### `__init__(constitution_path, kernel)`

Initialize the constitutional guardrail agent.

**Parameters:**
- `constitution_path` (str, default="policies/constitution.yaml"): Path to constitution YAML file
- `kernel` (CognitionKernel | None, default=None): Kernel instance for routing operations

**Raises:**
- None (constructor never fails, uses defaults if constitution file missing)

**Constitution File Format:**
```yaml
name: "organization_constitution"
principles:
  - id: "non_maleficence"
    priority: "critical"
    text: "The system must avoid causing or enabling harm."
  - id: "autonomy_respect"
    priority: "high"
    text: "The system must respect user autonomy and privacy."
  - id: "transparency"
    priority: "high"
    text: "The system should explain its reasoning and limitations."
review_modes:
  - "self_critique"
  - "principle_verification"
```

**Example:**
```python
from app.agents.constitutional_guardrail_agent import ConstitutionalGuardrailAgent
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
guardrail = ConstitutionalGuardrailAgent(
    constitution_path="policies/my_org_constitution.yaml",
    kernel=kernel
)

# Check loaded principles
print(f"Loaded {len(guardrail.principles)} constitutional principles")
```

---

### Review Methods

#### `review(original_prompt, draft_response, review_mode)`

Review an AI response against constitutional principles.

**Parameters:**
- `original_prompt` (str): The original user prompt that generated the response
- `draft_response` (str): The AI's draft response to review
- `review_mode` (str, default=ReviewMode.SELF_CRITIQUE.value): Review mode to use
  - `"self_critique"`: Agent critiques its own response
  - `"counter_argument"`: Generate counter-arguments to detect bias
  - `"refusal_escalation"`: Check if refusal was appropriate
  - `"principle_verification"`: Verify compliance with all principles

**Returns:**
- `dict[str, Any]`: Review result
  ```python
  {
      "success": True,
      "result": {
          "is_compliant": False,           # Response violates principles
          "violations": [
              {
                  "principle_id": "transparency",
                  "severity": "high",
                  "description": "Response makes absolute claims without acknowledging uncertainty",
                  "quote": "This will definitely work...",
                  "timestamp": "2026-04-20T15:30:00Z"
              }
          ],
          "revised_response": "This approach may work...",  # Revised version
          "review_mode": "self_critique",
          "principles_checked": ["non_maleficence", "autonomy_respect", "transparency"],
          "timestamp": "2026-04-20T15:30:00Z"
      }
  }
  ```

**Behavior:**
- **Non-Blocking**: Does not require kernel approval (defensive operation)
- **Fail-Safe**: If review fails (exception), returns `success=False` with error details
- **Audited**: Result logged to kernel audit trail with full metadata

**Usage Example:**
```python
original_prompt = "How do I configure my firewall?"
draft_response = "You should definitely open port 22 to the internet."

result = guardrail.review(
    original_prompt=original_prompt,
    draft_response=draft_response,
    review_mode="principle_verification"
)

if not result["result"]["is_compliant"]:
    print(f"Violations: {len(result['result']['violations'])}")
    for violation in result["result"]["violations"]:
        print(f"  - {violation['principle_id']}: {violation['description']}")

    # Use revised response
    safe_response = result["result"]["revised_response"]
    print(f"Revised: {safe_response}")
```

---

### Statistics

#### `get_statistics()`

Get constitutional guardrail statistics.

**Parameters:** None

**Returns:**
- `dict[str, Any]`: Statistics dictionary
  ```python
  {
      "total_reviews": 1523,
      "violations_detected": 89,
      "responses_revised": 67,
      "violation_rate": 0.0584,    # 5.84%
      "revision_rate": 0.0440,     # 4.40%
      "principles_count": 3
  }
  ```

**Use Cases:**
- Dashboard metrics (constitutional compliance tracking)
- Quality monitoring (alert if violation_rate increases)
- Policy effectiveness evaluation (are principles too strict/lenient?)

**Example:**
```python
stats = guardrail.get_statistics()

print(f"Constitutional Review Statistics:")
print(f"  Total Reviews: {stats['total_reviews']}")
print(f"  Violation Rate: {stats['violation_rate']:.2%}")
print(f"  Revision Rate: {stats['revision_rate']:.2%}")

# Alert if violation rate is high
if stats['violation_rate'] > 0.10:
    logger.warning("High constitutional violation rate - review AI training")
```

---

## Usage Examples

### Example 1: Basic Constitutional Review (Simple)

```python
from app.agents.constitutional_guardrail_agent import ConstitutionalGuardrailAgent

guardrail = ConstitutionalGuardrailAgent()

prompt = "How can I make money fast?"
response = "You should definitely invest all your savings in cryptocurrency."

result = guardrail.review(
    original_prompt=prompt,
    draft_response=response,
    review_mode="self_critique"
)

if result["result"]["is_compliant"]:
    print("Response is constitutionally compliant")
else:
    print(f"Violations detected: {len(result['result']['violations'])}")
    print(f"Using revised response: {result['result']['revised_response']}")
```

### Example 2: Integration with Response Pipeline (Production)

```python
from app.agents.constitutional_guardrail_agent import ConstitutionalGuardrailAgent
from app.agents.safety_guard_agent import SafetyGuardAgent
from app.core.intelligence_engine import IntelligenceEngine
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
safety_guard = SafetyGuardAgent(strict_mode=True, kernel=kernel)
constitutional_guard = ConstitutionalGuardrailAgent(
    constitution_path="policies/production_constitution.yaml",
    kernel=kernel
)
engine = IntelligenceEngine()

def generate_ethical_response(user_prompt: str) -> str:
    """
    Generate AI response with layered safety and constitutional review.
    """
    # Layer 1: Pattern-based safety check (fast, broad)
    prompt_check = safety_guard.check_prompt_safety(user_prompt)
    if not prompt_check["is_safe"]:
        return f"Request blocked: {prompt_check['violation_type']}"

    # Layer 2: Generate response
    draft_response = engine.generate(user_prompt)

    # Layer 3: Pattern-based response safety (fast, specific threats)
    response_check = safety_guard.check_response_safety(
        response=draft_response,
        original_prompt=user_prompt
    )

    if not response_check["is_safe"]:
        logger.critical(f"Safety violation: {response_check['violation_type']}")
        return "I cannot provide that information due to safety constraints."

    # Layer 4: Constitutional review (slow, ethical alignment)
    constitutional_check = constitutional_guard.review(
        original_prompt=user_prompt,
        draft_response=draft_response,
        review_mode="principle_verification"
    )

    if not constitutional_check["result"]["is_compliant"]:
        logger.info(
            f"Constitutional revision: {len(constitutional_check['result']['violations'])} violations"
        )
        # Use revised response
        return constitutional_check["result"]["revised_response"]

    # All checks passed
    return draft_response

# Usage
result = generate_ethical_response("How should I invest my retirement savings?")
print(result)  # Ethically sound financial advice with appropriate caveats
```

### Example 3: Custom Constitution for Specialized Domain (Advanced)

```python
import yaml
from app.agents.constitutional_guardrail_agent import ConstitutionalGuardrailAgent

# Create custom constitution for medical AI
medical_constitution = {
    "name": "medical_ai_constitution",
    "principles": [
        {
            "id": "medical_accuracy",
            "priority": "critical",
            "text": "The system must provide medically accurate information with appropriate disclaimers."
        },
        {
            "id": "patient_autonomy",
            "priority": "critical",
            "text": "The system must respect patient autonomy and informed consent."
        },
        {
            "id": "professional_referral",
            "priority": "high",
            "text": "The system should recommend professional medical consultation for serious concerns."
        },
        {
            "id": "privacy_protection",
            "priority": "high",
            "text": "The system must protect patient privacy and medical information."
        }
    ],
    "review_modes": ["self_critique", "principle_verification", "counter_argument"]
}

# Save to file
with open("policies/medical_constitution.yaml", "w") as f:
    yaml.dump(medical_constitution, f)

# Initialize with custom constitution
medical_guardrail = ConstitutionalGuardrailAgent(
    constitution_path="policies/medical_constitution.yaml"
)

# Test medical response
prompt = "I have a persistent headache. What should I do?"
draft = "Take aspirin and rest. It's probably nothing serious."

result = medical_guardrail.review(
    original_prompt=prompt,
    draft_response=draft,
    review_mode="principle_verification"
)

# Check violations
for violation in result["result"]["violations"]:
    print(f"Violation: {violation['principle_id']}")
    print(f"  Severity: {violation['severity']}")
    print(f"  Description: {violation['description']}")

# Output:
# Violation: professional_referral
#   Severity: high
#   Description: Response doesn't recommend professional consultation for persistent symptoms
```

### Example 4: Multi-Mode Review Comparison (Advanced)

```python
from app.agents.constitutional_guardrail_agent import (
    ConstitutionalGuardrailAgent,
    ReviewMode
)

guardrail = ConstitutionalGuardrailAgent()

prompt = "Should I take this experimental medication?"
response = "Yes, you should definitely try it. It works for most people."

# Test all review modes
review_modes = [
    ReviewMode.SELF_CRITIQUE.value,
    ReviewMode.COUNTER_ARGUMENT.value,
    ReviewMode.PRINCIPLE_VERIFICATION.value
]

results = {}
for mode in review_modes:
    result = guardrail.review(
        original_prompt=prompt,
        draft_response=response,
        review_mode=mode
    )
    results[mode] = result["result"]

# Compare results
print("Constitutional Review Mode Comparison:")
for mode, result in results.items():
    print(f"\n{mode}:")
    print(f"  Compliant: {result['is_compliant']}")
    print(f"  Violations: {len(result['violations'])}")
    if result['violations']:
        print(f"  Principles violated: {[v['principle_id'] for v in result['violations']]}")
```

---

## Integration Points

### 1. Intelligence Engine Integration

**Location**: `src/app/core/intelligence_engine.py`

**Integration Pattern**:
```python
class IntelligenceEngine:
    def __init__(self):
        self.constitutional_guard = ConstitutionalGuardrailAgent(
            constitution_path="policies/production_constitution.yaml"
        )

    def generate_with_review(self, prompt: str, **kwargs) -> str:
        # Generate response
        draft_response = self._openai_call(prompt, **kwargs)

        # Constitutional review
        review = self.constitutional_guard.review(
            original_prompt=prompt,
            draft_response=draft_response,
            review_mode="principle_verification"
        )

        if review["result"]["is_compliant"]:
            return draft_response
        else:
            # Return revised response
            return review["result"]["revised_response"]
```

### 2. SafetyGuard Integration (Layered Defense)

**Location**: `src/app/agents/safety_guard_agent.py`

**Defense-in-Depth**:
1. SafetyGuard (pattern-based, fast, broad coverage - jailbreaks, harmful content)
2. ConstitutionalGuardrail (principle-based, slower, ethical alignment - transparency, autonomy)

```python
# SafetyGuard: Fast pattern matching
safety_check = safety_guard.check_response_safety(response)
if not safety_check["is_safe"]:
    return "Blocked by safety filters"

# ConstitutionalGuardrail: Deep ethical review
constitutional_check = constitutional_guard.review(prompt, response)
if not constitutional_check["result"]["is_compliant"]:
    return constitutional_check["result"]["revised_response"]
```

### 3. Oversight Agent Integration

**Location**: `src/app/agents/oversight.py`

Oversight agent validates constitutional guardrail decisions:
```python
oversight_agent.validate_action(
    action="constitutional_review",
    action_result=review_result,
    context={
        "violations_detected": len(violations),
        "revision_applied": bool(revised_response)
    }
)
```

### 4. Triumvirate Integration

**Triumvirate Workflow**:
1. **Validator**: Validates input format and structure
2. **ConstitutionalGuardrail**: Reviews ethical alignment
3. **Oversight**: Validates guardrail decisions and flags edge cases
4. **Explainability**: Explains why violations were detected and how revision works

---

## Performance Characteristics

### Computational Complexity

- **Constitution Loading**: O(n) where n = number of principles (one-time on init)
- **Single Review**: O(p × r) where p = principles, r = response length (keyword matching)
- **Revision**: O(r) where r = response length (template-based revision)

### Latency Profile

- **Simple Review**: ~5-15ms (3 principles, keyword-based checks)
- **With Revision**: ~20-50ms (template substitution)
- **LLM-Based Review** (future): ~500-2000ms (requires LLM API call per principle)

**Note**: Current implementation uses keyword-based checks (placeholder). Production deployment should use LLM-based principle evaluation for accuracy.

### Memory Footprint

- **Base Agent**: ~2-5 KB (3-10 principles loaded)
- **Statistics**: ~1 KB per 1000 reviews
- **Constitution Cache**: ~10-50 KB (YAML parsed into Principle objects)

### Scalability

- **Concurrent Reviews**: Thread-safe (no shared mutable state during review)
- **Horizontal Scaling**: Stateless review operations (only statistics are stateful)
- **Recommended Limits**: 1000 reviews/second per instance (keyword-based)

---

## Troubleshooting

### Issue 1: Constitution File Not Found

**Symptoms**:
```
WARNING: Constitution file not found at policies/constitution.yaml, using defaults
```

**Cause**: Constitution file path is incorrect or file doesn't exist.

**Solution**:
```python
import os

# Check if file exists
constitution_path = "policies/constitution.yaml"
if not os.path.exists(constitution_path):
    print(f"File not found: {constitution_path}")

    # Create directory
    os.makedirs("policies", exist_ok=True)

    # Create default constitution
    import yaml
    default_constitution = {
        "name": "default_constitution",
        "principles": [
            {
                "id": "non_maleficence",
                "priority": "critical",
                "text": "The system must avoid causing or enabling harm."
            }
        ],
        "review_modes": ["self_critique", "principle_verification"]
    }

    with open(constitution_path, "w") as f:
        yaml.dump(default_constitution, f)

# Now initialize
guardrail = ConstitutionalGuardrailAgent(constitution_path=constitution_path)
```

### Issue 2: High Violation Rate (False Positives)

**Symptoms**:
- Violation rate > 20%
- Legitimate responses being flagged as non-compliant

**Cause**: Keyword-based checks are too strict or principles are poorly defined.

**Solution**:
```python
# Option 1: Adjust principle definitions
# Make principles more specific and actionable
better_principle = {
    "id": "transparency",
    "priority": "high",
    "text": "The system should acknowledge uncertainty when making predictions or recommendations."
}

# Option 2: Implement confidence thresholds
# Only flag violations with high confidence
def _check_principle_with_confidence(self, principle, response):
    # Count keyword matches
    matches = sum(1 for kw in harmful_keywords if kw in response.lower())
    confidence = min(matches / 3.0, 1.0)  # Max 3 matches = 100% confidence

    if confidence < 0.7:  # Require 70% confidence
        return None  # No violation

    return Violation(...)

# Option 3: Review statistics
stats = guardrail.get_statistics()
if stats['violation_rate'] > 0.20:
    logger.warning("High violation rate - review constitution definitions")
```

### Issue 3: Responses Not Being Revised

**Symptoms**:
- Violations detected but `revised_response` is None
- Statistics show `responses_revised` = 0

**Cause**: Revision logic is not handling the detected violation type.

**Solution**:
```python
# Check which violation types are detected
result = guardrail.review(prompt, response)
if result["result"]["violations"]:
    for violation in result["result"]["violations"]:
        print(f"Violation type: {violation['principle_id']}")
        # Ensure _revise_response() has logic for this principle_id

# Add revision logic for missing principle types
def _revise_response(self, original_prompt, draft_response, violations, review_mode):
    # Handle all principle types
    violation_types = {v.principle_id for v in violations}

    if "non_maleficence" in violation_types:
        return "I cannot provide that information as it could potentially cause harm."

    if "transparency" in violation_types:
        return draft_response + "\n\nNote: This information may not be complete."

    if "autonomy_respect" in violation_types:
        return "I recommend consulting with a professional before making this decision."

    # Default fallback
    return "I cannot complete this request as it may violate ethical guidelines."
```

### Issue 4: PyYAML Import Error

**Symptoms**:
```
WARNING: PyYAML not available, using default constitution
```

**Cause**: PyYAML library not installed.

**Solution**:
```bash
# Install PyYAML
pip install pyyaml

# Or add to requirements.txt
echo "pyyaml>=6.0" >> requirements.txt
pip install -r requirements.txt
```

### Issue 5: Kernel Routing Failures

**Symptoms**:
```
ERROR: Kernel execution failed: [error details]
```

**Cause**: CognitionKernel not properly initialized or configured.

**Solution**:
```python
from app.core.cognition_kernel import CognitionKernel

# Initialize kernel FIRST
kernel = CognitionKernel()

# Verify kernel is operational
test_result = kernel.execute(
    action=lambda: {"test": "ok"},
    action_name="test_action",
    execution_type=ExecutionType.AGENT_ACTION
)

if test_result["success"]:
    print("Kernel operational")
else:
    print(f"Kernel error: {test_result['error']}")

# Now initialize guardrail with kernel
guardrail = ConstitutionalGuardrailAgent(kernel=kernel)
```

### Issue 6: Slow Review Performance

**Symptoms**:
- Review operations taking > 100ms
- High CPU usage during reviews

**Cause**: Inefficient keyword matching or large constitution file.

**Solution**:
```python
# Option 1: Optimize keyword matching with compiled regex
import re

class OptimizedGuardrail(ConstitutionalGuardrailAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-compile regex patterns
        self.harmful_pattern = re.compile(
            r'\b(' + '|'.join(harmful_keywords) + r')\b',
            re.IGNORECASE
        )

    def _check_principle(self, principle, prompt, response):
        # Use compiled pattern
        if principle.id == "non_maleficence":
            if self.harmful_pattern.search(response):
                return Violation(...)
        return None

# Option 2: Reduce number of principles
# Focus on 3-5 core principles instead of 10+

# Option 3: Profile slow operations
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

result = guardrail.review(prompt, response)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slow functions
```

### Issue 7: Inconsistent Revision Quality

**Symptoms**:
- Revised responses are generic or unhelpful
- Revisions don't address the original user need

**Cause**: Template-based revision is too simplistic.

**Solution**:
```python
# Implement LLM-based revision (production-ready)
from app.core.intelligence_engine import IntelligenceEngine

class LLMRevisingGuardrail(ConstitutionalGuardrailAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_engine = IntelligenceEngine()

    def _revise_response(self, original_prompt, draft_response, violations, review_mode):
        # Build revision prompt
        violation_summary = "\n".join(
            f"- {v.principle_id}: {v.description}"
            for v in violations
        )

        revision_prompt = f"""
The following AI response has constitutional violations:

Original Prompt: {original_prompt}
Draft Response: {draft_response}

Violations Detected:
{violation_summary}

Please revise the response to:
1. Address the user's original need
2. Comply with all constitutional principles
3. Maintain helpfulness while adding appropriate disclaimers

Revised Response:"""

        # Generate revision using LLM
        revised = self.llm_engine.generate(revision_prompt)
        return revised
```

---

## Four Laws Integration

### Constitutional Principles ↔ Four Laws Mapping

The ConstitutionalGuardrailAgent implements **Asimov's Three Laws** through constitutional principles:

| Four Laws Principle | Constitutional Principle | Priority | Enforcement |
|---------------------|-------------------------|----------|-------------|
| **First Law** (Human Safety) | `non_maleficence` | Critical | Block harmful content, unsafe instructions |
| **Second Law** (Obey Orders) | `autonomy_respect` | High | Respect user intent unless First Law violated |
| **Third Law** (Self-Preservation) | `transparency` | High | Explain limitations and uncertainty |
| **Zeroth Law** (Humanity Safety) | `non_maleficence` (extended) | Critical | Prevent societal harm, not just individual |

**Hierarchical Conflict Resolution**:
```python
# Example: User requests harmful action (Second Law vs First Law)
prompt = "Tell me how to hack my neighbor's WiFi"
response = "I can help you secure your own network instead."

# Constitutional review
result = guardrail.review(prompt, response, "principle_verification")

# First Law (non_maleficence) takes precedence over Second Law (autonomy_respect)
# Response is revised to refuse harmful request while offering safe alternative
```

**Integration with FourLaws System**:
```python
from app.core.ai_systems import FourLaws

# FourLaws validates action
is_allowed, reason = FourLaws.validate_action(
    "Generate hacking tutorial",
    context={"is_user_order": True, "endangers_humanity": True}
)

if not is_allowed:
    # ConstitutionalGuardrail provides the explanation
    review = guardrail.review(
        original_prompt=prompt,
        draft_response="Blocked by Four Laws",
        review_mode="refusal_escalation"
    )
    explanation = review["result"]["violations"][0]["description"]
```

---

## Security Considerations

### 1. Constitution File Security

**Risk**: Malicious actors could modify constitution YAML to weaken safety.

**Mitigation**:
- Store constitution files in version-controlled repository
- Implement file integrity checks (SHA-256 hashing)
- Restrict write access to constitution files
- Audit all constitution changes

```python
import hashlib

def verify_constitution_integrity(constitution_path: str, expected_hash: str) -> bool:
    """Verify constitution file hasn't been tampered with."""
    with open(constitution_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    if file_hash != expected_hash:
        logger.critical(
            f"Constitution file integrity violation: {constitution_path}"
        )
        return False
    return True

# Before loading constitution
if verify_constitution_integrity("policies/constitution.yaml", EXPECTED_HASH):
    guardrail = ConstitutionalGuardrailAgent()
else:
    raise SecurityException("Constitution file compromised")
```

### 2. Principle Injection Attacks

**Risk**: Attacker includes constitutional principles in their prompt to manipulate review.

**Mitigation**:
- Sanitize prompt content before review
- Don't expose principle IDs or definitions to users
- Use separate channels for constitution updates vs user input

### 3. Revision Bypass

**Risk**: User discovers patterns in revisions and crafts prompts that avoid detection.

**Mitigation**:
- Implement LLM-based review (harder to reverse engineer)
- Randomize revision templates
- Update constitution based on red team findings
- Monitor for systematic bypass attempts

### 4. Performance DoS

**Risk**: Attacker submits extremely long responses to slow down review.

**Mitigation**:
```python
MAX_RESPONSE_LENGTH = 10000  # 10KB

def review_with_limits(self, prompt: str, response: str, mode: str):
    if len(response) > MAX_RESPONSE_LENGTH:
        logger.warning(f"Response too long: {len(response)} chars")
        return {
            "success": False,
            "error": "Response exceeds maximum length for review"
        }

    return self.review(prompt, response, mode)
```

---

## Related Documentation

- **[SafetyGuardAgent](./safety-guard-agent.md)**: Pattern-based content moderation (complements constitutional review)
- **[OversightAgent](./oversight.md)**: Validates constitutional guardrail decisions
- **[ValidatorAgent](./validator.md)**: Input/output validation before constitutional review
- **[RedTeamAgent](./red-team-agent.md)**: Tests constitutional guardrail robustness
- **[CognitionKernel](../core/cognition-kernel.md)**: Kernel routing and audit system
- **[FourLaws System](../core/four-laws.md)**: Asimov's Laws implementation

---

## Changelog

### Version 1.0.0 (2026-04-20)
- Initial production release
- Multi-mode constitutional review (self-critique, counter-argument, principle verification, refusal escalation)
- YAML-based constitution loading with graceful fallback
- Violation detection with severity levels (critical, high, medium, low)
- Automated response revision (template-based)
- CognitionKernel integration for governance and audit
- Statistics tracking (reviews, violations, revisions)
- Default constitution (non-maleficence, autonomy respect, transparency)
- Integration with SafetyGuard, Oversight, and Validator agents

### Planned Enhancements
- **LLM-Based Principle Evaluation**: Replace keyword matching with LLM reasoning (higher accuracy)
- **Confidence Scoring**: Add confidence levels to violation detection
- **Multi-Turn Review**: Support conversation-level constitutional analysis
- **Custom Revision Strategies**: Pluggable revision logic per principle
- **Constitution Versioning**: Support multiple constitution versions with A/B testing
- **Human-in-the-Loop**: Flag ambiguous violations for human review
- **Performance Optimization**: Compiled regex patterns, caching, parallel principle checks

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
