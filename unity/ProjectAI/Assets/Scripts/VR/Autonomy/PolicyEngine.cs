using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace ProjectAI.VR.Autonomy
{
    /// <summary>
    /// Evaluates requests against policy rules to determine outcomes
    /// </summary>
    public class PolicyEngine
    {
        private List<PolicyRule> rules;
        private RequestClassifier classifier;

        public PolicyEngine()
        {
            rules = new List<PolicyRule>();
            classifier = new RequestClassifier();
            LoadDefaultRules();
        }

        public PolicyEngine(List<PolicyRule> customRules)
        {
            rules = customRules ?? new List<PolicyRule>();
            classifier = new RequestClassifier();
        }

        /// <summary>
        /// Load default policy rules
        /// </summary>
        private void LoadDefaultRules()
        {
            rules.AddRange(DefaultPolicyRules.GetDefaultRules());
            Debug.Log($"PolicyEngine: Loaded {rules.Count} default rules");
        }

        /// <summary>
        /// Add a custom policy rule
        /// </summary>
        public void AddRule(PolicyRule rule)
        {
            if (rule != null)
            {
                rules.Add(rule);
                // Re-sort by priority
                rules = rules.OrderByDescending(r => r.Priority).ToList();
                Debug.Log($"PolicyEngine: Added rule '{rule.Name}' with priority {rule.Priority}");
            }
        }

        /// <summary>
        /// Remove a policy rule by ID
        /// </summary>
        public void RemoveRule(string ruleId)
        {
            rules.RemoveAll(r => r.RuleId == ruleId);
            Debug.Log($"PolicyEngine: Removed rule {ruleId}");
        }

        /// <summary>
        /// Get all active rules
        /// </summary>
        public List<PolicyRule> GetRules()
        {
            return new List<PolicyRule>(rules);
        }

        /// <summary>
        /// Evaluate a request and determine the appropriate outcome
        /// </summary>
        public RequestOutcomeResult Evaluate(UserRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.RawText))
            {
                return new RequestOutcomeResult
                {
                    ClassifiedType = RequestType.Casual,
                    Decision = RequestOutcome.Ignore,
                    Reason = "Empty or invalid request",
                    ConfidenceScore = 1.0f
                };
            }

            // Classify the request
            float confidence;
            RequestType requestType = classifier.Classify(request.RawText, out confidence);

            Debug.Log($"PolicyEngine: Classified '{request.RawText}' as {requestType} (confidence: {confidence:F2})");

            // Special handling for Genesis event
            if (request.Context.IsGenesisActive)
            {
                // During Genesis, apply special rules
                var genesisRules = DefaultPolicyRules.GetGenesisRules();
                foreach (var rule in genesisRules.OrderByDescending(r => r.Priority))
                {
                    if (rule.Matches(requestType, request.Context))
                    {
                        return new RequestOutcomeResult
                        {
                            ClassifiedType = requestType,
                            Decision = rule.DefaultOutcome,
                            Reason = rule.OutcomeReason,
                            RequiresUserConfirmation = rule.RequireConfirmation,
                            ConfidenceScore = confidence
                        };
                    }
                }
            }

            // Find the first matching rule (rules are sorted by priority)
            foreach (var rule in rules.OrderByDescending(r => r.Priority))
            {
                if (rule.Matches(requestType, request.Context))
                {
                    Debug.Log($"PolicyEngine: Matched rule '{rule.Name}' - Decision: {rule.DefaultOutcome}");
                    
                    return new RequestOutcomeResult
                    {
                        ClassifiedType = requestType,
                        Decision = rule.DefaultOutcome,
                        Reason = rule.OutcomeReason,
                        RequiresUserConfirmation = rule.RequireConfirmation,
                        ConfidenceScore = confidence
                    };
                }
            }

            // Default fallback: comply with low confidence
            Debug.LogWarning($"PolicyEngine: No matching rule found, using default outcome");
            return new RequestOutcomeResult
            {
                ClassifiedType = requestType,
                Decision = RequestOutcome.Comply,
                Reason = "No specific policy applies - default action",
                RequiresUserConfirmation = false,
                ConfidenceScore = confidence * 0.5f // Lower confidence for fallback
            };
        }

        /// <summary>
        /// Evaluate multiple requests and return outcomes for each
        /// </summary>
        public List<RequestOutcomeResult> EvaluateBatch(List<UserRequest> requests)
        {
            var results = new List<RequestOutcomeResult>();
            
            foreach (var request in requests)
            {
                results.Add(Evaluate(request));
            }

            return results;
        }

        /// <summary>
        /// Check if a specific action is allowed under current policy
        /// </summary>
        public bool IsActionAllowed(string actionText, RequestContext context)
        {
            var request = new UserRequest(actionText, context);
            var result = Evaluate(request);
            
            return result.Decision == RequestOutcome.Comply || 
                   result.Decision == RequestOutcome.Modify;
        }
    }
}
