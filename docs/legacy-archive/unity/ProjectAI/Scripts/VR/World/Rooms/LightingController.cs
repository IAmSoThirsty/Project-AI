using UnityEngine;
using ProjectAI.VR.Genesis;
using System.Collections;

namespace ProjectAI.VR.World.Rooms
{
    /// <summary>
    /// Controls lighting in the Archive Room
    /// Manages Genesis awakening animation and normal lighting states
    /// </summary>
    public class LightingController : MonoBehaviour
    {
        [Header("Lighting Objects")]
        [SerializeField] private Light[] roomLights;
        [SerializeField] private Light ambientLight;

        [Header("Genesis Settings")]
        [SerializeField] private float genesisLightingDuration = 5.0f;
        [SerializeField] private AnimationCurve genesisIntensityCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        [SerializeField] private Color genesisStartColor = new Color(0.1f, 0.1f, 0.2f);
        [SerializeField] private Color genesisEndColor = Color.white;

        [Header("Normal Settings")]
        [SerializeField] private float normalIntensity = 1.0f;
        [SerializeField] private Color normalColor = Color.white;

        private bool isGenesisActive = false;
        private Coroutine genesisLightingCoroutine;

        // Singleton
        private static LightingController instance;
        public static LightingController Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<LightingController>();
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
            // Find all lights if not assigned
            if (roomLights == null || roomLights.Length == 0)
            {
                roomLights = FindObjectsOfType<Light>();
                Debug.Log($"LightingController: Found {roomLights.Length} lights in scene");
            }

            // Set initial dim state (for Genesis)
            SetLightingState(0.1f, genesisStartColor);

            Debug.Log("LightingController: Initialized");
        }

        /// <summary>
        /// Handle Genesis state changes
        /// </summary>
        private void HandleGenesisStateChanged(object sender, GenesisStateChangedEventArgs e)
        {
            if (e.NewState == GenesisState.RoomAwakening)
            {
                AnimateGenesisLighting();
            }
        }

        /// <summary>
        /// Animate lighting during Genesis Room Awakening phase
        /// </summary>
        public void AnimateGenesisLighting()
        {
            Debug.Log("LightingController: Starting Genesis lighting animation");
            isGenesisActive = true;

            if (genesisLightingCoroutine != null)
            {
                StopCoroutine(genesisLightingCoroutine);
            }

            genesisLightingCoroutine = StartCoroutine(GenesisLightingSequence());
        }

        /// <summary>
        /// Genesis lighting animation coroutine
        /// </summary>
        private IEnumerator GenesisLightingSequence()
        {
            float elapsed = 0.0f;

            while (elapsed < genesisLightingDuration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / genesisLightingDuration;
                float curveValue = genesisIntensityCurve.Evaluate(t);

                // Interpolate intensity
                float intensity = Mathf.Lerp(0.1f, normalIntensity, curveValue);

                // Interpolate color
                Color color = Color.Lerp(genesisStartColor, genesisEndColor, curveValue);

                // Apply to all lights
                SetLightingState(intensity, color);

                yield return null;
            }

            // Ensure final state
            SetLightingState(normalIntensity, normalColor);
            Debug.Log("LightingController: Genesis lighting animation complete");
        }

        /// <summary>
        /// Handle Genesis completion
        /// </summary>
        private void HandleGenesisComplete(object sender, System.EventArgs e)
        {
            Debug.Log("LightingController: Genesis complete - setting normal lighting");
            isGenesisActive = false;
            SetNormalLighting();
        }

        /// <summary>
        /// Set lighting state (intensity and color)
        /// </summary>
        private void SetLightingState(float intensity, Color color)
        {
            if (roomLights == null)
                return;

            foreach (Light light in roomLights)
            {
                if (light != null)
                {
                    light.intensity = intensity;
                    light.color = color;
                }
            }

            // Update ambient light if assigned
            if (ambientLight != null)
            {
                ambientLight.intensity = intensity * 0.5f;
                ambientLight.color = color;
            }
        }

        /// <summary>
        /// Set normal lighting after Genesis
        /// </summary>
        public void SetNormalLighting()
        {
            SetLightingState(normalIntensity, normalColor);
            Debug.Log("LightingController: Normal lighting set");
        }

        /// <summary>
        /// Dim lighting (for dramatic effect)
        /// </summary>
        public void DimLighting(float targetIntensity = 0.3f, float duration = 1.0f)
        {
            if (isGenesisActive)
            {
                Debug.LogWarning("LightingController: Cannot change lighting during Genesis");
                return;
            }

            StartCoroutine(TransitionLighting(targetIntensity, normalColor, duration));
        }

        /// <summary>
        /// Brighten lighting
        /// </summary>
        public void BrightenLighting(float targetIntensity = 1.5f, float duration = 1.0f)
        {
            if (isGenesisActive)
            {
                Debug.LogWarning("LightingController: Cannot change lighting during Genesis");
                return;
            }

            StartCoroutine(TransitionLighting(targetIntensity, normalColor, duration));
        }

        /// <summary>
        /// Change lighting color
        /// </summary>
        public void SetLightingColor(Color targetColor, float duration = 1.0f)
        {
            if (isGenesisActive)
            {
                Debug.LogWarning("LightingController: Cannot change lighting during Genesis");
                return;
            }

            StartCoroutine(TransitionLighting(normalIntensity, targetColor, duration));
        }

        /// <summary>
        /// Generic lighting transition coroutine
        /// </summary>
        private IEnumerator TransitionLighting(float targetIntensity, Color targetColor, float duration)
        {
            // Get current state
            float startIntensity = roomLights[0].intensity;
            Color startColor = roomLights[0].color;

            float elapsed = 0.0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;

                float intensity = Mathf.Lerp(startIntensity, targetIntensity, t);
                Color color = Color.Lerp(startColor, targetColor, t);

                SetLightingState(intensity, color);

                yield return null;
            }

            SetLightingState(targetIntensity, targetColor);
        }

        /// <summary>
        /// Emergency lighting (red glow)
        /// </summary>
        public void SetEmergencyLighting()
        {
            if (isGenesisActive)
                return;

            SetLightingState(0.7f, new Color(1.0f, 0.2f, 0.2f));
            Debug.Log("LightingController: Emergency lighting activated");
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
