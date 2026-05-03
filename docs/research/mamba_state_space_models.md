# Research: Mamba and State Space Models (SSMs)

**Status:** Missing from course. Should be Phase 34 or extension of Phase 18.
**Last Updated:** May 2026
**Sources:** Mamba paper (Dec 2023), Mamba-2 (Jun 2024), Griffin/Gemma 2 (Google, 2024), various follow-ups

---

## 1. The Problem

Transformers have O(N²) attention complexity. For a 1M token sequence, the attention matrix is 1T entries. This makes long sequences prohibitively expensive. Linear attention, RNNs, and structured state space models (S4, H3) were proposed as alternatives, but they all underperformed Transformers on language — until Mamba.

## 2. What It Is

Mamba is a **selective state space model** that:
- Scales **linearly** with sequence length: O(N) instead of O(N²)
- Achieves **Transformer-quality** results on language
- Maintains **fast inference** (like RNNs: constant memory per step, not growing KV cache)

### State Space Models (SSM) Core Idea

An SSM defines a continuous system:
```
h'(t) = Ah(t) + Bx(t)   (state evolution)
y(t)  = Ch(t) + Dx(t)   (output)
```

Discretized for sequences:
```
h_t = Āh_{t-1} + B̄x_t
y_t = Ch_t + Dx_t
```

This is essentially a **linear RNN** with learned transition matrices. The state h_t is a compressed summary of all previous inputs.

### Why Previous SSMs Failed on Language

Standard SSMs (S4, S5) use **input-independent** A, B, C matrices. This means the transition dynamics are fixed regardless of the token. They cannot do content-based reasoning: "remember this specific fact, forget that one."

### Mamba's Breakthrough: Selectivity

Mamba makes B, C, and Δ (discretization step) **functions of the input**:
```
B_t = Linear_B(x_t)
C_t = Linear_C(x_t)
Δ_t = Softplus(Linear_Δ(x_t) + bias)
```

Now the model can **selectively** propagate or forget information based on the current token — just like attention, but without the quadratic cost.

### Hardware-Aware Parallel Scan

The problem: if B and C depend on x_t, we cannot use the convolution trick that made S4 fast. Mamba solves this with a **parallel associative scan** (also called parallel scan or Blelloch scan):
- In training: processes the sequence in parallel using a tree reduction
- In inference: maintains a recurrent state like an RNN (constant memory!)

This gives the best of both worlds:
- **Training:** Parallel like Transformer
- **Inference:** Constant memory like RNN

## 3. Real-World Analogy

**Transformer attention** is like a student who re-reads their entire notebook before answering every question. For short notes this is fine. For a library, it's impossible.

**Mamba** is like a student who maintains a running summary. As they read each page, they decide: "This is important, add it to my summary" or "This is detail, ignore it." When asked a question, they only consult their summary — not the entire book. The summary is small and fixed-size no matter how long the book.

## 4. Results

- Mamba-3B outperforms Transformer-3B and matches Transformer-6B on language modeling
- 5× higher inference throughput than Transformers
- Linear scaling tested up to **million-length sequences**
- State-of-the-art on audio, genomics, and time series

### Mamba-2 (Jun 2024)
- Unified SSM and attention into a single framework (SSD algorithm)
- 8× faster training than Mamba-1
- Better scaling to larger models

### Real-World Adoption
- **Gemma 2** (Google, 2024): Uses Griffin (Gated Linear RNN with local attention)
- **Falcon Mamba** (TII, 2024): Pure Mamba architecture at 7B scale
- **Zamba** (Zyphra, 2024): Hybrid Mamba-Attention architecture

## 5. Common Confusion

- **Mamba is not just a faster RNN.** It has selective gating that RNNs lack, and hardware-aware parallel training.
- **It does not replace attention everywhere.** Hybrid models (Mamba + local attention) often work best.
- **The state is not interpretable.** Unlike LSTM cell states which sometimes track counters, Mamba's state is a high-dimensional learned compression.
- **Copying is harder than for Transformers.** Attention can trivially copy tokens from any position. Mamba must learn to retain information in its state, which is harder for rare copy operations.
- **Long-context recall is still being researched.** While Mamba scales linearly, retrieving information from the very beginning of a 1M token sequence is an active research area.

## 6. What We Would Build

A toy 1D selective SSM that:
- Processes a sequence with learned A, B, C matrices
- Shows how selectivity allows the model to remember some inputs and forget others
- Compares memory usage: Transformer KV cache grows with N, SSM state is constant

## 7. Why It Matters Now

- Mamba is the first sub-quadratic architecture to genuinely compete with Transformers on language
- It removes the KV cache entirely — a massive win for long-context inference
- Google, Meta, and OpenAI are all investing in hybrid attention-SSM architectures
- The field is actively debating: "Will the next GPT be a Mamba variant?"

## 8. Connection to Existing Phases

- **Phase 13 (RNNs):** Mamba is a highly advanced RNN with linear complexity
- **Phase 14 (LSTMs):** Mamba's selectivity is like learned input/output gates
- **Phase 18 (Transformers):** Mamba is the leading alternative to self-attention
- **Phase 25 (Inference Optimization):** Mamba eliminates the KV cache problem entirely

---

## References

- Gu & Dao (2023): "Mamba: Linear-Time Sequence Modeling with Selective State Spaces"
- Dao & Gu (2024): "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
- De et al. (2024): "Griffin: Mixing Gated Linear Recurrences with Local Attention for Efficient Language Models"
