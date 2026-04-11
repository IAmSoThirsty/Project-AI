// Package honeypot — database.go
//
// Database honeypot: realistic fake database services.
//
// Purpose:
//   Provides convincing database services (MySQL, PostgreSQL, MongoDB)
//   that log all connection attempts, query patterns, and extraction attempts.

package honeypot

import (
	"bufio"
	"context"
	"crypto/rand"
	"encoding/binary"
	"fmt"
	"net"
	"strings"
	"sync"
	"time"

	"go.uber.org/zap"
)

// DatabaseHoneypotConfig configures database honeypots.
type DatabaseHoneypotConfig struct {
	// DatabaseType: "mysql", "postgresql", "mongodb"
	DatabaseType string

	// BindAddr is the address to bind.
	BindAddr string

	// ServerVersion is the version string to advertise.
	ServerVersion string

	// AuthDelay is the delay before rejecting authentication.
	AuthDelay time.Duration

	// FakeDatabases is a list of fake database names to advertise.
	FakeDatabases []string

	// FakeTables is a list of fake table names.
	FakeTables []string

	// EventSink receives events.
	EventSink EventSink
}

// DefaultMySQLHoneypotConfig returns default MySQL honeypot config.
func DefaultMySQLHoneypotConfig() DatabaseHoneypotConfig {
	return DatabaseHoneypotConfig{
		DatabaseType:  "mysql",
		BindAddr:      "0.0.0.0:3306",
		ServerVersion: "8.0.27",
		AuthDelay:     2 * time.Second,
		FakeDatabases: []string{"production", "users", "orders", "payments", "admin"},
		FakeTables:    []string{"users", "credentials", "api_keys", "sessions"},
	}
}

// DefaultPostgreSQLHoneypotConfig returns default PostgreSQL honeypot config.
func DefaultPostgreSQLHoneypotConfig() DatabaseHoneypotConfig {
	return DatabaseHoneypotConfig{
		DatabaseType:  "postgresql",
		BindAddr:      "0.0.0.0:5432",
		ServerVersion: "14.5",
		AuthDelay:     2 * time.Second,
		FakeDatabases: []string{"postgres", "production", "analytics", "reporting"},
		FakeTables:    []string{"users", "accounts", "transactions", "audit_log"},
	}
}

// DatabaseAttempt captures a database connection attempt.
type DatabaseAttempt struct {
	RemoteAddr   string
	DatabaseType string
	Username     string
	Database     string
	Timestamp    time.Time
	Queries      []string
	SessionID    string
	Duration     time.Duration
}

// DatabaseHoneypot implements database honeypots.
type DatabaseHoneypot struct {
	cfg      DatabaseHoneypotConfig
	log      *zap.Logger
	listener net.Listener
	mu       sync.Mutex
	attempts []DatabaseAttempt
	active   int
	totalConn int
}

// NewDatabaseHoneypot creates a new database honeypot.
func NewDatabaseHoneypot(cfg DatabaseHoneypotConfig, log *zap.Logger) *DatabaseHoneypot {
	return &DatabaseHoneypot{
		cfg:      cfg,
		log:      log,
		attempts: make([]DatabaseAttempt, 0, 1000),
	}
}

// Start starts the database honeypot.
func (h *DatabaseHoneypot) Start(ctx context.Context) error {
	lis, err := net.Listen("tcp", h.cfg.BindAddr)
	if err != nil {
		return fmt.Errorf("listen on %s: %w", h.cfg.BindAddr, err)
	}
	h.listener = lis

	h.log.Info("database honeypot started",
		zap.String("type", h.cfg.DatabaseType),
		zap.String("bind_addr", h.cfg.BindAddr),
		zap.String("version", h.cfg.ServerVersion))

	go h.acceptLoop(ctx)
	return nil
}

// Stop stops the database honeypot.
func (h *DatabaseHoneypot) Stop() error {
	if h.listener != nil {
		return h.listener.Close()
	}
	return nil
}

// acceptLoop accepts incoming connections.
func (h *DatabaseHoneypot) acceptLoop(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		conn, err := h.listener.Accept()
		if err != nil {
			if !strings.Contains(err.Error(), "use of closed network connection") {
				h.log.Error("accept error", zap.Error(err))
			}
			return
		}

		h.mu.Lock()
		h.totalConn++
		h.active++
		connID := h.totalConn
		h.mu.Unlock()

		go h.handleConnection(ctx, conn, connID)
	}
}

// handleConnection handles a database connection.
func (h *DatabaseHoneypot) handleConnection(ctx context.Context, conn net.Conn, connID int) {
	defer func() {
		conn.Close()
		h.mu.Lock()
		h.active--
		h.mu.Unlock()
	}()

	conn.SetDeadline(time.Now().Add(5 * time.Minute))

	remoteAddr := conn.RemoteAddr().String()
	sessionStart := time.Now()
	sessionID := fmt.Sprintf("%s_%d", h.cfg.DatabaseType, connID)

	h.log.Info("database connection",
		zap.String("type", h.cfg.DatabaseType),
		zap.String("remote_addr", remoteAddr),
		zap.String("session_id", sessionID))

	attempt := DatabaseAttempt{
		RemoteAddr:   remoteAddr,
		DatabaseType: h.cfg.DatabaseType,
		Timestamp:    sessionStart,
		SessionID:    sessionID,
		Queries:      make([]string, 0, 100),
	}

	// Handle based on database type
	switch h.cfg.DatabaseType {
	case "mysql":
		h.handleMySQL(conn, &attempt)
	case "postgresql":
		h.handlePostgreSQL(conn, &attempt)
	case "mongodb":
		h.handleMongoDB(conn, &attempt)
	}

	attempt.Duration = time.Since(sessionStart)

	// Record attempt
	h.mu.Lock()
	h.attempts = append(h.attempts, attempt)
	h.mu.Unlock()

	// Emit event
	if h.cfg.EventSink != nil {
		h.cfg.EventSink.Emit(HoneypotEvent{
			Type:       EventTypeDBAttempt,
			RemoteAddr: remoteAddr,
			Timestamp:  time.Now(),
			Metadata: map[string]interface{}{
				"database_type": h.cfg.DatabaseType,
				"username":      attempt.Username,
				"database":      attempt.Database,
				"query_count":   len(attempt.Queries),
				"duration_ms":   attempt.Duration.Milliseconds(),
			},
		})
	}

	h.log.Warn("database session ended",
		zap.String("type", h.cfg.DatabaseType),
		zap.String("remote_addr", remoteAddr),
		zap.String("username", attempt.Username),
		zap.Int("queries", len(attempt.Queries)),
		zap.Duration("duration", attempt.Duration))
}

// handleMySQL handles MySQL protocol.
func (h *DatabaseHoneypot) handleMySQL(conn net.Conn, attempt *DatabaseAttempt) {
	// Send handshake packet
	handshake := h.buildMySQLHandshake()
	conn.Write(handshake)

	// Read auth response
	reader := bufio.NewReader(conn)
	authBuf := make([]byte, 1024)
	n, err := reader.Read(authBuf)
	if err != nil || n < 32 {
		return
	}

	// Parse username (simplified)
	usernameEnd := 32
	for i := 32; i < n && i < 100; i++ {
		if authBuf[i] == 0 {
			usernameEnd = i
			break
		}
	}
	attempt.Username = string(authBuf[32:usernameEnd])

	// Delay to waste time
	time.Sleep(h.cfg.AuthDelay)

	// Send error (access denied)
	errorPkt := []byte{
		0x17, 0x00, 0x00, 0x02, // Packet header
		0xff,       // Error indicator
		0x15, 0x04, // Error code 1045
		'#', '2', '8', '0', '0', '0', // SQL state
	}
	errorMsg := "Access denied for user '" + attempt.Username + "'@'" + conn.RemoteAddr().String() + "'"
	errorPkt = append(errorPkt, []byte(errorMsg)...)
	conn.Write(errorPkt)
}

// buildMySQLHandshake builds a MySQL handshake packet.
func (h *DatabaseHoneypot) buildMySQLHandshake() []byte {
	pkt := []byte{
		0x0a, // Protocol version 10
	}

	// Server version
	pkt = append(pkt, []byte(h.cfg.ServerVersion)...)
	pkt = append(pkt, 0x00)

	// Connection ID (random)
	connID := make([]byte, 4)
	rand.Read(connID)
	pkt = append(pkt, connID...)

	// Auth plugin data (salt)
	salt := make([]byte, 8)
	rand.Read(salt)
	pkt = append(pkt, salt...)
	pkt = append(pkt, 0x00) // Filler

	// Capability flags
	pkt = append(pkt, 0xff, 0xf7, 0xff, 0x02)

	// More salt
	moreSalt := make([]byte, 12)
	rand.Read(moreSalt)
	pkt = append(pkt, moreSalt...)
	pkt = append(pkt, 0x00)

	// Auth plugin name
	pkt = append(pkt, []byte("mysql_native_password")...)
	pkt = append(pkt, 0x00)

	// Prepend length
	length := len(pkt)
	header := make([]byte, 4)
	header[0] = byte(length)
	header[1] = byte(length >> 8)
	header[2] = byte(length >> 16)
	header[3] = 0x00 // Sequence ID

	return append(header, pkt...)
}

// handlePostgreSQL handles PostgreSQL protocol.
func (h *DatabaseHoneypot) handlePostgreSQL(conn net.Conn, attempt *DatabaseAttempt) {
	reader := bufio.NewReader(conn)

	// Read startup message
	startupBuf := make([]byte, 1024)
	n, err := reader.Read(startupBuf)
	if err != nil || n < 8 {
		return
	}

	// Parse startup message
	length := binary.BigEndian.Uint32(startupBuf[0:4])
	if length > 0 && int(length) <= n {
		// Extract parameters
		params := string(startupBuf[8:length])
		if idx := strings.Index(params, "user\x00"); idx >= 0 {
			userStart := idx + 5
			if userEnd := strings.Index(params[userStart:], "\x00"); userEnd >= 0 {
				attempt.Username = params[userStart : userStart+userEnd]
			}
		}
		if idx := strings.Index(params, "database\x00"); idx >= 0 {
			dbStart := idx + 9
			if dbEnd := strings.Index(params[dbStart:], "\x00"); dbEnd >= 0 {
				attempt.Database = params[dbStart : dbStart+dbEnd]
			}
		}
	}

	time.Sleep(h.cfg.AuthDelay)

	// Send authentication request (MD5)
	authReq := []byte{
		'R',                   // Authentication request
		0x00, 0x00, 0x00, 0x0c, // Length
		0x00, 0x00, 0x00, 0x05, // MD5 authentication
	}
	salt := make([]byte, 4)
	rand.Read(salt)
	authReq = append(authReq, salt...)
	conn.Write(authReq)

	// Read password response
	reader.Read(startupBuf)

	time.Sleep(h.cfg.AuthDelay)

	// Send error
	errorMsg := "EFATAL\x00C28P01\x00Mpassword authentication failed for user \"" + attempt.Username + "\"\x00\x00"
	errorPkt := []byte{'E'}
	errorLen := make([]byte, 4)
	binary.BigEndian.PutUint32(errorLen, uint32(len(errorMsg)+4))
	errorPkt = append(errorPkt, errorLen...)
	errorPkt = append(errorPkt, []byte(errorMsg)...)
	conn.Write(errorPkt)
}

// handleMongoDB handles MongoDB protocol.
func (h *DatabaseHoneypot) handleMongoDB(conn net.Conn, attempt *DatabaseAttempt) {
	reader := bufio.NewReader(conn)

	// Read MongoDB query
	queryBuf := make([]byte, 1024)
	n, err := reader.Read(queryBuf)
	if err != nil || n < 16 {
		return
	}

	time.Sleep(h.cfg.AuthDelay)

	// Send authentication error (simplified)
	errorResp := []byte{
		0x00, 0x00, 0x00, 0x00, // Message length (placeholder)
		0x00, 0x00, 0x00, 0x00, // Request ID
		0x00, 0x00, 0x00, 0x00, // Response to
		0xd4, 0x07, 0x00, 0x00, // OpCode: OP_REPLY
		0x00, 0x00, 0x00, 0x00, // Response flags
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // Cursor ID
		0x00, 0x00, 0x00, 0x00, // Starting from
		0x01, 0x00, 0x00, 0x00, // Number returned
	}

	// BSON error document
	bsonError := []byte{
		0x26, 0x00, 0x00, 0x00, // Document size
		0x10, 'o', 'k', 0x00, 0x00, 0x00, 0x00, 0x00, // ok: 0
		0x02, 'e', 'r', 'r', 'm', 's', 'g', 0x00,
		0x12, 0x00, 0x00, 0x00, // String length
		'A', 'u', 't', 'h', ' ', 'f', 'a', 'i', 'l', 'e', 'd', 0x00,
		0x00, // End of document
	}

	errorResp = append(errorResp, bsonError...)

	// Update message length
	binary.LittleEndian.PutUint32(errorResp[0:4], uint32(len(errorResp)))

	conn.Write(errorResp)
}

// GetAttempts returns all recorded attempts.
func (h *DatabaseHoneypot) GetAttempts() []DatabaseAttempt {
	h.mu.Lock()
	defer h.mu.Unlock()
	result := make([]DatabaseAttempt, len(h.attempts))
	copy(result, h.attempts)
	return result
}

// GetStats returns honeypot statistics.
func (h *DatabaseHoneypot) GetStats() HoneypotStats {
	h.mu.Lock()
	defer h.mu.Unlock()

	return HoneypotStats{
		Type:             h.cfg.DatabaseType,
		TotalConnections: h.totalConn,
		ActiveSessions:   h.active,
		TotalAttempts:    len(h.attempts),
		UniqueIPs:        h.countUniqueIPs(),
	}
}

// countUniqueIPs counts unique IP addresses.
func (h *DatabaseHoneypot) countUniqueIPs() int {
	seen := make(map[string]bool)
	for _, attempt := range h.attempts {
		ip := strings.Split(attempt.RemoteAddr, ":")[0]
		seen[ip] = true
	}
	return len(seen)
}

var _ Honeypot = (*DatabaseHoneypot)(nil)
