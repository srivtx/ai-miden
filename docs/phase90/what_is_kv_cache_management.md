## What Is KV Cache Management?

---

## The Problem

In transformer inference, computing attention for token N requires the key and value vectors for tokens 1 through N. Recomputing them from scratch every step would make generation impossibly slow. Storing them in a cache saves compute but consumes enormous amounts of high-bandwidth GPU memory. Poor management of that memory limits batch size, sequence length, and the number of concurrent users a serving system can support.

---

## Definition

**KV cache management** is the set of techniques used to store, organize, and reuse key and value tensors during autoregressive generation while minimizing memory overhead and fragmentation.

**How it works:**
```
Standard KV cache usage:
  1. Prompt phase: compute K and V for all prompt tokens, store in cache
  2. Generation step N:
       - Compute K and V for the new token only
       - Append them to the cache
       - Attention uses cached K and V for tokens 1..N
       - No recomputation of earlier tokens

Memory optimization techniques:
  - Paging: split cache into fixed-size blocks, allocate on demand
  - Quantization: store K and V in lower precision (e.g., FP16 or INT8)
  - CPU offloading: move inactive sequences to host memory
  - Prefix sharing: reuse cached K and V for shared prompt prefixes
```

**Why this matters:**
- Without a KV cache, generating a 1,024-token sequence requires 1,024 full forward passes through all previous tokens.
- With a KV cache, each generation step is O(1) in prompt length rather than O(N).
- A 1-billion-parameter model with batch size 8 and sequence length 1,024 stores roughly 1.6 GB in the KV cache, making management critical for throughput.

---

## Real-Life Analogy

Reading a long novel, you keep notes on each chapter's characters and plot so you do not have to re-read earlier chapters to understand the current one. The notebook is your cache. Good management means organizing notes efficiently so the notebook does not fill up after chapter three.

Imagine a translator working on a multi-volume legal contract. For every new clause, the translator needs to know the definitions and parties established in earlier clauses. A naive approach would re-read the entire contract from page one before translating each new sentence. A smart translator maintains a glossary and character list that grows as they progress. However, if the glossary is a single scroll, the translator wastes space with large margins for each entry. A well-managed glossary uses index cards of fixed size, adding new cards only when needed, and sharing common definitions across related clauses. KV cache management is the translator's filing system: it stores past context for reuse, organizes it efficiently, and shares common prefixes so memory is never wasted.

**The trade-off:** A larger cache means faster generation but less room for other requests. Quantization saves memory but can slightly degrade output quality. CPU offloading frees GPU memory at the cost of slower access. Management is the art of balancing these knobs for the target latency and throughput requirements.

---

## Tiny Numeric Example

**Memory footprint of a 1B-parameter model KV cache:**

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Batch size | B | 8 |
| Sequence length | S | 1,024 |
| Number of layers | L | 24 |
| Hidden size | H | 2,048 |
| Key/Value tensors per layer | 2 | K and V |
| Bytes per parameter | 2 | FP16 |

| Calculation | Result |
|-------------|--------|
| B × S × L × H × 2 (tensors) × 2 (bytes) | 8 × 1,024 × 24 × 2,048 × 4 |
| Total KV cache memory | 1,610,612,736 bytes ≈ 1.6 GB |

**Scaling scenarios:**

| Scenario | Batch Size | Seq Length | KV Cache Memory |
|----------|-----------|------------|-----------------|
| Base | 8 | 1,024 | 1.6 GB |
| Double batch | 16 | 1,024 | 3.2 GB |
| Double length | 8 | 2,048 | 3.2 GB |
| Double both | 16 | 2,048 | 6.4 GB |

- A single NVIDIA A100 (80 GB) can hold the model weights plus 6.4 GB cache, but naive contiguous allocation wastes ~80% of that cache space.
- With PagedAttention and 16-token blocks, the same workload uses ~4.0 GB of allocated memory instead of 20 GB.

---

## Common Confusion

1. **"The KV cache is the model weights."** It is not. Weights are static and shared across all requests. The KV cache grows with every new token generated and is unique per request.

2. **"Management is just allocation."** It is not. It also includes eviction, swapping to CPU memory, quantization, and sharing across beams or sampling branches.

3. **"A larger cache means better quality."** It does not. Cache size affects generation speed, not output quality. Quality comes from the model weights and architecture.

4. **"KV cache management is automatic in all frameworks."** It is not. Some frameworks require manual tuning of cache size, block allocation, and eviction policies.

5. **"It is only for decoding."** It is not. Prefix caching for prompt processing also uses KV cache management to avoid recomputing shared system prompts.

6. **"Quantizing the KV cache has no quality impact."** It can have a small impact. INT8 quantization usually preserves quality, but aggressive quantization to INT4 may introduce noticeable errors in long contexts.

7. **"CPU offloading is free."** It is not. Moving tensors between GPU and CPU over PCIe introduces latency. It helps memory capacity but hurts per-token latency.

---

## Where It Is Used in Our Code

`src/phase90/phase90_inference_serving.py` — We simulate sequences of varying lengths sharing a fixed total cache budget. We compare naive per-sequence allocation against paged block allocation, demonstrating that intelligent management directly determines how many concurrent requests can be served. The script computes utilization percentages and plots fragmentation over time, saving the result to `kv_cache_fragmentation.png`.
