// Package honeypot — http.go
//
// HTTP honeypot: realistic fake web services with vulnerability detection.
//
// Purpose:
//   Provides convincing HTTP services that mimic real applications,
//   detect common web attack patterns, and waste attacker resources.
//
// Capabilities:
//   - Fake admin panels, login pages, API endpoints
//   - SQL injection detection
//   - XSS attempt detection
//   - Directory traversal detection
//   - Fake file uploads (with virus simulation)
//   - Slow responses to waste attacker bandwidth

package honeypot

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"

	"go.uber.org/zap"
)

// HTTPHoneypotConfig holds configuration for the HTTP honeypot.
type HTTPHoneypotConfig struct {
	// BindAddr is the address to bind the HTTP honeypot.
	// Default: "0.0.0.0:8080"
	BindAddr string

	// ServerHeader is the Server HTTP header value.
	// Default: "Apache/2.4.41 (Ubuntu)"
	ServerHeader string

	// ResponseDelay is the artificial delay before sending responses.
	// This wastes attacker time. Default: 1s.
	ResponseDelay time.Duration

	// MaxRequestBodySize is the maximum request body size to read.
	// Default: 10MB.
	MaxRequestBodySize int64

	// FakeVulnerabilities controls which fake vulnerabilities to expose.
	FakeVulnerabilities []string

	// EventSink receives honeypot events.
	EventSink EventSink
}

// DefaultHTTPHoneypotConfig returns default HTTP honeypot configuration.
func DefaultHTTPHoneypotConfig() HTTPHoneypotConfig {
	return HTTPHoneypotConfig{
		BindAddr:            "0.0.0.0:8080",
		ServerHeader:        "Apache/2.4.41 (Ubuntu)",
		ResponseDelay:       1 * time.Second,
		MaxRequestBodySize:  10 * 1024 * 1024, // 10MB
		FakeVulnerabilities: []string{"sqli", "xss", "lfi", "upload"},
	}
}

// HTTPAttempt captures an HTTP attack attempt.
type HTTPAttempt struct {
	RemoteAddr    string
	Method        string
	Path          string
	UserAgent     string
	Timestamp     time.Time
	AttackType    string
	AttackPayload string
	QueryParams   string
	Headers       map[string]string
}

// HTTPHoneypot implements a realistic HTTP honeypot.
type HTTPHoneypot struct {
	cfg      HTTPHoneypotConfig
	log      *zap.Logger
	server   *http.Server
	mu       sync.Mutex
	attempts []HTTPAttempt
	totalReq int
}

// NewHTTPHoneypot creates a new HTTP honeypot.
func NewHTTPHoneypot(cfg HTTPHoneypotConfig, log *zap.Logger) *HTTPHoneypot {
	return &HTTPHoneypot{
		cfg:      cfg,
		log:      log,
		attempts: make([]HTTPAttempt, 0, 1000),
	}
}

// Start starts the HTTP honeypot server.
func (h *HTTPHoneypot) Start(ctx context.Context) error {
	mux := http.NewServeMux()

	// Register honeypot routes
	mux.HandleFunc("/", h.handleRoot)
	mux.HandleFunc("/admin", h.handleAdmin)
	mux.HandleFunc("/admin/login", h.handleAdminLogin)
	mux.HandleFunc("/api/", h.handleAPI)
	mux.HandleFunc("/upload", h.handleUpload)
	mux.HandleFunc("/db", h.handleDatabase)
	mux.HandleFunc("/.git/", h.handleGit)
	mux.HandleFunc("/.env", h.handleEnv)
	mux.HandleFunc("/phpinfo.php", h.handlePHPInfo)
	mux.HandleFunc("/wp-admin/", h.handleWordPress)

	h.server = &http.Server{
		Addr:         h.cfg.BindAddr,
		Handler:      h.middleware(mux),
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	h.log.Info("HTTP honeypot started",
		zap.String("bind_addr", h.cfg.BindAddr),
		zap.String("server_header", h.cfg.ServerHeader))

	go func() {
		if err := h.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			h.log.Error("HTTP honeypot listen error", zap.Error(err))
		}
	}()

	return nil
}

// Stop stops the HTTP honeypot.
func (h *HTTPHoneypot) Stop() error {
	if h.server != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		return h.server.Shutdown(ctx)
	}
	return nil
}

// middleware wraps all HTTP handlers with logging and attack detection.
func (h *HTTPHoneypot) middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		remoteAddr := r.RemoteAddr

		// Set custom server header
		w.Header().Set("Server", h.cfg.ServerHeader)

		// Artificial delay to waste attacker time
		time.Sleep(h.cfg.ResponseDelay)

		// Detect and log attack patterns
		attempt := h.detectAttackPatterns(r)
		if attempt != nil {
			h.mu.Lock()
			h.attempts = append(h.attempts, *attempt)
			h.mu.Unlock()

			// Emit event
			if h.cfg.EventSink != nil {
				h.cfg.EventSink.Emit(HoneypotEvent{
					Type:       EventTypeHTTPAttempt,
					RemoteAddr: remoteAddr,
					Timestamp:  time.Now(),
					Metadata: map[string]interface{}{
						"method":         attempt.Method,
						"path":           attempt.Path,
						"attack_type":    attempt.AttackType,
						"attack_payload": attempt.AttackPayload,
						"user_agent":     attempt.UserAgent,
					},
				})
			}

			h.log.Warn("HTTP attack detected",
				zap.String("remote_addr", remoteAddr),
				zap.String("method", r.Method),
				zap.String("path", r.URL.Path),
				zap.String("attack_type", attempt.AttackType),
				zap.String("user_agent", r.UserAgent()))
		}

		h.mu.Lock()
		h.totalReq++
		h.mu.Unlock()

		// Pass to handler
		next.ServeHTTP(w, r)

		h.log.Debug("HTTP request",
			zap.String("remote_addr", remoteAddr),
			zap.String("method", r.Method),
			zap.String("path", r.URL.Path),
			zap.Duration("duration", time.Since(start)))
	})
}

// detectAttackPatterns detects common web attack patterns.
func (h *HTTPHoneypot) detectAttackPatterns(r *http.Request) *HTTPAttempt {
	fullURL := r.URL.Path + "?" + r.URL.RawQuery
	userAgent := r.UserAgent()

	attempt := &HTTPAttempt{
		RemoteAddr:  r.RemoteAddr,
		Method:      r.Method,
		Path:        r.URL.Path,
		UserAgent:   userAgent,
		Timestamp:   time.Now(),
		QueryParams: r.URL.RawQuery,
		Headers:     make(map[string]string),
	}

	// Copy selected headers
	for k, v := range r.Header {
		if len(v) > 0 {
			attempt.Headers[k] = v[0]
		}
	}

	// SQL Injection detection
	sqlPatterns := []string{
		"union", "select", "insert", "update", "delete", "drop",
		"'", "\"", "--", "/*", "*/", "xp_", "exec", "execute",
		"||", "&&", "1=1", "1' or '1'='1",
	}
	for _, pattern := range sqlPatterns {
		if strings.Contains(strings.ToLower(fullURL), pattern) {
			attempt.AttackType = "sqli"
			attempt.AttackPayload = fullURL
			return attempt
		}
	}

	// XSS detection
	xssPatterns := []string{
		"<script", "javascript:", "onerror=", "onload=", "onclick=",
		"alert(", "prompt(", "confirm(", "<iframe", "<img",
	}
	for _, pattern := range xssPatterns {
		if strings.Contains(strings.ToLower(fullURL), pattern) {
			attempt.AttackType = "xss"
			attempt.AttackPayload = fullURL
			return attempt
		}
	}

	// Directory traversal detection
	if strings.Contains(fullURL, "..") || strings.Contains(fullURL, "%2e%2e") {
		attempt.AttackType = "lfi"
		attempt.AttackPayload = fullURL
		return attempt
	}

	// Command injection detection
	cmdPatterns := []string{"|", ";", "`", "$", "&&", "||", "\n"}
	for _, pattern := range cmdPatterns {
		if strings.Contains(fullURL, pattern) {
			attempt.AttackType = "command_injection"
			attempt.AttackPayload = fullURL
			return attempt
		}
	}

	// Suspicious user agents (scanners)
	scannerAgents := []string{
		"nikto", "sqlmap", "nmap", "masscan", "zap", "burp",
		"metasploit", "nessus", "acunetix", "w3af",
	}
	for _, scanner := range scannerAgents {
		if strings.Contains(strings.ToLower(userAgent), scanner) {
			attempt.AttackType = "scanner"
			attempt.AttackPayload = userAgent
			return attempt
		}
	}

	return nil
}

// handleRoot serves the fake homepage.
func (h *HTTPHoneypot) handleRoot(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html>
<head>
    <title>Production Web Server</title>
</head>
<body>
    <h1>Welcome to Production Server</h1>
    <p>This is a production web server running critical applications.</p>
    <ul>
        <li><a href="/admin">Admin Panel</a></li>
        <li><a href="/api/users">API Documentation</a></li>
        <li><a href="/db">Database Admin</a></li>
    </ul>
    <p><small>Server version: Apache/2.4.41 (Ubuntu)</small></p>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, html)
}

// handleAdmin serves fake admin panel.
func (h *HTTPHoneypot) handleAdmin(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - Login Required</title>
</head>
<body>
    <h1>Admin Panel</h1>
    <form action="/admin/login" method="POST">
        <label>Username: <input type="text" name="username"></label><br>
        <label>Password: <input type="password" name="password"></label><br>
        <button type="submit">Login</button>
    </form>
    <p><small>Note: This panel is for authorized administrators only.</small></p>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, html)
}

// handleAdminLogin handles fake login attempts.
func (h *HTTPHoneypot) handleAdminLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method == "POST" {
		r.ParseForm()
		username := r.FormValue("username")
		password := r.FormValue("password")

		h.log.Warn("Admin login attempt",
			zap.String("remote_addr", r.RemoteAddr),
			zap.String("username", username),
			zap.String("password", password))

		// Always reject, but waste time
		time.Sleep(2 * time.Second)

		html := `<!DOCTYPE html>
<html>
<head><title>Login Failed</title></head>
<body>
    <h1>Login Failed</h1>
    <p>Invalid username or password.</p>
    <a href="/admin">Try again</a>
</body>
</html>`
		w.WriteHeader(http.StatusUnauthorized)
		fmt.Fprint(w, html)
		return
	}
	http.Redirect(w, r, "/admin", http.StatusSeeOther)
}

// handleAPI serves fake API endpoints.
func (h *HTTPHoneypot) handleAPI(w http.ResponseWriter, r *http.Request) {
	// Fake API response with credentials
	response := `{
  "status": "ok",
  "data": {
    "users": [
      {"id": 1, "username": "admin", "role": "administrator"},
      {"id": 2, "username": "dbadmin", "role": "database_admin"}
    ],
    "api_key": "sk_live_FAKE_API_KEY_HONEYPOT_1234567890",
    "database_url": "postgresql://admin:password123@localhost:5432/production"
  }
}`
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, response)
}

// handleUpload handles fake file uploads.
func (h *HTTPHoneypot) handleUpload(w http.ResponseWriter, r *http.Request) {
	if r.Method == "POST" {
		// Read upload data (limited)
		r.Body = http.MaxBytesReader(w, r.Body, h.cfg.MaxRequestBodySize)
		defer r.Body.Close()

		// Read file content
		file, header, err := r.FormFile("file")
		if err == nil {
			defer file.Close()
			content, _ := io.ReadAll(io.LimitReader(file, 1024))

			h.log.Warn("File upload attempt",
				zap.String("remote_addr", r.RemoteAddr),
				zap.String("filename", header.Filename),
				zap.Int64("size", header.Size))

			// Fake virus detection
			hash := sha256.Sum256(content)
			hashStr := hex.EncodeToString(hash[:])

			response := fmt.Sprintf(`{
  "status": "error",
  "message": "Virus detected in uploaded file",
  "file": "%s",
  "hash": "%s",
  "threat": "Trojan.Generic.KD.12345678"
}`, header.Filename, hashStr)

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusBadRequest)
			fmt.Fprint(w, response)
			return
		}
	}

	html := `<!DOCTYPE html>
<html>
<head><title>File Upload</title></head>
<body>
    <h1>File Upload</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprint(w, html)
}

// handleDatabase serves fake database admin interface.
func (h *HTTPHoneypot) handleDatabase(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html>
<head><title>phpMyAdmin 5.1.1</title></head>
<body>
    <h1>phpMyAdmin</h1>
    <h2>Databases</h2>
    <ul>
        <li>production_users</li>
        <li>production_orders</li>
        <li>production_payments</li>
        <li>admin_credentials</li>
    </ul>
    <p><small>MySQL 8.0.27</small></p>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprint(w, html)
}

// handleGit serves fake Git repository data.
func (h *HTTPHoneypot) handleGit(w http.ResponseWriter, r *http.Request) {
	// Fake .git directory structure
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "ref: refs/heads/master\nFAKE_GIT_REPOSITORY_HONEYPOT")
}

// handleEnv serves fake environment variables.
func (h *HTTPHoneypot) handleEnv(w http.ResponseWriter, r *http.Request) {
	env := `DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=SuperSecret123!
API_KEY=sk_live_FAKE_API_KEY_HONEYPOT
AWS_ACCESS_KEY_ID=AKIA_FAKE_KEY_HONEYPOT
AWS_SECRET_ACCESS_KEY=fake_aws_secret_honeypot_1234567890
STRIPE_SECRET_KEY=sk_live_FAKE_STRIPE_KEY
JWT_SECRET=fake_jwt_secret_honeypot_do_not_use
`
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, env)
}

// handlePHPInfo serves fake PHP info page.
func (h *HTTPHoneypot) handlePHPInfo(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html><head><title>phpinfo()</title></head>
<body>
<h1>PHP Version 7.4.3</h1>
<table>
    <tr><td>System</td><td>Linux web-server 5.4.0-125-generic x86_64</td></tr>
    <tr><td>Server API</td><td>Apache 2.0 Handler</td></tr>
    <tr><td>allow_url_fopen</td><td>On</td></tr>
    <tr><td>disable_functions</td><td>no value</td></tr>
</table>
</body></html>`
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprint(w, html)
}

// handleWordPress serves fake WordPress admin.
func (h *HTTPHoneypot) handleWordPress(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html>
<head><title>WordPress Admin</title></head>
<body>
    <h1>WordPress Administration</h1>
    <form method="POST">
        <label>Username: <input type="text" name="user"></label><br>
        <label>Password: <input type="password" name="pass"></label><br>
        <button type="submit">Log In</button>
    </form>
    <p><small>WordPress 6.1.1</small></p>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprint(w, html)
}

// GetAttempts returns all recorded HTTP attempts.
func (h *HTTPHoneypot) GetAttempts() []HTTPAttempt {
	h.mu.Lock()
	defer h.mu.Unlock()
	result := make([]HTTPAttempt, len(h.attempts))
	copy(result, h.attempts)
	return result
}

// GetStats returns honeypot statistics.
func (h *HTTPHoneypot) GetStats() HoneypotStats {
	h.mu.Lock()
	defer h.mu.Unlock()

	attackTypes := make(map[string]int)
	for _, attempt := range h.attempts {
		attackTypes[attempt.AttackType]++
	}

	return HoneypotStats{
		Type:             "http",
		TotalConnections: h.totalReq,
		TotalAttempts:    len(h.attempts),
		UniqueIPs:        h.countUniqueIPs(),
		Metadata: map[string]interface{}{
			"attack_types": attackTypes,
		},
	}
}

// countUniqueIPs counts unique IP addresses in attempts.
func (h *HTTPHoneypot) countUniqueIPs() int {
	seen := make(map[string]bool)
	for _, attempt := range h.attempts {
		ip := strings.Split(attempt.RemoteAddr, ":")[0]
		seen[ip] = true
	}
	return len(seen)
}

var _ Honeypot = (*HTTPHoneypot)(nil)
