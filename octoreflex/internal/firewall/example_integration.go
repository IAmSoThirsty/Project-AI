// Example: OCTOREFLEX Firewall Integration
//
// This example demonstrates how to integrate the firewall controller
// with the OCTOREFLEX escalation engine.
//
// Build: go build -o firewall-example example_integration.go
// Run: sudo ./firewall-example

//go:build linux
// +build linux

package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/octoreflex/octoreflex/internal/firewall"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func main() {
	// Create logger
	config := zap.NewDevelopmentConfig()
	config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
	logger, err := config.Build()
	if err != nil {
		panic(err)
	}
	defer logger.Sync()

	logger.Info("OCTOREFLEX Firewall Integration Example")

	// Check if running as root (required for nftables and cgroups)
	if os.Geteuid() != 0 {
		logger.Fatal("This example must be run as root (required for nftables and cgroups)")
	}

	// Create firewall configuration
	fwCfg := firewall.Defaults()
	fwCfg.Enabled = true
	fwCfg.DNSBlocklist = "./testdata/dns-blocklist.txt"

	logger.Info("Firewall configuration",
		zap.Bool("enabled", fwCfg.Enabled),
		zap.String("table", fwCfg.NftablesTable),
		zap.String("family", fwCfg.NftablesFamily),
		zap.String("dns_blocklist", fwCfg.DNSBlocklist))

	// Create firewall integration
	integration, err := firewall.NewIntegration(firewall.IntegrationConfig{
		Enabled:        true,
		FirewallConfig: fwCfg,
	}, logger)
	if err != nil {
		logger.Fatal("Failed to create firewall integration", zap.Error(err))
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start firewall
	logger.Info("Starting firewall...")
	if err := integration.Start(ctx); err != nil {
		logger.Fatal("Failed to start firewall", zap.Error(err))
	}
	defer integration.Stop(ctx)

	logger.Info("Firewall started successfully")

	// Example: Simulate process state changes
	testPID := uint32(os.Getpid())

	logger.Info("=== Testing State Transitions ===")

	// Test state transitions
	states := []struct {
		name  string
		state uint8
	}{
		{"NORMAL", 0},
		{"PRESSURE", 1},
		{"ISOLATED", 2},
		{"FROZEN", 3},
		{"QUARANTINED", 4},
	}

	for _, s := range states {
		logger.Info("Applying state", zap.String("state", s.name), zap.Uint32("pid", testPID))
		
		start := time.Now()
		err := integration.OnStateChange(ctx, testPID, 0, s.state)
		latency := time.Since(start)
		
		if err != nil {
			logger.Error("State change failed",
				zap.String("state", s.name),
				zap.Error(err))
		} else {
			logger.Info("State change successful",
				zap.String("state", s.name),
				zap.Duration("latency", latency),
				zap.Bool("meets_target", latency < 50*time.Microsecond))
		}

		time.Sleep(1 * time.Second)
	}

	// Show statistics
	stats := integration.GetStats()
	logger.Info("=== Firewall Statistics ===",
		zap.Uint64("rule_updates", stats.RuleUpdates),
		zap.Uint64("rule_errors", stats.RuleUpdateErrors),
		zap.Uint64("isolations", stats.Isolations),
		zap.Uint64("dns_blocks", stats.DNSBlocks),
		zap.Int("active_rules", stats.ActiveRules))

	// Clean up test process
	logger.Info("Cleaning up test process")
	if err := integration.OnProcessExit(ctx, testPID); err != nil {
		logger.Error("Process exit cleanup failed", zap.Error(err))
	}

	// Wait for signal
	logger.Info("Firewall running. Press Ctrl+C to stop.")
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	logger.Info("Shutting down firewall...")
}

// Example state machine integration:
//
// type EscalationEngine struct {
//     firewall *firewall.Integration
//     // ... other fields
// }
//
// func (e *EscalationEngine) EscalateProcess(pid uint32, newState uint8) error {
//     oldState := e.GetProcessState(pid)
//     
//     // Update internal state
//     e.updateState(pid, newState)
//     
//     // Notify firewall
//     if err := e.firewall.OnStateChange(ctx, pid, oldState, newState); err != nil {
//         log.Error("firewall state update failed", zap.Error(err))
//         // Non-fatal - continue with escalation
//     }
//     
//     return nil
// }
//
// func (e *EscalationEngine) OnProcessExit(pid uint32) {
//     // Clean up internal state
//     e.removeProcess(pid)
//     
//     // Notify firewall
//     if err := e.firewall.OnProcessExit(ctx, pid); err != nil {
//         log.Error("firewall cleanup failed", zap.Error(err))
//     }
// }
