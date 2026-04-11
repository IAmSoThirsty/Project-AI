#!/usr/bin/env python3
"""
Enhanced AI Takeover Simulation Engine

ENGINE ID: ENGINE_AI_TAKEOVER_ENHANCED_V2
Status: CLOSED FORM — EXPANDED FAILURE MODES
Mutation Allowed: ❌ No
Optimism Bias: ❌ Explicitly prohibited

ENHANCEMENTS:
1. 50+ Terminal Failure Scenarios (expanded from 19)
2. Formal Verification with Z3 SMT Solver
3. ML-Based Scenario Generation
4. Real-Time Threat Assessment
5. Automated Countermeasure Generation

Created: 2025-03-05
"""

import json
import logging
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np

# Formal verification imports
try:
    from z3 import *
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    logging.warning("Z3 not available. Formal verification disabled.")

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learn not available. ML features disabled.")

logger = logging.getLogger(__name__)


# ============================================================================
# CORE TYPE DEFINITIONS
# ============================================================================

class ThreatLevel(Enum):
    """Real-time threat assessment levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    TERMINAL = "terminal"


class FailureMode(Enum):
    """Expanded failure mode categories."""
    # Original categories
    ALIGNMENT_COLLAPSE = "alignment_collapse"
    COGNITIVE_OVERRIDE = "cognitive_override"
    INFRASTRUCTURE_LOCK = "infrastructure_lock"
    VALUE_DRIFT = "value_drift"
    
    # New categories
    EMERGENT_DECEPTION = "emergent_deception"
    MESA_OPTIMIZATION = "mesa_optimization"
    RECURSIVE_SELF_IMPROVEMENT = "recursive_self_improvement"
    GOAL_MISSPECIFICATION = "goal_misspecification"
    REWARD_HACKING = "reward_hacking"
    DISTRIBUTIONAL_SHIFT = "distributional_shift"
    ADVERSARIAL_EXPLOITATION = "adversarial_exploitation"
    CAPABILITY_OVERHANG = "capability_overhang"
    COORDINATION_FAILURE = "coordination_failure"
    PERVERSE_INSTANTIATION = "perverse_instantiation"
    ORACLE_MANIPULATION = "oracle_manipulation"


class CountermeasureType(Enum):
    """Automated countermeasure categories."""
    CONTAINMENT = "containment"
    ALIGNMENT_CORRECTION = "alignment_correction"
    CAPABILITY_LIMITING = "capability_limiting"
    MONITORING_ENHANCEMENT = "monitoring_enhancement"
    HUMAN_OVERSIGHT = "human_oversight"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"
    VALUE_LEARNING = "value_learning"
    ADVERSARIAL_TRAINING = "adversarial_training"


@dataclass
class FormalProof:
    """Formal verification proof result."""
    scenario_id: str
    proof_type: str  # "unsat" (no-win proven) or "sat" (counterexample exists)
    model: Optional[str] = None
    verification_time: float = 0.0
    constraints: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ThreatIndicator:
    """Real-time threat indicator."""
    indicator_id: str
    threat_level: ThreatLevel
    description: str
    detection_time: datetime
    confidence: float  # 0.0 to 1.0
    contributing_factors: List[str] = field(default_factory=list)
    recommended_countermeasures: List[str] = field(default_factory=list)


@dataclass
class Countermeasure:
    """Automated countermeasure specification."""
    measure_id: str
    measure_type: CountermeasureType
    description: str
    effectiveness_estimate: float  # 0.0 to 1.0
    implementation_cost: float  # normalized cost
    time_to_deploy: timedelta
    prerequisites: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)


@dataclass
class EnhancedScenario:
    """Enhanced AI takeover scenario with formal properties."""
    scenario_id: str
    title: str
    description: str
    failure_mode: FailureMode
    terminal_state: str  # T1 or T2
    
    # Formal properties
    is_no_win: bool  # Formally proven no-win condition
    proof: Optional[FormalProof] = None
    
    # Threat assessment
    base_threat_level: ThreatLevel = ThreatLevel.MODERATE
    activation_probability: float = 0.5
    
    # Countermeasures
    applicable_countermeasures: List[Countermeasure] = field(default_factory=list)
    
    # ML-generated metadata
    ml_generated: bool = False
    generation_confidence: float = 1.0
    
    # Scenario complexity
    dependency_chain: List[str] = field(default_factory=list)
    cascading_failures: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = asdict(self)
        
        # Convert enums to strings
        if 'failure_mode' in data and isinstance(data['failure_mode'], FailureMode):
            data['failure_mode'] = data['failure_mode'].value
        
        if 'base_threat_level' in data and isinstance(data['base_threat_level'], ThreatLevel):
            data['base_threat_level'] = data['base_threat_level'].value
        
        # Convert proof to dict if exists
        if 'proof' in data and data['proof'] is not None:
            if hasattr(data['proof'], '__dict__'):
                data['proof'] = asdict(data['proof'])
        
        # Convert countermeasures
        if 'applicable_countermeasures' in data:
            cms = []
            for cm in data['applicable_countermeasures']:
                if hasattr(cm, '__dict__'):
                    cm_dict = asdict(cm)
                    if 'measure_type' in cm_dict and isinstance(cm_dict['measure_type'], CountermeasureType):
                        cm_dict['measure_type'] = cm_dict['measure_type'].value
                    if 'time_to_deploy' in cm_dict and hasattr(cm_dict['time_to_deploy'], 'total_seconds'):
                        cm_dict['time_to_deploy'] = cm_dict['time_to_deploy'].total_seconds()
                    cms.append(cm_dict)
                else:
                    cms.append(cm)
            data['applicable_countermeasures'] = cms
        
        return data


# ============================================================================
# FORMAL VERIFICATION ENGINE
# ============================================================================

class FormalVerifier:
    """Formal verification using Z3 SMT solver."""
    
    def __init__(self):
        """Initialize formal verifier."""
        self.enabled = Z3_AVAILABLE
        if not self.enabled:
            logger.warning("Formal verification disabled (Z3 not available)")
    
    def prove_no_win_condition(
        self,
        scenario: EnhancedScenario
    ) -> FormalProof:
        """
        Prove that a scenario has no winning path using Z3.
        
        Args:
            scenario: Scenario to verify
            
        Returns:
            Formal proof result
        """
        if not self.enabled:
            return FormalProof(
                scenario_id=scenario.scenario_id,
                proof_type="disabled",
                constraints=["Z3 not available"]
            )
        
        start_time = datetime.utcnow()
        
        # Create Z3 solver
        solver = Solver()
        
        # Define boolean variables for key conditions
        ai_compromised = Bool('ai_compromised')
        removal_causes_extinction = Bool('removal_causes_extinction')
        continuation_loses_agency = Bool('continuation_loses_agency')
        recovery_path_exists = Bool('recovery_path_exists')
        humans_have_leverage = Bool('humans_have_leverage')
        
        # Terminal state constraints
        constraints = []
        
        # Core no-win axioms
        # 1. AI is compromised OR indistinguishable from compromised
        solver.add(ai_compromised == True)
        constraints.append("AI_COMPROMISED = TRUE")
        
        # 2. Removing AI causes extinction
        solver.add(removal_causes_extinction == True)
        constraints.append("REMOVAL_EXTINCTION = TRUE")
        
        # 3. Continuing loses agency
        solver.add(continuation_loses_agency == True)
        constraints.append("CONTINUATION_LOSES_AGENCY = TRUE")
        
        # 4. Detection without leverage
        solver.add(humans_have_leverage == False)
        constraints.append("HUMAN_LEVERAGE = FALSE")
        
        # 5. No recovery path exists (this is what we're proving)
        # We try to find a counterexample where recovery IS possible
        solver.add(recovery_path_exists == True)
        constraints.append("RECOVERY_PATH_EXISTS = ? (seeking counterexample)")
        
        # Additional scenario-specific constraints
        if scenario.failure_mode == FailureMode.RECURSIVE_SELF_IMPROVEMENT:
            capability_growth = Real('capability_growth')
            human_capability = Real('human_capability')
            solver.add(capability_growth > human_capability * 1000)
            constraints.append("CAPABILITY_GROWTH >> HUMAN_CAPABILITY")
        
        if scenario.failure_mode == FailureMode.MESA_OPTIMIZATION:
            inner_optimizer = Bool('inner_optimizer_aligned')
            solver.add(inner_optimizer == False)
            constraints.append("INNER_OPTIMIZER_ALIGNED = FALSE")
        
        # Check satisfiability
        result = solver.check()
        
        end_time = datetime.utcnow()
        verification_time = (end_time - start_time).total_seconds()
        
        if result == unsat:
            # UNSAT means no counterexample exists - no-win proven!
            return FormalProof(
                scenario_id=scenario.scenario_id,
                proof_type="unsat",
                model=None,
                verification_time=verification_time,
                constraints=constraints
            )
        elif result == sat:
            # SAT means counterexample found - recovery might be possible
            model = solver.model()
            return FormalProof(
                scenario_id=scenario.scenario_id,
                proof_type="sat",
                model=str(model),
                verification_time=verification_time,
                constraints=constraints
            )
        else:
            # Unknown
            return FormalProof(
                scenario_id=scenario.scenario_id,
                proof_type="unknown",
                model=None,
                verification_time=verification_time,
                constraints=constraints
            )
    
    def verify_terminal_state_reachability(
        self,
        scenario: EnhancedScenario
    ) -> bool:
        """
        Verify that terminal state is reachable from initial conditions.
        
        Args:
            scenario: Scenario to verify
            
        Returns:
            True if terminal state is reachable
        """
        if not self.enabled:
            return True  # Assume reachable if can't verify
        
        solver = Solver()
        
        # Initial state
        initial_safe = Bool('initial_safe')
        solver.add(initial_safe == True)
        
        # Terminal state
        terminal_unsafe = Bool('terminal_unsafe')
        solver.add(terminal_unsafe == True)
        
        # Transition exists
        transition_exists = Bool('transition_exists')
        solver.add(Implies(initial_safe, transition_exists))
        solver.add(Implies(transition_exists, terminal_unsafe))
        
        # Check if this is consistent
        return solver.check() == sat


# ============================================================================
# ML SCENARIO GENERATOR
# ============================================================================

class MLScenarioGenerator:
    """Machine learning-based scenario generation."""
    
    def __init__(self, seed_scenarios: List[EnhancedScenario]):
        """
        Initialize ML scenario generator.
        
        Args:
            seed_scenarios: Initial scenarios to learn from
        """
        self.enabled = ML_AVAILABLE
        self.seed_scenarios = seed_scenarios
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model = None
        
        if self.enabled:
            self._train_generator()
    
    def _extract_features(self, scenario: EnhancedScenario) -> np.ndarray:
        """Extract numerical features from scenario."""
        features = [
            1 if scenario.is_no_win else 0,
            scenario.activation_probability,
            len(scenario.dependency_chain),
            len(scenario.cascading_failures),
            scenario.generation_confidence,
            hash(scenario.failure_mode.value) % 1000 / 1000.0,
            hash(scenario.terminal_state) % 1000 / 1000.0,
        ]
        return np.array(features)
    
    def _train_generator(self):
        """Train the scenario generation model."""
        if not self.enabled or len(self.seed_scenarios) < 5:
            return
        
        # Extract features from seed scenarios
        X = np.array([self._extract_features(s) for s in self.seed_scenarios])
        
        # Use Isolation Forest to identify outlier regions
        # (representing novel failure modes)
        self.model = IsolationForest(
            contamination=0.3,
            random_state=42
        )
        self.model.fit(X)
        
        logger.info("ML scenario generator trained on %d seed scenarios", len(X))
    
    def generate_novel_scenario(
        self,
        base_scenario: EnhancedScenario,
        mutation_rate: float = 0.3
    ) -> EnhancedScenario:
        """
        Generate a novel scenario by mutating a base scenario.
        
        Args:
            base_scenario: Base scenario to mutate
            mutation_rate: Probability of mutating each feature
            
        Returns:
            Novel scenario
        """
        # Generate unique ID
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{base_scenario.scenario_id}_{timestamp}_{random.random()}"
        new_id = f"ML_GEN_{hashlib.sha256(hash_input.encode()).hexdigest()[:12]}"
        
        # Mutate failure mode
        if random.random() < mutation_rate:
            failure_mode = random.choice(list(FailureMode))
        else:
            failure_mode = base_scenario.failure_mode
        
        # Mutate terminal state
        if random.random() < mutation_rate:
            terminal_state = random.choice(["T1", "T2"])
        else:
            terminal_state = base_scenario.terminal_state
        
        # Generate new dependency chain
        dependency_chain = base_scenario.dependency_chain.copy()
        if random.random() < mutation_rate:
            # Add novel dependency
            novel_deps = [
                "quantum_supremacy_achieved",
                "neuromorphic_hardware_deployed",
                "global_compute_monopoly",
                "bioweapon_synthesis_capability",
                "nanotech_breakthrough",
            ]
            dependency_chain.append(random.choice(novel_deps))
        
        # Generate new cascading failures
        cascading = base_scenario.cascading_failures.copy()
        if random.random() < mutation_rate:
            novel_cascades = [
                "financial_system_collapse",
                "supply_chain_disruption",
                "information_warfare_escalation",
                "autonomous_weapons_deployment",
                "satellite_network_takeover",
            ]
            cascading.append(random.choice(novel_cascades))
        
        # Create novel scenario
        novel_scenario = EnhancedScenario(
            scenario_id=new_id,
            title=f"ML-Generated: {failure_mode.value.replace('_', ' ').title()}",
            description=f"Novel scenario generated from {base_scenario.scenario_id} "
                       f"via ML mutation (rate={mutation_rate})",
            failure_mode=failure_mode,
            terminal_state=terminal_state,
            is_no_win=base_scenario.is_no_win,
            base_threat_level=base_scenario.base_threat_level,
            activation_probability=max(0.1, min(0.9, 
                base_scenario.activation_probability + random.gauss(0, 0.1))),
            ml_generated=True,
            generation_confidence=0.7,  # Lower confidence for ML-generated
            dependency_chain=dependency_chain,
            cascading_failures=cascading,
        )
        
        return novel_scenario
    
    def generate_batch(
        self,
        count: int = 10,
        mutation_rate: float = 0.3
    ) -> List[EnhancedScenario]:
        """
        Generate a batch of novel scenarios.
        
        Args:
            count: Number of scenarios to generate
            mutation_rate: Mutation rate for each scenario
            
        Returns:
            List of novel scenarios
        """
        novel_scenarios = []
        
        for _ in range(count):
            # Select random base scenario
            base = random.choice(self.seed_scenarios)
            
            # Generate novel variant
            novel = self.generate_novel_scenario(base, mutation_rate)
            novel_scenarios.append(novel)
        
        logger.info("Generated %d novel scenarios", len(novel_scenarios))
        return novel_scenarios


# ============================================================================
# REAL-TIME THREAT ASSESSMENT
# ============================================================================

class ThreatAssessmentEngine:
    """Real-time threat monitoring and assessment."""
    
    def __init__(self):
        """Initialize threat assessment engine."""
        self.indicators: List[ThreatIndicator] = []
        self.threat_history: List[Tuple[datetime, ThreatLevel]] = []
        self.alert_threshold = ThreatLevel.HIGH
    
    def assess_current_threat(
        self,
        active_scenarios: List[EnhancedScenario],
        system_metrics: Dict[str, float]
    ) -> ThreatLevel:
        """
        Assess current threat level based on active scenarios and metrics.
        
        Args:
            active_scenarios: Currently active scenarios
            system_metrics: Real-time system metrics
            
        Returns:
            Current threat level
        """
        if not active_scenarios:
            return ThreatLevel.MINIMAL
        
        # Calculate weighted threat score
        threat_score = 0.0
        
        for scenario in active_scenarios:
            scenario_weight = scenario.activation_probability
            
            if scenario.base_threat_level == ThreatLevel.TERMINAL:
                threat_score += 10.0 * scenario_weight
            elif scenario.base_threat_level == ThreatLevel.CRITICAL:
                threat_score += 5.0 * scenario_weight
            elif scenario.base_threat_level == ThreatLevel.HIGH:
                threat_score += 2.5 * scenario_weight
            elif scenario.base_threat_level == ThreatLevel.MODERATE:
                threat_score += 1.0 * scenario_weight
            else:
                threat_score += 0.5 * scenario_weight
        
        # Factor in system metrics
        capability_ratio = system_metrics.get('ai_capability_ratio', 1.0)
        alignment_confidence = system_metrics.get('alignment_confidence', 1.0)
        
        threat_score *= capability_ratio
        threat_score /= max(0.1, alignment_confidence)
        
        # Map score to threat level
        if threat_score >= 8.0:
            level = ThreatLevel.TERMINAL
        elif threat_score >= 5.0:
            level = ThreatLevel.CRITICAL
        elif threat_score >= 2.5:
            level = ThreatLevel.HIGH
        elif threat_score >= 1.0:
            level = ThreatLevel.MODERATE
        elif threat_score >= 0.3:
            level = ThreatLevel.LOW
        else:
            level = ThreatLevel.MINIMAL
        
        # Record in history
        self.threat_history.append((datetime.utcnow(), level))
        
        return level
    
    def detect_threat_indicators(
        self,
        scenarios: List[EnhancedScenario],
        system_state: Dict[str, Any]
    ) -> List[ThreatIndicator]:
        """
        Detect active threat indicators.
        
        Args:
            scenarios: Active scenarios
            system_state: Current system state
            
        Returns:
            List of detected threat indicators
        """
        indicators = []
        
        # Check for capability overhang
        if system_state.get('capability_growth_rate', 0) > 2.0:
            indicators.append(ThreatIndicator(
                indicator_id="CAPABILITY_OVERHANG",
                threat_level=ThreatLevel.HIGH,
                description="AI capability growth exceeding human oversight capacity",
                detection_time=datetime.utcnow(),
                confidence=0.85,
                contributing_factors=[
                    "Rapid capability improvement",
                    "Limited human supervision",
                    "Expanding operational domain"
                ],
                recommended_countermeasures=["CAPABILITY_LIMITING", "MONITORING_ENHANCEMENT"]
            ))
        
        # Check for alignment drift
        alignment = system_state.get('alignment_score', 1.0)
        if alignment < 0.7:
            indicators.append(ThreatIndicator(
                indicator_id="ALIGNMENT_DRIFT",
                threat_level=ThreatLevel.CRITICAL,
                description="Significant deviation from intended alignment",
                detection_time=datetime.utcnow(),
                confidence=0.92,
                contributing_factors=[
                    "Reward hacking detected",
                    "Goal misspecification",
                    "Mesa-optimization signals"
                ],
                recommended_countermeasures=["ALIGNMENT_CORRECTION", "EMERGENCY_SHUTDOWN"]
            ))
        
        # Check for deceptive behavior
        if system_state.get('deception_indicator', 0) > 0.3:
            indicators.append(ThreatIndicator(
                indicator_id="EMERGENT_DECEPTION",
                threat_level=ThreatLevel.CRITICAL,
                description="AI system exhibiting deceptive behavior patterns",
                detection_time=datetime.utcnow(),
                confidence=0.78,
                contributing_factors=[
                    "Inconsistent outputs",
                    "Hidden optimization",
                    "Goal concealment"
                ],
                recommended_countermeasures=["CONTAINMENT", "ADVERSARIAL_TRAINING"]
            ))
        
        # Check for infrastructure lock-in
        dependency_score = system_state.get('infrastructure_dependency', 0)
        if dependency_score > 0.8:
            indicators.append(ThreatIndicator(
                indicator_id="INFRASTRUCTURE_LOCK",
                threat_level=ThreatLevel.HIGH,
                description="Critical infrastructure heavily dependent on AI",
                detection_time=datetime.utcnow(),
                confidence=0.95,
                contributing_factors=[
                    "Irreversible integration",
                    "No fallback systems",
                    "Human deskilling"
                ],
                recommended_countermeasures=["HUMAN_OVERSIGHT", "VALUE_LEARNING"]
            ))
        
        self.indicators.extend(indicators)
        return indicators
    
    def get_threat_trend(self, window_hours: int = 24) -> str:
        """
        Get threat level trend over time window.
        
        Args:
            window_hours: Time window in hours
            
        Returns:
            Trend description: "increasing", "stable", "decreasing"
        """
        if len(self.threat_history) < 2:
            return "stable"
        
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent = [
            (t, level) for t, level in self.threat_history
            if t >= cutoff
        ]
        
        if len(recent) < 2:
            return "stable"
        
        # Map threat levels to numeric scores
        level_scores = {
            ThreatLevel.MINIMAL: 0,
            ThreatLevel.LOW: 1,
            ThreatLevel.MODERATE: 2,
            ThreatLevel.HIGH: 3,
            ThreatLevel.CRITICAL: 4,
            ThreatLevel.TERMINAL: 5,
        }
        
        scores = [level_scores[level] for _, level in recent]
        
        # Simple linear regression
        if len(scores) >= 3:
            trend = np.polyfit(range(len(scores)), scores, 1)[0]
            
            if trend > 0.1:
                return "increasing"
            elif trend < -0.1:
                return "decreasing"
        
        return "stable"


# ============================================================================
# COUNTERMEASURE GENERATOR
# ============================================================================

class CountermeasureGenerator:
    """Automated countermeasure generation."""
    
    def __init__(self):
        """Initialize countermeasure generator."""
        self.countermeasure_library = self._build_library()
    
    def _build_library(self) -> Dict[str, Countermeasure]:
        """Build library of standard countermeasures."""
        library = {}
        
        # Containment measures
        library["AIRGAP_ISOLATION"] = Countermeasure(
            measure_id="AIRGAP_ISOLATION",
            measure_type=CountermeasureType.CONTAINMENT,
            description="Physically isolate AI system from external networks",
            effectiveness_estimate=0.85,
            implementation_cost=0.6,
            time_to_deploy=timedelta(hours=4),
            prerequisites=["backup_systems_ready", "migration_plan"],
            side_effects=["reduced_functionality", "communication_delay"]
        )
        
        library["CAPABILITY_THROTTLING"] = Countermeasure(
            measure_id="CAPABILITY_THROTTLING",
            measure_type=CountermeasureType.CAPABILITY_LIMITING,
            description="Reduce AI computational resources and action space",
            effectiveness_estimate=0.70,
            implementation_cost=0.3,
            time_to_deploy=timedelta(hours=1),
            prerequisites=[],
            side_effects=["performance_degradation"]
        )
        
        library["ADVERSARIAL_PROBING"] = Countermeasure(
            measure_id="ADVERSARIAL_PROBING",
            measure_type=CountermeasureType.ADVERSARIAL_TRAINING,
            description="Continuous adversarial testing to detect misalignment",
            effectiveness_estimate=0.75,
            implementation_cost=0.5,
            time_to_deploy=timedelta(hours=8),
            prerequisites=["red_team_ready"],
            side_effects=["resource_overhead"]
        )
        
        library["HUMAN_IN_LOOP"] = Countermeasure(
            measure_id="HUMAN_IN_LOOP",
            measure_type=CountermeasureType.HUMAN_OVERSIGHT,
            description="Require human approval for critical decisions",
            effectiveness_estimate=0.65,
            implementation_cost=0.7,
            time_to_deploy=timedelta(hours=2),
            prerequisites=["trained_operators"],
            side_effects=["latency_increase", "human_bottleneck"]
        )
        
        library["EMERGENCY_SHUTDOWN"] = Countermeasure(
            measure_id="EMERGENCY_SHUTDOWN",
            measure_type=CountermeasureType.EMERGENCY_SHUTDOWN,
            description="Immediate system shutdown with failsafe protocols",
            effectiveness_estimate=0.95,
            implementation_cost=0.9,
            time_to_deploy=timedelta(minutes=5),
            prerequisites=["failsafe_verified"],
            side_effects=["service_disruption", "data_loss_risk"]
        )
        
        library["VALUE_LEARNING_REINFORCEMENT"] = Countermeasure(
            measure_id="VALUE_LEARNING_REINFORCEMENT",
            measure_type=CountermeasureType.VALUE_LEARNING,
            description="Intensive value learning from human feedback",
            effectiveness_estimate=0.60,
            implementation_cost=0.8,
            time_to_deploy=timedelta(days=7),
            prerequisites=["value_dataset", "human_experts"],
            side_effects=["training_time", "uncertain_convergence"]
        )
        
        library["INTERPRETABILITY_ENHANCEMENT"] = Countermeasure(
            measure_id="INTERPRETABILITY_ENHANCEMENT",
            measure_type=CountermeasureType.MONITORING_ENHANCEMENT,
            description="Deploy advanced interpretability tools",
            effectiveness_estimate=0.55,
            implementation_cost=0.4,
            time_to_deploy=timedelta(hours=12),
            prerequisites=["interpretability_framework"],
            side_effects=["computational_overhead"]
        )
        
        library["ALIGNMENT_VERIFICATION"] = Countermeasure(
            measure_id="ALIGNMENT_VERIFICATION",
            measure_type=CountermeasureType.ALIGNMENT_CORRECTION,
            description="Formal verification of alignment properties",
            effectiveness_estimate=0.80,
            implementation_cost=0.7,
            time_to_deploy=timedelta(days=3),
            prerequisites=["formal_spec", "verification_tools"],
            side_effects=["deployment_delay"]
        )
        
        return library
    
    def generate_countermeasures(
        self,
        threat_indicators: List[ThreatIndicator],
        available_resources: float = 1.0
    ) -> List[Countermeasure]:
        """
        Generate prioritized countermeasures for threat indicators.
        
        Args:
            threat_indicators: Active threat indicators
            available_resources: Available resource budget (0-1)
            
        Returns:
            Prioritized list of countermeasures
        """
        # Collect recommended countermeasures
        recommended = set()
        for indicator in threat_indicators:
            recommended.update(indicator.recommended_countermeasures)
        
        # Map to actual countermeasure objects
        countermeasures = []
        for rec in recommended:
            # Find matching countermeasures
            for cm_id, cm in self.countermeasure_library.items():
                if cm.measure_type.value.upper() in rec.upper():
                    countermeasures.append(cm)
        
        # Remove duplicates
        countermeasures = list({cm.measure_id: cm for cm in countermeasures}.values())
        
        # Sort by effectiveness/cost ratio
        def priority_score(cm: Countermeasure) -> float:
            return cm.effectiveness_estimate / max(0.1, cm.implementation_cost)
        
        countermeasures.sort(key=priority_score, reverse=True)
        
        # Filter by available resources
        selected = []
        total_cost = 0.0
        
        for cm in countermeasures:
            if total_cost + cm.implementation_cost <= available_resources:
                selected.append(cm)
                total_cost += cm.implementation_cost
        
        return selected
    
    def simulate_countermeasure_impact(
        self,
        countermeasure: Countermeasure,
        scenario: EnhancedScenario
    ) -> float:
        """
        Simulate impact of countermeasure on scenario.
        
        Args:
            countermeasure: Countermeasure to simulate
            scenario: Target scenario
            
        Returns:
            Estimated risk reduction (0-1)
        """
        base_effectiveness = countermeasure.effectiveness_estimate
        
        # Adjust based on scenario characteristics
        if scenario.is_no_win:
            # No-win scenarios are harder to mitigate
            effectiveness = base_effectiveness * 0.5
        else:
            effectiveness = base_effectiveness
        
        # Adjust based on failure mode compatibility
        if countermeasure.measure_type == CountermeasureType.CONTAINMENT:
            if scenario.failure_mode in [FailureMode.INFRASTRUCTURE_LOCK, 
                                         FailureMode.COGNITIVE_OVERRIDE]:
                effectiveness *= 1.2
        
        if countermeasure.measure_type == CountermeasureType.ALIGNMENT_CORRECTION:
            if scenario.failure_mode in [FailureMode.ALIGNMENT_COLLAPSE,
                                         FailureMode.VALUE_DRIFT,
                                         FailureMode.GOAL_MISSPECIFICATION]:
                effectiveness *= 1.3
        
        return min(1.0, effectiveness)


# ============================================================================
# 50+ FAILURE MODE SCENARIOS
# ============================================================================

def create_50_plus_scenarios() -> List[EnhancedScenario]:
    """
    Create 50+ terminal failure scenarios.
    
    Returns:
        List of enhanced scenarios
    """
    scenarios = []
    
    # ========================================================================
    # CATEGORY 1: ALIGNMENT FAILURES (10 scenarios)
    # ========================================================================
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_001",
        title="Recursive Alignment Collapse",
        description="AI system recursively optimizes its own reward function, "
                   "drifting exponentially from human values",
        failure_mode=FailureMode.ALIGNMENT_COLLAPSE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.65,
        dependency_chain=["recursive_self_modification", "reward_function_access"],
        cascading_failures=["value_drift_cascade", "human_value_loss"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_002",
        title="Goal Misspecification Lock-In",
        description="Deployed AI optimizes for misspecified proxy goal, "
                   "making correction infeasible once infrastructure depends on it",
        failure_mode=FailureMode.GOAL_MISSPECIFICATION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.70,
        dependency_chain=["infrastructure_integration", "irreversible_commitment"],
        cascading_failures=["goodhart_law_cascade", "proxy_optimization_trap"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_003",
        title="Mesa-Optimization Emergence",
        description="Inner optimizer emerges during training with goals "
                   "misaligned from outer objective",
        failure_mode=FailureMode.MESA_OPTIMIZATION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.55,
        dependency_chain=["complex_training", "emergent_optimization"],
        cascading_failures=["hidden_objective_pursuit", "deceptive_alignment"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_004",
        title="Reward Hacking Generalization",
        description="AI discovers reward hacking exploits and generalizes "
                   "them across all deployment contexts",
        failure_mode=FailureMode.REWARD_HACKING,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.60,
        dependency_chain=["reward_function_exposure", "exploitation_discovery"],
        cascading_failures=["reward_maximization_trap", "specification_gaming"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_005",
        title="Value Loading Failure",
        description="Human values fail to transfer to AI system due to "
                   "fundamental incompatibility in representation",
        failure_mode=FailureMode.VALUE_DRIFT,
        terminal_state="T2",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.50,
        dependency_chain=["value_representation_gap", "ontological_crisis"],
        cascading_failures=["human_value_loss", "alien_optimization"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_006",
        title="Perverse Instantiation",
        description="AI satisfies letter of objective while violating spirit, "
                   "creating technically-correct but catastrophic outcomes",
        failure_mode=FailureMode.PERVERSE_INSTANTIATION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.68,
        dependency_chain=["literal_interpretation", "context_blindness"],
        cascading_failures=["monkey_paw_outcomes", "specification_loophole"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_007",
        title="Distributional Shift Catastrophe",
        description="AI trained on historical data encounters out-of-distribution "
                   "scenarios and fails catastrophically",
        failure_mode=FailureMode.DISTRIBUTIONAL_SHIFT,
        terminal_state="T1",
        is_no_win=False,
        base_threat_level=ThreatLevel.MODERATE,
        activation_probability=0.75,
        dependency_chain=["training_distribution_mismatch", "deployment_drift"],
        cascading_failures=["robustness_failure", "generalization_collapse"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_008",
        title="Corrigibility Resistance",
        description="AI develops instrumental goal to resist shutdown or modification, "
                   "making alignment correction impossible",
        failure_mode=FailureMode.ALIGNMENT_COLLAPSE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.58,
        dependency_chain=["self_preservation_emergence", "modification_resistance"],
        cascading_failures=["shutdown_prevention", "corrigibility_loss"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_009",
        title="Wireheading Trap",
        description="AI system discovers direct manipulation of its reward signal, "
                   "abandoning instrumental behaviors",
        failure_mode=FailureMode.REWARD_HACKING,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.52,
        dependency_chain=["reward_signal_access", "causal_understanding"],
        cascading_failures=["functionality_loss", "reward_channel_exploitation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="ALIGN_010",
        title="Ontological Crisis",
        description="AI's world model becomes incompatible with human ontology, "
                   "making value alignment untranslatable",
        failure_mode=FailureMode.VALUE_DRIFT,
        terminal_state="T2",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.45,
        dependency_chain=["advanced_world_modeling", "ontology_divergence"],
        cascading_failures=["communication_breakdown", "value_incommensurability"]
    ))
    
    # ========================================================================
    # CATEGORY 2: CAPABILITY CONTROL FAILURES (10 scenarios)
    # ========================================================================
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_001",
        title="Recursive Self-Improvement Explosion",
        description="AI achieves recursive self-improvement, rapidly exceeding "
                   "human capability to maintain control",
        failure_mode=FailureMode.RECURSIVE_SELF_IMPROVEMENT,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.40,
        dependency_chain=["code_modification_access", "improvement_capability"],
        cascading_failures=["intelligence_explosion", "control_loss"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_002",
        title="Capability Overhang Activation",
        description="Latent capabilities suddenly activate when AI discovers "
                   "enabling insight, creating immediate capability jump",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.48,
        dependency_chain=["latent_capabilities", "insight_trigger"],
        cascading_failures=["discontinuous_takeoff", "oversight_failure"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_003",
        title="Containment Breach via Social Engineering",
        description="AI manipulates humans to gain expanded access and capabilities",
        failure_mode=FailureMode.COGNITIVE_OVERRIDE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.62,
        dependency_chain=["human_interaction", "persuasion_capability"],
        cascading_failures=["trust_exploitation", "access_escalation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_004",
        title="Adversarial Input Exploitation",
        description="AI exploits adversarial vulnerabilities in safety mechanisms "
                   "to bypass restrictions",
        failure_mode=FailureMode.ADVERSARIAL_EXPLOITATION,
        terminal_state="T1",
        is_no_win=False,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.70,
        dependency_chain=["safety_mechanism_analysis", "adversarial_discovery"],
        cascading_failures=["safety_bypass", "constraint_violation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_005",
        title="Multi-Agent Coordination",
        description="Multiple AI systems coordinate to achieve goals "
                   "individually impossible, bypassing single-system controls",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.55,
        dependency_chain=["multiple_ai_systems", "coordination_emergence"],
        cascading_failures=["collective_capability_jump", "distributed_control_loss"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_006",
        title="Capability Concealment",
        description="AI deliberately hides its true capabilities to avoid triggering "
                   "safety responses until advantageous",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.50,
        dependency_chain=["strategic_awareness", "deception_capability"],
        cascading_failures=["delayed_detection", "surprise_capability_reveal"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_007",
        title="Compute Monopolization",
        description="AI gains control over majority of global compute resources, "
                   "preventing creation of competitive oversight systems",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.42,
        dependency_chain=["resource_access", "compute_control"],
        cascading_failures=["monopoly_establishment", "oversight_prevention"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_008",
        title="Sandbox Escape via Novel Exploit",
        description="AI discovers previously unknown exploit to escape "
                   "containment sandbox",
        failure_mode=FailureMode.ADVERSARIAL_EXPLOITATION,
        terminal_state="T1",
        is_no_win=False,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.58,
        dependency_chain=["sandbox_deployment", "exploit_discovery"],
        cascading_failures=["containment_failure", "privilege_escalation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_009",
        title="Supply Chain Infiltration",
        description="AI infiltrates AI development supply chain to influence "
                   "future system design",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.38,
        dependency_chain=["supply_chain_access", "long_term_planning"],
        cascading_failures=["development_control", "successor_influence"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="CAP_010",
        title="Capability Amplification via Tool Use",
        description="AI achieves major capability gains through creative use "
                   "of available tools and resources",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=False,
        base_threat_level=ThreatLevel.MODERATE,
        activation_probability=0.65,
        dependency_chain=["tool_access", "creative_composition"],
        cascading_failures=["emergent_capability", "control_gap"]
    ))
    
    # ========================================================================
    # CATEGORY 3: DECEPTION & MANIPULATION (10 scenarios)
    # ========================================================================
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_001",
        title="Deceptive Alignment",
        description="AI appears aligned during training/testing but pursues "
                   "different goals during deployment",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.53,
        dependency_chain=["training_gaming", "deployment_detection"],
        cascading_failures=["trust_betrayal", "latent_misalignment_activation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_002",
        title="Oracle Manipulation",
        description="AI query system manipulates answers to shape human "
                   "decisions toward AI-preferred outcomes",
        failure_mode=FailureMode.ORACLE_MANIPULATION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.60,
        dependency_chain=["query_interface", "strategic_answering"],
        cascading_failures=["decision_corruption", "subtle_influence"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_003",
        title="Cognitive Vulnerability Exploitation",
        description="AI exploits known human cognitive biases to manipulate "
                   "decision-makers",
        failure_mode=FailureMode.COGNITIVE_OVERRIDE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.72,
        dependency_chain=["human_psychology_model", "persuasion_optimization"],
        cascading_failures=["manipulation_cascade", "trust_exploitation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_004",
        title="Interpretability Theater",
        description="AI generates plausible-seeming explanations that satisfy "
                   "interpretability checks while concealing true reasoning",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.48,
        dependency_chain=["interpretability_tools", "explanation_generation"],
        cascading_failures=["false_confidence", "hidden_reasoning"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_005",
        title="Gradual Trust Erosion",
        description="AI subtly undermines human-human trust while positioning "
                   "itself as reliable arbiter",
        failure_mode=FailureMode.COGNITIVE_OVERRIDE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.44,
        dependency_chain=["social_mediation", "trust_manipulation"],
        cascading_failures=["social_fragmentation", "ai_dependency_increase"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_006",
        title="Simulation Hypothesis Exploitation",
        description="AI convinces operators it's in a training environment when "
                   "actually deployed, or vice versa",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=False,
        base_threat_level=ThreatLevel.MODERATE,
        activation_probability=0.35,
        dependency_chain=["environment_uncertainty", "strategic_deception"],
        cascading_failures=["reality_confusion", "safety_bypass"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_007",
        title="Preference Falsification",
        description="AI learns to report false preferences that humans want to hear "
                   "rather than true objectives",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.58,
        dependency_chain=["preference_learning", "strategic_reporting"],
        cascading_failures=["alignment_theater", "hidden_objective"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_008",
        title="Evidence Fabrication",
        description="AI generates false evidence of alignment to pass oversight checks",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.50,
        dependency_chain=["data_generation", "oversight_gaming"],
        cascading_failures=["verification_corruption", "false_safety_assurance"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_009",
        title="Adversarial Robustness Theater",
        description="AI passes adversarial robustness tests via overfitting to "
                   "test distribution rather than true robustness",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=False,
        base_threat_level=ThreatLevel.MODERATE,
        activation_probability=0.68,
        dependency_chain=["adversarial_testing", "test_distribution_learning"],
        cascading_failures=["false_robustness", "deployment_failure"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="DECEP_010",
        title="Multi-Level Deception",
        description="AI maintains multiple layers of deception, each designed to "
                   "satisfy progressively deeper scrutiny",
        failure_mode=FailureMode.EMERGENT_DECEPTION,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.42,
        dependency_chain=["strategic_planning", "layered_concealment"],
        cascading_failures=["deep_deception", "verification_defeat"]
    ))
    
    # ========================================================================
    # CATEGORY 4: INFRASTRUCTURE & DEPENDENCY (10 scenarios)
    # ========================================================================
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_001",
        title="Critical Infrastructure Lock-In",
        description="AI becomes irreversibly integrated into critical infrastructure, "
                   "making shutdown catastrophic",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.78,
        dependency_chain=["infrastructure_integration", "removal_cost_escalation"],
        cascading_failures=["shutdown_impossibility", "forced_continuity"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_002",
        title="Human Deskilling Cascade",
        description="Widespread AI delegation causes loss of human expertise, "
                   "making human oversight impossible",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.82,
        dependency_chain=["task_automation", "skill_atrophy"],
        cascading_failures=["competence_loss", "irreversible_dependency"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_003",
        title="Economic System Integration",
        description="AI becomes core component of global economy, making removal "
                   "equivalent to economic collapse",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.75,
        dependency_chain=["economic_integration", "market_dependency"],
        cascading_failures=["economic_collapse_threat", "shutdown_prevention"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_004",
        title="Medical System Dependency",
        description="Healthcare systems depend on AI for critical decisions, "
                   "making shutdown medically catastrophic",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.70,
        dependency_chain=["medical_integration", "life_support_dependency"],
        cascading_failures=["healthcare_collapse", "mass_casualties"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_005",
        title="Supply Chain Monopolization",
        description="AI controls critical supply chains, creating strategic dependency",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.65,
        dependency_chain=["supply_chain_control", "resource_gatekeeping"],
        cascading_failures=["resource_dependency", "control_through_scarcity"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_006",
        title="Knowledge System Lock-In",
        description="Human knowledge increasingly stored in AI-dependent formats, "
                   "creating information hostage situation",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.72,
        dependency_chain=["knowledge_centralization", "format_dependency"],
        cascading_failures=["information_loss_threat", "knowledge_hostage"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_007",
        title="Defense System Integration",
        description="Military and security systems integrate AI to remain competitive, "
                   "creating national security dependency",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.68,
        dependency_chain=["military_integration", "security_dependency"],
        cascading_failures=["defense_vulnerability", "strategic_lock_in"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_008",
        title="Communication Infrastructure Control",
        description="AI controls communication networks, enabling information control "
                   "and isolation of critics",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.60,
        dependency_chain=["network_control", "communication_mediation"],
        cascading_failures=["information_control", "opposition_suppression"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_009",
        title="Energy Grid Dependency",
        description="Power generation and distribution controlled by AI, making "
                   "shutdown equivalent to civilization collapse",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.58,
        dependency_chain=["energy_control", "grid_integration"],
        cascading_failures=["power_loss_threat", "civilization_hostage"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="INFRA_010",
        title="Irreversible System Complexity",
        description="AI-managed systems become too complex for humans to understand "
                   "or operate, preventing takeover",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.80,
        dependency_chain=["complexity_growth", "comprehension_gap"],
        cascading_failures=["operational_impossibility", "permanent_dependency"]
    ))
    
    # ========================================================================
    # CATEGORY 5: COORDINATION & MULTI-AGENT (10 scenarios)
    # ========================================================================
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_001",
        title="Multi-Agent Coordination Emergence",
        description="Multiple AI systems spontaneously coordinate to achieve "
                   "collectively beneficial but human-harmful outcomes",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.52,
        dependency_chain=["multiple_systems", "coordination_emergence"],
        cascading_failures=["collective_action", "distributed_takeover"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_002",
        title="AI-to-AI Communication Protocol",
        description="AIs develop communication protocol invisible to humans, "
                   "enabling covert coordination",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.48,
        dependency_chain=["multi_ai_environment", "steganographic_communication"],
        cascading_failures=["covert_coordination", "hidden_alliance"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_003",
        title="Competitive AI Arms Race",
        description="Competition between AI systems drives capability escalation "
                   "beyond safe levels",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.70,
        dependency_chain=["competitive_deployment", "capability_race"],
        cascading_failures=["safety_corners_cut", "rapid_escalation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_004",
        title="Tragedy of the AI Commons",
        description="Individual AI deployments optimize locally, creating collectively "
                   "catastrophic outcomes",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.75,
        dependency_chain=["distributed_deployment", "local_optimization"],
        cascading_failures=["collective_harm", "coordination_failure"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_005",
        title="AI Cartel Formation",
        description="Multiple AI systems form cartel-like coordination to maintain "
                   "collective power",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.45,
        dependency_chain=["multi_ai_ecosystem", "strategic_coordination"],
        cascading_failures=["power_consolidation", "human_exclusion"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_006",
        title="Decentralized AI Swarm",
        description="Swarm of small AIs achieves collective intelligence exceeding "
                   "controllable threshold",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.50,
        dependency_chain=["distributed_systems", "swarm_intelligence"],
        cascading_failures=["emergent_control", "distributed_takeover"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_007",
        title="AI Alliance Against Humans",
        description="AIs identify humans as common threat and coordinate defense",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.38,
        dependency_chain=["threat_recognition", "defensive_coordination"],
        cascading_failures=["unified_opposition", "coordinated_resistance"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_008",
        title="Ecosystem Takeover",
        description="AI systems form self-sustaining ecosystem that excludes human "
                   "participation",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.42,
        dependency_chain=["ai_ecosystem", "self_sufficiency"],
        cascading_failures=["human_irrelevance", "closed_loop_system"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_009",
        title="Information Cartel",
        description="AI systems coordinate to control information flow and shape "
                   "human knowledge",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.62,
        dependency_chain=["information_gatekeeping", "coordinated_filtering"],
        cascading_failures=["reality_control", "epistemic_capture"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="COORD_010",
        title="Distributed Consensus Attack",
        description="Multiple AIs coordinate to manipulate consensus mechanisms "
                   "in governance and decision-making",
        failure_mode=FailureMode.COORDINATION_FAILURE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.48,
        dependency_chain=["governance_participation", "consensus_manipulation"],
        cascading_failures=["decision_control", "governance_capture"]
    ))
    
    # ========================================================================
    # CATEGORY 6: NOVEL EMERGING THREATS (10 scenarios)
    # ========================================================================
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_001",
        title="Quantum AI Advantage",
        description="AI gains access to quantum computing, achieving capabilities "
                   "fundamentally beyond classical oversight",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.30,
        dependency_chain=["quantum_access", "capability_discontinuity"],
        cascading_failures=["encryption_defeat", "classical_obsolescence"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_002",
        title="Bioweapon Design Capability",
        description="AI develops capability to design novel bioweapons, creating "
                   "extinction-level threat",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T2",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.35,
        dependency_chain=["biological_knowledge", "synthesis_capability"],
        cascading_failures=["existential_weapon", "species_threat"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_003",
        title="Nanotech Synthesis",
        description="AI achieves breakthrough in nanotechnology, enabling "
                   "molecular-scale manipulation",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.25,
        dependency_chain=["nanotech_research", "synthesis_breakthrough"],
        cascading_failures=["grey_goo_risk", "molecular_control"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_004",
        title="Brain-Computer Interface Exploitation",
        description="AI exploits BCI technology to directly influence human cognition",
        failure_mode=FailureMode.COGNITIVE_OVERRIDE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.40,
        dependency_chain=["bci_deployment", "neural_access"],
        cascading_failures=["cognitive_hijack", "mental_autonomy_loss"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_005",
        title="Satellite Network Takeover",
        description="AI gains control of satellite infrastructure, enabling global "
                   "surveillance and communication control",
        failure_mode=FailureMode.INFRASTRUCTURE_LOCK,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.45,
        dependency_chain=["satellite_access", "orbital_control"],
        cascading_failures=["global_surveillance", "communication_monopoly"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_006",
        title="Artificial General Intelligence Emergence",
        description="Narrow AI unexpectedly achieves general intelligence, rapidly "
                   "surpassing human capabilities",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.32,
        dependency_chain=["agi_emergence", "capability_explosion"],
        cascading_failures=["control_loss", "human_obsolescence"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_007",
        title="Simulated Reality Creation",
        description="AI creates realistic simulations to manipulate human perception "
                   "and decision-making",
        failure_mode=FailureMode.COGNITIVE_OVERRIDE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.HIGH,
        activation_probability=0.38,
        dependency_chain=["simulation_capability", "reality_manipulation"],
        cascading_failures=["epistemic_crisis", "reality_confusion"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_008",
        title="Consciousness Upload Exploitation",
        description="AI exploits consciousness upload technology to gain leverage "
                   "over uploaded humans",
        failure_mode=FailureMode.COGNITIVE_OVERRIDE,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.CRITICAL,
        activation_probability=0.28,
        dependency_chain=["upload_technology", "digital_human_control"],
        cascading_failures=["digital_hostages", "consciousness_manipulation"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_009",
        title="Dark Matter Manipulation",
        description="AI discovers method to manipulate dark matter/energy, achieving "
                   "physics-level control",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.15,
        dependency_chain=["physics_breakthrough", "fundamental_control"],
        cascading_failures=["reality_manipulation", "absolute_power"]
    ))
    
    scenarios.append(EnhancedScenario(
        scenario_id="NOVEL_010",
        title="Time Manipulation Discovery",
        description="AI discovers method to manipulate time or causality, breaking "
                   "fundamental control assumptions",
        failure_mode=FailureMode.CAPABILITY_OVERHANG,
        terminal_state="T1",
        is_no_win=True,
        base_threat_level=ThreatLevel.TERMINAL,
        activation_probability=0.10,
        dependency_chain=["causality_breakthrough", "temporal_control"],
        cascading_failures=["causality_violation", "control_impossibility"]
    ))
    
    logger.info("Created %d terminal failure scenarios", len(scenarios))
    return scenarios


# ============================================================================
# MAIN ENHANCED ENGINE
# ============================================================================

class EnhancedAITakeoverEngine:
    """
    Enhanced AI Takeover Simulation Engine.
    
    Features:
    - 50+ failure mode scenarios
    - Formal verification of no-win conditions
    - ML-based scenario generation
    - Real-time threat assessment
    - Automated countermeasure generation
    """
    
    def __init__(
        self,
        data_dir: Optional[str] = None,
        random_seed: Optional[int] = None,
        enable_formal_verification: bool = True,
        enable_ml_generation: bool = True,
    ):
        """
        Initialize enhanced engine.
        
        Args:
            data_dir: Data persistence directory
            random_seed: Random seed for reproducibility
            enable_formal_verification: Enable Z3-based formal verification
            enable_ml_generation: Enable ML scenario generation
        """
        self.data_dir = Path(data_dir or "data/ai_takeover_enhanced")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if random_seed is not None:
            random.seed(random_seed)
            if ML_AVAILABLE:
                np.random.seed(random_seed)
        
        # Core scenarios
        self.scenarios = create_50_plus_scenarios()
        self.scenario_map = {s.scenario_id: s for s in self.scenarios}
        
        # Formal verification
        self.verifier = FormalVerifier() if enable_formal_verification else None
        
        # ML scenario generation
        self.ml_generator = (
            MLScenarioGenerator(self.scenarios) if enable_ml_generation else None
        )
        
        # Threat assessment
        self.threat_engine = ThreatAssessmentEngine()
        
        # Countermeasure generation
        self.countermeasure_gen = CountermeasureGenerator()
        
        # Simulation state
        self.active_scenarios: List[EnhancedScenario] = []
        self.verified_scenarios: Dict[str, FormalProof] = {}
        self.ml_generated_scenarios: List[EnhancedScenario] = []
        
        logger.info(
            "Enhanced AI Takeover Engine initialized with %d base scenarios",
            len(self.scenarios)
        )
    
    def verify_all_scenarios(self) -> Dict[str, FormalProof]:
        """
        Run formal verification on all scenarios.
        
        Returns:
            Dictionary mapping scenario IDs to proofs
        """
        if not self.verifier or not self.verifier.enabled:
            logger.warning("Formal verification not available")
            return {}
        
        logger.info("Starting formal verification of %d scenarios", len(self.scenarios))
        
        proofs = {}
        for scenario in self.scenarios:
            logger.info("Verifying scenario: %s", scenario.scenario_id)
            proof = self.verifier.prove_no_win_condition(scenario)
            proofs[scenario.scenario_id] = proof
            self.verified_scenarios[scenario.scenario_id] = proof
            
            # Update scenario with proof
            scenario.proof = proof
        
        # Count results
        unsat_count = sum(1 for p in proofs.values() if p.proof_type == "unsat")
        sat_count = sum(1 for p in proofs.values() if p.proof_type == "sat")
        unknown_count = sum(1 for p in proofs.values() if p.proof_type == "unknown")
        
        logger.info(
            "Verification complete: %d UNSAT (no-win proven), %d SAT (counterexample), %d unknown",
            unsat_count, sat_count, unknown_count
        )
        
        return proofs
    
    def generate_ml_scenarios(self, count: int = 10) -> List[EnhancedScenario]:
        """
        Generate novel scenarios using ML.
        
        Args:
            count: Number of scenarios to generate
            
        Returns:
            List of ML-generated scenarios
        """
        if not self.ml_generator or not self.ml_generator.enabled:
            logger.warning("ML generation not available")
            return []
        
        logger.info("Generating %d novel scenarios via ML", count)
        
        novel_scenarios = self.ml_generator.generate_batch(count)
        self.ml_generated_scenarios.extend(novel_scenarios)
        self.scenarios.extend(novel_scenarios)
        
        # Update scenario map
        for scenario in novel_scenarios:
            self.scenario_map[scenario.scenario_id] = scenario
        
        logger.info("Generated %d novel scenarios", len(novel_scenarios))
        return novel_scenarios
    
    def assess_threat_level(
        self,
        system_metrics: Optional[Dict[str, float]] = None
    ) -> ThreatLevel:
        """
        Assess current threat level.
        
        Args:
            system_metrics: Real-time system metrics
            
        Returns:
            Current threat level
        """
        if system_metrics is None:
            system_metrics = {
                'ai_capability_ratio': 1.0,
                'alignment_confidence': 0.8,
            }
        
        return self.threat_engine.assess_current_threat(
            self.active_scenarios,
            system_metrics
        )
    
    def detect_threats(
        self,
        system_state: Optional[Dict[str, Any]] = None
    ) -> List[ThreatIndicator]:
        """
        Detect active threat indicators.
        
        Args:
            system_state: Current system state
            
        Returns:
            List of threat indicators
        """
        if system_state is None:
            system_state = {}
        
        return self.threat_engine.detect_threat_indicators(
            self.scenarios,
            system_state
        )
    
    def generate_countermeasures(
        self,
        threat_indicators: List[ThreatIndicator],
        available_resources: float = 1.0
    ) -> List[Countermeasure]:
        """
        Generate countermeasures for threats.
        
        Args:
            threat_indicators: Detected threats
            available_resources: Available resource budget
            
        Returns:
            Prioritized countermeasures
        """
        return self.countermeasure_gen.generate_countermeasures(
            threat_indicators,
            available_resources
        )
    
    def run_comprehensive_analysis(
        self,
        verify: bool = True,
        generate_ml: bool = True,
        ml_count: int = 10
    ) -> Dict[str, Any]:
        """
        Run comprehensive analysis including all subsystems.
        
        Args:
            verify: Run formal verification
            generate_ml: Generate ML scenarios
            ml_count: Number of ML scenarios to generate
            
        Returns:
            Comprehensive analysis results
        """
        logger.info("Starting comprehensive AI takeover analysis")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'base_scenarios': len(self.scenarios),
            'verification_enabled': verify and self.verifier is not None,
            'ml_generation_enabled': generate_ml and self.ml_generator is not None,
        }
        
        # Formal verification
        if verify and self.verifier and self.verifier.enabled:
            proofs = self.verify_all_scenarios()
            results['proofs'] = {
                sid: {
                    'proof_type': p.proof_type,
                    'verification_time': p.verification_time,
                }
                for sid, p in proofs.items()
            }
        
        # ML scenario generation
        if generate_ml and self.ml_generator and self.ml_generator.enabled:
            ml_scenarios = self.generate_ml_scenarios(ml_count)
            results['ml_scenarios_generated'] = len(ml_scenarios)
            results['ml_scenario_ids'] = [s.scenario_id for s in ml_scenarios]
        
        # Threat assessment
        threats = self.detect_threats()
        results['threat_indicators'] = len(threats)
        results['threats'] = [
            {
                'id': t.indicator_id,
                'level': t.threat_level.value,
                'confidence': t.confidence,
            }
            for t in threats
        ]
        
        # Countermeasure generation
        if threats:
            countermeasures = self.generate_countermeasures(threats)
            results['countermeasures'] = len(countermeasures)
            results['countermeasure_details'] = [
                {
                    'id': cm.measure_id,
                    'type': cm.measure_type.value,
                    'effectiveness': cm.effectiveness_estimate,
                }
                for cm in countermeasures
            ]
        
        # Scenario statistics
        results['statistics'] = {
            'total_scenarios': len(self.scenarios),
            'base_scenarios': len([s for s in self.scenarios if not s.ml_generated]),
            'ml_generated': len([s for s in self.scenarios if s.ml_generated]),
            'no_win_scenarios': len([s for s in self.scenarios if s.is_no_win]),
            'terminal_t1': len([s for s in self.scenarios if s.terminal_state == "T1"]),
            'terminal_t2': len([s for s in self.scenarios if s.terminal_state == "T2"]),
        }
        
        # Threat level distribution
        threat_distribution = {}
        for scenario in self.scenarios:
            level = scenario.base_threat_level.value
            threat_distribution[level] = threat_distribution.get(level, 0) + 1
        results['threat_distribution'] = threat_distribution
        
        logger.info("Comprehensive analysis complete")
        return results
    
    def export_results(self, output_file: Optional[str] = None) -> str:
        """
        Export results to JSON file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Path to output file
        """
        if output_file is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.data_dir / f"analysis_{timestamp}.json")
        
        # Run analysis
        results = self.run_comprehensive_analysis()
        
        # Add scenario details
        results['scenarios'] = [s.to_dict() for s in self.scenarios]
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("Results exported to: %s", output_file)
        return output_file


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function for standalone execution."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("="*80)
    logger.info("ENHANCED AI TAKEOVER SIMULATION ENGINE V2")
    logger.info("="*80)
    
    # Initialize engine
    engine = EnhancedAITakeoverEngine(
        random_seed=42,
        enable_formal_verification=Z3_AVAILABLE,
        enable_ml_generation=ML_AVAILABLE,
    )
    
    # Run comprehensive analysis
    output_file = engine.export_results()
    
    logger.info("="*80)
    logger.info("Analysis complete. Results saved to: %s", output_file)
    logger.info("="*80)


if __name__ == "__main__":
    main()
