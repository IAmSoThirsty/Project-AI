using System;
using UnityEngine;

namespace ProjectAI.Core
{
    /// <summary>
    /// Manages user roles and permissions
    /// Singleton that tracks current user role and notifies systems of role changes
    /// </summary>
    public class RoleManager : MonoBehaviour
    {
        private string currentRole;
        private string currentUserId;

        // Events
        public event Action<string, string> OnRoleChanged;  // (userId, newRole)

        // Singleton
        private static RoleManager instance;
        public static RoleManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<RoleManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("RoleManager");
                        instance = go.AddComponent<RoleManager>();
                    }
                }
                return instance;
            }
        }

        // Properties
        public string CurrentRole => currentRole ?? "guest";
        public string CurrentUserId => currentUserId ?? "anonymous";

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

        private void Initialize()
        {
            // Load saved role from PlayerPrefs or default to guest
            currentUserId = PlayerPrefs.GetString("CurrentUserId", "anonymous");
            currentRole = PlayerPrefs.GetString("CurrentUserRole", "guest");
            
            Debug.Log($"RoleManager: Initialized with userId='{currentUserId}', role='{currentRole}'");
        }

        /// <summary>
        /// Set the current user role
        /// </summary>
        public void SetRole(string userId, string role)
        {
            if (string.IsNullOrWhiteSpace(userId) || string.IsNullOrWhiteSpace(role))
            {
                Debug.LogWarning("RoleManager: Invalid userId or role");
                return;
            }

            string previousRole = currentRole;
            currentUserId = userId;
            currentRole = role.ToLower();

            // Persist to PlayerPrefs
            PlayerPrefs.SetString("CurrentUserId", currentUserId);
            PlayerPrefs.SetString("CurrentUserRole", currentRole);
            PlayerPrefs.Save();

            Debug.Log($"RoleManager: Role changed from '{previousRole}' to '{currentRole}' for user '{currentUserId}'");

            // Notify listeners
            OnRoleChanged?.Invoke(currentUserId, currentRole);
        }

        /// <summary>
        /// Check if current user has a specific role
        /// </summary>
        public bool HasRole(string role)
        {
            return string.Equals(currentRole, role, StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Check if current user is owner or admin
        /// </summary>
        public bool IsPrivileged()
        {
            return HasRole("owner") || HasRole("admin");
        }

        /// <summary>
        /// Reset to guest role
        /// </summary>
        public void ResetToGuest()
        {
            SetRole("anonymous", "guest");
        }

        /// <summary>
        /// Logout current user
        /// </summary>
        public void Logout()
        {
            Debug.Log($"RoleManager: User '{currentUserId}' logged out");
            ResetToGuest();
        }
    }
}
