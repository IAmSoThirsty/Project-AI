"""Django State Engine - Main Engine.

Human Misunderstanding Extinction Engine with complete irreversibility laws,
event sourcing, and monolithic integration.
"""

import logging
from typing import Dict, Any, Optional
from .schemas import StateVector, Event, EngineConfig
from .kernel import RealityClock, IrreversibilityLaws, CollapseScheduler
from .modules import (
    HumanForcesModule,
    InstitutionalPressureModule,
    PerceptionWarfareModule,
    RedTeamModule,
    MetricsModule,
    TimelineModule,
    OutcomesModule,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DjangoStateEngine:
    """Main Django State Engine.
    
    Production-grade simulation engine for modeling human misunderstanding
    and system extinction through irreversible state evolution.
    
    Mandatory interface:
    - init() -> bool: Initialize simulation
    - tick() -> dict: Advance by one time step
    - inject_event(event) -> bool: Inject external event
    - observe(query) -> dict: Query current state
    - export_artifacts() -> dict: Generate reports and exports
    """
    
    def __init__(self, config: Optional[EngineConfig] = None):
        """Initialize Django State Engine.
        
        Args:
            config: Engine configuration (uses defaults if None)
        """
        self.config = config or EngineConfig()
        
        # Configure logging level
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)
        
        # State
        self.state: Optional[StateVector] = None
        self.initialized = False
        self.running = False
        
        # Kernel components
        self.clock: Optional[RealityClock] = None
        self.laws: Optional[IrreversibilityLaws] = None
        self.collapse_scheduler: Optional[CollapseScheduler] = None
        
        # Modules
        self.human_forces: Optional[HumanForcesModule] = None
        self.institutional_pressure: Optional[InstitutionalPressureModule] = None
        self.perception_warfare: Optional[PerceptionWarfareModule] = None
        self.red_team: Optional[RedTeamModule] = None
        self.metrics: Optional[MetricsModule] = None
        self.timeline: Optional[TimelineModule] = None
        self.outcomes: Optional[OutcomesModule] = None
        
        logger.info(f"Django State Engine created: {self.config.simulation_name}")
    
    def init(self) -> bool:
        """Initialize simulation with starting conditions.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing Django State Engine...")
            
            # Initialize kernel components
            self.clock = RealityClock(
                start_time=0.0,
                time_step=self.config.time_step,
            )
            
            self.laws = IrreversibilityLaws(
                config=self.config.irreversibility,
            )
            
            self.collapse_scheduler = CollapseScheduler()
            
            # Initialize state
            self.state = StateVector.create_initial_state(timestamp=0.0)
            
            # Initialize modules
            self.human_forces = HumanForcesModule(laws=self.laws)
            self.institutional_pressure = InstitutionalPressureModule(laws=self.laws)
            self.perception_warfare = PerceptionWarfareModule(laws=self.laws)
            self.red_team = RedTeamModule(
                laws=self.laws,
                black_vault_enabled=self.config.black_vault_enabled,
            )
            self.metrics = MetricsModule()
            self.timeline = TimelineModule()
            self.outcomes = OutcomesModule(thresholds=self.config.thresholds)
            
            # Record initial state
            self.timeline.create_snapshot(0, self.state)
            self.metrics.calculate_current_metrics(self.state)
            
            # Mark as initialized
            self.initialized = True
            self.running = True
            
            logger.info("Django State Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def tick(self) -> Dict[str, Any]:
        """Advance simulation by one time step.
        
        Applies all irreversibility laws and module dynamics.
        
        Returns:
            Dictionary with tick results
        """
        if not self.initialized:
            raise RuntimeError("Engine not initialized - call init() first")
        
        if not self.running:
            raise RuntimeError("Engine not running")
        
        # Save state before tick
        state_before = self.state.copy()
        
        # Advance clock
        new_time = self.clock.tick()
        self.state.timestamp = new_time
        self.state.tick_count += 1
        
        logger.debug(f"=== TICK {self.state.tick_count} (t={new_time}) ===")
        
        # Apply irreversibility laws (natural decay)
        law_changes = self.laws.tick_all_laws(self.state)
        
        # Update derived state
        self.state.update_derived_state()
        
        # Apply module dynamics
        human_results = self.human_forces.apply_cooperation_dynamics(self.state)
        institutional_results = self.institutional_pressure.apply_institutional_dynamics(self.state)
        perception_results = self.perception_warfare.apply_perception_warfare_dynamics(self.state)
        
        # Check collapse conditions
        collapsed, collapse_reason = self.state.check_collapse_conditions(
            self.config.thresholds.to_dict()["collapse"]
        )
        
        if collapsed and not self.state.in_collapse:
            self.state.in_collapse = True
            self.state.collapse_triggered_at = self.state.timestamp
            logger.critical(f"COLLAPSE TRIGGERED: {collapse_reason}")
        
        # Process collapse scheduler
        triggered_collapses = self.collapse_scheduler.process_tick(self.state)
        
        # Apply collapse acceleration if enabled
        if self.state.in_collapse and self.config.enable_collapse_acceleration:
            self.laws.apply_collapse_acceleration(
                self.state,
                self.config.collapse_acceleration_factor,
            )
        
        # Record in timeline
        all_changes = {
            "laws": law_changes,
            "human_forces": human_results,
            "institutional_pressure": institutional_results,
            "perception_warfare": perception_results,
            "collapses_triggered": len(triggered_collapses),
        }
        
        self.timeline.record_tick(
            self.state.tick_count,
            self.state.timestamp,
            state_before,
            self.state,
            all_changes,
        )
        
        # Calculate metrics
        current_metrics = self.metrics.calculate_current_metrics(self.state)
        
        # Create snapshot periodically
        if self.state.tick_count % self.config.snapshot_interval == 0:
            self.timeline.create_snapshot(self.state.tick_count, self.state)
        
        # Check if simulation should end
        terminal = self._check_terminal_conditions()
        
        # Build tick results
        results = {
            "tick": self.state.tick_count,
            "timestamp": self.state.timestamp,
            "state": self.state.to_dict(),
            "changes": all_changes,
            "metrics": current_metrics,
            "in_collapse": self.state.in_collapse,
            "collapse_reason": collapse_reason if collapsed else None,
            "terminal": terminal,
        }
        
        if terminal:
            self.running = False
            outcome = self.outcomes.determine_final_outcome(self.state)
            results["final_outcome"] = outcome
            logger.critical(f"SIMULATION TERMINATED: {outcome}")
        
        return results
    
    def inject_event(self, event: Event) -> bool:
        """Inject external event into simulation.
        
        Args:
            event: Event to inject
            
        Returns:
            True if event accepted and applied
        """
        if not self.initialized or not self.running:
            logger.warning("Cannot inject event - engine not running")
            return False
        
        try:
            logger.info(f"Injecting event: {event.event_type.value}")
            
            # Save state before event
            state_before = self.state.copy()
            
            # Set event timestamp to current time
            event.timestamp = self.state.timestamp
            
            # Apply event based on type
            changes = self._apply_event(event)
            
            # Update derived state
            self.state.update_derived_state()
            
            # Record in timeline
            self.timeline.record_event(event, state_before, self.state, changes)
            
            # Record causal event
            self.clock.record_event(
                event_id=event.event_id,
                state_hash=self.timeline._hash_state(self.state),
                irreversible=True,
            )
            
            logger.info(f"Event applied: {event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject event: {e}", exc_info=True)
            return False
    
    def _apply_event(self, event: Event) -> Dict[str, Any]:
        """Apply event to state.
        
        Args:
            event: Event to apply
            
        Returns:
            Dictionary of changes applied
        """
        from .schemas.event_schema import (
            EventType,
            BetrayalEvent,
            CooperationEvent,
            InstitutionalFailureEvent,
            ManipulationEvent,
            RedTeamEvent,
        )
        
        changes = {}
        
        if event.event_type == EventType.BETRAYAL:
            betrayal_event = BetrayalEvent(**event.__dict__)
            changes = self.laws.apply_betrayal_impact(self.state, betrayal_event.severity)
        
        elif event.event_type == EventType.COOPERATION:
            cooperation_event = CooperationEvent(**event.__dict__)
            change = self.laws.apply_cooperation_boost(self.state, cooperation_event.magnitude)
            changes = {"kindness_boost": change}
        
        elif event.event_type == EventType.INSTITUTIONAL_FAILURE:
            failure_event = InstitutionalFailureEvent(**event.__dict__)
            changes = self.laws.apply_legitimacy_erosion(
                self.state,
                broken_promises=0,
                failures=1,
                visibility=0.7,
            )
        
        elif event.event_type == EventType.BROKEN_PROMISE:
            changes = self.laws.apply_legitimacy_erosion(
                self.state,
                broken_promises=1,
                failures=0,
                visibility=0.5,
            )
        
        elif event.event_type == EventType.MANIPULATION:
            manipulation_event = ManipulationEvent(**event.__dict__)
            changes = self.laws.apply_manipulation_impact(
                self.state,
                reach=manipulation_event.reach,
                sophistication=manipulation_event.sophistication,
            )
        
        elif event.event_type == EventType.RED_TEAM_ATTACK:
            red_team_event = RedTeamEvent(**event.__dict__)
            impacts = red_team_event.calculate_multi_dimensional_impact()
            for dimension, impact in impacts.items():
                if dimension == "trust":
                    self.state.trust.update(impact, self.state.timestamp)
                elif dimension == "legitimacy":
                    self.state.legitimacy.update(impact, self.state.timestamp)
                elif dimension == "kindness":
                    self.state.kindness.update(impact, self.state.timestamp)
                elif dimension == "epistemic_confidence":
                    self.state.epistemic_confidence.update(impact, self.state.timestamp)
            changes = {"impacts": impacts}
        
        elif event.event_type == EventType.MORAL_VIOLATION:
            severity = event.metadata.get("severity", 0.5)
            changes = self.laws.accumulate_moral_injury(self.state, severity)
        
        return changes
    
    def observe(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query current simulation state.
        
        Args:
            query: Query parameters
                - "type": What to observe (state, metrics, timeline, etc.)
                - Additional type-specific parameters
        
        Returns:
            Query results
        """
        if not self.initialized:
            return {"error": "Engine not initialized"}
        
        query_type = query.get("type", "state")
        
        if query_type == "state":
            return self.state.to_dict()
        
        elif query_type == "metrics":
            return self.metrics.get_summary()
        
        elif query_type == "timeline":
            return self.timeline.get_summary()
        
        elif query_type == "collapse":
            return self.collapse_scheduler.get_summary()
        
        elif query_type == "human_forces":
            return self.human_forces.get_summary()
        
        elif query_type == "institutional_pressure":
            return self.institutional_pressure.get_summary()
        
        elif query_type == "perception_warfare":
            return self.perception_warfare.get_summary()
        
        elif query_type == "red_team":
            return self.red_team.get_summary()
        
        elif query_type == "outcomes":
            return self.outcomes.get_summary()
        
        elif query_type == "all":
            return {
                "state": self.state.to_dict(),
                "metrics": self.metrics.get_summary(),
                "timeline": self.timeline.get_summary(),
                "collapse": self.collapse_scheduler.get_summary(),
                "modules": {
                    "human_forces": self.human_forces.get_summary(),
                    "institutional_pressure": self.institutional_pressure.get_summary(),
                    "perception_warfare": self.perception_warfare.get_summary(),
                    "red_team": self.red_team.get_summary(),
                },
                "outcomes": self.outcomes.get_summary(),
            }
        
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    def export_artifacts(self) -> Dict[str, Any]:
        """Generate reports, metrics, state history.
        
        Returns:
            Dictionary with all exportable artifacts
        """
        if not self.initialized:
            return {"error": "Engine not initialized"}
        
        logger.info("Generating export artifacts...")
        
        artifacts = {
            "config": self.config.to_dict(),
            "final_state": self.state.to_dict() if self.state else None,
            "timeline": self.timeline.export_timeline(include_states=False),
            "metrics_history": self.metrics.export_metrics(),
            "collapse_events": self.collapse_scheduler.export_collapses(),
            "causal_chain": self.clock.export_causal_chain(),
            "outcome_report": self.outcomes.generate_outcome_report(self.state) if self.state else None,
            "module_summaries": {
                "human_forces": self.human_forces.get_summary(),
                "institutional_pressure": self.institutional_pressure.get_summary(),
                "perception_warfare": self.perception_warfare.get_summary(),
                "red_team": self.red_team.get_summary(),
                "metrics": self.metrics.get_summary(),
                "timeline": self.timeline.get_summary(),
                "outcomes": self.outcomes.get_summary(),
            },
        }
        
        logger.info("Export artifacts generated")
        return artifacts
    
    def _check_terminal_conditions(self) -> bool:
        """Check if simulation has reached terminal state.
        
        Returns:
            True if terminal
        """
        # Max ticks reached
        if self.state.tick_count >= self.config.max_ticks:
            logger.info(f"Max ticks reached: {self.config.max_ticks}")
            return True
        
        # Collapse conditions
        if self.state.in_collapse:
            # Give some time in collapse state before terminating
            ticks_in_collapse = self.state.tick_count - (self.state.collapse_triggered_at / self.config.time_step)
            if ticks_in_collapse > 50:  # Allow 50 ticks of collapse observation
                logger.info("Extended collapse state - terminating")
                return True
        
        # Extreme states (all critical thresholds crossed)
        thresholds_dict = self.config.thresholds.to_dict()["collapse"]
        crossed_count = 0
        
        if self.state.kindness.value < thresholds_dict["kindness_singularity"]:
            crossed_count += 1
        if self.state.trust.value < thresholds_dict["trust_collapse"]:
            crossed_count += 1
        if self.state.moral_injury.value > thresholds_dict["moral_injury_critical"]:
            crossed_count += 1
        if self.state.legitimacy.value < thresholds_dict["legitimacy_failure"]:
            crossed_count += 1
        if self.state.epistemic_confidence.value < thresholds_dict["epistemic_collapse"]:
            crossed_count += 1
        
        if crossed_count >= 4:  # 4 out of 5 critical thresholds
            logger.critical("Multiple critical thresholds crossed - terminal state")
            return True
        
        return False
    
    def reset(self) -> bool:
        """Reset engine to initial state.
        
        Returns:
            True if reset successful
        """
        logger.info("Resetting Django State Engine...")
        
        try:
            self.state = None
            self.initialized = False
            self.running = False
            
            if self.clock:
                self.clock.reset()
            if self.collapse_scheduler:
                self.collapse_scheduler.reset()
            if self.human_forces:
                self.human_forces.reset()
            if self.institutional_pressure:
                self.institutional_pressure.reset()
            if self.perception_warfare:
                self.perception_warfare.reset()
            if self.red_team:
                self.red_team.reset()
            if self.metrics:
                self.metrics.reset()
            if self.timeline:
                self.timeline.reset()
            if self.outcomes:
                self.outcomes.reset()
            
            logger.info("Engine reset successful")
            return True
            
        except Exception as e:
            logger.error(f"Reset failed: {e}", exc_info=True)
            return False
