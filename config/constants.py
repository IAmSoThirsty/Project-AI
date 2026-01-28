"""
Constants used throughout the Project AI system.
"""

# Actor Types
class ActorType:
    HUMAN = "human"
    AGENT = "agent"
    SYSTEM = "system"
    
    @classmethod
    def all(cls):
        return [cls.HUMAN, cls.AGENT, cls.SYSTEM]

# Action Types
class ActionType:
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    MUTATE = "mutate"
    
    @classmethod
    def all(cls):
        return [cls.READ, cls.WRITE, cls.EXECUTE, cls.MUTATE]

# Verdict Types
class VerdictType:
    ALLOW = "allow"
    DENY = "deny"
    DEGRADE = "degrade"
    
    @classmethod
    def all(cls):
        return [cls.ALLOW, cls.DENY, cls.DEGRADE]

# Pillar Names
class Pillar:
    GALAHAD = "Galahad"
    CERBERUS = "Cerberus"
    CODEX_DEUS = "CodexDeus"
    
    @classmethod
    def all(cls):
        return [cls.GALAHAD, cls.CERBERUS, cls.CODEX_DEUS]

# Risk Levels
class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def all(cls):
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL]

# HTTP Status Codes
class HttpStatus:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

# API Endpoints
class Endpoints:
    HEALTH = "/health"
    TARL = "/tarl"
    AUDIT = "/audit"
    INTENT = "/intent"
    EXECUTE = "/execute"

# Messages
class Messages:
    GOVERNANCE_DENIED = "Governance denied this request"
    INTENT_ACCEPTED = "Intent accepted under governance"
    EXECUTION_DENIED = "Execution denied by governance"
    EXECUTION_COMPLETED = "Execution completed under governance"
    NO_TARL_RULE = "No TARL rule – execution denied"
