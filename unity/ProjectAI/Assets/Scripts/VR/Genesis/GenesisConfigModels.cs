using System;
using System.Collections.Generic;

namespace ProjectAI.VR.Genesis
{
    /// <summary>
    /// States of the Genesis event sequence
    /// </summary>
    public enum GenesisState
    {
        Dormant,                // Pre-Genesis, waiting for first connection
        OrbForming,             // Orb materializing/coalescing
        SubsystemsIgniting,     // AI subsystems coming online
        PresenceStabilizing,    // AI presence solidifying
        RoomAwakening,          // Archive room lighting up, environment activating
        Acknowledgement,        // AI acknowledges user, final narration
        Complete                // Genesis finished, normal operation begins
    }

    /// <summary>
    /// Configuration for Genesis event timing and narration
    /// </summary>
    [Serializable]
    public class GenesisConfig
    {
        public GenesisTimings Timings { get; set; }
        public Dictionary<string, GenesisRoleConfig> RoleConfigs { get; set; }

        public GenesisConfig()
        {
            Timings = new GenesisTimings();
            RoleConfigs = new Dictionary<string, GenesisRoleConfig>();
        }
    }

    /// <summary>
    /// Timing configuration for each Genesis state
    /// </summary>
    [Serializable]
    public class GenesisTimings
    {
        public float OrbFormingDuration { get; set; }           // Seconds for orb formation
        public float SubsystemsIgnitingDuration { get; set; }   // Seconds for subsystems
        public float PresenceStabilizingDuration { get; set; }  // Seconds for presence
        public float RoomAwakeningDuration { get; set; }        // Seconds for room awakening
        public float AcknowledgementDuration { get; set; }      // Seconds for acknowledgement

        public GenesisTimings()
        {
            // Default timings (in seconds)
            OrbFormingDuration = 3.0f;
            SubsystemsIgnitingDuration = 4.0f;
            PresenceStabilizingDuration = 3.0f;
            RoomAwakeningDuration = 5.0f;
            AcknowledgementDuration = 4.0f;
        }

        public float GetTotalDuration()
        {
            return OrbFormingDuration + SubsystemsIgnitingDuration + 
                   PresenceStabilizingDuration + RoomAwakeningDuration + 
                   AcknowledgementDuration;
        }
    }

    /// <summary>
    /// Role-specific Genesis configuration
    /// </summary>
    [Serializable]
    public class GenesisRoleConfig
    {
        public string RoleName { get; set; }                    // owner, guest, admin, etc.
        public List<string> NarrationLines { get; set; }        // Voice/text lines for each state
        public bool AllowInterruption { get; set; }             // Can this role interrupt Genesis?

        public GenesisRoleConfig()
        {
            RoleName = "guest";
            NarrationLines = new List<string>();
            AllowInterruption = false;
        }
    }

    /// <summary>
    /// Genesis event progress information
    /// </summary>
    [Serializable]
    public class GenesisProgress
    {
        public GenesisState CurrentState { get; set; }
        public float StateProgress { get; set; }                // 0-1 progress within current state
        public float OverallProgress { get; set; }              // 0-1 overall Genesis progress
        public DateTime StartTime { get; set; }
        public bool IsComplete { get; set; }

        public GenesisProgress()
        {
            CurrentState = GenesisState.Dormant;
            StateProgress = 0.0f;
            OverallProgress = 0.0f;
            StartTime = DateTime.UtcNow;
            IsComplete = false;
        }
    }

    /// <summary>
    /// Event data for Genesis state changes
    /// </summary>
    public class GenesisStateChangedEventArgs : EventArgs
    {
        public GenesisState PreviousState { get; set; }
        public GenesisState NewState { get; set; }
        public float Progress { get; set; }

        public GenesisStateChangedEventArgs(GenesisState previous, GenesisState newState, float progress)
        {
            PreviousState = previous;
            NewState = newState;
            Progress = progress;
        }
    }
}
