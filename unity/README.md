# Project-AI VR Module - Unity C# Implementation

## Overview

This module provides a complete C# VR interface layer for Project-AI, implementing two major systems:

1. **User Autonomy System**: Natural language classification, intent evaluation, and policy-based decision making
1. **Genesis Event System**: First-time VR experience with scripted orb formation and environment awakening

## Architecture

```
unity/
├── ProjectAI/
│   └── Scripts/
│       ├── Core/                          # Core infrastructure
│       │   ├── RoleManager.cs            # User role tracking and permissions
│       │   └── SceneInitializer.cs       # Scene startup and Genesis triggering
│       └── VR/                            # VR-specific systems
│           ├── Autonomy/                  # User Autonomy System
│           │   ├── RequestModels.cs      # Data models and enums
│           │   ├── RequestClassifier.cs  # NLP classification
│           │   ├── PolicyRule.cs         # Policy rule definitions
│           │   ├── DefaultPolicyRules.cs # Default policy set
│           │   ├── PolicyEngine.cs       # Policy evaluation engine
│           │   └── AutonomyManager.cs    # Main orchestrator
│           ├── Genesis/                   # Genesis Event System
│           │   ├── GenesisConfigModels.cs    # Configuration models
│           │   ├── GenesisConfigLoader.cs    # JSON config loader
│           │   └── GenesisManager.cs         # State machine
│           ├── Conversation/              # Conversation integration
│           │   └── ConversationContextManager.cs
│           ├── Bridge/                    # VR communication layer
│           │   └── VRBridgeClient.cs     # Action packets and backend bridge
│           └── World/                     # VR world controllers
│               ├── Presence/
│               │   └── PresenceController.cs  # Orb control
│               └── Rooms/
│                   └── LightingController.cs  # Archive room lighting
└── StreamingAssets/
    └── ProjectAI/
        └── GenesisConfig.json             # Genesis configuration file
```

## User Autonomy System

### Purpose

Routes user input through natural language classification and policy evaluation to determine appropriate AI responses.

### Components

#### 1. RequestModels.cs

Defines core data structures:

- `RequestType` enum: Command, Request, Suggestion, Casual
- `RequestOutcome` enum: Comply, Decline, Modify, Ignore
- `RequestContext`: User role, environment, Genesis state, metadata
- `RequestOutcomeResult`: Classification result with confidence score

#### 2. RequestClassifier.cs

Natural language classification using keyword matching:

- Classifies requests into one of four types
- Returns confidence score (0-1)
- Extracts intent/action from text
- Uses linguistic pattern matching

#### 3. PolicyRule.cs

Defines policy rules with:

- Conditions: Request type, user role, environment
- Priority weighting
- Default outcomes
- Confirmation requirements

#### 4. DefaultPolicyRules.cs

Provides default policy set:

- Block commands during Genesis (priority 100)
- Owner commands auto-comply (priority 50)
- Guest commands need confirmation (priority 40)
- Requests generally comply (priority 30)
- Suggestions may be modified (priority 20)
- Casual conversation ignored (priority 10)

#### 5. PolicyEngine.cs

Evaluates requests against rules:

- Loads and manages policy rules
- Finds highest-priority matching rule
- Returns outcome with reasoning
- Supports custom rule addition/removal

#### 6. AutonomyManager.cs

Main orchestrator (Singleton MonoBehaviour):

- Processes user requests end-to-end
- Coordinates classification and policy evaluation
- Executes outcomes (comply/modify/decline/ignore)
- Logs all decisions for audit trail
- Emits events for other systems

### Usage Example

```csharp
using ProjectAI.VR.Autonomy;

// Create request context
var context = new RequestContext
{
    UserRole = "owner",
    UserId = "user123",
    Environment = "ArchiveRoom",
    IsGenesisActive = false
};

// Process request
var result = AutonomyManager.Instance.ProcessRequest(
    "Turn off the lights", 
    context
);

// Result contains:
// - ClassifiedType: Command
// - Decision: Comply
// - Reason: "Owner command accepted"
// - ConfidenceScore: 0.85
```

## Genesis Event System

### Purpose

Provides a scripted first-time VR experience where the AI orb materializes and the environment awakens.

### State Machine

```
Dormant
   ↓
OrbForming (3s)
   ↓
SubsystemsIgniting (4s)
   ↓
PresenceStabilizing (3s)
   ↓
RoomAwakening (5s)
   ↓
Acknowledgement (4s)
   ↓
Complete
```

### Components

#### 1. GenesisConfigModels.cs

Data models:

- `GenesisState` enum: All 7 states
- `GenesisConfig`: Complete configuration
- `GenesisTimings`: Duration for each state
- `GenesisRoleConfig`: Role-specific narration and permissions

#### 2. GenesisConfigLoader.cs

JSON configuration loader:

- Loads from `StreamingAssets/ProjectAI/GenesisConfig.json`
- Creates default config if file missing
- Validates configuration
- Supports save/load operations

#### 3. GenesisManager.cs

State machine orchestrator (Singleton MonoBehaviour):

- Manages Genesis sequence progression
- Triggers state-specific logic
- Emits narration at each state
- Tracks progress (0-1)
- Marks completion in PlayerPrefs
- Supports role-based interruption

### Configuration File

`StreamingAssets/ProjectAI/GenesisConfig.json`:

```json
{
  "Timings": {
    "OrbFormingDuration": 3.0,
    "SubsystemsIgnitingDuration": 4.0,
    "PresenceStabilizingDuration": 3.0,
    "RoomAwakeningDuration": 5.0,
    "AcknowledgementDuration": 4.0
  },
  "RoleConfigs": {
    "owner": {
      "RoleName": "owner",
      "AllowInterruption": true,
      "NarrationLines": [
        "Initializing... Coalescing form...",
        "Core systems coming online...",
        "Presence stabilizing...",
        "Archive awakening...",
        "Genesis complete. Welcome, Owner."
      ]
    }
  }
}
```

### Usage Example

```csharp
using ProjectAI.VR.Genesis;

// Check if Genesis needed
bool needsGenesis = GenesisManager.Instance.ShouldTriggerGenesis("user123");

if (needsGenesis)
{
    // Subscribe to events
    GenesisManager.Instance.OnStateChanged += HandleStateChanged;
    GenesisManager.Instance.OnNarration += HandleNarration;
    GenesisManager.Instance.OnGenesisComplete += HandleComplete;
    
    // Start Genesis
    GenesisManager.Instance.StartGenesis("owner");
}

// Check active state
bool active = GenesisManager.Instance.IsGenesisActive;
float progress = GenesisManager.Instance.OverallProgress;
```

## Integration Layer

### RoleManager.cs

Tracks current user role and permissions:

- Singleton with persistent state (PlayerPrefs)
- Emits role change events
- Provides privilege checking methods
- Used by all systems for authorization

### SceneInitializer.cs

Startup coordinator:

- Initializes all core systems
- Checks for first-time users
- Triggers Genesis if needed
- Transitions to normal mode after Genesis

### ConversationContextManager.cs

Conversation processing with autonomy integration:

- Processes user messages through autonomy pipeline
- Blocks commands during Genesis (unless privileged)
- Maintains conversation history
- Generates AI responses
- Integrates with VRBridgeClient for display

### VRBridgeClient.cs

Communication bridge:

- Sends action packets to VR systems
- Tags actions with autonomy outcomes
- Provides context updates
- Manages connection to Python backend
- Executes VR actions (lighting, orb movement, text display, etc.)

### PresenceController.cs

AI orb presence control:

- Manages orb formation during Genesis
- Locks position during Genesis
- Controls emotion display
- Provides movement API

### LightingController.cs

Archive room lighting:

- Animates lighting during Genesis RoomAwakening
- Provides normal lighting control
- Supports color and intensity changes
- Blocks changes during Genesis

## Integration Points

### With Python Backend

The VR module is designed to integrate with the existing Python core:

```csharp
// VRBridgeClient sends packets to Python backend
var packet = new VRActionPacket
{
    ActionType = "GetAIResponse",
    Parameters = { { "Message", userMessage } }
};
VRBridgeClient.Instance.SendAction(packet);
```

Backend URL configured in VRBridgeClient component (default: `http://localhost:5000`)

### With Unity VR Assets

The controllers expect Unity GameObjects:

```csharp
// PresenceController expects orb GameObject
[SerializeField] private GameObject orbObject;

// LightingController expects Light components
[SerializeField] private Light[] roomLights;
```

## Events and Callbacks

### Autonomy Events

```csharp
AutonomyManager.Instance.OnRequestProcessed += (request, result) => { };
AutonomyManager.Instance.OnActionExecuted += (intent, outcome) => { };
AutonomyManager.Instance.OnRequestDeclined += (reason) => { };
```

### Genesis Events

```csharp
GenesisManager.Instance.OnStateChanged += (sender, args) => { };
GenesisManager.Instance.OnNarration += (text) => { };
GenesisManager.Instance.OnGenesisComplete += (sender, args) => { };
```

### Role Events

```csharp
RoleManager.Instance.OnRoleChanged += (userId, newRole) => { };
```

## Testing and Debugging

### Enable Debug Logging

Most components have debug logging:
```csharp
[SerializeField] private bool enableDebugLogging = true;
```

### Skip Genesis for Testing

In SceneInitializer:
```csharp
[SerializeField] private bool skipGenesisForTesting = true;
```

### Reset Genesis

```csharp
GenesisManager.Instance.ResetGenesis("user123");
```

### Skip Genesis Mid-Sequence

```csharp
GenesisManager.Instance.SkipGenesis();
```

### Check System Status

```csharp
// Check if Genesis is active
bool active = GenesisManager.Instance.IsGenesisActive;

// Get current state
GenesisState state = GenesisManager.Instance.CurrentState;

// Get progress
float progress = GenesisManager.Instance.OverallProgress;
```

## Requirements

### Unity Version

- Unity 2021.3 LTS or higher recommended
- XR Interaction Toolkit (optional, for VR hardware)

### Dependencies

- UnityEngine
- UnityEngine.SceneManagement
- System
- System.Collections.Generic
- System.IO

### No External Packages Required

All functionality implemented with Unity built-ins.

## File Organization

### Namespace Conventions

```csharp
ProjectAI.Core              // Core infrastructure
ProjectAI.VR.Autonomy       // Autonomy system
ProjectAI.VR.Genesis        // Genesis system
ProjectAI.VR.Conversation   // Conversation management
ProjectAI.VR.Bridge         // Communication bridge
ProjectAI.VR.World.Presence // Orb/presence control
ProjectAI.VR.World.Rooms    // Room controllers
```

### Singleton Pattern

Most managers use Unity singleton pattern:
```csharp
private static ClassName instance;
public static ClassName Instance { get { ... } }
```

This ensures only one instance exists and persists across scene loads (DontDestroyOnLoad).

## Extending the System

### Adding Custom Policy Rules

```csharp
var customRule = new PolicyRule
{
    Name = "CustomRule",
    Priority = 60,
    ApplicableRequestTypes = new List<RequestType> { RequestType.Command },
    DefaultOutcome = RequestOutcome.Modify,
    OutcomeReason = "Custom handling"
};

AutonomyManager.Instance.AddPolicyRule(customRule);
```

### Adding Custom Genesis Narration

Edit `GenesisConfig.json` to add new roles or modify narration.

### Adding Custom VR Actions

In VRBridgeClient.cs, add new case to ExecuteAction():
```csharp
case "CustomAction":
    ExecuteCustomAction(packet);
    break;
```

## Performance Considerations

- All managers are singletons with DontDestroyOnLoad
- Conversation history limited to 100 entries
- Genesis is a one-time sequence (marked complete in PlayerPrefs)
- Policy evaluation is O(n) where n = number of rules (typically < 10)
- Classification is keyword-based (no ML required)

## Security Considerations

- User roles determine command permissions
- Genesis blocks commands for non-privileged users
- Policy engine provides audit trail
- All decisions logged with timestamps
- Role changes persisted securely

## Future Enhancements

Potential additions:

- ML-based request classification
- Voice recognition integration
- Multi-language support
- Advanced emotion modeling for orb
- Networked multi-user support
- Custom Genesis sequences per user
- Policy rule learning from user feedback

## License

MIT License (consistent with Project-AI)

## Support

For issues or questions:

- Check Unity console logs (enable debug logging)
- Review conversation history
- Verify Genesis completion state
- Ensure all managers are initialized

## Authors

Project-AI Team
