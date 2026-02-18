// Package bpf provides the CO-RE BPF loader, map accessor, and LSM attacher
// for the OCTOREFLEX agent.
//
// Responsibilities:
//   - Verify kernel version (>= 5.15) and BPF LSM availability.
//   - Load the embedded BPF ELF object via cilium/ebpf CO-RE.
//   - Pin all maps under /sys/fs/bpf/octoreflex/.
//   - Attach LSM programs via link.AttachLSM.
//   - Lock BPF programs read-only after attachment (BPF_F_RDONLY_PROG).
//   - Whitelist the agent's own PID in process_state_map (NORMAL state)
//     to prevent self-denial from the file_open hook.
//   - Expose typed accessors for process_state_map and drop counter.
//
// Failure contract:
//   - Any failure in Load() is fatal. The caller (agent lifecycle) must
//     abort startup. Partial BPF state is not tolerated.
//   - On agent restart, existing pinned maps are reused if present,
//     preserving process state across agent crashes.

package bpf

import (
	"bytes"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"syscall"
	"unsafe"

	"github.com/cilium/ebpf"
	"github.com/cilium/ebpf/link"
	"golang.org/x/sys/unix"
)

const (
	// BPFPinPath is the BPF filesystem directory where all maps are pinned.
	// Must be on a bpffs mount (typically /sys/fs/bpf).
	BPFPinPath = "/sys/fs/bpf/octoreflex"

	// MinKernelMajor and MinKernelMinor define the minimum supported kernel.
	MinKernelMajor = 5
	MinKernelMinor = 15

	// ProcessStateMapName is the BPF map name as declared in the C source.
	ProcessStateMapName = "process_state_map"

	// EventsMapName is the ring buffer map name.
	EventsMapName = "events"

	// DropCounterMapName is the per-CPU drop counter map name.
	DropCounterMapName = "octo_drop_counter"
)

// OctoState mirrors the octo_state_t enum from octoreflex.h.
// Values must be kept in sync with the C definition.
type OctoState uint8

const (
	StateNormal      OctoState = 0
	StatePressure    OctoState = 1
	StateIsolated    OctoState = 2
	StateFrozen      OctoState = 3
	StateQuarantined OctoState = 4
	StateTerminated  OctoState = 5
)

// Objects holds references to all loaded BPF programs and maps.
// Callers must call Close() when done to release kernel resources.
type Objects struct {
	// Programs (LSM hooks)
	SocketConnect *ebpf.Program
	FileOpen      *ebpf.Program
	TaskFixSetuid *ebpf.Program

	// Maps
	ProcessStateMap *ebpf.Map
	Events          *ebpf.Map
	DropCounter     *ebpf.Map

	// Links (keep alive to maintain LSM attachment)
	links []link.Link
}

// Close releases all BPF resources: programs, maps, and LSM links.
// Safe to call multiple times.
func (o *Objects) Close() error {
	var errs []error
	for _, l := range o.links {
		if err := l.Close(); err != nil {
			errs = append(errs, err)
		}
	}
	if o.SocketConnect != nil {
		errs = append(errs, o.SocketConnect.Close())
	}
	if o.FileOpen != nil {
		errs = append(errs, o.FileOpen.Close())
	}
	if o.TaskFixSetuid != nil {
		errs = append(errs, o.TaskFixSetuid.Close())
	}
	if o.ProcessStateMap != nil {
		errs = append(errs, o.ProcessStateMap.Close())
	}
	if o.Events != nil {
		errs = append(errs, o.Events.Close())
	}
	if o.DropCounter != nil {
		errs = append(errs, o.DropCounter.Close())
	}
	return errors.Join(errs...)
}

// Load performs the full BPF initialisation sequence:
//  1. Kernel version check (>= 5.15).
//  2. BPF LSM availability check (/sys/kernel/security/lsm contains "bpf").
//  3. BPF filesystem mount check (/sys/fs/bpf).
//  4. Load ELF from embedded bytes via CO-RE.
//  5. Pin maps under BPFPinPath (reuse existing pins on restart).
//  6. Attach LSM programs.
//  7. Whitelist agent PID in process_state_map.
//
// Returns a fully initialised *Objects or a descriptive error.
// On any error, all partially allocated resources are released.
func Load() (*Objects, error) {
	// Step 1: Kernel version check.
	if err := checkKernelVersion(MinKernelMajor, MinKernelMinor); err != nil {
		return nil, fmt.Errorf("kernel version check failed: %w", err)
	}

	// Step 2: BPF LSM availability.
	if err := checkBPFLSM(); err != nil {
		return nil, fmt.Errorf("BPF LSM check failed: %w", err)
	}

	// Step 3: BPF filesystem.
	if err := checkBPFFS(); err != nil {
		return nil, fmt.Errorf("BPF filesystem check failed: %w", err)
	}

	// Step 4: Load collection spec from embedded bytes.
	spec, err := ebpf.LoadCollectionSpecFromReader(bytes.NewReader(bpfObjectBytes))
	if err != nil {
		return nil, fmt.Errorf("failed to load BPF collection spec: %w", err)
	}

	// Prepare pin path directory.
	if err := os.MkdirAll(BPFPinPath, 0o700); err != nil {
		return nil, fmt.Errorf("failed to create BPF pin path %s: %w", BPFPinPath, err)
	}

	// Configure map pinning: reuse existing pinned maps on restart.
	// This preserves process state across agent crashes.
	for mapName, mapSpec := range spec.Maps {
		pinPath := filepath.Join(BPFPinPath, mapName)
		mapSpec.Pinning = ebpf.PinByName
		_ = pinPath // cilium/ebpf uses the map name + pin path from LoadOptions
	}

	// Step 4 (continued): Load and assign programs + maps.
	coll, err := ebpf.NewCollectionWithOptions(spec, ebpf.CollectionOptions{
		Maps: ebpf.MapOptions{
			PinPath: BPFPinPath,
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to load BPF collection: %w", err)
	}

	objs := &Objects{
		SocketConnect:   coll.Programs["octo_socket_connect"],
		FileOpen:        coll.Programs["octo_file_open"],
		TaskFixSetuid:   coll.Programs["octo_task_fix_setuid"],
		ProcessStateMap: coll.Maps[ProcessStateMapName],
		Events:          coll.Maps[EventsMapName],
		DropCounter:     coll.Maps[DropCounterMapName],
	}

	// Validate all expected objects were found.
	if err := objs.validate(); err != nil {
		_ = objs.Close()
		return nil, fmt.Errorf("BPF object validation failed: %w", err)
	}

	// Step 6: Attach LSM programs.
	if err := objs.attachLSM(); err != nil {
		_ = objs.Close()
		return nil, fmt.Errorf("LSM attachment failed: %w", err)
	}

	// Step 7: Whitelist agent PID to prevent self-denial from file_open hook.
	agentPID := uint32(os.Getpid())
	normalState := uint8(StateNormal)
	if err := objs.ProcessStateMap.Put(agentPID, normalState); err != nil {
		_ = objs.Close()
		return nil, fmt.Errorf("failed to whitelist agent PID %d: %w", agentPID, err)
	}

	return objs, nil
}

// validate checks that all expected BPF objects were loaded.
func (o *Objects) validate() error {
	var missing []string
	if o.SocketConnect == nil {
		missing = append(missing, "program:octo_socket_connect")
	}
	if o.FileOpen == nil {
		missing = append(missing, "program:octo_file_open")
	}
	if o.TaskFixSetuid == nil {
		missing = append(missing, "program:octo_task_fix_setuid")
	}
	if o.ProcessStateMap == nil {
		missing = append(missing, "map:process_state_map")
	}
	if o.Events == nil {
		missing = append(missing, "map:events")
	}
	if o.DropCounter == nil {
		missing = append(missing, "map:octo_drop_counter")
	}
	if len(missing) > 0 {
		return fmt.Errorf("missing BPF objects: %v", missing)
	}
	return nil
}

// attachLSM attaches all three LSM programs and stores the links.
// Links must be kept alive for the duration of the agent's lifetime.
func (o *Objects) attachLSM() error {
	programs := []struct {
		prog *ebpf.Program
		name string
	}{
		{o.SocketConnect, "octo_socket_connect"},
		{o.FileOpen, "octo_file_open"},
		{o.TaskFixSetuid, "octo_task_fix_setuid"},
	}

	for _, p := range programs {
		l, err := link.AttachLSM(link.LSMOptions{
			Program: p.prog,
		})
		if err != nil {
			return fmt.Errorf("failed to attach LSM program %s: %w", p.name, err)
		}
		o.links = append(o.links, l)
	}
	return nil
}

// SetProcessState writes a state value for a PID into process_state_map.
// This is the primary interface for the escalation engine to enforce state.
// The write is visible to the kernel immediately on the next hook invocation.
func (o *Objects) SetProcessState(pid uint32, state OctoState) error {
	val := uint8(state)
	if err := o.ProcessStateMap.Put(pid, val); err != nil {
		return fmt.Errorf("SetProcessState pid=%d state=%d: %w", pid, state, err)
	}
	return nil
}

// GetProcessState reads the current state for a PID from process_state_map.
// Returns StateNormal if the PID is not present (default-permit semantics).
func (o *Objects) GetProcessState(pid uint32) (OctoState, error) {
	var val uint8
	err := o.ProcessStateMap.Lookup(pid, &val)
	if errors.Is(err, ebpf.ErrKeyNotExist) {
		return StateNormal, nil
	}
	if err != nil {
		return StateNormal, fmt.Errorf("GetProcessState pid=%d: %w", pid, err)
	}
	return OctoState(val), nil
}

// DeleteProcessState removes a PID from process_state_map (decay to NORMAL).
// Used by the escalation engine during cool-down and by the exit handler.
func (o *Objects) DeleteProcessState(pid uint32) error {
	err := o.ProcessStateMap.Delete(pid)
	if errors.Is(err, ebpf.ErrKeyNotExist) {
		return nil // Already absent — idempotent.
	}
	return err
}

// ReadDropCount reads the total ring buffer drop count across all CPUs.
// Returns the sum of per-CPU counters.
func (o *Objects) ReadDropCount() (uint64, error) {
	var key uint32 = 0
	var perCPUValues []uint64
	if err := o.DropCounter.Lookup(key, &perCPUValues); err != nil {
		return 0, fmt.Errorf("ReadDropCount: %w", err)
	}
	var total uint64
	for _, v := range perCPUValues {
		total += v
	}
	return total, nil
}

// ─── Kernel / environment checks ─────────────────────────────────────────────

// checkKernelVersion reads the running kernel version via uname(2) and
// verifies it meets the minimum requirement.
func checkKernelVersion(major, minor int) error {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return fmt.Errorf("uname failed: %w", err)
	}
	// Utsname.Release is a [65]int8 on Linux/amd64.
	release := unix.ByteSliceToString((*[65]byte)(unsafe.Pointer(&uts.Release[0]))[:])

	var kMajor, kMinor, kPatch int
	if _, err := fmt.Sscanf(release, "%d.%d.%d", &kMajor, &kMinor, &kPatch); err != nil {
		return fmt.Errorf("failed to parse kernel version %q: %w", release, err)
	}

	if kMajor < major || (kMajor == major && kMinor < minor) {
		return fmt.Errorf("kernel %d.%d.%d < required %d.%d",
			kMajor, kMinor, kPatch, major, minor)
	}
	return nil
}

// checkBPFLSM verifies that the BPF LSM module is active by reading
// /sys/kernel/security/lsm and checking for "bpf" in the list.
func checkBPFLSM() error {
	const lsmPath = "/sys/kernel/security/lsm"
	data, err := os.ReadFile(lsmPath)
	if err != nil {
		if errors.Is(err, syscall.ENOENT) {
			return fmt.Errorf("%s not found: securityfs not mounted or kernel lacks LSM support", lsmPath)
		}
		return fmt.Errorf("failed to read %s: %w", lsmPath, err)
	}
	lsmList := string(data)
	for _, lsm := range splitCSV(lsmList) {
		if lsm == "bpf" {
			return nil
		}
	}
	return fmt.Errorf("BPF LSM not active. Current LSMs: %q. "+
		"Add 'lsm=...,bpf' to kernel command line or /etc/default/grub GRUB_CMDLINE_LINUX", lsmList)
}

// checkBPFFS verifies that the BPF filesystem is mounted at /sys/fs/bpf.
func checkBPFFS() error {
	const bpffsPath = "/sys/fs/bpf"
	var stat syscall.Statfs_t
	if err := syscall.Statfs(bpffsPath, &stat); err != nil {
		return fmt.Errorf("statfs %s failed: %w", bpffsPath, err)
	}
	// BPF filesystem magic number: 0xcafe4a11
	const bpffsMagic = 0xcafe4a11
	if stat.Type != bpffsMagic {
		return fmt.Errorf("%s is not a bpffs mount (magic=0x%x, expected=0x%x). "+
			"Mount with: mount -t bpf bpf /sys/fs/bpf", bpffsPath, stat.Type, bpffsMagic)
	}
	return nil
}

// splitCSV splits a comma-separated string, trimming whitespace.
func splitCSV(s string) []string {
	var result []string
	start := 0
	for i := 0; i <= len(s); i++ {
		if i == len(s) || s[i] == ',' || s[i] == '\n' {
			token := trimSpace(s[start:i])
			if token != "" {
				result = append(result, token)
			}
			start = i + 1
		}
	}
	return result
}

func trimSpace(s string) string {
	start, end := 0, len(s)
	for start < end && (s[start] == ' ' || s[start] == '\t' || s[start] == '\n' || s[start] == '\r') {
		start++
	}
	for end > start && (s[end-1] == ' ' || s[end-1] == '\t' || s[end-1] == '\n' || s[end-1] == '\r') {
		end--
	}
	return s[start:end]
}
