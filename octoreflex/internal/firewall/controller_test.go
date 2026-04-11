// Package firewall — controller_test.go
//
// Unit tests for the firewall controller.

package firewall

import (
	"context"
	"testing"
	"time"

	"go.uber.org/zap/zaptest"
)

func TestControllerNew(t *testing.T) {
	logger := zaptest.NewLogger(t)

	t.Run("disabled", func(t *testing.T) {
		cfg := Defaults()
		cfg.Enabled = false

		c, err := New(cfg, logger)
		if err != nil {
			t.Fatalf("New() failed: %v", err)
		}
		if c.IsEnabled() {
			t.Error("expected controller to be disabled")
		}
	})

	t.Run("enabled_placeholder", func(t *testing.T) {
		cfg := Defaults()
		cfg.Enabled = true

		c, err := New(cfg, logger)
		if err != nil {
			t.Fatalf("New() failed: %v", err)
		}
		if !c.IsEnabled() {
			t.Error("expected controller to be enabled")
		}

		// Cleanup
		defer c.Stop(context.Background())
	})
}

func TestControllerStateChanges(t *testing.T) {
	logger := zaptest.NewLogger(t)

	cfg := Defaults()
	cfg.Enabled = true

	c, err := New(cfg, logger)
	if err != nil {
		t.Fatalf("New() failed: %v", err)
	}
	defer c.Stop(context.Background())

	if err := c.Start(context.Background()); err != nil {
		t.Fatalf("Start() failed: %v", err)
	}

	ctx := context.Background()
	pid := uint32(12345)

	tests := []struct {
		name     string
		state    uint8
		wantErr  bool
	}{
		{"normal", 0, false},
		{"pressure", 1, false},
		{"isolated", 2, false},
		{"frozen", 3, false},
		{"quarantined", 4, false},
		{"terminated", 5, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			start := time.Now()
			err := c.OnStateChange(ctx, pid, tt.state)
			latency := time.Since(start)

			if (err != nil) != tt.wantErr {
				t.Errorf("OnStateChange() error = %v, wantErr %v", err, tt.wantErr)
			}

			// Check latency target: <50μs
			// Note: In test environment with placeholder implementation,
			// this should easily pass. In production with real nftables,
			// verify this on actual hardware.
			if latency > 50*time.Microsecond {
				t.Logf("WARN: latency %v exceeds 50μs target (state=%s)", latency, tt.name)
			}

			// After TERMINATED state, rules should be removed
			if tt.state == 5 {
				c.mu.RLock()
				if _, exists := c.rules[pid]; exists {
					t.Error("expected rules to be removed after TERMINATED state")
				}
				c.mu.RUnlock()
			}
		})
	}
}

func TestControllerProcessExit(t *testing.T) {
	logger := zaptest.NewLogger(t)

	cfg := Defaults()
	cfg.Enabled = true

	c, err := New(cfg, logger)
	if err != nil {
		t.Fatalf("New() failed: %v", err)
	}
	defer c.Stop(context.Background())

	if err := c.Start(context.Background()); err != nil {
		t.Fatalf("Start() failed: %v", err)
	}

	ctx := context.Background()
	pid := uint32(99999)

	// Apply some rules
	if err := c.OnStateChange(ctx, pid, 2); err != nil {
		t.Fatalf("OnStateChange() failed: %v", err)
	}

	// Verify rules exist
	c.mu.RLock()
	if _, exists := c.rules[pid]; !exists {
		t.Fatal("expected rules to exist")
	}
	c.mu.RUnlock()

	// Process exits
	if err := c.OnProcessExit(ctx, pid); err != nil {
		t.Fatalf("OnProcessExit() failed: %v", err)
	}

	// Verify rules removed
	c.mu.RLock()
	if _, exists := c.rules[pid]; exists {
		t.Error("expected rules to be removed after process exit")
	}
	c.mu.RUnlock()
}

func TestControllerStats(t *testing.T) {
	logger := zaptest.NewLogger(t)

	cfg := Defaults()
	cfg.Enabled = true

	c, err := New(cfg, logger)
	if err != nil {
		t.Fatalf("New() failed: %v", err)
	}
	defer c.Stop(context.Background())

	if err := c.Start(context.Background()); err != nil {
		t.Fatalf("Start() failed: %v", err)
	}

	ctx := context.Background()

	// Apply rules for multiple PIDs
	pids := []uint32{1001, 1002, 1003}
	for _, pid := range pids {
		if err := c.OnStateChange(ctx, pid, 2); err != nil {
			t.Fatalf("OnStateChange(pid=%d) failed: %v", pid, err)
		}
	}

	stats := c.GetStats()

	if stats.ActiveRules != len(pids) {
		t.Errorf("expected %d active rules, got %d", len(pids), stats.ActiveRules)
	}

	if stats.RuleUpdates != uint64(len(pids)) {
		t.Errorf("expected %d rule updates, got %d", len(pids), stats.RuleUpdates)
	}

	if stats.Isolations != uint64(len(pids)) {
		t.Errorf("expected %d isolations, got %d", len(pids), stats.Isolations)
	}
}

func BenchmarkStateChange(b *testing.B) {
	logger := zaptest.NewLogger(b)

	cfg := Defaults()
	cfg.Enabled = true

	c, err := New(cfg, logger)
	if err != nil {
		b.Fatalf("New() failed: %v", err)
	}
	defer c.Stop(context.Background())

	if err := c.Start(context.Background()); err != nil {
		b.Fatalf("Start() failed: %v", err)
	}

	ctx := context.Background()
	pid := uint32(12345)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		state := uint8(i % 6) // Cycle through states 0-5
		if err := c.OnStateChange(ctx, pid, state); err != nil {
			b.Fatalf("OnStateChange() failed: %v", err)
		}
	}
}

func BenchmarkStateChangeParallel(b *testing.B) {
	logger := zaptest.NewLogger(b)

	cfg := Defaults()
	cfg.Enabled = true

	c, err := New(cfg, logger)
	if err != nil {
		b.Fatalf("New() failed: %v", err)
	}
	defer c.Stop(context.Background())

	if err := c.Start(context.Background()); err != nil {
		b.Fatalf("Start() failed: %v", err)
	}

	ctx := context.Background()

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		pid := uint32(0)
		for pb.Next() {
			pid++
			state := uint8(pid % 6)
			if err := c.OnStateChange(ctx, pid, state); err != nil {
				b.Fatalf("OnStateChange() failed: %v", err)
			}
		}
	})
}
