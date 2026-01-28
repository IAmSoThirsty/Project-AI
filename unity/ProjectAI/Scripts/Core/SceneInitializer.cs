using System.Collections;
using UnityEngine;
using ProjectAI.VR.Genesis;

namespace ProjectAI.Core
{
    /// <summary>
    /// Initializes the VR scene and determines startup path
    /// Checks for first-time users and triggers Genesis event if needed
    /// </summary>
    public class SceneInitializer : MonoBehaviour
    {
        [Header("Startup Settings")]
        [SerializeField] private bool skipGenesisForTesting = false;
        [SerializeField] private float initializationDelay = 0.5f;

        private bool isInitialized = false;

        private void Start()
        {
            StartCoroutine(InitializeScene());
        }

        /// <summary>
        /// Main scene initialization sequence
        /// </summary>
        private IEnumerator InitializeScene()
        {
            Debug.Log("SceneInitializer: Beginning scene initialization");

            // Wait for initial delay to ensure all systems are ready
            yield return new WaitForSeconds(initializationDelay);

            // Initialize core systems
            InitializeCoreSystems();

            // Check if user needs Genesis experience
            string userId = RoleManager.Instance.CurrentUserId;
            string userRole = RoleManager.Instance.CurrentRole;

            bool needsGenesis = GenesisManager.Instance.ShouldTriggerGenesis(userId);

            if (needsGenesis && !skipGenesisForTesting)
            {
                Debug.Log($"SceneInitializer: First-time user detected - triggering Genesis for '{userRole}'");
                StartGenesisExperience(userRole);
            }
            else
            {
                Debug.Log("SceneInitializer: Standard initialization - bypassing Genesis");
                StartNormalExperience();
            }

            isInitialized = true;
            Debug.Log("SceneInitializer: Scene initialization complete");
        }

        /// <summary>
        /// Initialize core game systems
        /// </summary>
        private void InitializeCoreSystems()
        {
            // Ensure singletons are initialized
            var roleManager = RoleManager.Instance;
            var genesisManager = GenesisManager.Instance;
            var autonomyManager = ProjectAI.VR.Autonomy.AutonomyManager.Instance;

            Debug.Log("SceneInitializer: Core systems initialized");
        }

        /// <summary>
        /// Start the Genesis first-time experience
        /// </summary>
        private void StartGenesisExperience(string userRole)
        {
            // Subscribe to Genesis completion
            GenesisManager.Instance.OnGenesisComplete += OnGenesisComplete;

            // Start Genesis sequence
            GenesisManager.Instance.StartGenesis(userRole);

            Debug.Log("SceneInitializer: Genesis experience started");
        }

        /// <summary>
        /// Start normal (non-Genesis) experience
        /// </summary>
        private void StartNormalExperience()
        {
            // Enable normal VR interactions
            EnableVRInteractions();

            // Initialize conversation systems
            // Integration point: ConversationContextManager.Initialize()

            Debug.Log("SceneInitializer: Normal experience started");
        }

        /// <summary>
        /// Called when Genesis sequence completes
        /// </summary>
        private void OnGenesisComplete(object sender, System.EventArgs e)
        {
            Debug.Log("SceneInitializer: Genesis complete - transitioning to normal mode");

            // Unsubscribe from event
            GenesisManager.Instance.OnGenesisComplete -= OnGenesisComplete;

            // Enable normal VR interactions
            EnableVRInteractions();

            // Notify other systems that Genesis is complete
            // Integration point: Various systems can listen for this
        }

        /// <summary>
        /// Enable VR interactions after Genesis or for normal startup
        /// </summary>
        private void EnableVRInteractions()
        {
            Debug.Log("SceneInitializer: Enabling VR interactions");

            // Integration points:
            // - Enable conversation input
            // - Enable hand tracking
            // - Enable teleportation
            // - Enable object interaction
            // These would be implemented in respective controller classes
        }

        /// <summary>
        /// Public method to force Genesis reset (for testing/admin)
        /// </summary>
        public void ForceResetGenesis()
        {
            if (!RoleManager.Instance.IsPrivileged())
            {
                Debug.LogWarning("SceneInitializer: Only privileged users can reset Genesis");
                return;
            }

            string userId = RoleManager.Instance.CurrentUserId;
            GenesisManager.Instance.ResetGenesis(userId);
            Debug.Log($"SceneInitializer: Genesis reset for user '{userId}'");
        }

        /// <summary>
        /// Check if scene initialization is complete
        /// </summary>
        public bool IsInitialized()
        {
            return isInitialized;
        }

        private void OnDestroy()
        {
            // Clean up event subscriptions
            if (GenesisManager.Instance != null)
            {
                GenesisManager.Instance.OnGenesisComplete -= OnGenesisComplete;
            }
        }
    }
}
