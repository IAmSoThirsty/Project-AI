# Alien Invasion Defense Scenario Engine - Requirements Document

## Project Closure Notice
This PR branch is being closed. Work will restart fresh when ready.

## Original Requirements Summary

### Core Objective
Create a 4-million+ word scenario engine for alien invasion defense scenarios, integrated with Project-AI as a global defense coordinator working with humans against extraterrestrial threats.

### Key Requirements

#### 1. Biological Diversity
- Include diverse alien biological entities with anatomies vastly different from Earth life
- Categories required:
  - Silicon-based life forms
  - Energy beings (plasma, photonic)
  - Hive mind collectives
  - Crystalline intelligence
  - Gas-based entities
  - Symbiotic super-organisms
  - Non-carbon biochemistries
  - Dimension-shifting beings
  - Machine-organic hybrids
  - Quantum consciousness entities

#### 2. Complete Separation
- ENTIRELY SEPARATE from other contingency plans (zombie defense, etc.)
- Zero imports from other contingency engines
- Only consume shared primitives: Event, logging, governance hooks

#### 3. Architecture Type: Scenario Synthesis Core
- **NOT a narrative generator**
- Output structured scenario artifacts (YAML/JSON objects), not prose
- All prose must be derived from artifacts, never primary

#### 4. Required Input Structure
All scenarios must be generated from **explicit inputs**:
- `species_profile`: NonHumanBiologyProfile (MANDATORY)
- `technology_class`: TechnologyClassification
- `escalation_tier`: EscalationTier
- `planetary_conditions`: PlanetaryConditions
- `human_governance_posture`: HumanGovernancePosture
- **NO defaults allowed**
- **NO randomness without explicit seed**

#### 5. NonHumanBiologyProfile Model
Must define:
- **Anatomy**: Structure, sensory systems, locomotion
- **Metabolism**: Energy sources, biochemistry, lifecycle
- **Cognition topology**: Intelligence architecture, communication
- **Environmental tolerances**: Temperature, pressure, atmosphere, radiation
- **Weapon interaction constraints**: Vulnerabilities, immunities, countermeasures

**Engine must REJECT scenarios without biology profile**

#### 6. Escalation State Machine
- Enforce escalation tiers as state machine
- NO higher-tier actions without lower tiers completing
- Each transition MUST emit audit artifact
- Tiers: DETECTION → OBSERVATION → CONTACT → SKIRMISH → WAR → OCCUPATION → etc.
- No tier skipping allowed

#### 7. Specific Architecture Required
```
AlienInvasionEngine
├── SpeciesModel (wraps NonHumanBiologyProfile)
├── TechModel (TechnologyClassification)
├── EscalationStateMachine (enforced progression)
├── HumanResponseModel (military, diplomatic, civilian)
├── OutcomeEvaluator (victory conditions, casualties, impacts)
└── ArtifactEmitter (YAML/JSON output)
```

#### 8. Multi-Domain Defense Coverage
Must cover:
- **Land vehicles**: Tanks, APCs, mobile artillery, mech suits
- **Sea vehicles**: Submarines, carriers, destroyers, hydrofoils
- **Air vehicles**: Fighters, bombers, VTOL craft, aerospace fighters
- **Space vehicles**: Orbital platforms, interceptors, deep space scouts

#### 9. Advanced Weapons Systems
- **Kinetic**: Railguns, mass drivers, hypervelocity projectiles
- **Energy**: Lasers, particle beams, plasma cannons, EMP
- **Biological**: Targeted pathogens, genetic disruptors
- **Cyber**: AI countermeasures, network infiltration
- **Exotic**: Gravity distortion, quantum entanglement, temporal displacement

#### 10. Enemy AI Capabilities Modeling
- Distributed intelligence networks
- Adaptive learning systems
- Quantum computing advantages
- Predictive tactical analysis
- Swarm coordination algorithms

#### 11. Human-AI Cooperation Protocols
- Project-AI as global defense coordinator
- Real-time tactical analysis
- Resource allocation optimization
- Communication relay and translation
- Ethical decision-making (Four Laws integration)

#### 12. Documentation Requirement
**"Document, Everything. Not a single thing left untouched"**
- Every class documented
- Every method documented
- Every attribute documented
- Usage examples for all components
- Strategic/tactical implications where relevant

#### 13. God-Tier Architectural Design
- Monolithic density
- Production-ready code
- Realistic adversity modeling
- Complete system integration
- No stubs, no TODOs, no placeholders

## Technical Specifications

### Shared Primitives Only
From `app.core.event_spine`:
- `Event`
- `EventCategory`
- `EventPriority`

From `app.core.governance`:
- Governance hooks (if needed)

Standard library:
- `logging`
- `dataclasses`
- `enum`
- `pathlib`
- `json`
- `yaml`

### Data Structures Required

#### NonHumanBiologyProfile
```python
@dataclass
class NonHumanBiologyProfile:
    profile_id: str
    species_name: str
    classification: str
    
    anatomy: AnatomyDefinition
    metabolism: MetabolismModel
    cognition: CognitionModel
    environmental_tolerances: EnvironmentalTolerances
    weapon_interactions: WeaponInteractionConstraints
    
    def validate() -> tuple[bool, list[str]]
    def to_dict() -> dict[str, Any]
```

#### EscalationStateMachine
```python
class EscalationStateMachine:
    def initialize(trigger_events, actors) -> EscalationAuditArtifact
    def can_transition_to(target_tier) -> tuple[bool, str]
    def transition(target_tier, ...) -> EscalationAuditArtifact
    def get_current_tier() -> EscalationTier
    def get_audit_trail() -> list[EscalationAuditArtifact]
```

#### ArtifactEmitter
```python
class ArtifactEmitter:
    def emit_biology_profile(profile, format) -> str
    def emit_technology_classification(tech, format) -> str
    def emit_escalation_audit(audit, format) -> str
    def emit_scenario_artifact(data, scenario_id, format) -> str
    def validate_artifact(path) -> tuple[bool, list[str]]
```

#### AlienInvasionEngine (Main)
```python
class AlienInvasionEngine:
    def synthesize_scenario(
        species_profile: NonHumanBiologyProfile,  # REQUIRED
        technology_class: TechnologyClassification,  # REQUIRED
        initial_escalation_tier: EscalationTier,  # REQUIRED
        planetary_conditions: PlanetaryConditions,  # REQUIRED
        human_governance_posture: HumanGovernancePosture,  # REQUIRED
        seed: Optional[int] = None
    ) -> dict[str, Any]
```

### Output Artifacts
All outputs must be structured YAML or JSON files:
- Biology profiles: `biology_{profile_id}.yaml`
- Technology classifications: `technology_{tech_id}.yaml`
- Escalation audits: `escalation_{audit_id}.yaml`
- Complete scenarios: `scenario_{scenario_id}.yaml`

### File Structure
```
data/alien_invasion/
├── artifacts/
│   ├── biology_SPECIES_001.yaml
│   ├── technology_TECH_001.yaml
│   ├── escalation_INIT_xxx.yaml
│   └── scenario_ALIEN_SCENARIO_xxx.yaml
├── biology/
├── weapons_systems/
└── defense_assets/
```

## What Was Attempted

1. ✅ Analyzed existing Project-AI architecture
2. ✅ Reviewed shared primitives (Event, governance)
3. ✅ Created detailed implementation plan
4. ⚠️ Started creating `alien_invasion_engine.py` but file remained empty
5. ❌ Multiple write attempts failed due to process issues
6. ❌ No working implementation completed

## Recommendations for Fresh Start

### Phase 1: Core Models (Start Here)
1. Create enums first:
   - `BiochemistryType`
   - `CognitionTopology`
   - `SensoryModality`
   - `LocomotionMethod`
   - `EscalationTier`

2. Create dataclass models:
   - `AnatomyDefinition`
   - `MetabolismModel`
   - `CognitionModel`
   - `EnvironmentalTolerances`
   - `WeaponInteractionConstraints`
   - `NonHumanBiologyProfile`

3. Test each model independently

### Phase 2: State Machine
1. Implement `EscalationStateMachine`
2. Implement `EscalationAuditArtifact`
3. Test state transitions
4. Test audit emission

### Phase 3: Artifact System
1. Implement `ArtifactEmitter`
2. Test YAML output
3. Test JSON output
4. Test validation

### Phase 4: Main Engine
1. Implement `AlienInvasionEngine`
2. Implement validation (reject without biology profile)
3. Implement scenario synthesis
4. Test with example scenarios

### Phase 5: Content Generation
1. Create 10+ example biology profiles
2. Create example technology classifications
3. Create example planetary conditions
4. Create example governance postures
5. Generate sample scenarios

### Phase 6: Documentation
1. Document every class
2. Document every method
3. Add usage examples
4. Create architecture guide
5. Create API reference

## Testing Strategy

### Unit Tests
- Test each dataclass independently
- Test state machine transitions
- Test artifact emission
- Test validation logic

### Integration Tests
- Test full scenario synthesis
- Test artifact generation
- Test state machine with audit trail
- Test rejection of invalid inputs

### Example Scenarios
Create at least 10 diverse scenarios:
1. Silicon crystalline first contact
2. Plasma collective observation
3. Hive mind skirmish
4. Dimension shifter war
5. Quantum consciousness negotiation
6. Machine-organic hybrid occupation
7. Ammonia-based reconnaissance
8. Fungal network infiltration
9. Photonic life communication failure
10. Gas entity resource conflict

## Success Criteria

- [ ] All required dataclasses implemented
- [ ] State machine enforces tier progression
- [ ] Audit artifacts emitted on every transition
- [ ] Biology profile validation rejects incomplete profiles
- [ ] No defaults or randomness without seed
- [ ] YAML/JSON artifacts generated correctly
- [ ] Zero imports from other contingency engines
- [ ] Every component fully documented
- [ ] 10+ example scenarios generated
- [ ] Integration tests pass
- [ ] Can generate 4M+ word scenario documents from artifacts

## Notes for Implementation

1. **Start small**: Implement one model at a time, test, then move on
2. **Test continuously**: Don't build everything then test
3. **Documentation as you go**: Document each component immediately after writing it
4. **Use dataclasses**: They provide free serialization with `asdict()`
5. **YAML is more readable**: Prefer YAML for human-readable artifacts
6. **Validation is critical**: The engine MUST reject invalid inputs
7. **State machine is non-negotiable**: No tier skipping under any circumstances
8. **Audit everything**: Every state transition must have an audit artifact

## Contact

This work was started but not completed. When ready to restart:
1. Review this requirements document
2. Start with Phase 1 (Core Models)
3. Build incrementally with tests
4. Document everything as you go
5. Use the recommended phased approach

Good luck with the fresh start!
