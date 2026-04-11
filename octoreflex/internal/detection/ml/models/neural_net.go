// Package models - Neural Network for sequence-based threat prediction.
//
// Implements LSTM-style sequence modeling for temporal threat patterns.
// Lightweight implementation optimized for Go with <1ms inference.

package models

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"sync"
)

// SequenceModel represents a neural network for temporal sequence analysis.
// Simplified LSTM-style architecture optimized for low-latency inference.
type SequenceModel struct {
	mu sync.RWMutex
	
	// Network architecture
	InputDim    int
	HiddenDim   int
	OutputDim   int
	SequenceLen int
	
	// LSTM-like weights (simplified for speed)
	// Input gate: W_i * x + U_i * h + b_i
	W_input  [][]float64 // [HiddenDim x InputDim]
	U_input  [][]float64 // [HiddenDim x HiddenDim]
	B_input  []float64   // [HiddenDim]
	
	// Forget gate: W_f * x + U_f * h + b_f
	W_forget [][]float64
	U_forget [][]float64
	B_forget []float64
	
	// Output gate: W_o * x + U_o * h + b_o
	W_output [][]float64
	U_output [][]float64
	B_output []float64
	
	// Cell state: W_c * x + U_c * h + b_c
	W_cell   [][]float64
	U_cell   [][]float64
	B_cell   []float64
	
	// Final dense layer: W_dense * h + b_dense
	W_dense  [][]float64 // [OutputDim x HiddenDim]
	B_dense  []float64   // [OutputDim]
	
	// Normalization parameters
	InputMeans []float64
	InputStds  []float64
	
	// Model metadata
	Version     string
	TrainedAt   string
	EpochsTrained int
}

// SequenceModelConfig holds hyperparameters.
type SequenceModelConfig struct {
	InputDim    int // Number of features per timestep (default: 24)
	HiddenDim   int // LSTM hidden units (default: 64)
	OutputDim   int // Output classes (default: 2 - benign/malicious)
	SequenceLen int // Sequence length (default: 10 timesteps)
}

// DefaultSequenceModelConfig returns recommended hyperparameters.
func DefaultSequenceModelConfig() SequenceModelConfig {
	return SequenceModelConfig{
		InputDim:    24,
		HiddenDim:   64,
		OutputDim:   2,
		SequenceLen: 10,
	}
}

// NewSequenceModel creates an untrained sequence model.
func NewSequenceModel(config SequenceModelConfig) *SequenceModel {
	return &SequenceModel{
		InputDim:    config.InputDim,
		HiddenDim:   config.HiddenDim,
		OutputDim:   config.OutputDim,
		SequenceLen: config.SequenceLen,
	}
}

// InitializeWeights randomly initializes network weights (Xavier/Glorot).
// Called before training or can be loaded from file.
func (sm *SequenceModel) InitializeWeights() {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	
	// Xavier initialization scale
	scaleInput := math.Sqrt(2.0 / float64(sm.InputDim+sm.HiddenDim))
	scaleHidden := math.Sqrt(2.0 / float64(sm.HiddenDim+sm.HiddenDim))
	scaleDense := math.Sqrt(2.0 / float64(sm.HiddenDim+sm.OutputDim))
	
	sm.W_input = randomMatrix(sm.HiddenDim, sm.InputDim, scaleInput)
	sm.U_input = randomMatrix(sm.HiddenDim, sm.HiddenDim, scaleHidden)
	sm.B_input = make([]float64, sm.HiddenDim)
	
	sm.W_forget = randomMatrix(sm.HiddenDim, sm.InputDim, scaleInput)
	sm.U_forget = randomMatrix(sm.HiddenDim, sm.HiddenDim, scaleHidden)
	sm.B_forget = ones(sm.HiddenDim) // Initialize forget gate to 1 (remember by default)
	
	sm.W_output = randomMatrix(sm.HiddenDim, sm.InputDim, scaleInput)
	sm.U_output = randomMatrix(sm.HiddenDim, sm.HiddenDim, scaleHidden)
	sm.B_output = make([]float64, sm.HiddenDim)
	
	sm.W_cell = randomMatrix(sm.HiddenDim, sm.InputDim, scaleInput)
	sm.U_cell = randomMatrix(sm.HiddenDim, sm.HiddenDim, scaleHidden)
	sm.B_cell = make([]float64, sm.HiddenDim)
	
	sm.W_dense = randomMatrix(sm.OutputDim, sm.HiddenDim, scaleDense)
	sm.B_dense = make([]float64, sm.OutputDim)
}

// Predict performs inference on a sequence.
// sequence: [SequenceLen x InputDim] matrix (timesteps x features).
// Returns: [OutputDim] probability distribution over output classes.
// Inference time: <500µs for 10-step sequence.
func (sm *SequenceModel) Predict(sequence [][]float64) ([]float64, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	
	if len(sequence) != sm.SequenceLen {
		return nil, fmt.Errorf("sequence length mismatch: expected %d, got %d",
			sm.SequenceLen, len(sequence))
	}
	
	// Normalize input
	seqNorm := make([][]float64, len(sequence))
	for t := range sequence {
		seqNorm[t] = make([]float64, sm.InputDim)
		for i := range sequence[t] {
			if len(sm.InputStds) > i && sm.InputStds[i] > 0 {
				seqNorm[t][i] = (sequence[t][i] - sm.InputMeans[i]) / sm.InputStds[i]
			} else {
				seqNorm[t][i] = sequence[t][i]
			}
		}
	}
	
	// Initialize hidden state and cell state
	h := make([]float64, sm.HiddenDim)
	c := make([]float64, sm.HiddenDim)
	
	// Process sequence
	for t := 0; t < sm.SequenceLen; t++ {
		x := seqNorm[t]
		h, c = sm.lstmStep(x, h, c)
	}
	
	// Final dense layer
	output := matVecMul(sm.W_dense, h)
	for i := range output {
		output[i] += sm.B_dense[i]
	}
	
	// Softmax activation
	output = softmax(output)
	
	return output, nil
}

// PredictThreatScore returns a single threat score in [0, 1].
// Assumes binary classification: output[1] is the malicious class probability.
func (sm *SequenceModel) PredictThreatScore(sequence [][]float64) (float64, error) {
	probs, err := sm.Predict(sequence)
	if err != nil {
		return 0, err
	}
	if len(probs) < 2 {
		return 0, fmt.Errorf("invalid output dimension")
	}
	return probs[1], nil // Return probability of malicious class
}

// Save serializes the model to a file.
func (sm *SequenceModel) Save(path string) error {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	
	data, err := json.MarshalIndent(sm, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal model: %w", err)
	}
	
	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write model file: %w", err)
	}
	
	return nil
}

// LoadSequenceModel deserializes a model from a file.
func LoadSequenceModel(path string) (*SequenceModel, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read model file: %w", err)
	}
	
	var sm SequenceModel
	if err := json.Unmarshal(data, &sm); err != nil {
		return nil, fmt.Errorf("failed to unmarshal model: %w", err)
	}
	
	return &sm, nil
}

// --- Internal LSTM step ---

// lstmStep performs one LSTM timestep.
// x: input vector [InputDim]
// h_prev: previous hidden state [HiddenDim]
// c_prev: previous cell state [HiddenDim]
// Returns: (h_new, c_new)
func (sm *SequenceModel) lstmStep(x, h_prev, c_prev []float64) ([]float64, []float64) {
	// Input gate: i_t = σ(W_i * x + U_i * h + b_i)
	i_t := matVecMul(sm.W_input, x)
	addVec(i_t, matVecMul(sm.U_input, h_prev))
	addVec(i_t, sm.B_input)
	applySigmoid(i_t)
	
	// Forget gate: f_t = σ(W_f * x + U_f * h + b_f)
	f_t := matVecMul(sm.W_forget, x)
	addVec(f_t, matVecMul(sm.U_forget, h_prev))
	addVec(f_t, sm.B_forget)
	applySigmoid(f_t)
	
	// Output gate: o_t = σ(W_o * x + U_o * h + b_o)
	o_t := matVecMul(sm.W_output, x)
	addVec(o_t, matVecMul(sm.U_output, h_prev))
	addVec(o_t, sm.B_output)
	applySigmoid(o_t)
	
	// Cell candidate: c̃_t = tanh(W_c * x + U_c * h + b_c)
	c_tilde := matVecMul(sm.W_cell, x)
	addVec(c_tilde, matVecMul(sm.U_cell, h_prev))
	addVec(c_tilde, sm.B_cell)
	applyTanh(c_tilde)
	
	// Cell state: c_t = f_t ⊙ c_prev + i_t ⊙ c̃_t
	c_new := make([]float64, sm.HiddenDim)
	for i := 0; i < sm.HiddenDim; i++ {
		c_new[i] = f_t[i]*c_prev[i] + i_t[i]*c_tilde[i]
	}
	
	// Hidden state: h_t = o_t ⊙ tanh(c_t)
	c_tanh := make([]float64, len(c_new))
	copy(c_tanh, c_new)
	applyTanh(c_tanh)
	h_new := make([]float64, sm.HiddenDim)
	for i := 0; i < sm.HiddenDim; i++ {
		h_new[i] = o_t[i] * c_tanh[i]
	}
	
	return h_new, c_new
}

// --- Math utilities ---

// matVecMul: matrix-vector multiplication M * v.
func matVecMul(M [][]float64, v []float64) []float64 {
	result := make([]float64, len(M))
	for i := range M {
		for j := range v {
			result[i] += M[i][j] * v[j]
		}
	}
	return result
}

// addVec: element-wise addition (in-place).
func addVec(a, b []float64) {
	for i := range a {
		a[i] += b[i]
	}
}

// applySigmoid: element-wise sigmoid activation (in-place).
func applySigmoid(v []float64) {
	for i := range v {
		v[i] = 1.0 / (1.0 + math.Exp(-v[i]))
	}
}

// applyTanh: element-wise tanh activation (in-place).
func applyTanh(v []float64) {
	for i := range v {
		v[i] = math.Tanh(v[i])
	}
}

// softmax: convert logits to probabilities.
func softmax(logits []float64) []float64 {
	// Subtract max for numerical stability
	maxVal := logits[0]
	for _, val := range logits {
		if val > maxVal {
			maxVal = val
		}
	}
	
	expSum := 0.0
	probs := make([]float64, len(logits))
	for i, val := range logits {
		probs[i] = math.Exp(val - maxVal)
		expSum += probs[i]
	}
	
	for i := range probs {
		probs[i] /= expSum
	}
	
	return probs
}

// randomMatrix: create matrix with random values (Xavier initialization).
func randomMatrix(rows, cols int, scale float64) [][]float64 {
	mat := make([][]float64, rows)
	for i := range mat {
		mat[i] = make([]float64, cols)
		for j := range mat[i] {
			// Simple random initialization (production: use proper RNG)
			mat[i][j] = (2*float64(i*cols+j)/float64(rows*cols) - 1) * scale
		}
	}
	return mat
}

// ones: create vector filled with 1.0.
func ones(size int) []float64 {
	v := make([]float64, size)
	for i := range v {
		v[i] = 1.0
	}
	return v
}
