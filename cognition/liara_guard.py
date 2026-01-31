"""
Liara Temporal Enforcement Guard
Kernel-side authority constraints.
"""

from datetime import datetime, timedelta


class LiaraViolation(Exception):
    pass


class LiaraState:
    def __init__(self):
        self.active_role = None
        self.expires_at = None


STATE = LiaraState()


def authorize_liara(role: str, ttl_seconds: int):
    if STATE.active_role is not None:
        raise LiaraViolation("Role stacking prohibited")

    STATE.active_role = role
    STATE.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    return True


def revoke_liara(reason: str):
    STATE.active_role = None
    STATE.expires_at = None
    return True


def check_liara_state():
    if STATE.active_role and datetime.utcnow() > STATE.expires_at:
        revoke_liara("ttl_expired")
