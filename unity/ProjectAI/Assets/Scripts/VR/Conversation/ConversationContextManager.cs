using System.Collections.Generic;
using UnityEngine;
using ProjectAI.VR.Autonomy;
using ProjectAI.VR.Bridge;
using ProjectAI.VR.Genesis;
using ProjectAI.Core;

namespace ProjectAI.VR.Conversation
{
    /// <summary>
    /// Manages conversation context and integrates with autonomy system
    /// Routes user commands through policy evaluation and handles Genesis restrictions
    /// </summary>
    public class ConversationContextManager : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private bool enableDebugLogging = true;

        private List<string> conversationHistory;
        private AutonomyManager autonomyManager;
        private GenesisManager genesisManager;
        private VRBridgeClient bridgeClient;
        private RoleManager roleManager;

        // Events
        public event System.Action<string> OnUserMessage;
        public event System.Action<string> OnAIResponse;
        public event System.Action<string> OnCommandDeclined;

        // Singleton
        private static ConversationContextManager instance;
        public static ConversationContextManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<ConversationContextManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("ConversationContextManager");
                        instance = go.AddComponent<ConversationContextManager>();
                    }
                }
                return instance;
            }
        }

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
            conversationHistory = new List<string>();
            
            // Get references to other managers
            autonomyManager = AutonomyManager.Instance;
            genesisManager = GenesisManager.Instance;
            bridgeClient = VRBridgeClient.Instance;
            roleManager = RoleManager.Instance;

            // Subscribe to autonomy events
            autonomyManager.OnRequestDeclined += HandleRequestDeclined;
            autonomyManager.OnActionExecuted += HandleActionExecuted;

            // Subscribe to Genesis events
            genesisManager.OnNarration += HandleGenesisNarration;

            if (enableDebugLogging)
                Debug.Log("ConversationContextManager: Initialized");
        }

        /// <summary>
        /// Process a user message through the conversation and autonomy pipeline
        /// </summary>
        public void ProcessUserMessage(string message)
        {
            if (string.IsNullOrWhiteSpace(message))
            {
                Debug.LogWarning("ConversationContextManager: Received empty message");
                return;
            }

            if (enableDebugLogging)
                Debug.Log($"ConversationContextManager: Processing message: '{message}'");

            // Notify listeners
            OnUserMessage?.Invoke(message);

            // Add to conversation history
            AddToHistory($"User: {message}");

            // Check if Genesis is active
            if (genesisManager.IsGenesisActive)
            {
                HandleMessageDuringGenesis(message);
                return;
            }

            // Build request context
            RequestContext context = BuildRequestContext();

            // Process through autonomy system
            RequestOutcomeResult result = autonomyManager.ProcessRequest(message, context);

            // Handle the result
            HandleAutonomyResult(message, result);
        }

        /// <summary>
        /// Handle messages received during Genesis event
        /// </summary>
        private void HandleMessageDuringGenesis(string message)
        {
            string userRole = roleManager.CurrentRole;
            
            // Check if user can interrupt Genesis
            if (genesisManager.CanInterruptGenesis(userRole))
            {
                if (enableDebugLogging)
                    Debug.Log("ConversationContextManager: Privileged user message during Genesis - allowing");
                
                // Process normally but with Genesis context
                RequestContext context = BuildRequestContext();
                RequestOutcomeResult result = autonomyManager.ProcessRequest(message, context);
                HandleAutonomyResult(message, result);
            }
            else
            {
                // Block command during Genesis
                string response = "Genesis sequence in progress. Please wait for initialization to complete.";
                SendAIResponse(response);
                OnCommandDeclined?.Invoke(response);
                
                if (enableDebugLogging)
                    Debug.Log("ConversationContextManager: Command blocked during Genesis");
            }
        }

        /// <summary>
        /// Build request context from current state
        /// </summary>
        private RequestContext BuildRequestContext()
        {
            var context = new RequestContext
            {
                UserRole = roleManager.CurrentRole,
                UserId = roleManager.CurrentUserId,
                Environment = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,
                IsFirstConnection = genesisManager.ShouldTriggerGenesis(roleManager.CurrentUserId),
                IsGenesisActive = genesisManager.IsGenesisActive,
                InteractionCount = conversationHistory.Count
            };

            // Add additional metadata
            context.Metadata["VRActive"] = true;
            context.Metadata["CurrentScene"] = context.Environment;

            return context;
        }

        /// <summary>
        /// Handle the result from autonomy system
        /// </summary>
        private void HandleAutonomyResult(string originalMessage, RequestOutcomeResult result)
        {
            string response = string.Empty;

            switch (result.Decision)
            {
                case RequestOutcome.Comply:
                    response = $"Understood. {result.Reason}";
                    // Action is executed by AutonomyManager
                    break;

                case RequestOutcome.Modify:
                    if (result.RequiresUserConfirmation)
                    {
                        response = $"I'd like to modify that request: {result.Reason}. Do you approve?";
                    }
                    else
                    {
                        response = $"I'll handle that with some adjustments. {result.Reason}";
                    }
                    break;

                case RequestOutcome.Decline:
                    response = $"I cannot do that. {result.Reason}";
                    OnCommandDeclined?.Invoke(response);
                    break;

                case RequestOutcome.Ignore:
                    response = GenerateCasualResponse(originalMessage);
                    break;
            }

            SendAIResponse(response);
        }

        /// <summary>
        /// Generate a casual conversational response
        /// </summary>
        private string GenerateCasualResponse(string message)
        {
            // Simple casual response generation
            // In production, this would use AI backend
            string[] responses = 
            {
                "I understand what you're saying.",
                "Interesting observation.",
                "I see.",
                "That's noteworthy.",
                "Acknowledged."
            };

            return responses[Random.Range(0, responses.Length)];
        }

        /// <summary>
        /// Send an AI response
        /// </summary>
        private void SendAIResponse(string response)
        {
            if (string.IsNullOrWhiteSpace(response))
                return;

            AddToHistory($"AI: {response}");
            OnAIResponse?.Invoke(response);

            if (enableDebugLogging)
                Debug.Log($"ConversationContextManager: AI Response: '{response}'");

            // Send to VR display
            var actionPacket = new VRActionPacket
            {
                ActionType = "DisplayText",
                Parameters = new Dictionary<string, object>
                {
                    { "Text", response },
                    { "Source", "AI" }
                }
            };
            bridgeClient.SendAction(actionPacket);
        }

        /// <summary>
        /// Handle Genesis narration
        /// </summary>
        private void HandleGenesisNarration(string narration)
        {
            if (enableDebugLogging)
                Debug.Log($"ConversationContextManager: Genesis narration: '{narration}'");

            SendAIResponse(narration);
        }

        /// <summary>
        /// Handle declined requests
        /// </summary>
        private void HandleRequestDeclined(string reason)
        {
            if (enableDebugLogging)
                Debug.Log($"ConversationContextManager: Request declined: {reason}");
        }

        /// <summary>
        /// Handle executed actions
        /// </summary>
        private void HandleActionExecuted(string intent, RequestOutcome outcome)
        {
            if (enableDebugLogging)
                Debug.Log($"ConversationContextManager: Action executed - Intent: '{intent}', Outcome: {outcome}");
        }

        /// <summary>
        /// Add entry to conversation history
        /// </summary>
        private void AddToHistory(string entry)
        {
            conversationHistory.Add($"[{System.DateTime.UtcNow:HH:mm:ss}] {entry}");

            // Limit history size
            if (conversationHistory.Count > 100)
            {
                conversationHistory.RemoveAt(0);
            }
        }

        /// <summary>
        /// Get conversation history
        /// </summary>
        public List<string> GetHistory()
        {
            return new List<string>(conversationHistory);
        }

        /// <summary>
        /// Clear conversation history
        /// </summary>
        public void ClearHistory()
        {
            conversationHistory.Clear();
            if (enableDebugLogging)
                Debug.Log("ConversationContextManager: History cleared");
        }

        private void OnDestroy()
        {
            // Unsubscribe from events
            if (autonomyManager != null)
            {
                autonomyManager.OnRequestDeclined -= HandleRequestDeclined;
                autonomyManager.OnActionExecuted -= HandleActionExecuted;
            }

            if (genesisManager != null)
            {
                genesisManager.OnNarration -= HandleGenesisNarration;
            }
        }
    }
}
