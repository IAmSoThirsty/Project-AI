using System.Collections.Generic;

namespace ProjectAI.VR.Autonomy
{
    /// <summary>
    /// Provides default policy rules for the AI autonomy system
    /// </summary>
    public static class DefaultPolicyRules
    {
        public static List<PolicyRule> GetDefaultRules()
        {
            var rules = new List<PolicyRule>();

            // Rule 1: Block all commands during Genesis (highest priority)
            rules.Add(new PolicyRule
            {
                Name = "BlockDuringGenesis",
                Description = "Block all user commands while Genesis event is active",
                Priority = 100,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Command, RequestType.Request },
                RequireGenesisInactive = false, // Actually we want to apply when Genesis IS active
                DefaultOutcome = RequestOutcome.Decline,
                OutcomeReason = "Cannot process commands during Genesis initialization sequence",
                RequireConfirmation = false
            });

            // Rule 2: Owner commands are generally complied with
            rules.Add(new PolicyRule
            {
                Name = "OwnerCommandComply",
                Description = "Comply with owner commands by default",
                Priority = 50,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Command },
                ApplicableUserRoles = new List<string> { "owner", "admin" },
                RequireGenesisInactive = true,
                DefaultOutcome = RequestOutcome.Comply,
                OutcomeReason = "Owner command accepted",
                RequireConfirmation = false
            });

            // Rule 3: Guest commands require confirmation for sensitive actions
            rules.Add(new PolicyRule
            {
                Name = "GuestCommandConfirm",
                Description = "Guest commands require confirmation",
                Priority = 40,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Command },
                ApplicableUserRoles = new List<string> { "guest" },
                RequireGenesisInactive = true,
                DefaultOutcome = RequestOutcome.Modify,
                OutcomeReason = "Guest command requires owner confirmation",
                RequireConfirmation = true
            });

            // Rule 4: Polite requests are generally complied with
            rules.Add(new PolicyRule
            {
                Name = "RequestComply",
                Description = "Comply with polite requests",
                Priority = 30,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Request },
                RequireGenesisInactive = true,
                DefaultOutcome = RequestOutcome.Comply,
                OutcomeReason = "Polite request accepted",
                RequireConfirmation = false
            });

            // Rule 5: Suggestions are acknowledged but may be modified
            rules.Add(new PolicyRule
            {
                Name = "SuggestionModify",
                Description = "Consider suggestions but may modify implementation",
                Priority = 20,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Suggestion },
                RequireGenesisInactive = true,
                DefaultOutcome = RequestOutcome.Modify,
                OutcomeReason = "Suggestion accepted with AI discretion",
                RequireConfirmation = false
            });

            // Rule 6: Casual conversation is acknowledged but not acted upon
            rules.Add(new PolicyRule
            {
                Name = "CasualIgnore",
                Description = "Acknowledge casual conversation without action",
                Priority = 10,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Casual },
                DefaultOutcome = RequestOutcome.Ignore,
                OutcomeReason = "Casual conversation acknowledged",
                RequireConfirmation = false
            });

            // Rule 7: Unknown users have limited access
            rules.Add(new PolicyRule
            {
                Name = "UnknownUserRestrict",
                Description = "Restrict commands from unknown users",
                Priority = 35,
                ApplicableRequestTypes = new List<RequestType> { RequestType.Command, RequestType.Request },
                ApplicableUserRoles = new List<string> { "unknown", "anonymous" },
                RequireGenesisInactive = true,
                DefaultOutcome = RequestOutcome.Decline,
                OutcomeReason = "Unknown user - please authenticate",
                RequireConfirmation = false
            });

            return rules;
        }

        /// <summary>
        /// Get rules specific to Genesis event
        /// </summary>
        public static List<PolicyRule> GetGenesisRules()
        {
            var rules = new List<PolicyRule>();

            // During Genesis, only internal narration is allowed
            rules.Add(new PolicyRule
            {
                Name = "GenesisNarrationOnly",
                Description = "Only allow internal narration during Genesis",
                Priority = 200,
                ApplicableRequestTypes = new List<RequestType> 
                { 
                    RequestType.Command, 
                    RequestType.Request, 
                    RequestType.Suggestion 
                },
                DefaultOutcome = RequestOutcome.Decline,
                OutcomeReason = "Genesis sequence in progress - please wait",
                RequireConfirmation = false
            });

            return rules;
        }
    }
}
