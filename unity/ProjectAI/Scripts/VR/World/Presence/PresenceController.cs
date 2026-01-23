using UnityEngine;
using ProjectAI.VR.Genesis;

namespace ProjectAI.VR.World.Presence
{
    /// <summary>
    /// Controls the AI orb presence in VR
    /// Manages orb position, emotion display, and Genesis animations
    /// </summary>
    public class PresenceController : MonoBehaviour
    {
        [Header("Orb Settings")]
        [SerializeField] private GameObject orbObject;
        [SerializeField] private float formationDuration = 3.0f;
        [SerializeField] private float stabilizationDuration = 3.0f;

        [Header("Movement Settings")]
        [SerializeField] private bool lockPositionDuringGenesis = true;
        [SerializeField] private Vector3 defaultPosition = new Vector3(0, 1.5f, 2);

        private bool isGenesisActive = false;
        private bool isFormed = false;

        // Singleton
        private static PresenceController instance;
        public static PresenceController Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<PresenceController>();
                }
                return instance;
            }
        }

        public bool IsOrbFormed => isFormed;

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            instance = this;

            Initialize();
        }

        private void Start()
        {
            // Subscribe to Genesis events
            if (GenesisManager.Instance != null)
            {
                GenesisManager.Instance.OnStateChanged += HandleGenesisStateChanged;
                GenesisManager.Instance.OnGenesisComplete += HandleGenesisComplete;
            }
        }

        private void Initialize()
        {
            // Initialize orb (hidden initially for Genesis)
            if (orbObject != null)
            {
                // Start invisible for Genesis formation
                SetOrbVisibility(false);
            }
            else
            {
                Debug.LogWarning("PresenceController: Orb object not assigned");
            }

            Debug.Log("PresenceController: Initialized");
        }

        /// <summary>
        /// Handle Genesis state changes
        /// </summary>
        private void HandleGenesisStateChanged(object sender, GenesisStateChangedEventArgs e)
        {
            switch (e.NewState)
            {
                case GenesisState.OrbForming:
                    StartOrbFormation();
                    break;

                case GenesisState.PresenceStabilizing:
                    StartPresenceStabilization();
                    break;
            }
        }

        /// <summary>
        /// Start orb formation animation
        /// </summary>
        public void StartOrbFormation()
        {
            Debug.Log("PresenceController: Starting orb formation");
            isGenesisActive = true;

            if (orbObject == null)
            {
                Debug.LogWarning("PresenceController: Cannot form orb - object not assigned");
                return;
            }

            // Position orb at default location
            orbObject.transform.position = defaultPosition;

            // Start formation animation
            // This would trigger particle effects, materialization shader, etc.
            SetOrbVisibility(true);
            
            // TODO: Implement actual formation animation
            // - Particle coalescing effect
            // - Fade in shader
            // - Pulsing glow
            
            Debug.Log("PresenceController: Orb formation animation started");
        }

        /// <summary>
        /// Start presence stabilization
        /// </summary>
        public void StartPresenceStabilization()
        {
            Debug.Log("PresenceController: Stabilizing presence");

            // TODO: Implement stabilization effects
            // - Reduce pulsing
            // - Smooth out movements
            // - Solidify visual appearance

            isFormed = true;
        }

        /// <summary>
        /// Handle Genesis completion
        /// </summary>
        private void HandleGenesisComplete(object sender, System.EventArgs e)
        {
            Debug.Log("PresenceController: Genesis complete - unlocking orb movement");
            isGenesisActive = false;

            // Enable normal orb behaviors
            EnableNormalBehavior();
        }

        /// <summary>
        /// Enable normal orb behavior after Genesis
        /// </summary>
        private void EnableNormalBehavior()
        {
            // Enable idle animations, emotional responses, etc.
            Debug.Log("PresenceController: Normal behavior enabled");
        }

        /// <summary>
        /// Set orb visibility
        /// </summary>
        private void SetOrbVisibility(bool visible)
        {
            if (orbObject != null)
            {
                orbObject.SetActive(visible);
            }
        }

        /// <summary>
        /// Move orb to a position (blocked during Genesis)
        /// </summary>
        public void MoveOrb(Vector3 targetPosition)
        {
            if (lockPositionDuringGenesis && isGenesisActive)
            {
                Debug.LogWarning("PresenceController: Orb movement locked during Genesis");
                return;
            }

            if (orbObject == null)
                return;

            // Move orb smoothly
            // TODO: Implement smooth movement with animation
            orbObject.transform.position = targetPosition;
            
            Debug.Log($"PresenceController: Orb moved to {targetPosition}");
        }

        /// <summary>
        /// Set orb emotion/visual state
        /// </summary>
        public void SetEmotion(string emotion)
        {
            Debug.Log($"PresenceController: Setting emotion to '{emotion}'");
            
            // TODO: Implement emotion visualization
            // - Change orb color
            // - Adjust particle effects
            // - Modify animation patterns
        }

        /// <summary>
        /// Get current orb position
        /// </summary>
        public Vector3 GetOrbPosition()
        {
            if (orbObject != null)
            {
                return orbObject.transform.position;
            }
            return defaultPosition;
        }

        private void OnDestroy()
        {
            // Unsubscribe from events
            if (GenesisManager.Instance != null)
            {
                GenesisManager.Instance.OnStateChanged -= HandleGenesisStateChanged;
                GenesisManager.Instance.OnGenesisComplete -= HandleGenesisComplete;
            }
        }
    }
}
