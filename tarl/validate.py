from tarl.core import TARL

ALLOWED_AUTHORITIES = {"Galahad", "Cerberus", "CodexDeus"}

def validate(t: TARL) -> None:
    if not t.intent or not t.scope:
        raise ValueError("Invalid TARL: intent and scope required")
    if t.authority not in ALLOWED_AUTHORITIES:
        raise ValueError("Invalid TARL authority")
