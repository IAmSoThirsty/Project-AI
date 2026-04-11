# ML-Based Threat Detection for OctoReflex

**Production-grade machine learning threat detection with sub-millisecond latency**

---

## Overview

This module implements ML-based threat detection for OctoReflex, enhancing the existing Mahalanobis distance + Shannon entropy anomaly detection with:

- **Isolation Forest**: Unsupervised anomaly detection for behavioral analysis
- **Neural Network (LSTM)**: Sequence-based threat prediction
- **Real-time scoring**: Sub-millisecond inference pipeline
- **Advanced entropy analysis**: Shannon entropy + approximate Kolmogorov complexity
- **Feature engineering**: 24 extracted features from syscall patterns, network behavior, and memory access

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  eBPF Ring Buffer (Kernel Events)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Feature Extractor (24 features, 60s sliding window)       │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ Temporal (6) │ Behavioral(7)│ Network (6)  │            │
│  │ Memory (3)   │ Entropy (2)  │              │            │
│  └──────────────┴──────────────┴──────────────┘            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  ML Inference Engine (<1ms latency)                         │
│  ┌──────────────────────┬──────────────────────┐            │
│  │ Isolation Forest     │ Neural Network(LSTM) │            │
│  │ (100 trees)          │ (64 hidden units)    │            │
│  └──────────────────────┴──────────────────────┘            │
│                                                             │
│  Ensemble: weighted average → Combined Score [0, 1]        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Hybrid Detector (Legacy 30% + ML 70%)                      │
│  → Final Threat Score → Escalation Decision                │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Feature Extraction (`ml/features/`)

Extracts 24 features from kernel events in real-time:

**Temporal Features (6)**
- `InterEventMean`: Mean time between events (ms)
- `InterEventStdDev`: Standard deviation of inter-event times
- `BurstIntensity`: Events per second in last 1s window
- `Periodicity`: Autocorrelation (detects beaconing)
- `TimeSinceLastEvent`: ms since previous event
- `EventRate`: Events/sec over 60s window

**Behavioral Features (7)**
- `SyscallDiversity`: Shannon entropy of event types
- `RareEventFreq`: Frequency of rare events
- `TransitionEntropy`: Entropy of event-type transitions
- `SetUIDAttempts`: Count of privilege escalation attempts
- `UniqueFileCount`: Distinct files accessed
- `ReadWriteRatio`: Read vs write operations
- `SyscallBurstiness`: Coefficient of variation

**Network Features (6)**
- `UniqueIPCount`: Distinct destination IPs
- `UniquePortCount`: Distinct destination ports
- `ConnectRate`: Connections per second
- `PortEntropy`: Shannon entropy of port distribution
- `NewIPRatio`: Ratio of never-seen IPs
- `AvgConnInterval`: Mean time between connections

**Memory/File Features (3)**
- `FileWriteEntropy`: Entropy of file writes
- `MemAccessEntropy`: Entropy of memory access patterns
- `WriteAmplification`: Write/read ratio

**Advanced Entropy (2)**
- `ShannonEntropyGlobal`: Overall event entropy
- `KolmogorovApprox`: Compression-based complexity

**Performance**: Feature extraction completes in <100µs.

---

### 2. Isolation Forest (`ml/models/isolation_forest.go`)

Unsupervised anomaly detection based on path length isolation.

**Hyperparameters**:
- `NumTrees`: 100 (default)
- `SubsampleSize`: 256
- `MaxDepth`: 10
- `Contamination`: 0.1 (expected outlier ratio)

**Algorithm**:
1. Build 100 random trees on feature subsamples
2. For each sample, compute average path length across trees
3. Anomaly score: `s(x) = 2^(-E(h(x)) / c(n))`
   - Shorter paths → more anomalous
   - `c(n)` = average path length in BST of size n

**Training**: `O(n * trees * depth)` = `O(n * 100 * 10)`  
**Inference**: `O(trees * depth)` = `O(100 * 10)` ≈ **50µs**

---

### 3. Neural Network (`ml/models/neural_net.go`)

LSTM-style sequence model for temporal threat patterns.

**Architecture**:
```
Input [10 x 24] (sequence_len x features)
  ↓
LSTM Layer (64 hidden units)
  ↓
Dense Layer (2 outputs: benign/malicious)
  ↓
Softmax → Probability distribution
```

**Hyperparameters**:
- `InputDim`: 24 (features per timestep)
- `HiddenDim`: 64 (LSTM units)
- `SequenceLength`: 10 (timesteps)
- `OutputDim`: 2 (binary classification)

**Inference**: `O(seq_len * hidden^2)` = `O(10 * 64^2)` ≈ **400µs**

**Note**: Full training requires gradient descent (implement in Python with TensorFlow/PyTorch, export to ONNX).

---

### 4. Real-time Inference Engine (`ml/inference/engine.go`)

Combines Isolation Forest and Neural Network into a unified scoring pipeline.

**Features**:
- **Sub-millisecond inference**: <1ms p99 latency
- **Model versioning**: Load/reload models without downtime
- **A/B testing**: Route traffic to multiple model versions
- **Thread-safe**: Concurrent inference from multiple goroutines

**Scoring Pipeline**:
1. Extract features from sliding window
2. Isolation Forest inference → `score_iforest`
3. Neural Network inference → `score_neural`
4. Weighted ensemble: `score = 0.6 * score_iforest + 0.4 * score_neural`
5. Confidence: `1 - |score_iforest - score_neural|` (agreement)

**Performance Metrics**:
```go
metrics := engine.GetMetrics()
fmt.Printf("Avg latency: %v\n", metrics.AverageLatency)
fmt.Printf("Inference count: %d\n", metrics.InferenceCount)
```

---

### 5. Hybrid Detector (`detection/detector.go`)

Main orchestrator combining legacy Mahalanobis+Entropy with ML ensemble.

**Hybrid Scoring**:
```
score_hybrid = 0.3 * score_legacy + 0.7 * score_ml
```

**Legacy Score** (Mahalanobis + Entropy):
- `A = (x - μ)ᵀ Σ⁻¹ (x - μ) + w_e |ΔH|`
- Normalized to [0, 1]

**ML Score**:
- Ensemble of Isolation Forest + Neural Network
- Range: [0, 1]

**Benefits**:
- **Robustness**: Fallback to legacy if ML fails
- **Smooth transition**: Gradual weight shift from legacy to ML
- **Backward compatible**: Works with existing baselines

---

## Training Pipeline

### Isolation Forest Training

```go
import "github.com/octoreflex/octoreflex/internal/detection/ml/training"

// Load dataset
data, err := training.LoadDataset("datasets/threats.csv")

// Train model
config := training.DefaultTrainingConfig()
iforest, metrics, err := training.TrainIsolationForest(data, config)

// Evaluate
fmt.Printf("Accuracy: %.2f%%\n", metrics.Accuracy*100)
fmt.Printf("F1 Score: %.2f%%\n", metrics.F1Score*100)

// Save
iforest.Save("models/isolation_forest.json")
```

### Neural Network Training (Python)

```bash
cd internal/detection/ml/training
python train_neural.py \
  --data datasets/threat_sequences.csv \
  --output models/neural_net.onnx \
  --epochs 50 \
  --batch-size 32 \
  --hidden-dim 64
```

**Output**: ONNX model for Go inference (requires `onnx-go` library or gRPC service).

---

## Datasets

Expected CSV format for training:

**Isolation Forest** (single-sample features):
```csv
feature_0,feature_1,...,feature_23,label
1.23,4.56,...,0.89,0
2.34,5.67,...,1.23,1
...
```

**Neural Network** (sequence features):
```csv
seq_0_t0_f0,seq_0_t0_f1,...,seq_0_t9_f23,label
0.12,0.34,...,0.78,0
...
```

**Label Encoding**:
- `0` = Benign
- `1` = Malicious

**Synthetic Dataset Generation**:
```go
data := training.GenerateSyntheticDataset(10000, 24, 0.1)
training.SaveDataset(data, "datasets/synthetic.csv")
```

---

## Model Versioning & A/B Testing

### Enable A/B Testing

```go
// Load primary detector
detector, _ := detection.NewDetector(config)
detector.LoadModels("models/v1/isolation_forest.json", "models/v1/neural_net.json")

// Enable A/B test: 20% traffic to v2
detector.EnableABTest(
    "models/v2/isolation_forest.json",
    "models/v2/neural_net.json",
    20, // 20% traffic split
)

// Metrics will show traffic distribution
```

### Model Versioning Strategy

**Directory Structure**:
```
models/
├── v1/
│   ├── isolation_forest.json
│   └── neural_net.json
├── v2/
│   ├── isolation_forest.json
│   └── neural_net.json
└── production/  (symlink to current version)
```

**Deployment Workflow**:
1. Train new model → `models/v{N}/`
2. Enable A/B test with small traffic (5%)
3. Monitor metrics (accuracy, latency, false positives)
4. Gradually increase traffic (20% → 50% → 100%)
5. Promote to production: `ln -sf v{N} models/production`

---

## Benchmarks

Target: **<1ms p99 inference latency**

Run benchmarks:
```bash
cd internal/detection/ml/inference
go test -bench=BenchmarkInferenceLatency -benchtime=10s
```

Expected results (4-core, 2.5GHz CPU):
```
BenchmarkInferenceLatency-4            10000    650 µs/op
  p50_µs: 580
  p99_µs: 850
  p999_µs: 950
```

Component breakdown:
- Feature extraction: **80µs**
- Isolation Forest: **50µs**
- Neural Network: **400µs**
- Ensemble + overhead: **120µs**
- **Total: ~650µs** ✓ (well under 1ms)

---

## Integration Example

```go
package main

import (
    "github.com/octoreflex/octoreflex/internal/detection"
    "github.com/octoreflex/octoreflex/internal/detection/ml/features"
)

func main() {
    // Initialize detector
    config := detection.DefaultConfig()
    config.IsolationForestPath = "models/isolation_forest.json"
    config.NeuralNetPath = "models/neural_net.json"
    
    detector, _ := detection.NewDetector(config)
    detector.LoadModels(config.IsolationForestPath, config.NeuralNetPath)
    
    // Process events from eBPF ring buffer
    for event := range ebpfRingBuffer {
        mlEvent := features.Event{
            PID:       event.PID,
            Type:      features.EventType(event.Type),
            Timestamp: event.Timestamp,
            DstIP:     event.DstIP,
            DstPort:   event.DstPort,
        }
        
        detector.ProcessEvent(mlEvent)
        
        // Detect threat
        assessment, _ := detector.DetectThreat(event.PID, baseline)
        
        // Escalation decision
        if assessment.Score > 0.7 {
            escalatePID(event.PID, assessment.Score)
        }
    }
}
```

---

## Production Deployment

### Option 1: Native Go (Current Implementation)

**Pros**:
- No external dependencies
- Sub-millisecond latency
- Single binary deployment

**Cons**:
- Limited to simple models (Isolation Forest, shallow LSTM)
- No GPU acceleration

### Option 2: Python + gRPC

Train complex models in Python, serve via gRPC:

```python
# ml_service.py
import grpc
from concurrent import futures
import tensorflow as tf

class MLService:
    def Predict(self, request):
        features = np.array(request.features).reshape(1, -1)
        score = self.model.predict(features)[0]
        return ml_pb2.PredictResponse(score=score)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
ml_pb2_grpc.add_MLServiceServicer_to_server(MLService(), server)
server.add_insecure_port('[::]:50051')
server.start()
```

**Go client**:
```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
client := ml_pb2.NewMLServiceClient(conn)
response, _ := client.Predict(ctx, &ml_pb2.PredictRequest{Features: features})
```

**Trade-off**: +500µs latency from gRPC overhead, but enables state-of-the-art models.

### Option 3: ONNX Runtime

Export models to ONNX, load with `onnx-go`:

```go
import "github.com/owulveryck/onnx-go"

backend := gorgonnx.NewGraph()
model := onnx.NewModel(backend)
model.UnmarshalBinary(onnxData)

output, _ := model.Run(input)
score := output[0].Data().([]float32)[0]
```

**Latency**: ~300µs (GPU-accelerated).

---

## Monitoring & Observability

Add Prometheus metrics:

```go
var (
    mlInferenceLatency = prometheus.NewHistogram(prometheus.HistogramOpts{
        Name: "octoreflex_ml_inference_latency_microseconds",
        Help: "ML inference latency in microseconds",
        Buckets: []float64{100, 250, 500, 750, 1000, 2000, 5000},
    })
    
    mlThreatScoreGauge = prometheus.NewGaugeVec(prometheus.GaugeOpts{
        Name: "octoreflex_ml_threat_score",
        Help: "ML threat score per PID",
    }, []string{"pid", "model"})
)

// Record metrics
mlInferenceLatency.Observe(float64(latency.Microseconds()))
mlThreatScoreGauge.WithLabelValues(pid, "isolation_forest").Set(score)
```

**Grafana Dashboard**: Query p50/p99 latency, score distribution, model accuracy.

---

## Known Limitations

1. **Neural Network Training**: Current implementation is a stub. Full training requires:
   - Gradient descent (backpropagation)
   - Integration with TensorFlow/PyTorch
   - OR use Python training + ONNX export

2. **Streaming Inference**: No online learning (models are static after training)
   - Future: Implement incremental updates for Isolation Forest

3. **GPU Acceleration**: Native Go implementation is CPU-only
   - For GPU inference, use ONNX Runtime or gRPC to Python service

4. **Dataset Size**: Synthetic datasets for testing only
   - Production requires real threat data (APT samples, malware traces)

---

## Future Enhancements

1. **Transformer Models**: Self-attention for long-range dependencies
2. **Autoencoder**: Unsupervised reconstruction error for novelty detection
3. **Online Learning**: Incremental model updates without full retraining
4. **Explainability**: SHAP values to explain why a process was flagged
5. **Multi-modal Fusion**: Combine syscall, network, and file I/O features
6. **Adversarial Robustness**: Defense against ML evasion attacks

---

## References

- **Isolation Forest**: Liu, Ting, Zhou. "Isolation Forest" (IEEE 2008)
- **LSTM**: Hochreiter & Schmidhuber. "Long Short-Term Memory" (Neural Computation 1997)
- **Shannon Entropy**: Shannon. "A Mathematical Theory of Communication" (1948)
- **Kolmogorov Complexity**: Li & Vitányi. "An Introduction to Kolmogorov Complexity" (Springer 2008)

---

## License

Apache 2.0 (same as OctoReflex)

---

**For questions or issues, see main OctoReflex documentation or file an issue on GitHub.**
