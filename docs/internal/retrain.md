# Retraining the AI Persona Detectors

This document describes the CLI retrain helper and the retraining behavior used by the
AI Persona.

## Overview

The repository includes a lightweight CLI helper at `tools/retrain_detectors.py` that
lets you retrain the persona's Zeroth/First-law detectors without opening the GUI. This
is useful for automated retraining, scheduled jobs, or debugging model updates.

## Model artifacts and vocab

When retraining, the persona saves model artifacts and vocabulary under
`data/ai_persona/`:

- `zeroth_detector.pt`, `first_detector.pt` — PyTorch model weights (written if `torch` is available)
- `ml_vocab.json` — saved vocabulary (always written when retrain runs)
- `retrain_audit.log` — simple JSON lines audit log with timestamp and example counts

## CLI usage

PowerShell examples:

```powershell
# Synchronous retrain (runs and exits)
python .\tools\retrain_detectors.py --data-dir .\data

# Start retrain in background and poll progress until completion
python .\tools\retrain_detectors.py --async --data-dir .\data
```

## Retrain behavior

- If `scikit-learn` is available, retraining will use `TfidfVectorizer` to build feature vectors. If not, a simple

  bag-of-words vector based on saved vocabulary will be used.

- If `torch` is installed, retraining will train small linear detectors and save serialized weights. If not,

  the retrain flow still updates `ml_vocab.json` and sets `ml_last_trained` so retrain
  events are recorded.

- Retrain writes a small audit entry to `data/ai_persona/retrain_audit.log` containing timestamp, example counts, and

  whether `torch`/`sklearn` were available.

- When saving model files, existing files are backed up with a timestamped `.bak` copy when possible.

## Security notes

Retraining is an administrative action. Always validate training data and keep an audit
trail of changes. ML detectors augment the Four Laws by providing scores and
explainability tokens, but the Four Laws remain the authoritative control mechanism. Use
the Learning Request Log and Black Vault for human-in-the-loop approvals prior to
persistent learning.


---

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->
