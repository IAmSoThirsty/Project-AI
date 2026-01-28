from cognition.violations import attempted_violation

def hydra_check(expansion_attempt: bool, context: str):
    if expansion_attempt:
        attempted_violation("HYDRA_EFFECT", context)
        raise RuntimeError("Hydra Effect blocked")
