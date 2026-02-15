using System;
using System.Collections.Generic;

namespace ProjectAI.VR.Autonomy
{
    /// <summary>
    /// Defines the type of user request
    /// </summary>
    public enum RequestType
    {
        Command,      // Direct order: "Turn off the lights"
        Request,      // Polite ask: "Could you turn off the lights?"
        Suggestion,   // Idea: "Maybe we could turn off the lights?"
        Casual        // Conversational: "It's bright in here"
    }

    /// <summary>
    /// AI's decision on how to respond to a request
    /// </summary>
    public enum RequestOutcome
    {
        Comply,       // Execute the request as stated
        Decline,      // Refuse the request with explanation
        Modify,       // Alter the request before execution
        Ignore        // Acknowledge but take no action
    }

    /// <summary>
    /// Context information for evaluating a request
    /// </summary>
    [Serializable]
    public class RequestContext
    {
        public string UserRole { get; set; }           // owner, guest, admin, etc.
        public string UserId { get; set; }             // Unique user identifier
        public string Environment { get; set; }        // VR scene context
        public DateTime Timestamp { get; set; }        // When request was made
        public Dictionary<string, object> Metadata { get; set; }  // Additional context
        
        public bool IsFirstConnection { get; set; }    // Is this user's first VR session?
        public bool IsGenesisActive { get; set; }      // Is Genesis event running?
        public int InteractionCount { get; set; }      // Number of previous interactions

        public RequestContext()
        {
            Timestamp = DateTime.UtcNow;
            Metadata = new Dictionary<string, object>();
            IsFirstConnection = false;
            IsGenesisActive = false;
            InteractionCount = 0;
        }
    }

    /// <summary>
    /// Result of request evaluation
    /// </summary>
    [Serializable]
    public class RequestOutcomeResult
    {
        public RequestType ClassifiedType { get; set; }     // How request was classified
        public RequestOutcome Decision { get; set; }        // AI's decision
        public string Reason { get; set; }                  // Explanation for decision
        public string ModifiedRequest { get; set; }         // If modified, the new request
        public bool RequiresUserConfirmation { get; set; }  // Does this need confirmation?
        public float ConfidenceScore { get; set; }          // Classification confidence (0-1)

        public RequestOutcomeResult()
        {
            RequiresUserConfirmation = false;
            ConfidenceScore = 0.0f;
        }
    }

    /// <summary>
    /// Represents a user request to be processed
    /// </summary>
    [Serializable]
    public class UserRequest
    {
        public string RequestId { get; set; }          // Unique request ID
        public string RawText { get; set; }            // Original request text
        public RequestContext Context { get; set; }    // Request context
        public DateTime CreatedAt { get; set; }        // When request was created

        public UserRequest()
        {
            RequestId = Guid.NewGuid().ToString();
            CreatedAt = DateTime.UtcNow;
            Context = new RequestContext();
        }

        public UserRequest(string text, RequestContext context)
        {
            RequestId = Guid.NewGuid().ToString();
            RawText = text;
            Context = context ?? new RequestContext();
            CreatedAt = DateTime.UtcNow;
        }
    }
}
