## What Is the Chinchilla Rule?

---

### The Problem

You are about to launch a training run for a new LLM. Your team has been debating for weeks: should we make the model bigger, or train it longer? There are only so many GPUs and so much time. How do you settle this debate with math instead of opinions?

---

### Definition

The **Chinchilla rule** is the practical guideline derived from Chinchilla scaling laws:

```
For compute-optimal training:  D ≈ 20 × N
```

Where:
- **D** = number of training tokens (in billions)
- **N** = number of model parameters (in billions)

**Examples:**

| Model | Parameters (B) | Chinchilla Tokens (B) | Actual Tokens (B) | Status |
|---|---|---|---|---|
| GPT-3 | 175 | 3,500 | 300 | Severely undertrained |
| Gopher | 280 | 5,600 | 300 | Severely undertrained |
| Chinchilla | 70 | 1,400 | 1,400 | Compute-optimal |
| Llama 2 70B | 70 | 1,400 | 2,000 | Slightly over-trained |
| Llama 3 8B | 8 | 160 | 15,000 | Massively over-trained |

**What over-training achieves:** Llama 3 8B outperforms much larger models from 2022 because it was trained on 15 trillion tokens. The quality improvements from extra data did not saturate.

---

### Real-Life Analogy

Learning to play chess.
- **Under-trained (Kaplan-style):** Study 10 advanced opening books once. You know many openings superficially but forget them in real games.
- **Compute-optimal (Chinchilla):** Study 2 advanced opening books deeply, practicing each line 100 times. You master fewer openings but play them perfectly.
- **Over-trained (Llama 3-style):** Study those same 2 books 1000 times each. You not only master the openings but also discover subtle patterns and transpositions that others miss.

The Chinchilla rule says: do not buy more books than you have time to study deeply.

---

### Tiny Numeric Example

**You want to train a 10B parameter model.**

**Chinchilla-optimal data:**
```
D = 20 × 10B = 200B tokens
```

**Training time estimate (on 1024 A100 GPUs):**
```
Compute = 6 × 10B × 200B = 12 × 10^21 FLOPs
A100 throughput ≈ 312 TFLOPs/s (with sparsity)
Time = 12 × 10^21 / (1024 × 312 × 10^12) ≈ 37,500 seconds ≈ 10.4 hours
```

**What if you train on only 20B tokens (Kaplan-style)?**
```
Compute = 6 × 10B × 20B = 1.2 × 10^21 FLOPs
Time ≈ 1 hour
```

Same model, 10× less data, 10× less time — but significantly worse loss.

**What if you train on 1T tokens (over-trained)?**
```
Compute = 6 × 10B × 1T = 60 × 10^21 FLOPs
Time ≈ 52 hours
```

Much more expensive, but the model keeps improving. Whether it is worth it depends on your budget and quality requirements.

---

### Common Confusion

1. **"D = 20N is a hard rule."** No. It is an approximation derived from empirical fits. The exact optimal ratio depends on the architecture, data quality, and task. Recent work suggests D/N ratios from 10 to 200 can be optimal depending on the situation.

2. **"Following Chinchilla guarantees the best model."** No. It guarantees the best model FOR A FIXED COMPUTE BUDGET. If you can afford more compute, bigger + more data is always better.

3. **"The Chinchilla paper used small models."** No. Chinchilla trained models from 400M to 16B parameters and extrapolated. The 70B recommendation is an extrapolation, but it has been validated by Llama 2 and other models.

4. **"Chinchilla means we should all train tiny models."** No. It means we should train appropriately-sized models with enough data. For a given quality target, you still want the largest model you can afford — just with the right amount of data.

5. **"We have infinite data, so Chinchilla does not matter."** We do not have infinite data. High-quality text on the internet is estimated at ~10T tokens. We are approaching the "data wall" where scaling D becomes impossible without synthetic data or multi-epoch training.

---

### Where It Is Used in Our Code

`src/phase38/phase38_scaling_laws.py` — Plots the Chinchilla-optimal line D = 20N against various model training runs. Shows which models are undertrained, compute-optimal, or over-trained.
