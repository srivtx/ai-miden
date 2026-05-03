## What Is Mamba?

---

### The Problem

Transformers dominate AI, but their O(N²) attention makes long sequences expensive. RNNs are O(N) but forgetful and hard to train in parallel. State space models are O(N) and parallelizable, but earlier versions (S4, H3) used fixed parameters that could not do content-based reasoning. We need a model that is:
- Fast like an RNN (linear time, constant memory)
- Trainable like a Transformer (parallelizable)
- Smart like attention (content-aware, selective)

---

### Definition

**Mamba** is a selective state space model introduced by Gu & Dao in December 2023. It combines three key innovations:

1. **Selective State Spaces:** B, C, and Δ are computed from the input token, allowing the model to selectively remember or forget.
2. **Hardware-Aware Parallel Scan:** A GPU-efficient algorithm that trains the selective recurrence in parallel.
3. **Simplified Architecture:** No attention, no MLP blocks — just stacked selective SSM layers with gating.

**Core equation:**
```
h_t = Ā_t · h_{t-1} + B̄_t · x_t
y_t = C_t · h_t

where:
  B_t = Linear_B(x_t)
  C_t = Linear_C(x_t)
  Δ_t = Softplus(Linear_Δ(x_t) + bias)
  Ā_t = discretize(A, Δ_t)
  B̄_t = discretize(B_t, Δ_t)
```

**Discretization** converts the continuous SSM to a discrete step using the zero-order hold method:
```
Ā = exp(Δ · A)
B̄ = (Δ · A)⁻¹ · (exp(Δ · A) - I) · (Δ · B)
```

(For diagonal A, this simplifies to element-wise operations.)

---

### Real-Life Analogy

Mamba is like an elite executive assistant who sits in on every meeting.
- **Standard SSM:** The assistant takes notes at a constant rate, writing the same amount for every comment. They quickly run out of paper or miss key points.
- **Mamba:** The assistant actively decides what to write. When the CEO speaks, they take detailed notes. When someone discusses lunch plans, they ignore it. They maintain a concise, high-quality summary that fits on one page. At the end of the year, they can answer questions about any important decision without re-reading 10,000 pages of transcripts.

---

### Tiny Numeric Example

**Task:** A sequence contains occasional "important" impulses (value = 5.0) mixed with noise (value = 0.1). The target is the cumulative sum of only the important impulses.

**Input:** x = [5.0, 0.1, 0.1, 5.0, 0.1, 0.1, 5.0, 0.1]
**Target:** y = [5.0, 5.0, 5.0, 10.0, 10.0, 10.0, 15.0, 15.0]

**Non-selective SSM (fixed B = 0.5):**
```
h_t = 0.9·h_{t-1} + 0.5·x_t
```
This accumulates BOTH impulses and noise. It cannot learn to ignore noise.

**Selective SSM (Mamba-style):**
```
B_t = sigmoid(w·x_t + b)
```
The model learns that large x_t should have large B_t, and small x_t should have small B_t.

**Learned behavior:**
```
x = [5.0, 0.1, 0.1, 5.0, ...]
B = [0.95, 0.05, 0.05, 0.95, ...]   (learned to filter!)
```

Now the state only accumulates important impulses:
```
h_0 = 0.95·5.0 = 4.75
h_1 = 0.9·4.75 + 0.05·0.1 ≈ 4.28
h_2 = 0.9·4.28 + 0.05·0.1 ≈ 3.86
h_3 = 0.9·3.86 + 0.95·5.0 ≈ 8.22
```

The output approximately tracks the cumulative sum of important events.

---

### Common Confusion

1. **"Mamba replaces all Transformers."** Not yet. Mamba excels at long sequences and fast inference, but Transformers still win on some tasks, especially those requiring precise copying or retrieval of specific tokens. Hybrid models (Mamba + local attention) are currently the frontier.

2. **"Mamba has no memory bottleneck."** It has a different bottleneck. Instead of a growing KV cache, Mamba has a fixed-size state vector. If the state is too small, information is compressed and lost. If the state is too large, compute increases.

3. **"Mamba-2 is just a faster Mamba."** Mamba-2 (June 2024) is a deeper rethinking. It unifies SSMs and attention into a single framework called SSD (State Space Duality). This lets Mamba-2 use some of the same optimizations as Flash Attention, making it 8× faster than Mamba-1.

4. **"Mamba cannot do in-context learning."** It can, but differently. Transformers do in-context learning via attention to previous tokens. Mamba does it by compressing relevant context into its state. Some tasks are easier with attention; others work fine in the state.

5. **"Mamba eliminates the need for inference optimization."** No. While Mamba removes the KV cache problem, you still care about quantization, batching, and throughput. But the memory savings are dramatic: a 1M-token context needs constant memory instead of linearly growing cache.

---

### Where It Is Used in Our Code

`src/phase34/phase34_mamba.py` — A simplified selective SSM in NumPy that learns to filter important impulses from noise. Shows the core mechanics of selectivity and state evolution.

`src/phase34/phase34_mamba_colab.py` — A full Mamba-style model in PyTorch trained on a selective copy task, demonstrating linear scaling and constant inference memory.
