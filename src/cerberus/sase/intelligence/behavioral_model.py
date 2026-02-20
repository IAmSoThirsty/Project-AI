"""
SASE - Sovereign Adversarial Signal Engine
L5: Behavioral Modeling Engine

Hidden Markov Model for adversarial behavior classification.

STATES:
- S0: Passive Recon
- S1: Token Probe
- S2: Credential Use
- S3: API Enumeration
- S4: Escalation Attempt
- S5: Dormancy

Transition matrix stored per model version.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

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
    """
    Hidden Markov Model state transition probabilities

    Matrix[i][j] = P(state_j | state_i)
    """

    version: str
    states: List[BehaviorState]
    matrix: np.ndarray  # NxN matrix

    def __post_init__(self):
        # Validate matrix dimensions
        n = len(self.states)
        if self.matrix.shape != (n, n):
            raise ValueError(f"Matrix must be {n}x{n}, got {self.matrix.shape}")

        # Validate probabilities sum to 1
        for i in range(n):
            row_sum = np.sum(self.matrix[i])
            if not np.isclose(row_sum, 1.0):
                raise ValueError(f"Row {i} probabilities must sum to 1.0, got {row_sum}")

    def transition_probability(self, from_state: BehaviorState, to_state: BehaviorState) -> float:
        """Get transition probability"""
        i = self.states.index(from_state)
        j = self.states.index(to_state)
        return float(self.matrix[i][j])


@dataclass
class EmissionProbabilities:
    """
    Emission probabilities for observations given states

    P(observation | state)
    """

    version: str
    states: List[BehaviorState]
    observations: List[str]  # Observation types (e.g., "HTTP_CALLBACK", "DNS_RESOLUTION")
    matrix: np.ndarray  # States x Observations

    def __post_init__(self):
        # Validate dimensions
        n_states = len(self.states)
        n_obs = len(self.observations)

        if self.matrix.shape != (n_states, n_obs):
            raise ValueError(f"Matrix must be {n_states}x{n_obs}, got {self.matrix.shape}")

        # Validate probabilities sum to 1 for each state
        for i in range(n_states):
            row_sum = np.sum(self.matrix[i])
            if not np.isclose(row_sum, 1.0):
                raise ValueError(f"State {i} emissions must sum to 1.0, got {row_sum}")

    def emission_probability(self, state: BehaviorState, observation: str) -> float:
        """Get emission probability"""
        i = self.states.index(state)
        j = self.observations.index(observation)
        return float(self.matrix[i][j])


class HiddenMarkovModel:
    """
    Hidden Markov Model for adversarial behavior

    Models sequence of observations to infer underlying attacker state
    """

    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.states = list(BehaviorState)

        # Initialize transition matrix (example probabilities)
        self.transitions = self._initialize_transitions()

        # Initialize emission probabilities
        self.emissions = self._initialize_emissions()

        logger.info(f"HMM initialized (version={version})")

    def _initialize_transitions(self) -> StateTransitionMatrix:
        """
        Initialize state transition probabilities

        Design based on typical attack progression:
        Recon → Probe → Credential use → API enum → Escalation
        With dormancy states between activities
        """
        states = self.states
        n = len(states)

        # Create matrix (rows=from, cols=to)
        matrix = np.zeros((n, n))

        # S0: PASSIVE_RECON
        matrix[0] = [0.4, 0.3, 0.1, 0.1, 0.05, 0.05]  # Can probe or go dormant

        # S1: TOKEN_PROBE
        matrix[1] = [0.1, 0.3, 0.4, 0.1, 0.05, 0.05]  # Likely to use credentials next

        # S2: CREDENTIAL_USE
        matrix[2] = [0.05, 0.1, 0.2, 0.5, 0.1, 0.05]  # Often leads to API enum

        # S3: API_ENUMERATION
        matrix[3] = [0.05, 0.1, 0.2, 0.3, 0.3, 0.05]  # May escalate

        # S4: ESCALATION_ATTEMPT
        matrix[4] = [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]  # Often goes dormant after

        # S5: DORMANCY
        matrix[5] = [0.3, 0.2, 0.1, 0.1, 0.05, 0.25]  # Can re-activate to any state

        return StateTransitionMatrix(version=self.version, states=states, matrix=matrix)

    def _initialize_emissions(self) -> EmissionProbabilities:
        """
        Initialize emission probabilities

        P(observation_type | state)
        """
        observations = [
            "DNS_RESOLUTION",
            "HTTP_CALLBACK",
            "CREDENTIAL_MISUSE",
            "OAUTH_VALIDATION",
            "API_MISUSE",
            "WEBHOOK_INVOCATION",
            "SYNTHETIC_LEAK",
        ]

        n_states = len(self.states)
        n_obs = len(observations)

        # Create emission matrix
        matrix = np.zeros((n_states, n_obs))

        # S0: PASSIVE_RECON - mostly DNS and HTTP callbacks
        matrix[0] = [0.4, 0.4, 0.05, 0.05, 0.05, 0.03, 0.02]

        # S1: TOKEN_PROBE - HTTP callbacks and credentials
        matrix[1] = [0.2, 0.3, 0.3, 0.1, 0.05, 0.03, 0.02]

        # S2: CREDENTIAL_USE - credentials and OAuth
        matrix[2] = [0.05, 0.1, 0.5, 0.25, 0.05, 0.03, 0.02]

        # S3: API_ENUMERATION - API misuse and webhooks
        matrix[3] = [0.05, 0.1, 0.1, 0.2, 0.4, 0.1, 0.05]

        # S4: ESCALATION_ATTEMPT - diverse, including leaks
        matrix[4] = [0.1, 0.15, 0.2, 0.15, 0.2, 0.1, 0.1]

        # S5: DORMANCY - minimal observations
        matrix[5] = [0.3, 0.3, 0.1, 0.1, 0.1, 0.05, 0.05]

        return EmissionProbabilities(
            version=self.version,
            states=self.states,
            observations=observations,
            matrix=matrix,
        )

    def viterbi(self, observations: List[str]) -> Tuple[List[BehaviorState], float]:
        """
        Viterbi algorithm: Find most likely state sequence

        Args:
            observations: Sequence of observation types

        Returns:
            (state_sequence, probability)
        """
        n_states = len(self.states)
        n_obs = len(observations)

        # Initialize DP tables
        viterbi_table = np.zeros((n_states, n_obs))
        backpointer = np.zeros((n_states, n_obs), dtype=int)

        # Initial probabilities (uniform prior)
        initial_prob = np.ones(n_states) / n_states

        # Initialize first column
        for s in range(n_states):
            obs_idx = self.emissions.observations.index(observations[0])
            emission_prob = self.emissions.matrix[s][obs_idx]
            viterbi_table[s][0] = initial_prob[s] * emission_prob

        # Forward pass
        for t in range(1, n_obs):
            obs_idx = self.emissions.observations.index(observations[t])

            for s in range(n_states):
                # Find best previous state
                max_prob = 0.0
                best_prev = 0

                for prev_s in range(n_states):
                    trans_prob = self.transitions.matrix[prev_s][s]
                    prob = viterbi_table[prev_s][t - 1] * trans_prob

                    if prob > max_prob:
                        max_prob = prob
                        best_prev = prev_s

                emission_prob = self.emissions.matrix[s][obs_idx]
                viterbi_table[s][t] = max_prob * emission_prob
                backpointer[s][t] = best_prev

        # Backward pass (trace best path)
        best_path = []
        best_last_state = int(np.argmax(viterbi_table[:, -1]))
        best_prob = float(viterbi_table[best_last_state, -1])

        # Trace back
        current_state = best_last_state
        for t in range(n_obs - 1, -1, -1):
            best_path.insert(0, self.states[current_state])
            if t > 0:
                current_state = backpointer[current_state][t]

        return best_path, best_prob

    def predict_next_state(self, current_state: BehaviorState) -> BehaviorState:
        """
        Predict most likely next state

        Returns state with highest transition probability
        """
        state_idx = self.states.index(current_state)
        next_probs = self.transitions.matrix[state_idx]
        next_idx = int(np.argmax(next_probs))

        return self.states[next_idx]


class BehavioralModelEngine:
    """
    L5: Behavioral Modeling Engine

    Applies HMM to event sequences for behavioral classification
    """

    def __init__(self, model_version: str = "1.0.0"):
        self.hmm = HiddenMarkovModel(version=model_version)
        self.event_sequences: Dict[str, List[str]] = {}  # ip -> [observations]

        logger.info("L5 Behavioral Model Engine initialized")

    def process_event(self, event: Any) -> Optional[BehaviorState]:
        """
        Process event and infer current behavioral state

        Args:
            event: AdversarialEvent

        Returns:
            Inferred BehaviorState (or None if insufficient data)
        """
        from ..core.ingestion_gateway import AdversarialEvent

        if not isinstance(event, AdversarialEvent):
            raise TypeError("Event must be AdversarialEvent")

        ip = event.source_ip
        observation = event.artifact_type.value

        # Track sequence for this IP
        if ip not in self.event_sequences:
            self.event_sequences[ip] = []

        self.event_sequences[ip].append(observation)

        # Need at least 2 observations for HMM
        if len(self.event_sequences[ip]) < 2:
            return None

        # Run Viterbi to infer state sequence
        observations = self.event_sequences[ip]
        state_sequence, prob = self.hmm.viterbi(observations)

        current_state = state_sequence[-1]

        logger.info(f"Behavioral state inferred: {current_state.value} (p={prob:.4f})")

        return current_state

    def get_state_sequence(self, ip: str) -> Optional[List[BehaviorState]]:
        """Get full inferred state sequence for IP"""
        if ip not in self.event_sequences:
            return None

        observations = self.event_sequences[ip]
        if len(observations) < 2:
            return None

        state_sequence, _ = self.hmm.viterbi(observations)
        return state_sequence


__all__ = [
    "BehaviorState",
    "StateTransitionMatrix",
    "EmissionProbabilities",
    "HiddenMarkovModel",
    "BehavioralModelEngine",
]
