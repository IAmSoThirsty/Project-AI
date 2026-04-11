// Package inference implements real-time ML inference for threat detection.
//
// Combines Isolation Forest and Neural Network predictions with sub-millisecond latency.
// Supports model versioning and A/B testing.

package inference

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/octoreflex/octoreflex/internal/detection/ml/features"
	"github.com/octoreflex/octoreflex/internal/detection/ml/models"
)

// ThreatScore represents the combined ML threat assessment.
type ThreatScore struct {
	// Combined score [0, 1]: weighted combination of all models
	Combined float64
	
	// Individual model scores
	IsolationForestScore float64
	NeuralNetScore       float64
	
	// Confidence metrics
	Confidence float64 // Model agreement (higher = more confident)
	
	// Metadata
	ModelVersion string
	Latency      time.Duration // Inference latency
	Timestamp    time.Time
}

// Engine is the real-time inference engine.
// Thread-safe for concurrent inference requests.
type Engine struct {
	mu sync.RWMutex
	
	// Models
	isolationForest *models.IsolationForest
	neuralNet       *models.SequenceModel
	
	// Feature extractor
	featureExtractor *features.Extractor
	
	// Sequence buffer for neural network (sliding window)
	sequenceBuffer [][]float64
	bufferLock     sync.Mutex
	
	// Model weights for ensemble
	forestWeight float64
	neuralWeight float64
	
	// A/B testing support
	abTestEnabled bool
	modelA        *Engine // Primary model
	modelB        *Engine // Candidate model
	trafficSplitPct int   // % of traffic to modelB (0-100)
	
	// Performance metrics
	inferenceCount uint64
	totalLatency   uint64 // Microseconds
	
	// Configuration
	config EngineConfig
}

// EngineConfig holds inference engine configuration.
type EngineConfig struct {
	// Model weights
	IsolationForestWeight float64
	NeuralNetWeight       float64
	
	// Feature extraction
	FeatureWindowSize time.Duration
	MaxEvents         int
	
	// Neural network sequence length
	SequenceLength int
	
	// Performance
	MaxInferenceLatency time.Duration // Timeout for inference
	
	// Model paths
	IsolationForestPath string
	NeuralNetPath       string
}

// DefaultEngineConfig returns recommended configuration.
func DefaultEngineConfig() EngineConfig {
	return EngineConfig{
		IsolationForestWeight: 0.6,
		NeuralNetWeight:       0.4,
		FeatureWindowSize:     60 * time.Second,
		MaxEvents:             10000,
		SequenceLength:        10,
		MaxInferenceLatency:   time.Millisecond,
	}
}

// NewEngine creates a new inference engine.
func NewEngine(config EngineConfig) (*Engine, error) {
	engine := &Engine{
		forestWeight: config.IsolationForestWeight,
		neuralWeight: config.NeuralNetWeight,
		config:       config,
	}
	
	// Initialize feature extractor
	engine.featureExtractor = features.NewExtractor(
		config.FeatureWindowSize,
		config.MaxEvents,
	)
	
	// Initialize sequence buffer
	engine.sequenceBuffer = make([][]float64, 0, config.SequenceLength)
	
	// Load models if paths provided
	if config.IsolationForestPath != "" {
		iforest, err := models.LoadIsolationForest(config.IsolationForestPath)
		if err != nil {
			return nil, fmt.Errorf("failed to load isolation forest: %w", err)
		}
		engine.isolationForest = iforest
	}
	
	if config.NeuralNetPath != "" {
		neuralNet, err := models.LoadSequenceModel(config.NeuralNetPath)
		if err != nil {
			return nil, fmt.Errorf("failed to load neural network: %w", err)
		}
		engine.neuralNet = neuralNet
	}
	
	return engine, nil
}

// SetModels sets the ML models (for in-memory initialization).
func (e *Engine) SetModels(iforest *models.IsolationForest, neuralNet *models.SequenceModel) {
	e.mu.Lock()
	defer e.mu.Unlock()
	
	e.isolationForest = iforest
	e.neuralNet = neuralNet
}

// ProcessEvent adds an event to the sliding window and updates state.
// This should be called for each kernel event from the eBPF ring buffer.
func (e *Engine) ProcessEvent(event features.Event) {
	e.featureExtractor.AddEvent(event)
}

// Score computes a real-time threat score.
// Returns error if inference exceeds timeout or models not loaded.
// Target latency: <1ms.
func (e *Engine) Score() (*ThreatScore, error) {
	startTime := time.Now()
	
	// Timeout enforcement
	deadline := startTime.Add(e.config.MaxInferenceLatency)
	
	// Check A/B test routing
	if e.abTestEnabled {
		return e.scoreAB(deadline)
	}
	
	return e.scoreImpl(deadline, startTime)
}

// scoreImpl is the core scoring implementation.
func (e *Engine) scoreImpl(deadline time.Time, startTime time.Time) (*ThreatScore, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	
	if e.isolationForest == nil && e.neuralNet == nil {
		return nil, fmt.Errorf("no models loaded")
	}
	
	// Extract features
	fv := e.featureExtractor.Extract()
	features := fv.ToSlice()
	
	// Check timeout
	if time.Now().After(deadline) {
		return nil, fmt.Errorf("inference timeout during feature extraction")
	}
	
	var score ThreatScore
	score.Timestamp = startTime
	
	// Isolation Forest inference
	if e.isolationForest != nil {
		forestScore, err := e.isolationForest.Score(features)
		if err != nil {
			return nil, fmt.Errorf("isolation forest error: %w", err)
		}
		score.IsolationForestScore = forestScore
	}
	
	// Check timeout
	if time.Now().After(deadline) {
		return nil, fmt.Errorf("inference timeout after isolation forest")
	}
	
	// Neural Network inference
	if e.neuralNet != nil {
		// Add features to sequence buffer
		e.bufferLock.Lock()
		e.sequenceBuffer = append(e.sequenceBuffer, features)
		if len(e.sequenceBuffer) > e.config.SequenceLength {
			e.sequenceBuffer = e.sequenceBuffer[1:]
		}
		seqCopy := make([][]float64, len(e.sequenceBuffer))
		copy(seqCopy, e.sequenceBuffer)
		e.bufferLock.Unlock()
		
		// Only run neural net if we have enough sequence history
		if len(seqCopy) == e.config.SequenceLength {
			neuralScore, err := e.neuralNet.PredictThreatScore(seqCopy)
			if err != nil {
				return nil, fmt.Errorf("neural network error: %w", err)
			}
			score.NeuralNetScore = neuralScore
		}
	}
	
	// Combine scores (weighted average)
	totalWeight := 0.0
	combinedScore := 0.0
	
	if e.isolationForest != nil {
		combinedScore += e.forestWeight * score.IsolationForestScore
		totalWeight += e.forestWeight
	}
	
	if e.neuralNet != nil && score.NeuralNetScore > 0 {
		combinedScore += e.neuralWeight * score.NeuralNetScore
		totalWeight += e.neuralWeight
	}
	
	if totalWeight > 0 {
		score.Combined = combinedScore / totalWeight
	}
	
	// Compute confidence (agreement between models)
	if e.isolationForest != nil && e.neuralNet != nil && score.NeuralNetScore > 0 {
		// Confidence = 1 - |score1 - score2| (models agree when difference is small)
		diff := score.IsolationForestScore - score.NeuralNetScore
		if diff < 0 {
			diff = -diff
		}
		score.Confidence = 1.0 - diff
	} else {
		score.Confidence = 0.5 // Unknown confidence with single model
	}
	
	// Record latency
	score.Latency = time.Since(startTime)
	
	// Update metrics
	atomic.AddUint64(&e.inferenceCount, 1)
	atomic.AddUint64(&e.totalLatency, uint64(score.Latency.Microseconds()))
	
	return &score, nil
}

// EnableABTest enables A/B testing with a candidate model.
// trafficSplitPct: percentage of traffic to route to modelB (0-100).
func (e *Engine) EnableABTest(modelB *Engine, trafficSplitPct int) {
	e.mu.Lock()
	defer e.mu.Unlock()
	
	e.abTestEnabled = true
	e.modelA = e // Primary model
	e.modelB = modelB
	e.trafficSplitPct = trafficSplitPct
}

// DisableABTest disables A/B testing.
func (e *Engine) DisableABTest() {
	e.mu.Lock()
	defer e.mu.Unlock()
	
	e.abTestEnabled = false
	e.modelB = nil
}

// scoreAB routes request to modelA or modelB based on traffic split.
func (e *Engine) scoreAB(deadline time.Time) (*ThreatScore, error) {
	// Simple round-robin routing (production: use hash-based or random)
	count := atomic.LoadUint64(&e.inferenceCount)
	useModelB := (count % 100) < uint64(e.trafficSplitPct)
	
	startTime := time.Now()
	
	if useModelB && e.modelB != nil {
		return e.modelB.scoreImpl(deadline, startTime)
	}
	
	return e.scoreImpl(deadline, startTime)
}

// GetMetrics returns performance metrics.
func (e *Engine) GetMetrics() EngineMetrics {
	count := atomic.LoadUint64(&e.inferenceCount)
	totalLatency := atomic.LoadUint64(&e.totalLatency)
	
	var avgLatency time.Duration
	if count > 0 {
		avgLatency = time.Duration(totalLatency/count) * time.Microsecond
	}
	
	return EngineMetrics{
		InferenceCount:      count,
		AverageLatency:      avgLatency,
		AverageLatencyMicro: totalLatency / max(count, 1),
	}
}

// ResetMetrics resets performance counters.
func (e *Engine) ResetMetrics() {
	atomic.StoreUint64(&e.inferenceCount, 0)
	atomic.StoreUint64(&e.totalLatency, 0)
}

// EngineMetrics contains performance statistics.
type EngineMetrics struct {
	InferenceCount      uint64
	AverageLatency      time.Duration
	AverageLatencyMicro uint64 // Microseconds
}

func max(a, b uint64) uint64 {
	if a > b {
		return a
	}
	return b
}
