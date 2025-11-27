"""Explainability agent: format and enrich model explainability outputs."""

from typing import Any, Dict, List, Tuple


class ExplainabilityAgent:
    """Helpers for formatting and summarizing model explainability outputs."""

    def __init__(self) -> None:
        pass

    def explain(
        self, model_explain: List[Tuple[str, float]], top_n: int = 10
    ) -> Dict[str, Any]:
        """Return a structured explainability summary.

        Input is expected as list of (token, weight) tuples. Output contains a ranked
        list and a simple normalized score mapping.
        """
        ranked = model_explain[:top_n]
        total_abs = sum(abs(w) for _, w in ranked) or 1.0
        normalized = [(tok, float(w), float(w) / total_abs) for tok, w in ranked]
        return {
            "top": [{"token": tok, "weight": w, "norm": n} for tok, w, n in normalized],
            "top_n": len(ranked),
        }
