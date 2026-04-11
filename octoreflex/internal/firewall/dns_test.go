// Package firewall — dns_test.go
//
// Unit tests for DNS filtering.

package firewall

import (
	"context"
	"os"
	"path/filepath"
	"testing"

	"go.uber.org/zap/zaptest"
)

func TestDNSFilterBlocklist(t *testing.T) {
	logger := zaptest.NewLogger(t)

	// Create temporary blocklist file
	tmpDir := t.TempDir()
	blocklistPath := filepath.Join(tmpDir, "blocklist.txt")
	blocklist := `# Test blocklist
malware.com
evil.net
phishing.org

# Comment line
badsite.io
`
	if err := os.WriteFile(blocklistPath, []byte(blocklist), 0644); err != nil {
		t.Fatalf("failed to write blocklist: %v", err)
	}

	cfg := DNSConfig{
		BlocklistPath: blocklistPath,
		NftablesTable: "test",
	}

	dns, err := NewDNSFilter(cfg, logger)
	if err != nil {
		t.Fatalf("NewDNSFilter() failed: %v", err)
	}

	tests := []struct {
		domain  string
		blocked bool
	}{
		{"malware.com", true},
		{"evil.net", true},
		{"phishing.org", true},
		{"badsite.io", true},
		{"sub.malware.com", true}, // Subdomain should be blocked
		{"google.com", false},
		{"github.com", false},
	}

	for _, tt := range tests {
		t.Run(tt.domain, func(t *testing.T) {
			blocked := dns.IsBlocked(tt.domain)
			if blocked != tt.blocked {
				t.Errorf("IsBlocked(%q) = %v, want %v", tt.domain, blocked, tt.blocked)
			}
		})
	}
}

func TestDNSFilterAddRemove(t *testing.T) {
	logger := zaptest.NewLogger(t)

	tmpDir := t.TempDir()
	blocklistPath := filepath.Join(tmpDir, "empty.txt")
	if err := os.WriteFile(blocklistPath, []byte(""), 0644); err != nil {
		t.Fatalf("failed to write empty blocklist: %v", err)
	}

	cfg := DNSConfig{
		BlocklistPath: blocklistPath,
		NftablesTable: "test",
	}

	dns, err := NewDNSFilter(cfg, logger)
	if err != nil {
		t.Fatalf("NewDNSFilter() failed: %v", err)
	}

	ctx := context.Background()

	// Add domain
	domain := "newmalware.com"
	if err := dns.AddDomain(ctx, domain); err != nil {
		t.Fatalf("AddDomain() failed: %v", err)
	}

	if !dns.IsBlocked(domain) {
		t.Errorf("expected %q to be blocked after AddDomain()", domain)
	}

	// Remove domain
	if err := dns.RemoveDomain(ctx, domain); err != nil {
		t.Fatalf("RemoveDomain() failed: %v", err)
	}

	if dns.IsBlocked(domain) {
		t.Errorf("expected %q to not be blocked after RemoveDomain()", domain)
	}
}

func TestDNSFilterInvalidDomain(t *testing.T) {
	logger := zaptest.NewLogger(t)

	tmpDir := t.TempDir()
	blocklistPath := filepath.Join(tmpDir, "blocklist.txt")

	// Blocklist with invalid domains
	blocklist := `valid-domain.com
invalid domain with spaces
-invalid-start.com
invalid-end-.com
no-tld
toolonggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg.com
`
	if err := os.WriteFile(blocklistPath, []byte(blocklist), 0644); err != nil {
		t.Fatalf("failed to write blocklist: %v", err)
	}

	cfg := DNSConfig{
		BlocklistPath: blocklistPath,
		NftablesTable: "test",
	}

	dns, err := NewDNSFilter(cfg, logger)
	if err != nil {
		t.Fatalf("NewDNSFilter() failed: %v", err)
	}

	// Only valid domain should be loaded
	domains := dns.GetBlockedDomains()
	if len(domains) != 1 {
		t.Errorf("expected 1 valid domain, got %d", len(domains))
	}

	if !dns.IsBlocked("valid-domain.com") {
		t.Error("expected valid-domain.com to be blocked")
	}
}

func TestDNSFilterPIDTracking(t *testing.T) {
	logger := zaptest.NewLogger(t)

	tmpDir := t.TempDir()
	blocklistPath := filepath.Join(tmpDir, "blocklist.txt")
	if err := os.WriteFile(blocklistPath, []byte("malware.com\n"), 0644); err != nil {
		t.Fatalf("failed to write blocklist: %v", err)
	}

	cfg := DNSConfig{
		BlocklistPath: blocklistPath,
		NftablesTable: "test",
	}

	dns, err := NewDNSFilter(cfg, logger)
	if err != nil {
		t.Fatalf("NewDNSFilter() failed: %v", err)
	}

	ctx := context.Background()

	// Enable for PID
	pid := uint32(12345)
	if err := dns.EnableForPID(ctx, pid); err != nil {
		t.Fatalf("EnableForPID() failed: %v", err)
	}

	dns.mu.RLock()
	if _, exists := dns.pids[pid]; !exists {
		t.Error("expected PID to be tracked after EnableForPID()")
	}
	dns.mu.RUnlock()

	// Disable for PID
	if err := dns.DisableForPID(ctx, pid); err != nil {
		t.Fatalf("DisableForPID() failed: %v", err)
	}

	dns.mu.RLock()
	if _, exists := dns.pids[pid]; exists {
		t.Error("expected PID to not be tracked after DisableForPID()")
	}
	dns.mu.RUnlock()
}

func BenchmarkDNSFilterIsBlocked(b *testing.B) {
	logger := zaptest.NewLogger(b)

	tmpDir := b.TempDir()
	blocklistPath := filepath.Join(tmpDir, "blocklist.txt")

	// Create blocklist with 1000 domains
	domains := make([]string, 1000)
	for i := 0; i < 1000; i++ {
		domains[i] = "malware" + string(rune(i)) + ".com"
	}
	blocklist := ""
	for _, d := range domains {
		blocklist += d + "\n"
	}
	if err := os.WriteFile(blocklistPath, []byte(blocklist), 0644); err != nil {
		b.Fatalf("failed to write blocklist: %v", err)
	}

	cfg := DNSConfig{
		BlocklistPath: blocklistPath,
		NftablesTable: "test",
	}

	dns, err := NewDNSFilter(cfg, logger)
	if err != nil {
		b.Fatalf("NewDNSFilter() failed: %v", err)
	}

	testDomains := []string{
		"malware0.com",      // Blocked
		"sub.malware0.com",  // Blocked (subdomain)
		"google.com",        // Not blocked
		"malware999.com",    // Blocked
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		dns.IsBlocked(testDomains[i%len(testDomains)])
	}
}
