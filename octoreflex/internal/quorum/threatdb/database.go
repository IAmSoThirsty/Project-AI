// Package threatdb implements a distributed threat intelligence database
// for OctoReflex federated quorum.
//
// Features:
// - Replicated threat signatures (SHA256 hashes, YARA rules)
// - Indicators of Compromise (IoCs): IPs, domains, file hashes
// - Behavioral patterns (syscall sequences, network patterns)
// - Threat scoring with consensus (aggregate scores from multiple nodes)
// - Efficient updates (delta sync, compression)
// - Query API for local threat lookups
//
// Storage:
// - BoltDB for local persistence
// - Gossip for distribution
// - Raft for critical updates (new signatures, policy changes)

package threatdb

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"go.etcd.io/bbolt"
	"go.uber.org/zap"
)

// ThreatDB is the distributed threat intelligence database.
type ThreatDB struct {
	db   *bbolt.DB
	mu   sync.RWMutex
	log  *zap.Logger
	
	// In-memory cache for fast lookups
	signatures    map[[32]byte]*Signature
	iocs          map[string]*IoC
	behaviors     map[string]*BehaviorPattern
	
	// Metrics
	totalSignatures uint64
	totalIoCs       uint64
	totalBehaviors  uint64
}

// Signature represents a threat signature.
type Signature struct {
	Hash        [32]byte  // SHA256 hash of the signature
	Type        SignatureType
	Pattern     []byte    // YARA rule, regex, or binary pattern
	Severity    float64   // 0.0 (benign) to 1.0 (critical)
	Description string
	Source      string    // node that contributed this signature
	Confidence  float64   // 0.0 to 1.0
	FirstSeen   time.Time
	LastSeen    time.Time
	HitCount    uint64    // how many times detected across cluster
	FalsePositives uint64 // reported false positives
}

// SignatureType classifies signature types.
type SignatureType int

const (
	SignatureYARA SignatureType = iota
	SignatureHash
	SignatureRegex
	SignatureBinary
	SignatureSyscall
)

func (t SignatureType) String() string {
	switch t {
	case SignatureYARA:
		return "yara"
	case SignatureHash:
		return "hash"
	case SignatureRegex:
		return "regex"
	case SignatureBinary:
		return "binary"
	case SignatureSyscall:
		return "syscall"
	default:
		return fmt.Sprintf("unknown(%d)", t)
	}
}

// IoC represents an Indicator of Compromise.
type IoC struct {
	Value       string       // IP, domain, hash, etc.
	Type        IoCType
	Severity    float64
	Source      string
	FirstSeen   time.Time
	LastSeen    time.Time
	Metadata    map[string]string
	Confirmed   bool         // confirmed by multiple nodes
}

// IoCType classifies IoC types.
type IoCType int

const (
	IoCIPv4 IoCType = iota
	IoCIPv6
	IoCDomain
	IoCURL
	IoCFileHash
	IoCEmail
	IoCCertHash
)

func (t IoCType) String() string {
	switch t {
	case IoCIPv4:
		return "ipv4"
	case IoCIPv6:
		return "ipv6"
	case IoCDomain:
		return "domain"
	case IoCURL:
		return "url"
	case IoCFileHash:
		return "file_hash"
	case IoCEmail:
		return "email"
	case IoCCertHash:
		return "cert_hash"
	default:
		return fmt.Sprintf("unknown(%d)", t)
	}
}

// BehaviorPattern represents a behavioral threat pattern.
type BehaviorPattern struct {
	ID          string
	Name        string
	Syscalls    []string      // sequence of syscalls
	NetworkFlow NetworkPattern
	FileAccess  FilePattern
	Severity    float64
	Source      string
	FirstSeen   time.Time
	LastSeen    time.Time
}

// NetworkPattern describes network behavior.
type NetworkPattern struct {
	Protocol      string   // tcp, udp, icmp
	Ports         []uint16
	BytesPerSec   float64
	PacketsPerSec float64
	Destinations  []string // IPs or domains
}

// FilePattern describes file access behavior.
type FilePattern struct {
	Paths       []string
	Operations  []string // read, write, execute, delete
	Frequency   float64  // ops per second
}

var (
	bucketSignatures = []byte("signatures")
	bucketIoCs       = []byte("iocs")
	bucketBehaviors  = []byte("behaviors")
	bucketMetadata   = []byte("metadata")
)

// NewThreatDB creates a new threat intelligence database.
func NewThreatDB(dbPath string, log *zap.Logger) (*ThreatDB, error) {
	db, err := bbolt.Open(dbPath, 0600, &bbolt.Options{
		Timeout: 1 * time.Second,
	})
	if err != nil {
		return nil, fmt.Errorf("open threat db: %w", err)
	}
	
	// Create buckets
	err = db.Update(func(tx *bbolt.Tx) error {
		for _, bucket := range [][]byte{bucketSignatures, bucketIoCs, bucketBehaviors, bucketMetadata} {
			if _, err := tx.CreateBucketIfNotExists(bucket); err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		db.Close()
		return nil, fmt.Errorf("create buckets: %w", err)
	}
	
	tdb := &ThreatDB{
		db:         db,
		log:        log,
		signatures: make(map[[32]byte]*Signature),
		iocs:       make(map[string]*IoC),
		behaviors:  make(map[string]*BehaviorPattern),
	}
	
	// Load into memory cache
	if err := tdb.loadCache(); err != nil {
		db.Close()
		return nil, fmt.Errorf("load cache: %w", err)
	}
	
	log.Info("threat database initialized",
		zap.Uint64("signatures", tdb.totalSignatures),
		zap.Uint64("iocs", tdb.totalIoCs),
		zap.Uint64("behaviors", tdb.totalBehaviors))
	
	return tdb, nil
}

// Close closes the threat database.
func (tdb *ThreatDB) Close() error {
	return tdb.db.Close()
}

// AddSignature adds a new threat signature.
func (tdb *ThreatDB) AddSignature(sig *Signature) error {
	tdb.mu.Lock()
	defer tdb.mu.Unlock()
	
	sig.FirstSeen = time.Now()
	sig.LastSeen = time.Now()
	
	// Store in memory
	tdb.signatures[sig.Hash] = sig
	
	// Persist to disk
	err := tdb.db.Update(func(tx *bbolt.Tx) error {
		b := tx.Bucket(bucketSignatures)
		
		data, err := json.Marshal(sig)
		if err != nil {
			return err
		}
		
		return b.Put(sig.Hash[:], data)
	})
	
	if err == nil {
		tdb.totalSignatures++
		tdb.log.Debug("signature added",
			zap.String("hash", fmt.Sprintf("%x", sig.Hash[:8])),
			zap.String("type", sig.Type.String()),
			zap.Float64("severity", sig.Severity))
	}
	
	return err
}

// GetSignature retrieves a signature by hash.
func (tdb *ThreatDB) GetSignature(hash [32]byte) (*Signature, error) {
	tdb.mu.RLock()
	defer tdb.mu.RUnlock()
	
	if sig, ok := tdb.signatures[hash]; ok {
		return sig, nil
	}
	
	return nil, fmt.Errorf("signature not found")
}

// AddIoC adds an Indicator of Compromise.
func (tdb *ThreatDB) AddIoC(ioc *IoC) error {
	tdb.mu.Lock()
	defer tdb.mu.Unlock()
	
	ioc.FirstSeen = time.Now()
	ioc.LastSeen = time.Now()
	
	// Store in memory
	tdb.iocs[ioc.Value] = ioc
	
	// Persist to disk
	err := tdb.db.Update(func(tx *bbolt.Tx) error {
		b := tx.Bucket(bucketIoCs)
		
		data, err := json.Marshal(ioc)
		if err != nil {
			return err
		}
		
		return b.Put([]byte(ioc.Value), data)
	})
	
	if err == nil {
		tdb.totalIoCs++
		tdb.log.Debug("IoC added",
			zap.String("value", ioc.Value),
			zap.String("type", ioc.Type.String()),
			zap.Float64("severity", ioc.Severity))
	}
	
	return err
}

// GetIoC retrieves an IoC by value.
func (tdb *ThreatDB) GetIoC(value string) (*IoC, error) {
	tdb.mu.RLock()
	defer tdb.mu.RUnlock()
	
	if ioc, ok := tdb.iocs[value]; ok {
		return ioc, nil
	}
	
	return nil, fmt.Errorf("IoC not found")
}

// CheckIP checks if an IP is a known IoC.
func (tdb *ThreatDB) CheckIP(ip string) (bool, float64) {
	ioc, err := tdb.GetIoC(ip)
	if err != nil {
		return false, 0
	}
	return true, ioc.Severity
}

// CheckDomain checks if a domain is a known IoC.
func (tdb *ThreatDB) CheckDomain(domain string) (bool, float64) {
	ioc, err := tdb.GetIoC(domain)
	if err != nil {
		return false, 0
	}
	return true, ioc.Severity
}

// CheckFileHash checks if a file hash is a known threat.
func (tdb *ThreatDB) CheckFileHash(hash string) (bool, float64) {
	ioc, err := tdb.GetIoC(hash)
	if err != nil {
		return false, 0
	}
	return true, ioc.Severity
}

// AddBehaviorPattern adds a behavioral threat pattern.
func (tdb *ThreatDB) AddBehaviorPattern(pattern *BehaviorPattern) error {
	tdb.mu.Lock()
	defer tdb.mu.Unlock()
	
	pattern.FirstSeen = time.Now()
	pattern.LastSeen = time.Now()
	
	// Store in memory
	tdb.behaviors[pattern.ID] = pattern
	
	// Persist to disk
	err := tdb.db.Update(func(tx *bbolt.Tx) error {
		b := tx.Bucket(bucketBehaviors)
		
		data, err := json.Marshal(pattern)
		if err != nil {
			return err
		}
		
		return b.Put([]byte(pattern.ID), data)
	})
	
	if err == nil {
		tdb.totalBehaviors++
		tdb.log.Debug("behavior pattern added",
			zap.String("id", pattern.ID),
			zap.String("name", pattern.Name),
			zap.Float64("severity", pattern.Severity))
	}
	
	return err
}

// GetBehaviorPattern retrieves a behavior pattern by ID.
func (tdb *ThreatDB) GetBehaviorPattern(id string) (*BehaviorPattern, error) {
	tdb.mu.RLock()
	defer tdb.mu.RUnlock()
	
	if pattern, ok := tdb.behaviors[id]; ok {
		return pattern, nil
	}
	
	return nil, fmt.Errorf("behavior pattern not found")
}

// UpdateSignatureHit increments hit count for a signature.
func (tdb *ThreatDB) UpdateSignatureHit(hash [32]byte) error {
	tdb.mu.Lock()
	defer tdb.mu.Unlock()
	
	sig, ok := tdb.signatures[hash]
	if !ok {
		return fmt.Errorf("signature not found")
	}
	
	sig.HitCount++
	sig.LastSeen = time.Now()
	
	// Persist
	return tdb.db.Update(func(tx *bbolt.Tx) error {
		b := tx.Bucket(bucketSignatures)
		
		data, err := json.Marshal(sig)
		if err != nil {
			return err
		}
		
		return b.Put(hash[:], data)
	})
}

// ExportDelta exports threat intel added/updated since timestamp.
func (tdb *ThreatDB) ExportDelta(since time.Time) (*ThreatDelta, error) {
	tdb.mu.RLock()
	defer tdb.mu.RUnlock()
	
	delta := &ThreatDelta{
		Timestamp: time.Now(),
		Signatures: make([]*Signature, 0),
		IoCs: make([]*IoC, 0),
		Behaviors: make([]*BehaviorPattern, 0),
	}
	
	for _, sig := range tdb.signatures {
		if sig.LastSeen.After(since) {
			delta.Signatures = append(delta.Signatures, sig)
		}
	}
	
	for _, ioc := range tdb.iocs {
		if ioc.LastSeen.After(since) {
			delta.IoCs = append(delta.IoCs, ioc)
		}
	}
	
	for _, behavior := range tdb.behaviors {
		if behavior.LastSeen.After(since) {
			delta.Behaviors = append(delta.Behaviors, behavior)
		}
	}
	
	return delta, nil
}

// ImportDelta imports threat intelligence from another node.
func (tdb *ThreatDB) ImportDelta(delta *ThreatDelta) error {
	tdb.log.Info("importing threat delta",
		zap.Int("signatures", len(delta.Signatures)),
		zap.Int("iocs", len(delta.IoCs)),
		zap.Int("behaviors", len(delta.Behaviors)))
	
	for _, sig := range delta.Signatures {
		if err := tdb.AddSignature(sig); err != nil {
			tdb.log.Warn("failed to import signature", zap.Error(err))
		}
	}
	
	for _, ioc := range delta.IoCs {
		if err := tdb.AddIoC(ioc); err != nil {
			tdb.log.Warn("failed to import IoC", zap.Error(err))
		}
	}
	
	for _, behavior := range delta.Behaviors {
		if err := tdb.AddBehaviorPattern(behavior); err != nil {
			tdb.log.Warn("failed to import behavior", zap.Error(err))
		}
	}
	
	return nil
}

// ThreatDelta represents incremental threat intelligence updates.
type ThreatDelta struct {
	Timestamp  time.Time
	Signatures []*Signature
	IoCs       []*IoC
	Behaviors  []*BehaviorPattern
}

// Serialize encodes the delta for network transmission (with compression).
func (td *ThreatDelta) Serialize() ([]byte, error) {
	data, err := json.Marshal(td)
	if err != nil {
		return nil, err
	}
	
	// In production, compress with gzip or zstd
	// For now, return uncompressed
	return data, nil
}

// DeserializeDelta decodes a threat delta from bytes.
func DeserializeDelta(data []byte) (*ThreatDelta, error) {
	// In production, decompress first
	
	var delta ThreatDelta
	if err := json.Unmarshal(data, &delta); err != nil {
		return nil, err
	}
	
	return &delta, nil
}

// loadCache loads threat intel from disk into memory.
func (tdb *ThreatDB) loadCache() error {
	return tdb.db.View(func(tx *bbolt.Tx) error {
		// Load signatures
		b := tx.Bucket(bucketSignatures)
		c := b.Cursor()
		
		for k, v := c.First(); k != nil; k, v = c.Next() {
			var sig Signature
			if err := json.Unmarshal(v, &sig); err != nil {
				tdb.log.Warn("failed to unmarshal signature", zap.Error(err))
				continue
			}
			
			var hash [32]byte
			copy(hash[:], k)
			tdb.signatures[hash] = &sig
			tdb.totalSignatures++
		}
		
		// Load IoCs
		b = tx.Bucket(bucketIoCs)
		c = b.Cursor()
		
		for k, v := c.First(); k != nil; k, v = c.Next() {
			var ioc IoC
			if err := json.Unmarshal(v, &ioc); err != nil {
				tdb.log.Warn("failed to unmarshal IoC", zap.Error(err))
				continue
			}
			
			tdb.iocs[string(k)] = &ioc
			tdb.totalIoCs++
		}
		
		// Load behaviors
		b = tx.Bucket(bucketBehaviors)
		c = b.Cursor()
		
		for k, v := c.First(); k != nil; k, v = c.Next() {
			var behavior BehaviorPattern
			if err := json.Unmarshal(v, &behavior); err != nil {
				tdb.log.Warn("failed to unmarshal behavior", zap.Error(err))
				continue
			}
			
			tdb.behaviors[string(k)] = &behavior
			tdb.totalBehaviors++
		}
		
		return nil
	})
}

// Stats returns database statistics.
func (tdb *ThreatDB) Stats() map[string]uint64 {
	tdb.mu.RLock()
	defer tdb.mu.RUnlock()
	
	return map[string]uint64{
		"signatures": tdb.totalSignatures,
		"iocs":       tdb.totalIoCs,
		"behaviors":  tdb.totalBehaviors,
	}
}

// ComputeHash computes SHA256 hash of data.
func ComputeHash(data []byte) [32]byte {
	return sha256.Sum256(data)
}

// GenerateSignatureID generates a unique ID for a signature.
func GenerateSignatureID(pattern []byte, sigType SignatureType) [32]byte {
	h := sha256.New()
	h.Write([]byte{byte(sigType)})
	h.Write(pattern)
	
	var hash [32]byte
	copy(hash[:], h.Sum(nil))
	return hash
}

// AggregateScores aggregates severity scores from multiple nodes.
func AggregateScores(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	
	// Weighted average: higher scores get more weight
	var sum, weightSum float64
	for _, score := range scores {
		weight := score * score // quadratic weighting
		sum += score * weight
		weightSum += weight
	}
	
	if weightSum == 0 {
		return 0
	}
	
	return sum / weightSum
}

// EncodeUint64 encodes uint64 to bytes.
func EncodeUint64(n uint64) []byte {
	b := make([]byte, 8)
	binary.BigEndian.PutUint64(b, n)
	return b
}

// DecodeUint64 decodes bytes to uint64.
func DecodeUint64(b []byte) uint64 {
	return binary.BigEndian.Uint64(b)
}
