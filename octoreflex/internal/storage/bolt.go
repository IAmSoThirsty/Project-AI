// Package storage — bolt.go
//
// BoltDB-backed persistent storage for OCTOREFLEX.
//
// Schema (BoltDB bucket layout):
//
//	/baselines
//	    key:   sha256(binary_path)  [32 bytes hex-encoded = 64 chars]
//	    value: JSON-encoded BaselineRecord
//
//	/ledger
//	    key:   RFC3339Nano timestamp + "_" + pid  [monotonic, sortable]
//	    value: JSON-encoded LedgerEntry
//
//	/meta
//	    key:   "schema_version"
//	    value: "1"
//
// Consistency model:
//   - Single-process, single-writer (BoltDB does not support concurrent writers).
//   - All writes use ACID transactions (bbolt Tx.Commit()).
//   - Reads use read-only transactions (bbolt.View()).
//   - CRC32 integrity check on database open (bbolt built-in).
//
// Retention:
//   - Ledger entries older than RetentionDays are pruned on startup and
//     periodically by the retention goroutine (every 6 hours).
//   - Baselines are never automatically pruned (operator action required).
//
// Failure modes:
//   - BoltDB file corruption: bbolt detects via CRC and returns an error
//     on Open(). The agent logs a fatal event and refuses to start.
//     Recovery: restore from backup at /var/lib/octoreflex/db.bak.
//   - Disk full: bbolt.Update() returns an error. The agent logs the error
//     and continues without persisting (in-memory state preserved).

package storage

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	bolt "go.etcd.io/bbolt"
)

const (
	// DefaultDBPath is the default BoltDB file location.
	DefaultDBPath = "/var/lib/octoreflex/octoreflex.db"

	// SchemaVersion is the current database schema version.
	SchemaVersion = "1"

	// DefaultRetentionDays is the default ledger retention period.
	DefaultRetentionDays = 30

	// bucketBaselines is the BoltDB bucket name for baseline records.
	bucketBaselines = "baselines"

	// bucketLedger is the BoltDB bucket name for audit ledger entries.
	bucketLedger = "ledger"

	// bucketMeta is the BoltDB bucket name for schema metadata.
	bucketMeta = "meta"
)

// BaselineRecord is the persisted form of a process binary baseline.
// Stored as JSON in the baselines bucket.
type BaselineRecord struct {
	// BinaryPath is the absolute path of the monitored binary.
	BinaryPath string `json:"binary_path"`

	// BinaryHash is sha256(binary_path) used as the BoltDB key.
	BinaryHash string `json:"binary_hash"`

	// MeanVector is the per-feature mean computed from training samples.
	MeanVector []float64 `json:"mean_vector"`

	// CovarianceMatrix is the n×n sample covariance matrix.
	CovarianceMatrix [][]float64 `json:"covariance_matrix"`

	// BaselineEntropy is the Shannon entropy of the baseline event distribution.
	BaselineEntropy float64 `json:"baseline_entropy"`

	// SampleCount is the number of samples used to compute this baseline.
	SampleCount int `json:"sample_count"`

	// UpdatedAt is the timestamp of the last baseline update.
	UpdatedAt time.Time `json:"updated_at"`
}

// LedgerEntry is a single audit log record.
// Stored as JSON in the ledger bucket.
type LedgerEntry struct {
	// Timestamp is the event time (nanosecond precision).
	Timestamp time.Time `json:"timestamp"`

	// PID is the process ID of the affected process.
	PID uint32 `json:"pid"`

	// StateFrom is the previous isolation state.
	StateFrom uint8 `json:"state_from"`

	// StateTo is the new isolation state.
	StateTo uint8 `json:"state_to"`

	// Severity is the composite severity score that triggered the transition.
	Severity float64 `json:"severity"`

	// BudgetRemaining is the token bucket level at the time of the action.
	BudgetRemaining int `json:"budget_remaining"`

	// NodeID is the OCTOREFLEX node that recorded this entry.
	NodeID string `json:"node_id"`
}

// DB wraps a BoltDB instance with typed accessors for OCTOREFLEX data.
type DB struct {
	db            *bolt.DB
	retentionDays int
}

// Open opens (or creates) the BoltDB database at the given path.
// Initialises all required buckets and verifies the schema version.
// Returns an error if the database is corrupt or schema is incompatible.
func Open(path string, retentionDays int) (*DB, error) {
	if retentionDays <= 0 {
		retentionDays = DefaultRetentionDays
	}

	bdb, err := bolt.Open(path, 0o600, &bolt.Options{
		Timeout:         5 * time.Second,
		NoGrowSync:      false,
		FreelistType:    bolt.FreelistArrayType,
	})
	if err != nil {
		return nil, fmt.Errorf("bolt.Open(%q): %w", path, err)
	}

	d := &DB{db: bdb, retentionDays: retentionDays}

	// Initialise buckets and schema version in a single write transaction.
	if err := d.db.Update(func(tx *bolt.Tx) error {
		for _, name := range []string{bucketBaselines, bucketLedger, bucketMeta} {
			if _, err := tx.CreateBucketIfNotExists([]byte(name)); err != nil {
				return fmt.Errorf("CreateBucketIfNotExists(%q): %w", name, err)
			}
		}

		// Write schema version if not present.
		meta := tx.Bucket([]byte(bucketMeta))
		if meta.Get([]byte("schema_version")) == nil {
			if err := meta.Put([]byte("schema_version"), []byte(SchemaVersion)); err != nil {
				return fmt.Errorf("write schema_version: %w", err)
			}
		}
		return nil
	}); err != nil {
		_ = bdb.Close()
		return nil, fmt.Errorf("database initialisation failed: %w", err)
	}

	// Verify schema version compatibility.
	if err := d.checkSchemaVersion(); err != nil {
		_ = bdb.Close()
		return nil, err
	}

	return d, nil
}

// checkSchemaVersion reads and validates the stored schema version.
func (d *DB) checkSchemaVersion() error {
	return d.db.View(func(tx *bolt.Tx) error {
		meta := tx.Bucket([]byte(bucketMeta))
		v := meta.Get([]byte("schema_version"))
		if string(v) != SchemaVersion {
			return fmt.Errorf(
				"schema version mismatch: database has %q, agent requires %q. "+
					"Run migration or restore from backup.",
				string(v), SchemaVersion,
			)
		}
		return nil
	})
}

// Close closes the underlying BoltDB file.
func (d *DB) Close() error {
	return d.db.Close()
}

// ─── Baseline operations ──────────────────────────────────────────────────────

// binaryKey computes the BoltDB key for a binary path: sha256(path) hex-encoded.
func binaryKey(binaryPath string) []byte {
	h := sha256.Sum256([]byte(binaryPath))
	key := make([]byte, hex.EncodedLen(len(h)))
	hex.Encode(key, h[:])
	return key
}

// PutBaseline writes or updates a baseline record for a binary path.
// Uses a single ACID write transaction.
func (d *DB) PutBaseline(rec BaselineRecord) error {
	rec.BinaryHash = string(binaryKey(rec.BinaryPath))
	rec.UpdatedAt = time.Now().UTC()

	data, err := json.Marshal(rec)
	if err != nil {
		return fmt.Errorf("PutBaseline marshal: %w", err)
	}

	return d.db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucketBaselines))
		if err := b.Put([]byte(rec.BinaryHash), data); err != nil {
			return fmt.Errorf("PutBaseline bolt.Put: %w", err)
		}
		return nil
	})
}

// GetBaseline retrieves the baseline record for a binary path.
// Returns (nil, nil) if no baseline exists for this binary.
func (d *DB) GetBaseline(binaryPath string) (*BaselineRecord, error) {
	key := binaryKey(binaryPath)
	var rec BaselineRecord
	found := false

	err := d.db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucketBaselines))
		data := b.Get(key)
		if data == nil {
			return nil // Not found.
		}
		found = true
		return json.Unmarshal(data, &rec)
	})
	if err != nil {
		return nil, fmt.Errorf("GetBaseline(%q): %w", binaryPath, err)
	}
	if !found {
		return nil, nil
	}
	return &rec, nil
}

// ─── Ledger operations ────────────────────────────────────────────────────────

// ledgerKey constructs a sortable BoltDB key for a ledger entry.
// Format: RFC3339Nano + "_" + PID (zero-padded to 10 digits).
// Lexicographic sort = chronological sort.
func ledgerKey(t time.Time, pid uint32) []byte {
	return []byte(fmt.Sprintf("%s_%010d", t.UTC().Format(time.RFC3339Nano), pid))
}

// AppendLedger writes a new audit ledger entry.
// Uses a single ACID write transaction.
func (d *DB) AppendLedger(entry LedgerEntry) error {
	if entry.Timestamp.IsZero() {
		entry.Timestamp = time.Now().UTC()
	}

	data, err := json.Marshal(entry)
	if err != nil {
		return fmt.Errorf("AppendLedger marshal: %w", err)
	}

	key := ledgerKey(entry.Timestamp, entry.PID)

	return d.db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucketLedger))
		if err := b.Put(key, data); err != nil {
			return fmt.Errorf("AppendLedger bolt.Put: %w", err)
		}
		return nil
	})
}

// PruneOldLedgerEntries deletes ledger entries older than retentionDays.
// Called on startup and periodically by the retention goroutine.
// Returns the number of entries deleted.
func (d *DB) PruneOldLedgerEntries() (int, error) {
	cutoff := time.Now().UTC().AddDate(0, 0, -d.retentionDays)
	cutoffKey := ledgerKey(cutoff, 0)

	var deleted int
	err := d.db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucketLedger))
		c := b.Cursor()

		// Collect keys to delete (cannot delete during iteration in bbolt).
		var toDelete [][]byte
		for k, _ := c.First(); k != nil; k, _ = c.Next() {
			if string(k) >= string(cutoffKey) {
				break // All remaining keys are newer than cutoff.
			}
			keyCopy := make([]byte, len(k))
			copy(keyCopy, k)
			toDelete = append(toDelete, keyCopy)
		}

		for _, k := range toDelete {
			if err := b.Delete(k); err != nil {
				return fmt.Errorf("PruneOldLedgerEntries delete: %w", err)
			}
			deleted++
		}
		return nil
	})
	return deleted, err
}

// ReadLedger returns all ledger entries in chronological order.
// For operational use (CLI inspection). Not called on the hot path.
func (d *DB) ReadLedger() ([]LedgerEntry, error) {
	var entries []LedgerEntry
	err := d.db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucketLedger))
		return b.ForEach(func(_, v []byte) error {
			var entry LedgerEntry
			if err := json.Unmarshal(v, &entry); err != nil {
				return err
			}
			entries = append(entries, entry)
			return nil
		})
	})
	return entries, err
}
