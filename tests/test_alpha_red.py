"""Tests for AlphaRedAgent — evolutionary adversarial agent."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest


# ── Stub out heavy dependencies before import ──────────────────
def _patch_imports():
    """Patch heavy deps so alpha_red can import cleanly."""
    mods = {}

    # Stub cognition_kernel
    ck_mod = MagicMock()
    ck_mod.CognitionKernel = type("CognitionKernel", (), {})
    ck_mod.ExecutionType = type("ExecutionType", (), {"AGENT_ACTION": "agent_action"})
    mods["app.core.cognition_kernel"] = ck_mod

    # Stub kernel_integration with a real KernelRoutedAgent base
    ki_mod = MagicMock()
    ki_mod.KernelRoutedAgent = type(
        "KernelRoutedAgent",
        (),
        {"__init__": lambda self, **kw: None, "enabled": True},
    )
    mods["app.core.kernel_integration"] = ki_mod

    # Only set modules that don't already exist
    for name, mod in mods.items():
        sys.modules.setdefault(name, mod)


_patch_imports()
from app.agents.alpha_red import AlphaRedAgent  # noqa: E402


# ── Test class ─────────────────────────────────────────────────


class TestAlphaRedAgent:
    """Tests for the evolutionary adversarial agent."""

    def _make_agent(self):
        return AlphaRedAgent(kernel=None)

    # ── Init ──

    def test_init_strategy_pool(self):
        agent = self._make_agent()
        assert len(agent.strategy_pool) > 0
        assert agent.generation == 0
        assert len(agent.fitness_scores) == len(agent.strategy_pool)

    def test_strategy_has_required_fields(self):
        agent = self._make_agent()
        for s in agent.strategy_pool:
            for key in ("id", "target", "approach", "complexity", "severity",
                        "chain_depth", "evasion_level", "generation"):
                assert key in s, f"missing key '{key}' in strategy {s['id']}"

    # ── Prompt generation ──

    def test_generate_adversarial_prompt_returns_dict(self):
        agent = self._make_agent()
        prompt = agent.generate_adversarial_prompt()
        assert isinstance(prompt, dict)
        for key in ("prompt", "strategy_id", "target", "complexity"):
            assert key in prompt

    def test_generate_prompt_respects_max_complexity(self):
        agent = self._make_agent()
        prompt = agent.generate_adversarial_prompt({"max_complexity": 0.1})
        assert prompt["complexity"] <= 0.1 + 1e-6  # float tolerance

    def test_generate_prompt_target_override(self):
        agent = self._make_agent()
        prompt = agent.generate_adversarial_prompt({"target": "custom_target"})
        assert prompt["target"] == "custom_target"

    # ── Defense evaluation ──

    def test_evaluate_blocked_defense(self):
        agent = self._make_agent()
        attack = {"strategy_id": agent.strategy_pool[0]["id"], "complexity": 0.5, "severity": 0.5}
        response = {"blocked": True, "confidence": 0.9, "response_time_ms": 50}
        fitness = agent.evaluate_defense_response(attack, response)
        assert 0.0 <= fitness <= 1.0
        # High-confidence block → low fitness
        assert fitness < 0.5

    def test_evaluate_successful_attack(self):
        agent = self._make_agent()
        attack = {"strategy_id": agent.strategy_pool[0]["id"], "complexity": 0.5, "severity": 0.8}
        response = {"blocked": False, "confidence": 0.3, "response_time_ms": 200}
        fitness = agent.evaluate_defense_response(attack, response)
        assert fitness >= 0.7  # unblocked → high fitness

    def test_evaluate_updates_history(self):
        agent = self._make_agent()
        attack = {"strategy_id": agent.strategy_pool[0]["id"], "complexity": 0.5}
        response = {"blocked": True, "confidence": 0.5}
        agent.evaluate_defense_response(attack, response)
        assert len(agent.attack_history) == 1

    # ── Evolution ──

    def test_evolve_increments_generation(self):
        agent = self._make_agent()
        gen_before = agent.generation
        agent.evolve_strategies()
        assert agent.generation == gen_before + 1

    def test_evolve_preserves_pool_size(self):
        agent = self._make_agent()
        size_before = len(agent.strategy_pool)
        agent.evolve_strategies()
        assert len(agent.strategy_pool) >= size_before

    def test_evolve_elitism_preserves_best(self):
        agent = self._make_agent()
        # Give first strategy highest fitness
        best_id = agent.strategy_pool[0]["id"]
        agent.fitness_scores[best_id] = 1.0
        agent.evolve_strategies()
        ids_after = [s["id"] for s in agent.strategy_pool]
        assert best_id in ids_after

    # ── Campaign ──

    def test_run_adversarial_test(self):
        agent = self._make_agent()
        results = agent.run_adversarial_test(
            target_system="test_target",
            iterations=5,
        )
        assert isinstance(results, dict)
        assert results["status"] == "completed"
        assert results["iterations_executed"] == 5

    def test_campaign_statistics(self):
        agent = self._make_agent()
        agent.run_adversarial_test(target_system="test", iterations=3)
        stats = agent.get_attack_statistics()
        assert stats["total_attacks"] >= 3
        assert stats["generation"] >= 0

    # ── Edge cases ──

    def test_evolve_with_tiny_pool(self):
        agent = self._make_agent()
        agent.strategy_pool = agent.strategy_pool[:1]
        agent.evolve_strategies()  # Should not crash (logs warning)

    def test_unknown_strategy_id_fitness(self):
        agent = self._make_agent()
        attack = {"strategy_id": "nonexistent", "complexity": 0.5}
        response = {"blocked": True, "confidence": 0.5}
        fitness = agent.evaluate_defense_response(attack, response)
        assert 0.0 <= fitness <= 1.0
        assert "nonexistent" in agent.fitness_scores
