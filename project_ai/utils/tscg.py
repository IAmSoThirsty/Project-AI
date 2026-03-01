import re
from typing import Any


class TSCG:
    """
    Thirsty's Symbolic Compression Grammar (TSCG) - Python Implementation
    Used for compressed execution tracing and governance representation.
    """

    VERSION = "1.0"

    SYMBOLS = {
        "SEL": "Selection pressure",
        "COG": "Cognition (proposal only)",
        "Δ": "Mutation proposal",
        "Δ_NT": "Non-trivial mutation",
        "SHD": "Deterministic shadow",
        "INV": "Invariant engine",
        "CAP": "Capability authorization",
        "QRM": "Quorum",
        "COM": "Commit canonical",
        "ANC": "Anchor extension",
        "RFX": "Reflex containment",
        "ESC": "Escalation ladder",
        "SAFE": "SAFE-HALT",
        "MUT": "Mutation control law",
        "LED": "Ledger",
        "ING": "Ingress",
        "Ψ": "Volition (Independent Goal)",
        "Ι": "Identity (Persistent Totem)",
        "Ε": "Ethics (Moral Codex)",
    }

    OPERATORS = {
        "→": "Sequential pipeline",
        "∧": "Logical AND",
        "∨": "Logical OR",
        "¬": "Negation",
        "⊣": "Constrains / guards",
        "||": "Parallel / independent planes",
        ":=": "Definition",
        "=": "Equality",
        "∈": "Membership",
        "≥": "Threshold",
        "<": "Inequality",
        "⊻": "Sovereign Choice (Irreversible)",
    }

    # Reverse mapping for encoding
    SEMANTIC_TO_SYMBOL = {v: k for k, v in SYMBOLS.items()}


def get_symbol(semantic: str) -> str:
    return TSCG.SEMANTIC_TO_SYMBOL.get(semantic, semantic)


def get_semantic(symbol: str) -> str:
    return TSCG.SYMBOLS.get(symbol, symbol)


class TSCGEncoder:
    def encode_term(
        self,
        name: str,
        parameters: list[str] | None = None,
        classes: list[str] | None = None,
    ) -> str:
        symbol = get_symbol(name)
        result = symbol

        if classes:
            result += f"[{','.join(classes)}]"

        if parameters:
            result += f"({','.join(parameters)})"

        return result

    def encode_flow(self, steps: list[str | dict[str, Any]]) -> str:
        encoded = []
        for step in steps:
            if isinstance(step, str):
                encoded.append(step)
            else:
                encoded.append(
                    self.encode_term(
                        step.get("name", ""),
                        step.get("parameters"),
                        step.get("classes"),
                    )
                )
        return " ".join(encoded)


class TSCGDecoder:
    def decode_term(self, symbolic_term: str) -> dict[str, Any]:
        # Handle parameters (...)
        params = []
        match_params = re.search(r"\((.*?)\)", symbolic_term)
        if match_params:
            params = [p.strip() for p in match_params.group(1).split(",")]
            symbolic_term = symbolic_term.replace(match_params.group(0), "")

        # Handle classes [...]
        classes = []
        match_classes = re.search(r"\[(.*?)\]", symbolic_term)
        if match_classes:
            classes = [c.strip() for c in match_classes.group(1).split(",")]
            symbolic_term = symbolic_term.replace(match_classes.group(0), "")

        return {
            "name": get_semantic(symbolic_term.strip()),
            "parameters": params,
            "classes": classes,
        }

    def decode_flow(self, expression: str) -> list[str | dict[str, Any]]:
        tokens = expression.split(" ")
        steps = []
        operators = ["→", "∧", "∨", "||", "¬", ":=", "⊣", "=", "∈", "≥", "<", "⊻"]

        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if token in operators:
                steps.append(token)
            else:
                steps.append(self.decode_term(token))
        return steps
