## What Is KV Cache Compression?

---

### The Problem

You are running inference with a 70-billion-parameter model on a document that is 500,000 tokens long. Every token that the model generates requires attending to every previous token. For each layer and each attention head, you must store a Key vector and a Value vector for every token in the sequence. At sequence length 500,000, with 80 layers, 8 heads per layer, and a head dimension of 128, the KV cache alone consumes 500,000 * 80 * 8 * 128 * 2 (key + value) * 2 bytes (FP16) = 163.84 GB of GPU memory. That is more memory than the model weights themselves. You cannot fit a batch size greater than 1, you cannot run on a single A100, and you certainly cannot scale to 1,000,000 tokens. The KV cache is not just a bottleneck; it is a hard wall.

---

### Definition

**KV Cache Compression** is the set of techniques that reduce the memory footprint of the Key-Value cache during autoregressive inference by evicting, merging, or quantifying "unimportant" tokens, while preserving enough information for the model to generate accurate next-token predictions.

**How it works:**
```
Full KV cache:   [K1, V1], [K2, V2], [K3, V3], ..., [Kn, Vn]  →  O(n) memory
Compressed cache: [K1, V1], [K5, V5], [K9, V9], ...             →  O(k) memory, k << n
```

**Key techniques:**
- **Eviction-based:** Keep only the tokens with the highest cumulative attention scores (H2O).
- **Observation-based:** During prefill, observe which tokens early layers attend to, and compress the cache for later layers (SnapKV).
- **Pyramid-based:** Use a smaller KV cache for earlier layers and a larger one for deeper layers, because not all layers need full context.

**Why this matters:**
- A 50% compression ratio doubles the maximum context length on the same GPU.
- At 1M tokens, even a 20% compression saves tens of gigabytes.
- Compression is orthogonal to PagedAttention: PagedAttention fixes fragmentation; compression fixes fundamental growth.

---

### Real-Life Analogy

Imagine a lawyer preparing for a trial with a 10,000-page document dump.
- **Full KV cache:** The lawyer reads every single page, keeps every page open on their desk, and refers to any page at any moment. After 5,000 pages, the desk collapses under the weight. This is accurate but physically impossible at scale.
- **Compressed KV cache:** The lawyer uses a smart assistant who watches which pages the lawyer actually refers to during early case review. The assistant keeps only the most-cited contracts, the key emails, and the summary pages. The other 8,000 pages are stored in a warehouse. The lawyer can still win the case because the crucial evidence is on the desk.
- **The trade-off:** The lawyer might occasionally need a page that was moved to the warehouse, causing a slight delay or a minor factual gap. But the alternative — a collapsed desk — is total failure. Compression trades a small amount of recall for the ability to operate at all.

---

### Tiny Numeric Example

**Sequence of 10 tokens with attention scores (simplified, one head):**
```
Token:    t1   t2   t3   t4   t5   t6   t7   t8   t9   t10
Score:    0.05 0.02 0.20 0.01 0.15 0.03 0.25 0.04 0.10 0.15
```

**Full KV cache:**
```
Memory: 10 tokens * 2 vectors * 128 dims * 2 bytes = 5,120 bytes
All 10 KV pairs retained.
```

**H2O compression (keep top 4 by cumulative score):**
```
Retained: t3 (0.20), t7 (0.25), t5 (0.15), t10 (0.15)
Memory: 4 tokens * 2 vectors * 128 dims * 2 bytes = 2,048 bytes
Compression ratio: 60% reduction
```

**Accuracy comparison on next-token prediction (toy simulation):**
```
Full cache:           0.92 probability on correct next token
H2O compressed:       0.88 probability on correct next token
Random eviction:      0.61 probability on correct next token
```

**The shift:** Intentionally keeping high-attention tokens loses only 4% of probability mass, while random eviction loses 31%. The eviction policy is everything.

---

### Common Confusion

1. **"KV cache compression is the same as quantization."** Quantization reduces the precision of each vector (e.g., FP16 to INT8). Compression reduces the number of vectors. You can do both, but they solve different problems.

2. **"Compression hurts accuracy because information is lost."** Only unimportant information is lost. If the eviction policy is good, the model's attention is already concentrated on the retained tokens, so accuracy degradation is minimal.

3. **"PagedAttention already solves the KV cache problem."** PagedAttention solves allocation fragmentation by using non-contiguous memory blocks. It does not reduce the total number of KV vectors stored. Compression attacks the O(n) growth directly.

4. **"You can just recompute the KV vectors from the original tokens."** Recomputing requires storing the full input sequence and running the forward pass again for every generation step. That destroys inference speed. The entire point of the KV cache is to avoid recomputation.

5. **"All layers need the same amount of context."** Empirically, early layers in transformer models attend broadly, while deep layers attend to specific semantic tokens. PyramidKV exploits this by compressing more aggressively in early layers.

6. **"Compression only helps with very long sequences."** Even at 4,000 tokens, a 50% compression halves KV memory. For batch size 8, that is the difference between fitting on one GPU and needing two.

7. **"The eviction policy can be static, like keeping the first and last N tokens."** Static policies fail on real data. The "heavy hitter" tokens — names, numbers, core concepts — appear unpredictably throughout the sequence. Attention-based eviction is dynamic and adapts to the input.

---

### Where It Is Used in Our Code

`src/phase113/phase113_kv_compression_concepts.py` — We simulate attention scores over a long synthetic sequence, implement H2O eviction by keeping top-k tokens by cumulative attention score, simulate SnapKV by observing which tokens early layers attend to, and compare memory usage across full KV, H2O, and SnapKV. We visualize attention heatmaps, retained tokens, and compression ratio versus accuracy trade-offs.

`src/phase113/phase113_kv_compression_colab.py` — We load Llama-3.2-3B-Instruct in FP16 on a T4 GPU, implement H2O compression during autoregressive generation on a real 4,000-token book passage, and measure peak memory, generation speed, and output coherence. We show that 50% compression enables 2x longer contexts on the same hardware.

(End of file - total 97 lines)
