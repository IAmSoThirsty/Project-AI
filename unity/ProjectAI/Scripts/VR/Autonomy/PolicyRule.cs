using System;
using System.Collections.Generic;

namespace ProjectAI.VR.Autonomy
{
    /// <summary>
    /// Defines a rule for determining how the AI should respond to requests
    /// </summary>
    [Serializable]
    public class PolicyRule
    {
        public string RuleId { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int Priority { get; set; }                   // Higher priority rules override lower ones
        
        // Conditions
        public List<RequestType> ApplicableRequestTypes { get; set; }
        public List<string> ApplicableUserRoles { get; set; }
        public List<string> ApplicableEnvironments { get; set; }
        public bool RequireFirstConnection { get; set; }    // Only applies to first-time users
        public bool RequireGenesisInactive { get; set; }    // Only applies when Genesis is not running
        
        // Action
        public RequestOutcome DefaultOutcome { get; set; }
        public string OutcomeReason { get; set; }
        public bool RequireConfirmation { get; set; }

        public PolicyRule()
        {
            RuleId = Guid.NewGuid().ToString();
            Priority = 0;
            ApplicableRequestTypes = new List<RequestType>();
            ApplicableUserRoles = new List<string>();
            ApplicableEnvironments = new List<string>();
            RequireFirstConnection = false;
            RequireGenesisInactive = false;
            RequireConfirmation = false;
        }

        /// <summary>
        /// Checks if this rule applies to the given context
        /// </summary>
        public bool Matches(RequestType requestType, RequestContext context)
        {
            // Check request type
            if (ApplicableRequestTypes.Count > 0 && !ApplicableRequestTypes.Contains(requestType))
                return false;

            // Check user role
            if (ApplicableUserRoles.Count > 0 && !ApplicableUserRoles.Contains(context.UserRole))
                return false;

            // Check environment
            if (ApplicableEnvironments.Count > 0 && !ApplicableEnvironments.Contains(context.Environment))
                return false;

            // Check first connection requirement
            if (RequireFirstConnection && !context.IsFirstConnection)
                return false;

            // Check Genesis inactive requirement
            if (RequireGenesisInactive && context.IsGenesisActive)
                return false;

            return true;
        }
    }
}
