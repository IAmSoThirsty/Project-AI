# Integration Guide - VR Module with Unity Project

## Overview

This guide explains how to integrate the Project-AI VR module into a Unity VR project.

## Prerequisites

- Unity 2021.3 LTS or higher
- Basic understanding of Unity C# scripting
- VR headset support (optional, works in editor for testing)

## Step 1: Import the VR Module

1. Copy the entire `unity/` directory into your Unity project's `Assets/` folder:

   ```
   YourProject/
   └── Assets/
       └── ProjectAI/
           ├── Scripts/
           │   ├── Core/
           │   └── VR/
           └── StreamingAssets/
               └── ProjectAI/
   ```

1. Unity will automatically compile all C# scripts.

## Step 2: Scene Setup

### Create Core GameObjects

In your VR scene hierarchy, create these GameObjects:

```
Scene Root
├── [XR Origin] (your existing VR rig)
├── ProjectAI Systems
│   ├── RoleManager (add RoleManager.cs)
│   ├── AutonomyManager (add AutonomyManager.cs)
│   ├── GenesisManager (add GenesisManager.cs)
│   ├── ConversationContextManager (add ConversationContextManager.cs)
│   ├── VRBridgeClient (add VRBridgeClient.cs)
│   └── SceneInitializer (add SceneInitializer.cs)
├── VR World
│   ├── AI Orb (GameObject with visuals)
│   │   └── PresenceController (add PresenceController.cs)
│   └── Archive Room
│       ├── Lights (multiple Light components)
│       └── LightingController (add LightingController.cs)
```

### Configure Components

#### SceneInitializer

```csharp
// In Unity Inspector:
- Skip Genesis For Testing: false (uncheck for production)
- Initialization Delay: 0.5
```

#### PresenceController

```csharp
// In Unity Inspector:
- Orb Object: Drag your AI orb GameObject here
- Formation Duration: 3.0
- Stabilization Duration: 3.0
- Lock Position During Genesis: true (checked)
- Default Position: (0, 1.5, 2)
```

#### LightingController

```csharp
// In Unity Inspector:
- Room Lights: Drag all room Light components here (array)
- Ambient Light: Drag main ambient light here
- Genesis Lighting Duration: 5.0
- Genesis Intensity Curve: AnimationCurve (0,0) to (1,1) ease in/out
- Genesis Start Color: Dark blue (0.1, 0.1, 0.2, 1)
- Genesis End Color: White (1, 1, 1, 1)
- Normal Intensity: 1.0
- Normal Color: White (1, 1, 1, 1)
```

#### VRBridgeClient

```csharp
// In Unity Inspector:
- Backend URL: "http://localhost:5000" (adjust for your Python backend)
- Reconnect Delay: 5.0
```

## Step 3: Create the AI Orb

### Basic Orb Setup

```csharp
// Create a sphere GameObject
GameObject orb = GameObject.CreatePrimitive(PrimitiveType.Sphere);
orb.name = "AI_Orb";
orb.transform.position = new Vector3(0, 1.5f, 2);
orb.transform.localScale = new Vector3(0.3f, 0.3f, 0.3f);

// Add glow material
Material glowMat = new Material(Shader.Find("Standard"));
glowMat.EnableKeyword("_EMISSION");
glowMat.SetColor("_EmissionColor", Color.cyan * 2f);
orb.GetComponent<Renderer>().material = glowMat;

// Add particle system for effects
GameObject particles = new GameObject("OrbParticles");
particles.transform.SetParent(orb.transform);
ParticleSystem ps = particles.AddComponent<ParticleSystem>();
// Configure particle system as desired
```

### Link to PresenceController

```csharp
// In PresenceController Inspector:
PresenceController presenceCtrl = orb.AddComponent<PresenceController>();
presenceCtrl.orbObject = orb; // Set reference to itself or child visual
```

## Step 4: Implement User Input

### VR Controller Input Example

```csharp
using UnityEngine;
using UnityEngine.XR;
using ProjectAI.VR.Conversation;

public class VRUserInput : MonoBehaviour
{
    private ConversationContextManager conversationManager;

    void Start()
    {
        conversationManager = ConversationContextManager.Instance;
    }

    void Update()
    {
        // Example: Press A button on right controller to send test message
        if (GetButtonDown(XRNode.RightHand, "PrimaryButton"))
        {
            SendTestMessage();
        }
    }

    private void SendTestMessage()
    {
        conversationManager.ProcessUserMessage("Turn on the lights");
    }

    private bool GetButtonDown(XRNode node, string buttonName)
    {
        InputDevice device = InputDevices.GetDeviceAtXRNode(node);
        bool buttonValue;
        if (device.TryGetFeatureValue(new InputFeatureUsage<bool>(buttonName), out buttonValue))
        {
            return buttonValue;
        }
        return false;
    }
}
```

### Voice Input Integration

```csharp
using UnityEngine;
using ProjectAI.VR.Conversation;

public class VoiceInputHandler : MonoBehaviour
{
    private ConversationContextManager conversationManager;

    void Start()
    {
        conversationManager = ConversationContextManager.Instance;
        // Initialize your voice recognition system here
    }

    // Called by voice recognition system
    public void OnVoiceCommandRecognized(string command)
    {
        conversationManager.ProcessUserMessage(command);
    }
}
```

## Step 5: Display AI Responses

### UI Text Display

```csharp
using UnityEngine;
using UnityEngine.UI;
using ProjectAI.VR.Conversation;

public class AIResponseDisplay : MonoBehaviour
{
    [SerializeField] private Text responseText;
    private ConversationContextManager conversationManager;

    void Start()
    {
        conversationManager = ConversationContextManager.Instance;
        conversationManager.OnAIResponse += DisplayResponse;
    }

    private void DisplayResponse(string response)
    {
        responseText.text = response;
        // Optionally add fade-out after delay
        CancelInvoke("ClearText");
        Invoke("ClearText", 5f);
    }

    private void ClearText()
    {
        responseText.text = "";
    }

    void OnDestroy()
    {
        if (conversationManager != null)
        {
            conversationManager.OnAIResponse -= DisplayResponse;
        }
    }
}
```

### 3D Text Display

```csharp
using UnityEngine;
using TMPro;
using ProjectAI.VR.Conversation;

public class AIResponse3DDisplay : MonoBehaviour
{
    [SerializeField] private TextMeshPro textMesh;
    [SerializeField] private Transform cameraTransform;
    
    private ConversationContextManager conversationManager;

    void Start()
    {
        conversationManager = ConversationContextManager.Instance;
        conversationManager.OnAIResponse += DisplayResponse;
    }

    void Update()
    {
        // Billboard effect - face camera
        if (cameraTransform != null)
        {
            transform.LookAt(cameraTransform);
            transform.Rotate(0, 180, 0); // Flip to face camera
        }
    }

    private void DisplayResponse(string response)
    {
        textMesh.text = response;
        StartCoroutine(FadeOut());
    }

    private System.Collections.IEnumerator FadeOut()
    {
        yield return new WaitForSeconds(5f);
        
        float duration = 1f;
        float elapsed = 0f;
        Color startColor = textMesh.color;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float alpha = Mathf.Lerp(1f, 0f, elapsed / duration);
            textMesh.color = new Color(startColor.r, startColor.g, startColor.b, alpha);
            yield return null;
        }
        
        textMesh.text = "";
        textMesh.color = startColor; // Reset alpha
    }

    void OnDestroy()
    {
        if (conversationManager != null)
        {
            conversationManager.OnAIResponse -= DisplayResponse;
        }
    }
}
```

## Step 6: Configure User Roles

### Automatic Role Assignment

```csharp
using UnityEngine;
using ProjectAI.Core;

public class UserRoleSetup : MonoBehaviour
{
    void Start()
    {
        // For testing - set owner role
        RoleManager.Instance.SetRole("testUser", "owner");
        
        // In production, get from authentication system
        // string userId = AuthenticationSystem.GetUserId();
        // string role = AuthenticationSystem.GetUserRole();
        // RoleManager.Instance.SetRole(userId, role);
    }
}
```

### Login UI Integration

```csharp
using UnityEngine;
using UnityEngine.UI;
using ProjectAI.Core;

public class LoginUI : MonoBehaviour
{
    [SerializeField] private InputField userIdInput;
    [SerializeField] private Dropdown roleDropdown;
    [SerializeField] private Button loginButton;

    void Start()
    {
        loginButton.onClick.AddListener(OnLogin);
    }

    private void OnLogin()
    {
        string userId = userIdInput.text;
        string role = roleDropdown.options[roleDropdown.value].text.ToLower();
        
        RoleManager.Instance.SetRole(userId, role);
        
        // Close login UI and start VR experience
        gameObject.SetActive(false);
    }
}
```

## Step 7: Genesis Event Handling

### Listen to Genesis Events

```csharp
using UnityEngine;
using ProjectAI.VR.Genesis;

public class GenesisEventListener : MonoBehaviour
{
    void Start()
    {
        var genesisManager = GenesisManager.Instance;
        
        genesisManager.OnStateChanged += OnGenesisStateChanged;
        genesisManager.OnNarration += OnGenesisNarration;
        genesisManager.OnGenesisComplete += OnGenesisComplete;
    }

    private void OnGenesisStateChanged(object sender, GenesisStateChangedEventArgs args)
    {
        Debug.Log($"Genesis state: {args.PreviousState} -> {args.NewState} ({args.Progress:P0})");
        
        // Update UI, play sounds, etc.
        switch (args.NewState)
        {
            case GenesisState.OrbForming:
                // Play formation sound
                break;
            case GenesisState.SubsystemsIgniting:
                // Play ignition sound
                break;
            case GenesisState.RoomAwakening:
                // Play ambient awakening sound
                break;
        }
    }

    private void OnGenesisNarration(string narration)
    {
        Debug.Log($"Genesis narration: {narration}");
        // Display in UI or play as voice
    }

    private void OnGenesisComplete(object sender, System.EventArgs e)
    {
        Debug.Log("Genesis complete - enabling full interactions");
        // Enable all VR interaction systems
    }

    void OnDestroy()
    {
        var genesisManager = GenesisManager.Instance;
        if (genesisManager != null)
        {
            genesisManager.OnStateChanged -= OnGenesisStateChanged;
            genesisManager.OnNarration -= OnGenesisNarration;
            genesisManager.OnGenesisComplete -= OnGenesisComplete;
        }
    }
}
```

## Step 8: Python Backend Integration

### Backend Setup

Ensure your Python backend (from main Project-AI) is running:

```bash
cd /path/to/Project-AI
python -m src.app.main
```

### VRBridgeClient Configuration

The VRBridgeClient will attempt to connect to the Python backend. You can extend it to handle actual HTTP requests:

```csharp
// In VRBridgeClient.cs, implement actual networking:
private IEnumerator SendActionToBackend(VRActionPacket packet)
{
    string json = JsonUtility.ToJson(packet);
    byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
    
    UnityWebRequest request = new UnityWebRequest(backendUrl + "/vr/action", "POST");
    request.uploadHandler = new UploadHandlerRaw(bodyRaw);
    request.downloadHandler = new DownloadHandlerBuffer();
    request.SetRequestHeader("Content-Type", "application/json");
    
    yield return request.SendWebRequest();
    
    if (request.result == UnityWebRequest.Result.Success)
    {
        Debug.Log("Action sent successfully");
    }
    else
    {
        Debug.LogError($"Failed to send action: {request.error}");
    }
}
```

## Step 9: Testing

### Editor Testing

1. Open your scene in Unity Editor
1. Press Play
1. Check Console for initialization messages
1. If first-time user, Genesis should start automatically
1. Use test input methods to send commands

### Genesis Testing

```csharp
// In Unity Console or custom debug UI:
// Reset Genesis for current user:
GenesisManager.Instance.ResetGenesis(RoleManager.Instance.CurrentUserId);

// Skip Genesis immediately:
GenesisManager.Instance.SkipGenesis();

// Check status:
Debug.Log($"Genesis Active: {GenesisManager.Instance.IsGenesisActive}");
Debug.Log($"Genesis Progress: {GenesisManager.Instance.OverallProgress:P0}");
```

### Autonomy Testing

```csharp
// Test different request types:
var context = new RequestContext 
{ 
    UserRole = "owner", 
    UserId = "test", 
    IsGenesisActive = false 
};

// Command
AutonomyManager.Instance.ProcessRequest("Turn on the lights", context);

// Request
AutonomyManager.Instance.ProcessRequest("Could you please dim the lights?", context);

// Suggestion  
AutonomyManager.Instance.ProcessRequest("Maybe we could change the color", context);

// Casual
AutonomyManager.Instance.ProcessRequest("It's bright in here", context);
```

## Step 10: Advanced Customization

### Custom Policy Rules

```csharp
// Add at runtime:
var customRule = new PolicyRule
{
    Name = "NightModeRestriction",
    Description = "Restrict lighting changes at night",
    Priority = 75,
    ApplicableRequestTypes = new List<RequestType> { RequestType.Command },
    DefaultOutcome = RequestOutcome.Decline,
    OutcomeReason = "Lighting changes disabled during night mode",
    RequireConfirmation = false
};

// Check time condition in your code, then:
if (IsNightMode())
{
    AutonomyManager.Instance.AddPolicyRule(customRule);
}
```

### Custom Genesis Narration

Edit `StreamingAssets/ProjectAI/GenesisConfig.json`:

```json
{
  "RoleConfigs": {
    "vip": {
      "RoleName": "vip",
      "AllowInterruption": true,
      "NarrationLines": [
        "Welcome, esteemed guest...",
        "Exclusive systems activating...",
        "Premium features online...",
        "VIP environment ready...",
        "At your service, honored guest."
      ]
    }
  }
}
```

### Custom VR Actions

Extend VRBridgeClient.cs:

```csharp
case "CustomEffect":
    ExecuteCustomEffect(packet);
    break;

private void ExecuteCustomEffect(VRActionPacket packet)
{
    // Your custom VR effect logic
    string effectType = packet.Parameters["EffectType"] as string;
    float intensity = (float)packet.Parameters["Intensity"];
    
    // Execute effect...
}
```

## Troubleshooting

### Common Issues

1. **Genesis doesn't start**
   - Check PlayerPrefs: `PlayerPrefs.DeleteAll()` to reset
   - Verify SceneInitializer is active
   - Check console for initialization errors

1. **Commands not working**
   - Verify RoleManager has correct role set
   - Check if Genesis is active (blocks commands)
   - Enable debug logging in components

1. **Lighting not animating**
   - Ensure Light components are assigned in LightingController
   - Check that lights exist in scene
   - Verify Genesis RoomAwakening state is reached

1. **Orb not visible**
   - Check PresenceController.orbObject assignment
   - Verify orb GameObject is active
   - Check camera can see orb position

## Performance Tips

- Use object pooling for VR action packets
- Limit conversation history size (already set to 100)
- Disable debug logging in production
- Use Level of Detail (LOD) for orb visuals
- Batch lighting updates when possible

## Next Steps

- Integrate with your VR interaction system
- Add voice recognition
- Implement Python backend endpoints
- Create custom animations for Genesis
- Add audio feedback for events
- Implement orb emotion visuals
- Create admin UI for policy management

## Support Resources

- Unity Documentation: https://docs.unity3d.com/
- XR Interaction Toolkit: https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest
- Project-AI Repository: https://github.com/IAmSoThirsty/Project-AI

---

**Version:** 1.0  
**Last Updated:** 2026-01-23
