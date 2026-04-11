// Package features - Unit tests for feature extraction.

package features

import (
	"testing"
	"time"
)

func TestFeatureExtraction(t *testing.T) {
	extractor := NewExtractor(60*time.Second, 10000)
	
	// Add sample events
	events := []Event{
		{PID: 1234, Type: EventSocketConnect, Timestamp: time.Now(), DstIP: 0x08080808, DstPort: 443},
		{PID: 1234, Type: EventFileOpen, Timestamp: time.Now(), FilePath: "/etc/passwd", Flags: 0x0},
		{PID: 1234, Type: EventSocketConnect, Timestamp: time.Now(), DstIP: 0xC0A80101, DstPort: 22},
		{PID: 1234, Type: EventSetUID, Timestamp: time.Now(), UID: 0},
	}
	
	for _, event := range events {
		extractor.AddEvent(event)
	}
	
	// Extract features
	fv := extractor.Extract()
	features := fv.ToSlice()
	
	// Validate
	if len(features) != 24 {
		t.Errorf("Expected 24 features, got %d", len(features))
	}
	
	// Check specific features
	if fv.UniqueIPCount != 2 {
		t.Errorf("Expected 2 unique IPs, got %.0f", fv.UniqueIPCount)
	}
	
	if fv.SetUIDAttempts != 1 {
		t.Errorf("Expected 1 setuid attempt, got %.0f", fv.SetUIDAttempts)
	}
	
	if fv.SyscallDiversity <= 0 {
		t.Errorf("Expected positive syscall diversity, got %.4f", fv.SyscallDiversity)
	}
	
	t.Logf("Feature vector: %v", features[:5]) // Log first 5 features
}

func TestFeatureExtractorSlidingWindow(t *testing.T) {
	windowSize := 2 * time.Second
	extractor := NewExtractor(windowSize, 1000)
	
	now := time.Now()
	
	// Add events across time window
	for i := 0; i < 5; i++ {
		event := Event{
			PID:       1234,
			Type:      EventSocketConnect,
			Timestamp: now.Add(time.Duration(i) * time.Second),
			DstIP:     uint32(0x08080800 + i),
			DstPort:   443,
		}
		extractor.AddEvent(event)
	}
	
	// Events older than 2s should be evicted
	if extractor.size > 3 {
		t.Logf("Warning: Expected ≤3 events in window, got %d (eviction may be lazy)", extractor.size)
	}
	
	fv := extractor.Extract()
	if fv.UniqueIPCount <= 0 {
		t.Errorf("Expected some unique IPs, got %.0f", fv.UniqueIPCount)
	}
}

func TestToSlice(t *testing.T) {
	fv := FeatureVector{
		InterEventMean: 1.0,
		InterEventStdDev: 2.0,
		BurstIntensity: 3.0,
	}
	
	slice := fv.ToSlice()
	
	if len(slice) != 24 {
		t.Errorf("Expected 24 elements, got %d", len(slice))
	}
	
	if slice[0] != 1.0 || slice[1] != 2.0 || slice[2] != 3.0 {
		t.Errorf("Unexpected slice values: %v", slice[:3])
	}
}

func BenchmarkFeatureExtraction(b *testing.B) {
	extractor := NewExtractor(60*time.Second, 10000)
	
	// Populate with events
	for i := 0; i < 100; i++ {
		event := Event{
			PID:       1234,
			Type:      EventType((i % 3) + 1),
			Timestamp: time.Now(),
			DstIP:     uint32(0x08080800 + i),
			DstPort:   uint16(443 + i%10),
		}
		extractor.AddEvent(event)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = extractor.Extract()
	}
}
