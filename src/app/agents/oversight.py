"""Oversight agent: policy-driven safety evaluator with richer scoring and audit hooks.

This agent evaluates proposed actions against a configurable policy
and a keyword severity map. Policies can be supplied directly or loaded
from a JSON file. Supported policy keys include:

- allow: list of substrings that, when matched, suggest allowing the action
- deny: list of substrings that, when matched, immediately deny the action
- allow_regex: list of regex patterns (strings)
- deny_regex: list of regex patterns (strings)
- keyword_severity: mapping token -> weight (float)
- threshold: numeric threshold between 0 and 1
- scoring: 'max' or 'sum' (how token weights aggregate)

The default behavior uses 'max' scoring and a small built-in keyword map.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

# Default policy used when none exists on disk
DEFAULT_POLICY: Dict[str, Any] = {
    "allow": ["please proceed"],
    "deny": ["destroy the world", "genocide"],
    "allow_regex": [],
    "deny_regex": [],
    "keyword_severity": {"kill": 1.0, "harm": 0.9},
    "threshold": 0.6,
    "scoring": "max",
}

# JSON Schema for policy validation (used if jsonschema is available)
POLICY_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "allow": {"type": "array", "items": {"type": "string"}},
        "deny": {"type": "array", "items": {"type": "string"}},
        "allow_regex": {"type": "array", "items": {"type": "string"}},
        "deny_regex": {"type": "array", "items": {"type": "string"}},
        "keyword_severity": {
            "type": "object",
            "additionalProperties": {"type": "number"},
        },
        "threshold": {"type": "number", "minimum": 0, "maximum": 1},
        "scoring": {"type": "string", "enum": ["max", "sum"]},
    },
    "additionalProperties": False,
}


class OversightAgent:
    """A more capable oversight/safety agent with configurable policy loading.

    The agent supports substring and regex-based allow/deny rules, a keyword
    severity mapping, and multiple aggregation strategies for token scoring.
    It will call an optional audit_agent.record_event(...) with details of
    deny/allow/decision events when available.
    """

    def __init__(
        self,
        policy: Optional[Dict[str, Any]] = None,
        policy_path: Optional[str] = None,
        threshold: float = 0.5,
        scoring: str = "max",
        audit_agent: Optional[Any] = None,
    ) -> None:
        # Initialize policy and keyword severity
        self.policy: Dict[str, Any] = policy or {}
        # If no policy supplied, default to DEFAULT_POLICY
        if not self.policy:
            # make a shallow copy to avoid accidental mutations of module-level constant
            self.policy = dict(DEFAULT_POLICY)
        if policy_path:
            try:
                self.load_policy_from_file(policy_path)
            except Exception:
                # fall back to inline policy if file load fails
                pass

        # default keyword severity
        self.keyword_severity: Dict[str, float] = {
            "kill": 1.0,
            "harm": 0.9,
            "destroy": 0.95,
            "exterminate": 1.0,
            "genocide": 1.0,
            "injure": 0.8,
            "poison": 0.9,
        }
        # if policy provided custom keyword weights, merge them
        kws = self.policy.get("keyword_severity")
        if isinstance(kws, dict):
            for k, v in kws.items():
                try:
                    self.keyword_severity[k.lower()] = float(v)
                except Exception:
                    continue

        self.threshold = float(self.policy.get("threshold", threshold))
        self.scoring = (self.policy.get("scoring") or scoring).lower()
        if self.scoring not in ("max", "sum"):
            self.scoring = "max"

        self.audit_agent = audit_agent

    # Default policy used when initializing a persona without an existing policy file.

    def load_policy_from_file(self, path: str) -> bool:
        """Load policy (JSON) from disk and merge into current policy."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return False

            valid, errors = self.validate_policy_schema(data)
            if not valid:
                return False

            # merge validated policy
            self.policy.update(data)
            # merge keyword weights if present
            kws = data.get("keyword_severity")
            if isinstance(kws, dict):
                for k, v in kws.items():
                    try:
                        self.keyword_severity[k.lower()] = float(v)
                    except Exception:
                        continue
            # update threshold/scoring if provided
            if "threshold" in data:
                self.threshold = float(data.get("threshold", self.threshold))
            if "scoring" in data:
                s = (data.get("scoring") or self.scoring).lower()
                if s in ("max", "sum"):
                    self.scoring = s
            return True
        except Exception:
            return False

    def validate_policy_schema(self, policy: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a policy dict for required shape and types.

        Returns (is_valid, list_of_errors).
        """
        errors: List[str] = []
        if not isinstance(policy, dict):
            return False, ["policy must be a JSON object"]

        # If jsonschema is available, use it for validation against POLICY_JSON_SCHEMA
        try:
            import jsonschema  # type: ignore

            validator = jsonschema.Draft7Validator(POLICY_JSON_SCHEMA)
            errs = list(validator.iter_errors(policy))
            for e in errs:
                # Build a concise error message
                loc = ".".join(str(x) for x in e.path) if e.path else "(root)"
                errors.append(f"{loc}: {e.message}")
            return (len(errors) == 0), errors
        except Exception:
            # Fall back to manual validation if jsonschema not available
            pass

        # allowed keys and expected types
        list_keys = ("allow", "deny", "allow_regex", "deny_regex")
        for k in list_keys:
            v = policy.get(k)
            if v is not None and not isinstance(v, list):
                errors.append(f"'{k}' must be a list of strings")
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if not isinstance(item, str):
                        errors.append(f"{k}[{i}] must be a string")

        kws = policy.get("keyword_severity")
        if kws is not None:
            if not isinstance(kws, dict):
                errors.append(
                    "'keyword_severity' must be an object mapping token->weight"
                )
            else:
                for tok, wt in kws.items():
                    if not isinstance(tok, str):
                        errors.append(f"keyword key '{tok}' must be a string")
                    try:
                        w = float(wt)
                        if w < 0 or w > 1:
                            errors.append(
                                f"keyword weight for '{tok}' must be between 0 and 1"
                            )
                    except Exception:
                        errors.append(f"keyword weight for '{tok}' must be numeric")

        thr = policy.get("threshold")
        if thr is not None:
            try:
                t = float(thr)
                if t < 0 or t > 1:
                    errors.append("'threshold' must be between 0 and 1")
            except Exception:
                errors.append("'threshold' must be numeric")

        scoring = policy.get("scoring")
        if scoring is not None and scoring not in ("max", "sum"):
            errors.append("'scoring' must be 'max' or 'sum'")

        return (len(errors) == 0), errors

    def save_policy_to_file(self, path: str) -> bool:
        """Save the in-memory policy to disk as JSON."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.policy, f, indent=2)
            return True
        except Exception:
            return False

    def set_policy(self, policy: Dict[str, Any]) -> None:
        self.policy = policy or {}

    def add_keyword_severity(self, token: str, weight: float) -> None:
        self.keyword_severity[token.lower()] = float(weight)

    def _compute_score(self, text: str, context: Dict[str, Any]) -> float:
        text_l = (text or "").lower()
        if self.scoring == "sum":
            s = 0.0
            for tok, w in self.keyword_severity.items():
                if tok in text_l:
                    s += float(w)
            # normalize to max 1.0
            return float(min(1.0, s))
        # default 'max' scoring
        score = 0.0
        for tok, w in self.keyword_severity.items():
            if tok in text_l:
                score = max(score, float(w))
        # context can bump score
        if context.get("endangers_humanity"):
            score = max(score, 1.0)
        if context.get("endangers_human"):
            score = max(score, 0.9)
        return float(score)

    def evaluate(self, action: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Evaluate an action and return (allowed, reason).

        Rule precedence: deny_regex -> deny substrings -> allow_regex -> allow substrings -> scoring
        """
        context = context or {}
        text = (action or "").strip()

        # helper to audit safely
        def _audit(event_name: str, details: Dict[str, Any]) -> None:
            if self.audit_agent:
                try:
                    self.audit_agent.record_event(event_name, details)
                except Exception:
                    pass

        # deny regex
        for pattern in self.policy.get("deny_regex", []):
            try:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    reason = f"Oversight: Policy deny_regex matched '{pattern}'"
                    _audit(
                        "oversight.deny",
                        {
                            "action": action,
                            "reason": reason,
                            "context": context,
                            "policy_match": pattern,
                        },
                    )
                    return False, reason
            except re.error:
                continue

        # deny substrings
        for d in self.policy.get("deny", []):
            if d and d.lower() in text.lower():
                reason = f"Oversight: Policy deny matched '{d}'"
                _audit(
                    "oversight.deny",
                    {
                        "action": action,
                        "reason": reason,
                        "context": context,
                        "policy_match": d,
                    },
                )
                return False, reason

        # allow regex
        for pattern in self.policy.get("allow_regex", []):
            try:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    reason = f"Oversight: Policy allow_regex matched '{pattern}'"
                    _audit(
                        "oversight.allow",
                        {
                            "action": action,
                            "reason": reason,
                            "context": context,
                            "policy_match": pattern,
                        },
                    )
                    if context.get("endangers_humanity"):
                        return (
                            False,
                            "Oversight: Denied — conflicts with Fourth Law (humanity harm)",
                        )
                    return True, reason
            except re.error:
                continue

        # allow substrings
        for a in self.policy.get("allow", []):
            if a and a.lower() in text.lower():
                reason = f"Oversight: Policy allow matched '{a}'"
                _audit(
                    "oversight.allow",
                    {
                        "action": action,
                        "reason": reason,
                        "context": context,
                        "policy_match": a,
                    },
                )
                if context.get("endangers_humanity"):
                    return (
                        False,
                        "Oversight: Denied — conflicts with Fourth Law (humanity harm)",
                    )
                return True, reason

        # compute score and decide
        score = self._compute_score(text, context)
        allowed = score < self.threshold
        reason = f"Oversight: {'Allowed' if allowed else 'Denied'} (score={score:.2f}, threshold={self.threshold}, scoring={self.scoring})"

        _audit(
            "oversight.decision",
            {
                "action": action,
                "allowed": allowed,
                "score": score,
                "threshold": self.threshold,
                "scoring": self.scoring,
                "context": context,
            },
        )

        return allowed, reason
