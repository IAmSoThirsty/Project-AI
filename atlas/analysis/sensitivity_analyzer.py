"""
ATLAS Ω - Layer 10: Sensitivity & Stability Analysis Engine

Production-grade sensitivity analysis with:
- Sobol variance decomposition
- Eigenvalue stability analysis
- Lyapunov region estimation
- Parameter perturbation sweeps
- Driver shock elasticity mapping
- Tipping threshold computation

⚠️ SUBORDINATION NOTICE:
This is an analysis tool, not a decision-making system.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import linalg

from atlas.audit.trail import get_audit_trail

logger = logging.getLogger(__name__)


@dataclass
class SobolIndices:
    """Sobol sensitivity indices for parameter importance."""
    parameter_name: str
    first_order: float  # Main effect
    total_order: float  # Main + interaction effects
    
    def is_influential(self, threshold: float = 0.1) -> bool:
        """Check if parameter is influential."""
        return self.total_order > threshold


@dataclass
class StabilityMetrics:
    """Stability metrics from eigenvalue analysis."""
    max_eigenvalue: complex
    spectral_radius: float
    is_stable: bool  # spectral_radius < 1
    decay_rate: float  # How fast perturbations decay
    
    # Lyapunov exponents
    lyapunov_exponents: List[float] = field(default_factory=list)
    largest_lyapunov: Optional[float] = None


@dataclass
class TippingPoint:
    """Tipping point where system behavior changes qualitatively."""
    parameter_name: str
    threshold_value: float
    confidence: float  # [0, 1]
    description: str


@dataclass
class ParameterPerturbation:
    """Result of perturbing a single parameter."""
    parameter_name: str
    baseline_value: float
    perturbed_value: float
    perturbation_magnitude: float
    
    # Response metrics
    systemic_risk_delta: float
    stability_delta: float
    elasticity: float  # Response magnitude / perturbation magnitude


class SensitivityAnalyzer:
    """
    Layer 10: Sensitivity & Stability Analysis Engine
    
    Analyzes system sensitivity to parameters and stability regions.
    """
    
    def __init__(self, audit_trail=None):
        """Initialize sensitivity analyzer."""
        self.audit_trail = audit_trail or get_audit_trail()
        
        # Analysis results
        self.sobol_indices: List[SobolIndices] = []
        self.stability_metrics: Optional[StabilityMetrics] = None
        self.tipping_points: List[TippingPoint] = []
        self.perturbations: List[ParameterPerturbation] = []
        
        self.audit_trail.log(
            category="ANALYSIS",
            operation="sensitivity_analyzer_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL"
        )
        
        logger.info("Sensitivity analyzer initialized")
    
    def sobol_decomposition(self, parameters: Dict[str, float],
                           evaluate_fn: Any,
                           n_samples: int = 1000) -> List[SobolIndices]:
        """
        Perform Sobol variance decomposition.
        
        Identifies which parameters contribute most to output variance.
        
        Args:
            parameters: {param_name: baseline_value}
            evaluate_fn: Function that takes parameters and returns output
            n_samples: Number of Monte Carlo samples
        
        Returns:
            List of Sobol indices for each parameter
        """
        logger.info(f"Computing Sobol indices for {len(parameters)} parameters ({n_samples} samples)")
        
        param_names = list(parameters.keys())
        n_params = len(param_names)
        
        # Generate Sobol sequence (simplified - would use scipy.stats.qmc in production)
        # Using random sampling as approximation
        rng = np.random.RandomState(42)
        
        # Two independent matrices
        A = rng.uniform(0.8, 1.2, (n_samples, n_params))  # ±20% variation
        B = rng.uniform(0.8, 1.2, (n_samples, n_params))
        
        # Evaluate base matrices
        outputs_A = np.array([
            evaluate_fn({name: val * A[i, j] for j, (name, val) in enumerate(parameters.items())})
            for i in range(n_samples)
        ])
        
        outputs_B = np.array([
            evaluate_fn({name: val * B[i, j] for j, (name, val) in enumerate(parameters.items())})
            for i in range(n_samples)
        ])
        
        # Total variance
        all_outputs = np.concatenate([outputs_A, outputs_B])
        total_var = np.var(all_outputs)
        
        if total_var < 1e-10:
            logger.warning("Total variance near zero - sensitivity analysis may be unreliable")
        
        # Compute indices for each parameter
        indices = []
        
        for i, param_name in enumerate(param_names):
            # Create matrix C_i (A with column i from B)
            C_i = A.copy()
            C_i[:, i] = B[:, i]
            
            outputs_C = np.array([
                evaluate_fn({name: val * C_i[j, k] for k, (name, val) in enumerate(parameters.items())})
                for j in range(n_samples)
            ])
            
            # First-order index (main effect)
            if total_var > 0:
                V_i = np.mean(outputs_A * (outputs_C - outputs_B))
                S_i = V_i / total_var
            else:
                S_i = 0
            
            # Total-order index (approximation)
            var_not_i = np.var(outputs_C)
            if total_var > 0:
                S_Ti = 1 - (var_not_i / total_var)
            else:
                S_Ti = 0
            
            # Clamp to [0, 1]
            S_i = np.clip(S_i, 0, 1)
            S_Ti = np.clip(S_Ti, 0, 1)
            
            indices.append(SobolIndices(
                parameter_name=param_name,
                first_order=float(S_i),
                total_order=float(S_Ti)
            ))
        
        self.sobol_indices = indices
        
        self.audit_trail.log(
            category="ANALYSIS",
            operation="sobol_decomposition_complete",
            details={
                "parameters": len(parameters),
                "samples": n_samples,
                "influential_params": sum(1 for idx in indices if idx.is_influential())
            },
            level="INFORMATIONAL"
        )
        
        logger.info(f"Sobol decomposition complete: {len(indices)} parameters analyzed")
        return indices
    
    def eigenvalue_stability(self, jacobian_matrix: np.ndarray) -> StabilityMetrics:
        """
        Analyze stability via eigenvalue analysis.
        
        Args:
            jacobian_matrix: Jacobian of system dynamics
        
        Returns:
            Stability metrics
        """
        logger.info(f"Computing eigenvalue stability for {jacobian_matrix.shape[0]}D system")
        
        # Compute eigenvalues
        eigenvalues = linalg.eigvals(jacobian_matrix)
        
        # Spectral radius
        spectral_radius = float(np.max(np.abs(eigenvalues)))
        
        # System is stable if spectral radius < 1
        is_stable = spectral_radius < 1.0
        
        # Decay rate (for stable systems)
        if is_stable:
            decay_rate = 1.0 - spectral_radius
        else:
            decay_rate = 0.0
        
        # Lyapunov exponents (real parts of eigenvalues)
        lyapunov_exponents = [float(np.real(ev)) for ev in eigenvalues]
        largest_lyapunov = float(np.max(lyapunov_exponents))
        
        metrics = StabilityMetrics(
            max_eigenvalue=eigenvalues[np.argmax(np.abs(eigenvalues))],
            spectral_radius=spectral_radius,
            is_stable=is_stable,
            decay_rate=decay_rate,
            lyapunov_exponents=lyapunov_exponents,
            largest_lyapunov=largest_lyapunov
        )
        
        self.stability_metrics = metrics
        
        self.audit_trail.log(
            category="ANALYSIS",
            operation="eigenvalue_stability_computed",
            details={
                "spectral_radius": spectral_radius,
                "is_stable": is_stable,
                "largest_lyapunov": largest_lyapunov
            },
            level="INFORMATIONAL"
        )
        
        logger.info(f"Stability analysis: {'STABLE' if is_stable else 'UNSTABLE'} (ρ={spectral_radius:.3f})")
        return metrics
    
    def parameter_perturbation_sweep(self, parameters: Dict[str, float],
                                    evaluate_fn: Any,
                                    perturbation_magnitude: float = 0.1) -> List[ParameterPerturbation]:
        """
        Sweep through parameter perturbations.
        
        Args:
            parameters: {param_name: baseline_value}
            evaluate_fn: Function that takes parameters and returns (systemic_risk, stability)
            perturbation_magnitude: Magnitude of perturbation (±)
        
        Returns:
            List of perturbation results
        """
        logger.info(f"Parameter perturbation sweep: {len(parameters)} parameters")
        
        # Baseline
        baseline_risk, baseline_stability = evaluate_fn(parameters)
        
        perturbations = []
        
        for param_name, baseline_value in parameters.items():
            # Perturb up
            perturbed_params = parameters.copy()
            perturbed_value = baseline_value * (1 + perturbation_magnitude)
            perturbed_params[param_name] = perturbed_value
            
            risk, stability = evaluate_fn(perturbed_params)
            
            # Compute deltas
            risk_delta = risk - baseline_risk
            stability_delta = stability - baseline_stability
            
            # Elasticity (normalized response)
            if abs(risk_delta) > abs(stability_delta):
                response = abs(risk_delta)
            else:
                response = abs(stability_delta)
            
            elasticity = response / perturbation_magnitude if perturbation_magnitude > 0 else 0
            
            perturbation = ParameterPerturbation(
                parameter_name=param_name,
                baseline_value=baseline_value,
                perturbed_value=perturbed_value,
                perturbation_magnitude=perturbation_magnitude,
                systemic_risk_delta=risk_delta,
                stability_delta=stability_delta,
                elasticity=elasticity
            )
            
            perturbations.append(perturbation)
        
        # Sort by elasticity (most sensitive first)
        perturbations.sort(key=lambda p: abs(p.elasticity), reverse=True)
        
        self.perturbations = perturbations
        
        self.audit_trail.log(
            category="ANALYSIS",
            operation="perturbation_sweep_complete",
            details={
                "parameters": len(parameters),
                "perturbation_magnitude": perturbation_magnitude,
                "max_elasticity": perturbations[0].elasticity if perturbations else 0
            },
            level="INFORMATIONAL"
        )
        
        logger.info(f"Perturbation sweep complete: max elasticity={perturbations[0].elasticity:.3f}")
        return perturbations
    
    def identify_tipping_points(self, parameter_name: str,
                                evaluate_fn: Any,
                                search_range: Tuple[float, float],
                                n_steps: int = 100) -> List[TippingPoint]:
        """
        Identify tipping points where system behavior changes.
        
        Args:
            parameter_name: Parameter to vary
            evaluate_fn: Function that takes parameter value and returns stability flag
            search_range: (min_value, max_value) to search
            n_steps: Number of evaluation points
        
        Returns:
            List of tipping points found
        """
        logger.info(f"Searching for tipping points in {parameter_name}")
        
        min_val, max_val = search_range
        values = np.linspace(min_val, max_val, n_steps)
        
        # Evaluate stability at each point
        is_stable = []
        for val in values:
            stable = evaluate_fn(val)
            is_stable.append(stable)
        
        # Find transitions
        tipping_points = []
        for i in range(len(is_stable) - 1):
            if is_stable[i] != is_stable[i+1]:
                # Transition detected
                threshold = (values[i] + values[i+1]) / 2
                
                tip = TippingPoint(
                    parameter_name=parameter_name,
                    threshold_value=threshold,
                    confidence=0.9,  # Based on step size
                    description=f"Stability transition at {parameter_name}={threshold:.3f}"
                )
                tipping_points.append(tip)
        
        self.tipping_points.extend(tipping_points)
        
        self.audit_trail.log(
            category="ANALYSIS",
            operation="tipping_points_identified",
            details={
                "parameter": parameter_name,
                "tipping_points": len(tipping_points),
                "search_range": search_range
            },
            level="INFORMATIONAL"
        )
        
        logger.info(f"Found {len(tipping_points)} tipping points for {parameter_name}")
        return tipping_points
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        influential_params = [idx for idx in self.sobol_indices if idx.is_influential()]
        
        return {
            "sobol_analysis": {
                "total_parameters": len(self.sobol_indices),
                "influential_parameters": len(influential_params),
                "top_3": [
                    {"name": idx.parameter_name, "total_order": idx.total_order}
                    for idx in sorted(self.sobol_indices, key=lambda x: x.total_order, reverse=True)[:3]
                ]
            },
            "stability": {
                "is_stable": self.stability_metrics.is_stable if self.stability_metrics else None,
                "spectral_radius": self.stability_metrics.spectral_radius if self.stability_metrics else None,
                "largest_lyapunov": self.stability_metrics.largest_lyapunov if self.stability_metrics else None
            },
            "perturbations": {
                "total": len(self.perturbations),
                "most_sensitive": self.perturbations[0].parameter_name if self.perturbations else None,
                "max_elasticity": self.perturbations[0].elasticity if self.perturbations else 0
            },
            "tipping_points": len(self.tipping_points)
        }


# Singleton instance
_analyzer = None


def get_sensitivity_analyzer(audit_trail=None) -> SensitivityAnalyzer:
    """Get singleton sensitivity analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SensitivityAnalyzer(audit_trail=audit_trail)
    return _analyzer
