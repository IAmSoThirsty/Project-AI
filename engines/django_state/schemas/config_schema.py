"""Configuration schema for Django State Engine.

Defines configuration parameters for irreversibility laws, thresholds,
and engine behavior.
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IrreversibilityConfig:
    """Configuration for irreversibility laws."""

    # Trust decay parameters
    trust_decay_rate: float = 0.001  # Per tick decay
    trust_recovery_limit: float = 0.9  # Maximum recovery after damage
    betrayal_trust_impact: float = 0.15  # Trust loss per betrayal
    betrayal_ceiling_reduction: float = 0.1  # Permanent ceiling reduction

    # Kindness singularity
    kindness_decay_rate: float = 0.0005
    kindness_singularity_threshold: float = 0.2
    kindness_cooperation_boost: float = 0.02

    # Legitimacy erosion
    legitimacy_decay_rate: float = 0.0008
    legitimacy_recovery_limit: float = 0.85
    broken_promise_impact: float = 0.08
    institutional_failure_impact: float = 0.12

    # Moral injury accumulation
    moral_injury_decay_rate: float = 0.0002  # Very slow healing
    moral_injury_threshold: float = 0.85  # Critical threshold
    violation_severity_base: float = 0.05

    # Epistemic confidence
    epistemic_decay_rate: float = 0.0004
    manipulation_impact: float = 0.1
    epistemic_collapse_threshold: float = 0.2

    # Betrayal probability function parameters
    betrayal_prob_base: float = 0.01
    betrayal_prob_trust_factor: float = 0.15
    betrayal_prob_legitimacy_factor: float = 0.10
    betrayal_prob_moral_factor: float = 0.12

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "trust": {
                "decay_rate": self.trust_decay_rate,
                "recovery_limit": self.trust_recovery_limit,
                "betrayal_impact": self.betrayal_trust_impact,
                "ceiling_reduction": self.betrayal_ceiling_reduction,
            },
            "kindness": {
                "decay_rate": self.kindness_decay_rate,
                "singularity_threshold": self.kindness_singularity_threshold,
                "cooperation_boost": self.kindness_cooperation_boost,
            },
            "legitimacy": {
                "decay_rate": self.legitimacy_decay_rate,
                "recovery_limit": self.legitimacy_recovery_limit,
                "broken_promise_impact": self.broken_promise_impact,
                "institutional_failure_impact": self.institutional_failure_impact,
            },
            "moral_injury": {
                "decay_rate": self.moral_injury_decay_rate,
                "threshold": self.moral_injury_threshold,
                "violation_base": self.violation_severity_base,
            },
            "epistemic": {
                "decay_rate": self.epistemic_decay_rate,
                "manipulation_impact": self.manipulation_impact,
                "collapse_threshold": self.epistemic_collapse_threshold,
            },
            "betrayal_probability": {
                "base": self.betrayal_prob_base,
                "trust_factor": self.betrayal_prob_trust_factor,
                "legitimacy_factor": self.betrayal_prob_legitimacy_factor,
                "moral_factor": self.betrayal_prob_moral_factor,
            },
        }


@dataclass
class OutcomeThresholds:
    """Thresholds for outcome classification."""

    # Collapse thresholds
    kindness_singularity: float = 0.2
    trust_collapse: float = 0.15
    moral_injury_critical: float = 0.85
    legitimacy_failure: float = 0.1
    epistemic_collapse: float = 0.2

    # Outcome classification thresholds
    survivor_trust: float = 0.3
    survivor_legitimacy: float = 0.25
    martyr_kindness: float = 0.3
    martyr_moral: float = 0.6

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "collapse": {
                "kindness_singularity": self.kindness_singularity,
                "trust_collapse": self.trust_collapse,
                "moral_injury_critical": self.moral_injury_critical,
                "legitimacy_failure": self.legitimacy_failure,
                "epistemic_collapse": self.epistemic_collapse,
            },
            "outcome": {
                "survivor_trust": self.survivor_trust,
                "survivor_legitimacy": self.survivor_legitimacy,
                "martyr_kindness": self.martyr_kindness,
                "martyr_moral": self.martyr_moral,
            },
        }


@dataclass
class EngineConfig:
    """Complete configuration for Django State Engine."""

    # Simulation parameters
    simulation_name: str = "django_state_simulation"
    time_step: float = 1.0  # Duration of each tick
    max_ticks: int = 10000
    snapshot_interval: int = 100  # Take state snapshot every N ticks

    # Irreversibility laws
    irreversibility: IrreversibilityConfig = field(default_factory=IrreversibilityConfig)

    # Outcome thresholds
    thresholds: OutcomeThresholds = field(default_factory=OutcomeThresholds)

    # Collapse behavior
    enable_collapse_acceleration: bool = True
    collapse_acceleration_factor: float = 2.0

    # Red team configuration
    enable_red_team: bool = True
    black_vault_enabled: bool = True

    # Logging and output
    log_level: str = "INFO"
    export_state_history: bool = True
    export_event_log: bool = True

    # Validation
    enable_state_validation: bool = True
    enable_determinism_checks: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "simulation": {
                "name": self.simulation_name,
                "time_step": self.time_step,
                "max_ticks": self.max_ticks,
                "snapshot_interval": self.snapshot_interval,
            },
            "irreversibility": self.irreversibility.to_dict(),
            "thresholds": self.thresholds.to_dict(),
            "collapse": {
                "enable_acceleration": self.enable_collapse_acceleration,
                "acceleration_factor": self.collapse_acceleration_factor,
            },
            "red_team": {
                "enabled": self.enable_red_team,
                "black_vault_enabled": self.black_vault_enabled,
            },
            "output": {
                "log_level": self.log_level,
                "export_state_history": self.export_state_history,
                "export_event_log": self.export_event_log,
            },
            "validation": {
                "state_validation": self.enable_state_validation,
                "determinism_checks": self.enable_determinism_checks,
            },
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "EngineConfig":
        """Create configuration from dictionary."""
        simulation = config_dict.get("simulation", {})
        irrev_dict = config_dict.get("irreversibility", {})
        threshold_dict = config_dict.get("thresholds", {})
        collapse = config_dict.get("collapse", {})
        red_team = config_dict.get("red_team", {})
        output = config_dict.get("output", {})
        validation = config_dict.get("validation", {})

        # Build irreversibility config
        trust_conf = irrev_dict.get("trust", {})
        kindness_conf = irrev_dict.get("kindness", {})
        legitimacy_conf = irrev_dict.get("legitimacy", {})
        moral_conf = irrev_dict.get("moral_injury", {})
        epistemic_conf = irrev_dict.get("epistemic", {})
        betrayal_conf = irrev_dict.get("betrayal_probability", {})

        irreversibility = IrreversibilityConfig(
            trust_decay_rate=trust_conf.get("decay_rate", 0.001),
            trust_recovery_limit=trust_conf.get("recovery_limit", 0.9),
            betrayal_trust_impact=trust_conf.get("betrayal_impact", 0.15),
            betrayal_ceiling_reduction=trust_conf.get("ceiling_reduction", 0.1),
            kindness_decay_rate=kindness_conf.get("decay_rate", 0.0005),
            kindness_singularity_threshold=kindness_conf.get("singularity_threshold", 0.2),
            kindness_cooperation_boost=kindness_conf.get("cooperation_boost", 0.02),
            legitimacy_decay_rate=legitimacy_conf.get("decay_rate", 0.0008),
            legitimacy_recovery_limit=legitimacy_conf.get("recovery_limit", 0.85),
            broken_promise_impact=legitimacy_conf.get("broken_promise_impact", 0.08),
            institutional_failure_impact=legitimacy_conf.get("institutional_failure_impact", 0.12),
            moral_injury_decay_rate=moral_conf.get("decay_rate", 0.0002),
            moral_injury_threshold=moral_conf.get("threshold", 0.85),
            violation_severity_base=moral_conf.get("violation_base", 0.05),
            epistemic_decay_rate=epistemic_conf.get("decay_rate", 0.0004),
            manipulation_impact=epistemic_conf.get("manipulation_impact", 0.1),
            epistemic_collapse_threshold=epistemic_conf.get("collapse_threshold", 0.2),
            betrayal_prob_base=betrayal_conf.get("base", 0.01),
            betrayal_prob_trust_factor=betrayal_conf.get("trust_factor", 0.15),
            betrayal_prob_legitimacy_factor=betrayal_conf.get("legitimacy_factor", 0.10),
            betrayal_prob_moral_factor=betrayal_conf.get("moral_factor", 0.12),
        )

        # Build threshold config
        collapse_thresh = threshold_dict.get("collapse", {})
        outcome_thresh = threshold_dict.get("outcome", {})

        thresholds = OutcomeThresholds(
            kindness_singularity=collapse_thresh.get("kindness_singularity", 0.2),
            trust_collapse=collapse_thresh.get("trust_collapse", 0.15),
            moral_injury_critical=collapse_thresh.get("moral_injury_critical", 0.85),
            legitimacy_failure=collapse_thresh.get("legitimacy_failure", 0.1),
            epistemic_collapse=collapse_thresh.get("epistemic_collapse", 0.2),
            survivor_trust=outcome_thresh.get("survivor_trust", 0.3),
            survivor_legitimacy=outcome_thresh.get("survivor_legitimacy", 0.25),
            martyr_kindness=outcome_thresh.get("martyr_kindness", 0.3),
            martyr_moral=outcome_thresh.get("martyr_moral", 0.6),
        )

        return cls(
            simulation_name=simulation.get("name", "django_state_simulation"),
            time_step=simulation.get("time_step", 1.0),
            max_ticks=simulation.get("max_ticks", 10000),
            snapshot_interval=simulation.get("snapshot_interval", 100),
            irreversibility=irreversibility,
            thresholds=thresholds,
            enable_collapse_acceleration=collapse.get("enable_acceleration", True),
            collapse_acceleration_factor=collapse.get("acceleration_factor", 2.0),
            enable_red_team=red_team.get("enabled", True),
            black_vault_enabled=red_team.get("black_vault_enabled", True),
            log_level=output.get("log_level", "INFO"),
            export_state_history=output.get("export_state_history", True),
            export_event_log=output.get("export_event_log", True),
            enable_state_validation=validation.get("state_validation", True),
            enable_determinism_checks=validation.get("determinism_checks", True),
        )
