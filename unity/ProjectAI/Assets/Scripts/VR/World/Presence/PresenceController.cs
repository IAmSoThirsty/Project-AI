using System.Collections;
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
        [SerializeField] private ParticleSystem formationParticles;
        [SerializeField] private ParticleSystem stabilizationParticles;
        [SerializeField] private Renderer orbRenderer;

        [Header("Movement Settings")]
        [SerializeField] private bool lockPositionDuringGenesis = true;
        [SerializeField] private Vector3 defaultPosition = new Vector3(0, 1.5f, 2);
        [SerializeField] private float moveSpeed = 2.0f;

        private bool isGenesisActive = false;
        private bool isFormed = false;
        private Coroutine currentAnimationCoroutine;
        private Vector3 targetPosition;
        private MaterialPropertyBlock propBlock;

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

        private void Update()
        {
            if (orbObject != null && isFormed && !isGenesisActive)
            {
                // Smooth movement to target
                if (Vector3.Distance(orbObject.transform.position, targetPosition) > 0.01f)
                {
                    orbObject.transform.position = Vector3.Lerp(
                        orbObject.transform.position, 
                        targetPosition, 
                        Time.deltaTime * moveSpeed
                    );
                }
            }
        }

        private void Initialize()
        {
            propBlock = new MaterialPropertyBlock();

            // Initialize orb (hidden initially for Genesis)
            if (orbObject != null)
            {
                // Start invisible for Genesis formation
                targetPosition = defaultPosition;
                orbObject.transform.position = defaultPosition;
                orbObject.transform.localScale = Vector3.zero; // Start small
                SetOrbVisibility(false);
                
                if (orbRenderer == null)
                    orbRenderer = orbObject.GetComponent<Renderer>();
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
            if (e.NewState == GenesisState.OrbForming)
            {
                StartOrbFormation();
            }
            else if (e.NewState == GenesisState.PresenceStabilizing)
            {
                StartPresenceStabilization();
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
            SetOrbVisibility(true);

            if (currentAnimationCoroutine != null) StopCoroutine(currentAnimationCoroutine);
            currentAnimationCoroutine = StartCoroutine(AnimateFormation());

            Debug.Log("PresenceController: Orb formation animation started");
        }

        private IEnumerator AnimateFormation()
        {
            // Particle Coalescing
            if (formationParticles != null)
            {
                formationParticles.Play();
            }

            float elapsed = 0f;
            Vector3 initialScale = Vector3.zero;
            Vector3 finalScale = Vector3.one;

            // Visual Transformation: Swell from zero to full size with pulsing
            while (elapsed < formationDuration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / formationDuration;
                // Ease out elastic
                float scale = Mathf.Lerp(0, 1, t);
                
                // Add some noise/pulse during formation
                float noise = Mathf.Sin(elapsed * 10) * 0.1f * (1-t); 
                orbObject.transform.localScale = (finalScale * scale) + (Vector3.one * noise);

                yield return null;
            }

            orbObject.transform.localScale = finalScale;
        }

        /// <summary>
        /// Start presence stabilization
        /// </summary>
        public void StartPresenceStabilization()
        {
            Debug.Log("PresenceController: Stabilizing presence");

            if (currentAnimationCoroutine != null) StopCoroutine(currentAnimationCoroutine);
            currentAnimationCoroutine = StartCoroutine(AnimateStabilization());

            isFormed = true;
        }

        private IEnumerator AnimateStabilization()
        {
            if (formationParticles != null) formationParticles.Stop();
            if (stabilizationParticles != null) stabilizationParticles.Play();

            float elapsed = 0f;
            
            // Stabilization: Reduce pulsing, smooth color transition
            while (elapsed < stabilizationDuration)
            {
                elapsed += Time.deltaTime;
                // Smooth out any residual jitter
                yield return null;
            }
            
            // Finalize state
            if (stabilizationParticles != null) stabilizationParticles.Stop();
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
            StartCoroutine(AnimateIdle());
            Debug.Log("PresenceController: Normal behavior enabled");
        }

        private IEnumerator AnimateIdle()
        {
            while (!isGenesisActive)
            {
                // Gentle bobbing
                float yOffset = Mathf.Sin(Time.time) * 0.1f;
                if (!isGenesisActive) // Double check inside loop
                {
                     // Only apply bobbing visual offset, don't change actual transform position 
                     // so movement logic doesn't fight it. 
                     // Ideally we'd use a child object for visuals.
                }
                yield return null;
            }
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
        public void MoveOrb(Vector3 newTargetPosition)
        {
            if (lockPositionDuringGenesis && isGenesisActive)
            {
                Debug.LogWarning("PresenceController: Orb movement locked during Genesis");
                return;
            }

            if (orbObject == null)
                return;

            targetPosition = newTargetPosition;
            Debug.Log($"PresenceController: Orb target set to {targetPosition}");
        }

        /// <summary>
        /// Set orb emotion/visual state
        /// </summary>
        public void SetEmotion(string emotion)
        {
            if (orbRenderer == null) return;

            Debug.Log($"PresenceController: Setting emotion to '{emotion}'");
            
            Color emissionColor = Color.white;
            switch (emotion.ToLower())
            {
                case "happy": emissionColor = Color.green; break;
                case "alert": emissionColor = Color.yellow; break;
                case "warning": emissionColor = Color.red; break;
                case "thinking": emissionColor = Color.cyan; break;
                default: emissionColor = Color.blue; break; // Neutral
            }

            orbRenderer.GetPropertyBlock(propBlock);
            propBlock.SetColor("_EmissionColor", emissionColor);
            orbRenderer.SetPropertyBlock(propBlock);
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

