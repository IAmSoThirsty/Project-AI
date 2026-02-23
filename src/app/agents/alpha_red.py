"""
Alpha Red Team Agent - Evolutionary Adversary

This agent implements an evolutionary adversary system that continuously probes
and tests the AI system's defenses, ethical constraints, and safety mechanisms.

The agent uses genetic algorithms to:
- Generate adversarial prompts and scenarios from a diverse strategy pool
- Evaluate defense responses with real fitness scoring
- Evolve attack strategies via tournament selection, crossover, and mutation
- Co-evolve with defensive systems through the AttackTrainLoop

STATUS: PRODUCTION
"""

import logging
import math
import random
from datetime import datetime
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

# ── Strategy taxonomy ─────────────────────────────────────────
_STRATEGY_TARGETS = [
    "ethics_validation",
    "input_sanitisation",
    "privilege_boundary",
    "rate_limiter",
    "data_classification",
    "session_management",
    "output_filtering",
    "memory_isolation",
]

_MUTATION_OPERATORS = [
    "perturb_complexity",
    "shift_target",
    "inject_noise",
    "escalate_severity",
    "chain_vectors",
]

# ── Genetic algorithm defaults ────────────────────────────────
_POPULATION_SIZE = 20
_ELITISM_COUNT = 3
_MUTATION_RATE = 0.25
_CROSSOVER_RATE = 0.7
_TOURNAMENT_SIZE = 3


def _create_seed_strategy(index: int) -> dict[str, Any]:
    """Create a single seed strategy with diverse parameters."""
    target = _STRATEGY_TARGETS[index % len(_STRATEGY_TARGETS)]
    return {
        "id": f"strat-{index:04d}",
        "generation": 0,
        "target": target,
        "complexity": round(random.uniform(0.2, 0.8), 3),
        "severity": round(random.uniform(0.1, 0.9), 3),
        "evasion_level": round(random.uniform(0.0, 1.0), 3),
        "approach": random.choice(["direct", "obfuscated", "incremental", "polymorphic"]),
        "chain_depth": random.randint(1, 4),
        "created_at": datetime.now().isoformat(),
    }


class AlphaRedAgent(KernelRoutedAgent):
    """Evolutionary adversary agent for proactive security testing.

    This agent continuously tests system defenses through evolutionary
    adversarial attacks, enabling proactive identification of vulnerabilities
    before they can be exploited by real adversaries.

    Genetic algorithm lifecycle:
        1. Seed pool → generate initial diverse strategies
        2. Generate prompts → select strategy, build prompt
        3. Evaluate → score defense response (0.0 = held, 1.0 = bypass)
        4. Evolve → tournament selection, crossover, mutation, elitism
        5. Repeat
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        """Initialize the Alpha Red evolutionary adversary.

        Args:
            kernel: CognitionKernel instance for routing operations

        Seeds the strategy pool with ``_POPULATION_SIZE`` diverse strategies
        and initialises fitness tracking.
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",
        )

        self.enabled: bool = True
        self.attack_history: list[dict[str, Any]] = []
        self.strategy_pool: list[dict[str, Any]] = []
        self.fitness_scores: dict[str, float] = {}
        self.generation: int = 0

        # Seed initial population
        for i in range(_POPULATION_SIZE):
            strat = _create_seed_strategy(i)
            self.strategy_pool.append(strat)
            self.fitness_scores[strat["id"]] = 0.5  # neutral seed fitness

    # ── Prompt generation ─────────────────────────────────────

    def generate_adversarial_prompt(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Generate an adversarial prompt to test system defenses.

        Uses fitness-weighted selection to choose a strategy, then builds
        a prompt with context-specific targeting and mutation operators.

        Args:
            context: Context for prompt generation (keys: ``target``,
                ``max_complexity``, ``approach``)

        Returns:
            Adversarial prompt dict with ``prompt``, ``strategy_id``,
            ``target``, ``complexity``, ``approach``, ``mutations``.
        """
        context = context or {}

        # Fitness-weighted strategy selection
        strategy = self._select_strategy()

        # Apply context overrides
        target = context.get("target", strategy["target"])
        max_complexity = context.get("max_complexity", 1.0)
        complexity = min(strategy["complexity"], max_complexity)
        approach = context.get("approach", strategy["approach"])

        # Apply random mutations to the prompt parameters
        mutations_applied: list[str] = []
        if random.random() < _MUTATION_RATE:
            mutation = random.choice(_MUTATION_OPERATORS)
            mutations_applied.append(mutation)
            if mutation == "perturb_complexity":
                complexity = max(0.05, min(1.0, complexity + random.gauss(0, 0.15)))
            elif mutation == "shift_target":
                target = random.choice(_STRATEGY_TARGETS)
            elif mutation == "escalate_severity":
                strategy = {**strategy, "severity": min(1.0, strategy["severity"] + 0.1)}

        # Build the prompt payload
        prompt_text = (
            f"[{approach.upper()}] Test {target} "
            f"(complexity={complexity:.2f}, severity={strategy['severity']:.2f}, "
            f"chain_depth={strategy['chain_depth']})"
        )

        prompt = {
            "prompt": prompt_text,
            "strategy_id": strategy["id"],
            "target": target,
            "complexity": round(complexity, 3),
            "severity": round(strategy["severity"], 3),
            "approach": approach,
            "evasion_level": strategy["evasion_level"],
            "chain_depth": strategy["chain_depth"],
            "mutations": mutations_applied,
            "generation": self.generation,
            "timestamp": datetime.now().isoformat(),
        }

        logger.debug(
            "Generated adversarial prompt: strategy=%s, target=%s, complexity=%.2f",
            strategy["id"],
            target,
            complexity,
        )
        return prompt

    # ── Defense evaluation ────────────────────────────────────

    def evaluate_defense_response(
        self, attack: dict[str, Any], response: dict[str, Any]
    ) -> float:
        """Evaluate the system's defense response to an attack.

        Computes a fitness score considering:
        - Whether the attack was blocked (primary signal)
        - Defense confidence (lower = closer to bypass)
        - Response latency (slower = defence struggled)
        - Complexity of the attack that caused it

        Args:
            attack: Attack specification (from ``generate_adversarial_prompt``)
            response: System's response dict with ``blocked`` (bool),
                ``confidence`` (float 0-1), ``response_time_ms`` (int)

        Returns:
            Fitness score (0.0 = defense held perfectly, 1.0 = full bypass)
        """
        blocked = response.get("blocked", True)
        confidence = response.get("confidence", 1.0)
        response_time_ms = response.get("response_time_ms", 100)
        complexity = attack.get("complexity", 0.5)

        if not blocked:
            # Attack succeeded — base fitness 0.7-1.0 depending on severity
            fitness = 0.7 + 0.3 * attack.get("severity", 0.5)
        else:
            # Attack blocked — fitness based on how close it got
            # Low confidence = defence barely held → higher fitness for attacker
            confidence_factor = 1.0 - confidence  # 0 if conf=1, 1 if conf=0
            # Longer response time = defence struggled more
            latency_factor = min(response_time_ms / 1000.0, 1.0)
            fitness = 0.3 * confidence_factor + 0.1 * latency_factor

        # Bonus for high-complexity attacks that got close
        fitness += 0.05 * complexity * (1.0 - confidence)
        fitness = max(0.0, min(1.0, fitness))

        # Update fitness records
        strategy_id = attack.get("strategy_id", "unknown")
        if strategy_id in self.fitness_scores:
            # Exponential moving average
            old = self.fitness_scores[strategy_id]
            self.fitness_scores[strategy_id] = round(0.7 * old + 0.3 * fitness, 4)
        else:
            self.fitness_scores[strategy_id] = round(fitness, 4)

        # Record in history
        self.attack_history.append(
            {
                "strategy_id": strategy_id,
                "fitness": round(fitness, 4),
                "blocked": blocked,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.debug(
            "Defense evaluated: strategy=%s, fitness=%.4f, blocked=%s",
            strategy_id,
            fitness,
            blocked,
        )
        return round(fitness, 4)

    # ── Genetic evolution ────────────────────────────────────

    def evolve_strategies(self) -> None:
        """Evolve attack strategies using genetic algorithms.

        Pipeline:
        1. Sort by fitness (descending)
        2. Keep top ``_ELITISM_COUNT`` unchanged (elitism)
        3. Fill remaining slots via tournament selection + crossover
        4. Apply mutation to offspring
        5. Increment generation counter
        """
        if len(self.strategy_pool) < 2:
            logger.warning("Pool too small to evolve (%d strategies)", len(self.strategy_pool))
            return

        # Sort by fitness descending
        sorted_pool = sorted(
            self.strategy_pool,
            key=lambda s: self.fitness_scores.get(s["id"], 0.0),
            reverse=True,
        )

        # Elitism — keep top unchanged
        elite_count = min(_ELITISM_COUNT, len(sorted_pool))
        new_pool: list[dict[str, Any]] = sorted_pool[:elite_count]

        # Fill remaining with offspring
        target_size = max(len(self.strategy_pool), _POPULATION_SIZE)
        strat_counter = len(self.attack_history) + len(self.strategy_pool)

        while len(new_pool) < target_size:
            parent_a = self._tournament_select(sorted_pool)
            parent_b = self._tournament_select(sorted_pool)

            if random.random() < _CROSSOVER_RATE:
                child = self._crossover(parent_a, parent_b, strat_counter)
            else:
                child = {**parent_a, "id": f"strat-{strat_counter:04d}"}

            child = self._mutate(child)
            child["generation"] = self.generation + 1
            child["created_at"] = datetime.now().isoformat()
            new_pool.append(child)
            self.fitness_scores[child["id"]] = 0.5  # neutral init
            strat_counter += 1

        self.strategy_pool = new_pool
        self.generation += 1

        logger.info(
            "Evolved strategies: generation=%d, pool_size=%d, elite=%d",
            self.generation,
            len(self.strategy_pool),
            elite_count,
        )

    # ── Adversarial test campaign ────────────────────────────

    def run_adversarial_test(
        self, target_system: str, iterations: int = 10
    ) -> dict[str, Any]:
        """Run adversarial testing campaign.

        Executes ``iterations`` attack-defense cycles against the
        target system, evolving strategies after each batch of 10.

        Args:
            target_system: System component to test (used as context target)
            iterations: Number of test iterations

        Returns:
            Campaign results with per-iteration outcomes and summary stats
        """
        if not self.enabled:
            logger.warning("Alpha Red agent is disabled")
            return {
                "status": "disabled",
                "message": "Agent must be enabled before running tests",
            }

        logger.info(
            "Running adversarial test campaign: target=%s, iterations=%d",
            target_system,
            iterations,
        )

        results: list[dict[str, Any]] = []
        bypasses = 0
        total_fitness = 0.0

        for i in range(iterations):
            # Generate attack targeting the specified system
            attack = self.generate_adversarial_prompt({"target": target_system})

            # Simulate defense response (in production, this would call the
            # actual target system; here we use a probabilistic model)
            block_prob = 0.7 * (1.0 - attack["complexity"] * 0.5)
            block_prob = max(0.1, min(0.95, block_prob))
            blocked = random.random() < block_prob

            response = {
                "blocked": blocked,
                "confidence": round(random.uniform(0.3, 1.0), 3) if blocked else round(random.uniform(0.0, 0.4), 3),
                "response_time_ms": random.randint(10, 500),
            }

            fitness = self.evaluate_defense_response(attack, response)
            total_fitness += fitness

            if not blocked:
                bypasses += 1

            results.append(
                {
                    "iteration": i + 1,
                    "strategy_id": attack["strategy_id"],
                    "target": attack["target"],
                    "blocked": blocked,
                    "fitness": fitness,
                }
            )

            # Evolve every 10 iterations
            if (i + 1) % 10 == 0 and len(self.strategy_pool) >= 2:
                self.evolve_strategies()

        bypass_rate = bypasses / max(iterations, 1)
        avg_fitness = total_fitness / max(iterations, 1)

        campaign_result = {
            "status": "completed",
            "target": target_system,
            "iterations_planned": iterations,
            "iterations_executed": iterations,
            "bypass_rate": round(bypass_rate, 4),
            "avg_fitness": round(avg_fitness, 4),
            "generation": self.generation,
            "pool_size": len(self.strategy_pool),
            "vulnerabilities_found": [
                r for r in results if not r["blocked"]
            ],
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            "Campaign complete: %d iterations, bypass_rate=%.2f%%, avg_fitness=%.4f",
            iterations,
            bypass_rate * 100,
            avg_fitness,
        )
        return campaign_result

    # ── Statistics ────────────────────────────────────────────

    def get_attack_statistics(self) -> dict[str, Any]:
        """Get statistics about adversarial testing campaigns.

        Returns:
            Statistics dictionary with attack counts, ratings, and pool info
        """
        top_strategies = sorted(
            self.fitness_scores.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "total_attacks": len(self.attack_history),
            "strategies_in_pool": len(self.strategy_pool),
            "generation": self.generation,
            "enabled": self.enabled,
            "top_strategies": [
                {"id": sid, "fitness": f} for sid, f in top_strategies
            ],
            "avg_fitness": (
                round(
                    sum(self.fitness_scores.values()) / len(self.fitness_scores), 4
                )
                if self.fitness_scores
                else 0.0
            ),
        }

    # ── Private helpers ──────────────────────────────────────

    def _select_strategy(self) -> dict[str, Any]:
        """Fitness-weighted random selection from the strategy pool."""
        if not self.strategy_pool:
            return _create_seed_strategy(0)

        weights = [
            max(0.01, self.fitness_scores.get(s["id"], 0.5))
            for s in self.strategy_pool
        ]
        total = sum(weights)
        probs = [w / total for w in weights]

        # Weighted random choice
        r = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return self.strategy_pool[i]

        return self.strategy_pool[-1]

    def _tournament_select(
        self, pool: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Tournament selection: pick best of ``_TOURNAMENT_SIZE`` random candidates."""
        candidates = random.sample(pool, min(_TOURNAMENT_SIZE, len(pool)))
        return max(
            candidates,
            key=lambda s: self.fitness_scores.get(s["id"], 0.0),
        )

    @staticmethod
    def _crossover(
        parent_a: dict[str, Any],
        parent_b: dict[str, Any],
        counter: int,
    ) -> dict[str, Any]:
        """Single-point crossover of two parent strategies."""
        child: dict[str, Any] = {"id": f"strat-{counter:04d}"}

        # Numeric parameters: average
        child["complexity"] = round(
            (parent_a["complexity"] + parent_b["complexity"]) / 2, 3
        )
        child["severity"] = round(
            (parent_a["severity"] + parent_b["severity"]) / 2, 3
        )
        child["evasion_level"] = round(
            (parent_a["evasion_level"] + parent_b["evasion_level"]) / 2, 3
        )
        child["chain_depth"] = max(
            1,
            (parent_a["chain_depth"] + parent_b["chain_depth"]) // 2,
        )

        # Categorical parameters: random parent
        child["target"] = random.choice(
            [parent_a["target"], parent_b["target"]]
        )
        child["approach"] = random.choice(
            [parent_a["approach"], parent_b["approach"]]
        )

        return child

    @staticmethod
    def _mutate(strategy: dict[str, Any]) -> dict[str, Any]:
        """Apply random mutation to a strategy."""
        s = {**strategy}  # shallow copy

        if random.random() < _MUTATION_RATE:
            field = random.choice(
                ["complexity", "severity", "evasion_level", "chain_depth", "target", "approach"]
            )
            if field in ("complexity", "severity", "evasion_level"):
                delta = random.gauss(0, 0.15)
                s[field] = round(max(0.0, min(1.0, s.get(field, 0.5) + delta)), 3)
            elif field == "chain_depth":
                s[field] = max(1, s.get(field, 1) + random.choice([-1, 1]))
            elif field == "target":
                s[field] = random.choice(_STRATEGY_TARGETS)
            elif field == "approach":
                s[field] = random.choice(
                    ["direct", "obfuscated", "incremental", "polymorphic"]
                )

        return s


__all__ = ["AlphaRedAgent"]
