# Core AI Systems Architecture

```mermaid
graph TB
    subgraph "GUI Layer"
        UI[LeatherBookInterface<br/>PyQt6 Main Window]
        DASH[LeatherBookDashboard<br/>6-Zone Layout]
        PERSONA[PersonaPanel<br/>4-Tab Configuration]
    end

    subgraph "Core AI Systems (ai_systems.py - 470 lines)"
        FL[FourLaws<br/>Immutable Ethics]
        AP[AIPersona<br/>8 Personality Traits]
        MEM[MemoryExpansionSystem<br/>Knowledge Base]
        LRM[LearningRequestManager<br/>Human-in-Loop]
        CO[CommandOverride<br/>SHA-256 Protection]
        PM[PluginManager<br/>Enable/Disable]
    end

    subgraph "Feature Modules"
        UM[UserManager<br/>bcrypt Auth]
        LP[LearningPaths<br/>OpenAI GPT]
        DA[DataAnalysis<br/>K-means ML]
        SR[SecurityResources<br/>GitHub API]
        LT[LocationTracker<br/>Fernet Encryption]
        EA[EmergencyAlert<br/>Email System]
        IE[IntelligenceEngine<br/>Chat GPT]
        ID[IntentDetection<br/>Scikit-learn]
        IG[ImageGenerator<br/>DALL-E/SD]
    end

    subgraph "AI Agents"
        OV[Oversight<br/>Safety Validation]
        PL[Planner<br/>Task Decomposition]
        VA[Validator<br/>Input/Output Check]
        EX[Explainability<br/>Decision Logs]
    end

    subgraph "Data Persistence"
        U_JSON[users.json<br/>bcrypt hashes]
        P_JSON[ai_persona/state.json<br/>Mood & Traits]
        M_JSON[memory/knowledge.json<br/>6 Categories]
        L_JSON[learning_requests/<br/>requests.json]
        BV[Black Vault<br/>Denied Content]
        AL[Audit Logs<br/>Override History]
    end

    %% GUI to Core Systems
    UI --> DASH
    UI --> PERSONA
    DASH --> FL
    DASH --> AP
    DASH --> MEM
    PERSONA --> AP

    %% Core Systems Interactions
    FL -.validates.-> AP
    FL -.validates.-> MEM
    FL -.validates.-> LRM
    AP --> MEM
    MEM --> LRM
    CO --> FL
    PM --> FL

    %% Core to Feature Modules
    AP --> IE
    MEM --> LP
    LRM --> LP
    IE --> ID

    %% Feature Modules to Agents
    IE --> OV
    LP --> PL
    DA --> VA
    SR --> OV

    %% Agents to Data
    OV --> AL
    PL --> M_JSON
    VA --> BV
    EX --> AL

    %% Core Systems to Data
    UM --> U_JSON
    AP --> P_JSON
    MEM --> M_JSON
    LRM --> L_JSON
    CO --> AL
    FL --> BV

    %% Styling
    classDef guiClass fill:#00ff00,stroke:#00ffff,stroke-width:2px,color:#000
    classDef coreClass fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef featureClass fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff
    classDef agentClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef dataClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff

    class UI,DASH,PERSONA guiClass
    class FL,AP,MEM,LRM,CO,PM coreClass
    class UM,LP,DA,SR,LT,EA,IE,ID,IG featureClass
    class OV,PL,VA,EX agentClass
    class U_JSON,P_JSON,M_JSON,L_JSON,BV,AL dataClass
```

## Architecture Notes

### Six Integrated AI Systems

All six core systems reside in `src/app/core/ai_systems.py` (470 lines) for cohesive integration:

1. **FourLaws** (Lines 1-120): Validates all actions against Asimov's Laws hierarchy
2. **AIPersona** (Lines 125-230): 8 personality traits, mood tracking, interaction counts
3. **MemoryExpansionSystem** (Lines 235-295): Conversation logs, 6-category knowledge base
4. **LearningRequestManager** (Lines 300-335): Human approval workflow, Black Vault for denied content
5. **CommandOverride** (Lines 400-470): Master password system with audit logging
6. **PluginManager** (Lines 340-395): Simple enable/disable plugin system

### Data Persistence Pattern

- **JSON-based**: All systems use JSON files in `data/` directory
- **Atomic saves**: Every state mutation calls `_save_state()` or `save_users()`
- **Isolated testing**: All constructors accept `data_dir` parameter for test isolation
- **Encryption**: Sensitive data uses Fernet (location history, cloud sync)

### Validation Flow

```
User Action → FourLaws.validate_action() → Context Evaluation → Allow/Deny
              ↓                              ↓
          Log to Audit                   Check Black Vault
```

### Integration Points

- **OpenAI**: `learning_paths.py`, `intelligence_engine.py`, `image_generator.py`
- **Hugging Face**: `image_generator.py` (Stable Diffusion 2.1)
- **GitHub API**: `security_resources.py` (CTF/security repos)
- **IP Geolocation**: `location_tracker.py` (encrypted GPS history)

### Module Import Pattern

```python
from app.core.ai_systems import FourLaws, AIPersona, MemoryExpansionSystem
from app.core.user_manager import UserManager
from app.agents.oversight import OversightAgent
```

**Critical**: Always use `python -m src.app.main` (not `python src/app/main.py`) for correct PYTHONPATH resolution.
