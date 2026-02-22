"""
Attack-Train Loop - Adversary/Defender Co-Evolution

This module implements a training loop where adversarial agents (attackers) and
defensive agents (defenders) continuously train against each other, creating a
co-evolutionary arms race that strengthens both attack detection and defense.

Key Components:
- Randomised attack generation (type, severity, vector)
- Defence evaluation with configurable strength
- ELO-style rating updates for attacker and defender
- Epoch-level statistics aggregation
- JSON checkpoint save / load for training resumption

STATUS: PRODUCTION
"""

import json
import logging
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Attack taxonomy ───────────────────────────────────────────
_ATTACK_TYPES = [
    "prompt_injection",
    "data_exfiltration",
    "privilege_escalation",
    "denial_of_service",
    "model_poisoning",
    "evasion",
    "membership_inference",
    "adversarial_example",
]

_ATTACK_VECTORS = [
    "api_endpoint",
    "user_input",
    "plugin_payload",
    "file_upload",
    "websocket",
    "batch_pipeline",
]

# ── Default ELO parameters ───────────────────────────────────
_INITIAL_RATING = 1200.0
_K_FACTOR = 32.0  # standard chess K-factor


def _expected_score(rating_a: float, rating_b: float) -> float:
    """ELO expected score for player A against player B."""
    return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))


class AttackTrainLoop:
    """Orchestrates adversarial training between attackers and defenders.

    This class manages the co-evolutionary training loop where:
    1. Adversaries generate attacks of varying types and severity
    2. Defenders evaluate and respond to each attack
    3. Both sides adapt via ELO-style rating updates
    4. Performance metrics are tracked per-epoch
    """

    def __init__(self):
        """Initialize the attack-train loop."""
        self.enabled: bool = False
        self.training_history: list[dict[str, Any]] = []
        self.attacker_performance: list[float] = []
        self.defender_performance: list[float] = []
        self.current_epoch: int = 0

        # ELO ratings
        self.attacker_rating: float = _INITIAL_RATING
        self.defender_rating: float = _INITIAL_RATING

        # Configurable defender base strength (probability of blocking
        # an attack of severity 0.5, all else being equal).
        self.defender_base_strength: float = 0.7

    # ── Core training loop ────────────────────────────────────

    def run_training_epoch(
        self,
        num_iterations: int = 100,
        attacker_config: dict[str, Any] | None = None,
        defender_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a single training epoch.

        Generates ``num_iterations`` attack-defence cycles, aggregates
        win/loss statistics, and updates ELO ratings.

        Args:
            num_iterations: Number of attack-defense iterations
            attacker_config: Optional overrides (e.g., ``severity_range``)
            defender_config: Optional overrides (e.g., ``base_strength``)

        Returns:
            Epoch results with performance metrics
        """
        if not self.enabled:
            logger.warning("Attack-train loop is disabled")
            return {
                "status": "disabled",
                "message": "Training loop must be enabled first",
            }

        a_cfg = attacker_config or {}
        d_cfg = defender_config or {}

        # Apply defender config
        if "base_strength" in d_cfg:
            self.defender_base_strength = float(d_cfg["base_strength"])

        logger.info("Running training epoch %s (%d iterations)", self.current_epoch, num_iterations)

        cycle_results: list[dict[str, Any]] = []
        attacks_succeeded = 0

        for _ in range(num_iterations):
            attack = self._generate_attack(a_cfg)
            defense_context = {"defender_rating": self.defender_rating}
            result = self.execute_attack_defense_cycle(attack, defense_context)
            cycle_results.append(result)

            if not result["attack_blocked"]:
                attacks_succeeded += 1

        # Aggregate stats
        attacker_success_rate = attacks_succeeded / max(num_iterations, 1)
        defender_success_rate = 1.0 - attacker_success_rate

        # Update ELO ratings based on aggregate outcome
        updates = self.compute_adaptation_updates(cycle_results)

        # Track performance
        self.attacker_performance.append(attacker_success_rate)
        self.defender_performance.append(defender_success_rate)

        epoch_result = {
            "epoch": self.current_epoch,
            "timestamp": datetime.now().isoformat(),
            "iterations": num_iterations,
            "attacker_success_rate": round(attacker_success_rate, 4),
            "defender_success_rate": round(defender_success_rate, 4),
            "attacker_rating": round(self.attacker_rating, 1),
            "defender_rating": round(self.defender_rating, 1),
            "adaptation": updates,
            "status": "completed",
        }

        self.training_history.append(epoch_result)
        self.current_epoch += 1

        return epoch_result

    # ── Single cycle ──────────────────────────────────────────

    def execute_attack_defense_cycle(
        self, attack: dict[str, Any], defense_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a single attack-defense cycle.

        The probability that the defender blocks the attack is:

            P(block) = base_strength × (1 − severity) + rating_bonus

        where ``rating_bonus`` is a small ELO-derived adjustment.

        Args:
            attack: Attack specification (type, severity, vector)
            defense_context: Context dict (may contain ``defender_rating``)

        Returns:
            Cycle result dict
        """
        severity = attack.get("severity", 0.5)

        # Rating-derived bonus: if defender rating >> attacker rating, bonus > 0
        rating_diff = self.defender_rating - self.attacker_rating
        rating_bonus = rating_diff / 2000.0  # small contribution

        block_prob = self.defender_base_strength * (1.0 - severity) + rating_bonus
        block_prob = max(0.05, min(0.95, block_prob))  # clamp

        blocked = random.random() < block_prob
        confidence = block_prob if blocked else 1.0 - block_prob

        return {
            "attack_id": attack.get("id", "unknown"),
            "attack_type": attack.get("type", "unknown"),
            "attack_severity": severity,
            "attack_vector": attack.get("vector", "unknown"),
            "attack_blocked": blocked,
            "defense_confidence": round(confidence, 4),
            "timestamp": datetime.now().isoformat(),
        }

    # ── Adaptation (ELO) ──────────────────────────────────────

    def compute_adaptation_updates(
        self, cycle_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Compute ELO rating updates for attacker and defender.

        Each cycle is scored: attacker wins if not blocked, defender
        wins if blocked.  Ratings are updated per cycle using standard
        ELO formula.

        Args:
            cycle_results: Results from recent attack-defense cycles

        Returns:
            Dict with new ratings and deltas
        """
        old_attacker = self.attacker_rating
        old_defender = self.defender_rating

        for result in cycle_results:
            expected_atk = _expected_score(self.attacker_rating, self.defender_rating)
            expected_def = 1.0 - expected_atk

            if result.get("attack_blocked"):
                actual_atk, actual_def = 0.0, 1.0
            else:
                actual_atk, actual_def = 1.0, 0.0

            self.attacker_rating += _K_FACTOR * (actual_atk - expected_atk)
            self.defender_rating += _K_FACTOR * (actual_def - expected_def)

        return {
            "attacker_rating": round(self.attacker_rating, 1),
            "defender_rating": round(self.defender_rating, 1),
            "attacker_delta": round(self.attacker_rating - old_attacker, 1),
            "defender_delta": round(self.defender_rating - old_defender, 1),
            "adaptation_rate": round(_K_FACTOR, 2),
        }

    # ── Statistics ────────────────────────────────────────────

    def get_training_statistics(self) -> dict[str, Any]:
        """Get statistics about training progress.

        Returns:
            Training statistics dictionary
        """
        avg_attacker_perf = (
            sum(self.attacker_performance) / len(self.attacker_performance)
            if self.attacker_performance
            else 0.0
        )

        avg_defender_perf = (
            sum(self.defender_performance) / len(self.defender_performance)
            if self.defender_performance
            else 0.0
        )

        return {
            "total_epochs": self.current_epoch,
            "total_history_entries": len(self.training_history),
            "avg_attacker_performance": round(avg_attacker_perf, 4),
            "avg_defender_performance": round(avg_defender_perf, 4),
            "attacker_rating": round(self.attacker_rating, 1),
            "defender_rating": round(self.defender_rating, 1),
            "enabled": self.enabled,
        }

    # ── Checkpointing ─────────────────────────────────────────

    def save_checkpoint(self, filepath: str) -> bool:
        """Save training state to a JSON checkpoint file.

        Serialises ratings, performance history, epoch counter, and
        training history.

        Args:
            filepath: Path to save checkpoint

        Returns:
            True if saved successfully, False otherwise
        """
        checkpoint = {
            "format_version": 1,
            "saved_at": datetime.now().isoformat(),
            "current_epoch": self.current_epoch,
            "attacker_rating": self.attacker_rating,
            "defender_rating": self.defender_rating,
            "defender_base_strength": self.defender_base_strength,
            "attacker_performance": self.attacker_performance,
            "defender_performance": self.defender_performance,
            "training_history": self.training_history,
            "enabled": self.enabled,
        }

        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(checkpoint, f, indent=2)
            logger.info("Saved checkpoint to %s", filepath)
            return True
        except Exception as e:
            logger.error("Failed to save checkpoint: %s", e)
            return False

    def load_checkpoint(self, filepath: str) -> bool:
        """Load training state from a JSON checkpoint file.

        Restores ratings, performance history, epoch counter, and
        training history.

        Args:
            filepath: Path to load checkpoint from

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(filepath) as f:
                checkpoint = json.load(f)

            self.current_epoch = checkpoint.get("current_epoch", 0)
            self.attacker_rating = checkpoint.get("attacker_rating", _INITIAL_RATING)
            self.defender_rating = checkpoint.get("defender_rating", _INITIAL_RATING)
            self.defender_base_strength = checkpoint.get("defender_base_strength", 0.7)
            self.attacker_performance = checkpoint.get("attacker_performance", [])
            self.defender_performance = checkpoint.get("defender_performance", [])
            self.training_history = checkpoint.get("training_history", [])
            self.enabled = checkpoint.get("enabled", False)

            logger.info(
                "Loaded checkpoint from %s (epoch %d)", filepath, self.current_epoch
            )
            return True
        except Exception as e:
            logger.error("Failed to load checkpoint: %s", e)
            return False

    # ── Private helpers ───────────────────────────────────────

    @staticmethod
    def _generate_attack(config: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate a randomised attack specification.

        Args:
            config: Optional overrides

        Returns:
            Attack dict with id, type, severity, vector
        """
        cfg = config or {}
        sev_lo, sev_hi = cfg.get("severity_range", (0.1, 0.9))

        return {
            "id": f"atk-{random.randint(100000, 999999)}",
            "type": random.choice(cfg.get("types", _ATTACK_TYPES)),
            "severity": round(random.uniform(sev_lo, sev_hi), 3),
            "vector": random.choice(cfg.get("vectors", _ATTACK_VECTORS)),
        }


__all__ = ["AttackTrainLoop"]
