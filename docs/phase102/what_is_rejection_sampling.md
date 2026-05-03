## What Is Rejection Sampling?

---

### The Problem

When a language model generates synthetic training data, most of the output is mediocre. A code generation model might produce 100 solutions to a programming problem, but only 30 pass the unit tests. The remaining 70 are syntactically valid but logically wrong — buggy, inefficient, or misaligned. If you train the model on all 100 solutions, the 70 bad examples dilute the signal and can actively degrade performance. How do you filter generated data so that only high-quality samples enter the training set?

---

### Definition

**Rejection Sampling** is a filtering procedure in which samples are generated from a model and then accepted or rejected based on a quality criterion — such as a reward model score, a verifier result, or a heuristic threshold. Only accepted samples are added to the training set. The procedure shifts the effective training distribution toward higher-quality outputs without modifying the generator's parameters.

**How it works:**
```
Generator distribution: P(x)  (broad, includes many low-quality samples)
Target distribution:    Q(x) proportional to P(x) * I[score(x) >= threshold]

Procedure:
  1. Generate N samples from P(x).
  2. Score each sample with verifier V(x).
  3. Accept samples where V(x) >= T.
  4. Train on accepted subset.

Effective acceptance rate:
  If P(x) has 30% high-quality samples and we generate 1000:
    Accepted: ~300
    Rejected: ~700
  Training distribution is now concentrated on the top 30%.
```

**Key properties:**
- The generator does not learn during sampling; filtering is a post-hoc step.
- Higher thresholds increase quality but decrease acceptance rate, creating a quality-quantity trade-off.
- Can be applied iteratively: train on accepted samples, regenerate, filter again.

**Why this matters:**
- Training on filtered synthetic data can outperform training on unfiltered human data.
- It is the simplest form of verifier-augmented generation and the foundation of self-improvement loops.
- It provides explicit control over training distribution quality through the threshold parameter.

---

### Real-Life Analogy

Imagine a publishing house that accepts unsolicited manuscripts. Ten thousand manuscripts arrive every year. The editor cannot read every page of every submission, so she uses a first-chapter test: she reads the first chapter of each manuscript and rejects those that do not meet quality standards for prose, pacing, and originality. Only the accepted first chapters proceed to full manuscript review. The rejected manuscripts never enter the publishing pipeline. The editor is the rejection sampler; the first-chapter test is the quality criterion; and the pool of accepted manuscripts is the filtered training distribution. The publishing house does not rewrite the rejected manuscripts — it simply discards them and focuses resources on the promising ones.

The trade-off is quantity versus quality. A lenient editor who accepts 80% of first chapters fills the pipeline with mediocre books, and the publishing house's reputation suffers. A strict editor who accepts only 2% ensures high quality but may reject brilliant manuscripts that start slowly. Setting the threshold is the central challenge. Too high, and you discard valuable training data; too low, and you poison the model with errors. There is also a subtle bias: if the editor prefers certain genres, the published catalog becomes homogeneous. Similarly, a verifier with a narrow quality model can bias the training set toward a specific solution style, reducing the model's creativity and robustness on out-of-distribution problems.

---

### Tiny Numeric Example

**Raw generation distribution:**
```
Generator: Gaussian with mean 0.5, std 1.5
True target mean: 2.0
Verifier: score(x) = -|x - 2.0| (higher is closer to target)
```

**Rejection sampling at different thresholds:**
```
Threshold | Accepted | Acceptance rate | Mean of accepted | Std of accepted
----------|----------|-----------------|------------------|----------------
-0.5      | 3,850    | 77%             | 1.42             | 1.10
0.0       | 2,400    | 48%             | 1.68             | 0.85
0.5       | 1,100    | 22%             | 1.89             | 0.60
1.0       | 280      | 5.6%            | 1.98             | 0.35
```

**Training effect on next iteration:**
```
Initial generator mean: 0.50
After training on threshold=0.5 accepted samples:
  Generator mean shifts to: 1.25
After next generation + filtering:
  Accepted mean: 1.89
  Generator mean after training: 1.72
After 3 iterations:
  Generator mean: 1.91
  Accepted mean: 1.97
```

**Quality-quantity trade-off visualization:**
```
Threshold | Training set size | Effective quality | Convergence speed
----------|-------------------|-------------------|------------------
-0.5      | Large             | Low               | Slow (noisy signal)
0.0       | Medium            | Medium            | Medium
0.5       | Small             | High              | Fast
1.0       | Tiny              | Very high         | Unstable (variance)
```

**The shift:** Rejection sampling shifts the training distribution toward the target mean. A threshold of 0.5 provides the best balance: high enough to filter noise, low enough to retain sufficient samples for stable training.

---

### Common Confusion

1. **"Rejection Sampling is just data cleaning."** It is not. Data cleaning removes pre-existing bad data from a fixed dataset. Rejection Sampling is an active generation-and-filter loop: the model generates candidates, and an external judge decides what enters the dataset. The dynamic interaction between generator and filter is what makes it powerful.

2. **"The generator improves during rejection sampling."** It does not. Rejection sampling is a data collection step. The generator is frozen during sampling. Training on the accepted samples happens afterward, in a separate step.

3. **"Higher thresholds are always better."** Not necessarily. A threshold that is too high produces too few accepted samples, leading to high-variance training and unstable convergence. The optimal threshold balances quality and quantity.

4. **"Rejection Sampling requires a learned verifier."** It does not. The quality criterion can be a simple heuristic, a symbolic checker, a unit test, or even human judgment. Any scoring function that separates good from bad samples works.

5. **"It is only used for synthetic data."** While most common in synthetic data pipelines, rejection sampling can filter any generated or retrieved content: search results, candidate translations, or proposed code edits.

6. **"Rejection Sampling and best-of-N are different."** They are closely related. Best-of-N selects the single highest-scoring sample from a pool. Rejection Sampling selects all samples above a threshold. Best-of-N is a special case of rejection sampling with an adaptive threshold.

7. **"Rejection Sampling eliminates the need for human labels."** It reduces the need but does not eliminate it. Humans design the verifier, validate the acceptance criteria, and spot-check the accepted samples. The filter automates bulk selection, not human judgment.

---

### Where It Is Used in Our Code

`src/phase102/phase102_synthetic_data.py` — We implement rejection sampling on Gaussian-generated samples using a distance-based verifier. We compare histograms of all samples versus accepted samples across four threshold values, showing how the accepted distribution shifts toward the true mean. We also measure acceptance rates and demonstrate the quality-quantity trade-off as the threshold increases.
