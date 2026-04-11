<!--                                         [2026-03-04 09:48] -->
<!--                                        Productivity: Active -->

# Mathematical Model: Thirsty's Asymmetric Security

## 1. Threat & Attacker Model

We assume a rational attacker maximizing expected profit:

**Maximize:**
$$\Pi = (N_{targets} \times P_{success} \times V_{target}) - C_{total}$$

Where:

- $N_{targets}$: number of targets attacked
- $P_{success}$: probability exploit succeeds per target
- $V_{target}$: value extracted per successful exploit
- $C_{total}$: total cost of attack campaign

**Total Cost Decomposition:**
$$C_{total} = C_{dev} + (N_{targets} \times C_{transfer}) + C_{operational}$$

Where:

- $C_{dev}$: initial exploit development cost
- $C_{transfer}$: per-target adaptation cost
- $C_{operational}$: infrastructure, botnet, hosting, etc.

**Traditional Assumption:** $C_{transfer} \approx 0$ (Scale dominates)
**Sovereign Requirement:** $C_{transfer} \approx C_{dev}$ (Exploit non-transferable)

## 2. Transferability Formalization

Define exploit $E$.
Let:

- $C$: random variable representing context.
- $C_i$: context vector for target $i$.

**Condition for Reuse:**
Exploit transfer requires $H(C \mid E) \approx 0$ (knowledge of the exploit collapses context entropy).

**The Independence mandate:**
We assume a context vector $C$ with $d$ dimensions. Traditional decay assumes independence:
$$\bar{\tau} = \prod_{k=1}^{d} p_k$$

> [!WARNING]
> If dimensions are correlated, decay becomes **polynomial**. If independent, decay is **exponential**. Exponential decay is required to collapse attacker economics.

**Mandate:** Maximize statistical independence and minimize mutual information $I(D_k; D_j)$ between context dimensions.

## 3. Reuse Friction Index (RFI): Information-Theoretic Definition

A stronger formulation defines RFI in terms of entropy:

$$RFI = 1 - \frac{I(E; C)}{H(C)}$$

Where:

- $H(C)$: Total entropy of the context surface.
- $I(E; C)$: Mutual information between the exploit and the context (how much the exploit "knows" about the target).

This moves RFI from a probability heuristic to an information-theoretic quantity.

## 4. Expected Cost Under Asymmetry

The 100x claim is driven by **Information Acquisition Cost**:
$$C_{transfer} = C_{adapt} + C_{probe}$$

Where:

- $C_{probe}$: Cost of discovering the specific context (fingerprinting, side channels).
- $C_{adapt}$: Exploit modification cost.

Our framework ensures $C_{probe} \gg 0$ by poisoning side channels and maximizing entropy.

## 5. Structural Unfinishability Condition

Exploit becomes economically irrational (unfinishable) if:
$$\bar{\tau} < \frac{C_{dev} + C_{operational}}{P_{success} \times V_{target}}$$

Including $C_{operational}$ ensures botnet economics cannot compensate for entropy decay.

## 6. Engineering Requirement: The Dimension Count

To maintain $RFI > 0.95$ (assuming $\bar{\tau} < 0.05$):
If each dimension $k$ has survival probability $p_k = 0.7$:
$$d > \frac{\ln(0.05)}{\ln(0.7)} \approx 8.4$$

**Mandate:** The system must provide at least **9 independent entropy dimensions** to achieve structural unfinishability.

## 7. Formal Definition of an "Entropy Dimension" ($D_k$)

To ensure exponential decay, each dimension $D_k$ in the context vector $C$ must satisfy the following invariants:

1. **High Marginal Entropy**: $H(D_k) \ge S_{req}$. The dimension must provide sufficient surprise to an observer who has not probed the system.
2. **Statistical Independence**: $I(D_k; D_j) \le \epsilon$ for all $k \neq j$. Mutual information between dimensions must be near-zero to prevent cross-dimensional inference (e.g., inferring a schema variant from a tenant ID).
3. **Temporal Non-Transitivity**: $I(D_k(t); D_k(t + \Delta t)) \rightarrow 0$ for $\Delta t > T_{window}$. Observations from one temporal window must not assist in predicting the state of the next window.
4. **Observer-Sensitivity**: $I(D_k; E) \approx 0$. The exploit's static structure must contain zero information about the runtime instance of $D_k$.

## 8. Adversarial Probing Resistance Model

The attacker's success probability after $Q$ probes is modeled as:
$$P(success \mid Q) = 1 - e^{-Q \cdot 2^{-H(C)}}$$

Where $H(C)$ is the total joint entropy of the context vector. For a "structurally unfinishable" guarantee, we mandate:
$$H(C) \ge \log_2\left(\frac{Q_{max} \cdot P_{target}}{V_{target} \cdot \epsilon}\right)$$

In Project-AI, we target $H(C) \ge 64$ bits of runtime entropy per critical operation, forcing $Q \approx 1.8 \times 10^{19}$ probes to achieve parity.

## 9. Implementation Mandate

...
