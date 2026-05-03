## What Are Scaling Laws?

---

### The Problem

Training a large model costs millions of dollars. If you have a fixed compute budget, should you train a bigger model for fewer steps, or a smaller model for more steps? For years, the AI field got this wrong — and the correction changed how every major lab trains models.

---

### Definition

**Scaling laws** are empirical relationships that predict a model's performance (loss) as a function of:
- **N** = number of parameters
- **D** = number of training tokens
- **C** = compute budget (in FLOPs)

The key finding is that loss follows a **power law** with respect to both model size and data size:
```
Loss(N, D) = A / N^α + B / D^β + L_∞
```

Where:
- `α` and `β` are scaling exponents (typically ~0.3–0.35)
- `L_∞` is the irreducible loss (the best possible performance)
- `A` and `B` are constants

**The central question:** For a fixed compute budget C, what is the optimal balance between N and D?

---

### Real-Life Analogy

Building a library and filling it with books.

**The wrong approach (Kaplan 2020):** Build a massive library with millions of shelves, but only fill 10% of them. The shelves are impressive, but most are empty. The library looks big but is not very useful.

**The right approach (Chinchilla 2022):** Build a library sized exactly for your book collection. Every shelf is full. The library is smaller in square footage but more useful because every shelf has books.

**The twist:** The smaller, full library costs less to build AND is more useful. This is the Chinchilla insight: for a fixed budget, model size and data should grow together.

---

### Tiny Numeric Example

**Power law for model size:**
```
Loss(N) = 2.5 / N^0.34
```

**Compute three model sizes:**

| Model | Parameters (N) | Predicted Loss |
|---|---|---|
| Small | 10M | 2.5 / (10^7)^0.34 = 2.5 / 316 = 0.0079 |
| Medium | 100M | 2.5 / (10^8)^0.34 = 2.5 / 631 = 0.0040 |
| Large | 1B | 2.5 / (10^9)^0.34 = 2.5 / 1259 = 0.0020 |

**Power law for data size:**
```
Loss(D) = 1.8 / D^0.28
```

**Training token counts:**

| Dataset | Tokens (D) | Predicted Loss |
|---|---|---|
| Small | 100M | 1.8 / (10^8)^0.28 = 1.8 / 52 = 0.0346 |
| Medium | 1B | 1.8 / (10^9)^0.28 = 1.8 / 83 = 0.0217 |
| Large | 10B | 1.8 / (10^10)^0.28 = 1.8 / 132 = 0.0136 |

**Combined loss:**
```
Loss(N, D) = 2.5 / N^0.34 + 1.8 / D^0.28 + 1.5
```

For N=100M, D=1B: Loss = 0.0040 + 0.0217 + 1.5 = 1.5257

This means both bigger models AND more data help, but with diminishing returns.

---

### Common Confusion

1. **"Scaling laws are theoretical."** No. They are purely empirical — curve fits to experimental data. They describe what happens, not why. The theoretical foundations are still being researched.

2. **"Bigger models always win."** Not for a fixed compute budget. A 70B model trained on 1.4T tokens (Chinchilla-optimal) outperforms a 280B model trained on 300B tokens (undertrained). Data matters as much as size.

3. **"Scaling laws predict exact loss numbers."** No. They predict relative trends. The exact constants vary by architecture, task, and data quality. But the power-law shape is remarkably consistent.

4. **"Scaling laws work forever."** Probably not. At some scale, other factors (data quality, architecture, reasoning) may become more important than raw scale. The power laws might break or saturate.

5. **"Scaling laws only apply to language models."** No. Similar power laws have been observed in vision models, speech models, reinforcement learning, and even biological neural networks.

---

### Where It Is Used in Our Code

`src/phase38/phase38_scaling_laws.py` — Simulates scaling law curves and visualizes the Chinchilla optimal point. Shows how loss improves with model size and data size, and compares different training strategies.
