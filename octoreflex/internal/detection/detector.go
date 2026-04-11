// Package detection provides the main ML-based threat detection orchestrator.
//
// Integrates Isolation Forest, Neural Networks, and existing anomaly detection
// into a unified threat scoring system with <1ms latency.

package detection

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/octoreflex/octoreflex/internal/anomaly"
	"github.com/octoreflex/octoreflex/internal/detection/ml/features"
	"github.com/octoreflex/octoreflex/internal/detection/ml/inference"
	"github.com/octoreflex/octoreflex/internal/detection/ml/models"
)

// Detector is the main threat detection orchestrator.
// Combines traditional Mahalanobis + Entropy with ML models.
type Detector struct {
	mu sync.RWMutex
	
	// Legacy anomaly engine (Mahalanobis + Shannon entropy)
	legacyEngine *anomaly.Engine
	
	// ML inference engine
	mlEngine *inference.Engine
	
	// Model versioning
	currentVersion string
	loadedAt       time.Time
	
	// Feature extractors per PID
	extractors map[uint32]*features.Extractor
	
	// Configuration
	config Config
	
	// Hybrid scoring weights
	legacyWeight float64 // Weight for Mahalanobis+Entropy score
	mlWeight     float64 // Weight for ML ensemble score
}

// Config holds detector configuration.
type Config struct {
	// Model paths
	IsolationForestPath string
	NeuralNetPath       string
	
	// Hybrid weights
	LegacyWeight float64 // Default: 0.3 (30% legacy)
	MLWeight     float64 // Default: 0.7 (70% ML)
	
	// Feature extraction
	FeatureWindowSize time.Duration
	MaxEventsPerPID   int
	
	// Performance
	MaxDetectionLatency time.Duration
	
	// Model versioning
	EnableAutoReload bool
	ReloadInterval   time.Duration
}

// DefaultConfig returns recommended configuration.
func DefaultConfig() Config {
	return Config{
		LegacyWeight:        0.3,
		MLWeight:            0.7,
		FeatureWindowSize:   60 * time.Second,
		MaxEventsPerPID:     10000,
		MaxDetectionLatency: time.Millisecond,
		EnableAutoReload:    true,
		ReloadInterval:      5 * time.Minute,
	}
}

// NewDetector creates a new threat detector.
func NewDetector(config Config) (*Detector, error) {
	d := &Detector{
		legacyEngine: anomaly.NewEngine(0.3), // Entropy weight = 0.3
		extractors:   make(map[uint32]*features.Extractor),
		config:       config,
		legacyWeight: config.LegacyWeight,
		mlWeight:     config.MLWeight,
		loadedAt:     time.Now(),
	}
	
	// Initialize ML engine
	mlConfig := inference.DefaultEngineConfig()
	mlConfig.IsolationForestPath = config.IsolationForestPath
	mlConfig.NeuralNetPath = config.NeuralNetPath
	mlConfig.FeatureWindowSize = config.FeatureWindowSize
	mlConfig.MaxEvents = config.MaxEventsPerPID
	mlConfig.MaxInferenceLatency = config.MaxDetectionLatency
	
	mlEngine, err := inference.NewEngine(mlConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize ML engine: %w", err)
	}
	d.mlEngine = mlEngine
	
	return d, nil
}

// LoadModels loads or reloads ML models from disk.
func (d *Detector) LoadModels(iforestPath, neuralPath string) error {
	d.mu.Lock()
	defer d.mu.Unlock()
	
	var iforest *models.IsolationForest
	var neuralNet *models.SequenceModel
	
	// Load Isolation Forest
	if iforestPath != "" {
		var err error
		iforest, err = models.LoadIsolationForest(iforestPath)
		if err != nil {
			return fmt.Errorf("failed to load isolation forest: %w", err)
		}
	}
	
	// Load Neural Network
	if neuralPath != "" {
		var err error
		neuralNet, err = models.LoadSequenceModel(neuralPath)
		if err != nil {
			return fmt.Errorf("failed to load neural network: %w", err)
		}
	}
	
	// Update ML engine
	d.mlEngine.SetModels(iforest, neuralNet)
	d.loadedAt = time.Now()
	d.currentVersion = fmt.Sprintf("v%d", d.loadedAt.Unix())
	
	return nil
}

// ProcessEvent processes a kernel event and updates detection state.
// This should be called for each event from the eBPF ring buffer.
func (d *Detector) ProcessEvent(event features.Event) {
	// Get or create feature extractor for this PID
	d.mu.Lock()
	extractor, exists := d.extractors[event.PID]
	if !exists {
		extractor = features.NewExtractor(d.config.FeatureWindowSize, d.config.MaxEventsPerPID)
		d.extractors[event.PID] = extractor
	}
	d.mu.Unlock()
	
	// Add event to feature extractor
	extractor.AddEvent(event)
	
	// Also process in ML engine (global feature extractor)
	d.mlEngine.ProcessEvent(event)
}

// DetectThreat computes a hybrid threat score for a PID.
// Combines legacy Mahalanobis+Entropy with ML ensemble.
// Target latency: <1ms.
func (d *Detector) DetectThreat(pid uint32, baseline *anomaly.Baseline) (*ThreatAssessment, error) {
	ctx, cancel := context.WithTimeout(context.Background(), d.config.MaxDetectionLatency)
	defer cancel()
	
	startTime := time.Now()
	
	// Get feature extractor for this PID
	d.mu.RLock()
	extractor, exists := d.extractors[pid]
	d.mu.RUnlock()
	
	if !exists {
		return &ThreatAssessment{
			PID:         pid,
			Score:       0.0,
			Confidence:  0.0,
			ModelUsed:   "none",
			Latency:     time.Since(startTime),
		}, nil
	}
	
	// Extract features
	fv := extractor.Extract()
	features := fv.ToSlice()
	
	// Legacy score (Mahalanobis + Entropy)
	var legacyScore float64
	if baseline != nil {
		currentEntropy := fv.ShannonEntropyGlobal
		score, err := d.legacyEngine.Score(features[:min(len(features), len(baseline.MeanVector))],
			baseline, currentEntropy)
		if err == nil {
			// Normalize to [0, 1] (assuming Mahalanobis distance < 10 for normal behavior)
			legacyScore = min(score/10.0, 1.0)
		}
	}
	
	// Check context timeout
	select {
	case <-ctx.Done():
		return nil, fmt.Errorf("detection timeout after legacy scoring")
	default:
	}
	
	// ML score
	mlAssessment, err := d.mlEngine.Score()
	if err != nil {
		// Fallback to legacy-only scoring
		return &ThreatAssessment{
			PID:            pid,
			Score:          legacyScore,
			LegacyScore:    legacyScore,
			MLScore:        0.0,
			Confidence:     0.5,
			ModelUsed:      "legacy_only",
			ModelVersion:   "mahalanobis_v1",
			Latency:        time.Since(startTime),
			ComponentScores: make(map[string]float64),
		}, nil
	}
	
	// Hybrid score: weighted combination
	hybridScore := d.legacyWeight*legacyScore + d.mlWeight*mlAssessment.Combined
	
	// Confidence: average of ML confidence and legacy availability
	confidence := mlAssessment.Confidence
	if baseline != nil {
		confidence = (confidence + 1.0) / 2.0 // Boost confidence if baseline available
	}
	
	assessment := &ThreatAssessment{
		PID:          pid,
		Score:        hybridScore,
		LegacyScore:  legacyScore,
		MLScore:      mlAssessment.Combined,
		Confidence:   confidence,
		ModelUsed:    "hybrid",
		ModelVersion: d.currentVersion,
		Latency:      time.Since(startTime),
		ComponentScores: map[string]float64{
			"isolation_forest": mlAssessment.IsolationForestScore,
			"neural_network":   mlAssessment.NeuralNetScore,
			"mahalanobis":      legacyScore,
		},
	}
	
	return assessment, nil
}

// ThreatAssessment represents the final threat detection result.
type ThreatAssessment struct {
	PID          uint32
	Score        float64            // Final hybrid score [0, 1]
	LegacyScore  float64            // Mahalanobis + Entropy score
	MLScore      float64            // ML ensemble score
	Confidence   float64            // Confidence [0, 1]
	ModelUsed    string             // "hybrid", "ml_only", "legacy_only"
	ModelVersion string             // Model version identifier
	Latency      time.Duration      // Detection latency
	ComponentScores map[string]float64 // Individual model scores
}

// GetMetrics returns detector performance metrics.
func (d *Detector) GetMetrics() DetectorMetrics {
	mlMetrics := d.mlEngine.GetMetrics()
	
	d.mu.RLock()
	numExtractors := len(d.extractors)
	d.mu.RUnlock()
	
	return DetectorMetrics{
		MLInferenceCount: mlMetrics.InferenceCount,
		AverageLatency:   mlMetrics.AverageLatency,
		TrackedPIDs:      numExtractors,
		ModelVersion:     d.currentVersion,
		LoadedAt:         d.loadedAt,
	}
}

// DetectorMetrics holds detector statistics.
type DetectorMetrics struct {
	MLInferenceCount uint64
	AverageLatency   time.Duration
	TrackedPIDs      int
	ModelVersion     string
	LoadedAt         time.Time
}

// CleanupPID removes feature extractor for a terminated PID.
func (d *Detector) CleanupPID(pid uint32) {
	d.mu.Lock()
	defer d.mu.Unlock()
	delete(d.extractors, pid)
}

// EnableABTest enables A/B testing with alternative models.
func (d *Detector) EnableABTest(iforestPathB, neuralPathB string, trafficSplit int) error {
	// Load alternative models
	iforest, err := models.LoadIsolationForest(iforestPathB)
	if err != nil {
		return fmt.Errorf("failed to load model B (isolation forest): %w", err)
	}
	
	neuralNet, err := models.LoadSequenceModel(neuralPathB)
	if err != nil {
		return fmt.Errorf("failed to load model B (neural network): %w", err)
	}
	
	// Create alternative engine
	mlConfigB := inference.DefaultEngineConfig()
	mlConfigB.FeatureWindowSize = d.config.FeatureWindowSize
	mlConfigB.MaxEvents = d.config.MaxEventsPerPID
	mlConfigB.MaxInferenceLatency = d.config.MaxDetectionLatency
	
	mlEngineB, err := inference.NewEngine(mlConfigB)
	if err != nil {
		return fmt.Errorf("failed to create engine B: %w", err)
	}
	mlEngineB.SetModels(iforest, neuralNet)
	
	// Enable A/B test
	d.mlEngine.EnableABTest(mlEngineB, trafficSplit)
	
	return nil
}

// DisableABTest disables A/B testing.
func (d *Detector) DisableABTest() {
	d.mlEngine.DisableABTest()
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
