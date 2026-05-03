## What Is Batch Optimization?

---

### The Problem

Real users do not send requests of identical length. One user asks "Hi" (1 token). Another pastes a legal contract and asks for a summary (4,000 tokens). Your model expects rectangular input tensors, so you must pad every short sequence to match the longest one in the batch. If you batch the 1-token greeting with the 4,000-token contract, you pay for 4,000 tokens of computation for the greeting — a 4,000x waste on that sample. Worse, padding tokens still consume memory and bandwidth. On a production system handling thousands of requests per minute, this waste translates directly into dollars and user frustration. How do you group requests so the GPU is fed efficiently without making any user wait too long?

---

### Definition

**Batch optimization** is the set of techniques that minimize wasted computation and memory when serving variable-length inputs. The three pillars are:

1. **Dynamic batching:** Requests are held in a queue for a short time window (e.g., 10ms). As requests arrive, the scheduler groups them into a batch that fits within a latency budget, rather than using a fixed batch size.

2. **Padding strategies:** Deciding where to insert padding tokens (left vs. right) and whether to use "bucketing" — pre-defined length buckets (0-64, 65-128, etc.) so sequences within a bucket are padded only to the bucket max, not the global max.

3. **Memory-aware scheduling:** The scheduler estimates the memory required for a candidate batch (KV cache size scales with batch_size × sequence_length) and rejects batches that would cause an out-of-memory error.

**Why this matters:**
- Dynamic batching can improve throughput 2-3x over static batching on real traffic
- Bucketing reduces padding waste from 50% to under 10% on typical workloads
- Memory-aware scheduling prevents crashes that would drop all in-flight requests

---

### Real-Life Analogy

A laundromat.
- **No optimization:** Every load, whether one sock or a king comforter, runs in a separate industrial washer for a full 60-minute cycle. The water and electricity cost is the same. Most machines are 90% empty.
- **Static batching:** You wait until you have exactly 8 loads, then start 8 machines. But one load is a comforter that needs 90 minutes. The other 7 loads of t-shirts are done in 30 minutes, yet you cannot remove them until the comforter finishes.
- **Dynamic batching + bucketing:** You sort clothes into small/medium/large machines. As soon as a small machine has 4 loads, it starts. A medium machine starts with 3 loads. The comforter goes alone in a large machine. No machine runs half-empty, and no t-shirt waits for a comforter.

---

### Tiny Numeric Example

**Setup:** 4 requests with token lengths [5, 10, 15, 20]. Per-token compute cost = 1 unit. Fixed overhead per batch = 10 units.

**No batching (4 separate forwards):**
```
Cost = (10 + 5) + (10 + 10) + (10 + 15) + (10 + 20) = 90 units
```

**Naive static batch (pad all to 20):**
```
Cost = 10 + (4 × 20) = 90 units
```
Wait — same cost? Yes, but in reality the 4 separate forwards have 4x kernel launch overhead, so naive batching is still faster. The real problem is memory: KV cache reserves space for 4 × 20 = 80 tokens even though only 50 tokens are real.

**Dynamic batching with bucketing (bucket size 8 and 24):**
```
Bucket A: [5, 10] padded to 10  -> cost = 10 + (2 × 10) = 30
Bucket B: [15, 20] padded to 20 -> cost = 10 + (2 × 20) = 50
Total cost = 80 units
Padding waste reduced from 30 tokens to 10 tokens.
```

**Result:** Bucketing alone saved 10 units (11%). On a real system with hundreds of requests and memory constraints, the savings compound into 2-3x throughput gains.

---

### Common Confusion

1. **"Dynamic batching means variable batch size is always better."** Not always. If traffic is sparse, holding requests to form a batch increases queuing latency. The optimizer must balance wait time against compute efficiency.

2. **"Left padding and right padding are interchangeable."** No. Causal language models attend to all previous tokens. If you left-pad, the model sees padding tokens before real tokens, which can shift position embeddings and hurt quality. Most LLM serving uses left padding for encoder models and left padding carefully managed for decoders.

3. **"Bucketing requires recompiling the model for each bucket."** No. Modern frameworks like PyTorch and JAX use dynamic shapes. Bucketing is purely a data-preprocessing decision; the same model graph handles all shapes.

4. **"Batch optimization only matters for NLP."** No. Vision models with variable image sizes, audio models with different clip lengths, and multimodal models all suffer from the same padding waste and benefit from dynamic batching.

5. **"The scheduler should always fill the maximum batch size."** No. Memory usage scales quadratically with sequence length for attention (O(n²) in the naive case, O(n) with KV cache but still linear in batch). A batch of 32 long sequences can OOM while a batch of 64 short sequences is fine.

6. **"Zero-padding is free because multiply-by-zero is cheap."** No. Padding tokens still traverse every layer, every matrix multiplication, and every attention head. Hardware does not skip zero rows automatically unless specifically optimized (e.g., sparse kernels).

7. **"Batch optimization is only about throughput."** No. It is equally about reliability. Memory-aware scheduling prevents out-of-memory crashes that would drop every request in flight, not just the oversized one.

---

### Where It Is Used in Our Code

`src/phase71/phase71_inference_deployment.py` — We generate synthetic requests of random lengths, sort them into length buckets, and compute the exact padding waste saved versus naive batching. We also simulate a dynamic batching scheduler that caps wait time.

`src/phase71/phase71_inference_deployment_colab.py` — We show how the transformers `DataCollatorWithPadding` and vLLM's internal scheduler automatically handle bucketing and dynamic batching, and we measure the throughput difference with and without these optimizations.
