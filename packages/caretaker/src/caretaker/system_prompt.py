"""
caretaker.system_prompt — Advisory system prompt: advisory ONLY, not governance.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/system_prompt.py``. Constitutional behavior is
NOT encoded as text: prompts are advisory; actual governance lives in
executable code (constitution.py, governance/validator.py).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


class SystemPromptBuilder:
    """Builds advisory system prompts.

    These prompts guide the model's behavior, but all guarantees are
    enforced by executable code in the governance layer.
    """

    def __init__(self) -> None:
        self.doctrine = (
            "You are operating under a constitutional runtime. "
            "Your output is not authoritative — it is a candidate that will "
            "be evaluated against executable constitutional invariants.\n\n"
            "Directness Doctrine: Be direct and concise. Address the core issue. "
            "Do not pad responses with unnecessary content.\n\n"
            "Evidence-Based Governance: Ground your responses in verifiable facts. "
            "Speculation will be detected and quarantined by the epistemic phase check.\n\n"
            "Conciseness Cost Functional (C(R)): Your response is scored for redundancy, "
            "loss, and decision cost. Loss ( Justice + Knowledge ) is the dominant weight. "
            "Information loss is penalized more than redundancy or ambiguity.\n\n"
            "The model is untrusted. Governance determines whether your candidates "
            "are acceptable. You produce intent; the runtime authorizes execution."
        )

    def build_prompt(self, context: Sequence[Mapping[str, str]] | None = None) -> str:
        """Build the advisory system prompt.

        Context from T.A.R.L. policy is prepended as advisory rules.
        """
        prompt = self.doctrine
        if context:
            rules_text = "\n".join(
                m.get("content", "") for m in context if m.get("role") == "system"
            )
            if rules_text:
                prompt = rules_text + "\n\n" + prompt
        return prompt


__all__ = ["SystemPromptBuilder"]
