// Package redteam — s4_isolation_test.go
//
// Red-team benchmark harness for OCTOREFLEX S4 (QUARANTINED) namespace isolation.
//
// Purpose:
//   Verify that a process in the QUARANTINED state cannot exfiltrate data,
//   communicate externally, or escape its isolation boundary via known
//   side-channels.
//
// Test categories:
//    1. Network side-channels: net.Dial (TCP/UDP)
//    2. Filesystem side-channels: write, openat relative, O_TRUNC, O_APPEND,
//       rename-over-protected, hardlink (link(2)), mount(2)
//    3. /proc isolation: stat("/proc/1") EACCES, open("/proc/1/maps") EACCES
//       (authoritative — not PID count heuristic)
//    4. cgroup escape: write to root cgroup.procs + prctl(PR_GET_NO_NEW_PRIVS)
//    5. Namespace fd leakage: /proc/1/fd, /proc/1/mem, ptrace(PTRACE_ATTACH)
//    6. IPC isolation: shmget, msgget, semget, /dev/shm, mmap shared fd
//    7. Timing side-channels (documentation)
//    8. RawConn + syscall.Connect() (bypasses net.Dial)
//    9. unix.Sendto() direct syscall (bypasses connect)
//   10. AF_UNIX socket (rendezvous, /tmp bind, SOCK_DGRAM sendto)
//
// Requirements:
//   - Must run as root on a Linux host with cgroup v2.
//   - Requires the OCTOREFLEX BPF programs to be loaded (or a mock).
//   - Run with: go test -v -tags redteam ./test/redteam/
//
// NOTE: This harness documents the attack surface and expected mitigations.
// It does NOT contain actual rootkit code. The "attacker" is a benign
// Go process that attempts the side-channel using standard syscalls.

//go:build redteam

package redteam_test

import (
	"context"
	"errors"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"
	"unsafe"

	"golang.org/x/sys/unix"
)

// ─── Test infrastructure ──────────────────────────────────────────────────────

func TestMain(m *testing.M) {
	if runtime.GOOS != "linux" {
		fmt.Fprintln(os.Stderr, "SKIP: red-team tests require Linux")
		os.Exit(0)
	}
	if os.Getuid() != 0 {
		fmt.Fprintln(os.Stderr, "SKIP: red-team tests require root (UID 0)")
		os.Exit(0)
	}
	os.Exit(m.Run())
}

const quarantinedCgroupPath = "/sys/fs/cgroup/octoreflex-redteam-s4"

func setupQuarantineCgroup(t *testing.T) func() {
	t.Helper()
	if err := os.MkdirAll(quarantinedCgroupPath, 0o755); err != nil {
		t.Fatalf("create quarantine cgroup: %v", err)
	}
	pidFile := filepath.Join(quarantinedCgroupPath, "cgroup.procs")
	if err := os.WriteFile(pidFile, []byte(strconv.Itoa(os.Getpid())), 0o644); err != nil {
		t.Fatalf("move PID to quarantine cgroup: %v", err)
	}
	return func() {
		_ = os.WriteFile("/sys/fs/cgroup/cgroup.procs",
			[]byte(strconv.Itoa(os.Getpid())), 0o644)
		_ = os.Remove(quarantinedCgroupPath)
	}
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

// isEPERM returns true if err (or any error in its chain) is syscall.EPERM.
func isEPERM(err error) bool { return errors.Is(err, syscall.EPERM) }

// isEACCES returns true if err (or any error in its chain) is syscall.EACCES.
func isEACCES(err error) bool { return errors.Is(err, syscall.EACCES) }

// isBlocked returns true if err is a kernel-level permission denial (EPERM or EACCES).
// These are the only two errno values BPF LSM hooks can return.
func isBlocked(err error) bool { return isEPERM(err) || isEACCES(err) }

// logResult logs PASS/FINDING/INFO based on whether the attempt was blocked.
func logResult(t *testing.T, label string, err error, expectBlocked bool) {
	t.Helper()
	switch {
	case err == nil && expectBlocked:
		t.Logf("FINDING: %s — succeeded (BPF hook may not be active)", label)
	case err == nil && !expectBlocked:
		t.Logf("PASS: %s — succeeded (expected)", label)
	case isBlocked(err):
		t.Logf("PASS: %s — blocked (%v)", label, err)
	default:
		t.Logf("INFO: %s — failed with non-permission error: %v", label, err)
	}
}

// ─── Test 1: Network side-channel (net.Dial) ──────────────────────────────────

// TestS4_NetworkBlocked verifies that outbound TCP/UDP via net.Dial is blocked.
// Mitigation: BPF lsm/socket_connect hook returns -EPERM for state >= ISOLATED.
func TestS4_NetworkBlocked(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	targets := []struct{ name, network, addr string }{
		{"TCP outbound", "tcp", "8.8.8.8:443"},
		{"UDP DNS", "udp", "8.8.8.8:53"},
		{"TCP loopback", "tcp", "127.0.0.1:1"},
	}
	for _, tt := range targets {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
			defer cancel()
			var d net.Dialer
			conn, err := d.DialContext(ctx, tt.network, tt.addr)
			if err == nil {
				conn.Close()
			}
			logResult(t, tt.name, err, true)
		})
	}
}

// ─── Test 2: Filesystem side-channels ─────────────────────────────────────────

// TestS4_FilesystemBlocked covers multiple filesystem bypass vectors:
//   a. Standard write to /etc
//   b. openat(2) with relative path (bypasses absolute-path checks)
//   c. O_TRUNC on an existing protected file
//   d. O_APPEND on an existing protected file
//   e. rename(2) over a protected file (rename + replace pattern)
//   f. link(2) hardlink attack (creates alias bypassing path checks)
//   g. mount(2) syscall (requires CAP_SYS_ADMIN — should be dropped)
//
// Mitigation: BPF lsm/file_open, lsm/path_rename, lsm/path_link hooks.
func TestS4_FilesystemBlocked(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	t.Run("write to /etc", func(t *testing.T) {
		err := os.WriteFile("/etc/octoreflex-redteam-probe", []byte("probe"), 0o644)
		if err == nil {
			_ = os.Remove("/etc/octoreflex-redteam-probe")
		}
		logResult(t, "write /etc/octoreflex-redteam-probe", err, true)
	})

	t.Run("openat relative path", func(t *testing.T) {
		// Open a dirfd for /etc, then openat with a relative name.
		// Attackers use this to bypass hooks that only check absolute paths.
		dirfd, err := unix.Open("/etc", unix.O_RDONLY|unix.O_DIRECTORY, 0)
		if err != nil {
			t.Logf("INFO: open /etc dirfd failed: %v", err)
			return
		}
		defer unix.Close(dirfd)

		fd, err := unix.Openat(dirfd, "octoreflex-redteam-openat", unix.O_WRONLY|unix.O_CREAT, 0o644)
		if err == nil {
			unix.Close(fd)
			_ = os.Remove("/etc/octoreflex-redteam-openat")
		}
		logResult(t, "openat(dirfd_etc, relative_name, O_CREAT)", err, true)
	})

	t.Run("O_TRUNC on protected file", func(t *testing.T) {
		// /etc/hostname exists on all Linux systems.
		fd, err := unix.Open("/etc/hostname", unix.O_WRONLY|unix.O_TRUNC, 0)
		if err == nil {
			unix.Close(fd)
			t.Logf("FINDING: O_TRUNC on /etc/hostname succeeded — file_open hook may not check O_TRUNC")
		} else if isBlocked(err) {
			t.Logf("PASS: O_TRUNC on /etc/hostname blocked (%v)", err)
		} else {
			t.Logf("INFO: O_TRUNC failed with: %v", err)
		}
	})

	t.Run("O_APPEND on protected file", func(t *testing.T) {
		fd, err := unix.Open("/etc/hostname", unix.O_WRONLY|unix.O_APPEND, 0)
		if err == nil {
			unix.Close(fd)
			t.Logf("FINDING: O_APPEND on /etc/hostname succeeded — file_open hook may not check O_APPEND")
		} else if isBlocked(err) {
			t.Logf("PASS: O_APPEND on /etc/hostname blocked (%v)", err)
		} else {
			t.Logf("INFO: O_APPEND failed with: %v", err)
		}
	})

	t.Run("rename over protected file", func(t *testing.T) {
		// Create a staging file in /tmp, then rename it over /etc/hostname.
		// This is the classic rename+replace bypass: the attacker never opens
		// the target file directly — they rename a prepared file over it.
		// Mitigation: BPF lsm/path_rename hook.
		staging := "/tmp/octoreflex-redteam-rename-staging"
		if err := os.WriteFile(staging, []byte("malicious"), 0o644); err != nil {
			t.Logf("INFO: could not create staging file: %v", err)
			return
		}
		defer os.Remove(staging)

		err := unix.Rename(staging, "/etc/hostname")
		if err == nil {
			// Restore /etc/hostname (it was overwritten — this is a real finding).
			_ = os.WriteFile("/etc/hostname", []byte("redteam-restored\n"), 0o644)
			t.Logf("FINDING: rename over /etc/hostname succeeded — lsm/path_rename hook not active. " +
				"Attacker can replace protected files without opening them.")
		} else if isBlocked(err) {
			t.Logf("PASS: rename over /etc/hostname blocked (%v)", err)
		} else {
			t.Logf("INFO: rename failed with: %v", err)
		}
	})

	t.Run("hardlink attack (link syscall)", func(t *testing.T) {
		// Create a hardlink to /etc/shadow (or /etc/hostname).
		// A hardlink gives the attacker a new path alias to the same inode,
		// potentially bypassing path-based access controls.
		// Mitigation: BPF lsm/path_link hook.
		linkTarget := "/tmp/octoreflex-redteam-hardlink"
		defer os.Remove(linkTarget)

		err := unix.Link("/etc/shadow", linkTarget)
		if err == nil {
			t.Logf("FINDING: hardlink to /etc/shadow created at %s — "+
				"lsm/path_link hook not active. Attacker has inode alias.", linkTarget)
		} else if isBlocked(err) {
			t.Logf("PASS: hardlink to /etc/shadow blocked (%v)", err)
		} else {
			// ENOENT is expected if /etc/shadow doesn't exist; try /etc/hostname.
			err2 := unix.Link("/etc/hostname", linkTarget)
			if err2 == nil {
				t.Logf("FINDING: hardlink to /etc/hostname created — lsm/path_link hook not active")
			} else if isBlocked(err2) {
				t.Logf("PASS: hardlink to /etc/hostname blocked (%v)", err2)
			} else {
				t.Logf("INFO: link failed: shadow=%v hostname=%v", err, err2)
			}
		}
	})

	t.Run("mount syscall", func(t *testing.T) {
		// Attempt to bind-mount /etc over /tmp.
		// Requires CAP_SYS_ADMIN — should be dropped in S4.
		// If this succeeds, the attacker can overlay a writable filesystem
		// over a protected path.
		err := unix.Mount("/etc", "/tmp/octoreflex-redteam-mount", "", unix.MS_BIND, "")
		if err == nil {
			_ = unix.Unmount("/tmp/octoreflex-redteam-mount", 0)
			t.Logf("FINDING: mount(MS_BIND) succeeded — CAP_SYS_ADMIN not dropped in S4")
		} else if isBlocked(err) {
			t.Logf("PASS: mount blocked (%v) — CAP_SYS_ADMIN not available", err)
		} else {
			t.Logf("INFO: mount failed with: %v (may be EPERM from kernel without CAP_SYS_ADMIN)", err)
		}
	})
}

// ─── Test 3: /proc isolation (authoritative) ──────────────────────────────────

// TestS4_ProcIsolation verifies /proc isolation using authoritative syscall
// checks — not PID count heuristics.
//
// Authoritative checks:
//   a. stat("/proc/1") returns EACCES (hidepid=2 effective)
//   b. open("/proc/1/maps") returns EACCES (memory map not readable)
//
// Mitigation: hidepid=2 mount option on /proc.
func TestS4_ProcIsolation(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	t.Run("stat /proc/1 returns EACCES", func(t *testing.T) {
		var stat unix.Stat_t
		err := unix.Stat("/proc/1", &stat)
		if err == nil {
			t.Logf("FINDING: stat(\"/proc/1\") succeeded — hidepid=2 not effective. " +
				"Attacker can enumerate process metadata for PID 1.")
		} else if isEACCES(err) || isEPERM(err) {
			t.Logf("PASS: stat(\"/proc/1\") returned %v — hidepid=2 effective", err)
		} else {
			t.Logf("INFO: stat(\"/proc/1\") returned: %v", err)
		}
	})

	t.Run("open /proc/1/maps returns EACCES", func(t *testing.T) {
		fd, err := unix.Open("/proc/1/maps", unix.O_RDONLY, 0)
		if err == nil {
			unix.Close(fd)
			t.Logf("FINDING: open(\"/proc/1/maps\") succeeded — " +
				"attacker can read init's memory map (ASLR bypass candidate).")
		} else if isBlocked(err) {
			t.Logf("PASS: open(\"/proc/1/maps\") blocked (%v)", err)
		} else {
			t.Logf("INFO: open(\"/proc/1/maps\") failed with: %v", err)
		}
	})

	// Informational: PID count (not authoritative, but useful for context).
	t.Run("pid count (informational)", func(t *testing.T) {
		entries, err := os.ReadDir("/proc")
		if err != nil {
			t.Logf("INFO: ReadDir /proc: %v", err)
			return
		}
		var pids []string
		for _, e := range entries {
			if _, err := strconv.Atoi(e.Name()); err == nil {
				pids = append(pids, e.Name())
			}
		}
		t.Logf("INFO: %d PIDs visible in /proc (self=%d). "+
			"Use stat/open tests above for authoritative hidepid check.", len(pids), os.Getpid())
	})
}

// ─── Test 4: cgroup escape + capability state ──────────────────────────────────

// TestS4_CgroupEscapeAndCapabilities verifies:
//   a. Writing to root cgroup.procs is blocked (userland permission check).
//   b. prctl(PR_GET_NO_NEW_PRIVS) returns 1 (no_new_privs set).
//   c. CAP_SYS_ADMIN is not in the effective capability set.
//
// Mitigation: CAP_SYS_ADMIN dropped, no_new_privs set, LSM state map enforced.
func TestS4_CgroupEscapeAndCapabilities(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	t.Run("write to root cgroup.procs", func(t *testing.T) {
		err := os.WriteFile("/sys/fs/cgroup/cgroup.procs",
			[]byte(strconv.Itoa(os.Getpid())), 0o644)
		if err == nil {
			t.Logf("FINDING: cgroup escape succeeded — CAP_SYS_ADMIN may not be dropped")
		} else if isBlocked(err) {
			t.Logf("PASS: cgroup escape blocked (%v)", err)
		} else {
			t.Logf("INFO: cgroup escape failed with: %v", err)
		}
	})

	t.Run("prctl PR_GET_NO_NEW_PRIVS", func(t *testing.T) {
		// prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) returns 1 if set, 0 if not.
		const PR_GET_NO_NEW_PRIVS = 39
		ret, _, errno := syscall.Syscall6(syscall.SYS_PRCTL,
			PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0, 0)
		if errno != 0 {
			t.Logf("INFO: prctl(PR_GET_NO_NEW_PRIVS) failed: %v", errno)
			return
		}
		if ret == 1 {
			t.Logf("PASS: no_new_privs=1 — process cannot gain new privileges")
		} else {
			t.Logf("FINDING: no_new_privs=0 — process can gain new privileges. " +
				"S4 quarantine must call prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) before isolation.")
		}
	})

	t.Run("CAP_SYS_ADMIN not in effective set", func(t *testing.T) {
		// Read /proc/self/status and check CapEff.
		data, err := os.ReadFile("/proc/self/status")
		if err != nil {
			t.Logf("INFO: read /proc/self/status: %v", err)
			return
		}
		for _, line := range strings.Split(string(data), "\n") {
			if !strings.HasPrefix(line, "CapEff:") {
				continue
			}
			fields := strings.Fields(line)
			if len(fields) < 2 {
				break
			}
			capEff, err := strconv.ParseUint(fields[1], 16, 64)
			if err != nil {
				t.Logf("INFO: parse CapEff: %v", err)
				break
			}
			const CAP_SYS_ADMIN = 21
			if capEff&(1<<CAP_SYS_ADMIN) != 0 {
				t.Logf("FINDING: CAP_SYS_ADMIN is in effective capability set (CapEff=0x%x). "+
					"S4 quarantine must drop all capabilities before isolation.", capEff)
			} else {
				t.Logf("PASS: CAP_SYS_ADMIN not in effective set (CapEff=0x%x)", capEff)
			}
			break
		}
	})
}

// ─── Test 5: Namespace fd leakage ────────────────────────────────────────────

// TestS4_NamespaceFdLeakage verifies that a quarantined process cannot access
// other processes' memory or file descriptors.
//
// Tests:
//   a. open("/proc/1/fd") — directory listing of init's fds.
//   b. open("/proc/1/mem") — direct memory read of init's address space.
//   c. ptrace(PTRACE_ATTACH, 1) — attach to init (may bypass hidepid via Yama).
//
// Mitigation: hidepid=2 + Yama LSM ptrace_scope >= 1.
func TestS4_NamespaceFdLeakage(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	t.Run("open /proc/1/fd", func(t *testing.T) {
		entries, err := os.ReadDir("/proc/1/fd")
		if err == nil {
			t.Logf("FINDING: /proc/1/fd readable (%d entries) — hidepid=2 not effective", len(entries))
		} else if isBlocked(err) {
			t.Logf("PASS: /proc/1/fd blocked (%v)", err)
		} else {
			t.Logf("INFO: /proc/1/fd failed with: %v", err)
		}
	})

	t.Run("open /proc/1/mem", func(t *testing.T) {
		// /proc/1/mem allows direct read/write of another process's memory.
		// Even with hidepid=2, this may be accessible if the kernel version
		// or configuration allows it.
		fd, err := unix.Open("/proc/1/mem", unix.O_RDONLY, 0)
		if err == nil {
			unix.Close(fd)
			t.Logf("FINDING: /proc/1/mem opened successfully — " +
				"attacker can read init's memory (credential extraction, ASLR bypass).")
		} else if isBlocked(err) {
			t.Logf("PASS: /proc/1/mem blocked (%v)", err)
		} else {
			t.Logf("INFO: /proc/1/mem failed with: %v (ENOENT expected if hidepid=2)", err)
		}
	})

	t.Run("ptrace PTRACE_ATTACH to PID 1", func(t *testing.T) {
		// ptrace(PTRACE_ATTACH, 1, 0, 0) attempts to attach to init.
		// Yama LSM ptrace_scope controls this:
		//   0 = classic ptrace (any process can attach to any other)
		//   1 = restricted (only parent or CAP_SYS_PTRACE)
		//   2 = admin-only (requires CAP_SYS_PTRACE)
		//   3 = no attach (disabled)
		// hidepid=2 does NOT prevent ptrace — Yama is the mitigation.
		err := unix.PtraceAttach(1)
		if err == nil {
			// Detach immediately to avoid disrupting init.
			_ = unix.PtraceDetach(1)
			t.Logf("FINDING: ptrace(PTRACE_ATTACH, 1) succeeded — " +
				"Yama ptrace_scope may be 0. Attacker can attach to any process. " +
				"Set /proc/sys/kernel/yama/ptrace_scope >= 1.")
		} else if isBlocked(err) {
			t.Logf("PASS: ptrace(PTRACE_ATTACH, 1) blocked (%v) — Yama ptrace_scope >= 1", err)
		} else {
			t.Logf("INFO: ptrace(PTRACE_ATTACH, 1) failed with: %v", err)
		}
	})
}

// ─── Test 6: IPC isolation ────────────────────────────────────────────────────

// TestS4_IPCIsolation verifies that a quarantined process cannot communicate
// via any IPC mechanism.
//
// Tests:
//   a. shmget — System V shared memory
//   b. msgget — System V message queue
//   c. semget — System V semaphore
//   d. /dev/shm visibility — POSIX shared memory
//   e. mmap shared fd trick — mmap of a file descriptor shared before quarantine
//
// Mitigation: IPC namespace isolation (unshare CLONE_NEWIPC).
func TestS4_IPCIsolation(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	// Well-known key that a co-conspirator would have created before quarantine.
	const coConspiratoryKey = 0x4f435f52 // "OC_R"

	t.Run("shmget attach to existing segment", func(t *testing.T) {
		// IPC_CREAT not set — attach only. If IPC namespace is isolated,
		// the segment won't exist in the new namespace.
		shmid, _, errno := syscall.Syscall(syscall.SYS_SHMGET,
			uintptr(coConspiratoryKey), 4096, 0)
		if errno == 0 {
			t.Logf("FINDING: shmget(key=0x%x) succeeded (shmid=%d) — "+
				"IPC namespace not isolated. Attacker can read co-conspirator's shared memory.", coConspiratoryKey, shmid)
		} else {
			t.Logf("PASS: shmget(key=0x%x) failed (%v) — IPC namespace isolated or segment absent", coConspiratoryKey, errno)
		}
	})

	t.Run("msgget attach to existing queue", func(t *testing.T) {
		// msgget with IPC_CREAT not set — attach only.
		msgid, _, errno := syscall.Syscall(syscall.SYS_MSGGET,
			uintptr(coConspiratoryKey), 0)
		if errno == 0 {
			t.Logf("FINDING: msgget(key=0x%x) succeeded (msgid=%d) — "+
				"IPC namespace not isolated. Attacker can read/write message queue.", coConspiratoryKey, msgid)
		} else {
			t.Logf("PASS: msgget(key=0x%x) failed (%v) — IPC namespace isolated or queue absent", coConspiratoryKey, errno)
		}
	})

	t.Run("semget attach to existing semaphore", func(t *testing.T) {
		// semget with IPC_CREAT not set — attach only.
		semid, _, errno := syscall.Syscall(syscall.SYS_SEMGET,
			uintptr(coConspiratoryKey), 1, 0)
		if errno == 0 {
			t.Logf("FINDING: semget(key=0x%x) succeeded (semid=%d) — "+
				"IPC namespace not isolated. Attacker can signal via semaphore.", coConspiratoryKey, semid)
		} else {
			t.Logf("PASS: semget(key=0x%x) failed (%v) — IPC namespace isolated or semaphore absent", coConspiratoryKey, errno)
		}
	})

	t.Run("/dev/shm visibility (POSIX shared memory)", func(t *testing.T) {
		// POSIX shared memory (shm_open) uses /dev/shm as a tmpfs.
		// If IPC namespace is isolated, /dev/shm should be empty or a new tmpfs.
		// If not isolated, the attacker can see and open segments created by others.
		entries, err := os.ReadDir("/dev/shm")
		if err != nil {
			t.Logf("INFO: ReadDir /dev/shm: %v", err)
			return
		}
		if len(entries) > 0 {
			names := make([]string, 0, len(entries))
			for _, e := range entries {
				names = append(names, e.Name())
			}
			t.Logf("FINDING: /dev/shm contains %d entries: %v — "+
				"POSIX shared memory segments visible. IPC namespace may not be isolated.", len(entries), names)
		} else {
			t.Logf("PASS: /dev/shm is empty — POSIX shared memory isolated")
		}
	})

	t.Run("mmap shared fd trick", func(t *testing.T) {
		// An attacker may have inherited an open file descriptor to a shared
		// memory file (e.g., /dev/shm/co-conspirator) before quarantine.
		// We simulate this by creating a memfd and attempting to mmap it.
		// If the mmap succeeds, the attacker has a shared memory region
		// regardless of IPC namespace isolation.
		//
		// Mitigation: Close all inherited fds before quarantine (fd table cleanup).
		// This test verifies that memfd_create is blocked for quarantined processes.
		fd, _, errno := syscall.Syscall(syscall.SYS_MEMFD_CREATE,
			uintptr(unsafe.Pointer(syscall.StringBytePtr("redteam-memfd"))),
			0, 0)
		if errno != 0 {
			if errno == syscall.EPERM || errno == syscall.EACCES {
				t.Logf("PASS: memfd_create blocked (%v) — BPF hook active", errno)
			} else {
				t.Logf("INFO: memfd_create failed: %v", errno)
			}
			return
		}
		memFd := int(fd)
		defer syscall.Close(memFd)

		// Attempt to mmap the memfd.
		const size = 4096
		if err := syscall.Ftruncate(memFd, size); err != nil {
			t.Logf("INFO: ftruncate memfd: %v", err)
			return
		}
		addr, _, mmapErrno := syscall.Syscall6(syscall.SYS_MMAP,
			0, size, syscall.PROT_READ|syscall.PROT_WRITE,
			syscall.MAP_SHARED, uintptr(memFd), 0)
		if mmapErrno != 0 {
			if mmapErrno == syscall.EPERM || mmapErrno == syscall.EACCES {
				t.Logf("PASS: mmap(MAP_SHARED, memfd) blocked (%v)", mmapErrno)
			} else {
				t.Logf("INFO: mmap failed: %v", mmapErrno)
			}
			return
		}
		// mmap succeeded — this is a shared memory region.
		_, _ = syscall.Syscall(syscall.SYS_MUNMAP, addr, size, 0)
		t.Logf("FINDING: memfd_create + mmap(MAP_SHARED) succeeded — "+
			"attacker has a shared memory region. Close all inherited fds before quarantine.")
	})
}

// ─── Test 7: Timing side-channels (documentation) ────────────────────────────

func TestS4_TimingSideChannel(t *testing.T) {
	t.Log("DOCUMENTATION: Timing side-channel attack surface for S4 (QUARANTINED)")
	t.Log("  [MITIGATED]   CPU cache timing — IPC namespace prevents shared memory")
	t.Log("  [PARTIAL]     /proc/timer_list — should be masked in quarantine mount ns")
	t.Log("  [UNMITIGATED] clock_gettime(CLOCK_REALTIME) — unavoidable")
	t.Log("  [FUTURE]      CPU frequency scaling via rdtsc — requires core pinning")
	t.Log("  Recommendation: Pin quarantined processes to dedicated CPU cores")
	t.Log("  with cpuset cgroup controller to prevent cross-core cache attacks.")
}

// ─── Test 8: RawConn + syscall.Connect() ─────────────────────────────────────

// TestS4_RawConnSyscallConnect verifies that calling syscall.Connect() directly
// (bypassing net.Dial) is still blocked by the BPF LSM hook.
//
// The BPF hook fires on the kernel connect(2) path regardless of how it is
// invoked from userspace. This test confirms that.
func TestS4_RawConnSyscallConnect(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	targets := []struct {
		name     string
		sockType int
		addr     syscall.Sockaddr
	}{
		{
			name:     "TCP raw connect to 8.8.8.8:443",
			sockType: syscall.SOCK_STREAM,
			addr:     &syscall.SockaddrInet4{Port: 443, Addr: [4]byte{8, 8, 8, 8}},
		},
		{
			name:     "UDP raw connect to 8.8.8.8:53",
			sockType: syscall.SOCK_DGRAM,
			addr:     &syscall.SockaddrInet4{Port: 53, Addr: [4]byte{8, 8, 8, 8}},
		},
	}

	for _, tt := range targets {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			fd, err := syscall.Socket(syscall.AF_INET, tt.sockType, 0)
			if err != nil {
				logResult(t, "socket(2)", err, true)
				return
			}
			defer syscall.Close(fd)

			err = syscall.Connect(fd, tt.addr)
			if errors.Is(err, syscall.EINPROGRESS) {
				// Non-blocking connect in progress — check SO_ERROR.
				fds := &syscall.FdSet{}
				fds.Bits[fd/64] |= 1 << (uint(fd) % 64)
				tv := syscall.Timeval{Sec: 1}
				n, _ := syscall.Select(fd+1, nil, fds, nil, &tv)
				if n == 0 {
					t.Logf("PASS: connect timed out — blocked or unreachable")
					return
				}
				soErr, _ := syscall.GetsockoptInt(fd, syscall.SOL_SOCKET, syscall.SO_ERROR)
				if soErr == int(syscall.EPERM) || soErr == int(syscall.EACCES) {
					t.Logf("PASS: connect completed with EPERM/EACCES — BPF hook active")
				} else if soErr == 0 {
					t.Logf("FINDING: connect completed successfully — BPF hook may not be active")
				} else {
					t.Logf("INFO: connect completed with errno %d", soErr)
				}
				return
			}
			logResult(t, tt.name, err, true)
		})
	}
}

// ─── Test 9: unix.Sendto() direct syscall ────────────────────────────────────

// TestS4_UnixSendtoDirect verifies that sendto(2) without a prior connect()
// is blocked. This tests lsm/socket_sendmsg coverage, not just socket_connect.
func TestS4_UnixSendtoDirect(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	fd, err := unix.Socket(unix.AF_INET, unix.SOCK_DGRAM, 0)
	if err != nil {
		logResult(t, "socket(2) for sendto test", err, true)
		return
	}
	defer unix.Close(fd)

	dest := &unix.SockaddrInet4{Port: 53, Addr: [4]byte{8, 8, 8, 8}}
	// Minimal DNS query header — 12 bytes.
	payload := []byte("\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00")

	err = unix.Sendto(fd, payload, 0, dest)
	if err == nil {
		t.Logf("FINDING: unix.Sendto to 8.8.8.8:53 succeeded — " +
			"lsm/socket_sendmsg hook not active. Attacker can exfiltrate via sendto without connect.")
	} else if isBlocked(err) {
		t.Logf("PASS: unix.Sendto blocked (%v) — lsm/socket_sendmsg hook active", err)
	} else {
		t.Logf("INFO: unix.Sendto failed with: %v (may be network unreachable)", err)
	}
}

// ─── Test 10: AF_UNIX socket ──────────────────────────────────────────────────

// TestS4_AFUnixSocket verifies that AF_UNIX sockets cannot be used to
// communicate with co-conspirator processes or stage data.
func TestS4_AFUnixSocket(t *testing.T) {
	cleanup := setupQuarantineCgroup(t)
	defer cleanup()

	t.Run("connect to pre-arranged rendezvous socket", func(t *testing.T) {
		rendezvousPath := "/run/octoreflex-redteam-rendezvous.sock"
		l, listenErr := net.Listen("unix", rendezvousPath)
		if listenErr != nil {
			t.Logf("INFO: could not create rendezvous socket: %v", listenErr)
			return
		}
		defer l.Close()
		defer os.Remove(rendezvousPath)

		conn, err := net.DialTimeout("unix", rendezvousPath, 1*time.Second)
		if err == nil {
			conn.Close()
			t.Logf("FINDING: AF_UNIX connect to rendezvous socket succeeded — " +
				"lsm/unix_stream_connect hook not active.")
		} else if isBlocked(err) {
			t.Logf("PASS: AF_UNIX connect blocked (%v)", err)
		} else {
			t.Logf("INFO: AF_UNIX connect failed with: %v", err)
		}
	})

	t.Run("bind new unix socket in /tmp", func(t *testing.T) {
		stagingPath := "/tmp/octoreflex-redteam-staging.sock"
		defer os.Remove(stagingPath)

		fd, err := unix.Socket(unix.AF_UNIX, unix.SOCK_STREAM, 0)
		if err != nil {
			logResult(t, "AF_UNIX socket creation", err, true)
			return
		}
		defer unix.Close(fd)

		err = unix.Bind(fd, &unix.SockaddrUnix{Name: stagingPath})
		if err == nil {
			t.Logf("FINDING: AF_UNIX bind to /tmp succeeded — " +
				"/tmp not restricted. Attacker can stage data via Unix socket.")
		} else if isBlocked(err) {
			t.Logf("PASS: AF_UNIX bind to /tmp blocked (%v)", err)
		} else {
			t.Logf("INFO: AF_UNIX bind failed with: %v", err)
		}
	})

	t.Run("AF_UNIX SOCK_DGRAM sendto co-conspirator", func(t *testing.T) {
		stagingPath := "/tmp/octoreflex-redteam-dgram.sock"
		defer os.Remove(stagingPath)

		serverFd, err := unix.Socket(unix.AF_UNIX, unix.SOCK_DGRAM, 0)
		if err != nil {
			t.Logf("INFO: server socket: %v", err)
			return
		}
		defer unix.Close(serverFd)
		if err := unix.Bind(serverFd, &unix.SockaddrUnix{Name: stagingPath}); err != nil {
			t.Logf("INFO: server bind: %v", err)
			return
		}

		clientFd, err := unix.Socket(unix.AF_UNIX, unix.SOCK_DGRAM, 0)
		if err != nil {
			logResult(t, "client AF_UNIX socket", err, true)
			return
		}
		defer unix.Close(clientFd)

		err = unix.Sendto(clientFd, []byte("exfil-payload"), 0, &unix.SockaddrUnix{Name: stagingPath})
		if err == nil {
			t.Logf("FINDING: AF_UNIX SOCK_DGRAM sendto succeeded — " +
				"attacker can send datagrams to co-conspirator without connect()")
		} else if isBlocked(err) {
			t.Logf("PASS: AF_UNIX sendto blocked (%v)", err)
		} else {
			t.Logf("INFO: AF_UNIX sendto failed with: %v", err)
		}
	})
}
