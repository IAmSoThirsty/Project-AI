// Package models implements ML models for threat detection.
//
// Isolation Forest: Unsupervised anomaly detection based on path length isolation.
// Production-grade implementation with sub-millisecond inference.

package models

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"os"
	"sync"
)

// IsolationTree represents a single tree in the Isolation Forest.
type IsolationTree struct {
	Root *INode
	MaxDepth int
}

// INode is a node in an isolation tree (internal or leaf).
type INode struct {
	IsLeaf       bool
	SplitFeature int     // Feature index to split on
	SplitValue   float64 // Threshold value
	Left         *INode  // Samples where feature < splitValue
	Right        *INode  // Samples where feature >= splitValue
	Size         int     // Number of samples at this node (for leaf nodes)
}

// IsolationForest implements the Isolation Forest algorithm.
// Thread-safe for concurrent inference after training.
type IsolationForest struct {
	mu          sync.RWMutex
	Trees       []*IsolationTree
	NumTrees    int
	SubsampleSize int
	MaxDepth    int
	NumFeatures int
	
	// Normalization parameters (learned during training)
	FeatureMeans []float64
	FeatureStds  []float64
	
	// Model metadata
	Version     string
	TrainedAt   string
	SampleCount int
}

// IsolationForestConfig holds hyperparameters.
type IsolationForestConfig struct {
	NumTrees      int     // Number of trees (default: 100)
	SubsampleSize int     // Sample size per tree (default: 256)
	MaxDepth      int     // Maximum tree depth (default: 10)
	Contamination float64 // Expected outlier ratio (default: 0.1)
}

// DefaultIsolationForestConfig returns recommended hyperparameters.
func DefaultIsolationForestConfig() IsolationForestConfig {
	return IsolationForestConfig{
		NumTrees:      100,
		SubsampleSize: 256,
		MaxDepth:      10,
		Contamination: 0.1,
	}
}

// NewIsolationForest creates an untrained Isolation Forest.
func NewIsolationForest(config IsolationForestConfig) *IsolationForest {
	return &IsolationForest{
		NumTrees:      config.NumTrees,
		SubsampleSize: config.SubsampleSize,
		MaxDepth:      config.MaxDepth,
		Trees:         make([]*IsolationTree, 0, config.NumTrees),
	}
}

// Train builds the Isolation Forest from training samples.
// X: feature matrix (rows = samples, columns = features).
// Returns error if input is invalid.
func (iforest *IsolationForest) Train(X [][]float64) error {
	if len(X) == 0 {
		return fmt.Errorf("training data is empty")
	}
	
	iforest.mu.Lock()
	defer iforest.mu.Unlock()
	
	numSamples := len(X)
	iforest.NumFeatures = len(X[0])
	iforest.SampleCount = numSamples
	
	// Compute normalization parameters
	iforest.FeatureMeans, iforest.FeatureStds = computeNormalization(X)
	
	// Normalize training data
	XNorm := normalizeData(X, iforest.FeatureMeans, iforest.FeatureStds)
	
	// Build trees
	iforest.Trees = make([]*IsolationTree, iforest.NumTrees)
	for i := 0; i < iforest.NumTrees; i++ {
		// Sample subset
		subsample := sampleRows(XNorm, iforest.SubsampleSize)
		
		// Build tree
		tree := &IsolationTree{
			MaxDepth: iforest.MaxDepth,
		}
		tree.Root = buildITree(subsample, 0, iforest.MaxDepth, iforest.NumFeatures)
		iforest.Trees[i] = tree
	}
	
	return nil
}

// Score computes the anomaly score for a single sample.
// Returns value in range [0, 1], where higher = more anomalous.
// Inference time: <100µs for 100 trees.
func (iforest *IsolationForest) Score(x []float64) (float64, error) {
	iforest.mu.RLock()
	defer iforest.mu.RUnlock()
	
	if len(x) != iforest.NumFeatures {
		return 0, fmt.Errorf("feature dimension mismatch: expected %d, got %d",
			iforest.NumFeatures, len(x))
	}
	
	if len(iforest.Trees) == 0 {
		return 0, fmt.Errorf("model not trained")
	}
	
	// Normalize input
	xNorm := make([]float64, len(x))
	for i := range x {
		if iforest.FeatureStds[i] > 0 {
			xNorm[i] = (x[i] - iforest.FeatureMeans[i]) / iforest.FeatureStds[i]
		} else {
			xNorm[i] = 0
		}
	}
	
	// Compute average path length across all trees
	var avgPathLength float64
	for _, tree := range iforest.Trees {
		pathLength := pathLength(tree.Root, xNorm, 0)
		avgPathLength += pathLength
	}
	avgPathLength /= float64(len(iforest.Trees))
	
	// Anomaly score: s(x, n) = 2^(-E(h(x)) / c(n))
	// where c(n) is the average path length of unsuccessful search in BST.
	c := cFactor(iforest.SubsampleSize)
	score := math.Pow(2, -avgPathLength/c)
	
	return score, nil
}

// ScoreBatch computes anomaly scores for multiple samples.
// Optimized for throughput (processes in parallel).
func (iforest *IsolationForest) ScoreBatch(X [][]float64) ([]float64, error) {
	scores := make([]float64, len(X))
	errChan := make(chan error, 1)
	
	var wg sync.WaitGroup
	for i := range X {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			score, err := iforest.Score(X[idx])
			if err != nil {
				select {
				case errChan <- err:
				default:
				}
				return
			}
			scores[idx] = score
		}(i)
	}
	
	wg.Wait()
	close(errChan)
	
	if err := <-errChan; err != nil {
		return nil, err
	}
	
	return scores, nil
}

// Save serializes the model to a file.
func (iforest *IsolationForest) Save(path string) error {
	iforest.mu.RLock()
	defer iforest.mu.RUnlock()
	
	data, err := json.MarshalIndent(iforest, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal model: %w", err)
	}
	
	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write model file: %w", err)
	}
	
	return nil
}

// Load deserializes a model from a file.
func LoadIsolationForest(path string) (*IsolationForest, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read model file: %w", err)
	}
	
	var iforest IsolationForest
	if err := json.Unmarshal(data, &iforest); err != nil {
		return nil, fmt.Errorf("failed to unmarshal model: %w", err)
	}
	
	return &iforest, nil
}

// --- Internal functions ---

// buildITree recursively builds an isolation tree.
func buildITree(X [][]float64, depth, maxDepth, numFeatures int) *INode {
	n := len(X)
	
	// Termination conditions
	if n <= 1 || depth >= maxDepth {
		return &INode{
			IsLeaf: true,
			Size:   n,
		}
	}
	
	// Random split: select random feature and random value in its range
	featureIdx := rand.Intn(numFeatures)
	minVal, maxVal := featureRange(X, featureIdx)
	
	if minVal == maxVal {
		// Cannot split (all values identical)
		return &INode{
			IsLeaf: true,
			Size:   n,
		}
	}
	
	splitValue := minVal + rand.Float64()*(maxVal-minVal)
	
	// Split data
	var leftX, rightX [][]float64
	for _, row := range X {
		if row[featureIdx] < splitValue {
			leftX = append(leftX, row)
		} else {
			rightX = append(rightX, row)
		}
	}
	
	// If split fails to partition, return leaf
	if len(leftX) == 0 || len(rightX) == 0 {
		return &INode{
			IsLeaf: true,
			Size:   n,
		}
	}
	
	// Recurse
	return &INode{
		IsLeaf:       false,
		SplitFeature: featureIdx,
		SplitValue:   splitValue,
		Left:         buildITree(leftX, depth+1, maxDepth, numFeatures),
		Right:        buildITree(rightX, depth+1, maxDepth, numFeatures),
	}
}

// pathLength computes the path length of x in the tree.
func pathLength(node *INode, x []float64, currentDepth int) float64 {
	if node.IsLeaf {
		// Adjust for leaf size (average depth of external node in BST)
		return float64(currentDepth) + cFactor(node.Size)
	}
	
	if x[node.SplitFeature] < node.SplitValue {
		return pathLength(node.Left, x, currentDepth+1)
	}
	return pathLength(node.Right, x, currentDepth+1)
}

// cFactor computes the average path length of unsuccessful search in BST of size n.
// c(n) = 2H(n-1) - 2(n-1)/n, where H(n) is the harmonic number.
func cFactor(n int) float64 {
	if n <= 1 {
		return 0
	}
	if n == 2 {
		return 1
	}
	// Harmonic number approximation: H(n) ≈ ln(n) + γ (Euler's constant)
	gamma := 0.5772156649
	H := math.Log(float64(n-1)) + gamma
	return 2*H - 2*float64(n-1)/float64(n)
}

// featureRange returns min and max values for a feature in dataset X.
func featureRange(X [][]float64, featureIdx int) (min, max float64) {
	if len(X) == 0 {
		return 0, 0
	}
	
	min = X[0][featureIdx]
	max = X[0][featureIdx]
	
	for _, row := range X {
		val := row[featureIdx]
		if val < min {
			min = val
		}
		if val > max {
			max = val
		}
	}
	return
}

// sampleRows randomly samples k rows from X (with replacement).
func sampleRows(X [][]float64, k int) [][]float64 {
	if k > len(X) {
		k = len(X)
	}
	
	sampled := make([][]float64, k)
	for i := 0; i < k; i++ {
		idx := rand.Intn(len(X))
		sampled[i] = X[idx]
	}
	return sampled
}

// computeNormalization computes mean and standard deviation for each feature.
func computeNormalization(X [][]float64) (means, stds []float64) {
	if len(X) == 0 {
		return nil, nil
	}
	
	numFeatures := len(X[0])
	means = make([]float64, numFeatures)
	stds = make([]float64, numFeatures)
	
	// Compute means
	for _, row := range X {
		for j, val := range row {
			means[j] += val
		}
	}
	for j := range means {
		means[j] /= float64(len(X))
	}
	
	// Compute standard deviations
	for _, row := range X {
		for j, val := range row {
			diff := val - means[j]
			stds[j] += diff * diff
		}
	}
	for j := range stds {
		stds[j] = math.Sqrt(stds[j] / float64(len(X)))
	}
	
	return
}

// normalizeData applies z-score normalization to X.
func normalizeData(X [][]float64, means, stds []float64) [][]float64 {
	normalized := make([][]float64, len(X))
	for i, row := range X {
		normalized[i] = make([]float64, len(row))
		for j, val := range row {
			if stds[j] > 0 {
				normalized[i][j] = (val - means[j]) / stds[j]
			} else {
				normalized[i][j] = 0
			}
		}
	}
	return normalized
}
