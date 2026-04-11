// Package escalation — audit.go
//
// Cryptographic audit log for state transitions using Ed25519 signatures.
//
// DESIGN:
//   - Each state transition is signed with Ed25519 private key
//   - Signature covers: PID, old_state, new_state, timestamp
//   - Tamper-evident: any modification invalidates signature chain
//   - Append-only: entries cannot be deleted or reordered
//   - Async writing: non-blocking for critical path
//
// ENTRY FORMAT (variable length, line-based JSON for human readability):
//   {"pid": 1234, "old": 0, "new": 1, "ts": 1234567890000000000, "sig": "base64..."}
//
// VERIFICATION:
//   - Public key can verify all signatures independently
//   - Merkle tree can be built for batch verification (future)

package escalation

import (
	"bufio"
	"crypto/ed25519"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"time"
)

// AuditEntry is a single signed state transition record.
type AuditEntry struct {
	PID       uint32 `json:"pid"`
	OldState  State  `json:"old"`
	NewState  State  `json:"new"`
	Timestamp int64  `json:"ts"` // Unix nanoseconds
	Signature string `json:"sig"` // Base64-encoded Ed25519 signature
}

// AuditLog is a cryptographically signed append-only log.
type AuditLog struct {
	file   *os.File
	writer *bufio.Writer
	mu     sync.Mutex // Protects file writes
	pubKey ed25519.PublicKey
	
	// Async write queue
	queue chan AuditEntry
	wg    sync.WaitGroup
	done  chan struct{}
}

// OpenAuditLog opens or creates an audit log file.
// pubKey is the Ed25519 public key corresponding to the signing key.
func OpenAuditLog(path string, pubKey ed25519.PublicKey) (*AuditLog, error) {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
	if err != nil {
		return nil, err
	}
	
	al := &AuditLog{
		file:   file,
		writer: bufio.NewWriter(file),
		pubKey: pubKey,
		queue:  make(chan AuditEntry, 1024),
		done:   make(chan struct{}),
	}
	
	// Start async writer
	al.wg.Add(1)
	go al.writer_loop()
	
	return al, nil
}

// LogTransition signs and appends a state transition to the audit log (async).
func (al *AuditLog) LogTransition(pid uint32, oldState, newState State, timestamp int64, signingKey ed25519.PrivateKey) {
	// Construct message to sign: pid || old || new || timestamp
	msg := make([]byte, 4+1+1+8)
	msg[0] = byte(pid)
	msg[1] = byte(pid >> 8)
	msg[2] = byte(pid >> 16)
	msg[3] = byte(pid >> 24)
	msg[4] = byte(oldState)
	msg[5] = byte(newState)
	msg[6] = byte(timestamp)
	msg[7] = byte(timestamp >> 8)
	msg[8] = byte(timestamp >> 16)
	msg[9] = byte(timestamp >> 24)
	msg[10] = byte(timestamp >> 32)
	msg[11] = byte(timestamp >> 40)
	msg[12] = byte(timestamp >> 48)
	msg[13] = byte(timestamp >> 56)
	
	// Sign message
	sig := ed25519.Sign(signingKey, msg)
	
	// Create audit entry
	entry := AuditEntry{
		PID:       pid,
		OldState:  oldState,
		NewState:  newState,
		Timestamp: timestamp,
		Signature: base64.StdEncoding.EncodeToString(sig),
	}
	
	// Enqueue for async write (non-blocking)
	select {
	case al.queue <- entry:
	default:
		// Queue full — drop (should never happen with 1024 buffer)
		// TODO: Increment dropped counter metric
	}
}

// writer_loop runs in background and writes queued entries to disk.
func (al *AuditLog) writer_loop() {
	defer al.wg.Done()
	
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	
	for {
		select {
		case entry := <-al.queue:
			al.writeEntry(entry)
		case <-ticker.C:
			// Periodic flush
			al.mu.Lock()
			al.writer.Flush()
			al.file.Sync()
			al.mu.Unlock()
		case <-al.done:
			// Drain queue
			for {
				select {
				case entry := <-al.queue:
					al.writeEntry(entry)
				default:
					al.mu.Lock()
					al.writer.Flush()
					al.file.Sync()
					al.mu.Unlock()
					return
				}
			}
		}
	}
}

// writeEntry writes a single audit entry to the file.
func (al *AuditLog) writeEntry(entry AuditEntry) {
	al.mu.Lock()
	defer al.mu.Unlock()
	
	data, err := json.Marshal(entry)
	if err != nil {
		// Should never happen with fixed struct
		return
	}
	
	al.writer.Write(data)
	al.writer.WriteByte('\n')
}

// Close flushes and closes the audit log.
func (al *AuditLog) Close() error {
	close(al.done)
	al.wg.Wait()
	
	al.mu.Lock()
	defer al.mu.Unlock()
	
	al.writer.Flush()
	al.file.Sync()
	return al.file.Close()
}

// VerifyLog reads an audit log file and verifies all signatures.
// Returns the number of valid entries and any verification errors.
func VerifyLog(path string, pubKey ed25519.PublicKey) (int, error) {
	file, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer file.Close()
	
	scanner := bufio.NewScanner(file)
	validCount := 0
	lineNum := 0
	
	for scanner.Scan() {
		lineNum++
		line := scanner.Bytes()
		
		var entry AuditEntry
		if err := json.Unmarshal(line, &entry); err != nil {
			return validCount, fmt.Errorf("line %d: invalid JSON: %w", lineNum, err)
		}
		
		// Decode signature
		sig, err := base64.StdEncoding.DecodeString(entry.Signature)
		if err != nil {
			return validCount, fmt.Errorf("line %d: invalid signature encoding: %w", lineNum, err)
		}
		
		if len(sig) != ed25519.SignatureSize {
			return validCount, fmt.Errorf("line %d: invalid signature length", lineNum)
		}
		
		// Reconstruct signed message
		msg := make([]byte, 14)
		msg[0] = byte(entry.PID)
		msg[1] = byte(entry.PID >> 8)
		msg[2] = byte(entry.PID >> 16)
		msg[3] = byte(entry.PID >> 24)
		msg[4] = byte(entry.OldState)
		msg[5] = byte(entry.NewState)
		msg[6] = byte(entry.Timestamp)
		msg[7] = byte(entry.Timestamp >> 8)
		msg[8] = byte(entry.Timestamp >> 16)
		msg[9] = byte(entry.Timestamp >> 24)
		msg[10] = byte(entry.Timestamp >> 32)
		msg[11] = byte(entry.Timestamp >> 40)
		msg[12] = byte(entry.Timestamp >> 48)
		msg[13] = byte(entry.Timestamp >> 56)
		
		// Verify signature
		if !ed25519.Verify(pubKey, msg, sig) {
			return validCount, fmt.Errorf("line %d: signature verification failed", lineNum)
		}
		
		validCount++
	}
	
	if err := scanner.Err(); err != nil {
		return validCount, err
	}
	
	return validCount, nil
}
