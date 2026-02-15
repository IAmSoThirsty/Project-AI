using System;
using System.Collections;
using UnityEngine;

namespace ProjectAI.VR.Genesis
{
    /// <summary>
    /// Manages the Genesis event sequence - the first-time VR experience
    /// State machine that orchestrates orb formation, subsystem ignition, and room awakening
    /// </summary>
    public class GenesisManager : MonoBehaviour
    {
        private GenesisConfig config;
        private GenesisProgress progress;
        private Coroutine genesisCoroutine;
        private string currentUserRole;

        // Events
        public event EventHandler<GenesisStateChangedEventArgs> OnStateChanged;
        public event EventHandler OnGenesisComplete;
        public event Action<string> OnNarration;  // For displaying narration text/voice

        // Singleton
        private static GenesisManager instance;
        public static GenesisManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<GenesisManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("GenesisManager");
                        instance = go.AddComponent<GenesisManager>();
                    }
                }
                return instance;
            }
        }

        // Properties
        public bool IsGenesisActive => progress != null && !progress.IsComplete;
        public GenesisState CurrentState => progress?.CurrentState ?? GenesisState.Dormant;
        public float OverallProgress => progress?.OverallProgress ?? 0.0f;

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
        /// Initialize Genesis system
        /// </summary>
        private void Initialize()
        {
            config = GenesisConfigLoader.LoadConfig();
            progress = new GenesisProgress();
            
            Debug.Log("GenesisManager: Initialized");
        }

        /// <summary>
        /// Check if Genesis should be triggered for a user
        /// </summary>
        public bool ShouldTriggerGenesis(string userId)
        {
            // Check PlayerPrefs for Genesis completion flag
            string key = $"Genesis_Complete_{userId}";
            return !PlayerPrefs.HasKey(key) || PlayerPrefs.GetInt(key, 0) == 0;
        }

        /// <summary>
        /// Start the Genesis event sequence
        /// </summary>
        public void StartGenesis(string userRole = "guest")
        {
            if (IsGenesisActive)
            {
                Debug.LogWarning("GenesisManager: Genesis already active");
                return;
            }

            currentUserRole = userRole;
            progress = new GenesisProgress
            {
                CurrentState = GenesisState.Dormant,
                StartTime = DateTime.UtcNow,
                IsComplete = false
            };

            Debug.Log($"GenesisManager: Starting Genesis for role '{userRole}'");
            
            if (genesisCoroutine != null)
            {
                StopCoroutine(genesisCoroutine);
            }
            
            genesisCoroutine = StartCoroutine(GenesisSequence());
        }

        /// <summary>
        /// Main Genesis sequence coroutine
        /// </summary>
        private IEnumerator GenesisSequence()
        {
            yield return StartCoroutine(TransitionToState(GenesisState.OrbForming, config.Timings.OrbFormingDuration));
            yield return StartCoroutine(TransitionToState(GenesisState.SubsystemsIgniting, config.Timings.SubsystemsIgnitingDuration));
            yield return StartCoroutine(TransitionToState(GenesisState.PresenceStabilizing, config.Timings.PresenceStabilizingDuration));
            yield return StartCoroutine(TransitionToState(GenesisState.RoomAwakening, config.Timings.RoomAwakeningDuration));
            yield return StartCoroutine(TransitionToState(GenesisState.Acknowledgement, config.Timings.AcknowledgementDuration));
            
            CompleteGenesis();
        }

        /// <summary>
        /// Transition to a new Genesis state
        /// </summary>
        private IEnumerator TransitionToState(GenesisState newState, float duration)
        {
            GenesisState previousState = progress.CurrentState;
            progress.CurrentState = newState;

            Debug.Log($"GenesisManager: Transitioning to {newState} (duration: {duration}s)");

            // Notify state change
            OnStateChanged?.Invoke(this, new GenesisStateChangedEventArgs(previousState, newState, 0.0f));

            // Get narration for this state
            string narration = GetNarrationForState(newState);
            if (!string.IsNullOrEmpty(narration))
            {
                OnNarration?.Invoke(narration);
                Debug.Log($"GenesisManager: Narration - '{narration}'");
            }

            // Execute state-specific logic
            ExecuteStateLogic(newState);

            // Wait for state duration with progress updates
            float elapsed = 0.0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                progress.StateProgress = Mathf.Clamp01(elapsed / duration);
                progress.OverallProgress = CalculateOverallProgress(newState, progress.StateProgress);
                
                yield return null;
            }

            progress.StateProgress = 1.0f;
        }

        /// <summary>
        /// Execute logic specific to each Genesis state
        /// </summary>
        private void ExecuteStateLogic(GenesisState state)
        {
            switch (state)
            {
                case GenesisState.OrbForming:
                    // Trigger orb formation animation
                    Debug.Log("GenesisManager: Triggering orb formation");
                    // Integration point: PresenceController.StartOrbFormation()
                    break;

                case GenesisState.SubsystemsIgniting:
                    // Activate subsystem visual effects
                    Debug.Log("GenesisManager: Igniting subsystems");
                    // Integration point: SubsystemVisuals.Ignite()
                    break;

                case GenesisState.PresenceStabilizing:
                    // Stabilize orb presence
                    Debug.Log("GenesisManager: Stabilizing presence");
                    // Integration point: PresenceController.Stabilize()
                    break;

                case GenesisState.RoomAwakening:
                    // Animate room lighting
                    Debug.Log("GenesisManager: Awakening archive room");
                    // Integration point: LightingController.AnimateGenesis()
                    break;

                case GenesisState.Acknowledgement:
                    // Final acknowledgement
                    Debug.Log("GenesisManager: Final acknowledgement");
                    break;
            }
        }

        /// <summary>
        /// Get narration text for a given state
        /// </summary>
        private string GetNarrationForState(GenesisState state)
        {
            if (!config.RoleConfigs.TryGetValue(currentUserRole, out GenesisRoleConfig roleConfig))
            {
                // Fallback to guest if role not found
                config.RoleConfigs.TryGetValue("guest", out roleConfig);
            }

            if (roleConfig == null || roleConfig.NarrationLines == null)
                return string.Empty;

            // Map state to narration line index
            int index = state switch
            {
                GenesisState.OrbForming => 0,
                GenesisState.SubsystemsIgniting => 1,
                GenesisState.PresenceStabilizing => 2,
                GenesisState.RoomAwakening => 3,
                GenesisState.Acknowledgement => 4,
                _ => -1
            };

            if (index >= 0 && index < roleConfig.NarrationLines.Count)
            {
                return roleConfig.NarrationLines[index];
            }

            return string.Empty;
        }

        /// <summary>
        /// Calculate overall progress across all states
        /// </summary>
        private float CalculateOverallProgress(GenesisState currentState, float stateProgress)
        {
            float totalDuration = config.Timings.GetTotalDuration();
            float completedDuration = 0.0f;

            // Add completed state durations
            if (currentState > GenesisState.OrbForming)
                completedDuration += config.Timings.OrbFormingDuration;
            if (currentState > GenesisState.SubsystemsIgniting)
                completedDuration += config.Timings.SubsystemsIgnitingDuration;
            if (currentState > GenesisState.PresenceStabilizing)
                completedDuration += config.Timings.PresenceStabilizingDuration;
            if (currentState > GenesisState.RoomAwakening)
                completedDuration += config.Timings.RoomAwakeningDuration;

            // Add current state partial progress
            float currentStateDuration = currentState switch
            {
                GenesisState.OrbForming => config.Timings.OrbFormingDuration,
                GenesisState.SubsystemsIgniting => config.Timings.SubsystemsIgnitingDuration,
                GenesisState.PresenceStabilizing => config.Timings.PresenceStabilizingDuration,
                GenesisState.RoomAwakening => config.Timings.RoomAwakeningDuration,
                GenesisState.Acknowledgement => config.Timings.AcknowledgementDuration,
                _ => 0.0f
            };

            completedDuration += currentStateDuration * stateProgress;

            return Mathf.Clamp01(completedDuration / totalDuration);
        }

        /// <summary>
        /// Complete the Genesis event
        /// </summary>
        private void CompleteGenesis()
        {
            progress.CurrentState = GenesisState.Complete;
            progress.IsComplete = true;
            progress.OverallProgress = 1.0f;

            Debug.Log("GenesisManager: Genesis complete!");

            // Mark Genesis as complete in PlayerPrefs
            // Note: userId should be passed and stored, using a default for now
            PlayerPrefs.SetInt("Genesis_Complete_default", 1);
            PlayerPrefs.Save();

            // Notify completion
            OnGenesisComplete?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Reset Genesis for testing or new user
        /// </summary>
        public void ResetGenesis(string userId = "default")
        {
            string key = $"Genesis_Complete_{userId}";
            PlayerPrefs.DeleteKey(key);
            PlayerPrefs.Save();
            
            Debug.Log($"GenesisManager: Reset Genesis for user '{userId}'");
        }

        /// <summary>
        /// Skip Genesis (for debugging)
        /// </summary>
        public void SkipGenesis()
        {
            if (genesisCoroutine != null)
            {
                StopCoroutine(genesisCoroutine);
            }
            CompleteGenesis();
        }

        /// <summary>
        /// Check if user role can interrupt Genesis
        /// </summary>
        public bool CanInterruptGenesis(string userRole)
        {
            if (!config.RoleConfigs.TryGetValue(userRole, out GenesisRoleConfig roleConfig))
            {
                return false;
            }
            return roleConfig.AllowInterruption;
        }
    }
}
