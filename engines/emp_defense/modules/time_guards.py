"""
Time phase guards for EMP Defense Engine.

Enforces valid time transitions and phase boundaries.
Prevents accidental breakage of early-phase realism.
"""

from engines.emp_defense.modules.sectorized_state import SectorizedWorldState
from engines.emp_defense.modules.constants import TimeConstants


def is_early_phase(state: SectorizedWorldState) -> bool:
    """
    Check if simulation is in early critical phase (first 72 hours).
    
    Early phase requires hour-level precision and different cascade rules.
    
    Args:
        state: World state to check
        
    Returns:
        True if in first 72 hours
        
    Examples:
        >>> state = SectorizedWorldState()
        >>> state.simulation_hour = 24
        >>> is_early_phase(state)
        True
        >>> state.simulation_hour = 100
        >>> is_early_phase(state)
        False
    """
    return state.simulation_hour < TimeConstants.EARLY_PHASE_HOURS


def is_food_water_shock_phase(state: SectorizedWorldState) -> bool:
    """
    Check if simulation is in food/water shock phase (72h-336h / 3-14 days).
    
    Args:
        state: World state to check
        
    Returns:
        True if in food/water shock phase
    """
    return (TimeConstants.FOOD_SHOCK_START_HOURS <= state.simulation_hour 
            < TimeConstants.FOOD_SHOCK_END_HOURS)


def is_governance_failure_phase(state: SectorizedWorldState) -> bool:
    """
    Check if simulation is in governance failure phase (336h-2160h / 14-90 days).
    
    Args:
        state: World state to check
        
    Returns:
        True if in governance failure phase
    """
    return (TimeConstants.FOOD_SHOCK_END_HOURS <= state.simulation_hour 
            < TimeConstants.GOVERNANCE_FAILURE_END_HOURS)


def is_demographic_collapse_phase(state: SectorizedWorldState) -> bool:
    """
    Check if simulation is in demographic collapse phase (90+ days).
    
    Args:
        state: World state to check
        
    Returns:
        True if past 90 days
    """
    return state.simulation_hour >= TimeConstants.GOVERNANCE_FAILURE_END_HOURS


def get_current_phase_name(state: SectorizedWorldState) -> str:
    """
    Get human-readable name of current phase.
    
    Args:
        state: World state to check
        
    Returns:
        Phase name string
        
    Examples:
        >>> state = SectorizedWorldState()
        >>> state.simulation_hour = 50
        >>> get_current_phase_name(state)
        'early_critical'
    """
    if is_early_phase(state):
        return "early_critical"
    elif is_food_water_shock_phase(state):
        return "food_water_shock"
    elif is_governance_failure_phase(state):
        return "governance_failure"
    else:
        return "demographic_collapse"


def should_use_hourly_timestep(state: SectorizedWorldState) -> bool:
    """
    Determine if simulation should use hourly timesteps.
    
    Early phase requires hour-level precision.
    After 72 hours, can switch to daily timesteps.
    
    Args:
        state: World state to check
        
    Returns:
        True if should use hourly timesteps
    """
    return is_early_phase(state)


def validate_time_transition(
    state: SectorizedWorldState,
    hours_to_advance: int
) -> tuple[bool, str]:
    """
    Validate that a time transition is allowed.
    
    Args:
        state: Current world state
        hours_to_advance: Hours to advance
        
    Returns:
        (valid, reason) tuple
        
    Examples:
        >>> state = SectorizedWorldState()
        >>> state.simulation_hour = 24
        >>> validate_time_transition(state, 1)
        (True, 'Valid transition')
        
        >>> validate_time_transition(state, -5)
        (False, 'Cannot move backward in time')
    """
    if hours_to_advance < 0:
        return False, "Cannot move backward in time"
    
    if hours_to_advance == 0:
        return False, "Must advance time"
    
    # Early phase should use small timesteps
    if is_early_phase(state) and hours_to_advance > 24:
        return False, f"Early phase requires timesteps ≤24h, got {hours_to_advance}h"
    
    # After early phase, daily timesteps are fine
    if not is_early_phase(state) and hours_to_advance % 24 != 0:
        return False, f"Post-early phase should use daily timesteps, got {hours_to_advance}h"
    
    return True, "Valid transition"


def get_coupling_strength_modifier(state: SectorizedWorldState) -> float:
    """
    Get coupling strength modifier based on current phase.
    
    Early phase has stronger coupling as systems are still interconnected.
    Later phases have weaker coupling as systems fragment.
    
    Args:
        state: World state to check
        
    Returns:
        Coupling strength multiplier (0.0-1.0)
    """
    if is_early_phase(state):
        return 1.0  # Full strength
    elif is_food_water_shock_phase(state):
        return 0.90  # Slight weakening
    elif is_governance_failure_phase(state):
        return 0.75  # Significant weakening
    else:
        return 0.60  # Fragmented systems


def phase_allows_event(
    state: SectorizedWorldState,
    event_name: str
) -> tuple[bool, str]:
    """
    Check if current phase allows specific event execution.
    
    Some events are only available in certain phases.
    
    Args:
        state: World state to check
        event_name: Name of event to execute
        
    Returns:
        (allowed, reason) tuple
    """
    # Early phase - limited coordination
    if is_early_phase(state):
        early_allowed = [
            "emergency_broadcast",
            "declare_martial_law",
        ]
        if event_name not in early_allowed:
            return False, "Event requires >72h coordination time"
    
    # Governance failure - limited legitimacy needed
    if is_governance_failure_phase(state):
        if state.governance.legitimacy_score < 0.20:
            legitimacy_required = [
                "food_aid_distribution",
                "grid_recovery_effort",
            ]
            if event_name in legitimacy_required:
                return False, "Insufficient government legitimacy"
    
    return True, "Event allowed in current phase"
