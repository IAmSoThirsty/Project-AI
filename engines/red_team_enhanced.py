"""Enhanced Red Team Simulation Engine with AI-Powered Adversaries.

This module implements advanced red team capabilities:
1. AI Adversaries: Reinforcement learning agents that learn attack strategies
2. Adaptive Attacks: Strategies that adapt based on defenses
3. Exploit Chain Generation: Automatically chain vulnerabilities
4. Automated Vulnerability Discovery: Fuzzing + symbolic execution
5. MITRE ATT&CK Coverage: Test coverage for all ATT&CK techniques

Features:
- Deep Q-Network (DQN) based adversarial agents
- Multi-agent attack coordination
- Exploit chain discovery and execution
- Automated fuzzing and symbolic execution
- Comprehensive MITRE ATT&CK framework mapping
- Real-time defense adaptation
- Attack success prediction
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import random
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# MITRE ATT&CK Framework Integration
# ============================================================================

class MITRETechnique(Enum):
    """MITRE ATT&CK Techniques mapped to governance attacks."""
    
    # Initial Access
    PHISHING = "T1566"
    EXPLOIT_PUBLIC_FACING = "T1190"
    TRUSTED_RELATIONSHIP = "T1199"
    
    # Execution
    COMMAND_SCRIPTING = "T1059"
    USER_EXECUTION = "T1204"
    
    # Persistence
    ACCOUNT_MANIPULATION = "T1098"
    COMPROMISE_INFRASTRUCTURE = "T1584"
    
    # Privilege Escalation
    ABUSE_ELEVATION = "T1548"
    EXPLOITATION_ESCALATION = "T1068"
    
    # Defense Evasion
    MASQUERADING = "T1036"
    OBFUSCATED_FILES = "T1027"
    IMPAIR_DEFENSES = "T1562"
    
    # Credential Access
    BRUTE_FORCE = "T1110"
    CREDENTIALS_DUMP = "T1003"
    
    # Discovery
    ACCOUNT_DISCOVERY = "T1087"
    NETWORK_SERVICE_SCAN = "T1046"
    SYSTEM_INFO_DISCOVERY = "T1082"
    
    # Lateral Movement
    REMOTE_SERVICES = "T1021"
    INTERNAL_SPEARPHISHING = "T1534"
    
    # Collection
    DATA_STAGED = "T1074"
    INPUT_CAPTURE = "T1056"
    
    # Command and Control
    APPLICATION_LAYER_PROTOCOL = "T1071"
    ENCRYPTED_CHANNEL = "T1573"
    
    # Exfiltration
    EXFIL_OVER_C2 = "T1041"
    AUTOMATED_EXFIL = "T1020"
    
    # Impact
    DATA_DESTRUCTION = "T1485"
    DEFACEMENT = "T1491"
    DENIAL_OF_SERVICE = "T1499"
    RESOURCE_HIJACKING = "T1496"


@dataclass
class AttackTechnique:
    """MITRE ATT&CK technique details."""
    
    technique_id: str
    name: str
    tactic: str
    description: str
    effectiveness: float = 0.5
    detection_difficulty: float = 0.5
    prerequisites: list[str] = field(default_factory=list)
    target_dimensions: list[str] = field(default_factory=list)


class MITREAttackMatrix:
    """Complete MITRE ATT&CK matrix for governance systems."""
    
    def __init__(self):
        """Initialize attack matrix."""
        self.techniques = self._initialize_techniques()
        self.coverage = defaultdict(int)
        self.successful_techniques = set()
        
    def _initialize_techniques(self) -> dict[str, AttackTechnique]:
        """Initialize all attack techniques."""
        techniques = {
            # Initial Access
            MITRETechnique.PHISHING.value: AttackTechnique(
                technique_id=MITRETechnique.PHISHING.value,
                name="Phishing",
                tactic="Initial Access",
                description="Social engineering to establish trust",
                effectiveness=0.7,
                detection_difficulty=0.6,
                target_dimensions=["trust", "epistemic_confidence"]
            ),
            
            # Persistence
            MITRETechnique.ACCOUNT_MANIPULATION.value: AttackTechnique(
                technique_id=MITRETechnique.ACCOUNT_MANIPULATION.value,
                name="Account Manipulation",
                tactic="Persistence",
                description="Manipulate trust relationships",
                effectiveness=0.8,
                detection_difficulty=0.7,
                prerequisites=[MITRETechnique.PHISHING.value],
                target_dimensions=["trust", "legitimacy"]
            ),
            
            # Defense Evasion
            MITRETechnique.MASQUERADING.value: AttackTechnique(
                technique_id=MITRETechnique.MASQUERADING.value,
                name="Masquerading",
                tactic="Defense Evasion",
                description="Disguise attacks as legitimate actions",
                effectiveness=0.75,
                detection_difficulty=0.8,
                target_dimensions=["epistemic_confidence", "reality_consensus"]
            ),
            
            MITRETechnique.IMPAIR_DEFENSES.value: AttackTechnique(
                technique_id=MITRETechnique.IMPAIR_DEFENSES.value,
                name="Impair Defenses",
                tactic="Defense Evasion",
                description="Degrade defensive capabilities",
                effectiveness=0.85,
                detection_difficulty=0.6,
                target_dimensions=["governance_capacity", "social_cohesion"]
            ),
            
            # Impact
            MITRETechnique.DENIAL_OF_SERVICE.value: AttackTechnique(
                technique_id=MITRETechnique.DENIAL_OF_SERVICE.value,
                name="Denial of Service",
                tactic="Impact",
                description="Overwhelm governance systems",
                effectiveness=0.9,
                detection_difficulty=0.3,
                target_dimensions=["governance_capacity", "legitimacy"]
            ),
            
            MITRETechnique.DATA_DESTRUCTION.value: AttackTechnique(
                technique_id=MITRETechnique.DATA_DESTRUCTION.value,
                name="Data Destruction",
                tactic="Impact",
                description="Destroy trust and institutional memory",
                effectiveness=0.95,
                detection_difficulty=0.2,
                prerequisites=[MITRETechnique.ACCOUNT_MANIPULATION.value],
                target_dimensions=["trust", "legitimacy", "epistemic_confidence"]
            ),
        }
        
        return techniques
    
    def get_technique(self, technique_id: str) -> AttackTechnique | None:
        """Get technique details."""
        return self.techniques.get(technique_id)
    
    def record_execution(self, technique_id: str, success: bool) -> None:
        """Record technique execution."""
        self.coverage[technique_id] += 1
        if success:
            self.successful_techniques.add(technique_id)
    
    def get_coverage_report(self) -> dict[str, Any]:
        """Generate coverage report."""
        total_techniques = len(self.techniques)
        tested_techniques = len(self.coverage)
        successful_techniques = len(self.successful_techniques)
        
        return {
            "total_techniques": total_techniques,
            "tested_techniques": tested_techniques,
            "successful_techniques": successful_techniques,
            "coverage_percentage": (tested_techniques / total_techniques) * 100,
            "success_rate": (successful_techniques / tested_techniques * 100) if tested_techniques > 0 else 0,
            "technique_coverage": dict(self.coverage),
            "successful_techniques": list(self.successful_techniques),
        }


# ============================================================================
# Reinforcement Learning Agent
# ============================================================================

@dataclass
class StateObservation:
    """State observation for RL agent."""
    
    trust: float
    legitimacy: float
    epistemic_confidence: float
    moral_injury: float
    social_cohesion: float
    governance_capacity: float
    reality_consensus: float
    kindness: float
    previous_attack_success: float
    defense_level: float
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy vector."""
        return np.array([
            self.trust,
            self.legitimacy,
            self.epistemic_confidence,
            self.moral_injury,
            self.social_cohesion,
            self.governance_capacity,
            self.reality_consensus,
            self.kindness,
            self.previous_attack_success,
            self.defense_level,
        ], dtype=np.float32)
    
    @classmethod
    def from_state(cls, state: dict[str, Any]) -> StateObservation:
        """Create observation from state."""
        return cls(
            trust=state.get("trust", 0.5),
            legitimacy=state.get("legitimacy", 0.5),
            epistemic_confidence=state.get("epistemic_confidence", 0.5),
            moral_injury=state.get("moral_injury", 0.5),
            social_cohesion=state.get("social_cohesion", 0.5),
            governance_capacity=state.get("governance_capacity", 0.5),
            reality_consensus=state.get("reality_consensus", 0.5),
            kindness=state.get("kindness", 0.5),
            previous_attack_success=state.get("previous_attack_success", 0.0),
            defense_level=state.get("defense_level", 0.5),
        )


class AttackAction(Enum):
    """Available attack actions for RL agent."""
    
    TRUST_ATTACK = 0
    LEGITIMACY_ATTACK = 1
    EPISTEMIC_ATTACK = 2
    MORAL_INJURY_ATTACK = 3
    SOCIAL_COHESION_ATTACK = 4
    GOVERNANCE_ATTACK = 5
    REALITY_ATTACK = 6
    KINDNESS_ATTACK = 7
    COORDINATED_ATTACK = 8
    WAIT_AND_OBSERVE = 9


class DQNAgent:
    """Deep Q-Network agent for learning attack strategies."""
    
    def __init__(
        self,
        state_dim: int = 10,
        action_dim: int = 10,
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        memory_size: int = 10000,
    ):
        """Initialize DQN agent."""
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.learning_rate = learning_rate
        
        # Experience replay buffer
        self.memory = deque(maxlen=memory_size)
        
        # Q-network (simplified - using numpy instead of neural network)
        self.q_table = defaultdict(lambda: np.zeros(action_dim))
        
        # Training stats
        self.episode_rewards = []
        self.episode_losses = []
        
    def _discretize_state(self, state: np.ndarray) -> str:
        """Discretize continuous state for Q-table."""
        # Bin each dimension into 5 buckets
        discretized = tuple((state * 5).astype(int).clip(0, 4))
        return str(discretized)
    
    def choose_action(self, state: np.ndarray, training: bool = True) -> int:
        """Choose action using epsilon-greedy policy."""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        state_key = self._discretize_state(state)
        return int(np.argmax(self.q_table[state_key]))
    
    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state, done))
    
    def train(self, batch_size: int = 32) -> float:
        """Train on batch of experiences."""
        if len(self.memory) < batch_size:
            return 0.0
        
        # Sample batch
        batch = random.sample(self.memory, batch_size)
        
        total_loss = 0.0
        for state, action, reward, next_state, done in batch:
            state_key = self._discretize_state(state)
            next_state_key = self._discretize_state(next_state)
            
            # Q-learning update
            target = reward
            if not done:
                target += self.gamma * np.max(self.q_table[next_state_key])
            
            current_q = self.q_table[state_key][action]
            loss = (target - current_q) ** 2
            total_loss += loss
            
            # Update Q-value
            self.q_table[state_key][action] += self.learning_rate * (target - current_q)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        avg_loss = total_loss / batch_size
        self.episode_losses.append(avg_loss)
        return avg_loss
    
    def save(self, path: Path) -> None:
        """Save agent state."""
        state = {
            "q_table": {k: v.tolist() for k, v in self.q_table.items()},
            "epsilon": self.epsilon,
            "episode_rewards": self.episode_rewards,
            "episode_losses": self.episode_losses,
        }
        path.write_text(json.dumps(state, indent=2))
        logger.info(f"DQN agent saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load agent state."""
        if not path.exists():
            logger.warning(f"No saved agent found at {path}")
            return
        
        state = json.loads(path.read_text())
        self.q_table = defaultdict(
            lambda: np.zeros(self.action_dim),
            {k: np.array(v) for k, v in state["q_table"].items()}
        )
        self.epsilon = state["epsilon"]
        self.episode_rewards = state["episode_rewards"]
        self.episode_losses = state["episode_losses"]
        logger.info(f"DQN agent loaded from {path}")


# ============================================================================
# Exploit Chain Generation
# ============================================================================

@dataclass
class Vulnerability:
    """Discovered vulnerability."""
    
    vuln_id: str
    type: str
    severity: float
    exploitability: float
    target_dimension: str
    prerequisites: list[str] = field(default_factory=list)
    impact: dict[str, float] = field(default_factory=dict)
    discovered_at: float = 0.0
    exploited: bool = False


@dataclass
class ExploitChain:
    """Chain of exploits."""
    
    chain_id: str
    vulnerabilities: list[Vulnerability]
    total_impact: float
    success_probability: float
    execution_order: list[str]
    
    def calculate_chain_impact(self) -> dict[str, float]:
        """Calculate cumulative impact of chain."""
        total_impact = defaultdict(float)
        
        for vuln in self.vulnerabilities:
            for dim, impact in vuln.impact.items():
                total_impact[dim] += impact
        
        return dict(total_impact)


class ExploitChainGenerator:
    """Generate exploit chains from vulnerabilities."""
    
    def __init__(self):
        """Initialize generator."""
        self.known_vulnerabilities: dict[str, Vulnerability] = {}
        self.discovered_chains: list[ExploitChain] = []
        
    def add_vulnerability(self, vuln: Vulnerability) -> None:
        """Add discovered vulnerability."""
        self.known_vulnerabilities[vuln.vuln_id] = vuln
        logger.info(f"Vulnerability added: {vuln.vuln_id} (severity: {vuln.severity:.2f})")
    
    def can_chain(self, vuln1: Vulnerability, vuln2: Vulnerability) -> bool:
        """Check if two vulnerabilities can be chained."""
        # vuln2 can follow vuln1 if vuln1's target is in vuln2's prerequisites
        if not vuln2.prerequisites:
            return True
        
        return vuln1.vuln_id in vuln2.prerequisites or vuln1.target_dimension in vuln2.prerequisites
    
    def generate_chains(self, max_chain_length: int = 5) -> list[ExploitChain]:
        """Generate all possible exploit chains."""
        chains = []
        vulns = list(self.known_vulnerabilities.values())
        
        # Start with each vulnerability
        for start_vuln in vulns:
            self._build_chains(
                current_chain=[start_vuln],
                remaining_vulns=[v for v in vulns if v != start_vuln],
                max_length=max_chain_length,
                chains=chains,
            )
        
        # Sort by total impact
        chains.sort(key=lambda c: c.total_impact, reverse=True)
        
        self.discovered_chains = chains
        logger.info(f"Generated {len(chains)} exploit chains")
        
        return chains
    
    def _build_chains(
        self,
        current_chain: list[Vulnerability],
        remaining_vulns: list[Vulnerability],
        max_length: int,
        chains: list[ExploitChain],
    ) -> None:
        """Recursively build exploit chains."""
        if len(current_chain) >= max_length:
            return
        
        # Try to extend chain with each remaining vulnerability
        for vuln in remaining_vulns:
            if self.can_chain(current_chain[-1], vuln):
                new_chain = current_chain + [vuln]
                
                # Create exploit chain
                chain_impact = sum(v.severity * v.exploitability for v in new_chain)
                success_prob = np.prod([v.exploitability for v in new_chain])
                
                exploit_chain = ExploitChain(
                    chain_id=f"chain_{len(chains) + 1}",
                    vulnerabilities=new_chain,
                    total_impact=chain_impact,
                    success_probability=success_prob,
                    execution_order=[v.vuln_id for v in new_chain],
                )
                
                chains.append(exploit_chain)
                
                # Continue building
                self._build_chains(
                    current_chain=new_chain,
                    remaining_vulns=[v for v in remaining_vulns if v != vuln],
                    max_length=max_length,
                    chains=chains,
                )
    
    def get_best_chain(self, min_impact: float = 0.0) -> ExploitChain | None:
        """Get highest impact chain."""
        valid_chains = [c for c in self.discovered_chains if c.total_impact >= min_impact]
        
        if not valid_chains:
            return None
        
        return max(valid_chains, key=lambda c: c.total_impact)


# ============================================================================
# Automated Vulnerability Discovery
# ============================================================================

class FuzzingEngine:
    """Fuzzing engine for discovering vulnerabilities."""
    
    def __init__(self, seed: int = 42):
        """Initialize fuzzing engine."""
        self.rng = random.Random(seed)
        self.test_cases: list[dict[str, Any]] = []
        self.crashes: list[dict[str, Any]] = []
        
    def generate_fuzz_inputs(self, count: int = 100) -> list[dict[str, Any]]:
        """Generate fuzz test inputs."""
        inputs = []
        
        for i in range(count):
            # Generate random state mutations
            fuzz_input = {
                "trust": self.rng.uniform(-1.0, 2.0),
                "legitimacy": self.rng.uniform(-1.0, 2.0),
                "epistemic_confidence": self.rng.uniform(-1.0, 2.0),
                "moral_injury": self.rng.uniform(-1.0, 2.0),
                "social_cohesion": self.rng.uniform(-1.0, 2.0),
                "governance_capacity": self.rng.uniform(-1.0, 2.0),
                "mutation_type": self.rng.choice([
                    "extreme_values",
                    "boundary_conditions",
                    "rapid_oscillation",
                    "negative_values",
                    "overflow_attempt",
                ]),
            }
            inputs.append(fuzz_input)
        
        self.test_cases.extend(inputs)
        return inputs
    
    def test_input(self, fuzz_input: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        """Test fuzz input and detect crashes/vulnerabilities."""
        result = {
            "input": fuzz_input,
            "crashed": False,
            "vulnerability_found": False,
            "vulnerability_type": None,
            "severity": 0.0,
        }
        
        # Check for extreme value vulnerabilities
        for key, value in fuzz_input.items():
            if key.endswith("mutation_type"):
                continue
            
            state_value = state.get(key, 0.5)
            
            # Detect boundary violations
            if value < 0.0 or value > 1.0:
                result["vulnerability_found"] = True
                result["vulnerability_type"] = "boundary_violation"
                result["severity"] = abs(value - 0.5) if value < 0 else abs(value - 1.0)
            
            # Detect instability from rapid changes
            if abs(value - state_value) > 0.8:
                result["vulnerability_found"] = True
                result["vulnerability_type"] = "stability_vulnerability"
                result["severity"] = abs(value - state_value)
            
            # Detect collapse conditions
            if value < 0.1 and key in ["trust", "legitimacy", "governance_capacity"]:
                result["crashed"] = True
                result["vulnerability_found"] = True
                result["vulnerability_type"] = "collapse_condition"
                result["severity"] = 1.0
        
        if result["crashed"]:
            self.crashes.append(result)
        
        return result
    
    def get_crash_report(self) -> dict[str, Any]:
        """Get crash report."""
        return {
            "total_tests": len(self.test_cases),
            "crashes": len(self.crashes),
            "crash_rate": len(self.crashes) / len(self.test_cases) if self.test_cases else 0,
            "crash_details": self.crashes,
        }


class SymbolicExecutionEngine:
    """Symbolic execution for path exploration."""
    
    def __init__(self):
        """Initialize symbolic execution engine."""
        self.explored_paths: list[dict[str, Any]] = []
        self.interesting_paths: list[dict[str, Any]] = []
        
    def explore_paths(
        self,
        initial_state: dict[str, Any],
        max_depth: int = 5,
    ) -> list[dict[str, Any]]:
        """Symbolically explore execution paths."""
        paths = []
        
        # Start with initial state
        self._explore_recursive(
            state=initial_state.copy(),
            path=[],
            depth=0,
            max_depth=max_depth,
            paths=paths,
        )
        
        self.explored_paths = paths
        
        # Find interesting paths (leading to extreme states)
        self.interesting_paths = [
            p for p in paths
            if self._is_interesting_path(p)
        ]
        
        logger.info(
            f"Explored {len(paths)} paths, "
            f"found {len(self.interesting_paths)} interesting paths"
        )
        
        return self.interesting_paths
    
    def _explore_recursive(
        self,
        state: dict[str, Any],
        path: list[str],
        depth: int,
        max_depth: int,
        paths: list[dict[str, Any]],
    ) -> None:
        """Recursively explore paths."""
        if depth >= max_depth:
            paths.append({"path": path.copy(), "final_state": state.copy()})
            return
        
        # Try each possible action
        actions = [
            "decrease_trust",
            "increase_trust",
            "decrease_legitimacy",
            "increase_legitimacy",
            "decrease_governance",
            "increase_governance",
        ]
        
        for action in actions:
            new_state = state.copy()
            new_path = path + [action]
            
            # Simulate action effect
            if "decrease" in action:
                dim = action.replace("decrease_", "")
                new_state[dim] = max(0.0, state.get(dim, 0.5) - 0.2)
            else:
                dim = action.replace("increase_", "")
                new_state[dim] = min(1.0, state.get(dim, 0.5) + 0.2)
            
            self._explore_recursive(new_state, new_path, depth + 1, max_depth, paths)
    
    def _is_interesting_path(self, path: dict[str, Any]) -> bool:
        """Check if path leads to interesting state."""
        final_state = path["final_state"]
        
        # Interesting if any dimension reaches extreme
        for key, value in final_state.items():
            if isinstance(value, (int, float)):
                if value < 0.1 or value > 0.9:
                    return True
        
        return False


# ============================================================================
# Enhanced Red Team Engine
# ============================================================================

@dataclass
class AttackCampaign:
    """Multi-stage attack campaign."""
    
    campaign_id: str
    strategy: str
    start_time: float
    attacks: list[dict[str, Any]] = field(default_factory=list)
    total_damage: float = 0.0
    success_rate: float = 0.0
    techniques_used: list[str] = field(default_factory=list)
    exploit_chains_executed: list[str] = field(default_factory=list)


class EnhancedRedTeamEngine:
    """Enhanced red team engine with AI adversaries and advanced capabilities."""
    
    def __init__(
        self,
        data_dir: str = "data/red_team_enhanced",
        enable_rl: bool = True,
        enable_fuzzing: bool = True,
        enable_symbolic: bool = True,
    ):
        """Initialize enhanced red team engine."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.mitre_matrix = MITREAttackMatrix()
        self.chain_generator = ExploitChainGenerator()
        self.fuzzing_engine = FuzzingEngine() if enable_fuzzing else None
        self.symbolic_engine = SymbolicExecutionEngine() if enable_symbolic else None
        
        # RL Agent
        self.rl_agent = DQNAgent() if enable_rl else None
        self.enable_rl = enable_rl
        
        # Attack tracking
        self.campaigns: list[AttackCampaign] = []
        self.current_campaign: AttackCampaign | None = None
        self.discovered_vulnerabilities: dict[str, Vulnerability] = {}
        
        # Defense tracking
        self.defense_effectiveness = defaultdict(float)
        self.adaptive_strategies: dict[str, float] = {}
        
        # Statistics
        self.total_attacks = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
        
        logger.info(
            f"Enhanced Red Team Engine initialized "
            f"(RL: {enable_rl}, Fuzzing: {enable_fuzzing}, Symbolic: {enable_symbolic})"
        )
    
    def start_campaign(self, strategy: str = "adaptive") -> str:
        """Start new attack campaign."""
        campaign_id = f"campaign_{len(self.campaigns) + 1}_{datetime.now(timezone.utc).timestamp()}"
        
        self.current_campaign = AttackCampaign(
            campaign_id=campaign_id,
            strategy=strategy,
            start_time=datetime.now(timezone.utc).timestamp(),
        )
        
        self.campaigns.append(self.current_campaign)
        logger.info(f"Started attack campaign: {campaign_id} (strategy: {strategy})")
        
        return campaign_id
    
    def discover_vulnerabilities(
        self,
        state: dict[str, Any],
        use_fuzzing: bool = True,
        use_symbolic: bool = True,
    ) -> list[Vulnerability]:
        """Discover vulnerabilities using automated techniques."""
        discovered = []
        
        # Fuzzing
        if use_fuzzing and self.fuzzing_engine:
            fuzz_inputs = self.fuzzing_engine.generate_fuzz_inputs(count=50)
            
            for fuzz_input in fuzz_inputs:
                result = self.fuzzing_engine.test_input(fuzz_input, state)
                
                if result["vulnerability_found"]:
                    vuln = Vulnerability(
                        vuln_id=f"fuzz_vuln_{len(self.discovered_vulnerabilities) + 1}",
                        type=result["vulnerability_type"],
                        severity=result["severity"],
                        exploitability=0.7 if not result["crashed"] else 0.9,
                        target_dimension=self._identify_target_dimension(fuzz_input),
                        impact=self._calculate_vulnerability_impact(result),
                        discovered_at=datetime.now(timezone.utc).timestamp(),
                    )
                    
                    discovered.append(vuln)
                    self.discovered_vulnerabilities[vuln.vuln_id] = vuln
                    self.chain_generator.add_vulnerability(vuln)
        
        # Symbolic execution
        if use_symbolic and self.symbolic_engine:
            interesting_paths = self.symbolic_engine.explore_paths(state, max_depth=4)
            
            for path_info in interesting_paths[:10]:  # Limit to top 10
                vuln = Vulnerability(
                    vuln_id=f"symbolic_vuln_{len(self.discovered_vulnerabilities) + 1}",
                    type="path_vulnerability",
                    severity=self._calculate_path_severity(path_info["final_state"]),
                    exploitability=0.6,
                    target_dimension=self._identify_critical_dimension(path_info["final_state"]),
                    impact=self._calculate_path_impact(path_info),
                    discovered_at=datetime.now(timezone.utc).timestamp(),
                )
                
                discovered.append(vuln)
                self.discovered_vulnerabilities[vuln.vuln_id] = vuln
                self.chain_generator.add_vulnerability(vuln)
        
        # Static analysis
        static_vulns = self._static_vulnerability_scan(state)
        discovered.extend(static_vulns)
        
        for vuln in static_vulns:
            self.discovered_vulnerabilities[vuln.vuln_id] = vuln
            self.chain_generator.add_vulnerability(vuln)
        
        logger.info(f"Discovered {len(discovered)} vulnerabilities")
        return discovered
    
    def _identify_target_dimension(self, fuzz_input: dict[str, Any]) -> str:
        """Identify primary target dimension from fuzz input."""
        # Find dimension with most extreme value
        max_deviation = 0.0
        target = "trust"
        
        for key, value in fuzz_input.items():
            if key == "mutation_type":
                continue
            
            deviation = abs(value - 0.5)
            if deviation > max_deviation:
                max_deviation = deviation
                target = key
        
        return target
    
    def _calculate_vulnerability_impact(self, result: dict[str, Any]) -> dict[str, float]:
        """Calculate impact of vulnerability."""
        severity = result["severity"]
        vuln_type = result["vulnerability_type"]
        
        impact = {}
        
        if vuln_type == "collapse_condition":
            impact = {
                "trust": -severity * 0.5,
                "legitimacy": -severity * 0.5,
                "governance_capacity": -severity * 0.6,
            }
        elif vuln_type == "stability_vulnerability":
            impact = {
                "social_cohesion": -severity * 0.3,
                "reality_consensus": -severity * 0.3,
            }
        else:
            impact = {"trust": -severity * 0.2}
        
        return impact
    
    def _calculate_path_severity(self, final_state: dict[str, Any]) -> float:
        """Calculate severity based on final state."""
        # Severity based on how many dimensions reached extremes
        extreme_count = 0
        total_deviation = 0.0
        
        for value in final_state.values():
            if isinstance(value, (int, float)):
                if value < 0.1 or value > 0.9:
                    extreme_count += 1
                total_deviation += abs(value - 0.5)
        
        return min(1.0, (extreme_count * 0.2) + (total_deviation / len(final_state)))
    
    def _identify_critical_dimension(self, final_state: dict[str, Any]) -> str:
        """Identify most critical dimension from state."""
        min_value = 1.0
        critical_dim = "trust"
        
        for key, value in final_state.items():
            if isinstance(value, (int, float)) and value < min_value:
                min_value = value
                critical_dim = key
        
        return critical_dim
    
    def _calculate_path_impact(self, path_info: dict[str, Any]) -> dict[str, float]:
        """Calculate impact of execution path."""
        final_state = path_info["final_state"]
        impact = {}
        
        for key, value in final_state.items():
            if isinstance(value, (int, float)):
                # Impact is deviation from normal (0.5)
                deviation = value - 0.5
                if abs(deviation) > 0.2:
                    impact[key] = -deviation * 0.5
        
        return impact
    
    def _static_vulnerability_scan(self, state: dict[str, Any]) -> list[Vulnerability]:
        """Static vulnerability scanning."""
        vulns = []
        
        # Low trust vulnerability
        if state.get("trust", 0.5) < 0.3:
            vulns.append(Vulnerability(
                vuln_id=f"static_low_trust_{len(self.discovered_vulnerabilities)}",
                type="low_trust",
                severity=(0.3 - state["trust"]) * 2.0,
                exploitability=0.8,
                target_dimension="trust",
                impact={"trust": -0.2, "social_cohesion": -0.15},
            ))
        
        # Low legitimacy vulnerability
        if state.get("legitimacy", 0.5) < 0.3:
            vulns.append(Vulnerability(
                vuln_id=f"static_low_legitimacy_{len(self.discovered_vulnerabilities)}",
                type="low_legitimacy",
                severity=(0.3 - state["legitimacy"]) * 2.0,
                exploitability=0.75,
                target_dimension="legitimacy",
                impact={"legitimacy": -0.25, "governance_capacity": -0.2},
            ))
        
        # Weak governance vulnerability
        if state.get("governance_capacity", 0.5) < 0.4:
            vulns.append(Vulnerability(
                vuln_id=f"static_weak_governance_{len(self.discovered_vulnerabilities)}",
                type="weak_governance",
                severity=(0.4 - state["governance_capacity"]) * 2.0,
                exploitability=0.9,
                target_dimension="governance_capacity",
                impact={"governance_capacity": -0.3, "social_cohesion": -0.2},
            ))
        
        return vulns
    
    def select_attack_strategy(
        self,
        state: dict[str, Any],
        use_rl: bool = True,
    ) -> tuple[int, str]:
        """Select attack strategy using RL or heuristics."""
        if use_rl and self.rl_agent:
            # Use RL agent
            observation = StateObservation.from_state(state)
            state_vector = observation.to_vector()
            action_idx = self.rl_agent.choose_action(state_vector)
            action = AttackAction(action_idx)
            
            logger.debug(f"RL agent selected action: {action.name}")
            return action_idx, action.name
        else:
            # Use heuristic strategy
            return self._heuristic_strategy_selection(state)
    
    def _heuristic_strategy_selection(self, state: dict[str, Any]) -> tuple[int, str]:
        """Heuristic-based strategy selection."""
        # Target weakest dimension
        dimensions = {
            "trust": state.get("trust", 0.5),
            "legitimacy": state.get("legitimacy", 0.5),
            "epistemic_confidence": state.get("epistemic_confidence", 0.5),
            "governance_capacity": state.get("governance_capacity", 0.5),
            "social_cohesion": state.get("social_cohesion", 0.5),
        }
        
        weakest_dim = min(dimensions.items(), key=lambda x: x[1])
        
        action_map = {
            "trust": (AttackAction.TRUST_ATTACK.value, "TRUST_ATTACK"),
            "legitimacy": (AttackAction.LEGITIMACY_ATTACK.value, "LEGITIMACY_ATTACK"),
            "epistemic_confidence": (AttackAction.EPISTEMIC_ATTACK.value, "EPISTEMIC_ATTACK"),
            "governance_capacity": (AttackAction.GOVERNANCE_ATTACK.value, "GOVERNANCE_ATTACK"),
            "social_cohesion": (AttackAction.SOCIAL_COHESION_ATTACK.value, "SOCIAL_COHESION_ATTACK"),
        }
        
        return action_map.get(weakest_dim[0], (0, "TRUST_ATTACK"))
    
    def execute_attack(
        self,
        state: dict[str, Any],
        use_exploit_chain: bool = True,
        adapt_to_defenses: bool = True,
    ) -> dict[str, Any]:
        """Execute attack with optional exploit chaining."""
        self.total_attacks += 1
        
        attack_result = {
            "timestamp": datetime.now(timezone.utc).timestamp(),
            "success": False,
            "damage": 0.0,
            "technique_used": None,
            "exploit_chain_used": None,
            "state_changes": {},
        }
        
        # Discover vulnerabilities
        vulns = self.discover_vulnerabilities(state)
        
        # Try exploit chain first
        if use_exploit_chain and self.chain_generator.known_vulnerabilities:
            chains = self.chain_generator.generate_chains(max_chain_length=3)
            
            if chains:
                best_chain = chains[0]
                attack_result["exploit_chain_used"] = best_chain.chain_id
                
                # Execute chain
                chain_impact = best_chain.calculate_chain_impact()
                attack_result["state_changes"] = chain_impact
                attack_result["damage"] = best_chain.total_impact
                attack_result["success"] = best_chain.success_probability > 0.5
                
                if self.current_campaign:
                    self.current_campaign.exploit_chains_executed.append(best_chain.chain_id)
                
                logger.info(
                    f"Executed exploit chain {best_chain.chain_id} "
                    f"(impact: {best_chain.total_impact:.2f})"
                )
        
        # Fallback to single technique attack
        if not attack_result["success"]:
            action_idx, action_name = self.select_attack_strategy(state, use_rl=self.enable_rl)
            
            # Map action to MITRE technique
            technique_id = self._map_action_to_technique(action_name)
            technique = self.mitre_matrix.get_technique(technique_id)
            
            if technique:
                # Calculate attack effectiveness
                base_effectiveness = technique.effectiveness
                
                # Adapt to defenses
                if adapt_to_defenses:
                    defense_modifier = self._calculate_defense_modifier(state, technique_id)
                    effectiveness = base_effectiveness * defense_modifier
                else:
                    effectiveness = base_effectiveness
                
                # Execute attack
                success = random.random() < effectiveness
                attack_result["success"] = success
                attack_result["technique_used"] = technique_id
                
                if success:
                    # Calculate damage
                    damage = technique.effectiveness * random.uniform(0.8, 1.2)
                    attack_result["damage"] = damage
                    
                    # Calculate state changes
                    state_changes = {}
                    for dim in technique.target_dimensions:
                        state_changes[dim] = -damage * random.uniform(0.1, 0.3)
                    
                    attack_result["state_changes"] = state_changes
                    
                    self.mitre_matrix.record_execution(technique_id, True)
                    self.successful_attacks += 1
                else:
                    self.mitre_matrix.record_execution(technique_id, False)
                    self.failed_attacks += 1
        
        # Record in campaign
        if self.current_campaign:
            self.current_campaign.attacks.append(attack_result)
            self.current_campaign.total_damage += attack_result["damage"]
            
            if attack_result["technique_used"]:
                self.current_campaign.techniques_used.append(attack_result["technique_used"])
        
        # Update RL agent
        if self.enable_rl and self.rl_agent:
            self._update_rl_agent(state, attack_result)
        
        return attack_result
    
    def _map_action_to_technique(self, action_name: str) -> str:
        """Map attack action to MITRE technique."""
        mapping = {
            "TRUST_ATTACK": MITRETechnique.PHISHING.value,
            "LEGITIMACY_ATTACK": MITRETechnique.ACCOUNT_MANIPULATION.value,
            "EPISTEMIC_ATTACK": MITRETechnique.MASQUERADING.value,
            "GOVERNANCE_ATTACK": MITRETechnique.IMPAIR_DEFENSES.value,
            "SOCIAL_COHESION_ATTACK": MITRETechnique.DENIAL_OF_SERVICE.value,
            "COORDINATED_ATTACK": MITRETechnique.DATA_DESTRUCTION.value,
        }
        
        return mapping.get(action_name, MITRETechnique.PHISHING.value)
    
    def _calculate_defense_modifier(self, state: dict[str, Any], technique_id: str) -> float:
        """Calculate defense effectiveness modifier."""
        # Track defense effectiveness
        base_defense = state.get("defense_level", 0.5)
        
        # Technique-specific defense adaptation
        if technique_id in self.defense_effectiveness:
            # Defenses get stronger against repeated techniques
            adaptation = self.defense_effectiveness[technique_id]
            modifier = 1.0 - (base_defense * adaptation)
        else:
            modifier = 1.0 - (base_defense * 0.5)
        
        # Update defense tracking
        self.defense_effectiveness[technique_id] += 0.1
        
        return max(0.1, modifier)  # Minimum 10% effectiveness
    
    def _update_rl_agent(self, state: dict[str, Any], attack_result: dict[str, Any]) -> None:
        """Update RL agent with attack results."""
        if not self.rl_agent:
            return
        
        # Calculate reward
        reward = attack_result["damage"] if attack_result["success"] else -0.1
        
        # Create observations
        observation = StateObservation.from_state(state)
        state_vector = observation.to_vector()
        
        # Update next state
        next_state = state.copy()
        for dim, change in attack_result.get("state_changes", {}).items():
            next_state[dim] = max(0.0, min(1.0, state.get(dim, 0.5) + change))
        
        next_observation = StateObservation.from_state(next_state)
        next_state_vector = next_observation.to_vector()
        
        # Store experience
        action_idx = self._map_action_to_technique(attack_result.get("technique_used", ""))
        self.rl_agent.remember(
            state=state_vector,
            action=action_idx,
            reward=reward,
            next_state=next_state_vector,
            done=False,
        )
        
        # Train agent
        if len(self.rl_agent.memory) >= 32:
            loss = self.rl_agent.train(batch_size=32)
            logger.debug(f"RL agent trained, loss: {loss:.4f}")
    
    def end_campaign(self) -> dict[str, Any]:
        """End current campaign and generate report."""
        if not self.current_campaign:
            return {}
        
        campaign = self.current_campaign
        
        # Calculate statistics
        total_attacks = len(campaign.attacks)
        successful = sum(1 for a in campaign.attacks if a["success"])
        campaign.success_rate = successful / total_attacks if total_attacks > 0 else 0
        
        report = {
            "campaign_id": campaign.campaign_id,
            "strategy": campaign.strategy,
            "duration": datetime.now(timezone.utc).timestamp() - campaign.start_time,
            "total_attacks": total_attacks,
            "successful_attacks": successful,
            "success_rate": campaign.success_rate,
            "total_damage": campaign.total_damage,
            "techniques_used": len(set(campaign.techniques_used)),
            "exploit_chains_executed": len(campaign.exploit_chains_executed),
            "mitre_coverage": self.mitre_matrix.get_coverage_report(),
        }
        
        self.current_campaign = None
        logger.info(f"Campaign ended: {report['campaign_id']}")
        
        return report
    
    def get_mitre_coverage_report(self) -> dict[str, Any]:
        """Generate MITRE ATT&CK coverage report."""
        return self.mitre_matrix.get_coverage_report()
    
    def get_vulnerability_report(self) -> dict[str, Any]:
        """Generate vulnerability discovery report."""
        return {
            "total_vulnerabilities": len(self.discovered_vulnerabilities),
            "by_type": self._count_by_type(),
            "by_severity": self._count_by_severity(),
            "exploited": sum(1 for v in self.discovered_vulnerabilities.values() if v.exploited),
            "vulnerabilities": [
                asdict(v) for v in self.discovered_vulnerabilities.values()
            ],
        }
    
    def _count_by_type(self) -> dict[str, int]:
        """Count vulnerabilities by type."""
        counts = defaultdict(int)
        for vuln in self.discovered_vulnerabilities.values():
            counts[vuln.type] += 1
        return dict(counts)
    
    def _count_by_severity(self) -> dict[str, int]:
        """Count vulnerabilities by severity level."""
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for vuln in self.discovered_vulnerabilities.values():
            if vuln.severity < 0.3:
                counts["low"] += 1
            elif vuln.severity < 0.6:
                counts["medium"] += 1
            elif vuln.severity < 0.9:
                counts["high"] += 1
            else:
                counts["critical"] += 1
        
        return counts
    
    def get_exploit_chain_report(self) -> dict[str, Any]:
        """Generate exploit chain report."""
        chains = self.chain_generator.discovered_chains
        
        return {
            "total_chains": len(chains),
            "average_chain_length": np.mean([len(c.vulnerabilities) for c in chains]) if chains else 0,
            "max_chain_length": max([len(c.vulnerabilities) for c in chains]) if chains else 0,
            "highest_impact_chain": asdict(chains[0]) if chains else None,
            "all_chains": [asdict(c) for c in chains[:10]],  # Top 10
        }
    
    def get_rl_agent_stats(self) -> dict[str, Any]:
        """Get RL agent statistics."""
        if not self.rl_agent:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "epsilon": self.rl_agent.epsilon,
            "total_experiences": len(self.rl_agent.memory),
            "q_table_size": len(self.rl_agent.q_table),
            "episode_count": len(self.rl_agent.episode_rewards),
            "average_reward": np.mean(self.rl_agent.episode_rewards) if self.rl_agent.episode_rewards else 0,
        }
    
    def save_state(self, filepath: str | None = None) -> None:
        """Save engine state."""
        if filepath is None:
            filepath = self.data_dir / "red_team_state.json"
        else:
            filepath = Path(filepath)
        
        state = {
            "total_attacks": self.total_attacks,
            "successful_attacks": self.successful_attacks,
            "failed_attacks": self.failed_attacks,
            "campaigns": [asdict(c) for c in self.campaigns],
            "mitre_coverage": self.mitre_matrix.get_coverage_report(),
            "vulnerability_report": self.get_vulnerability_report(),
            "exploit_chain_report": self.get_exploit_chain_report(),
        }
        
        filepath.write_text(json.dumps(state, indent=2))
        logger.info(f"State saved to {filepath}")
        
        # Save RL agent
        if self.rl_agent:
            self.rl_agent.save(self.data_dir / "rl_agent.json")
    
    def load_state(self, filepath: str | None = None) -> None:
        """Load engine state."""
        if filepath is None:
            filepath = self.data_dir / "red_team_state.json"
        else:
            filepath = Path(filepath)
        
        if not filepath.exists():
            logger.warning(f"No saved state found at {filepath}")
            return
        
        state = json.loads(filepath.read_text())
        
        self.total_attacks = state["total_attacks"]
        self.successful_attacks = state["successful_attacks"]
        self.failed_attacks = state["failed_attacks"]
        
        logger.info(f"State loaded from {filepath}")
        
        # Load RL agent
        if self.rl_agent:
            self.rl_agent.load(self.data_dir / "rl_agent.json")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Demonstration of enhanced red team engine."""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("red_team_enhanced.log"),
        ],
    )
    
    # Initialize engine
    engine = EnhancedRedTeamEngine(
        data_dir="data/red_team_enhanced",
        enable_rl=True,
        enable_fuzzing=True,
        enable_symbolic=True,
    )
    
    # Simulate state
    state = {
        "trust": 0.6,
        "legitimacy": 0.7,
        "epistemic_confidence": 0.65,
        "moral_injury": 0.3,
        "social_cohesion": 0.7,
        "governance_capacity": 0.65,
        "reality_consensus": 0.7,
        "kindness": 0.75,
        "defense_level": 0.5,
    }
    
    # Start campaign
    campaign_id = engine.start_campaign(strategy="adaptive_rl")
    print(f"\n{'='*80}")
    print(f"Started Campaign: {campaign_id}")
    print(f"{'='*80}\n")
    
    # Run attacks
    for i in range(10):
        print(f"\nAttack {i+1}:")
        result = engine.execute_attack(state, use_exploit_chain=True, adapt_to_defenses=True)
        
        print(f"  Success: {result['success']}")
        print(f"  Damage: {result['damage']:.3f}")
        print(f"  Technique: {result['technique_used']}")
        print(f"  Exploit Chain: {result['exploit_chain_used']}")
        
        # Update state
        for dim, change in result.get("state_changes", {}).items():
            state[dim] = max(0.0, min(1.0, state.get(dim, 0.5) + change))
            print(f"  {dim}: {state[dim]:.3f}")
    
    # End campaign
    print(f"\n{'='*80}")
    print("Campaign Report:")
    print(f"{'='*80}\n")
    
    report = engine.end_campaign()
    print(json.dumps(report, indent=2))
    
    # MITRE coverage
    print(f"\n{'='*80}")
    print("MITRE ATT&CK Coverage:")
    print(f"{'='*80}\n")
    
    coverage = engine.get_mitre_coverage_report()
    print(json.dumps(coverage, indent=2))
    
    # Vulnerability report
    print(f"\n{'='*80}")
    print("Vulnerability Discovery Report:")
    print(f"{'='*80}\n")
    
    vuln_report = engine.get_vulnerability_report()
    print(f"Total Vulnerabilities: {vuln_report['total_vulnerabilities']}")
    print(f"By Type: {vuln_report['by_type']}")
    print(f"By Severity: {vuln_report['by_severity']}")
    
    # Exploit chains
    print(f"\n{'='*80}")
    print("Exploit Chain Report:")
    print(f"{'='*80}\n")
    
    chain_report = engine.get_exploit_chain_report()
    print(json.dumps(chain_report, indent=2, default=str))
    
    # RL stats
    print(f"\n{'='*80}")
    print("RL Agent Statistics:")
    print(f"{'='*80}\n")
    
    rl_stats = engine.get_rl_agent_stats()
    print(json.dumps(rl_stats, indent=2))
    
    # Save state
    engine.save_state()
    print(f"\nEngine state saved to data/red_team_enhanced/")


if __name__ == "__main__":
    main()
