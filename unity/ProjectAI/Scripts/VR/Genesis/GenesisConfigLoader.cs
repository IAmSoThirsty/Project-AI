using System;
using System.IO;
using UnityEngine;

namespace ProjectAI.VR.Genesis
{
    /// <summary>
    /// Loads Genesis configuration from JSON file in StreamingAssets
    /// </summary>
    public class GenesisConfigLoader
    {
        private const string CONFIG_FILENAME = "GenesisConfig.json";
        private const string CONFIG_FOLDER = "ProjectAI";

        /// <summary>
        /// Load Genesis configuration from StreamingAssets
        /// </summary>
        public static GenesisConfig LoadConfig()
        {
            string configPath = GetConfigPath();
            
            if (!File.Exists(configPath))
            {
                Debug.LogWarning($"GenesisConfigLoader: Config file not found at {configPath}, using defaults");
                return CreateDefaultConfig();
            }

            try
            {
                string jsonContent = File.ReadAllText(configPath);
                GenesisConfig config = JsonUtility.FromJson<GenesisConfig>(jsonContent);
                
                if (config == null)
                {
                    Debug.LogError("GenesisConfigLoader: Failed to parse config, using defaults");
                    return CreateDefaultConfig();
                }

                Debug.Log($"GenesisConfigLoader: Successfully loaded config from {configPath}");
                return config;
            }
            catch (Exception ex)
            {
                Debug.LogError($"GenesisConfigLoader: Error loading config: {ex.Message}");
                return CreateDefaultConfig();
            }
        }

        /// <summary>
        /// Save Genesis configuration to StreamingAssets
        /// </summary>
        public static bool SaveConfig(GenesisConfig config)
        {
            string configPath = GetConfigPath();
            
            try
            {
                // Ensure directory exists
                string directory = Path.GetDirectoryName(configPath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                string jsonContent = JsonUtility.ToJson(config, true);
                File.WriteAllText(configPath, jsonContent);
                
                Debug.Log($"GenesisConfigLoader: Successfully saved config to {configPath}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"GenesisConfigLoader: Error saving config: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get the full path to the config file
        /// </summary>
        private static string GetConfigPath()
        {
            return Path.Combine(Application.streamingAssetsPath, CONFIG_FOLDER, CONFIG_FILENAME);
        }

        /// <summary>
        /// Create default Genesis configuration
        /// </summary>
        public static GenesisConfig CreateDefaultConfig()
        {
            var config = new GenesisConfig
            {
                Timings = new GenesisTimings
                {
                    OrbFormingDuration = 3.0f,
                    SubsystemsIgnitingDuration = 4.0f,
                    PresenceStabilizingDuration = 3.0f,
                    RoomAwakeningDuration = 5.0f,
                    AcknowledgementDuration = 4.0f
                }
            };

            // Owner role configuration
            var ownerConfig = new GenesisRoleConfig
            {
                RoleName = "owner",
                AllowInterruption = true,
                NarrationLines = new System.Collections.Generic.List<string>
                {
                    "Initializing... Coalescing form...",                          // OrbForming
                    "Core systems coming online... Subsystems igniting...",         // SubsystemsIgniting
                    "Presence stabilizing... Identity forming...",                  // PresenceStabilizing
                    "Archive awakening... Environment systems online...",           // RoomAwakening
                    "Genesis complete. Welcome, Owner. I am ready to serve."       // Acknowledgement
                }
            };

            // Guest role configuration
            var guestConfig = new GenesisRoleConfig
            {
                RoleName = "guest",
                AllowInterruption = false,
                NarrationLines = new System.Collections.Generic.List<string>
                {
                    "Initializing... Coalescing form...",                          // OrbForming
                    "Core systems coming online... Subsystems igniting...",         // SubsystemsIgniting
                    "Presence stabilizing... Identity forming...",                  // PresenceStabilizing
                    "Archive awakening... Environment systems online...",           // RoomAwakening
                    "Genesis complete. Welcome, Guest. How may I assist you?"      // Acknowledgement
                }
            };

            // Admin role configuration
            var adminConfig = new GenesisRoleConfig
            {
                RoleName = "admin",
                AllowInterruption = true,
                NarrationLines = new System.Collections.Generic.List<string>
                {
                    "Initializing... Coalescing form...",                          // OrbForming
                    "Core systems coming online... Subsystems igniting...",         // SubsystemsIgniting
                    "Presence stabilizing... Identity forming...",                  // PresenceStabilizing
                    "Archive awakening... Environment systems online...",           // RoomAwakening
                    "Genesis complete. Welcome, Administrator. Systems ready."     // Acknowledgement
                }
            };

            config.RoleConfigs.Add("owner", ownerConfig);
            config.RoleConfigs.Add("guest", guestConfig);
            config.RoleConfigs.Add("admin", adminConfig);

            return config;
        }

        /// <summary>
        /// Validate Genesis configuration
        /// </summary>
        public static bool ValidateConfig(GenesisConfig config)
        {
            if (config == null)
            {
                Debug.LogError("GenesisConfigLoader: Config is null");
                return false;
            }

            if (config.Timings == null)
            {
                Debug.LogError("GenesisConfigLoader: Timings is null");
                return false;
            }

            if (config.RoleConfigs == null || config.RoleConfigs.Count == 0)
            {
                Debug.LogWarning("GenesisConfigLoader: No role configs defined");
            }

            // Validate timings are positive
            if (config.Timings.OrbFormingDuration <= 0 ||
                config.Timings.SubsystemsIgnitingDuration <= 0 ||
                config.Timings.PresenceStabilizingDuration <= 0 ||
                config.Timings.RoomAwakeningDuration <= 0 ||
                config.Timings.AcknowledgementDuration <= 0)
            {
                Debug.LogError("GenesisConfigLoader: All timing values must be positive");
                return false;
            }

            return true;
        }
    }
}
