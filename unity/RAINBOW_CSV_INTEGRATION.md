# Rainbow CSV Integration for Unity

## Overview

This guide shows how to connect Unity to the **Rainbow CSV Visualizer** backend to display data-driven VR visuals in real-time.

## Architecture

```
Python Script → HTTP POST → Backend API → Unity Client (Poll)
(CSV Reader)    (JSON)      (/vr/command)   (VRBridgeClient)
```

## Step 1: Start the Backend

Ensure the API server is running:

```bash
cd c:\UserQuencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI
python scripts/start_api.py
```

The API will start on `http://localhost:8001` with the `/vr/command` endpoint.

## Step 2: Update VRBridgeClient.cs

Modify `unity/ProjectAI/Scripts/VR/Bridge/VRBridgeClient.cs` to poll the backend:

```csharp
using UnityEngine.Networking;
using System.Collections;

[Header("Polling Settings")]
[SerializeField] private float pollInterval = 0.5f;  // Poll every 500ms
private float lastPollTime = 0;

private void Update()
{
    if (Time.time - lastPollTime > pollInterval && isConnected)
    {
        StartCoroutine(PollCommands());
        lastPollTime = Time.time;
    }
}

private IEnumerator PollCommands()
{
    string url = $"{backendUrl}/vr/commands?since={lastPollTime}";
    
    using (UnityWebRequest request = UnityWebRequest.Get(url))
    {
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            // Parse JSON array of commands
            var commands = JsonUtility.FromJson<VRCommandList>(request.downloadHandler.text);
            
            foreach (var cmd in commands.commands)
            {
                ProcessCommand(cmd);
            }
        }
    }
}

private void ProcessCommand(VRCommand cmd)
{
    // Create action packet from command
    var packet = new VRActionPacket
    {
        ActionType = cmd.type,
        Parameters = cmd.params  // You'll need to deserialize this properly
    };
    
    OnActionReceived?.Invoke(packet);
    ExecuteAction(packet);
}

[System.Serializable]
public class VRCommand
{
    public string type;
    public Dictionary<string, object> @params;
    public float timestamp;
}

[System.Serializable]
public class VRCommandList
{
    public List<VRCommand> commands;
}
```

## Step 3: Run the Rainbow Visualizer

In a separate terminal:

```bash
python scripts/demos/rainbow_csv_visualizer.py
```

This will send commands like:

- `ChangeLighting` with username-based colors
- `SpawnObject` for data orbs
- `DisplayText` for activation messages

## Step 4: See It in Unity

Press **Play** in Unity Editor. You should see:

1. Console logs showing commands received
2. Lights changing color based on CSV data
3. Orbs spawning for each user activation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No commands received | Check backend is running on port 8001 |
| Unity errors | Ensure `UnityEngine.Networking` is imported |
| Commands not executing | Check `ExecuteAction()` logic in `VRBridgeClient.cs` |

## Next Steps

- Implement actual lighting control in `ExecuteChangeLighting()`
- Create orb prefab for `ExecuteSpawnObject()`
- Add UI text display for `ExecuteDisplayText()`
