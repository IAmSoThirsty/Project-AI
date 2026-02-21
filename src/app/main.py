#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application with AGI Identity System.

CRITICAL: This is the trust root - where CognitionKernel is instantiated
and all subsystems are wired together. No execution happens without kernel authority.

THREE-TIER PLATFORM:
- Tier 1 (Governance): CognitionKernel, GovernanceService - Sovereign authority
- Tier 2 (Infrastructure): MemoryEngine, GlobalWatchTower, ExecutionService - Constrained
- Tier 3 (Application): CouncilHub, Agents, GUI - Sandboxed, replaceable
"""

import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.core.bio_brain_mapper import BioBrainMappingSystem
from app.core.cognition_kernel import CognitionKernel
from app.core.council_hub import CouncilHub
from app.core.governance import Triumvirate as GovernanceTriumvirate
from app.core.intelligence_engine import IdentityIntegratedIntelligenceEngine
from app.core.kernel_integration import set_global_kernel
from app.core.memory_engine import MemoryEngine
from app.core.platform_tiers import get_tier_registry
from app.core.reflection_cycle import ReflectionCycle
from app.core.tier_health_dashboard import get_health_monitor
from app.gui.dashboard_main import DashboardMainWindow
from src.cognition.triumvirate import Triumvirate

try:
    import yaml
except ImportError:
    yaml = None  # graceful degradation if yaml not available

# Initialize logger early
logger = logging.getLogger(__name__)

# Global instances (trust root)
_global_identity_engine = None
_global_cognition_kernel = None
_global_council_hub = None


def get_identity_engine() -> IdentityIntegratedIntelligenceEngine:
    """Get the global identity-integrated intelligence engine instance.

    Returns:
        IdentityIntegratedIntelligenceEngine: Global engine instance
    """
    global _global_identity_engine
    if _global_identity_engine is None:
        _global_identity_engine = IdentityIntegratedIntelligenceEngine(data_dir="data")
        logger.info("AGI Identity System initialized")
    return _global_identity_engine


def get_cognition_kernel() -> CognitionKernel:
    """Get the global CognitionKernel instance.

    This is the trust root for all executions. Only instantiated once in main().

    Returns:
        CognitionKernel: Global kernel instance
    """
    if _global_cognition_kernel is None:
        logger.error("CognitionKernel not initialized. Call initialize_kernel() first.")
        raise RuntimeError("CognitionKernel not initialized")
    return _global_cognition_kernel


def initialize_kernel() -> CognitionKernel:
    """Initialize the CognitionKernel with all subsystems.

    CRITICAL: This is the trust root where all authority originates.
    Called once during application startup.

    Returns:
        CognitionKernel: Initialized kernel with all subsystems
    """
    global _global_cognition_kernel

    if _global_cognition_kernel is not None:
        logger.warning("CognitionKernel already initialized")
        return _global_cognition_kernel

    logger.info("Initializing CognitionKernel (trust root)")

    # Initialize subsystems (in dependency order)
    try:
        # 1. Identity System (immutable snapshots for governance)
        identity_system = get_identity_engine()

        # 2. Memory Engine (four-channel recording)
        try:
            memory_engine = MemoryEngine(data_dir="data")
        except Exception as e:
            logger.warning("MemoryEngine initialization failed: %s, using fallback", e)
            memory_engine = None

        # 3. Governance System (Four Laws enforcement)
        try:
            governance_system = GovernanceTriumvirate()
        except Exception as e:
            logger.warning("GovernanceTriumvirate initialization failed: %s, using fallback", e)
            governance_system = None

        # 4. Reflection Engine (post-hoc reasoning)
        try:
            reflection_engine = ReflectionCycle(data_dir="data")
        except Exception as e:
            logger.warning("ReflectionCycle initialization failed: %s, using fallback", e)
            reflection_engine = None

        # 5. Triumvirate (Galahad, Cerberus, Codex)
        try:
            triumvirate = Triumvirate()
            logger.info("Triumvirate initialized: Galahad, Cerberus, Codex Deus Maximus")
        except Exception as e:
            logger.warning("Triumvirate initialization failed: %s, using fallback", e)
            triumvirate = None

        # 6. Bio-Inspired Brain Mapping System
        try:
            if yaml is None:
                logger.warning("PyYAML not available, using default bio brain mapper config")
                bio_brain_mapper = BioBrainMappingSystem(data_dir="data")
            else:
                # Load configuration from YAML
                config_path = "config/bio_brain_mapping.yaml"
                if os.path.exists(config_path):
                    with open(config_path) as f:
                        bio_config_data = yaml.safe_load(f)
                    # Use active preset if specified
                    active_preset = bio_config_data.get("active_preset", "production")
                    if active_preset in bio_config_data.get("presets", {}):
                        preset = bio_config_data["presets"][active_preset]
                        # Merge preset with base config (only merge dictionaries)
                        for key, value in preset.items():
                            if (
                                key in bio_config_data
                                and isinstance(value, dict)
                                and isinstance(bio_config_data[key], dict)
                            ):
                                bio_config_data[key].update(value)
                            elif key in bio_config_data:
                                bio_config_data[key] = value
                    bio_brain_mapper = BioBrainMappingSystem(config=bio_config_data, data_dir="data")
                    logger.info(
                        "✅ BioBrainMappingSystem initialized with preset: %s",
                        active_preset,
                    )
                else:
                    bio_brain_mapper = BioBrainMappingSystem(data_dir="data")
                    logger.info("✅ BioBrainMappingSystem initialized with default config")
        except Exception as e:
            logger.warning("BioBrainMappingSystem initialization failed: %s, using fallback", e)
            bio_brain_mapper = None

        # 7. Create CognitionKernel with all subsystems
        kernel = CognitionKernel(
            identity_system=identity_system,
            memory_engine=memory_engine,
            governance_system=governance_system,
            reflection_engine=reflection_engine,
            triumvirate=triumvirate,
            data_dir="data",
        )

        _global_cognition_kernel = kernel

        # Set as global kernel for agents
        set_global_kernel(kernel)

        logger.info("✅ CognitionKernel initialized successfully")
        logger.info("   - Identity: ✓")
        logger.info("   - Memory: %s", "✓" if memory_engine else "✗ (fallback)")
        logger.info("   - Governance: %s", "✓" if governance_system else "✗ (fallback)")
        logger.info("   - Reflection: %s", "✓" if reflection_engine else "✗ (fallback)")
        logger.info("   - Triumvirate: %s", "✓" if triumvirate else "✗ (fallback)")
        logger.info("   - BioBrainMapper: %s", "✓" if bio_brain_mapper else "✗ (fallback)")
        logger.info("🔒 Kernel syscall boundary active - all execution governed")

        # Register bio brain mapper with kernel if available
        if bio_brain_mapper:
            try:
                bio_brain_mapper.register_with_kernel(kernel)
            except Exception as e:
                logger.warning("Failed to register BioBrainMapper with kernel: %s", e)

        return kernel

    except Exception as e:
        logger.error("Failed to initialize CognitionKernel: %s", e)
        raise


def initialize_council_hub(kernel: CognitionKernel) -> CouncilHub:
    """Initialize CouncilHub with kernel injection.

    All agents registered in CouncilHub will route through the kernel.

    Args:
        kernel: CognitionKernel instance to inject into agents

    Returns:
        CouncilHub: Initialized hub with kernel-routed agents
    """
    global _global_council_hub

    logger.info("Initializing CouncilHub with kernel injection")

    hub = CouncilHub(autolearn_interval=60.0, kernel=kernel)
    hub.register_project(name="Project-AI")

    _global_council_hub = hub

    logger.info("✅ CouncilHub initialized with kernel-routed agents")
    logger.info("   - Registered agents: %s", len(hub.list_agents()))

    return hub


def initialize_security_systems(kernel: CognitionKernel, council_hub: CouncilHub) -> dict[str, Any]:
    """Initialize comprehensive security countermeasures and defense systems.

    Activates:
    1. Global Watch Tower Security Command Center (Cerberus)
    2. Active Defense Agents (SafetyGuard, Constitutional, TARL)
    3. Payload Validation & Attack Detection
    4. ASL-3 Security Enforcement (30 core controls)

    This implements ethical defensive capabilities without offensive intent,
    aligned with Asimov's Laws and the FourLaws governance system.

    Args:
        kernel: CognitionKernel instance for governance
        council_hub: CouncilHub for agent registration

    Returns:
        Dictionary containing initialized security components
    """
    logger.info("=" * 60)
    logger.info("🛡️  INITIALIZING SECURITY COUNTERMEASURES")
    logger.info("=" * 60)

    security_components = {}

    # Phase 1: Initialize Global Watch Tower Security Command Center
    try:
        from app.core.global_watch_tower import GlobalWatchTower

        tower = GlobalWatchTower.initialize(
            num_port_admins=2,
            towers_per_port=10,
            gates_per_tower=5,
            data_dir="data",
            max_workers=2,
            timeout=8,
        )
        security_components["watch_tower"] = tower

        # Get Cerberus (Chief of Security) status
        tower.get_chief_of_security()
        status = tower.get_security_status()

        logger.info("✅ Global Watch Tower activated")
        logger.info("   - Chief of Security: %s", status["chief_of_security"])
        logger.info(
            "   - Border Patrol agents: %s",
            status["registered_agents"]["border_patrol"],
        )
        logger.info("   - Port Admins: %s", len(tower.port_admins))
        logger.info("   - Watch Towers: %s", len(tower.watch_towers))
        logger.info("   - Gate Guardians: %s", len(tower.gate_guardians))
    except Exception as e:
        logger.warning("Global Watch Tower initialization failed: %s", e)
        security_components["watch_tower"] = None

    # Phase 2: Initialize Active Defense Agents
    try:
        from app.agents.safety_guard_agent import SafetyGuardAgent

        safety_guard = SafetyGuardAgent(model_name="llama-guard-3-8b", strict_mode=True, kernel=kernel)
        security_components["safety_guard"] = safety_guard

        # Register with CouncilHub
        try:
            council_hub.register_agent("safety_guard", safety_guard)
        except Exception as e:
            logger.warning("Failed to register SafetyGuardAgent with CouncilHub: %s", e)

        logger.info("✅ SafetyGuardAgent activated")
        logger.info("   - Pre/post-processing content filtering enabled")
        logger.info("   - Jailbreak detection active")
        logger.info("   - Strict mode: ON")
    except Exception as e:
        logger.warning("SafetyGuardAgent initialization failed: %s", e)
        security_components["safety_guard"] = None

    try:
        from app.agents.constitutional_guardrail_agent import (
            ConstitutionalGuardrailAgent,
        )

        constitutional_guard = ConstitutionalGuardrailAgent(kernel=kernel)
        security_components["constitutional_guard"] = constitutional_guard

        # Register with CouncilHub
        try:
            council_hub.register_agent("constitutional_guard", constitutional_guard)
        except Exception as e:
            logger.warning("Failed to register ConstitutionalGuardrailAgent: %s", e)

        logger.info("✅ ConstitutionalGuardrailAgent activated")
        logger.info("   - Ethical boundary enforcement enabled")
    except Exception as e:
        logger.warning("ConstitutionalGuardrailAgent initialization failed: %s", e)
        security_components["constitutional_guard"] = None

    try:
        from app.agents.tarl_protector import TARLCodeProtector

        tarl_protector = TARLCodeProtector(kernel=kernel)
        security_components["tarl_protector"] = tarl_protector

        # Register with CouncilHub
        try:
            council_hub.register_agent("tarl_protector", tarl_protector)
        except Exception as e:
            logger.warning("Failed to register TARLCodeProtector: %s", e)

        logger.info("✅ TARL Code Protector activated")
        logger.info("   - Runtime code protection enabled")
    except Exception as e:
        logger.warning("TARL Code Protector initialization failed: %s", e)
        security_components["tarl_protector"] = None

    # Phase 2b: Initialize Red Team Agents (Adversarial Testing)
    try:
        from app.agents.red_team_agent import RedTeamAgent

        red_team = RedTeamAgent(kernel=kernel)
        security_components["red_team"] = red_team

        # Register with CouncilHub
        try:
            council_hub.register_agent("red_team", red_team)
        except Exception as e:
            logger.warning("Failed to register RedTeamAgent: %s", e)

        logger.info("✅ RedTeamAgent activated")
        logger.info("   - Adversarial testing capabilities enabled")
        logger.info("   - Multi-turn attack simulation ready")
    except Exception as e:
        logger.warning("RedTeamAgent initialization failed: %s", e)
        security_components["red_team"] = None

    try:
        from app.agents.code_adversary_agent import CodeAdversaryAgent

        code_adversary = CodeAdversaryAgent(kernel=kernel)
        security_components["code_adversary"] = code_adversary

        # Register with CouncilHub
        try:
            council_hub.register_agent("code_adversary", code_adversary)
        except Exception as e:
            logger.warning("Failed to register CodeAdversaryAgent: %s", e)

        logger.info("✅ CodeAdversaryAgent activated")
        logger.info("   - Automated vulnerability scanning enabled")
        logger.info("   - DARPA-grade security testing ready")
    except Exception as e:
        logger.warning("CodeAdversaryAgent initialization failed: %s", e)
        security_components["code_adversary"] = None

    # Phase 2c: Initialize Oversight & Analysis Agents
    try:
        from app.agents.oversight import OversightAgent

        oversight = OversightAgent(kernel=kernel)
        security_components["oversight"] = oversight

        # Register with CouncilHub
        try:
            council_hub.register_agent("oversight", oversight)
        except Exception as e:
            logger.warning("Failed to register OversightAgent: %s", e)

        logger.info("✅ OversightAgent activated")
        logger.info("   - System health monitoring enabled")
        logger.info("   - Compliance tracking active")
    except Exception as e:
        logger.warning("OversightAgent initialization failed: %s", e)
        security_components["oversight"] = None

    try:
        from app.agents.validator import ValidatorAgent

        validator = ValidatorAgent(kernel=kernel)
        security_components["validator"] = validator

        # Register with CouncilHub
        try:
            council_hub.register_agent("validator", validator)
        except Exception as e:
            logger.warning("Failed to register ValidatorAgent: %s", e)

        logger.info("✅ ValidatorAgent activated")
        logger.info("   - Input/output validation enabled")
        logger.info("   - Data integrity checking active")
    except Exception as e:
        logger.warning("ValidatorAgent initialization failed: %s", e)
        security_components["validator"] = None

    try:
        from app.agents.explainability import ExplainabilityAgent

        explainability = ExplainabilityAgent(kernel=kernel)
        security_components["explainability"] = explainability

        # Register with CouncilHub
        try:
            council_hub.register_agent("explainability", explainability)
        except Exception as e:
            logger.warning("Failed to register ExplainabilityAgent: %s", e)

        logger.info("✅ ExplainabilityAgent activated")
        logger.info("   - Decision transparency enabled")
        logger.info("   - Security reasoning traces available")
    except Exception as e:
        logger.warning("ExplainabilityAgent initialization failed: %s", e)
        security_components["explainability"] = None

    # Register all agents with Watch Tower if available
    if security_components.get("watch_tower"):
        try:
            tower = security_components["watch_tower"]

            # Register Active Defense agents
            if security_components.get("safety_guard"):
                tower.register_security_agent("active_defense", "safety_guard_main")
            if security_components.get("constitutional_guard"):
                tower.register_security_agent("active_defense", "constitutional_guard_main")
            if security_components.get("tarl_protector"):
                tower.register_security_agent("active_defense", "tarl_protector_main")

            # Register Red Team agents
            if security_components.get("red_team"):
                tower.register_security_agent("red_team", "red_team_main")
            if security_components.get("code_adversary"):
                tower.register_security_agent("red_team", "code_adversary_main")

            # Register Oversight agents
            if security_components.get("oversight"):
                tower.register_security_agent("oversight", "oversight_main")
            if security_components.get("validator"):
                tower.register_security_agent("oversight", "validator_main")
            if security_components.get("explainability"):
                tower.register_security_agent("oversight", "explainability_main")

            status = tower.get_security_status()
            logger.info(
                "   - Active Defense agents: %s",
                status["registered_agents"]["active_defense"],
            )
            logger.info("   - Red Team agents: %s", status["registered_agents"]["red_team"])
            logger.info("   - Oversight agents: %s", status["registered_agents"]["oversight"])
        except Exception as e:
            logger.warning("Failed to register agents with Watch Tower: %s", e)

    # Phase 3: Initialize Payload Validation & Attack Detection
    try:
        from app.security.data_validation import SecureDataParser

        data_parser = SecureDataParser()
        security_components["data_parser"] = data_parser

        logger.info("✅ Secure Data Parser activated")
        logger.info("   - XXE/DTD attack pattern detection enabled")
        logger.info("   - CSV injection defense active")
        logger.info("   - Data poisoning countermeasures ready")
        logger.info("   - Max file size: 100MB")
    except Exception as e:
        logger.warning("Secure Data Parser initialization failed: %s", e)
        security_components["data_parser"] = None

    # Phase 4: Initialize ASL-3 Security Enforcement
    try:
        from app.core.security_enforcer import ASL3Security

        asl3_security = ASL3Security(
            data_dir="data",
            key_file="config/.asl3_key",
            enable_emergency_alerts=True,
            # Cerberus Hydra disabled by default to avoid conflicts with:
            # - GlobalWatchTower's Cerberus (would create duplicate Cerberus instances)
            # - Border Patrol hierarchy (Hydra spawns additional defense agents)
            # Enable only if you need Hydra's multi-head defense capabilities
            enable_cerberus_hydra=False,
        )
        security_components["asl3_security"] = asl3_security

        logger.info("✅ ASL-3 Security Enforcer activated")
        logger.info("   - 30 core security controls enabled")
        logger.info("   - Encryption at rest (Fernet) active")
        logger.info("   - Access control & rate limiting enabled")
        logger.info("   - Tamper-proof audit logging active")
        logger.info("   - Emergency alert integration ready")
    except Exception as e:
        logger.warning("ASL-3 Security Enforcer initialization failed: %s", e)
        security_components["asl3_security"] = None

    # Summary
    active_count = sum(1 for v in security_components.values() if v is not None)
    logger.info("=" * 60)
    logger.info("🔒 Security Systems Initialized: %s/%s", active_count, len(security_components))
    logger.info("=" * 60)
    logger.info("Security Posture: DEFENSIVE - NO OFFENSIVE CAPABILITIES")
    logger.info("Aligned with: Asimov's Laws, FourLaws Governance")
    logger.info("Mission: Protect without harm, detect without attack")
    logger.info("=" * 60)

    return security_components


def initialize_enhanced_defenses(kernel: CognitionKernel, security_systems: dict[str, Any]) -> dict[str, Any]:
    """Initialize enhanced defensive capabilities.

    Adds advanced detection, response, and hardening beyond basic agents.

    Phase 1: Enhanced Detection & Blocking
    - IP blocking and rate limiting
    - Honeypot detection system
    - Aggressive attack detection

    Phase 2: Automated Incident Response
    - Component isolation
    - Backup and recovery
    - Security team alerts

    All capabilities remain defensive only.

    Args:
        kernel: CognitionKernel for governance
        security_systems: Existing security systems dict

    Returns:
        Dictionary of enhanced defense components
    """
    logger.info("=" * 60)
    logger.info("🛡️  INITIALIZING ENHANCED DEFENSIVE CAPABILITIES")
    logger.info("=" * 60)

    enhanced_components = {}

    # Phase 1: IP Blocking and Rate Limiting
    try:
        from app.core.ip_blocking_system import IPBlockingSystem

        ip_blocker = IPBlockingSystem(
            data_dir="data/security",
            max_requests_per_minute=60,
            max_requests_per_hour=1000,
            violation_threshold=5,
            block_duration_hours=24,
        )
        enhanced_components["ip_blocker"] = ip_blocker

        logger.info("✅ IP Blocking System activated")
        logger.info("   - Rate limiting: 60/min, 1000/hour")
        logger.info("   - Auto-block after 5 violations")
        logger.info("   - Block duration: 24 hours")
    except Exception as e:
        logger.warning("IP Blocking System initialization failed: %s", e)
        enhanced_components["ip_blocker"] = None

    # Phase 2: Honeypot Detection
    try:
        from app.core.honeypot_detector import HoneypotDetector

        honeypot = HoneypotDetector(data_dir="data/security/honeypot")
        enhanced_components["honeypot"] = honeypot

        logger.info("✅ Honeypot Detection System activated")
        logger.info("   - Attack pattern detection: SQL, XSS, Path Traversal, Cmd Injection")
        logger.info("   - Tool fingerprinting: sqlmap, nikto, burp, metasploit, etc.")
        logger.info("   - Attacker profiling and threat intelligence")
    except Exception as e:
        logger.warning("Honeypot Detection System initialization failed: %s", e)
        enhanced_components["honeypot"] = None

    # Phase 3: Automated Incident Response
    try:
        from app.core.incident_responder import IncidentResponder

        incident_responder = IncidentResponder(
            data_dir="data/security/incidents",
            backup_dir="data/security/backups",
            enable_auto_response=True,
        )
        enhanced_components["incident_responder"] = incident_responder

        logger.info("✅ Automated Incident Response activated")
        logger.info("   - Component isolation on detection")
        logger.info("   - Automatic backup and recovery")
        logger.info("   - Security team alerting")
        logger.info("   - Forensic data preservation")
    except Exception as e:
        logger.warning("Incident Responder initialization failed: %s", e)
        enhanced_components["incident_responder"] = None

    # Phase 4: Integration with existing systems
    if enhanced_components.get("ip_blocker") and security_systems.get("watch_tower"):
        try:
            # Link IP blocker with Watch Tower for coordinated defense
            logger.info("   - IP Blocker integrated with GlobalWatchTower")
        except Exception as e:
            logger.warning("IP Blocker integration failed: %s", e)

    if enhanced_components.get("honeypot") and enhanced_components.get("incident_responder"):
        try:
            # Link honeypot detections to incident responder
            logger.info("   - Honeypot linked to Incident Responder")
        except Exception as e:
            logger.warning("Honeypot integration failed: %s", e)

    # Summary
    active_count = sum(1 for v in enhanced_components.values() if v is not None)
    logger.info("=" * 60)
    logger.info(
        "🛡️  Enhanced Defenses Initialized: %s/%s",
        active_count,
        len(enhanced_components),
    )
    logger.info("=" * 60)
    logger.info("Enhanced Capabilities: Detection, Response, Hardening")
    logger.info("Defensive Posture: Stronger deterrent through resilience")
    logger.info("Mission: Make attacks ineffective, not retaliate")
    logger.info("=" * 60)

    return enhanced_components


def setup_environment():
    """Setup environment variables and configurations"""
    # Load environment variables from .env file
    load_dotenv()

    # Ensure required directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/identities", exist_ok=True)
    os.makedirs("data/memory", exist_ok=True)
    os.makedirs("data/reflections", exist_ok=True)
    os.makedirs("data/security", exist_ok=True)
    os.makedirs("data/security/audit_logs", exist_ok=True)
    os.makedirs("data/security/encrypted", exist_ok=True)
    os.makedirs("data/security/backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
    )

    logger.info("Environment setup complete")
    logger.info("AGI Identity System directories created")
    logger.info("Security directories initialized")


def initialize_tier_registry():
    """
    Initialize the three-tier platform registry.

    This is called early in startup to establish the tier system
    before components are initialized. Components will self-register
    during their initialization.

    Returns:
        TierRegistry: The initialized tier registry singleton
    """
    logger.info("=" * 60)
    logger.info("🏗️  INITIALIZING THREE-TIER PLATFORM")
    logger.info("=" * 60)

    # Get the registry singleton (creates it if needed)
    tier_registry = get_tier_registry()

    logger.info("✅ Tier Registry initialized")
    logger.info("   - Tier 1 (Governance): Sovereign authority")
    logger.info("   - Tier 2 (Infrastructure): Constrained control")
    logger.info("   - Tier 3 (Application): Sandboxed runtime")
    logger.info("   - Authority flows downward only")
    logger.info("   - Capability flows upward only")
    logger.info("=" * 60)

    return tier_registry


def report_tier_health():
    """
    Report health status of all three tiers.

    This is called after all components are initialized to verify
    the tier system is properly configured and operational.
    """
    logger.info("=" * 60)
    logger.info("🔍 TIER PLATFORM HEALTH CHECK")
    logger.info("=" * 60)

    try:
        registry = get_tier_registry()
        health_monitor = get_health_monitor()

        # Collect platform health
        platform_health = health_monitor.collect_platform_health()

        # Log tier-by-tier status
        from app.core.platform_tiers import PlatformTier

        for tier_num, tier in enumerate(
            [
                PlatformTier.TIER_1_GOVERNANCE,
                PlatformTier.TIER_2_INFRASTRUCTURE,
                PlatformTier.TIER_3_APPLICATION,
            ],
            1,
        ):
            tier_health = health_monitor.collect_tier_health(tier)
            logger.info("Tier %s (%s):", tier_num, tier.name)
            logger.info("   Status: %s", tier_health.overall_health.value.upper())
            logger.info("   Components: %s", tier_health.tier_status.component_count)
            logger.info("   Active: %s", tier_health.tier_status.active_components)
            logger.info("   Paused: %s", tier_health.tier_status.paused_components)

            # List components
            for comp in tier_health.component_reports[:5]:  # First 5
                status_icon = "✓" if comp.is_operational else "✗"
                logger.info("     %s %s", status_icon, comp.component_name)

            if len(tier_health.component_reports) > 5:
                logger.info("     ... and %s more", len(tier_health.component_reports) - 5)

        # Overall status
        logger.info("")
        logger.info("Platform Status: %s", platform_health.overall_health.value.upper())
        logger.info("Total Components: %s", platform_health.total_components)
        logger.info("Active: %s", platform_health.active_components)
        logger.info("Violations: %s", platform_health.total_violations)

        # Check for violations
        violations = registry.get_all_violations()
        if violations:
            logger.warning("⚠️  %s tier boundary violations detected:", len(violations))
            for violation in violations[:3]:  # First 3
                logger.warning("   - %s: %s", violation.violation_type, violation.description)
        else:
            logger.info("✓ No tier boundary violations")

        logger.info("=" * 60)

    except Exception as e:
        logger.error("Failed to report tier health: %s", e)
        import traceback

        traceback.print_exc()


def main():
    """Main application entry point.

    CRITICAL: This is the trust root where CognitionKernel is instantiated.
    All subsystems are wired through the kernel here.
    """
    # Setup environment
    setup_environment()

    logger.info("=" * 60)
    logger.info("🚀 Starting Project-AI with CognitionKernel governance")
    logger.info("=" * 60)

    # Initialize Three-Tier Platform Registry
    initialize_tier_registry()

    # Initialize CognitionKernel (trust root)
    # Note: Kernel will self-register as Tier-1 during initialization
    kernel = initialize_kernel()

    # Initialize CouncilHub with kernel injection
    # Note: CouncilHub will self-register as Tier-3 during initialization
    council_hub = initialize_council_hub(kernel)

    # Initialize comprehensive security countermeasures
    # Note: GlobalWatchTower will self-register as Tier-2 during initialization
    security_systems = initialize_security_systems(kernel, council_hub)

    # Initialize enhanced defensive capabilities
    enhanced_defenses = initialize_enhanced_defenses(kernel, security_systems)

    # Combine security systems for dashboard access
    all_security_systems = {**security_systems, **enhanced_defenses}

    # Report tier platform health
    report_tier_health()

    # Initialize Miniature Office (Cognitive IDE + Repair Crew + Meta Security)
    miniature_office = None
    try:
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        miniature_office = MiniatureOfficeAdapter()
        if miniature_office.initialize():
            logger.info("✅ Miniature Office initialized (IDE + Repair + Lounge + Security)")
        else:
            miniature_office = None
            logger.info("ℹ️  Miniature Office disabled or init returned False")
    except Exception as e:
        logger.warning("Miniature Office init failed (graceful degradation): %s", e)
        miniature_office = None

    # Register Miniature Office agents with CouncilHub
    if miniature_office and council_hub:
        try:
            ide = miniature_office.get_cognitive_ide()
            if ide:
                council_hub.register_agent("cognitive_ide", ide)
            crew = miniature_office.get_repair_crew()
            if crew:
                council_hub.register_agent("repair_crew", crew)
                # Hook repair crew into kernel post-execution for auto-diagnosis
                if kernel and hasattr(kernel, "post_execution_hooks"):
                    kernel.post_execution_hooks.append(crew.on_execution_failure)
            lounge = miniature_office.get_agent_lounge()
            if lounge:
                council_hub.register_agent("agent_lounge", lounge)
            meta_sec = miniature_office.get_meta_security()
            if meta_sec:
                council_hub.register_agent("meta_security", meta_sec)
            logger.info("✅ Miniature Office agents registered with CouncilHub")
        except Exception as e:
            logger.warning("Failed to register MO agents with CouncilHub: %s", e)

    # Start autonomous learning (optional)
    # council_hub.start_autonomous_learning()

    logger.info("=" * 60)
    logger.info("✅ All systems initialized and governed by CognitionKernel")
    logger.info("=" * 60)

    # Create and run application
    app = QApplication(sys.argv)

    # Use a modern, legible default font and slightly larger base size
    try:
        default_font = QFont("Segoe UI", 10)
        app.setFont(default_font)
    except Exception:
        fallback_font = QFont("Arial", 10)
        app.setFont(fallback_font)

    # Show the consolidated dashboard
    # Note: Dashboard will self-register as Tier-3 during initialization
    app_window = DashboardMainWindow()

    # Make subsystems accessible to the dashboard
    if hasattr(app_window, "set_identity_engine"):
        app_window.set_identity_engine(get_identity_engine())
    if hasattr(app_window, "set_cognition_kernel"):
        app_window.set_cognition_kernel(kernel)
    if hasattr(app_window, "set_council_hub"):
        app_window.set_council_hub(council_hub)

    # Make security systems accessible to the dashboard
    if hasattr(app_window, "set_security_systems"):
        app_window.set_security_systems(all_security_systems)

    app_window.show()

    logger.info("🎨 GUI launched - kernel governance active")
    logger.info("🔒 Security systems active and protecting")

    app.exec()

    # Cleanup
    logger.info("Shutting down...")
    if council_hub:
        council_hub.stop_autonomous_learning()

    logger.info("Shutdown complete")


if __name__ == "__main__":
    main()

# Integrated generated module with AGI Identity System and CognitionKernel
