#                                           [2026-04-09 11:30]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L5: Behavioral Modeling Engine

Hidden Markov Model for adversarial behavior classification.
Hardened against memory exhaustion via bounded observation sequences.
"""

import logging
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger("SASE.L5.BehavioralModel")


class BehaviorState(Enum):
    """HMM behavioral states"""

    PASSIVE_RECON = "S0_PASSIVE_RECON"
    TOKEN_PROBE = "S1_TOKEN_PROBE"
    CREDENTIAL_USE = "S2_CREDENTIAL_USE"
    API_ENUMERATION = "S3_API_ENUMERATION"
    ESCALATION_ATTEMPT = "S4_ESCALATION_ATTEMPT"
    DORMANCY = "S5_DORMANCY"


@dataclass
class StateTransitionMatrix:
    """NxN state transition probabilities."""

    version: str
    states: list[BehaviorState]
    matrix: np.ndarray

    def __post_init__(self):
        n = len(self.states)
        if self.matrix.shape != (n, n):
            raise ValueError(f"Matrix must be {n}x{n}, got {self.matrix.shape}")
        for i in range(n):
            row_sum = np.sum(self.matrix[i])
            if not np.isclose(row_sum, 1.0):
                raise ValueError(f"Row {i} probabilities must sum to 1.0, got {row_sum}")


@dataclass
class EmissionProbabilities:
    """P(observation | state) matrix."""

    version: str
    states: list[BehaviorState]
    observations: list[str]
    matrix: np.ndarray

    def __post_init__(self):
        n_states = len(self.states)
        n_obs = len(self.observations)
        if self.matrix.shape != (n_states, n_obs):
            raise ValueError(f"Matrix must be {n_states}x{n_obs}, got {self.matrix.shape}")
        for i in range(n_states):
            row_sum = np.sum(self.matrix[i])
            if not np.isclose(row_sum, 1.0):
                raise ValueError(f"State {i} emissions must sum to 1.0, got {row_sum}")


class HiddenMarkovModel:
    """HMM for adversarial behavior inference."""

    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.states = list(BehaviorState)
        self.transitions = self._initialize_transitions()
        self.emissions = self._initialize_emissions()
        logger.info("L5 HMM initialized (version=%s)", version)

    def _initialize_transitions(self) -> StateTransitionMatrix:
        n = len(self.states)
        matrix = np.zeros((n, n))
        matrix[0] = [0.4, 0.3, 0.1, 0.1, 0.05, 0.05]  # Recon
        matrix[1] = [0.1, 0.3, 0.4, 0.1, 0.05, 0.05]  # Probe
        matrix[2] = [0.05, 0.1, 0.2, 0.5, 0.1, 0.05]  # Creds
        matrix[3] = [0.05, 0.1, 0.2, 0.3, 0.3, 0.05]  # API
        matrix[4] = [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]  # Escalate
        matrix[5] = [0.3, 0.2, 0.1, 0.1, 0.05, 0.25]  # Dormant
        return StateTransitionMatrix(version=self.version, states=self.states, matrix=matrix)

    def _initialize_emissions(self) -> EmissionProbabilities:
        observations = ["DNS_RESOLUTION", "HTTP_CALLBACK", "CREDENTIAL_MISUSE", "OAUTH_VALIDATION", 
                        "API_MISUSE", "WEBHOOK_INVOCATION", "SYNTHETIC_LEAK"]
        n_states = len(self.states)
        n_obs = len(observations)
        matrix = np.zeros((n_states, n_obs))
        matrix[0] = [0.4, 0.4, 0.05, 0.05, 0.05, 0.03, 0.02]
        matrix[1] = [0.2, 0.3, 0.3, 0.1, 0.05, 0.03, 0.02]
        matrix[2] = [0.05, 0.1, 0.5, 0.25, 0.05, 0.03, 0.02]
        matrix[3] = [0.05, 0.1, 0.1, 0.2, 0.4, 0.1, 0.05]
        matrix[4] = [0.1, 0.15, 0.2, 0.15, 0.2, 0.1, 0.1]
        matrix[5] = [0.3, 0.3, 0.1, 0.1, 0.1, 0.05, 0.05]
        return EmissionProbabilities(version=self.version, states=self.states, observations=observations, matrix=matrix)

    def viterbi(self, observations: list[str]) -> tuple[list[BehaviorState], float]:
        """Find most likely state sequence using DP."""
        n_states = len(self.states)
        n_obs = len(observations)
        viterbi_table = np.zeros((n_states, n_obs))
        backpointer = np.zeros((n_states, n_obs), dtype=int)
        
        initial_prob = np.ones(n_states) / n_states

        for s in range(n_states):
            try:
                obs_idx = self.emissions.observations.index(observations[0])
            except ValueError:
                obs_idx = 0 # Fallback
            viterbi_table[s][0] = initial_prob[s] * self.emissions.matrix[s][obs_idx]

        for t in range(1, n_obs):
            try:
                obs_idx = self.emissions.observations.index(observations[t])
            except ValueError:
                obs_idx = 0

            for s in range(n_states):
                # Using vectorized approach for efficiency
                probs = viterbi_table[:, t - 1] * self.transitions.matrix[:, s]
                best_prev = int(np.argmax(probs))
                viterbi_table[s][t] = probs[best_prev] * self.emissions.matrix[s][obs_idx]
                backpointer[s][t] = best_prev

        best_last_state = int(np.argmax(viterbi_table[:, -1]))
        best_prob = float(viterbi_table[best_last_state, -1])
        
        best_path = []
        current_state = best_last_state
        for t in range(n_obs - 1, -1, -1):
            best_path.insert(0, self.states[current_state])
            if t > 0: current_state = backpointer[current_state][t]
            
        return best_path, best_prob


class BehavioralModelEngine:
    """
    L5: Behavioral Modeling Engine
    Hardened against memory exhaustion via bounded observation sequences.
    """

    def __init__(self, model_version: str = "1.0.0", max_sequence: int = 20):
        self.hmm = HiddenMarkovModel(version=model_version)
        # Memory-hardened observation tracking
        self.event_sequences: dict[str, deque[str]] = {}
        self.max_sequence = max_sequence

        logger.info("L5 Behavioral Engine initialized (max_sequence=%d)", max_sequence)

    def process_event(self, event: Any) -> BehaviorState | None:
        """Infer current behavioral state from observation sequence."""
        ip = getattr(event, "source_ip", "UNKNOWN")
        artifact_type = getattr(event, "artifact_type", None)
        observation = getattr(artifact_type, "value", "DNS_RESOLUTION") if artifact_type else "DNS_RESOLUTION"

        if ip not in self.event_sequences:
            if len(self.event_sequences) >= 1000:
                self.event_sequences.clear() # Emergency eviction
            self.event_sequences[ip] = deque(maxlen=self.max_sequence)

        self.event_sequences[ip].append(observation)

        if len(self.event_sequences[ip]) < 2:
            return None

        observations = list(self.event_sequences[ip])
        state_sequence, prob = self.hmm.viterbi(observations)
        current_state = state_sequence[-1]

        logger.info("Behavioral state inferred: %s (p=%.4f) for %s", current_state.value, prob, ip)
        return current_state


__all__ = ["BehaviorState", "HiddenMarkovModel", "BehavioralModelEngine"]
