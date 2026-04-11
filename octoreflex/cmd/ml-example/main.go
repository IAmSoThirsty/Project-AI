// Example: Integration of ML-based threat detection into OctoReflex agent.
//
// Shows how to integrate the ML detection pipeline into the main event loop.

package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/octoreflex/octoreflex/internal/anomaly"
	"github.com/octoreflex/octoreflex/internal/detection"
	"github.com/octoreflex/octoreflex/internal/detection/ml/features"
	"github.com/octoreflex/octoreflex/internal/detection/ml/training"
)

func main() {
	fmt.Println("OctoReflex ML Detection - Integration Example")
	fmt.Println("===============================================\n")
	
	// Example 1: Initialize detector with models
	if err := exampleInitializeDetector(); err != nil {
		log.Fatalf("Failed to initialize detector: %v", err)
	}
	
	// Example 2: Process events and detect threats
	if err := exampleProcessEvents(); err != nil {
		log.Fatalf("Failed to process events: %v", err)
	}
	
	// Example 3: A/B testing with model versioning
	if err := exampleABTesting(); err != nil {
		log.Fatalf("Failed A/B testing: %v", err)
	}
	
	fmt.Println("\n✓ All examples completed successfully")
}

// Example 1: Initialize detector with pre-trained models
func exampleInitializeDetector() error {
	fmt.Println("Example 1: Initialize ML Detector")
	fmt.Println("----------------------------------")
	
	// Configure detector
	config := detection.DefaultConfig()
	config.IsolationForestPath = "models/isolation_forest.json"
	config.NeuralNetPath = "models/neural_net.json"
	config.LegacyWeight = 0.3 // 30% legacy Mahalanobis
	config.MLWeight = 0.7     // 70% ML ensemble
	
	// Create detector
	detector, err := detection.NewDetector(config)
	if err != nil {
		return fmt.Errorf("failed to create detector: %w", err)
	}
	
	fmt.Printf("✓ Detector initialized\n")
	fmt.Printf("  - Legacy weight: %.1f%%\n", config.LegacyWeight*100)
	fmt.Printf("  - ML weight: %.1f%%\n", config.MLWeight*100)
	
	// For this example, train models on synthetic data
	fmt.Println("\nTraining models on synthetic data...")
	data := training.GenerateSyntheticDataset(5000, 24, 0.1)
	
	trainConfig := training.DefaultTrainingConfig()
	trainConfig.ModelOutputDir = "models"
	
	_, _, err = training.TrainIsolationForest(data, trainConfig)
	if err != nil {
		return fmt.Errorf("failed to train isolation forest: %w", err)
	}
	
	// Load trained models
	if err := detector.LoadModels("models/isolation_forest.json", ""); err != nil {
		return fmt.Errorf("failed to load models: %w", err)
	}
	
	fmt.Println("✓ Models trained and loaded\n")
	
	return nil
}

// Example 2: Process events and detect threats
func exampleProcessEvents() error {
	fmt.Println("Example 2: Process Events and Detect Threats")
	fmt.Println("---------------------------------------------")
	
	// Initialize detector
	config := detection.DefaultConfig()
	detector, err := detection.NewDetector(config)
	if err != nil {
		return err
	}
	
	// Train and load models
	data := training.GenerateSyntheticDataset(1000, 24, 0.1)
	trainConfig := training.DefaultTrainingConfig()
	trainConfig.ModelOutputDir = "models"
	training.TrainIsolationForest(data, trainConfig)
	detector.LoadModels("models/isolation_forest.json", "")
	
	// Simulate incoming events from eBPF ring buffer
	pid := uint32(12345)
	
	events := []features.Event{
		{
			PID:       pid,
			Type:      features.EventSocketConnect,
			Timestamp: time.Now(),
			DstIP:     0x08080808, // 8.8.8.8
			DstPort:   443,
		},
		{
			PID:       pid,
			Type:      features.EventFileOpen,
			Timestamp: time.Now(),
			FilePath:  "/etc/passwd",
			Flags:     0x0, // Read-only
		},
		{
			PID:       pid,
			Type:      features.EventSocketConnect,
			Timestamp: time.Now(),
			DstIP:     0xC0A80101, // 192.168.1.1
			DstPort:   22,
		},
	}
	
	fmt.Printf("Processing %d events for PID %d...\n", len(events), pid)
	
	for i, event := range events {
		detector.ProcessEvent(event)
		fmt.Printf("  [%d] %s\n", i+1, eventTypeName(event.Type))
	}
	
	// Detect threat after accumulating events
	baseline := &anomaly.Baseline{
		MeanVector:      make([]float64, 24),
		CovarianceMatrix: make([][]float64, 24),
		BaselineEntropy: 1.5,
		SampleCount:     1000,
	}
	for i := range baseline.MeanVector {
		baseline.MeanVector[i] = 1.0
	}
	
	assessment, err := detector.DetectThreat(pid, baseline)
	if err != nil {
		return fmt.Errorf("detection failed: %w", err)
	}
	
	fmt.Println("\nThreat Assessment:")
	fmt.Printf("  - Combined Score: %.4f\n", assessment.Score)
	fmt.Printf("  - Legacy Score: %.4f\n", assessment.LegacyScore)
	fmt.Printf("  - ML Score: %.4f\n", assessment.MLScore)
	fmt.Printf("  - Confidence: %.2f%%\n", assessment.Confidence*100)
	fmt.Printf("  - Latency: %v\n", assessment.Latency)
	fmt.Printf("  - Model: %s (%s)\n", assessment.ModelUsed, assessment.ModelVersion)
	
	// Decision threshold
	threshold := 0.7
	if assessment.Score > threshold {
		fmt.Printf("\n⚠️  THREAT DETECTED (score %.4f > %.2f)\n", assessment.Score, threshold)
		fmt.Println("  → Recommended action: Escalate to ISOLATED state")
	} else {
		fmt.Printf("\n✓ Normal behavior (score %.4f ≤ %.2f)\n", assessment.Score, threshold)
	}
	
	fmt.Println()
	return nil
}

// Example 3: A/B testing with model versioning
func exampleABTesting() error {
	fmt.Println("Example 3: A/B Testing with Model Versioning")
	fmt.Println("---------------------------------------------")
	
	// Initialize primary detector
	config := detection.DefaultConfig()
	detector, err := detection.NewDetector(config)
	if err != nil {
		return err
	}
	
	// Train model A (current production)
	dataA := training.GenerateSyntheticDataset(1000, 24, 0.1)
	trainConfig := training.DefaultTrainingConfig()
	trainConfig.ModelOutputDir = "models"
	training.TrainIsolationForest(dataA, trainConfig)
	detector.LoadModels("models/isolation_forest.json", "")
	
	fmt.Println("✓ Model A (production) loaded")
	
	// Train model B (candidate)
	dataB := training.GenerateSyntheticDataset(1500, 24, 0.15) // More data, higher malicious ratio
	trainConfig.ModelOutputDir = "models_b"
	training.TrainIsolationForest(dataB, trainConfig)
	
	fmt.Println("✓ Model B (candidate) trained")
	
	// Enable A/B test: 20% traffic to model B
	trafficSplit := 20
	if err := detector.EnableABTest("models_b/isolation_forest.json", "", trafficSplit); err != nil {
		return fmt.Errorf("failed to enable A/B test: %w", err)
	}
	
	fmt.Printf("✓ A/B testing enabled: %d%% traffic to model B\n\n", trafficSplit)
	
	// Simulate 100 inference requests
	pid := uint32(99999)
	modelCounts := map[string]int{}
	
	for i := 0; i < 100; i++ {
		// Add event
		event := features.Event{
			PID:       pid,
			Type:      features.EventType((i % 3) + 1),
			Timestamp: time.Now(),
		}
		detector.ProcessEvent(event)
		
		// Detect
		assessment, err := detector.DetectThreat(pid, nil)
		if err == nil {
			modelCounts[assessment.ModelUsed]++
		}
	}
	
	fmt.Println("A/B Test Results (100 requests):")
	for model, count := range modelCounts {
		fmt.Printf("  - %s: %d requests (%.1f%%)\n", model, count, float64(count))
	}
	
	// Disable A/B test
	detector.DisableABTest()
	fmt.Println("\n✓ A/B test disabled, reverted to model A\n")
	
	return nil
}

// Helper functions

func eventTypeName(t features.EventType) string {
	switch t {
	case features.EventSocketConnect:
		return "socket_connect"
	case features.EventFileOpen:
		return "file_open"
	case features.EventSetUID:
		return "setuid"
	default:
		return "unknown"
	}
}

// Production integration example
func integrateWithMainLoop(ctx context.Context) {
	// This would be called from the main OctoReflex agent loop
	
	// Initialize detector
	config := detection.DefaultConfig()
	config.IsolationForestPath = "/var/lib/octoreflex/models/isolation_forest.json"
	config.NeuralNetPath = "/var/lib/octoreflex/models/neural_net.json"
	
	detector, err := detection.NewDetector(config)
	if err != nil {
		log.Fatalf("Failed to initialize detector: %v", err)
	}
	
	log.Println("ML detector initialized")
	
	// Event processing loop (pseudo-code)
	for {
		select {
		case <-ctx.Done():
			return
			
		// case event := <-ebpfRingBuffer:
		// 	// Convert eBPF event to features.Event
		// 	mlEvent := convertToMLEvent(event)
		// 	detector.ProcessEvent(mlEvent)
		// 	
		// 	// Detect threat
		// 	baseline := loadBaseline(event.PID)
		// 	assessment, err := detector.DetectThreat(event.PID, baseline)
		// 	if err != nil {
		// 		log.Printf("Detection error: %v", err)
		// 		continue
		// 	}
		// 	
		// 	// Escalation decision
		// 	if assessment.Score > 0.7 {
		// 		escalate(event.PID, assessment)
		// 	}
		}
	}
}
