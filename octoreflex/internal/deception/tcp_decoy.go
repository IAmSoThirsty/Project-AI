// Package deception — tcp_decoy.go
//
// Stateful TCP decoys with realistic handshakes.
//
// Purpose:
//   Creates realistic TCP decoy services that complete full handshakes,
//   engage attackers in protocol exchanges, and waste their resources
//   while gathering intelligence.
//
// Features:
//   - Stateful TCP connection handling
//   - Protocol-specific responses (HTTP, SSH, MySQL, etc.)
//   - Bandwidth amplification to waste attacker resources
//   - Connection fingerprinting and analysis

package deception

import (
	"bufio"
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"io"
	"net"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"go.uber.org/zap"
)

// TCPDecoyConfig configures the TCP decoy system.
type TCPDecoyConfig struct {
	// BindAddrs is a list of addresses to bind decoy listeners.
	BindAddrs []string

	// ProtocolHandlers maps ports to protocol handlers.
	// If empty, generic handler is used.
	ProtocolHandlers map[int]string

	// MaxConcurrentConns limits concurrent connections.
	MaxConcurrentConns int

	// ConnectionTimeout is the max time to keep a connection alive.
	ConnectionTimeout time.Duration

	// BandwidthWasteTarget is bytes to send per connection.
	// Higher values waste more attacker bandwidth.
	BandwidthWasteTarget int64

	// SlowResponseDelay delays responses to waste attacker time.
	SlowResponseDelay time.Duration

	// EventSink receives decoy events.
	EventSink DecoyEventSink
}

// DefaultTCPDecoyConfig returns default configuration.
func DefaultTCPDecoyConfig() TCPDecoyConfig {
	return TCPDecoyConfig{
		BindAddrs: []string{
			"0.0.0.0:22",   // SSH
			"0.0.0.0:3306", // MySQL
			"0.0.0.0:5432", // PostgreSQL
			"0.0.0.0:6379", // Redis
		},
		MaxConcurrentConns:   100,
		ConnectionTimeout:    5 * time.Minute,
		BandwidthWasteTarget: 1024 * 1024, // 1MB per connection
		SlowResponseDelay:    500 * time.Millisecond,
		ProtocolHandlers: map[int]string{
			22:   "ssh",
			3306: "mysql",
			5432: "postgresql",
			6379: "redis",
		},
	}
}

// DecoyConnection represents a single decoy connection.
type DecoyConnection struct {
	Conn         net.Conn
	RemoteAddr   string
	LocalPort    int
	StartTime    time.Time
	BytesRead    int64
	BytesWritten int64
	Protocol     string
	Fingerprint  string
}

// DecoyEventSink receives events from decoy connections.
type DecoyEventSink interface {
	EmitConnection(conn DecoyConnection)
}

// TCPDecoy manages TCP decoy listeners.
type TCPDecoy struct {
	cfg       TCPDecoyConfig
	log       *zap.Logger
	listeners []net.Listener
	mu        sync.Mutex
	activeConns int32
	totalConns  uint64
	totalBytes  uint64
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewTCPDecoy creates a new TCP decoy manager.
func NewTCPDecoy(cfg TCPDecoyConfig, log *zap.Logger) *TCPDecoy {
	ctx, cancel := context.WithCancel(context.Background())
	return &TCPDecoy{
		cfg:    cfg,
		log:    log,
		ctx:    ctx,
		cancel: cancel,
	}
}

// Start starts all TCP decoy listeners.
func (td *TCPDecoy) Start() error {
	for _, addr := range td.cfg.BindAddrs {
		lis, err := net.Listen("tcp", addr)
		if err != nil {
			td.log.Warn("failed to start decoy listener",
				zap.String("addr", addr),
				zap.Error(err))
			continue
		}

		td.listeners = append(td.listeners, lis)
		td.log.Info("TCP decoy listener started", zap.String("addr", addr))

		go td.acceptLoop(lis)
	}

	if len(td.listeners) == 0 {
		return fmt.Errorf("no decoy listeners started")
	}

	return nil
}

// Stop stops all TCP decoy listeners.
func (td *TCPDecoy) Stop() error {
	td.cancel()

	for _, lis := range td.listeners {
		lis.Close()
	}

	td.log.Info("TCP decoy stopped")
	return nil
}

// acceptLoop accepts incoming connections for a listener.
func (td *TCPDecoy) acceptLoop(lis net.Listener) {
	localAddr := lis.Addr().String()
	port := extractPort(localAddr)

	for {
		select {
		case <-td.ctx.Done():
			return
		default:
		}

		conn, err := lis.Accept()
		if err != nil {
			if !strings.Contains(err.Error(), "use of closed network connection") {
				td.log.Error("accept error", zap.Error(err))
			}
			return
		}

		// Check connection limit
		active := atomic.LoadInt32(&td.activeConns)
		if int(active) >= td.cfg.MaxConcurrentConns {
			td.log.Warn("connection limit reached, dropping",
				zap.String("remote_addr", conn.RemoteAddr().String()))
			conn.Close()
			continue
		}

		atomic.AddInt32(&td.activeConns, 1)
		atomic.AddUint64(&td.totalConns, 1)

		go td.handleConnection(conn, port)
	}
}

// handleConnection handles a single decoy connection.
func (td *TCPDecoy) handleConnection(conn net.Conn, localPort int) {
	defer func() {
		conn.Close()
		atomic.AddInt32(&td.activeConns, -1)
	}()

	// Set connection deadline
	deadline := time.Now().Add(td.cfg.ConnectionTimeout)
	conn.SetDeadline(deadline)

	remoteAddr := conn.RemoteAddr().String()
	startTime := time.Now()

	decoyConn := DecoyConnection{
		Conn:       conn,
		RemoteAddr: remoteAddr,
		LocalPort:  localPort,
		StartTime:  startTime,
	}

	// Determine protocol
	protocol := "generic"
	if p, ok := td.cfg.ProtocolHandlers[localPort]; ok {
		protocol = p
	}
	decoyConn.Protocol = protocol

	td.log.Info("decoy connection accepted",
		zap.String("remote_addr", remoteAddr),
		zap.Int("local_port", localPort),
		zap.String("protocol", protocol))

	// Fingerprint connection
	decoyConn.Fingerprint = td.fingerprintConnection(conn)

	// Handle based on protocol
	switch protocol {
	case "ssh":
		td.handleSSH(&decoyConn)
	case "mysql":
		td.handleMySQL(&decoyConn)
	case "postgresql":
		td.handlePostgreSQL(&decoyConn)
	case "redis":
		td.handleRedis(&decoyConn)
	default:
		td.handleGeneric(&decoyConn)
	}

	// Update statistics
	atomic.AddUint64(&td.totalBytes, uint64(decoyConn.BytesWritten))

	// Emit event
	if td.cfg.EventSink != nil {
		td.cfg.EventSink.EmitConnection(decoyConn)
	}

	duration := time.Since(startTime)
	td.log.Info("decoy connection closed",
		zap.String("remote_addr", remoteAddr),
		zap.Int("local_port", localPort),
		zap.Int64("bytes_read", decoyConn.BytesRead),
		zap.Int64("bytes_written", decoyConn.BytesWritten),
		zap.Duration("duration", duration))
}

// fingerprintConnection generates a fingerprint of the connection.
func (td *TCPDecoy) fingerprintConnection(conn net.Conn) string {
	// Read initial bytes with short timeout
	conn.SetReadDeadline(time.Now().Add(2 * time.Second))
	buf := make([]byte, 256)
	n, _ := conn.Read(buf)
	conn.SetReadDeadline(time.Time{}) // Reset

	if n > 0 {
		return hex.EncodeToString(buf[:n])
	}
	return "no_data"
}

// handleSSH handles SSH protocol decoy.
func (td *TCPDecoy) handleSSH(dc *DecoyConnection) {
	// Send SSH banner
	banner := "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n"
	n, _ := dc.Conn.Write([]byte(banner))
	dc.BytesWritten += int64(n)

	time.Sleep(td.cfg.SlowResponseDelay)

	// Read client banner
	reader := bufio.NewReader(dc.Conn)
	clientBanner, _ := reader.ReadString('\n')
	dc.BytesRead += int64(len(clientBanner))

	// Send key exchange init
	kexInit := make([]byte, 1024)
	rand.Read(kexInit)
	n, _ = dc.Conn.Write(kexInit)
	dc.BytesWritten += int64(n)

	// Waste bandwidth with fake SSH protocol data
	for dc.BytesWritten < td.cfg.BandwidthWasteTarget {
		time.Sleep(td.cfg.SlowResponseDelay)
		chunk := make([]byte, 4096)
		rand.Read(chunk)
		n, err := dc.Conn.Write(chunk)
		dc.BytesWritten += int64(n)
		if err != nil {
			break
		}
	}
}

// handleMySQL handles MySQL protocol decoy.
func (td *TCPDecoy) handleMySQL(dc *DecoyConnection) {
	// MySQL handshake packet
	handshake := []byte{
		0x0a, // Protocol version 10
		'8', '.', '0', '.', '2', '7', 0x00, // Server version
		0x01, 0x00, 0x00, 0x00, // Connection ID
	}
	// Add salt and capabilities
	salt := make([]byte, 20)
	rand.Read(salt)
	handshake = append(handshake, salt...)

	n, _ := dc.Conn.Write(handshake)
	dc.BytesWritten += int64(n)

	time.Sleep(td.cfg.SlowResponseDelay)

	// Read auth packet
	buf := make([]byte, 1024)
	n, _ = dc.Conn.Read(buf)
	dc.BytesRead += int64(n)

	// Send error packet (access denied)
	errorPkt := []byte{
		0xff,                                       // Error packet
		0x15, 0x04,                                 // Error code 1045
		'#', '2', '8', '0', '0', '0',              // SQL state
		'A', 'c', 'c', 'e', 's', 's', ' ', 'd', 'e', 'n', 'i', 'e', 'd',
	}
	time.Sleep(td.cfg.SlowResponseDelay)
	n, _ = dc.Conn.Write(errorPkt)
	dc.BytesWritten += int64(n)
}

// handlePostgreSQL handles PostgreSQL protocol decoy.
func (td *TCPDecoy) handlePostgreSQL(dc *DecoyConnection) {
	// Read startup packet
	buf := make([]byte, 1024)
	n, _ := dc.Conn.Read(buf)
	dc.BytesRead += int64(n)

	time.Sleep(td.cfg.SlowResponseDelay)

	// Send authentication request
	authReq := []byte{'R', 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x03}
	n, _ = dc.Conn.Write(authReq)
	dc.BytesWritten += int64(n)

	// Read password
	n, _ = dc.Conn.Read(buf)
	dc.BytesRead += int64(n)

	time.Sleep(td.cfg.SlowResponseDelay)

	// Send error response
	errorMsg := "EFATAL\x00C28P01\x00Mpassword authentication failed\x00\x00"
	n, _ = dc.Conn.Write([]byte(errorMsg))
	dc.BytesWritten += int64(n)
}

// handleRedis handles Redis protocol decoy.
func (td *TCPDecoy) handleRedis(dc *DecoyConnection) {
	reader := bufio.NewReader(dc.Conn)

	for {
		time.Sleep(td.cfg.SlowResponseDelay)

		// Read Redis command
		line, err := reader.ReadString('\n')
		if err != nil {
			break
		}
		dc.BytesRead += int64(len(line))

		// Send error response
		response := "-ERR Authentication required\r\n"
		n, _ := dc.Conn.Write([]byte(response))
		dc.BytesWritten += int64(n)

		if dc.BytesWritten >= td.cfg.BandwidthWasteTarget {
			break
		}
	}
}

// handleGeneric handles generic TCP decoy.
func (td *TCPDecoy) handleGeneric(dc *DecoyConnection) {
	// Just echo data back slowly to waste time
	buf := make([]byte, 1024)

	for {
		time.Sleep(td.cfg.SlowResponseDelay)

		n, err := dc.Conn.Read(buf)
		if err != nil {
			if err != io.EOF {
				td.log.Debug("read error", zap.Error(err))
			}
			break
		}
		dc.BytesRead += int64(n)

		// Echo back
		n, err = dc.Conn.Write(buf[:n])
		dc.BytesWritten += int64(n)
		if err != nil {
			break
		}

		if dc.BytesWritten >= td.cfg.BandwidthWasteTarget {
			break
		}
	}
}

// GetStats returns TCP decoy statistics.
func (td *TCPDecoy) GetStats() TCPDecoyStats {
	return TCPDecoyStats{
		ActiveConnections: int(atomic.LoadInt32(&td.activeConns)),
		TotalConnections:  atomic.LoadUint64(&td.totalConns),
		TotalBytesWritten: atomic.LoadUint64(&td.totalBytes),
		ListenerCount:     len(td.listeners),
	}
}

// TCPDecoyStats contains statistics about TCP decoys.
type TCPDecoyStats struct {
	ActiveConnections int
	TotalConnections  uint64
	TotalBytesWritten uint64
	ListenerCount     int
}

// extractPort extracts port number from "host:port" address.
func extractPort(addr string) int {
	parts := strings.Split(addr, ":")
	if len(parts) < 2 {
		return 0
	}
	var port int
	fmt.Sscanf(parts[len(parts)-1], "%d", &port)
	return port
}
