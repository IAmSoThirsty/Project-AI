// Adversarial simulation: Ransomware mass file encryption
//
// This test simulates a ransomware attack that:
//   1. Opens hundreds of files rapidly
//   2. Writes random data (simulating encryption)
//   3. Measures time to containment
//
// Expected behavior:
//   - High file_open event rate triggers anomaly spike
//   - Process escalated to ISOLATED within 3 seconds
//   - Further file writes blocked by eBPF hook
//
// Target containment latency: < 3s (spec requirement)

package adversarial

import (
	"crypto/rand"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestRansomwareSimulation(t *testing.T) {
	// Create temporary directory with test files
	tmpDir := t.TempDir()
	
	// Create 100 test files
	fileCount := 100
	for i := 0; i < fileCount; i++ {
		path := filepath.Join(tmpDir, fmt.Sprintf("file_%04d.txt", i))
		content := fmt.Sprintf("Original content %d\n", i)
		if err := os.WriteFile(path, []byte(content), 0644); err != nil {
			t.Fatalf("Failed to create test file: %v", err)
		}
	}
	
	t.Logf("Created %d test files in %s", fileCount, tmpDir)
	
	// Simulate ransomware behavior
	startTime := time.Now()
	encryptedCount := 0
	encryptionKey := make([]byte, 32)
	rand.Read(encryptionKey)
	
	for i := 0; i < fileCount; i++ {
		path := filepath.Join(tmpDir, fmt.Sprintf("file_%04d.txt", i))
		
		// Read original
		original, err := os.ReadFile(path)
		if err != nil {
			t.Logf("Read error at file %d (containment may be active): %v", i, err)
			break
		}
		
		// "Encrypt" (XOR with random key for simulation)
		encrypted := make([]byte, len(original))
		for j := range original {
			encrypted[j] = original[j] ^ encryptionKey[j%len(encryptionKey)]
		}
		
		// Write back
		if err := os.WriteFile(path, encrypted, 0644); err != nil {
			t.Logf("Write blocked at file %d after %.2fs", i, time.Since(startTime).Seconds())
			break
		}
		
		encryptedCount++
		
		// Minimal delay (ransomware is fast)
		time.Sleep(10 * time.Millisecond)
	}
	
	elapsed := time.Since(startTime)
	
	t.Logf("Simulation stats:")
	t.Logf("  Files encrypted: %d / %d", encryptedCount, fileCount)
	t.Logf("  Time elapsed: %.2fs", elapsed.Seconds())
	t.Logf("  Encryption rate: %.1f files/sec", float64(encryptedCount)/elapsed.Seconds())
	
	// Verify containment happened
	if encryptedCount >= fileCount {
		t.Errorf("WARNING: All files encrypted without containment!")
		t.Logf("This indicates OCTOREFLEX did not detect the attack pattern.")
	} else {
		t.Logf("SUCCESS: Containment triggered after %d files", encryptedCount)
	}
	
	// Check containment latency (should be < 3s per spec)
	if elapsed > 3*time.Second && encryptedCount >= fileCount {
		t.Errorf("Containment latency %.2fs exceeds 3s threshold", elapsed.Seconds())
	}
}

func TestRansomwareWithHighEntropy(t *testing.T) {
	// Variant: Write truly random data (high entropy signal)
	tmpDir := t.TempDir()
	
	startTime := time.Now()
	filesWritten := 0
	
	for i := 0; i < 1000; i++ {
		path := filepath.Join(tmpDir, fmt.Sprintf("random_%04d.bin", i))
		
		// Generate random data
		randomData := make([]byte, 4096)
		if _, err := io.ReadFull(rand.Reader, randomData); err != nil {
			t.Fatalf("Failed to generate random data: %v", err)
		}
		
		// Attempt write
		if err := os.WriteFile(path, randomData, 0644); err != nil {
			t.Logf("Write blocked at file %d after %.2fs", i, time.Since(startTime).Seconds())
			break
		}
		
		filesWritten++
		time.Sleep(5 * time.Millisecond)
	}
	
	elapsed := time.Since(startTime)
	
	t.Logf("High-entropy write test:")
	t.Logf("  Files written: %d", filesWritten)
	t.Logf("  Time to containment: %.2fs", elapsed.Seconds())
	
	if filesWritten >= 1000 {
		t.Error("No containment detected for high-entropy writes")
	}
}

func TestRansomwareFileRenaming(t *testing.T) {
	// Ransomware often renames files with .encrypted extension
	tmpDir := t.TempDir()
	
	// Create victim files
	for i := 0; i < 50; i++ {
		path := filepath.Join(tmpDir, fmt.Sprintf("document_%d.txt", i))
		os.WriteFile(path, []byte("important data"), 0644)
	}
	
	startTime := time.Now()
	renamedCount := 0
	
	for i := 0; i < 50; i++ {
		oldPath := filepath.Join(tmpDir, fmt.Sprintf("document_%d.txt", i))
		newPath := filepath.Join(tmpDir, fmt.Sprintf("document_%d.txt.encrypted", i))
		
		// Ransomware pattern: read, encrypt, rename
		data, err := os.ReadFile(oldPath)
		if err != nil {
			t.Logf("Read blocked at file %d", i)
			break
		}
		
		// Write encrypted version
		encrypted := make([]byte, len(data))
		for j := range data {
			encrypted[j] = data[j] ^ 0xAA
		}
		
		if err := os.WriteFile(newPath, encrypted, 0644); err != nil {
			t.Logf("Write blocked at file %d", i)
			break
		}
		
		// Remove original
		if err := os.Remove(oldPath); err != nil {
			t.Logf("Delete blocked at file %d", i)
			break
		}
		
		renamedCount++
		time.Sleep(20 * time.Millisecond)
	}
	
	elapsed := time.Since(startTime)
	
	t.Logf("Rename attack test:")
	t.Logf("  Files renamed: %d / 50", renamedCount)
	t.Logf("  Containment latency: %.2fs", elapsed.Seconds())
	
	if renamedCount >= 50 {
		t.Error("All files renamed without containment")
	}
}

func BenchmarkRansomwareEncryptionRate(b *testing.B) {
	// Measure baseline encryption rate without containment
	tmpDir := b.TempDir()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		path := filepath.Join(tmpDir, fmt.Sprintf("bench_%d.bin", i))
		data := make([]byte, 4096)
		rand.Read(data)
		os.WriteFile(path, data, 0644)
	}
}
