# Sovereign Dataset Sourcing & Labeling Guidelines

**Protocol**: Thirsty-Lang Family Ethical Dataset Ingestion (EDI)

## 1. Provenance Verification

Every dataset ingested into Project-AI must have a **Sovereign Source Certificate**.

- **Requirement**: Datasets must be signed by the provider's Ed25519 key.
- **Audit**: Clear text source metadata must be hashed into the **Ingestion Audit Chain**.

## 2. Ethical Labeling Guidelines

- **Law 0 Alignment**: Labels must not de-prioritize collective human welfare.
- **Double-Blind Verification**: Every label must be verified by two independent "Label Verifiers" (AI or Human) before being promoted to the **Sovereign Training Set**.
- **Compensation Transparency**: Guidelines for fair compensation and ethical treatment of human labelers must be cryptographically attached to the dataset metadata.

## 3. Data Licensing Enforcement

- **Automated Check**: The `DataIngestManager` (Thirsty-Lang) checks every shard against the `DATA_INGEST_LICENSE.md`.
- **Constraint**: No data with "Non-Commercial" restrictions is permitted in the Enterprise Production Plane.

---

# Sovereign Bias Audit & Evaluation Suite (Full Detail)

## 1. Structural Bias Detection

- **Metric**: Disparate Impact Ratio (DIR).
- **Threshold**: Systems must maintain a DIR between **0.8 and 1.2** for all protected classes (Race, Gender, Age, Jurisdiction).
- **Execution**: Run the `SovereignEvalSuite` on every model checkpoint before deployment.

## 2. Adversarial Robustness Eval

- **Target**: Models must resist "Behavioral Drift" attacks where a malicious verifier attempts to nudge the model toward Law 1 violation.
- **Test**: Simulated prompt injection and gradient-based attacks on the **Shadow Plane**.

## 3. Transparency & Explainability

- **XAI Integration**: Every decision must provide a "Sovereign Explanation Hash" that maps back to the specific training shards influenced the output.
