// Package firewall — integration.go
//
// Integration hooks for OCTOREFLEX state machine.
// Bridges the escalation engine with the firewall controller.

package firewall

import (
	"context"
	"fmt"

	"go.uber.org/zap"
)

// StateChangeHook is called by the escalation engine when a process state changes.
// It applies firewall rules to match the new isolation level.
//
// This function is designed to be registered as a callback in the escalation
// engine's state machine.
//
// Performance target: <50μs
func StateChangeHook(ctx context.Context, c *Controller, pid uint32, oldState, newState uint8) error {
	if c == nil || !c.IsEnabled() {
		return nil // Firewall disabled, no-op
	}

	// Log state transition
	c.logger.Debug("firewall: state transition",
		zap.Uint32("pid", pid),
		zap.Uint8("old_state", oldState),
		zap.Uint8("new_state", newState))

	// Apply firewall rules for new state
	return c.OnStateChange(ctx, pid, newState)
}

// ProcessExitHook is called when a process terminates.
// It removes all firewall rules for the PID.
//
// This function is designed to be registered as a callback for process
// exit events.
func ProcessExitHook(ctx context.Context, c *Controller, pid uint32) error {
	if c == nil || !c.IsEnabled() {
		return nil // Firewall disabled, no-op
	}

	c.logger.Debug("firewall: process exit", zap.Uint32("pid", pid))

	return c.OnProcessExit(ctx, pid)
}

// IntegrationConfig holds configuration for firewall integration.
type IntegrationConfig struct {
	// Enabled controls whether firewall integration is active.
	Enabled bool

	// FirewallConfig is the firewall controller configuration.
	FirewallConfig Config
}

// Integration manages the firewall controller lifecycle.
type Integration struct {
	controller *Controller
	logger     *zap.Logger
}

// NewIntegration creates a new firewall integration.
func NewIntegration(cfg IntegrationConfig, logger *zap.Logger) (*Integration, error) {
	if !cfg.Enabled {
		logger.Info("firewall: integration disabled")
		return &Integration{
			controller: nil,
			logger:     logger,
		}, nil
	}

	controller, err := New(cfg.FirewallConfig, logger)
	if err != nil {
		return nil, fmt.Errorf("firewall integration: %w", err)
	}

	return &Integration{
		controller: controller,
		logger:     logger,
	}, nil
}

// Start initializes the firewall controller.
func (i *Integration) Start(ctx context.Context) error {
	if i.controller == nil {
		return nil // Disabled, no-op
	}

	i.logger.Info("firewall: starting integration")
	return i.controller.Start(ctx)
}

// Stop tears down the firewall controller.
func (i *Integration) Stop(ctx context.Context) error {
	if i.controller == nil {
		return nil // Disabled, no-op
	}

	i.logger.Info("firewall: stopping integration")
	return i.controller.Stop(ctx)
}

// GetController returns the firewall controller.
// Returns nil if firewall is disabled.
func (i *Integration) GetController() *Controller {
	return i.controller
}

// IsEnabled returns true if firewall integration is enabled.
func (i *Integration) IsEnabled() bool {
	return i.controller != nil && i.controller.IsEnabled()
}

// OnStateChange is a convenience wrapper for StateChangeHook.
func (i *Integration) OnStateChange(ctx context.Context, pid uint32, oldState, newState uint8) error {
	return StateChangeHook(ctx, i.controller, pid, oldState, newState)
}

// OnProcessExit is a convenience wrapper for ProcessExitHook.
func (i *Integration) OnProcessExit(ctx context.Context, pid uint32) error {
	return ProcessExitHook(ctx, i.controller, pid)
}

// GetStats returns firewall statistics.
// Returns zero stats if firewall is disabled.
func (i *Integration) GetStats() Stats {
	if i.controller == nil {
		return Stats{}
	}
	return i.controller.GetStats()
}
