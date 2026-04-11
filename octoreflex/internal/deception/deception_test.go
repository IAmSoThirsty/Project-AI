// Package deception — deception_test.go
//
// Integration tests for deception mechanisms.

package deception

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
)

func TestPortRotation(t *testing.T) {
	log := zap.NewNop()
	cfg := DefaultPortRotationConfig()
	cfg.NodeID = "test-node-1"
	cfg.MinRotationInterval = 100 * time.Millisecond
	cfg.MaxRotationInterval = 200 * time.Millisecond

	pr, err := NewPortRotation(cfg, log)
	require.NoError(t, err)

	// Test deterministic port generation
	serviceID := "test-service"
	port1 := pr.GetCurrentPort(serviceID)
	port2 := pr.GetCurrentPort(serviceID)
	assert.Equal(t, port1, port2, "same service should get same port")

	// Test port rotation
	pr.SetThreatLevel(0.8)
	time.Sleep(300 * time.Millisecond)

	port3 := pr.GetNextPort(serviceID)
	assert.NotEqual(t, port1, port3, "port should rotate after interval")

	// Test sequence info
	info := pr.GetSequenceInfo()
	assert.Greater(t, info.Epoch, int64(0))
	assert.Equal(t, pr.cfg.HopSequenceLength, info.SequenceLen)
}

func TestCostAmplifier(t *testing.T) {
	log := zap.NewNop()
	cfg := DefaultCostAmplifierConfig()
	cfg.POWDifficulty = 10 // Easier for testing

	ca := NewCostAmplifier(cfg, log)

	// Test POW challenge generation
	challenge := ca.GeneratePOWChallenge()
	assert.NotEmpty(t, challenge.Data)
	assert.Equal(t, cfg.POWDifficulty, challenge.Difficulty)

	// Test POW solving
	nonce, err := SolvePOW(challenge)
	require.NoError(t, err)

	// Test POW verification
	verified := ca.VerifyPOW(challenge, nonce)
	assert.True(t, verified, "valid POW should verify")

	// Test bandwidth amplification
	requestSize := 100
	data := ca.AmplifyBandwidth(requestSize)
	assert.NotNil(t, data)
	assert.Greater(t, len(data), requestSize)

	// Test slowdown
	delay := ca.ApplySlowdown(0.5)
	assert.Greater(t, delay, time.Duration(0))

	// Test stats
	stats := ca.GetStats()
	assert.Greater(t, stats.TotalChallenges, uint64(0))
	assert.Greater(t, stats.SuccessfulSolves, uint64(0))

	// Test cost calculation
	cost := ca.CalculateCostUSD()
	assert.Greater(t, cost.TotalCostUSD, 0.0)
}

func TestTCPDecoy(t *testing.T) {
	log := zap.NewNop()
	cfg := DefaultTCPDecoyConfig()
	// Use non-privileged ports for testing
	cfg.BindAddrs = []string{
		"127.0.0.1:12222", // SSH
		"127.0.0.1:13306", // MySQL
	}
	cfg.ProtocolHandlers = map[int]string{
		12222: "ssh",
		13306: "mysql",
	}

	td := NewTCPDecoy(cfg, log)

	err := td.Start()
	require.NoError(t, err)
	defer td.Stop()

	// Give listeners time to start
	time.Sleep(100 * time.Millisecond)

	// Test stats
	stats := td.GetStats()
	assert.Equal(t, 2, stats.ListenerCount)
}

func TestOrchestrator(t *testing.T) {
	log := zap.NewNop()
	cfg := DefaultOrchestratorConfig()
	
	// Disable honeypots for this test (would need network access)
	cfg.EnableSSHHoneypot = false
	cfg.EnableHTTPHoneypot = false
	
	// Use non-privileged ports for TCP decoys
	cfg.TCPDecoy.BindAddrs = []string{"127.0.0.1:14444"}

	o, err := NewOrchestrator(cfg, log)
	require.NoError(t, err)
	require.NotNil(t, o)

	err = o.Start()
	require.NoError(t, err)
	defer o.Stop()

	// Test port rotation integration
	port := o.GetCurrentPort("test-service")
	assert.Greater(t, port, 0)

	// Test threat level adjustment
	o.SetThreatLevel(0.7)

	// Test POW integration
	challenge := o.GeneratePOWChallenge()
	assert.NotEmpty(t, challenge.Data)

	// Test stats
	stats := o.GetStats()
	assert.True(t, stats.Enabled)
	assert.True(t, stats.Running)
}

func TestCostCalculation(t *testing.T) {
	log := zap.NewNop()
	cfg := DefaultCostAmplifierConfig()
	cfg.POWDifficulty = 15

	ca := NewCostAmplifier(cfg, log)

	// Generate and solve some challenges
	for i := 0; i < 5; i++ {
		challenge := ca.GeneratePOWChallenge()
		nonce, _ := SolvePOW(challenge)
		ca.VerifyPOW(challenge, nonce)
	}

	// Amplify some bandwidth
	for i := 0; i < 10; i++ {
		ca.AmplifyBandwidth(1000)
	}

	cost := ca.CalculateCostUSD()
	
	// Verify cost breakdown
	assert.Greater(t, cost.TotalCostUSD, 0.0)
	assert.Greater(t, cost.CPUCostUSD, 0.0)
	assert.Greater(t, cost.BandwidthCostUSD, 0.0)
	assert.Greater(t, cost.TimeCostUSD, 0.0)
	
	// Total should be sum of components
	sum := cost.CPUCostUSD + cost.BandwidthCostUSD + cost.TimeCostUSD
	assert.InDelta(t, cost.TotalCostUSD, sum, 0.01)

	t.Logf("Total cost imposed: $%.2f", cost.TotalCostUSD)
	t.Logf("  CPU cost: $%.2f", cost.CPUCostUSD)
	t.Logf("  Bandwidth cost: $%.2f", cost.BandwidthCostUSD)
	t.Logf("  Time cost: $%.2f", cost.TimeCostUSD)
}

func TestPortRotationChaos(t *testing.T) {
	log := zap.NewNop()
	cfg := DefaultPortRotationConfig()
	cfg.NodeID = "chaos-test"
	cfg.EnableChaosMode = true

	pr, err := NewPortRotation(cfg, log)
	require.NoError(t, err)

	// Generate sequence
	info := pr.GetSequenceInfo()
	
	// Verify sequence has expected length
	assert.Equal(t, cfg.HopSequenceLength, info.SequenceLen)

	// Test that chaos mode produces different sequences
	// even with same base parameters (due to chaotic shuffling)
	ports := make(map[int]bool)
	for i := 0; i < 10; i++ {
		serviceID := "service-" + string(rune('A'+i))
		port := pr.GetCurrentPort(serviceID)
		ports[port] = true
	}

	// Should have multiple unique ports
	assert.GreaterOrEqual(t, len(ports), 5)
}

func BenchmarkPOWSolve(b *testing.B) {
	log := zap.NewNop()
	cfg := DefaultCostAmplifierConfig()
	cfg.POWDifficulty = 15 // Moderate difficulty

	ca := NewCostAmplifier(cfg, log)
	challenge := ca.GeneratePOWChallenge()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		SolvePOW(challenge)
	}
}

func BenchmarkPortRotation(b *testing.B) {
	log := zap.NewNop()
	cfg := DefaultPortRotationConfig()
	cfg.NodeID = "bench-test"

	pr, _ := NewPortRotation(cfg, log)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pr.GetCurrentPort("service-1")
	}
}
