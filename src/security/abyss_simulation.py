#                                            [2026-03-02 08:32]
#                                           Productivity: Active
"""
ABYSS ASYMMETRIC HYBRID SIMULATION ENGINE
Verification Architect (Abyss & Angler)

This module implements a combined simulation of the Asymmetric Security Framework,
integrating graph-based network topology, vector-based context similarity (Entropy-Relative Friction),
and Goblin Angler hybrid lures for hard isolation.
"""

import math
import os
import random
import sys

import networkx as nx

# Ensure src is in path for imports
sys.path.append(os.getcwd() + "/src")

try:
    from security.asymmetric_security import RFICalculator, SecurityContext
except ImportError:
    # Minimal fallback calculator if execution environment differs
    class SecurityContext:
        def __init__(self, user_id, action, dimensions):
            self.user_id = user_id
            self.action = action
            self.dimensions = dimensions

    class RFICalculator:
        def calculate(self, ctx):
            total_entropy = sum(ctx.dimensions.values())
            return 1.0 - (2.0**-total_entropy) if total_entropy > 0 else 0.0


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculates cosine similarity between two context vectors."""
    if not a or not b:
        return 0.0
    dot = sum(ai * bi for ai, bi in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(ai**2 for ai in a))
    norm_b = math.sqrt(sum(bi**2 for bi in b))
    return dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0


class AbyssAsymmetryHybrid:
    """
    Simulates an adaptive attacker against the Abyss Asymmetric Hybrid ecosystem.

    Includes:
    - Goblin Angler: Hidden lures that trigger Hard Isolation.
    - Information-Theoretic RFI: Entropy-based success probability.
    - Graph-Based PIVOT: Attackers can move to neighbors with similar context.
    """

    def __init__(self, network_size=30, num_lures=6, entropy_bits=64, seed=None):
        if seed is not None:
            random.seed(seed)

        self.network = nx.erdos_renyi_graph(network_size, 0.25)
        self.nodes = list(self.network.nodes)

        # Context vectors (for similarity/pivot logic)
        # Each node has a 3-dimensional context vector for spatial similarity
        self.node_vectors = {
            n: [random.uniform(0, 1) for _ in range(3)] for n in self.nodes
        }

        # Entropy Bits (Formal RFI calculation)
        # Base entropy bits per node, simulating variance in dimension quality
        self.node_entropies = {
            n: random.uniform(entropy_bits * 0.5, entropy_bits * 1.2)
            for n in self.nodes
        }

        # Goblin Angler Lures (Hidden from attacker)
        self.lures = set(random.sample(self.nodes, num_lures))
        self.sensor_certainty = dict.fromkeys(self.lures, 0.5)
        self.node_probe_counts = dict.fromkeys(self.nodes, 0)

        # Security Gateway Components
        self.rfi_calculator = RFICalculator()

        # Statistics
        self.breaches = 0
        self.lure_hits = 0
        self.quarantines = 0
        self.total_probes = 0

        # Attacker State
        self.known_success_nodes = []
        self.current_tuned_vector = None
        self.probed_nodes = set()

    def run_campaign(self, num_probes=25):
        """Simulates an attack campaign."""
        print(f"\n=== STARTING ABYSS HYBRID CAMPAIGN ({num_probes} Probes) ===")
        print(
            f"Network Size: {len(self.nodes)} | Lures (Goblin Angler): {len(self.lures)}"
        )

        for p in range(num_probes):
            if not self.network.nodes:
                print("All nodes quarantined or removed. Campaign ended early.")
                break

            self.total_probes += 1

            # Attacker Strategy: Adaptive Pivot
            target = self._select_target()
            self.probed_nodes.add(target)
            self.node_probe_counts[target] = self.node_probe_counts.get(target, 0) + 1

            print(
                f"Probe #{p + 1}: Targeting node {target} (Successes={self.breaches})"
            )

            # Defense Trigger: Goblin Angler
            if target in self.lures:
                self._handle_lure_hit(target)
                continue

            # Defense Trigger: Entropy-Based RFI Validation
            self._handle_real_node_attack(target)

        self._print_results()

    def _select_target(self) -> int:
        """Adaptive attacker targeting logic."""
        # If we have a tuned vector, target neighbors of successful breaches with similar vectors
        if self.current_tuned_vector and self.known_success_nodes:
            recent = self.known_success_nodes[-3:]
            candidates = set()
            for s in recent:
                if s in self.network:
                    candidates.update(self.network.neighbors(s))

            # Filter candidates that haven't been probed (or are still active)
            active_candidates = [
                c
                for c in candidates
                if c in self.network and c not in self.probed_nodes
            ]

            if active_candidates:
                # Rank by cosine similarity to our tuned exploit
                scored = [
                    (
                        c,
                        cosine_similarity(
                            self.current_tuned_vector, self.node_vectors[c]
                        ),
                    )
                    for c in active_candidates
                ]
                return max(scored, key=lambda x: x[1])[0]

        # Fallback to random unprobed node (or random node if all probed)
        unprobed = [n for n in self.network.nodes if n not in self.probed_nodes]
        return (
            random.choice(unprobed)
            if unprobed
            else random.choice(list(self.network.nodes))
        )

    def _handle_lure_hit(self, node):
        """Goblin Angler sensor and strike logic."""
        print("   -> ATTRACTED TO GOBLIN ANGLER LURE")
        # Increase sensor strength with each probe
        self.sensor_certainty[node] = min(
            1.0, self.sensor_certainty[node] + 0.15 * self.node_probe_counts[node]
        )

        if random.random() < self.sensor_certainty[node]:
            print(
                f"   -> GOBLIN ANGLER STRIKE! (Certainty: {self.sensor_certainty[node]:.2f})"
            )
            self.lure_hits += 1
            self._isolate_node(node)
        else:
            print(
                f"   -> Probe grazed lure undetected (Certainty: {self.sensor_certainty[node]:.2f})"
            )

    def _handle_real_node_attack(self, node):
        """Formal RFI and transferability logic."""
        # Calculate RFI for this node
        # Mocking a SecurityContext with the node's entropy bits
        ctx = SecurityContext(
            user_id="attacker",
            action="exploit",
            dimensions={"node_entropy": self.node_entropies[node]},
        )
        rfi = self.rfi_calculator.calculate(ctx)

        # Base survival probability (Tau)
        tau = 1.0 - rfi

        # Adaptation Factor: Similarity to current tuned vector
        similarity = 0.25  # Default low similarity if not tuned
        if self.current_tuned_vector:
            similarity = cosine_similarity(
                self.current_tuned_vector, self.node_vectors[node]
            )

        # Exploit Decay: Each successive transfer makes it harder (Temporal/Schema drift)
        decay = 0.85 ** len(self.known_success_nodes)

        # Final success probability
        success_prob = similarity * tau * decay
        success_prob = min(0.9, max(0.01, success_prob))

        if random.random() < success_prob:
            print(
                f"   -> BREACH SUCCESS (Sim={similarity:.2f}, Tau={tau:.10f}, Decay={decay:.2f})"
            )
            self.breaches += 1
            self.known_success_nodes.append(node)
            self.current_tuned_vector = self.node_vectors[node][:]
            self._isolate_node(node)  # Still isolate after breach to contain threat
        else:
            print(f"   -> BREACH FAILED (Prob={success_prob:.10f})")

    def _isolate_node(self, node):
        """Removes node from network (Hard Isolation)."""
        if node in self.network:
            print(f"   -> Hard Isolation: Node {node} removed from network topology.")
            self.network.remove_node(node)
            self.quarantines += 1
            if node in self.lures:
                self.lures.remove(node)

    def _print_results(self):
        """Prints final campaign results."""
        print("\n=== CAMPAIGN RESULTS ===")
        print(f"Total Probes: {self.total_probes}")
        print(f"Breach Successes: {self.breaches}")
        print(f"Goblin Angler Hits (Sensor Alerts): {self.lure_hits}")
        print(f"Total Quarantines (Containment): {self.quarantines}")

        tau_bar = self.breaches / self.total_probes if self.total_probes > 0 else 0
        print(f"Empirical Tau-Bar (τ̄): {tau_bar:.4f}")
        print(
            f"Structural Unfinishability Ratio: {1.0 / tau_bar if tau_bar > 0 else float('inf'):.2f}x cost increase"
        )
        print("========================")


if __name__ == "__main__":
    # Standard setup for verification (Scaling to 100 probes for full stress test)
    sim = AbyssAsymmetryHybrid(network_size=50, num_lures=12, entropy_bits=64, seed=42)
    sim.run_campaign(100)
