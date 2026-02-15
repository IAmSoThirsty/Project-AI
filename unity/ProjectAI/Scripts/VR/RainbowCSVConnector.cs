using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using ProjectAI.VR.Bridge;

namespace ProjectAI.VR.RainbowCSV
{
    /// <summary>
    /// Example script demonstrating how to consume commands from the Rainbow CSV backend
    /// Attach this to a GameObject in your VR scene
    /// </summary>
    public class RainbowCSVConnector : MonoBehaviour
    {
        [Header("Connection")]
        [SerializeField] private string backendUrl = "http://localhost:8001";
        [SerializeField] private float pollInterval = 0.5f;

        [Header("Visual Elements")]
        [SerializeField] private Light roomLight;
        [SerializeField] private GameObject orbPrefab;
        [SerializeField] private Transform orbContainer;

        private float lastPollTimestamp = 0;

        private void Start()
        {
            if (roomLight == null)
            {
                Debug.LogWarning("RainbowCSVConnector: No Light assigned. Please assign a Light component.");
            }

            StartCoroutine(PollLoop());
        }

        private IEnumerator PollLoop()
        {
            while (true)
            {
                yield return new WaitForSeconds(pollInterval);
                yield return PollCommands();
            }
        }

        private IEnumerator PollCommands()
        {
            string url = $"{backendUrl}/vr/commands?since={lastPollTimestamp}";

            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    string json = request.downloadHandler.text;
                    
                    // Simple JSON parsing (you may need JsonUtility or Newtonsoft.Json for complex objects)
                    if (!string.IsNullOrEmpty(json) && json != "[]")
                    {
                        Debug.Log($"[Rainbow CSV] Received commands: {json}");
                        // For Demo: just log. In production, parse and execute
                        // ProcessCommands(json);
                    }
                }
                else
                {
                    Debug.LogWarning($"[Rainbow CSV] Poll failed: {request.error}");
                }
            }
        }

        /// <summary>
        /// Example: Change light color based on hex string
        /// </summary>
        public void ChangeLightColor(string hexColor)
        {
            if (roomLight == null) return;

            if (ColorUtility.TryParseHtmlString(hexColor, out Color color))
            {
                roomLight.color = color;
                Debug.Log($"[Rainbow CSV] Light color changed to {hexColor}");
            }
        }

        /// <summary>
        /// Example: Spawn a data orb
        /// </summary>
        public void SpawnOrb(string label, string hexColor)
        {
            if (orbPrefab == null || orbContainer == null) return;

            GameObject orb = Instantiate(orbPrefab, orbContainer);
            orb.name = $"DataOrb_{label}";

            if (ColorUtility.TryParseHtmlString(hexColor, out Color color))
            {
                Renderer renderer = orb.GetComponent<Renderer>();
                if (renderer != null)
                {
                    renderer.material.color = color;
                }
            }

            Debug.Log($"[Rainbow CSV] Spawned orb: {label}");
        }
    }
}
