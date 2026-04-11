// Package iouring provides io_uring integration for ultra-low-latency I/O.
//
// io_uring bypasses traditional syscall overhead by using shared memory rings
// between userspace and kernel, enabling:
//   - Zero-copy I/O operations
//   - Batched syscalls (submit multiple ops in one syscall)
//   - Kernel-side polling (no context switches for fast devices)
//   - ~2-5μs latency vs ~10-15μs for traditional epoll
//
// Architecture:
//   - Submission Queue (SQ): Userspace prepares I/O operations
//   - Completion Queue (CQ): Kernel posts completion events
//   - No intermediate buffering, direct DMA to application memory
//
// Use cases in OctoReflex:
//   - Reading BPF maps (faster than bpf() syscalls)
//   - Writing containment actions to cgroup files
//   - Logging audit events to disk with minimal latency
//
// Requires Linux kernel >= 5.1, optimal performance on >= 5.19.

package iouring

import (
	"errors"
	"fmt"
	"syscall"
	"unsafe"

	"golang.org/x/sys/unix"
)

const (
	// IORING_SETUP_SQPOLL enables kernel-side polling thread.
	// Reduces latency but increases CPU usage.
	IORING_SETUP_SQPOLL = 1 << 1

	// IORING_SETUP_IOPOLL enables polling mode for block devices.
	IORING_SETUP_IOPOLL = 1 << 0

	// IORING_ENTER_GETEVENTS waits for completions.
	IORING_ENTER_GETEVENTS = 1 << 0

	// Max entries for single ring (must be power of 2).
	MaxEntries = 4096
)

// Ring represents an io_uring instance with submission and completion queues.
type Ring struct {
	fd          int           // io_uring file descriptor
	sqEntries   uint32        // Submission queue size
	cqEntries   uint32        // Completion queue size
	sqRingPtr   uintptr       // Mmap'd submission queue ring
	cqRingPtr   uintptr       // Mmap'd completion queue ring
	sqesPtr     uintptr       // Mmap'd submission queue entries
	sqRingSize  uintptr       // Size of SQ mmap
	sqesSize    uintptr       // Size of SQEs mmap  
	cqRingSize  uintptr       // Size of CQ mmap
	sqHead      *uint32       // SQ head pointer
	sqTail      *uint32       // SQ tail pointer
	sqMask      *uint32       // SQ ring mask
	cqHead      *uint32       // CQ head pointer
	cqTail      *uint32       // CQ tail pointer
	cqMask      *uint32       // CQ ring mask
	sqArray     *uint32       // SQ index array
	cqes        *CompletionQueueEntry // CQ entries
	sqes        *SubmissionQueueEntry // SQ entries
}

// SubmissionQueueEntry represents a single I/O operation to submit.
type SubmissionQueueEntry struct {
	Opcode      uint8   // Operation code (read, write, fsync, etc.)
	Flags       uint8   // Operation flags
	IoPrio      uint16  // I/O priority
	Fd          int32   // File descriptor
	Offset      uint64  // File offset or address
	Addr        uint64  // Buffer address
	Len         uint32  // Buffer length
	OpFlags     uint32  // Operation-specific flags
	UserData    uint64  // Application data (returned in completion)
	BufIndex    uint16  // Buffer group ID
	Personality uint16  // Credentials ID
	SpliceFd    int32   // Splice target FD
	Pad         [2]uint64
}

// CompletionQueueEntry represents a completed I/O operation.
type CompletionQueueEntry struct {
	UserData uint64 // Application data from submission
	Res      int32  // Result (bytes transferred or error)
	Flags    uint32 // Completion flags
}

// OpCode constants for common operations.
const (
	IORING_OP_NOP        = 0
	IORING_OP_READV      = 1
	IORING_OP_WRITEV     = 2
	IORING_OP_FSYNC      = 3
	IORING_OP_READ_FIXED = 4
	IORING_OP_WRITE_FIXED = 5
	IORING_OP_POLL_ADD   = 6
	IORING_OP_POLL_REMOVE = 7
	IORING_OP_READ       = 22
	IORING_OP_WRITE      = 23
)

// Setup creates a new io_uring instance.
//
// Parameters:
//   - entries: Number of submission queue entries (power of 2, max 4096)
//   - flags: Setup flags (IORING_SETUP_SQPOLL, etc.)
//
// Returns initialized Ring or error.
func Setup(entries uint32, flags uint32) (*Ring, error) {
	if entries == 0 || entries > MaxEntries {
		return nil, fmt.Errorf("entries must be 1-%d", MaxEntries)
	}
	if entries&(entries-1) != 0 {
		return nil, errors.New("entries must be power of 2")
	}

	// io_uring_setup syscall.
	params := unix.IOUringParams{
		Sq_entries: entries,
		Flags:      flags,
	}

	fd, err := unix.IORingSetup(entries, &params)
	if err != nil {
		return nil, fmt.Errorf("io_uring_setup: %w", err)
	}

	ring := &Ring{
		fd:        fd,
		sqEntries: params.Sq_entries,
		cqEntries: params.Cq_entries,
	}

	// Mmap submission queue ring.
	sqRingSize := uintptr(params.Sq_off.Array) + uintptr(params.Sq_entries)*4
	sqRing, err := unix.Mmap(fd, unix.IORING_OFF_SQ_RING,
		int(sqRingSize), unix.PROT_READ|unix.PROT_WRITE, unix.MAP_SHARED|unix.MAP_POPULATE)
	if err != nil {
		unix.Close(fd)
		return nil, fmt.Errorf("mmap SQ ring: %w", err)
	}
	ring.sqRingPtr = uintptr(unsafe.Pointer(&sqRing[0]))
	ring.sqRingSize = sqRingSize

	// Mmap completion queue ring.
	cqRingSize := uintptr(params.Cq_off.Cqes) + uintptr(params.Cq_entries)*uint32(unsafe.Sizeof(CompletionQueueEntry{}))
	cqRing, err := unix.Mmap(fd, unix.IORING_OFF_CQ_RING,
		int(cqRingSize), unix.PROT_READ|unix.PROT_WRITE, unix.MAP_SHARED|unix.MAP_POPULATE)
	if err != nil {
		unix.Munmap(sqRing)
		unix.Close(fd)
		return nil, fmt.Errorf("mmap CQ ring: %w", err)
	}
	ring.cqRingPtr = uintptr(unsafe.Pointer(&cqRing[0]))
	ring.cqRingSize = cqRingSize

	// Mmap submission queue entries.
	sqesSize := uintptr(params.Sq_entries) * unsafe.Sizeof(SubmissionQueueEntry{})
	sqes, err := unix.Mmap(fd, unix.IORING_OFF_SQES,
		int(sqesSize), unix.PROT_READ|unix.PROT_WRITE, unix.MAP_SHARED|unix.MAP_POPULATE)
	if err != nil {
		unix.Munmap(sqRing)
		unix.Munmap(cqRing)
		unix.Close(fd)
		return nil, fmt.Errorf("mmap SQEs: %w", err)
	}
	ring.sqesPtr = uintptr(unsafe.Pointer(&sqes[0]))
	ring.sqesSize = sqesSize

	// Set up pointers to shared memory structures.
	ring.sqHead = (*uint32)(unsafe.Pointer(ring.sqRingPtr + uintptr(params.Sq_off.Head)))
	ring.sqTail = (*uint32)(unsafe.Pointer(ring.sqRingPtr + uintptr(params.Sq_off.Tail)))
	ring.sqMask = (*uint32)(unsafe.Pointer(ring.sqRingPtr + uintptr(params.Sq_off.Ring_mask)))
	ring.sqArray = (*uint32)(unsafe.Pointer(ring.sqRingPtr + uintptr(params.Sq_off.Array)))

	ring.cqHead = (*uint32)(unsafe.Pointer(ring.cqRingPtr + uintptr(params.Cq_off.Head)))
	ring.cqTail = (*uint32)(unsafe.Pointer(ring.cqRingPtr + uintptr(params.Cq_off.Tail)))
	ring.cqMask = (*uint32)(unsafe.Pointer(ring.cqRingPtr + uintptr(params.Cq_off.Ring_mask)))
	ring.cqes = (*CompletionQueueEntry)(unsafe.Pointer(ring.cqRingPtr + uintptr(params.Cq_off.Cqes)))

	ring.sqes = (*SubmissionQueueEntry)(unsafe.Pointer(ring.sqesPtr))

	return ring, nil
}

// Close releases all resources associated with the ring.
func (r *Ring) Close() error {
	var errs []error

	if r.sqRingPtr != 0 {
		sqRing := unsafe.Slice((*byte)(unsafe.Pointer(r.sqRingPtr)), r.sqRingSize)
		if err := unix.Munmap(sqRing); err != nil {
			errs = append(errs, fmt.Errorf("munmap SQ ring: %w", err))
		}
	}

	if r.cqRingPtr != 0 {
		cqRing := unsafe.Slice((*byte)(unsafe.Pointer(r.cqRingPtr)), r.cqRingSize)
		if err := unix.Munmap(cqRing); err != nil {
			errs = append(errs, fmt.Errorf("munmap CQ ring: %w", err))
		}
	}

	if r.sqesPtr != 0 {
		sqes := unsafe.Slice((*byte)(unsafe.Pointer(r.sqesPtr)), r.sqesSize)
		if err := unix.Munmap(sqes); err != nil {
			errs = append(errs, fmt.Errorf("munmap SQEs: %w", err))
		}
	}

	if r.fd >= 0 {
		if err := unix.Close(r.fd); err != nil {
			errs = append(errs, fmt.Errorf("close io_uring fd: %w", err))
		}
	}

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}

// GetSQE returns the next available submission queue entry.
// Returns nil if the queue is full.
func (r *Ring) GetSQE() *SubmissionQueueEntry {
	tail := *r.sqTail
	head := *r.sqHead
	mask := *r.sqMask

	// Check if queue is full.
	if tail-head >= r.sqEntries {
		return nil
	}

	idx := tail & mask
	sqe := (*SubmissionQueueEntry)(unsafe.Pointer(uintptr(unsafe.Pointer(r.sqes)) + 
		uintptr(idx)*unsafe.Sizeof(SubmissionQueueEntry{})))

	// Clear the entry for reuse.
	*sqe = SubmissionQueueEntry{}

	return sqe
}

// Submit submits all pending SQEs to the kernel.
// Returns the number of SQEs submitted or error.
func (r *Ring) Submit() (int, error) {
	return r.SubmitAndWait(0)
}

// SubmitAndWait submits SQEs and optionally waits for completions.
//
// Parameters:
//   - waitNr: Number of completions to wait for (0 = don't wait)
//
// Returns number of submitted SQEs or error.
func (r *Ring) SubmitAndWait(waitNr uint) (int, error) {
	tail := *r.sqTail
	head := *r.sqHead
	toSubmit := tail - head

	if toSubmit == 0 {
		return 0, nil
	}

	flags := uint32(0)
	if waitNr > 0 {
		flags |= IORING_ENTER_GETEVENTS
	}

	// Update tail pointer to make SQEs visible to kernel.
	*r.sqTail = tail

	// io_uring_enter syscall.
	n, _, errno := syscall.Syscall6(
		unix.SYS_IO_URING_ENTER,
		uintptr(r.fd),
		uintptr(toSubmit),
		uintptr(waitNr),
		uintptr(flags),
		0, 0)

	if errno != 0 {
		return 0, errno
	}

	return int(n), nil
}

// PeekCQE returns the next completion queue entry without consuming it.
// Returns nil if no completions are available.
func (r *Ring) PeekCQE() *CompletionQueueEntry {
	head := *r.cqHead
	tail := *r.cqTail

	if head == tail {
		return nil
	}

	mask := *r.cqMask
	idx := head & mask
	cqe := (*CompletionQueueEntry)(unsafe.Pointer(uintptr(unsafe.Pointer(r.cqes)) +
		uintptr(idx)*unsafe.Sizeof(CompletionQueueEntry{})))

	return cqe
}

// ConsumeCQE marks a completion as consumed, advancing the head pointer.
func (r *Ring) ConsumeCQE() {
	*r.cqHead++
}

// PrepareRead prepares a read operation.
//
// Parameters:
//   - sqe: SQE to populate (from GetSQE)
//   - fd: File descriptor to read from
//   - buf: Buffer to read into
//   - offset: File offset (-1 for current position)
//   - userData: Application data (returned in completion)
func PrepareRead(sqe *SubmissionQueueEntry, fd int, buf []byte, offset int64, userData uint64) {
	sqe.Opcode = IORING_OP_READ
	sqe.Fd = int32(fd)
	sqe.Addr = uint64(uintptr(unsafe.Pointer(&buf[0])))
	sqe.Len = uint32(len(buf))
	sqe.Offset = uint64(offset)
	sqe.UserData = userData
}

// PrepareWrite prepares a write operation.
func PrepareWrite(sqe *SubmissionQueueEntry, fd int, buf []byte, offset int64, userData uint64) {
	sqe.Opcode = IORING_OP_WRITE
	sqe.Fd = int32(fd)
	sqe.Addr = uint64(uintptr(unsafe.Pointer(&buf[0])))
	sqe.Len = uint32(len(buf))
	sqe.Offset = uint64(offset)
	sqe.UserData = userData
}
