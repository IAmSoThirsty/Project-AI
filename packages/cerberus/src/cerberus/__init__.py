"""Project-AI cerberus public interface.

Canonical multi-agent runtime surface (agent, spawn constraints, lockdown)
plus the Cerberus Guard Bot port from ``IAmSoThirsty/Cerberus`` (guardians,
hub coordinator, settings, structured logging). Importing this package has
no side effects; call :func:`cerberus.logging_config.configure_logging`
explicitly to set up logging.
"""

from cerberus.agent import (
    AGENT_STATE_KEY,
    ALLOWED_AGENT_STATES,
    ALLOWED_ROLES,
    CerberusAgent,
    CerberusAgentError,
)
from cerberus.config import (
    CerberusConfigError,
    CerberusSettings,
    get_settings,
    reset_settings,
    set_settings,
)
from cerberus.guardians import (
    Guardian,
    HeuristicGuardian,
    PatternGuardian,
    StatisticalGuardian,
    StrictGuardian,
    ThreatLevel,
    ThreatReport,
)
from cerberus.hub import HubCoordinator
from cerberus.lockdown import (
    ALLOWED_LOCKDOWN_REASONS,
    ALLOWED_LOCKDOWN_STATES,
    LOCKDOWN_ACTIVE,
    LOCKDOWN_ARMED,
    LOCKDOWN_REASON_KEY,
    LOCKDOWN_RELEASED,
    LOCKDOWN_STATE_KEY,
    LockdownController,
    LockdownError,
    LockdownTrigger,
    default_lockdown_trigger,
)
from cerberus.spawn_constraints import (
    ALLOWED_AGENT_TYPES,
    SPAWN_HISTORY_KEY,
    SPAWN_STATE_KEY,
    SpawnConstraintError,
    SpawnConstraints,
    SpawnPolicy,
    default_spawn_policy,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "AGENT_STATE_KEY",
    "ALLOWED_AGENT_STATES",
    "ALLOWED_AGENT_TYPES",
    "ALLOWED_LOCKDOWN_REASONS",
    "ALLOWED_LOCKDOWN_STATES",
    "ALLOWED_ROLES",
    "LOCKDOWN_ACTIVE",
    "LOCKDOWN_ARMED",
    "LOCKDOWN_REASON_KEY",
    "LOCKDOWN_RELEASED",
    "LOCKDOWN_STATE_KEY",
    "SPAWN_HISTORY_KEY",
    "SPAWN_STATE_KEY",
    "CerberusAgent",
    "CerberusAgentError",
    "CerberusConfigError",
    "CerberusSettings",
    "Guardian",
    "HeuristicGuardian",
    "HubCoordinator",
    "LockdownController",
    "LockdownError",
    "LockdownTrigger",
    "PatternGuardian",
    "SpawnConstraintError",
    "SpawnConstraints",
    "SpawnPolicy",
    "StatisticalGuardian",
    "StrictGuardian",
    "ThreatLevel",
    "ThreatReport",
    "default_lockdown_trigger",
    "default_spawn_policy",
    "get_settings",
    "reset_settings",
    "set_settings",
]
