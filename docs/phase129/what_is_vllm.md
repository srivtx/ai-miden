## What Is vLLM?

---

### The Problem

You have a 70-billion-parameter model that answers one question in 3 seconds. Then you put it behind an API and 100 users hit it simultaneously. Each user now waits 5 minutes. Your GPU memory is 80% wasted because every request allocates a giant contiguous block for its entire sequence, even though most of the sequence is empty padding. You try batching, but requests finish at different times, so you either pad everything to the longest running request or you waste even more time. Naive inference breaks down the moment it leaves the notebook.

---

### Definition

**vLLM** is an open-source inference engine that serves large language models with **PagedAttention**, **continuous batching**, and **prefix caching**. It treats GPU memory like an operating system treats RAM: allocating small non-contiguous blocks that can be shared, evicted, and reused on demand. This lets vLLM pack far more concurrent requests onto the same hardware than a standard HuggingFace pipeline.

**How it works:**
```
Naive inference:
  Request A → allocates 4096-token KV cache block (uses 512 tokens)
  Request B → allocates 4096-token KV cache block (uses 128 tokens)
  Request C → allocates 4096-token KV cache block (uses 2048 tokens)
  Result: 3 blocks × 4096 = 12,288 slots, 6,208 used, 6,080 wasted (49%)

vLLM PagedAttention:
  Memory is split into 16-token "pages"
  Request A → 32 pages (512 tokens), non-contiguous
  Request B → 8 pages (128 tokens), reuses freed pages from A
  Request C → 128 pages (2048 tokens), fits in gaps
  Result: 168 pages used, zero internal fragmentation
```

**Key techniques:**
- **PagedAttention:** KV cache is stored in fixed-size blocks (like OS pages); blocks are mapped via a lookup table, so physical storage need not be contiguous
- **Continuous batching:** new requests are added to the current batch every decoding step; finished requests are removed immediately instead of waiting for the slowest one
- **Prefix caching:** if multiple requests share the same system prompt or conversation history, their KV cache blocks are stored once and referenced by multiple sequences

**Why this matters:**
- vLLM routinely achieves 10-20x higher throughput than naive generate() on the same GPU
- You can serve Llama-3-8B on a single A100 to hundreds of concurrent users
- The scheduling logic is automatic; you do not rewrite your model, you just call `vllm.LLM`

---

### Real-Life Analogy

A restaurant with tables vs. a sushi conveyor belt.
- **Naive inference:** A traditional restaurant where each party gets an entire table for the whole evening. A couple of two sits at a ten-seat table. A solo diner sits at another ten-seat table. Fifty seats, ten guests, forty seats wasted. Nobody else can sit until the current party leaves.
- **vLLM:** A sushi conveyor belt. Diners take only the plates they need, in whatever order they arrive. Two people share the same belt. A solo diner grabs three plates and leaves in five minutes. The belt never stops; new diners step up the moment space opens. Every inch of belt is used continuously.
- **Prefix caching:** If five friends all order the same appetizer, the kitchen makes one batch and plates five portions from it. They do not cook the appetizer five times.

---

### Tiny Numeric Example

**Three requests on a 4096-token model:**
```
Request A: prompt 256 tokens, generate 128 tokens
Request B: prompt 64 tokens, generate 512 tokens
Request C: prompt 128 tokens, generate 256 tokens
```

**Naive HuggingFace generate(batch_size=3):**
```
Batch padded to longest sequence = 256 + 512 = 768 tokens
Memory per layer = 3 × 768 × 4096 (hidden) × 2 (K+V) × 2 bytes (fp16)
                 = 3 × 768 × 4096 × 4 bytes = 37.7 MB per layer
For 32 layers = 1.21 GB just for KV cache
Effective batch utilization: 64% (because B and C waste padding)
Throughput: 42 tokens/sec total
```

**vLLM PagedAttention (block size 16):**
```
No padding. Each request uses exactly its token count.
A: 256 + 128 = 384 tokens → 24 blocks
B: 64 + 512 = 576 tokens → 36 blocks
C: 128 + 256 = 384 tokens → 24 blocks
Total blocks: 84. No fragmentation because blocks are fixed size.
Memory for same 32 layers: 0.79 GB (35% savings)
Continuous batching lets new requests join on every step.
Throughput: 680 tokens/sec total (16× faster)
```

**The shift:** Same model, same GPU, same requests. vLLM eliminates padding waste and keeps the GPU busy every cycle.

---

### Common Confusion

1. **"vLLM is a model."** No. vLLM is an inference engine. It serves models (Llama, Qwen, Mistral) but is not itself a model architecture.

2. **"PagedAttention means the model has fewer parameters."** No. The model weights are identical. PagedAttention only changes how the key-value cache is stored and scheduled in memory.

3. **"vLLM only helps at large batch sizes."** It helps at all batch sizes, but the gap widens as concurrency grows. Even a single long sequence benefits from block-based allocation because memory is never over-provisioned.

4. **"Continuous batching is the same as dynamic batching."** Dynamic batching collects requests into a bucket and runs them together, but everyone waits for the slowest. Continuous batching adds and removes requests at every decoding step.

5. **"Prefix caching only works for identical prompts."** It works for any shared prefix: system prompts, few-shot examples, document chunks in RAG. Even a shared first sentence triggers reuse.

6. **"vLLM replaces TensorRT-LLM."** They solve overlapping but distinct problems. vLLM excels at serving diversity of requests and dynamic scheduling. TensorRT-LLM excels at maximizing single-request latency on NVIDIA hardware with aggressive kernel fusion.

7. **"You need a cluster to use vLLM."** A single consumer GPU works fine. vLLM is most famous for datacenter scale, but the optimizations apply equally to a single RTX 4090.

---

### Where It Is Used in Our Code

`src/phase129/phase129_inference_concepts.py` — We simulate PagedAttention by showing how fixed-size blocks eliminate memory fragmentation compared to contiguous allocation. We plot throughput vs. batch size curves to show why continuous batching outperforms static batching.

`src/phase129/phase129_inference_colab.py` — We compare real inference with HuggingFace `model.generate()` (baseline), HuggingFace with KV cache enabled, and vLLM (or batched simulation) on Llama-3.2-3B-Instruct. We measure TTFT, TPOT, throughput, and peak memory to demonstrate the 5-10× speedup.

(End of file)
