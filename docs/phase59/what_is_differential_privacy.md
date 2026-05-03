## What Is Differential Privacy?

---

### The Problem

Federated learning keeps raw data local, but model updates can still leak sensitive information. If a hospital's update is very specific, an attacker might reconstruct patient records from the gradient. How do you mathematically guarantee that no individual's data can be identified from the model?

---

### Definition

**Differential privacy (DP)** is a mathematical framework that guarantees the output of a computation (like a model) is statistically indistinguishable whether or not any single individual's data was included.

**The formal definition:**
```
A mechanism M is (ε, δ)-differentially private if for all datasets D, D' 
that differ by one record, and for all outputs S:

P[M(D) ∈ S] ≤ e^ε * P[M(D') ∈ S] + δ
```

**In plain English:**
- Changing one person's data in the dataset should not noticeably change the model
- ε (epsilon) = privacy budget. Smaller ε = stronger privacy.
- δ (delta) = probability of failure. Usually set to a very small number like 1/n².

**How to achieve DP in ML:**
```
1. Clip gradients: bound the maximum influence of any single example
   g_clipped = g * min(1, C / ||g||)

2. Add noise: add Gaussian or Laplace noise calibrated to the clip bound
   g_private = g_clipped + noise(0, σ²C²)

3. Track privacy budget: sum up ε across training steps
```

**Why this matters:**
- DP provides formal, provable privacy guarantees
- Used by Apple (iOS keyboard), Google (Chrome), and the US Census Bureau
- Required for HIPAA-compliant and GDPR-compliant ML

---

### Real-Life Analogy

A witness protection program for data.
- **Without DP:** A witness testifies in court. Skilled investigators can deduce where they live from subtle clues in their testimony.
- **With DP:** The witness testifies through a voice scrambler and sits behind a screen. The testimony is useful, but no one can identify the witness. Even if they remove one witness, the overall testimony barely changes.
- **Epsilon (ε):** How loud the voice scrambler is. Low ε = heavy scrambling = very private but less clear. High ε = light scrambling = clearer but less private.

Differential privacy is the voice scrambler for machine learning.

---

### Tiny Numeric Example

**Dataset:** 1000 people. Average income = $50,000.
**Question:** What is the average income?

**Without DP:**
```
Release: $50,000
Attacker removes one person (Alice, income $200,000):
  New average = $49,850
Attacker deduces: Alice's income ≈ $200,000
```

**With DP (ε=1, sensitivity = $100,000/1000 = $100):**
```
Noise scale = sensitivity / ε = $100
Noisy average = $50,000 + Laplace(0, $100) = $50,047

Attacker removes Alice:
  True new average = $49,850
  Noisy new average = $49,850 + Laplace(0, $100) = $49,923

Difference between noisy averages: $50,047 - $49,923 = $124
This is within the noise range. Attacker cannot confidently 
deduce Alice's income.
```

**Privacy-utility trade-off:**
```
ε=0.1: noise = $1000, average = $50,000 ± $1000 (very private, useless)
ε=1:   noise = $100,  average = $50,000 ± $100  (moderate privacy)
ε=10:  noise = $10,   average = $50,000 ± $10   (weak privacy, accurate)
```

---

### Common Confusion

1. **"DP means the data is encrypted."** No. DP perturbs the OUTPUT, not the data. The model itself is noisy.

2. **"DP guarantees absolute privacy."** No. It guarantees bounded privacy loss with probability 1-δ. For very small δ, the guarantee is effectively absolute.

3. **"DP makes models useless."** At very low ε, yes. But ε=1-8 is practical for many applications. Apple's iOS uses ε=2-4.

4. **"DP is only for federated learning."** No. It can be applied to any data release: census data, search trends, medical studies.

5. **"You can add DP after training."** No. DP must be built into the training process (gradient clipping + noise addition at each step).

---

### Where It Is Used in Our Code

`src/phase59/phase59_federated_learning.py` — We add Gaussian noise to clipped gradients during federated averaging, demonstrating the privacy-utility trade-off: more noise protects privacy but slows convergence.
