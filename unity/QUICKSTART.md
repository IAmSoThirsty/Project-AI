# Quick Start Guide - VR Module

## 5-Minute Setup

### 1. Import Scripts (2 minutes)

Copy the `unity/ProjectAI/` folder into your Unity project's `Assets/` folder:

```
YourUnityProject/Assets/ProjectAI/
```

Unity will automatically compile all C# scripts.

### 2. Create Core GameObjects (2 minutes)

In your VR scene, create an empty GameObject called "ProjectAI Systems" and add these components:

1. **RoleManager** component
1. **AutonomyManager** component  
1. **GenesisManager** component
1. **ConversationContextManager** component
1. **VRBridgeClient** component
1. **SceneInitializer** component

All managers are singletons and will persist across scene loads.

### 3. Test in Editor (1 minute)

Press Play in Unity Editor. You should see console messages:

```
RoleManager: Initialized with userId='anonymous', role='guest'
PolicyEngine: Loaded 7 default rules
GenesisManager: Initialized
ConversationContextManager: Initialized
VRBridgeClient: Initialized (Backend URL: http://localhost:5000)
SceneInitializer: Beginning scene initialization
SceneInitializer: First-time user detected - triggering Genesis for 'guest'
GenesisManager: Starting Genesis for role 'guest'
GenesisManager: Transitioning to OrbForming (duration: 3s)
```

✅ **You're done!** The system is running.

## Basic Usage

### Send a User Command

```csharp
using ProjectAI.VR.Conversation;

// Anywhere in your code:
ConversationContextManager.Instance.ProcessUserMessage("Turn on the lights");
```

The system will:

1. Classify the request (Command, Request, Suggestion, or Casual)
1. Evaluate against policies
1. Execute, modify, decline, or ignore based on user role
1. Log the decision
1. Trigger appropriate VR actions

### Check Genesis Status

```csharp
using ProjectAI.VR.Genesis;

if (GenesisManager.Instance.IsGenesisActive)
{
    Debug.Log("Genesis in progress...");
    float progress = GenesisManager.Instance.OverallProgress;
    Debug.Log($"Progress: {progress:P0}");
}
```

### Set User Role

```csharp
using ProjectAI.Core;

// Set user as owner (full permissions)
RoleManager.Instance.SetRole("user123", "owner");

// Set as guest (limited permissions)
RoleManager.Instance.SetRole("user456", "guest");
```

### Listen to Events

```csharp
// AI responses
ConversationContextManager.Instance.OnAIResponse += (response) => 
{
    Debug.Log($"AI said: {response}");
};

// Genesis completion
GenesisManager.Instance.OnGenesisComplete += (sender, args) => 
{
    Debug.Log("Genesis complete!");
};

// Autonomy decisions
AutonomyManager.Instance.OnActionExecuted += (intent, outcome) => 
{
    Debug.Log($"Action: {intent}, Outcome: {outcome}");
};
```

## Key Concepts

### User Autonomy System

Classifies and evaluates user input based on policies:

- **Command**: "Turn on the lights" → Usually comply (if authorized)
- **Request**: "Could you turn on the lights?" → Usually comply
- **Suggestion**: "Maybe we could brighten things" → May modify
- **Casual**: "It's dark in here" → Acknowledge only

Policies consider:

- User role (owner/admin/guest)
- Context (Genesis active?)
- Request type
- Priority rules

### Genesis Event

First-time VR experience (one-time per user):

1. **OrbForming** (3s) - AI orb materializes
1. **SubsystemsIgniting** (4s) - Systems come online
1. **PresenceStabilizing** (3s) - AI presence solidifies
1. **RoomAwakening** (5s) - Environment lights up
1. **Acknowledgement** (4s) - AI greets user
1. **Complete** - Normal operation begins

Total duration: ~19 seconds

Commands are blocked during Genesis (except for privileged users).

### Managers (Singletons)

All managers use the singleton pattern:

```csharp
RoleManager.Instance          // User roles and permissions
AutonomyManager.Instance      // Request processing
GenesisManager.Instance       // Genesis event
ConversationContextManager.Instance  // Conversation flow
VRBridgeClient.Instance      // VR communication
```

They persist across scene loads (DontDestroyOnLoad).

## Configuration

### Genesis Config

Edit `StreamingAssets/ProjectAI/GenesisConfig.json`:

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
      "AllowInterruption": true,
      "NarrationLines": [...]
    }
  }
}
```

### Skip Genesis (Testing)

In Unity Editor, add SceneInitializer component and check:

- ☑ Skip Genesis For Testing

Or reset programmatically:
```csharp
GenesisManager.Instance.ResetGenesis("userId");
```

## Testing Commands

Try these in your VR scene:

```csharp
var conv = ConversationContextManager.Instance;

// Different request types
conv.ProcessUserMessage("Turn on the lights");           // Command
conv.ProcessUserMessage("Could you dim the lights?");    // Request
conv.ProcessUserMessage("Maybe we could change color");  // Suggestion
conv.ProcessUserMessage("It's bright in here");          // Casual

// Check what happens
conv.OnAIResponse += (response) => Debug.Log(response);
```

Expected outcomes:

- **Owner role**: Most commands comply
- **Guest role**: Commands need confirmation
- **During Genesis**: Commands blocked

## Common Patterns

### User Login

```csharp
void OnUserLogin(string userId, string userRole)
{
    RoleManager.Instance.SetRole(userId, userRole);
    
    // Check if Genesis needed
    if (GenesisManager.Instance.ShouldTriggerGenesis(userId))
    {
        GenesisManager.Instance.StartGenesis(userRole);
    }
}
```

### VR Controller Input

```csharp
void Update()
{
    // When button pressed
    if (Input.GetButtonDown("Fire1"))
    {
        string command = GetVoiceInput(); // Your voice recognition
        ConversationContextManager.Instance.ProcessUserMessage(command);
    }
}
```

### Display AI Response

```csharp
void Start()
{
    ConversationContextManager.Instance.OnAIResponse += DisplayResponse;
}

void DisplayResponse(string text)
{
    // Show in UI
    responseText.text = text;
}
```

## Architecture Overview

```
User Input
    ↓
ConversationContextManager
    ↓
AutonomyManager
    ├─→ RequestClassifier (classify input)
    └─→ PolicyEngine (evaluate rules)
        ↓
    Decision (Comply/Decline/Modify/Ignore)
        ↓
VRBridgeClient (execute actions)
    ↓
VR Scene Updates
```

Genesis runs independently and blocks commands until complete.

## Next Steps

1. **Add Visuals**: Create AI orb GameObject and link to PresenceController
1. **Add Lighting**: Configure LightingController with room lights
1. **Add Input**: Implement VR controller or voice input
1. **Add Output**: Display AI responses in 3D or UI
1. **Connect Backend**: Set up Python backend for AI intelligence
1. **Customize Policies**: Add custom rules for your use case
1. **Enhance Genesis**: Add animations, sounds, and effects

## Example: Complete Setup Script

```csharp
using UnityEngine;
using ProjectAI.Core;
using ProjectAI.VR.Conversation;
using ProjectAI.VR.Genesis;

public class QuickSetup : MonoBehaviour
{
    void Start()
    {
        // 1. Set user role
        RoleManager.Instance.SetRole("demo_user", "owner");
        
        // 2. Subscribe to events
        ConversationContextManager.Instance.OnAIResponse += OnResponse;
        GenesisManager.Instance.OnGenesisComplete += OnGenesisComplete;
        
        // 3. Test message
        Invoke("SendTestMessage", 2f);
    }
    
    void SendTestMessage()
    {
        if (!GenesisManager.Instance.IsGenesisActive)
        {
            ConversationContextManager.Instance
                .ProcessUserMessage("Hello, can you turn on the lights?");
        }
    }
    
    void OnResponse(string response)
    {
        Debug.Log($"AI Response: {response}");
    }
    
    void OnGenesisComplete(object sender, System.EventArgs e)
    {
        Debug.Log("Genesis complete - ready for interaction!");
    }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No console output | Check all managers are on GameObjects in scene |
| Genesis doesn't run | Check `ShouldTriggerGenesis()` - may need to reset PlayerPrefs |
| Commands ignored | Check user role and Genesis status |
| Errors on Play | Ensure all scripts are in correct folders |

## Resources

- **Full README**: `unity/README.md`
- **Integration Guide**: `unity/INTEGRATION_GUIDE.md`
- **Test Script**: `unity/ProjectAI/Tests/VRModuleTests.cs`
- **Config**: `unity/StreamingAssets/ProjectAI/GenesisConfig.json`

## Support

For detailed documentation, see the full README.md file.

For issues, check Unity console logs with debug logging enabled:
```csharp
// On any manager with the option:
enableDebugLogging = true;
```

---

**Quick Start Version:** 1.0  
**Ready to code!** 🚀
