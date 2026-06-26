using System;
using System.Collections.Generic;
using UnityEngine;
using ProjectAI.VR.Autonomy;

namespace ProjectAI.VR.Bridge
{
    /// <summary>
    /// Action packet sent to VR system with autonomy outcome tagging
    /// </summary>
    [Serializable]
    public class VRActionPacket
    {
        public string ActionId { get; set; }
        public string ActionType { get; set; }           // e.g., "MoveOrb", "ChangeLighting", "DisplayText"
        public Dictionary<string, object> Parameters { get; set; }
        public RequestOutcome Outcome { get; set; }       // How request was handled
        public string Intent { get; set; }               // Original user intent
        public DateTime Timestamp { get; set; }

        public VRActionPacket()
        {
            ActionId = Guid.NewGuid().ToString();
            Parameters = new Dictionary<string, object>();
            Timestamp = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Context packet for VR state information
    /// </summary>
    [Serializable]
    public class VRContextPacket
    {
        public string UserId { get; set; }
        public string UserRole { get; set; }
        public string CurrentScene { get; set; }
        public bool IsGenesisActive { get; set; }
        public Dictionary<string, object> StateData { get; set; }

        public VRContextPacket()
        {
            StateData = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Bridge client for communicating between Unity VR and AI backend
    /// Handles action execution and feedback with autonomy tagging
    /// </summary>
    public class VRBridgeClient : MonoBehaviour
    {
        [Header("Connection Settings")]
        [SerializeField] private string backendUrl = "http://localhost:5000";
        [SerializeField] private float reconnectDelay = 5.0f;

        private bool isConnected = false;
        private Queue<VRActionPacket> actionQueue;

        // Events
        public event Action<VRActionPacket> OnActionReceived;
        public event Action<VRContextPacket> OnContextUpdate;
        public event Action<bool> OnConnectionStatusChanged;

        // Singleton
        private static VRBridgeClient instance;
        public static VRBridgeClient Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<VRBridgeClient>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("VRBridgeClient");
                        instance = go.AddComponent<VRBridgeClient>();
                    }
                }
                return instance;
            }
        }

        public bool IsConnected => isConnected;

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            instance = this;
            DontDestroyOnLoad(gameObject);

            Initialize();
        }

        private void Initialize()
        {
            actionQueue = new Queue<VRActionPacket>();
            Debug.Log($"VRBridgeClient: Initialized (Backend URL: {backendUrl})");
            
            // Start connection attempt
            AttemptConnection();
        }

        /// <summary>
        /// Attempt to connect to backend
        /// </summary>
        private void AttemptConnection()
        {
            // This would implement actual network connection logic
            // For now, simulate connection
            isConnected = true;
            Debug.Log("VRBridgeClient: Connected to backend");
            OnConnectionStatusChanged?.Invoke(true);
        }

        /// <summary>
        /// Send an action packet to VR system
        /// </summary>
        public void SendAction(VRActionPacket packet)
        {
            if (packet == null)
            {
                Debug.LogWarning("VRBridgeClient: Attempted to send null packet");
                return;
            }

            Debug.Log($"VRBridgeClient: Sending action '{packet.ActionType}' (Outcome: {packet.Outcome})");

            // Add to queue for processing
            actionQueue.Enqueue(packet);

            // Process immediately if connected
            if (isConnected)
            {
                ProcessAction(packet);
            }
        }

        /// <summary>
        /// Process an action packet
        /// </summary>
        private void ProcessAction(VRActionPacket packet)
        {
            Debug.Log($"VRBridgeClient: Processing action {packet.ActionId} - Type: {packet.ActionType}");

            // Notify listeners
            OnActionReceived?.Invoke(packet);

            // Execute action based on type
            ExecuteAction(packet);
        }

        /// <summary>
        /// Execute a specific action in VR
        /// </summary>
        private void ExecuteAction(VRActionPacket packet)
        {
            switch (packet.ActionType)
            {
                case "MoveOrb":
                    ExecuteMoveOrb(packet);
                    break;

                case "ChangeLighting":
                    ExecuteChangeLighting(packet);
                    break;

                case "DisplayText":
                    ExecuteDisplayText(packet);
                    break;

                case "PlayAnimation":
                    ExecutePlayAnimation(packet);
                    break;

                case "UpdateEmotion":
                    ExecuteUpdateEmotion(packet);
                    break;

                default:
                    Debug.LogWarning($"VRBridgeClient: Unknown action type '{packet.ActionType}'");
                    break;
            }
        }

        private void ExecuteMoveOrb(VRActionPacket packet)
        {
            Debug.Log("VRBridgeClient: Executing MoveOrb action");
            // Integration point: PresenceController.MoveOrb(parameters)
        }

        private void ExecuteChangeLighting(VRActionPacket packet)
        {
            Debug.Log("VRBridgeClient: Executing ChangeLighting action");
            // Integration point: LightingController.SetLighting(parameters)
        }

        private void ExecuteDisplayText(VRActionPacket packet)
        {
            Debug.Log("VRBridgeClient: Executing DisplayText action");
            // Integration point: UIController.ShowText(parameters)
        }

        private void ExecutePlayAnimation(VRActionPacket packet)
        {
            Debug.Log("VRBridgeClient: Executing PlayAnimation action");
            // Integration point: AnimationController.PlayAnimation(parameters)
        }

        private void ExecuteUpdateEmotion(VRActionPacket packet)
        {
            Debug.Log("VRBridgeClient: Executing UpdateEmotion action");
            // Integration point: PresenceController.SetEmotion(parameters)
        }

        /// <summary>
        /// Send context update to backend
        /// </summary>
        public void SendContextUpdate(VRContextPacket context)
        {
            if (context == null)
            {
                Debug.LogWarning("VRBridgeClient: Attempted to send null context");
                return;
            }

            Debug.Log($"VRBridgeClient: Sending context update for user '{context.UserId}'");
            
            // Notify listeners
            OnContextUpdate?.Invoke(context);

            // Would send to backend here
        }

        /// <summary>
        /// Create action packet from autonomy result
        /// </summary>
        public VRActionPacket CreateActionFromAutonomy(string actionType, RequestOutcomeResult autonomyResult, Dictionary<string, object> parameters = null)
        {
            var packet = new VRActionPacket
            {
                ActionType = actionType,
                Outcome = autonomyResult.Decision,
                Intent = autonomyResult.ClassifiedType.ToString(),
                Parameters = parameters ?? new Dictionary<string, object>()
            };

            // Add autonomy metadata
            packet.Parameters["AutonomyConfidence"] = autonomyResult.ConfidenceScore;
            packet.Parameters["AutonomyReason"] = autonomyResult.Reason;

            return packet;
        }

        /// <summary>
        /// Get current VR context
        /// </summary>
        public VRContextPacket GetCurrentContext()
        {
            var context = new VRContextPacket
            {
                UserId = ProjectAI.Core.RoleManager.Instance.CurrentUserId,
                UserRole = ProjectAI.Core.RoleManager.Instance.CurrentRole,
                CurrentScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,
                IsGenesisActive = ProjectAI.VR.Genesis.GenesisManager.Instance.IsGenesisActive
            };

            return context;
        }

        private void Update()
        {
            // Process any queued actions
            if (isConnected && actionQueue.Count > 0)
            {
                // Could implement batching or rate limiting here
            }
        }

        private void OnDestroy()
        {
            isConnected = false;
            OnConnectionStatusChanged?.Invoke(false);
        }
    }
}
