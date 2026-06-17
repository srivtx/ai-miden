## Why it exists (THE PROBLEM)

A model trained at batch_size=16 can handle 16 requests simultaneously in a batched inference. But if 100 users hit the API, 84 wait. You could increase batch size — but GPU VRAM limits you. A 10M model with KV cache at 1000 tokens × 100 concurrent sequences would need 100 × 1000 × 256 × 4 = 100MB just for the cache. With model weights (40MB) and activations, you might hit the 16GB T4 limit at ~50 concurrent users.

**Inference optimization** is the set of techniques to squeeze maximum throughput from fixed hardware: continuous batching (never idle), paged attention (no memory wasted on padding), KV cache quantization (cut cache memory by 4×), and speculative decoding (predict multiple tokens per forward pass).

These techniques don't change the model. They change how the model is SCHEDULED and how memory is MANAGED. Same weights, same quality, 5-50× more throughput.

## Core techniques

### 1. Continuous batching (orca, vLLM)

Standard batching: wait for N requests to arrive → batch → generate one token for all → repeat. Problem: sequences finish at different times. If one sequence finishes, its slot is idle until the batch completes.

Continuous batching: the batch is a dynamic set. When a new request arrives, add it. When a token generates, add to KV cache. When a sequence finishes (EOS or max length), remove it and free memory. The batch size fluctuates: 10 → 15 → 12 → 18 → 8. No idle slots.

**Gain:** 2-5× throughput at high concurrency.

### 2. Paged attention (vLLM)

Standard KV cache: pre-allocate a contiguous block of memory per sequence: `max_seq_len * head_dim * n_heads * 2 bytes`. For max_seq_len=2048, head_dim=128, 8 heads: 2048 × 128 × 8 × 2 = 4.2MB per sequence. At 100 concurrent sequences, that's 420MB. But most sequences use partial length (maybe 500 tokens before an answer), wasting 3/4 of the allocation.

Paged attention: the KV cache is split into fixed-size "pages" (typically 16 tokens). Each sequence gets pages allocated ON DEMAND as it generates more tokens. When memory is full, evict least-recently-used pages (they can be recomputed). No pre-allocation waste.

**Gain:** With paged attention on a T4, you can fit 4× more concurrent sequences.

### 3. KV cache quantization (INT8/FP8)

The KV cache stores floats (fp16: 2 bytes per element). But attention is robust to quantization noise. If you quantize K and V to INT8 (1 byte per element), you halve the memory with negligible quality loss. GPTQ-style quantization on KV cache: apply a scaling factor per channel, quantize each channel, dequantize before attention.

**Gain:** 2× more sequences in the same VRAM. Combined with paged attention: 8× more throughput.

### 4. Speculative decoding

A small draft model generates K candidate tokens (fast, 1ms). The large target model verifies them all in ONE forward pass (10ms). Accept N of K, generate the rest. The draft model: same architecture but 10× smaller. Or: a simple n-gram model. Or: the target model itself with a low-temperature greedy decode.

**Gain:** 2-3× faster generation (fewer expensive forward passes).

### 5. Prefix caching

If multiple requests share a common prefix (system prompt, few-shot examples), the KV cache for that prefix is computed ONCE and shared. New requests skip the common tokens. Redundant compute: gone.

**Gain:** For chatbots (long system prompts), the first 1000 tokens cost ZERO for subsequent requests.

## The combined effect

A standard FastAPI serving loop handles 1 request/second on a T4 with a 10M model. With: continuous batching (+3×), paged attention (+4× sequences), KV cache INT8 (+2×), speculative decoding (+2×), prefix caching (+1.5×). The combined improvement isn't additive — it's multiplicative: 3 × 4 × 2 × 2 × 1.5 = 72×. 1 req/s → ~70 req/s on the same hardware.

In practice, the gains overlap (each doesn't multiply perfectly), so you get 10-30× improvement. Still: 1 request/second → 10-30 requests/second. Same T4. Same model. Same quality.

## Connection to our projects

**cortexcode:** Add continuous batching to `cortexcode_api.py`. Replace the single-sequence generate loop with a batched scheduler. Use paged attention (vLLM or manual page table). Quantize KV cache. This is ~200 lines of Python + vLLM integration. Goes from 1 req/s to 10-30 req/s.
