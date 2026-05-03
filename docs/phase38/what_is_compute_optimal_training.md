## What Is Compute-Optimal Training?

---

### The Problem

You have $10 million to train a model. Should you build a 100B-parameter model and train it on 200B tokens? Or a 10B-parameter model and train it on 2T tokens? Or something in between? The answer determines whether your model is good or mediocre — and the wrong choice wastes millions.

---

### Definition

**Compute-optimal training** is the strategy of choosing model size (N) and data size (D) to minimize loss for a fixed compute budget C.

**Compute is approximately:**
```
C ≈ 6 × N × D
```
(6 FLOPs per parameter per token for standard Transformers)

**The Chinchilla finding (DeepMind, 2022):**
For a fixed compute budget C, the optimal choices are:
```
N_optimal ∝ C^0.50
D_optimal ∝ C^0.50
```

In practical terms:
```
D_optimal ≈ 20 × N
```

A 70B parameter model needs **1.4 trillion tokens** for compute-optimal training.

**The Kaplan finding (OpenAI, 2020) — outdated:**
```
N_optimal ∝ C^0.73
D_optimal ∝ C^0.27
```

Kaplan suggested favoring model size over data. This led to undertrained giants like GPT-3 (175B params, 300B tokens — it should have used ~3.5T tokens).

---

### Real-Life Analogy

Training athletes for the Olympics with a fixed budget.
- **Kaplan approach:** Recruit the tallest athletes (bigger model) but only train them for 2 months (less data). They have genetic potential but lack conditioning.
- **Chinchilla approach:** Recruit well-sized athletes and train them for 2 years (balanced). They reach their full potential because they have both genetics AND conditioning.

The tallest untrained athlete loses to the moderately-sized well-trained one.

---

### Tiny Numeric Example

**Compute budget:** C = 10^21 FLOPs

**Kaplan recommendation:**
```
N = C^0.73 ≈ (10^21)^0.73 ≈ 10^15 parameters  (impossibly large!)
D = C^0.27 ≈ (10^21)^0.27 ≈ 10^6 tokens       (way too small)
```

Actually, let us use more realistic numbers. For C = 10^20 FLOPs:

**Kaplan:**
```
N ≈ 100B parameters
D ≈ 170B tokens
Ratio D/N ≈ 1.7
```

**Chinchilla:**
```
N ≈ 35B parameters
D ≈ 700B tokens
Ratio D/N ≈ 20
```

**Result:** The Chinchilla model is 3× smaller but trained on 4× more data. It achieves better loss with the same compute budget.

**Real-world example:**
- Gopher (DeepMind, 2021): 280B params, 300B tokens — undertrained
- Chinchilla (DeepMind, 2022): 70B params, 1.4T tokens — compute-optimal
- Chinchilla outperforms Gopher despite being 4× smaller!

---

### Common Confusion

1. **"Compute-optimal means best possible model."** No. It means best model FOR A FIXED BUDGET. If you have more money, a bigger model trained on more data will always be better.

2. **"Chinchilla says all models should use D = 20N."** That is the approximate rule of thumb. Recent work suggests the ratio varies: smaller models benefit from D/N ≈ 100, while very large models might need only D/N ≈ 10.

3. **"Over-training is wasteful."** Not necessarily. Llama 3 8B trains on 15T tokens (D/N ≈ 1875). This is massively over-trained by Chinchilla standards, but the quality keeps improving. Chinchilla is compute-optimal; over-training can be quality-optimal.

4. **"Compute-optimal training is cheaper."** Yes! A smaller model trained longer uses the same compute but less memory. You can fit it on fewer GPUs. Chinchilla 70B costs the same as Gopher 280B but runs on 1/4 the hardware.

5. **"Scaling laws tell you the exact hyperparameters."** No. They tell you the approximate region to search in. You still need to tune learning rate schedules, batch sizes, and data mixing within that region.

---

### Where It Is Used in Our Code

`src/phase38/phase38_scaling_laws.py` — Visualizes the compute-optimal frontier. Shows how different (N, D) pairs with the same compute budget produce different losses, and identifies the Chinchilla-optimal point.
