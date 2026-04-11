// Package inference - Benchmark tests for ML inference engine.
//
// Validates sub-millisecond inference latency requirement.

package inference

import (
	"testing"
	"time"

	"github.com/octoreflex/octoreflex/internal/detection/ml/features"
	"github.com/octoreflex/octoreflex/internal/detection/ml/models"
	"github.com/octoreflex/octoreflex/internal/detection/ml/training"
)

// BenchmarkInferenceLatency benchmarks end-to-end inference latency.
// Target: <1ms (1000µs) p99 latency.
func BenchmarkInferenceLatency(b *testing.B) {
	// Setup
	config := DefaultEngineConfig()
	engine, err := NewEngine(config)
	if err != nil {
		b.Fatal(err)
	}
	
	// Train models on synthetic data
	data := training.GenerateSyntheticDataset(1000, 24, 0.1)
	
	// Train Isolation Forest
	iforest := models.NewIsolationForest(models.DefaultIsolationForestConfig())
	if err := iforest.Train(data.Features); err != nil {
		b.Fatal(err)
	}
	
	// Initialize Neural Network (stub)
	neuralNet := models.NewSequenceModel(models.DefaultSequenceModelConfig())
	neuralNet.InitializeWeights()
	
	engine.SetModels(iforest, neuralNet)
	
	// Add some events to build sequence
	for i := 0; i < 10; i++ {
		event := features.Event{
			PID:       1234,
			Type:      features.EventType((i % 3) + 1),
			Timestamp: time.Now(),
			DstIP:     0x08080808, // 8.8.8.8
			DstPort:   443,
		}
		engine.ProcessEvent(event)
	}
	
	// Benchmark
	b.ResetTimer()
	
	var latencies []time.Duration
	for i := 0; i < b.N; i++ {
		start := time.Now()
		_, err := engine.Score()
		latency := time.Since(start)
		
		if err != nil && err.Error() != "no models loaded" {
			b.Errorf("inference error: %v", err)
		}
		
		latencies = append(latencies, latency)
	}
	
	b.StopTimer()
	
	// Report statistics
	if len(latencies) > 0 {
		p50, p99, p999 := percentiles(latencies)
		b.ReportMetric(float64(p50.Microseconds()), "p50_µs")
		b.ReportMetric(float64(p99.Microseconds()), "p99_µs")
		b.ReportMetric(float64(p999.Microseconds()), "p999_µs")
		
		// Validate <1ms p99 requirement
		if p99 > time.Millisecond {
			b.Errorf("FAILED: p99 latency %v exceeds 1ms requirement", p99)
		}
	}
}

// BenchmarkIsolationForestOnly benchmarks Isolation Forest alone.
func BenchmarkIsolationForestOnly(b *testing.B) {
	data := training.GenerateSyntheticDataset(1000, 24, 0.1)
	iforest := models.NewIsolationForest(models.DefaultIsolationForestConfig())
	if err := iforest.Train(data.Features); err != nil {
		b.Fatal(err)
	}
	
	testSample := data.Features[0]
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := iforest.Score(testSample)
		if err != nil {
			b.Fatal(err)
		}
	}
}

// BenchmarkNeuralNetworkOnly benchmarks neural network alone.
func BenchmarkNeuralNetworkOnly(b *testing.B) {
	neuralNet := models.NewSequenceModel(models.DefaultSequenceModelConfig())
	neuralNet.InitializeWeights()
	
	// Create test sequence
	sequence := make([][]float64, 10)
	for i := range sequence {
		sequence[i] = make([]float64, 24)
		for j := range sequence[i] {
			sequence[i][j] = float64(i*j) / 100.0
		}
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := neuralNet.Predict(sequence)
		if err != nil {
			b.Fatal(err)
		}
	}
}

// BenchmarkFeatureExtraction benchmarks feature extraction.
func BenchmarkFeatureExtraction(b *testing.B) {
	extractor := features.NewExtractor(60*time.Second, 10000)
	
	// Add some events
	for i := 0; i < 100; i++ {
		event := features.Event{
			PID:       1234,
			Type:      features.EventType((i % 3) + 1),
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

// BenchmarkConcurrentInference benchmarks parallel inference.
func BenchmarkConcurrentInference(b *testing.B) {
	config := DefaultEngineConfig()
	engine, err := NewEngine(config)
	if err != nil {
		b.Fatal(err)
	}
	
	// Setup models
	data := training.GenerateSyntheticDataset(1000, 24, 0.1)
	iforest := models.NewIsolationForest(models.DefaultIsolationForestConfig())
	if err := iforest.Train(data.Features); err != nil {
		b.Fatal(err)
	}
	engine.SetModels(iforest, nil)
	
	// Add events
	for i := 0; i < 10; i++ {
		event := features.Event{
			PID:       1234,
			Type:      features.EventType((i % 3) + 1),
			Timestamp: time.Now(),
		}
		engine.ProcessEvent(event)
	}
	
	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			_, err := engine.Score()
			if err != nil && err.Error() != "no models loaded" {
				b.Errorf("inference error: %v", err)
			}
		}
	})
}

// --- Helper functions ---

func percentiles(latencies []time.Duration) (p50, p99, p999 time.Duration) {
	if len(latencies) == 0 {
		return 0, 0, 0
	}
	
	// Sort latencies
	sorted := make([]time.Duration, len(latencies))
	copy(sorted, latencies)
	
	// Simple insertion sort (good enough for benchmarks)
	for i := 1; i < len(sorted); i++ {
		for j := i; j > 0 && sorted[j] < sorted[j-1]; j-- {
			sorted[j], sorted[j-1] = sorted[j-1], sorted[j]
		}
	}
	
	p50 = sorted[len(sorted)/2]
	p99 = sorted[int(float64(len(sorted))*0.99)]
	p999 = sorted[int(float64(len(sorted))*0.999)]
	
	return
}
