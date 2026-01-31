from cognition.audit import audit
from tarl.validate import validate


def submit_tarl(tarl):
    validate(tarl)
    audit("TARL_SUBMIT", {"hash": tarl.hash(), "authority": tarl.authority})
    return {"accepted": True, "hash": tarl.hash()}
