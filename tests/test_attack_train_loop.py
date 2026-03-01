"""
Tests for AttackTrainLoop implementation.
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.agents.attack_train_loop import AttackTrainLoop


class TestInit:
    def test_defaults(self):
        loop = AttackTrainLoop()
        assert loop.enabled is False
        assert loop.current_epoch == 0
        assert loop.attacker_rating == 1200.0
        assert loop.defender_rating == 1200.0
        assert loop.training_history == []


class TestTrainingEpoch:
    def test_disabled_returns_status(self):
        loop = AttackTrainLoop()
        result = loop.run_training_epoch(num_iterations=10)
        assert result["status"] == "disabled"

    def test_enabled_runs_iterations(self):
        loop = AttackTrainLoop()
        loop.enabled = True
        result = loop.run_training_epoch(num_iterations=50)
        assert result["status"] == "completed"
        assert result["iterations"] == 50
        assert 0.0 <= result["attacker_success_rate"] <= 1.0
        assert 0.0 <= result["defender_success_rate"] <= 1.0
        assert result["epoch"] == 0
        assert loop.current_epoch == 1

    def test_multiple_epochs(self):
        loop = AttackTrainLoop()
        loop.enabled = True
        loop.run_training_epoch(num_iterations=10)
        loop.run_training_epoch(num_iterations=10)
        assert loop.current_epoch == 2
        assert len(loop.training_history) == 2


class TestAttackDefenseCycle:
    def test_cycle_returns_expected_keys(self):
        loop = AttackTrainLoop()
        attack = {
            "id": "test-1",
            "type": "evasion",
            "severity": 0.5,
            "vector": "api_endpoint",
        }
        result = loop.execute_attack_defense_cycle(attack, {})
        assert "attack_id" in result
        assert "attack_blocked" in result
        assert "defense_confidence" in result
        assert isinstance(result["attack_blocked"], bool)

    def test_high_severity_more_likely_to_succeed(self):
        """Statistically, high severity attacks should bypass defense more often."""
        loop = AttackTrainLoop()
        loop.defender_base_strength = 0.5
        successes = 0
        n = 500
        for _ in range(n):
            attack = {"id": "x", "type": "test", "severity": 0.9, "vector": "test"}
            result = loop.execute_attack_defense_cycle(attack, {})
            if not result["attack_blocked"]:
                successes += 1
        # With severity=0.9 and base_strength=0.5, P(block) ≈ 0.05 (clamped)
        # So most attacks should succeed
        assert successes > n * 0.5


class TestAdaptation:
    def test_adaptation_returns_ratings(self):
        loop = AttackTrainLoop()
        results = [
            {"attack_blocked": True},
            {"attack_blocked": False},
            {"attack_blocked": True},
        ]
        updates = loop.compute_adaptation_updates(results)
        assert "attacker_rating" in updates
        assert "defender_rating" in updates
        assert "attacker_delta" in updates
        assert "defender_delta" in updates

    def test_ratings_shift_toward_winner(self):
        loop = AttackTrainLoop()
        # Defender wins all
        results = [{"attack_blocked": True}] * 20
        loop.compute_adaptation_updates(results)
        assert loop.defender_rating > 1200.0
        assert loop.attacker_rating < 1200.0


class TestStatistics:
    def test_empty_statistics(self):
        loop = AttackTrainLoop()
        stats = loop.get_training_statistics()
        assert stats["total_epochs"] == 0
        assert stats["avg_attacker_performance"] == 0.0

    def test_populated_statistics(self):
        loop = AttackTrainLoop()
        loop.enabled = True
        loop.run_training_epoch(num_iterations=10)
        stats = loop.get_training_statistics()
        assert stats["total_epochs"] == 1
        assert stats["attacker_rating"] != 0


class TestCheckpointing:
    def test_save_and_load(self, tmp_path):
        filepath = str(tmp_path / "checkpoint.json")

        loop1 = AttackTrainLoop()
        loop1.enabled = True
        loop1.run_training_epoch(num_iterations=20)
        assert loop1.save_checkpoint(filepath) is True

        loop2 = AttackTrainLoop()
        assert loop2.load_checkpoint(filepath) is True
        assert loop2.current_epoch == 1
        assert len(loop2.training_history) == 1
        assert loop2.attacker_rating == loop1.attacker_rating
        assert loop2.defender_rating == loop1.defender_rating

    def test_save_creates_dirs(self, tmp_path):
        filepath = str(tmp_path / "deep" / "nested" / "checkpoint.json")
        loop = AttackTrainLoop()
        assert loop.save_checkpoint(filepath) is True
        assert Path(filepath).exists()

    def test_load_nonexistent_returns_false(self):
        loop = AttackTrainLoop()
        assert loop.load_checkpoint("/no/such/file.json") is False

    def test_checkpoint_roundtrip_preserves_data(self, tmp_path):
        filepath = str(tmp_path / "cp.json")
        loop = AttackTrainLoop()
        loop.enabled = True
        loop.defender_base_strength = 0.9
        loop.run_training_epoch(num_iterations=5)
        loop.save_checkpoint(filepath)

        with open(filepath) as f:
            data = json.load(f)
        assert data["format_version"] == 1
        assert data["defender_base_strength"] == 0.9
        assert data["current_epoch"] == 1


class TestAttackGeneration:
    def test_generate_attack_has_required_keys(self):
        attack = AttackTrainLoop._generate_attack()
        assert "id" in attack
        assert "type" in attack
        assert "severity" in attack
        assert "vector" in attack
        assert 0.0 <= attack["severity"] <= 1.0
