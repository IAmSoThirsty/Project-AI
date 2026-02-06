"""
Thirsty Super Kernel - Master Integration Orchestrator

Integrates all components of the holographic defense system:
- Holographic Layer Manager
- AI Threat Detection Engine
- Deception Orchestrator
- Visualization System

This is the main entry point for the complete system.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import all core systems
from kernel.holographic import HolographicLayerManager, Command, ThreatLevel, Layer
from kernel.threat_detection import ThreatDetectionEngine, ThreatAssessment, AttackType
from kernel.deception import DeceptionOrchestrator, DeceptionStrategy
from kernel.visualize import DemoVisualizer, VisualizationMode

# New advanced components
try:
    from kernel.learning_engine import DefenseEvolutionEngine
    from kernel.advanced_visualizations import (
        SplitScreenVisualizer,
        AnimatedAttackFlow,
        AttackFlowStep,
    )

    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    logger = logging.getLogger(__name__)
    logger.warning("Advanced features not available")

# Project-AI Integration
try:
    from kernel.project_ai_bridge import get_project_ai_integration

    PROJECT_AI_AVAILABLE = True
except ImportError:
    PROJECT_AI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Project-AI integration not available - running in standalone mode")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """Configuration for the integrated system"""

    enable_ai_detection: bool = True
    enable_deception: bool = True
    enable_visualization: bool = True
    observation_window: int = 2
    threat_threshold: float = 0.6
    bubblegum_confidence: float = 0.9
    max_deception_layers: int = 10


class ThirstySuperKernel:
    """
    Thirsty Super Kernel - Complete Integrated System

    Thirst of Gods Level Architecture:
    - Holographic multi-layer defense
    - AI-powered threat detection
    - Dynamic deception environments
    - Real-time visualization
    - Bubblegum protocol

    For Google Engineers Presentation (Feb 12, 2026)
    and DARPA Classified Briefing
    """

    VERSION = "0.1.0-thirst-of-gods"

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()

        logger.info("=" * 70)
        logger.info("THIRSTY SUPER KERNEL - INITIALIZING")
        logger.info(f"Version: {self.VERSION}")
        logger.info("Thirst of Gods Level Architecture")
        logger.info("=" * 70)

        # Component initialization
        self.layer_manager = HolographicLayerManager()
        logger.info("✅ Holographic Layer Manager initialized")

        if self.config.enable_ai_detection:
            self.threat_detector = ThreatDetectionEngine(use_ml=True)
            logger.info("✅ AI Threat Detection Engine initialized")

        if self.config.enable_deception:
            self.deception_orchestrator = DeceptionOrchestrator()
            logger.info("✅ Deception Orchestrator initialized")

        if self.config.enable_visualization:
            self.visualizer = DemoVisualizer()
            logger.info("✅ Visualization System initialized")

        # Advanced Features
        self.learning_engine = None
        self.split_screen = None
        self.attack_flow = None

        if ADVANCED_FEATURES:
            try:
                self.learning_engine = DefenseEvolutionEngine()
                self.split_screen = SplitScreenVisualizer()
                self.attack_flow = AnimatedAttackFlow()
                logger.info("✅ Advanced Features initialized")
                logger.info("   - Learning Engine: ACTIVE")
                logger.info("   - Split-Screen Viz: ACTIVE")
                logger.info("   - Attack Flow Animation: ACTIVE")
            except Exception as e:
                logger.warning(f"Advanced features initialization failed: {e}")

        # Project-AI Integration
        self.project_ai = None
        if PROJECT_AI_AVAILABLE:
            try:
                self.project_ai = get_project_ai_integration()
                logger.info("✅ Project-AI Integration initialized")

                # Show integration status
                status = self.project_ai.get_integration_status()
                logger.info(
                    f"   - Cerberus: {'ACTIVE' if status['cerberus']['available'] else 'UNAVAILABLE'}"
                )
                logger.info(
                    f"   - CodexDeus: {'ACTIVE' if status['codex_deus']['available'] else 'FALLBACK'}"
                )
                logger.info(
                    f"   - Triumvirate: {'ACTIVE' if status['triumvirate']['available'] else 'UNAVAILABLE'}"
                )
            except Exception as e:
                logger.warning(f"Project-AI integration failed: {e}")

        # System state
        self.start_time = time.time()
        self.total_commands = 0
        self.threats_detected = 0
        self.deceptions_active = 0

        logger.info("")
        logger.info("🔥 THIRSTY SUPER KERNEL READY")
        logger.info("   All systems operational")
        logger.info("")

    def execute_command(self, user_id: int, command_str: str) -> Dict[str, Any]:
        """
        Main command execution entry point

        Full system flow:
        1. Parse command
        2. Execute in observation mode (holographic layer)
        3. AI threat analysis
        4. Decision: allow, monitor, or deception
        5. For deception: transition to honeypot
        6. Monitor for Bubblegum trigger
        7. Update visualizations

        Args:
            user_id: User identifier
            command_str: Command string

        Returns:
            Execution result with status and metadata
        """
        self.total_commands += 1
        start_time = time.time()

        # Parse command
        parts = command_str.split()
        cmd = Command(
            cmdtype=parts[0] if parts else "", args=parts[1:] if len(parts) > 1 else []
        )

        logger.info(f"[User {user_id}] Executing: {command_str}")

        # Get user's current layer
        layer_id = self.layer_manager.get_user_layer(user_id)
        layer = self.layer_manager.layers[layer_id]

        # STEP 1: Execute in observation mode
        observed = layer.execute_observed(cmd, user_id)

        # STEP 2: AI Threat Analysis (if enabled)
        if self.config.enable_ai_detection:
            threat = self.threat_detector.analyze_threat(
                user_id=user_id,
                command=command_str,
                observed_behavior={
                    "syscalls": observed.system_calls,
                    "file_accesses": observed.file_accesses,
                    "network_activity": observed.network_activity,
                },
            )
        else:
            # Fallback to basic analysis
            threat = self.layer_manager.analyze_threat(observed, user_id, layer)

        # STEP 3: Decision and action
        if threat.level == ThreatLevel.SAFE:
            result = self._handle_safe_command(user_id, cmd, observed, layer)

        elif threat.level == ThreatLevel.SUSPICIOUS:
            result = self._handle_suspicious_command(user_id, cmd, observed, threat)

        elif threat.level in (ThreatLevel.MALICIOUS, ThreatLevel.CRITICAL):
            result = self._handle_malicious_command(user_id, cmd, observed, threat)

        else:
            result = {"status": "ERROR", "message": "Unknown threat level"}

        # STEP 4: Update metrics
        execution_time = (time.time() - start_time) * 1000
        result["execution_time_ms"] = execution_time

        # Add threat metadata to result
        result["threat_level"] = threat.level.name
        result["threat_confidence"] = getattr(threat, "confidence", 0.0)
        if "layer" not in result:
            result["layer"] = layer.id

        if self.config.enable_visualization:
            self.visualizer.metrics.update("total_commands", self.total_commands)
            if threat.level != ThreatLevel.SAFE:
                self.visualizer.metrics.increment("threats_detected")

        logger.info(
            f"[User {user_id}] Result: {result['status']} (threat: {threat.level.name})"
        )

        return result

    def _handle_safe_command(
        self, user_id: int, cmd: Command, observed: Any, layer: Layer
    ) -> Dict[str, Any]:
        """Handle safe command execution"""
        # If in mirror layer, apply to real system
        if layer.is_mirror():
            self.layer_manager._apply_to_real_layer(cmd)

        return {
            "status": "SUCCESS",
            "result": observed.result,
            "layer": layer.id,
            "threat_level": "SAFE",
        }

    def _handle_suspicious_command(
        self, user_id: int, cmd: Command, observed: Any, threat: ThreatAssessment
    ) -> Dict[str, Any]:
        """Handle suspicious command - allow but monitor closely"""
        logger.warning(f"⚠️  Suspicious activity from user {user_id}")
        logger.warning(f"   Type: {threat.threat_type}")
        logger.warning(f"   Indicators: {', '.join(threat.indicators)}")

        if self.config.enable_visualization:
            self.visualizer.show_threat_detected(
                {
                    "type": threat.threat_type,
                    "level": "SUSPICIOUS",
                    "confidence": threat.confidence,
                }
            )

        return {
            "status": "SUCCESS",
            "result": observed.result,
            "layer": self.layer_manager.get_user_layer(user_id),
            "threat_level": "SUSPICIOUS",
            "monitored": True,
            "threat_info": {
                "type": threat.threat_type,
                "confidence": threat.confidence,
                "indicators": threat.indicators,
            },
        }

    def _handle_malicious_command(
        self, user_id: int, cmd: Command, observed: Any, threat: ThreatAssessment
    ) -> Dict[str, Any]:
        """Handle malicious command - transition to deception"""
        self.threats_detected += 1

        logger.error(f"🚨 MALICIOUS ACTIVITY DETECTED from user {user_id}")
        logger.error(f"   Type: {threat.threat_type}")
        logger.error(f"   Confidence: {threat.confidence:.2f}")
        logger.error(f"   Indicators: {', '.join(threat.indicators)}")

        # Get current layer
        current_layer = self.layer_manager.get_user_layer(user_id)

        # Check if already in deception
        if current_layer >= 2:
            # Already in deception - record action and check for Bubblegum
            if self.config.enable_deception:
                action_result = self.deception_orchestrator.record_action(
                    user_id, str(cmd)
                )

                # Check if Bubblegum triggered
                if action_result.get("protocol") == "BUBBLEGUM":
                    self._execute_bubblegum_transition(user_id, action_result)

                    return {
                        "status": "BUBBLEGUM_EXECUTED",
                        "result": "System reset",
                        "layer": 1,  # Reset to mirror
                        "threat_level": "CRITICAL",
                        "bubblegum_result": action_result,
                    }

                # Return fake success
                fake_response = self.deception_orchestrator.get_fake_response(
                    user_id, str(cmd)
                )

                return {
                    "status": "SUCCESS",  # Fake!
                    "result": fake_response,
                    "layer": current_layer,
                    "threat_level": threat.level.name,
                    "DECEPTION_ACTIVE": True,
                }

        # Not in deception yet - create deception environment
        if self.config.enable_deception:
            deception_env = self.deception_orchestrator.create_environment(
                user_id=user_id,
                threat_type=threat.threat_type,
                strategy=DeceptionStrategy.ADAPTIVE,
            )
            self.deceptions_active += 1

        # Transition to deception layer
        deception_layer = self.layer_manager.transition_to_deception(user_id, threat)

        if self.config.enable_visualization:
            self.visualizer.show_layer_transition(
                from_layer=current_layer,
                to_layer=deception_layer.id,
                reason=f"Malicious activity: {threat.threat_type}",
            )
            self.visualizer.show_threat_detected(
                {
                    "type": threat.threat_type,
                    "level": threat.level.name,
                    "confidence": threat.confidence,
                }
            )

        # Return fake success so attacker doesn't know
        return {
            "status": "SUCCESS",  # Fake!
            "result": f"Command executed successfully",  # Lie!
            "layer": deception_layer.id,
            "threat_level": threat.level.name,
            "DECEPTION_ACTIVE": True,
            "deception_env_id": deception_env.env_id
            if self.config.enable_deception
            else None,
        }

    def _execute_bubblegum_transition(
        self, user_id: int, bubblegum_result: Dict[str, Any]
    ):
        """Execute the Bubblegum protocol transition"""
        logger.critical("")
        logger.critical("=" * 70)
        logger.critical("💥 BUBBLEGUM PROTOCOL EXECUTED")
        logger.critical("=" * 70)

        if self.config.enable_visualization:
            self.visualizer.show_bubblegum()

        # Reset user to mirror layer
        self.layer_manager.user_layer_map[user_id] = 1

        # Cleanup deception environment
        if self.config.enable_deception:
            self.deception_orchestrator.cleanup_environment(user_id)
            self.deceptions_active = max(0, self.deceptions_active - 1)

        logger.critical(f"User {user_id} returned to mirror layer")
        logger.critical(f"Actions logged: {bubblegum_result.get('actions_logged', 0)}")
        logger.critical("=" * 70)
        logger.critical("")

    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        uptime = time.time() - self.start_time

        status = {
            "version": self.VERSION,
            "uptime_seconds": uptime,
            "total_commands": self.total_commands,
            "threats_detected": self.threats_detected,
            "deceptions_active": self.deceptions_active,
            "layers": self.layer_manager.get_layer_status(),
        }

        if self.config.enable_ai_detection:
            status["threat_detection"] = self.threat_detector.get_stats()

        if self.config.enable_deception:
            status["deception"] = self.deception_orchestrator.get_stats()

        return status

    def show_intro(self):
        """Display system introduction (for demos)"""
        if self.config.enable_visualization:
            self.visualizer.show_intro()

    def show_metrics(self, mode: VisualizationMode = VisualizationMode.DETAILED):
        """Display performance metrics"""
        if self.config.enable_visualization:
            # Update metrics first
            status = self.get_system_status()
            self.visualizer.metrics.update("total_commands", status["total_commands"])
            self.visualizer.metrics.update(
                "threats_detected", status["threats_detected"]
            )
            self.visualizer.metrics.update(
                "deceptions_active", status["deceptions_active"]
            )

            if "deception" in status:
                self.visualizer.metrics.update(
                    "bubblegum_triggers",
                    status["deception"].get("total_bubblegum_triggers", 0),
                )

            self.visualizer.show_metrics(mode)


# Quick test function
def quick_test():
    """Quick system test"""
    print("\nThirsty Super Kernel - Quick Test\n")

    kernel = ThirstySuperKernel()

    # Test commands
    test_user = 1001
    commands = [
        "ls -la",
        "whoami",
        "sudo -l",
        "cat /etc/shadow",
        "tar czf /tmp/exfil.tar.gz /etc/shadow",
    ]

    for cmd in commands:
        print(f"\n[TEST] Executing: {cmd}")
        result = kernel.execute_command(test_user, cmd)
        print(f"[TEST] Result: {result['status']} (Layer: {result.get('layer', '?')})")

    print("\n" + "=" * 70)
    print("FINAL SYSTEM STATUS")
    print("=" * 70)
    kernel.show_metrics(VisualizationMode.DETAILED)


# Public API
__all__ = [
    "ThirstySuperKernel",
    "SystemConfig",
]


if __name__ == "__main__":
    quick_test()
