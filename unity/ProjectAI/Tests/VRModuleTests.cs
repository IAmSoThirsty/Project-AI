using System;
using System.Collections.Generic;
using UnityEngine;

namespace ProjectAI.Tests
{
    /// <summary>
    /// Simple test runner for VR module components
    /// Can be attached to a GameObject in Unity Editor for testing
    /// </summary>
    public class VRModuleTests : MonoBehaviour
    {
        [Header("Test Configuration")]
        [SerializeField] private bool runOnStart = false;
        [SerializeField] private bool verboseLogging = true;

        private int testsPassed = 0;
        private int testsFailed = 0;

        private void Start()
        {
            if (runOnStart)
            {
                RunAllTests();
            }
        }

        /// <summary>
        /// Run all tests
        /// </summary>
        [ContextMenu("Run All Tests")]
        public void RunAllTests()
        {
            Debug.Log("=== VR Module Tests Starting ===");
            testsPassed = 0;
            testsFailed = 0;

            // Autonomy System Tests
            TestRequestModels();
            TestRequestClassifier();
            TestPolicyEngine();

            // Genesis System Tests
            TestGenesisConfigModels();
            TestGenesisConfigLoader();

            // Integration Tests
            TestRoleManager();

            // Summary
            Debug.Log($"=== Tests Complete: {testsPassed} passed, {testsFailed} failed ===");
        }

        #region Autonomy System Tests

        private void TestRequestModels()
        {
            try
            {
                Log("Testing RequestModels...");

                // Test RequestContext creation
                var context = new VR.Autonomy.RequestContext
                {
                    UserRole = "owner",
                    UserId = "test123",
                    Environment = "TestScene",
                    IsGenesisActive = false
                };

                Assert(context.UserRole == "owner", "RequestContext UserRole");
                Assert(context.Metadata != null, "RequestContext Metadata initialized");

                // Test UserRequest creation
                var request = new VR.Autonomy.UserRequest("Turn on the lights", context);
                Assert(request.RequestId != null, "UserRequest has ID");
                Assert(request.RawText == "Turn on the lights", "UserRequest text");

                TestPass("RequestModels");
            }
            catch (Exception ex)
            {
                TestFail("RequestModels", ex.Message);
            }
        }

        private void TestRequestClassifier()
        {
            try
            {
                Log("Testing RequestClassifier...");

                var classifier = new VR.Autonomy.RequestClassifier();

                // Test command classification
                float confidence;
                var type = classifier.Classify("Turn off the lights", out confidence);
                Assert(type == VR.Autonomy.RequestType.Command, "Command classification");
                Assert(confidence > 0, "Classification confidence");

                // Test request classification
                type = classifier.Classify("Could you please turn off the lights?", out confidence);
                Assert(type == VR.Autonomy.RequestType.Request, "Request classification");

                // Test suggestion classification
                type = classifier.Classify("Maybe we could dim the lights", out confidence);
                Assert(type == VR.Autonomy.RequestType.Suggestion, "Suggestion classification");

                // Test casual classification
                type = classifier.Classify("It's bright in here", out confidence);
                Assert(type == VR.Autonomy.RequestType.Casual, "Casual classification");

                // Test intent extraction
                string intent = classifier.ExtractIntent("Please turn off the lights");
                Assert(!string.IsNullOrEmpty(intent), "Intent extraction");

                TestPass("RequestClassifier");
            }
            catch (Exception ex)
            {
                TestFail("RequestClassifier", ex.Message);
            }
        }

        private void TestPolicyEngine()
        {
            try
            {
                Log("Testing PolicyEngine...");

                var engine = new VR.Autonomy.PolicyEngine();
                
                // Create test request
                var context = new VR.Autonomy.RequestContext
                {
                    UserRole = "owner",
                    UserId = "test123",
                    IsGenesisActive = false
                };

                var request = new VR.Autonomy.UserRequest("Turn on the lights", context);

                // Evaluate request
                var result = engine.Evaluate(request);
                Assert(result != null, "PolicyEngine returns result");
                Assert(result.ClassifiedType != default, "Result has classification");
                Assert(result.Decision != default, "Result has decision");
                Assert(!string.IsNullOrEmpty(result.Reason), "Result has reason");

                // Test custom rule addition
                var customRule = new VR.Autonomy.PolicyRule
                {
                    Name = "TestRule",
                    Priority = 100
                };
                engine.AddRule(customRule);

                TestPass("PolicyEngine");
            }
            catch (Exception ex)
            {
                TestFail("PolicyEngine", ex.Message);
            }
        }

        #endregion

        #region Genesis System Tests

        private void TestGenesisConfigModels()
        {
            try
            {
                Log("Testing GenesisConfigModels...");

                // Test GenesisTimings
                var timings = new VR.Genesis.GenesisTimings();
                float total = timings.GetTotalDuration();
                Assert(total > 0, "GenesisTimings total duration");

                // Test GenesisProgress
                var progress = new VR.Genesis.GenesisProgress
                {
                    CurrentState = VR.Genesis.GenesisState.OrbForming,
                    StateProgress = 0.5f
                };
                Assert(progress.CurrentState == VR.Genesis.GenesisState.OrbForming, "GenesisProgress state");

                TestPass("GenesisConfigModels");
            }
            catch (Exception ex)
            {
                TestFail("GenesisConfigModels", ex.Message);
            }
        }

        private void TestGenesisConfigLoader()
        {
            try
            {
                Log("Testing GenesisConfigLoader...");

                // Load or create default config
                var config = VR.Genesis.GenesisConfigLoader.CreateDefaultConfig();
                Assert(config != null, "Config created");
                Assert(config.Timings != null, "Config has timings");
                Assert(config.RoleConfigs != null, "Config has role configs");
                Assert(config.RoleConfigs.Count > 0, "Config has roles");

                // Validate config
                bool isValid = VR.Genesis.GenesisConfigLoader.ValidateConfig(config);
                Assert(isValid, "Config is valid");

                TestPass("GenesisConfigLoader");
            }
            catch (Exception ex)
            {
                TestFail("GenesisConfigLoader", ex.Message);
            }
        }

        #endregion

        #region Integration Tests

        private void TestRoleManager()
        {
            try
            {
                Log("Testing RoleManager...");

                var roleManager = Core.RoleManager.Instance;
                Assert(roleManager != null, "RoleManager singleton exists");

                // Test role setting
                roleManager.SetRole("testUser", "owner");
                Assert(roleManager.CurrentRole == "owner", "Role set correctly");
                Assert(roleManager.CurrentUserId == "testUser", "UserId set correctly");

                // Test privilege checking
                bool isPrivileged = roleManager.IsPrivileged();
                Assert(isPrivileged, "Owner is privileged");

                // Test role check
                bool hasRole = roleManager.HasRole("owner");
                Assert(hasRole, "HasRole check works");

                TestPass("RoleManager");
            }
            catch (Exception ex)
            {
                TestFail("RoleManager", ex.Message);
            }
        }

        #endregion

        #region Test Utilities

        private void Assert(bool condition, string testName)
        {
            if (!condition)
            {
                throw new Exception($"Assertion failed: {testName}");
            }
            if (verboseLogging)
            {
                Log($"  ✓ {testName}");
            }
        }

        private void TestPass(string testName)
        {
            testsPassed++;
            Debug.Log($"✓ {testName} PASSED");
        }

        private void TestFail(string testName, string reason)
        {
            testsFailed++;
            Debug.LogError($"✗ {testName} FAILED: {reason}");
        }

        private void Log(string message)
        {
            if (verboseLogging)
            {
                Debug.Log(message);
            }
        }

        #endregion
    }
}
