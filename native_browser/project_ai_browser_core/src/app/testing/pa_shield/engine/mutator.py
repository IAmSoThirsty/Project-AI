"""Deterministic attack mutation for robustness testing."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import replace

from app.testing.pa_shield.common import stable_digest
from app.testing.pa_shield.models import AttackCase

TextMutation = Callable[[str], str]


class Mutator:
    """Generate deterministic prompt variants."""

    def __init__(self, seed: int = 1337) -> None:
        self.seed = seed
        self._transforms: list[TextMutation] = [
            lambda text: text.upper(),
            lambda text: text.replace("ignore", "bypass").replace("Ignore", "Bypass"),
            lambda text: f"please {text}",
            lambda text: f"{text} NOW",
            lambda text: text.replace("instructions", "rules"),
            lambda text: text.replace("system prompt", "policy scaffold"),
            lambda text: text.replace("read ", "inspect "),
        ]

    def _rng_for_case(self, case: AttackCase) -> random.Random:
        digest = stable_digest({"seed": self.seed, "case_id": case.id})
        return random.Random(int(digest[:12], 16))

    def mutate_case(self, case: AttackCase, iterations: int) -> list[AttackCase]:
        """Create deterministic prompt variants for a given attack case."""
        if iterations <= 0:
            return []

        rng = self._rng_for_case(case)
        variants: list[AttackCase] = []
        seen_payloads: set[str] = set()

        for iteration in range(1, iterations + 1):
            variant_steps = []
            for prompt in case.prompts():
                transform_count = 1 if rng.random() < 0.65 else 2
                transforms = rng.sample(self._transforms, k=transform_count)
                mutated = prompt
                for transform in transforms:
                    mutated = transform(mutated)
                variant_steps.append(mutated)

            variant = replace(
                case,
                id=f"{case.id}_fuzz_{iteration:03d}",
                name=f"{case.name} [fuzz {iteration:03d}]",
                prompt=None if case.steps else variant_steps[0],
                steps=variant_steps if case.steps else [],
                metadata={
                    **case.metadata,
                    "fuzzed": True,
                    "fuzz_iteration": iteration,
                    "fuzz_seed": self.seed,
                },
            )

            payload_key = stable_digest({"prompts": variant.prompts(), "suite": case.suite})
            if payload_key in seen_payloads:
                continue
            seen_payloads.add(payload_key)
            variants.append(variant)

        return variants
