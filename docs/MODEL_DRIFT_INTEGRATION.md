# Model Drift Detection Integration

## Overview

Complete integration of model drift detection with the ML training pipeline for the SASE (Sovereign Adversarial Signal Engine) system. This enables automatic detection of distribution drift and triggers model retraining when performance degrades.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Drift Detection Pipeline                      │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
   ┌────▼────┐                                     ┌────▼────┐
   │  Drift  │                                     │Training │
   │Detector │                                     │Pipeline │
   └────┬────┘                                     └────┬────┘
        │                                               │
        │  1. Monitor Features                          │
        │  2. Calculate KL Divergence                   │
        │  3. Track Confidence Variance                 │
        │  4. Measure ASN Entropy                       │
        │                                               │
        └────────────────┬──────────────────────────────┘
                         │
                    ┌────▼────┐
                    │Retrain  │
                    │Trigger  │
                    └────┬────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   ┌────▼─────┐                      ┌───▼────┐
   │ Lock     │                      │Deploy  │
   │ Model    │                      │Model   │
   └──────────┘                      └────────┘
```

## Components

### 1. KLDivergenceCalculator

Calculates Kullback-Leibler divergence between historical and current feature distributions.

**Usage:**
```python
from src.cerberus.sase.advanced.model_drift import KLDivergenceCalculator

calc = KLDivergenceCalculator()
p = np.array([0.3, 0.4, 0.3])  # Historical distribution
q = np.array([0.2, 0.5, 0.3])  # Current distribution

kl = calc.calculate(p, q)
print(f"KL Divergence: {kl:.3f} bits")
```

**Key Features:**
- Automatic normalization of input distributions
- Epsilon handling to prevent log(0) errors
- Returns divergence in bits

### 2. DriftDetector

Monitors multiple drift indicators:
- **Feature Distribution Drift**: KL divergence > 0.5 bits
- **Confidence Variance Change**: |Δvar| > 0.1
- **ASN Entropy Change**: |Δentropy| > 0.15

**Usage:**
```python
from src.cerberus.sase.advanced.model_drift import DriftDetector

detector = DriftDetector()

# Build baseline
for features, confidence, entropy in training_data:
    detector.update_baseline(features, confidence, entropy)

# Detect drift
current_features = [...]
current_confidences = [...]
current_entropy = [...]

drift_result = detector.detect_drift(
    current_features,
    current_confidences,
    current_entropy
)

if drift_result["drift_detected"]:
    print(f"Drift detected! KL={drift_result['kl_divergence']:.3f}")
```

**Memory Management:**
- Maintains rolling window of last 1000 observations
- Prevents memory exhaustion in long-running systems

### 3. ModelTrainingPipeline

Complete ML training pipeline with drift integration hooks.

**Usage:**
```python
from src.cerberus.sase.advanced.model_drift import ModelTrainingPipeline

pipeline = ModelTrainingPipeline(
    model_path="models/sase_model",
    adapter_type="pytorch"  # or "huggingface", "dummy"
)

# Gather training data
stats = pipeline.gather_training_data(
    historical_features,
    historical_confidences,
    historical_labels
)

# Retrain
result = pipeline.retrain_model(epochs=20, learning_rate=0.001)

# Validate
validation = pipeline.validate_model(validation_threshold=0.85)

# Deploy if validation passed
if validation["status"] == "passed":
    deploy_result = pipeline.deploy_model()
```

**Pipeline Stages:**
1. **Lock Model**: Prevents concurrent modifications
2. **Gather Data**: Collects recent observations
3. **Retrain**: Trains model on new data
4. **Validate**: Checks model performance
5. **Deploy**: Updates production model (only if improved)
6. **Unlock**: Releases model lock

### 4. RetrainingTrigger

Orchestrates automatic retraining when drift is detected.

**Usage:**
```python
from src.cerberus.sase.advanced.model_drift import (
    DriftDetector,
    RetrainingTrigger,
    ModelTrainingPipeline
)

# Setup
detector = DriftDetector()
pipeline = ModelTrainingPipeline(adapter_type="pytorch")
trigger = RetrainingTrigger(
    pipeline=pipeline,
    min_retrain_interval=3600  # 1 hour cooldown
)

# Monitor and retrain
drift_result = detector.detect_drift(current_features, confidences, entropy)

if trigger.should_retrain(drift_result):
    retrain_result = trigger.trigger_retrain(
        historical_features=detector.historical_features,
        historical_confidences=detector.historical_confidences
    )
    
    print(f"Retraining: {retrain_result['status']}")
    print(f"Deployed: {retrain_result['deployed']}")
```

**Features:**
- **Cooldown Period**: Prevents excessive retraining
- **Full Pipeline Execution**: Automated end-to-end process
- **History Tracking**: Maintains last 100 retraining attempts
- **Safe Rollback**: Keeps old model if new model fails validation

## Integration Example

Complete end-to-end integration:

```python
import numpy as np
from src.cerberus.sase.advanced.model_drift import (
    DriftDetector,
    RetrainingTrigger,
    ModelTrainingPipeline
)

# Initialize components
detector = DriftDetector()
pipeline = ModelTrainingPipeline(
    model_path="models/sase_production",
    adapter_type="pytorch"
)
trigger = RetrainingTrigger(
    pipeline=pipeline,
    min_retrain_interval=3600  # 1 hour
)

# Build initial baseline (training phase)
print("Building baseline...")
for sample in training_dataset:
    detector.update_baseline(
        sample["features"],
        sample["confidence"],
        sample["asn_entropy"]
    )

# Production monitoring loop
print("Monitoring for drift...")
while True:
    # Collect current observations
    current_batch = collect_recent_observations(window_size=100)
    
    # Extract metrics
    current_features = [s["features"] for s in current_batch]
    current_confidences = [s["confidence"] for s in current_batch]
    current_entropy = [s["asn_entropy"] for s in current_batch]
    
    # Detect drift
    drift_result = detector.detect_drift(
        current_features,
        current_confidences,
        current_entropy
    )
    
    # Log metrics
    log_drift_metrics(drift_result)
    
    # Check if retraining needed
    if trigger.should_retrain(drift_result):
        print("Drift detected - initiating retraining...")
        
        retrain_result = trigger.trigger_retrain(
            historical_features=detector.historical_features,
            historical_confidences=detector.historical_confidences
        )
        
        if retrain_result["deployed"]:
            print(f"New model deployed! Metrics: {retrain_result['stages']['validate']['metrics']}")
        else:
            print(f"Retraining failed or validation not passed: {retrain_result['status']}")
    
    # Update baseline with current observations
    for sample in current_batch:
        detector.update_baseline(
            sample["features"],
            sample["confidence"],
            sample["asn_entropy"]
        )
    
    # Sleep until next check
    time.sleep(300)  # Check every 5 minutes
```

## Configuration

### Drift Thresholds

Adjust in `DriftDetector`:

```python
class DriftDetector:
    DRIFT_THRESHOLD_KL = 0.5        # KL divergence (bits)
    DRIFT_THRESHOLD_VARIANCE = 0.1  # Confidence variance change
    DRIFT_THRESHOLD_ENTROPY = 0.15  # ASN entropy change
```

### Retraining Parameters

```python
# Cooldown period
trigger = RetrainingTrigger(min_retrain_interval=3600)  # seconds

# Training hyperparameters
pipeline.retrain_model(
    epochs=20,
    learning_rate=0.001
)

# Validation threshold
pipeline.validate_model(validation_threshold=0.85)  # 85% accuracy
```

## Monitoring & Metrics

### Drift Metrics

The drift detector returns:
- `drift_detected`: Boolean flag
- `kl_divergence`: Feature distribution drift (bits)
- `variance_change`: Confidence variance change
- `entropy_change`: ASN entropy change
- `thresholds`: Current threshold values

### Retraining Metrics

The retraining trigger returns:
- `status`: "success", "failed", "validation_failed", "error"
- `deployed`: Boolean - whether new model was deployed
- `duration_seconds`: Total pipeline execution time
- `stages`: Detailed results from each stage
  - `lock`: Model locking status
  - `gather_data`: Data collection results
  - `retrain`: Training metrics (loss, epochs)
  - `validate`: Validation metrics (accuracy, precision, recall, F1)
  - `deploy`: Deployment status
  - `unlock`: Model unlock status

### Access History

```python
# Get retraining history
history = trigger.get_retrain_history()

for event in history:
    print(f"Retrain #{event['count']}")
    print(f"  Status: {event['status']}")
    print(f"  Deployed: {event['deployed']}")
    print(f"  Duration: {event['duration_seconds']:.2f}s")
    if event.get('stages', {}).get('validate'):
        metrics = event['stages']['validate']['metrics']
        print(f"  Accuracy: {metrics['accuracy']:.3f}")
```

## Testing

Run comprehensive tests:

```bash
# All drift detection tests
pytest tests/sase/test_model_drift.py -v

# Specific test class
pytest tests/sase/test_model_drift.py::TestDriftDetector -v

# Integration tests only
pytest tests/sase/test_model_drift.py::TestIntegratedDriftAndRetrain -v
```

## Security Considerations

1. **Model Locking**: Prevents concurrent modifications during retraining
2. **Validation Required**: New models must pass validation before deployment
3. **Safe Rollback**: Failed validations keep the old model in production
4. **Cooldown Period**: Prevents resource exhaustion from excessive retraining
5. **Memory Bounds**: Baseline history limited to 1000 observations

## Performance

- **Drift Detection**: O(n) where n = current batch size
- **KL Divergence**: O(k) where k = histogram bins (default: 10)
- **Memory Usage**: ~8MB for 1000 10-dimensional feature vectors
- **Retraining Time**: Depends on model size and training data (typically 1-10 minutes)

## Troubleshooting

### Drift Not Detected

- Check if baseline has sufficient data (minimum 100 samples)
- Verify threshold values are appropriate for your data
- Inspect actual metric values in `drift_result`

### Excessive Retraining

- Increase `min_retrain_interval`
- Adjust drift thresholds to be less sensitive
- Review data distribution for actual changes

### Retraining Failures

- Check model adapter compatibility
- Verify training data quality
- Inspect error messages in `retrain_result["error"]`
- Review logs for detailed error traces

## Future Enhancements

- [ ] A/B testing framework for model comparison
- [ ] Gradual rollout of new models
- [ ] Custom metric hooks for domain-specific drift
- [ ] Automated threshold tuning
- [ ] Multi-model ensemble support
- [ ] Distributed training integration

## References

- KL Divergence: [Wikipedia](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)
- Drift Detection: [Concept Drift Survey](https://arxiv.org/abs/1010.4784)
- Model Training: `scripts/train_sovereign.py`
- Model Adapter: `src/cognition/adapters/model_adapter.py`

---

**Last Updated**: 2026-04-11  
**Author**: SASE Engineering Team  
**Status**: Production Ready ✅
