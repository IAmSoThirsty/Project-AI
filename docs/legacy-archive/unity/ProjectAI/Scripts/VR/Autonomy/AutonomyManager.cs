using System;
using UnityEngine;

namespace ProjectAI.VR.Autonomy
{
    /// <summary>
    /// Main orchestrator for the AI autonomy system
    /// Coordinates request classification, policy evaluation, and outcome execution
    /// </summary>
    public class AutonomyManager : MonoBehaviour
    {
        private PolicyEngine policyEngine;
        private RequestClassifier classifier;

        // Events for notifying other systems
        public event Action<UserRequest, RequestOutcomeResult> OnRequestProcessed;
        public event Action<string, RequestOutcome> OnActionExecuted;
        public event Action<string> OnRequestDeclined;

        private static AutonomyManager instance;
        public static AutonomyManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<AutonomyManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("AutonomyManager");
                        instance = go.AddComponent<AutonomyManager>();
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

        /// <summary>
        /// Initialize the autonomy system
        /// </summary>
        private void Initialize()
        {
            policyEngine = new PolicyEngine();
            classifier = new RequestClassifier();
            Debug.Log("AutonomyManager: Initialized");
        }

        /// <summary>
        /// Process a user request through the autonomy pipeline
        /// </summary>
        public RequestOutcomeResult ProcessRequest(string requestText, RequestContext context)
        {
            if (string.IsNullOrWhiteSpace(requestText))
            {
                Debug.LogWarning("AutonomyManager: Received empty request");
                return null;
            }

            // Create request object
            var request = new UserRequest(requestText, context);
            
            Debug.Log($"AutonomyManager: Processing request from {context.UserRole}: '{requestText}'");

            // Evaluate through policy engine
            var result = policyEngine.Evaluate(request);

            // Log the decision
            LogDecision(request, result);

            // Notify listeners
            OnRequestProcessed?.Invoke(request, result);

            // Handle the outcome
            HandleOutcome(request, result);

            return result;
        }

        /// <summary>
        /// Handle the request outcome
        /// </summary>
        private void HandleOutcome(UserRequest request, RequestOutcomeResult result)
        {
            switch (result.Decision)
            {
                case RequestOutcome.Comply:
                    ExecuteRequest(request, result);
                    break;

                case RequestOutcome.Modify:
                    ExecuteModifiedRequest(request, result);
                    break;

                case RequestOutcome.Decline:
                    DeclineRequest(request, result);
                    break;

                case RequestOutcome.Ignore:
                    AcknowledgeRequest(request, result);
                    break;
            }
        }

        /// <summary>
        /// Execute a complied request
        /// </summary>
        private void ExecuteRequest(UserRequest request, RequestOutcomeResult result)
        {
            Debug.Log($"AutonomyManager: COMPLY - Executing: {request.RawText}");
            
            // Extract intent for execution
            string intent = classifier.ExtractIntent(request.RawText);
            
            // Notify action execution
            OnActionExecuted?.Invoke(intent, RequestOutcome.Comply);

            // Here would be integration with VRBridgeClient to send action packets
            // For now, just log
            Debug.Log($"AutonomyManager: Action dispatched - Intent: '{intent}'");
        }

        /// <summary>
        /// Execute a modified version of the request
        /// </summary>
        private void ExecuteModifiedRequest(UserRequest request, RequestOutcomeResult result)
        {
            Debug.Log($"AutonomyManager: MODIFY - Original: {request.RawText}");
            
            if (result.RequiresUserConfirmation)
            {
                Debug.Log($"AutonomyManager: Requesting user confirmation for: {request.RawText}");
                // Here would be integration to show confirmation dialog
            }
            else
            {
                string modifiedIntent = classifier.ExtractIntent(result.ModifiedRequest ?? request.RawText);
                OnActionExecuted?.Invoke(modifiedIntent, RequestOutcome.Modify);
                Debug.Log($"AutonomyManager: Modified action dispatched - Intent: '{modifiedIntent}'");
            }
        }

        /// <summary>
        /// Decline a request with explanation
        /// </summary>
        private void DeclineRequest(UserRequest request, RequestOutcomeResult result)
        {
            Debug.Log($"AutonomyManager: DECLINE - Request: {request.RawText}, Reason: {result.Reason}");
            OnRequestDeclined?.Invoke(result.Reason);
            
            // Here would be integration to provide feedback to user in VR
        }

        /// <summary>
        /// Acknowledge a casual request without action
        /// </summary>
        private void AcknowledgeRequest(UserRequest request, RequestOutcomeResult result)
        {
            Debug.Log($"AutonomyManager: IGNORE - Acknowledging casual: {request.RawText}");
            
            // Could trigger a simple acknowledgment response
        }

        /// <summary>
        /// Log the decision for audit trail
        /// </summary>
        private void LogDecision(UserRequest request, RequestOutcomeResult result)
        {
            string logEntry = $"[{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}] " +
                            $"User: {request.Context.UserId} ({request.Context.UserRole}) | " +
                            $"Request: '{request.RawText}' | " +
                            $"Type: {result.ClassifiedType} | " +
                            $"Decision: {result.Decision} | " +
                            $"Reason: {result.Reason} | " +
                            $"Confidence: {result.ConfidenceScore:F2}";
            
            Debug.Log($"AutonomyManager: {logEntry}");
            
            // Here could write to persistent audit log
        }

        /// <summary>
        /// Add a custom policy rule at runtime
        /// </summary>
        public void AddPolicyRule(PolicyRule rule)
        {
            policyEngine.AddRule(rule);
        }

        /// <summary>
        /// Remove a policy rule at runtime
        /// </summary>
        public void RemovePolicyRule(string ruleId)
        {
            policyEngine.RemoveRule(ruleId);
        }

        /// <summary>
        /// Check if an action would be allowed without executing it
        /// </summary>
        public bool WouldAllowAction(string actionText, RequestContext context)
        {
            return policyEngine.IsActionAllowed(actionText, context);
        }
    }
}
