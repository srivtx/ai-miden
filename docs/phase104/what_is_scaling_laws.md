## What Are Scaling Laws?

---

## The Problem

Training a large model costs millions of dollars in compute. Given a fixed budget of GPU-hours, should you train a 70-billion-parameter model on 300 billion tokens, or a 7-billion-parameter model on 3 trillion tokens? Historically, teams chose enormous models and relatively little data, assuming size was the dominant factor. But many of those models were severely undertrained. How do you predict the optimal balance before burning the budget?

---

## Definition

**Scaling Laws** describe how model performance (typically measured as test loss) predictably improves as a function of compute, model size (number of parameters), and training data size. They are empirical power-law relationships that allow researchers to forecast the loss of a model before it is trained.

**How it works:**
```
Loss  ≈  A / (N ^ alpha)  +  B / (D ^ beta)  +  C / (C ^ gamma)

Where:
  N = number of parameters
  D = number of training tokens
  C = compute (FLOPs)
  alpha, beta, gamma ≈ 0.05 to 0.1 (empirically fitted)
```

**Key findings:**
- **Chinchilla scaling laws:** for compute-optimal training, model size and data size should scale in roughly equal proportions (D ≈ 20N)
- Many large models (e.g., GPT-3) were undertrained by this standard
- Loss improvements are smooth and predictable over multiple orders of magnitude

**Why this matters:**
- Scaling laws prevent wasted compute on suboptimal configurations
- They guide decisions about whether to scale up data, parameters, or both
- They reveal that data quality and diversity may matter more than raw token count

---

## Real-Life Analogy

Imagine you are building a factory and you have a fixed budget. You can spend it on more machines or on running existing machines for more hours. If you buy too many machines but only run each one for a single shift, you waste capital on idle equipment. If you run a small handful of machines around the clock, you hit diminishing returns because the fleet is too small to process orders efficiently. Scaling laws are the engineering formula that tells you the optimal machine-hours balance for your budget.

But the factory analogy understates the stakes. In AI, a suboptimal choice does not just waste money; it produces a worse model. GPT-3 (175B parameters, ~300B tokens) was celebrated as a breakthrough, but the Chinchilla paper showed that a 70B model trained on 1.4 trillion tokens would achieve better loss for the same compute. The field had been building oversized factories and running them part-time. The law predicted this relationship before the 70B model was ever trained, demonstrating that empirical trends can override intuition.

The trade-off is between sample efficiency and inference cost. A smaller, better-trained model is cheaper to serve but requires more data to reach a given quality level. A larger model reaches the same quality with less data but costs more per inference. For a research team with one training run, the Chinchilla-optimal point minimizes loss. For a product team serving billions of queries, a smaller model may be preferable even if it required more data to train.

---

## Tiny Numeric Example

**Given a fixed compute budget of 10^21 FLOPs, two training configurations:**

| Configuration | Parameters | Tokens | Loss (predicted) |
|---------------|------------|--------|------------------|
| Oversized     | 175B       | 300B   | 1.85             |
| Chinchilla    | 70B        | 1,400B | 1.72             |
| Undersized    | 7B         | 14,000B| 1.91             |

**The Chinchilla configuration achieves the best loss by balancing size and data.**

**Scaling trend simulation:**
```
Compute (FLOPs)    Loss (synthetic power law)
1e18               2.50
1e19               2.10
1e20               1.85
1e21               1.65
1e22               1.50
```

**Sample efficiency comparison:**
```
Fully connected network (no inductive bias):
  200 training samples → 62% validation accuracy
  800 training samples → 78% validation accuracy

Locally connected network (spatial inductive bias):
  200 training samples → 81% validation accuracy
  800 training samples → 93% validation accuracy
```

**The shift:** The right architecture (inductive bias) achieves 81% accuracy with 200 samples, while the wrong architecture needs 800 samples to reach 78%. Scaling laws help you choose not just how much to train, but what to train.

---

## Common Confusion

1. **"Scaling laws are physical laws like gravity."** They are empirical trends fitted to data. They hold approximately over the ranges where they were measured, but extrapolation to radically different regimes (novel architectures, multimodal training) may fail.

2. **"Scaling laws say bigger is always better."** They say that loss predictably improves with scale, but they also prescribe proportional scaling of data. A bigger model without proportionally more data is suboptimal.

3. **"Scaling laws describe capability, not just loss."** Scaling laws predict average-case loss on a held-out set. They do not predict emergent capabilities, safety properties, or performance on specific reasoning tasks.

4. **"Following scaling laws guarantees the best model."** Scaling laws optimize for compute efficiency. Other constraints (latency, memory, interpretability) may push you toward a non-optimal loss point.

5. **"Data size and parameter size are completely interchangeable."** Within the law's range, there is some substitutability, but the relationship is sub-linear. Doubling data does not fully compensate for halving parameters.

6. **"Scaling laws only apply to language models."** Similar power-law relationships have been observed in vision, audio, and multimodal models, though the exact exponents differ by domain.

7. **"If you have infinite compute, you should build an infinite model."** Inference costs, deployment constraints, and data scarcity make infinite scaling impractical. The laws describe trends, not mandates.

---

## Where It Is Used in Our Code

`src/phase104/phase104_architecture_search.py` — We simulate a synthetic scaling law by plotting loss against compute on a log-log scale, demonstrating the predictable power-law relationship. We also compare sample efficiency curves for architectures with and without inductive bias, showing how the right architecture changes the effective scaling behavior.
