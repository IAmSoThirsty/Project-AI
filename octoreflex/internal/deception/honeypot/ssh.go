// Package honeypot — ssh.go
//
// SSH honeypot: realistic fake SSH service with authentication tracking.
//
// Purpose:
//   Provides a convincing SSH service that logs all connection attempts,
//   authentication credentials, and command execution patterns. Designed
//   to waste attacker time and resources while gathering intelligence.
//
// Capabilities:
//   - Realistic SSH banner and version negotiation
//   - Password authentication (always fails after delay)
//   - Key-based authentication (always fails)
//   - Fake shell environment with common commands
//   - Credential harvesting for threat intelligence
//   - Command pattern analysis
//   - CPU/bandwidth cost amplification through slow responses

package honeypot

import (
	"bufio"
	"context"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net"
	"strings"
	"sync"
	"time"

	"go.uber.org/zap"
)

// SSHHoneypotConfig holds configuration for the SSH honeypot.
type SSHHoneypotConfig struct {
	// BindAddr is the address to bind the SSH honeypot.
	// Default: "0.0.0.0:2222" (non-standard SSH port to avoid conflicts).
	BindAddr string

	// Banner is the SSH version banner sent to clients.
	// Default: "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
	Banner string

	// AuthDelay is the artificial delay before rejecting authentication.
	// This wastes attacker time. Default: 3s.
	AuthDelay time.Duration

	// CommandDelay is the artificial delay before responding to commands.
	// Default: 500ms.
	CommandDelay time.Duration

	// MaxConnectionTime is the maximum time a connection can stay open.
	// Default: 5 minutes.
	MaxConnectionTime time.Duration

	// MaxCommandsPerSession limits commands executed per session.
	// Default: 50.
	MaxCommandsPerSession int

	// PrivateKey is the RSA private key for the SSH server.
	// If nil, a new key is generated on startup.
	PrivateKey *rsa.PrivateKey

	// EventSink receives honeypot events.
	EventSink EventSink
}

// DefaultSSHHoneypotConfig returns default SSH honeypot configuration.
func DefaultSSHHoneypotConfig() SSHHoneypotConfig {
	return SSHHoneypotConfig{
		BindAddr:              "0.0.0.0:2222",
		Banner:                "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5",
		AuthDelay:             3 * time.Second,
		CommandDelay:          500 * time.Millisecond,
		MaxConnectionTime:     5 * time.Minute,
		MaxCommandsPerSession: 50,
	}
}

// SSHAttempt captures an SSH authentication attempt.
type SSHAttempt struct {
	RemoteAddr     string
	Username       string
	Password       string
	PublicKey      string
	Timestamp      time.Time
	SessionID      string
	AuthMethod     string
	CommandCount   int
	CommandHistory []string
	TimeInSession  time.Duration
}

// SSHHoneypot implements a realistic SSH honeypot.
type SSHHoneypot struct {
	cfg      SSHHoneypotConfig
	log      *zap.Logger
	listener net.Listener
	mu       sync.Mutex
	attempts []SSHAttempt
	active   int
	totalConn int
}

// NewSSHHoneypot creates a new SSH honeypot.
func NewSSHHoneypot(cfg SSHHoneypotConfig, log *zap.Logger) (*SSHHoneypot, error) {
	// Generate host key if not provided
	if cfg.PrivateKey == nil {
		key, err := rsa.GenerateKey(rand.Reader, 2048)
		if err != nil {
			return nil, fmt.Errorf("generate RSA key: %w", err)
		}
		cfg.PrivateKey = key
	}

	return &SSHHoneypot{
		cfg:      cfg,
		log:      log,
		attempts: make([]SSHAttempt, 0, 1000),
	}, nil
}

// Start starts the SSH honeypot listener.
func (h *SSHHoneypot) Start(ctx context.Context) error {
	lis, err := net.Listen("tcp", h.cfg.BindAddr)
	if err != nil {
		return fmt.Errorf("listen on %s: %w", h.cfg.BindAddr, err)
	}
	h.listener = lis

	h.log.Info("SSH honeypot started",
		zap.String("bind_addr", h.cfg.BindAddr),
		zap.String("banner", h.cfg.Banner))

	go h.acceptLoop(ctx)
	return nil
}

// Stop stops the SSH honeypot.
func (h *SSHHoneypot) Stop() error {
	if h.listener != nil {
		return h.listener.Close()
	}
	return nil
}

// acceptLoop accepts incoming SSH connections.
func (h *SSHHoneypot) acceptLoop(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		conn, err := h.listener.Accept()
		if err != nil {
			if !strings.Contains(err.Error(), "use of closed network connection") {
				h.log.Error("accept connection", zap.Error(err))
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

// handleConnection handles a single SSH connection.
func (h *SSHHoneypot) handleConnection(ctx context.Context, conn net.Conn, connID int) {
	defer func() {
		conn.Close()
		h.mu.Lock()
		h.active--
		h.mu.Unlock()
	}()

	// Set maximum connection time
	sessionDeadline := time.Now().Add(h.cfg.MaxConnectionTime)
	conn.SetDeadline(sessionDeadline)

	remoteAddr := conn.RemoteAddr().String()
	sessionStart := time.Now()
	sessionID := fmt.Sprintf("ssh_%d_%s", connID, generateSessionID())

	h.log.Info("SSH connection received",
		zap.String("remote_addr", remoteAddr),
		zap.String("session_id", sessionID))

	attempt := SSHAttempt{
		RemoteAddr:     remoteAddr,
		Timestamp:      sessionStart,
		SessionID:      sessionID,
		CommandHistory: make([]string, 0, 50),
	}

	// Send SSH banner
	_, _ = conn.Write([]byte(h.cfg.Banner + "\r\n"))

	// Simulate SSH protocol exchange (simplified)
	h.simulateSSHProtocol(conn, &attempt)

	// Update attempt duration
	attempt.TimeInSession = time.Since(sessionStart)

	// Record attempt
	h.mu.Lock()
	h.attempts = append(h.attempts, attempt)
	h.mu.Unlock()

	// Emit event
	if h.cfg.EventSink != nil {
		h.cfg.EventSink.Emit(HoneypotEvent{
			Type:       EventTypeSSHAttempt,
			RemoteAddr: remoteAddr,
			Timestamp:  time.Now(),
			Metadata: map[string]interface{}{
				"username":      attempt.Username,
				"password":      attempt.Password,
				"session_id":    sessionID,
				"command_count": attempt.CommandCount,
				"duration_ms":   attempt.TimeInSession.Milliseconds(),
			},
		})
	}

	h.log.Warn("SSH session ended",
		zap.String("remote_addr", remoteAddr),
		zap.String("session_id", sessionID),
		zap.String("username", attempt.Username),
		zap.Int("commands", attempt.CommandCount),
		zap.Duration("duration", attempt.TimeInSession))
}

// simulateSSHProtocol simulates a simplified SSH protocol exchange.
func (h *SSHHoneypot) simulateSSHProtocol(conn net.Conn, attempt *SSHAttempt) {
	reader := bufio.NewReader(conn)

	// Read client banner
	clientBanner, _ := reader.ReadString('\n')
	h.log.Debug("SSH client banner", zap.String("banner", strings.TrimSpace(clientBanner)))

	// Send authentication prompt
	_, _ = conn.Write([]byte("login as: "))
	username, _ := reader.ReadString('\n')
	attempt.Username = strings.TrimSpace(username)

	// Artificial delay to waste attacker time
	time.Sleep(h.cfg.AuthDelay)

	// Send password prompt
	_, _ = conn.Write([]byte(fmt.Sprintf("%s@honeypot's password: ", attempt.Username)))
	password, _ := reader.ReadString('\n')
	attempt.Password = strings.TrimSpace(password)
	attempt.AuthMethod = "password"

	// Another delay to simulate authentication check
	time.Sleep(h.cfg.AuthDelay)

	// Decide whether to grant fake access
	// Grant fake access in 30% of cases to keep attacker engaged
	grantAccess := len(attempt.Password) > 0 && (time.Now().Unix()%10 < 3)

	if !grantAccess {
		_, _ = conn.Write([]byte("Permission denied, please try again.\r\n"))
		return
	}

	// Grant fake shell access
	_, _ = conn.Write([]byte("Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-125-generic x86_64)\r\n\r\n"))
	_, _ = conn.Write([]byte("Last login: Mon Jan 15 14:32:11 2024 from 10.0.0.5\r\n"))
	h.provideFakeShell(conn, reader, attempt)
}

// provideFakeShell provides a fake interactive shell.
func (h *SSHHoneypot) provideFakeShell(conn net.Conn, reader *bufio.Reader, attempt *SSHAttempt) {
	prompt := fmt.Sprintf("%s@honeypot:~$ ", attempt.Username)

	for attempt.CommandCount < h.cfg.MaxCommandsPerSession {
		// Send prompt
		_, err := conn.Write([]byte(prompt))
		if err != nil {
			return
		}

		// Read command
		command, err := reader.ReadString('\n')
		if err != nil {
			return
		}
		command = strings.TrimSpace(command)
		if command == "" {
			continue
		}

		attempt.CommandCount++
		attempt.CommandHistory = append(attempt.CommandHistory, command)

		h.log.Debug("SSH command executed",
			zap.String("session_id", attempt.SessionID),
			zap.String("command", command))

		// Artificial delay to slow down attacker
		time.Sleep(h.cfg.CommandDelay)

		// Generate fake response
		response := h.generateFakeResponse(command)
		_, _ = conn.Write([]byte(response + "\r\n"))

		// Exit on explicit exit/logout
		if command == "exit" || command == "logout" {
			return
		}
	}

	// Limit reached
	_, _ = conn.Write([]byte("Connection to honeypot closed.\r\n"))
}

// generateFakeResponse generates a fake response for common commands.
func (h *SSHHoneypot) generateFakeResponse(cmd string) string {
	cmdLower := strings.ToLower(strings.TrimSpace(cmd))
	fields := strings.Fields(cmdLower)
	if len(fields) == 0 {
		return ""
	}

	base := fields[0]

	// Map of common commands to fake responses
	responses := map[string]string{
		"whoami":   "www-data",
		"id":       "uid=33(www-data) gid=33(www-data) groups=33(www-data)",
		"hostname": "web-server-prod-01",
		"pwd":      "/home/www-data",
		"uname":    "Linux web-server-prod-01 5.4.0-125-generic #141-Ubuntu SMP x86_64 GNU/Linux",
		"date":     time.Now().Format("Mon Jan 2 15:04:05 MST 2006"),
		"uptime":   "14:32:11 up 42 days, 3:15, 1 user, load average: 0.42, 0.35, 0.28",
	}

	if resp, exists := responses[base]; exists {
		return resp
	}

	switch base {
	case "ls", "dir":
		return "backup.sql  config.php  database  logs  passwords.txt  secrets  uploads"
	case "cat":
		if len(fields) > 1 && strings.Contains(fields[1], "password") {
			return "admin:$6$fakehash$verylonghashstring...\nroot:$6$anotherfake$morefakedata..."
		}
		return "[fake file contents]"
	case "ps", "top":
		return `  PID TTY          TIME CMD
 1234 ?        00:00:01 nginx
 1235 ?        00:00:00 php-fpm
 1236 ?        00:00:02 mysql
 1237 ?        00:00:00 sshd`
	case "netstat", "ss":
		return `tcp   LISTEN  0  128  0.0.0.0:80      0.0.0.0:*
tcp   LISTEN  0  128  0.0.0.0:443     0.0.0.0:*
tcp   LISTEN  0  128  0.0.0.0:3306    0.0.0.0:*`
	case "ifconfig", "ip":
		return `eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.0.0.42  netmask 255.255.255.0  broadcast 10.0.0.255`
	case "sudo":
		// Fake sudo prompt - always fail after delay
		return "[sudo] password for www-data: \nSorry, user www-data is not allowed to execute this command."
	case "wget", "curl":
		// Fake download - waste bandwidth
		return "Connecting to example.com... connected.\nHTTP request sent, awaiting response... 200 OK\nLength: 1048576 (1.0M) [text/html]\nSaving to: 'index.html'\n\n100%[===================>] 1,048,576   2.00MB/s   in 0.5s\n\n'index.html' saved [1048576/1048576]"
	case "find":
		// Fake find with interesting files
		return "/var/www/backup.sql\n/etc/shadow\n/root/.ssh/id_rsa\n/opt/secrets/api_keys.txt"
	default:
		return fmt.Sprintf("%s: command not found", base)
	}
}

// GetAttempts returns all recorded SSH attempts.
func (h *SSHHoneypot) GetAttempts() []SSHAttempt {
	h.mu.Lock()
	defer h.mu.Unlock()
	result := make([]SSHAttempt, len(h.attempts))
	copy(result, h.attempts)
	return result
}

// GetStats returns honeypot statistics.
func (h *SSHHoneypot) GetStats() HoneypotStats {
	h.mu.Lock()
	defer h.mu.Unlock()

	return HoneypotStats{
		Type:             "ssh",
		TotalConnections: h.totalConn,
		ActiveSessions:   h.active,
		TotalAttempts:    len(h.attempts),
		UniqueIPs:        h.countUniqueIPs(),
	}
}

// countUniqueIPs counts unique IP addresses in attempts.
func (h *SSHHoneypot) countUniqueIPs() int {
	seen := make(map[string]bool)
	for _, attempt := range h.attempts {
		// Extract IP from "IP:port"
		ip := strings.Split(attempt.RemoteAddr, ":")[0]
		seen[ip] = true
	}
	return len(seen)
}

// generateSessionID generates a random session ID.
func generateSessionID() string {
	b := make([]byte, 8)
	rand.Read(b)
	hash := sha256.Sum256(b)
	return hex.EncodeToString(hash[:8])
}

var _ Honeypot = (*SSHHoneypot)(nil)
