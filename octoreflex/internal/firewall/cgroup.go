// Package firewall — cgroup.go
//
// Per-process network isolation using cgroups v2.
// Integrates with nftables for cgroup-based packet filtering.
//
// Architecture:
//   - cgroup v2 hierarchy: /sys/fs/cgroup/octoreflex/isolated/
//   - Each isolated process gets a unique cgroup: isolated/pid-{pid}
//   - nftables matches on cgroup ID for efficient packet filtering
//   - Automatic cleanup on process exit
//
// Requirements:
//   - cgroup v2 mounted at /sys/fs/cgroup
//   - Kernel 4.5+ (cgroup v2 support)

package firewall

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"sync"

	"go.uber.org/zap"
)

// CgroupIsolator manages per-process cgroup isolation.
type CgroupIsolator struct {
	mu     sync.Mutex
	logger *zap.Logger
	cfg    CgroupConfig

	// State tracking
	isolated map[uint32]string // pid -> cgroup path
}

// CgroupConfig holds cgroup isolator configuration.
type CgroupConfig struct {
	// Root is the cgroup v2 mount point.
	Root string

	// IsolatedPath is the cgroup path for isolated processes.
	IsolatedPath string
}

// NewCgroupIsolator creates a new cgroup isolator.
func NewCgroupIsolator(cfg CgroupConfig, logger *zap.Logger) (*CgroupIsolator, error) {
	if cfg.Root == "" {
		cfg.Root = "/sys/fs/cgroup"
	}
	if cfg.IsolatedPath == "" {
		cfg.IsolatedPath = filepath.Join(cfg.Root, "octoreflex", "isolated")
	}

	return &CgroupIsolator{
		logger:   logger,
		cfg:      cfg,
		isolated: make(map[uint32]string),
	}, nil
}

// Initialize creates the cgroup hierarchy.
func (c *CgroupIsolator) Initialize(ctx context.Context) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.logger.Info("cgroup: initializing hierarchy",
		zap.String("root", c.cfg.Root),
		zap.String("isolated_path", c.cfg.IsolatedPath))

	// Check if cgroup v2 is mounted
	if _, err := os.Stat(filepath.Join(c.cfg.Root, "cgroup.controllers")); os.IsNotExist(err) {
		c.logger.Warn("cgroup: cgroup v2 not detected, cgroup isolation will not work",
			zap.String("path", c.cfg.Root))
		// Non-fatal, continue without cgroup support
		return nil
	}

	// Create isolated cgroup directory
	if err := os.MkdirAll(c.cfg.IsolatedPath, 0755); err != nil && !os.IsExist(err) {
		return fmt.Errorf("cgroup: mkdir %s: %w", c.cfg.IsolatedPath, err)
	}

	// Enable controllers (cpu, memory, io, pids)
	controllersPath := filepath.Join(c.cfg.IsolatedPath, "cgroup.subtree_control")
	controllers := "+cpu +memory +io +pids"
	if err := os.WriteFile(controllersPath, []byte(controllers), 0644); err != nil {
		// Non-fatal if controllers cannot be enabled (might already be enabled)
		c.logger.Warn("cgroup: failed to enable controllers",
			zap.String("path", controllersPath),
			zap.Error(err))
	}

	c.logger.Info("cgroup: initialized successfully")
	return nil
}

// Teardown removes the cgroup hierarchy.
func (c *CgroupIsolator) Teardown(ctx context.Context) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.logger.Info("cgroup: tearing down hierarchy")

	// Release all isolated processes
	for pid := range c.isolated {
		if err := c.releaseLocked(ctx, pid); err != nil {
			c.logger.Error("cgroup: failed to release PID during teardown",
				zap.Uint32("pid", pid),
				zap.Error(err))
		}
	}

	// Remove isolated cgroup directory
	// Note: This will fail if any processes are still in the cgroup
	if err := os.Remove(c.cfg.IsolatedPath); err != nil && !os.IsNotExist(err) {
		c.logger.Warn("cgroup: failed to remove isolated path",
			zap.String("path", c.cfg.IsolatedPath),
			zap.Error(err))
	}

	return nil
}

// Isolate moves a process into an isolated cgroup.
// Returns the cgroup path.
func (c *CgroupIsolator) Isolate(ctx context.Context, pid uint32) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if path, exists := c.isolated[pid]; exists {
		return path, nil // Already isolated
	}

	c.logger.Debug("cgroup: isolating process", zap.Uint32("pid", pid))

	// Create per-PID cgroup
	cgroupPath := filepath.Join(c.cfg.IsolatedPath, fmt.Sprintf("pid-%d", pid))
	if err := os.MkdirAll(cgroupPath, 0755); err != nil {
		return "", fmt.Errorf("cgroup: mkdir %s: %w", cgroupPath, err)
	}

	// Move process into cgroup
	procsPath := filepath.Join(cgroupPath, "cgroup.procs")
	if err := os.WriteFile(procsPath, []byte(strconv.Itoa(int(pid))), 0644); err != nil {
		// Clean up cgroup on failure
		os.Remove(cgroupPath)
		return "", fmt.Errorf("cgroup: write %s: %w", procsPath, err)
	}

	// Apply resource limits (optional, for defense in depth)
	c.applyResourceLimits(cgroupPath)

	c.isolated[pid] = cgroupPath
	c.logger.Info("cgroup: process isolated",
		zap.Uint32("pid", pid),
		zap.String("cgroup", cgroupPath),
		zap.Int("total_isolated", len(c.isolated)))

	return cgroupPath, nil
}

// Release removes a process from isolation.
func (c *CgroupIsolator) Release(ctx context.Context, pid uint32) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.releaseLocked(ctx, pid)
}

// releaseLocked is the internal implementation of Release.
// Caller must hold c.mu.
func (c *CgroupIsolator) releaseLocked(ctx context.Context, pid uint32) error {
	cgroupPath, exists := c.isolated[pid]
	if !exists {
		return nil // Not isolated
	}

	c.logger.Debug("cgroup: releasing process", zap.Uint32("pid", pid))

	// Move process back to root cgroup
	rootProcsPath := filepath.Join(c.cfg.Root, "cgroup.procs")
	if err := os.WriteFile(rootProcsPath, []byte(strconv.Itoa(int(pid))), 0644); err != nil {
		// Process might have exited, non-fatal
		c.logger.Debug("cgroup: failed to move process to root (might have exited)",
			zap.Uint32("pid", pid),
			zap.Error(err))
	}

	// Remove cgroup directory
	if err := os.Remove(cgroupPath); err != nil && !os.IsNotExist(err) {
		c.logger.Warn("cgroup: failed to remove cgroup directory",
			zap.String("path", cgroupPath),
			zap.Error(err))
	}

	delete(c.isolated, pid)
	c.logger.Info("cgroup: process released",
		zap.Uint32("pid", pid),
		zap.Int("total_isolated", len(c.isolated)))

	return nil
}

// applyResourceLimits applies resource limits to an isolated cgroup.
// This provides defense in depth against resource exhaustion attacks.
func (c *CgroupIsolator) applyResourceLimits(cgroupPath string) {
	// Memory limit: 256 MiB
	memoryMaxPath := filepath.Join(cgroupPath, "memory.max")
	if err := os.WriteFile(memoryMaxPath, []byte("268435456"), 0644); err != nil {
		c.logger.Debug("cgroup: failed to set memory limit",
			zap.String("path", memoryMaxPath),
			zap.Error(err))
	}

	// CPU limit: 10% of one core
	cpuMaxPath := filepath.Join(cgroupPath, "cpu.max")
	if err := os.WriteFile(cpuMaxPath, []byte("10000 100000"), 0644); err != nil {
		c.logger.Debug("cgroup: failed to set CPU limit",
			zap.String("path", cpuMaxPath),
			zap.Error(err))
	}

	// PID limit: 100 processes
	pidsMaxPath := filepath.Join(cgroupPath, "pids.max")
	if err := os.WriteFile(pidsMaxPath, []byte("100"), 0644); err != nil {
		c.logger.Debug("cgroup: failed to set pids limit",
			zap.String("path", pidsMaxPath),
			zap.Error(err))
	}
}

// GetCgroupID returns the cgroup ID for a cgroup path.
// The cgroup ID is used by nftables for cgroup-based matching.
//
// Note: This requires reading from /proc/<pid>/cgroup or using
// the name_to_handle_at syscall to get the cgroup inode number.
func (c *CgroupIsolator) GetCgroupID(cgroupPath string) (uint32, error) {
	// PLACEHOLDER: Real implementation would:
	// 1. Read /proc/<pid>/cgroup to find the cgroup path
	// 2. Use name_to_handle_at syscall to get the file handle
	// 3. Extract the inode number (cgroup ID) from the handle
	//
	// Example:
	// handle, _, err := unix.NameToHandleAt(unix.AT_FDCWD, cgroupPath, 0)
	// if err != nil {
	//     return 0, err
	// }
	// return uint32(handle.Ino), nil

	// For now, return a placeholder
	return 0, fmt.Errorf("cgroup: GetCgroupID not implemented")
}

// GetIsolatedPIDs returns a list of all isolated PIDs.
func (c *CgroupIsolator) GetIsolatedPIDs() []uint32 {
	c.mu.Lock()
	defer c.mu.Unlock()

	pids := make([]uint32, 0, len(c.isolated))
	for pid := range c.isolated {
		pids = append(pids, pid)
	}
	return pids
}

// GetCount returns the number of isolated processes.
func (c *CgroupIsolator) GetCount() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return len(c.isolated)
}

// GetPath returns the cgroup path for an isolated PID.
func (c *CgroupIsolator) GetPath(pid uint32) (string, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()

	path, exists := c.isolated[pid]
	return path, exists
}
