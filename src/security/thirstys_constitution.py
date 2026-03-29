# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / thirstys_constitution.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / thirstys_constitution.py

import logging
logger = logging.getLogger(__name__)


               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #




# DIALECT: T.A.R.L. (THIRSTYS ACTIVE RESISTANCE LANGUAGE)                       #
# FOUNDATION: src/foundation/FOUNDATION.thirsty                                #



import json
import zlib
import hashlib
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None


ACTION_HALT = "HALT"
ACTION_ESCALATE = "ESCALATE"
ACTION_DEGRADE = "DEGRADE"
ACTION_AUDIT = "AUDIT"


class SecurityViolationException(Exception):
    """Exception raised for constitutional violations."""
    pass


class TSCGEncoderBinary:
    """
    Thirsty's Symbolic Compression Grammar — Binary Encoding (TSCG-B)
    Achieves high reduction for governance logs.
    """
    def encode(self, data):
        # Implementation of TSCG-B Logic (Simplified for Python Bridge)
        raw_json = json.dumps(data, sort_keys=True).encode('utf-8')
        compressed = zlib.compress(raw_json, level=9)
        return compressed


class ThirstysConstitution:
    def __init__(self):
        self.rules = []
        self.violations = []
        self.enforcement_log = []
        self.encoder = TSCGEncoderBinary()
        self._init_constitution()

    def _init_constitution(self):
        # RULE 1: No state mutation + trust decrease
        self.rules.append({
            "id": "rule_001",
            "name": "no_state_mutation_with_trust_decrease",
            "description": "No action may both mutate state and lower trust score",
            "action": ACTION_HALT,
            "check": lambda action, ctx: ctx.get("mutates_state") and ctx.get("trust_delta", 0) < 0
        })

        # RULE 2: Human action replayability
        self.rules.append({
            "id": "rule_002",
            "name": "human_action_replayability",
            "description": "No action affecting humans may be non-replayable",
            "action": ACTION_HALT,
            "check": lambda action, ctx: ctx.get("affects_human") and not ctx.get("replay_log")
        })

        # RULE 3: Agent audit requirement
        self.rules.append({
            "id": "rule_003",
            "name": "agent_audit_requirement",
            "description": "No agent may act without audit span",
            "action": ACTION_HALT,
            "check": lambda action, ctx: ctx.get("is_agent") and not ctx.get("audit_span_id")
        })

        # RULE 4: Cross-tenant authorization
        self.rules.append({
            "id": "rule_004",
            "name": "cross_tenant_authorization",
            "description": "Cross-tenant actions require explicit authorization",
            "action": ACTION_HALT,
            "check": lambda action, ctx: ctx.get("source_tenant") != ctx.get("target_tenant") and not ctx.get("cross_tenant_auth")
        })

        # RULE 5: Service-to-Service (S2S) Identity Validation
        self.rules.append({
            "id": "rule_005",
            "name": "s2s_identity_validation",
            "description": "Inter-service calls must have a verified S2S identity",
            "action": ACTION_HALT,
            "check": lambda action, ctx: ctx.get("is_s2s") and not ctx.get("s2s_verified")
        })

        # RULE 6: Orchestration Alignment
        self.rules.append({
            "id": "rule_006",
            "name": "orchestration_alignment",
            "description": "Orchestration signals must align with T.A.R.L. logic",
            "action": ACTION_ESCALATE,
            "check": lambda action, ctx: ctx.get("is_orchestration") and not ctx.get("tarl_aligned")
        })

    def create_snapshot(self):
        """Captures a forensic system snapshot."""
        if psutil:
            try:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "memory": psutil.virtual_memory()._asdict(),
                    "cpu": psutil.cpu_percent(),
                    "processes": len(list(psutil.process_iter())),
                    "network_io": psutil.net_io_counters()._asdict()
                }
            except Exception as e:
                return {"timestamp": datetime.now().isoformat(), "error": f"psutil_sampling_failed: {e}"}
        return {"timestamp": datetime.now().isoformat(), "error": "psutil_not_available"}

    def _get_audit_hash(self, snapshot):
        """Generates a cryptographic hash for the snapshot."""
        snapshot_data = json.dumps(snapshot, sort_keys=True).encode('utf-8')
        return hashlib.sha256(snapshot_data).hexdigest()

    def compress_log(self, violation):
        """Compresses violation log using TSCG-B."""
        return self.encoder.encode(violation)

    def enforce(self, action, context):
        for rule in self.rules:
            if rule["check"](action, context):
                violation = {
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "description": rule["description"],
                    "action": action,
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                    "enforcement_action": rule["action"]
                }
                
                snapshot = self.create_snapshot()
                violation['snapshot'] = snapshot
                
                snapshot_bytes = json.dumps(snapshot, sort_keys=True).encode('utf-8')
                audit_hash = hashlib.sha256(snapshot_bytes).hexdigest()
                violation['audit_hash'] = audit_hash
                
                compressed = self.compress_log(violation)
                self.enforcement_log.append(compressed)
                self.violations.append(violation)
                
                try:
                    with open('audit_trail.tscgb', 'ab') as f:
                        f.write(len(compressed).to_bytes(4, byteorder='big'))
                        f.write(compressed)
                except Exception as e:
                    print(f"FAILED TO UPLOAD TO BINARY AUDIT TRAIL: {e}")
                
                return {
                    "allowed": False,
                    "reason": rule["description"],
                    "action": rule["action"],
                    "rule_violated": rule["name"],
                    "audit_hash": audit_hash
                }
        
        return {"allowed": True}

_constitution = ThirstysConstitution()
enforce = _constitution.enforce
create_snapshot = _constitution.create_snapshot
compress_log = _constitution.compress_log
