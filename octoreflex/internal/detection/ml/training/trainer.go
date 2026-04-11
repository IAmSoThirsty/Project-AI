// Package training implements ML model training pipelines.
//
// Trains Isolation Forest and Neural Network models on historical threat data.
// Includes data preprocessing, validation, and model persistence.

package training

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/octoreflex/octoreflex/internal/detection/ml/models"
)

// TrainingData represents a dataset for model training.
type TrainingData struct {
	Features [][]float64 // Feature matrix [samples x features]
	Labels   []int       // Labels (0 = benign, 1 = malicious)
	Metadata []string    // Sample metadata (timestamps, process names, etc.)
}

// TrainingConfig holds training hyperparameters.
type TrainingConfig struct {
	// Data
	TrainTestSplit float64 // Fraction for training (default: 0.8)
	ValidationSplit float64 // Fraction for validation (default: 0.1)
	
	// Isolation Forest
	IForestConfig models.IsolationForestConfig
	
	// Neural Network
	NeuralConfig models.SequenceModelConfig
	LearningRate float64
	Epochs       int
	BatchSize    int
	
	// Output
	ModelOutputDir string
	SaveCheckpoints bool
}

// DefaultTrainingConfig returns recommended training configuration.
func DefaultTrainingConfig() TrainingConfig {
	return TrainingConfig{
		TrainTestSplit:  0.8,
		ValidationSplit: 0.1,
		IForestConfig:   models.DefaultIsolationForestConfig(),
		NeuralConfig:    models.DefaultSequenceModelConfig(),
		LearningRate:    0.001,
		Epochs:          50,
		BatchSize:       32,
		ModelOutputDir:  "models",
		SaveCheckpoints: true,
	}
}

// LoadDataset loads training data from CSV file.
// CSV format: feature1,feature2,...,featureN,label
// Returns TrainingData with features and labels.
func LoadDataset(csvPath string) (*TrainingData, error) {
	file, err := os.Open(csvPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open dataset: %w", err)
	}
	defer file.Close()
	
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("failed to read CSV: %w", err)
	}
	
	if len(records) < 2 {
		return nil, fmt.Errorf("dataset is empty")
	}
	
	// Parse records (skip header row)
	numFeatures := len(records[0]) - 1
	data := &TrainingData{
		Features: make([][]float64, 0, len(records)-1),
		Labels:   make([]int, 0, len(records)-1),
		Metadata: make([]string, 0, len(records)-1),
	}
	
	for i := 1; i < len(records); i++ {
		record := records[i]
		if len(record) != numFeatures+1 {
			continue // Skip malformed rows
		}
		
		// Parse features
		features := make([]float64, numFeatures)
		valid := true
		for j := 0; j < numFeatures; j++ {
			val, err := strconv.ParseFloat(record[j], 64)
			if err != nil {
				valid = false
				break
			}
			features[j] = val
		}
		
		if !valid {
			continue
		}
		
		// Parse label
		label, err := strconv.Atoi(record[numFeatures])
		if err != nil {
			continue
		}
		
		data.Features = append(data.Features, features)
		data.Labels = append(data.Labels, label)
		data.Metadata = append(data.Metadata, fmt.Sprintf("sample_%d", i))
	}
	
	return data, nil
}

// SplitDataset splits data into train, validation, and test sets.
func SplitDataset(data *TrainingData, trainRatio, valRatio float64) (train, val, test *TrainingData) {
	n := len(data.Features)
	trainEnd := int(float64(n) * trainRatio)
	valEnd := trainEnd + int(float64(n)*valRatio)
	
	train = &TrainingData{
		Features: data.Features[:trainEnd],
		Labels:   data.Labels[:trainEnd],
		Metadata: data.Metadata[:trainEnd],
	}
	
	val = &TrainingData{
		Features: data.Features[trainEnd:valEnd],
		Labels:   data.Labels[trainEnd:valEnd],
		Metadata: data.Metadata[trainEnd:valEnd],
	}
	
	test = &TrainingData{
		Features: data.Features[valEnd:],
		Labels:   data.Labels[valEnd:],
		Metadata: data.Metadata[valEnd:],
	}
	
	return
}

// TrainIsolationForest trains an Isolation Forest on the dataset.
// Returns trained model and validation metrics.
func TrainIsolationForest(data *TrainingData, config TrainingConfig) (*models.IsolationForest, *Metrics, error) {
	fmt.Printf("[Training] Isolation Forest: %d samples, %d features\n",
		len(data.Features), len(data.Features[0]))
	
	startTime := time.Now()
	
	// Create model
	iforest := models.NewIsolationForest(config.IForestConfig)
	
	// Train (unsupervised - only use features, ignore labels)
	if err := iforest.Train(data.Features); err != nil {
		return nil, nil, fmt.Errorf("training failed: %w", err)
	}
	
	trainTime := time.Since(startTime)
	fmt.Printf("[Training] Completed in %v\n", trainTime)
	
	// Evaluate on training data
	scores, err := iforest.ScoreBatch(data.Features)
	if err != nil {
		return nil, nil, fmt.Errorf("scoring failed: %w", err)
	}
	
	metrics := ComputeMetrics(scores, data.Labels, 0.5)
	metrics.TrainTime = trainTime
	
	fmt.Printf("[Metrics] Accuracy: %.2f%%, Precision: %.2f%%, Recall: %.2f%%, F1: %.2f%%\n",
		metrics.Accuracy*100, metrics.Precision*100, metrics.Recall*100, metrics.F1Score*100)
	
	// Save model
	if config.ModelOutputDir != "" {
		modelPath := config.ModelOutputDir + "/isolation_forest.json"
		if err := iforest.Save(modelPath); err != nil {
			return nil, nil, fmt.Errorf("failed to save model: %w", err)
		}
		fmt.Printf("[Saved] Model: %s\n", modelPath)
	}
	
	return iforest, metrics, nil
}

// TrainNeuralNetwork trains a sequence model (stub - full training requires gradient descent).
// For production: integrate with TensorFlow/PyTorch via cgo or gRPC.
func TrainNeuralNetwork(data *TrainingData, config TrainingConfig) (*models.SequenceModel, *Metrics, error) {
	fmt.Printf("[Training] Neural Network: %d samples, %d features\n",
		len(data.Features), len(data.Features[0]))
	
	startTime := time.Now()
	
	// Create model
	neuralNet := models.NewSequenceModel(config.NeuralConfig)
	neuralNet.InitializeWeights()
	
	// NOTE: Full training loop requires backpropagation implementation.
	// For production deployment, use:
	// 1. Train in Python (TensorFlow/PyTorch)
	// 2. Export to ONNX
	// 3. Load ONNX in Go using github.com/owulveryck/onnx-go
	// OR
	// 4. Use gRPC to call Python inference service
	
	fmt.Printf("[Training] Neural network training not implemented in this stub.\n")
	fmt.Printf("[Training] Use Python training pipeline (see training/train_neural.py)\n")
	
	// For now, just initialize and save
	trainTime := time.Since(startTime)
	
	// Save model
	if config.ModelOutputDir != "" {
		modelPath := config.ModelOutputDir + "/neural_net.json"
		if err := neuralNet.Save(modelPath); err != nil {
			return nil, nil, fmt.Errorf("failed to save model: %w", err)
		}
		fmt.Printf("[Saved] Model skeleton: %s\n", modelPath)
	}
	
	metrics := &Metrics{
		TrainTime: trainTime,
	}
	
	return neuralNet, metrics, nil
}

// Metrics holds model evaluation metrics.
type Metrics struct {
	Accuracy  float64
	Precision float64
	Recall    float64
	F1Score   float64
	AUC       float64
	
	TP int // True positives
	FP int // False positives
	TN int // True negatives
	FN int // False negatives
	
	TrainTime time.Duration
}

// ComputeMetrics computes classification metrics.
// scores: predicted scores [0, 1]
// labels: ground truth (0 = benign, 1 = malicious)
// threshold: decision boundary (default: 0.5)
func ComputeMetrics(scores []float64, labels []int, threshold float64) *Metrics {
	if len(scores) != len(labels) {
		return nil
	}
	
	var tp, fp, tn, fn int
	
	for i := range scores {
		predicted := 0
		if scores[i] >= threshold {
			predicted = 1
		}
		
		actual := labels[i]
		
		if predicted == 1 && actual == 1 {
			tp++
		} else if predicted == 1 && actual == 0 {
			fp++
		} else if predicted == 0 && actual == 0 {
			tn++
		} else if predicted == 0 && actual == 1 {
			fn++
		}
	}
	
	accuracy := float64(tp+tn) / float64(len(labels))
	
	precision := 0.0
	if tp+fp > 0 {
		precision = float64(tp) / float64(tp+fp)
	}
	
	recall := 0.0
	if tp+fn > 0 {
		recall = float64(tp) / float64(tp+fn)
	}
	
	f1 := 0.0
	if precision+recall > 0 {
		f1 = 2 * (precision * recall) / (precision + recall)
	}
	
	return &Metrics{
		Accuracy:  accuracy,
		Precision: precision,
		Recall:    recall,
		F1Score:   f1,
		TP:        tp,
		FP:        fp,
		TN:        tn,
		FN:        fn,
	}
}

// GenerateSyntheticDataset creates a synthetic dataset for testing.
// numSamples: total samples to generate
// maliciousRatio: fraction of malicious samples (default: 0.1)
func GenerateSyntheticDataset(numSamples int, numFeatures int, maliciousRatio float64) *TrainingData {
	data := &TrainingData{
		Features: make([][]float64, numSamples),
		Labels:   make([]int, numSamples),
		Metadata: make([]string, numSamples),
	}
	
	for i := 0; i < numSamples; i++ {
		features := make([]float64, numFeatures)
		
		// Determine if malicious
		isMalicious := float64(i)/float64(numSamples) < maliciousRatio
		
		for j := 0; j < numFeatures; j++ {
			if isMalicious {
				// Malicious: higher values, more variance
				features[j] = 5.0 + float64(i*j%100)/10.0
			} else {
				// Benign: lower values, less variance
				features[j] = 1.0 + float64(i*j%50)/50.0
			}
		}
		
		data.Features[i] = features
		if isMalicious {
			data.Labels[i] = 1
		} else {
			data.Labels[i] = 0
		}
		data.Metadata[i] = fmt.Sprintf("sample_%d", i)
	}
	
	return data
}

// SaveDataset saves a TrainingData to CSV.
func SaveDataset(data *TrainingData, path string) error {
	file, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}
	defer file.Close()
	
	writer := csv.NewWriter(file)
	defer writer.Flush()
	
	// Write header
	if len(data.Features) > 0 {
		header := make([]string, len(data.Features[0])+1)
		for i := 0; i < len(data.Features[0]); i++ {
			header[i] = fmt.Sprintf("feature_%d", i)
		}
		header[len(header)-1] = "label"
		writer.Write(header)
	}
	
	// Write data
	for i := range data.Features {
		record := make([]string, len(data.Features[i])+1)
		for j, val := range data.Features[i] {
			record[j] = fmt.Sprintf("%.6f", val)
		}
		record[len(record)-1] = fmt.Sprintf("%d", data.Labels[i])
		writer.Write(record)
	}
	
	return nil
}
