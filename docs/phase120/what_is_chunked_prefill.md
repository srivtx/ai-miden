## What Is Chunked Prefill?

---

### The Problem

Full disaggregated serving requires multiple GPU pools and high-speed interconnects, which many teams cannot afford or manage. But colocated serving still suffers from the prefill/decode mismatch. When a long prompt arrives, the GPU spends 100ms in prefill while decode requests in the same batch sit frozen. When generating tokens, the GPU wastes compute units waiting for memory. Is there a middle ground that smooths out these phase mismatches without needing separate hardware?

---

### Definition

**Chunked Prefill** is a scheduling technique that breaks long prompts into smaller chunks and interleaves prefill computation with decode computation on the same GPU. Instead of processing an entire 2048-token prompt in one monolithic forward pass, the system processes 256 tokens at a time, slipping in a decode step between chunks. This prevents decode requests from starving during long prefills and keeps the GPU utilization more uniform.

**How it works:**
```
Standard scheduling (inefficient):
  Batch: [Prefill 2048 tokens, Decode A, Decode B, Decode C]
  Time 0-100ms: GPU runs prefill for 2048 tokens
                 Decodes A, B, C are BLOCKED and waiting
  Time 100-115ms: GPU runs decode for A, B, C
  Result: decodes wait 100ms; GPU is 100% prefill then 100% decode

Chunked prefill (efficient):
  Batch: [Prefill 2048 tokens, Decode A, Decode B, Decode C]
  Chunk size: 256 tokens
  
  Time 0-12ms:   Prefill chunk 1 (tokens 1-256)
  Time 12-15ms:  Decode step for A, B, C
  Time 15-27ms:  Prefill chunk 2 (tokens 257-512)
  Time 27-30ms:  Decode step for A, B, C
  ...
  Time 84-96ms:  Prefill chunk 8 (tokens 1793-2048)
  Time 96-99ms:  Decode step for A, B, C
  
  Result: decodes get tokens every ~15ms instead of waiting 100ms
          GPU never sits fully idle in one phase for long
```

**Key techniques:**
- **Fixed chunk size:** typically 256-512 tokens. Smaller chunks mean more frequent decode interleaving but higher scheduling overhead. Larger chunks reduce overhead but block decodes longer.
- **Priority scheduling:** decode requests often get higher priority because users are actively waiting for tokens. Prefill chunks yield to decodes when the queue grows.
- **KV cache accumulation:** each prefill chunk appends to the KV cache. After all chunks are processed, the full prompt's KV cache is ready for decode.
- **Dynamic chunk sizing:** some systems adjust chunk size based on queue depth. Deep queues get smaller chunks to reduce decode latency.

**Why this matters:**
- Chunked prefill reduces time-to-first-token latency for decode requests by 5-10x when long prefills are in the batch
- It improves GPU utilization by avoiding long monolithic prefills that starve other work
- It requires no extra hardware: everything runs on the same GPU pool
- It is the standard technique in production serving frameworks (vLLM, TensorRT-LLM, TGI)

---

### Real-Life Analogy

Imagine a doctor's office with one examination room.
- **Standard scheduling:** A patient arrives with a massive stack of medical records (long prefill). The doctor locks the door and spends 30 minutes reading every page before seeing any other patients. Three patients with quick follow-up questions (decode) sit in the waiting room getting increasingly annoyed. After 30 minutes, the doctor briefly sees each follow-up, then locks the door again for the next big records review.
- **Chunked prefill:** The doctor reads 5 pages of the big records, then opens the door and sees one follow-up patient for 2 minutes. Then reads 5 more pages, sees another follow-up. The big records patient still gets full attention, just in slices. The follow-up patients wait 7 minutes instead of 30. The doctor's day is more evenly paced, and nobody storms out of the waiting room.
- **The trade-off:** The big records patient takes slightly longer to finish because the doctor keeps pausing. A 30-minute uninterrupted review becomes a 35-minute chunked review. But the overall office throughput is higher because follow-ups are not blocked. For the health of the practice (GPU utilization), this is the right trade.

---

### Tiny Numeric Example

**Batch with 1 long prefill and 3 decode requests:**
```
Prompt: 1024 tokens
Chunk size: 256 tokens
Decode step time: 15ms
Prefill chunk time: 12ms per 256 tokens

Standard (no chunking):
  Prefill: 1024 * 0.00012 = 122ms
  Decodes blocked: 0-122ms
  Decode steps: 122-167ms
  Decode latency: 122ms (time until first token)
  Total batch time: 167ms

Chunked prefill (4 chunks):
  Chunk 1:   0-12ms   (prefill 1-256)
  Decodes:   12-27ms  (all 3 decodes)
  Chunk 2:   27-39ms  (prefill 257-512)
  Decodes:   39-54ms
  Chunk 3:   54-66ms  (prefill 513-768)
  Decodes:   66-81ms
  Chunk 4:   81-93ms  (prefill 769-1024)
  Decodes:   93-108ms
  
  Decode latency: 12ms (first chance to run)
  Total batch time: 108ms
  Speedup: 1.55x faster completion
  Decode starvation: eliminated
```

**GPU utilization comparison:**
```
Standard scheduling:
  0-122ms:  100% prefill, 0% decode
  122-167ms: 0% prefill, 100% decode
  Average utilization: 50% of each capability

Chunked prefill:
  Every 27ms cycle: 12ms prefill + 15ms decode
  Prefill share: 44%, Decode share: 56%
  Average utilization: ~85% of both capabilities
  (some overhead from context switching)
```

---

### Common Confusion

1. **"Chunked prefill is the same as disaggregated serving."** No. Chunked prefill keeps both phases on the same GPU and interleaves them in time. Disaggregated serving puts them on different GPUs entirely. Chunked prefill is a software scheduling technique; disaggregation is a hardware architecture.

2. **"Chunked prefill reduces prefill throughput."** Yes, slightly. A chunked prefill takes longer to complete than a monolithic prefill because of decode interruptions and context-switching overhead. But total system throughput improves because decodes are not starved.

3. **"Smaller chunks are always better."** No. Very small chunks (e.g., 64 tokens) create excessive kernel launch overhead and fragment the attention computation. The sweet spot is typically 256-512 tokens for modern models.

4. **"Chunked prefill solves the compute/bandwidth mismatch."** It mitigates the scheduling problem but does not solve the fundamental mismatch. The GPU still switches between compute-heavy and bandwidth-heavy workloads. True separation requires disaggregation.

5. **"Chunked prefill only helps when long and short requests mix."** That is where the benefit is most visible. If all requests have identical lengths, standard batching is already efficient and chunking adds unnecessary overhead.

6. **"You can use infinite chunk size and it becomes standard prefill."** Yes. Chunked prefill is a generalization of standard scheduling where chunk size equals prompt length. Most serving frameworks expose chunk size as a tunable parameter.

7. **"Chunked prefill hurts the long-prompt request's latency."** Yes, marginally. The long-prompt request takes longer to finish prefill because the GPU pauses for decodes. But in a multi-tenant system, overall user satisfaction is higher because no single request monopolizes the GPU.

---

### Where It Is Used in Our Code

`src/phase120/phase120_serving_concepts.py` — We simulate a GPU batch containing both long prefills and decode requests. We compare standard scheduling (monolithic prefill) against chunked prefill, measuring decode latency and total batch completion time. We show that chunked prefill eliminates decode starvation at a small cost to prefill latency.

`src/phase120/phase120_serving_colab.py` — We profile real LLaMA inference with varying prompt lengths and show how decode throughput drops when long prefills block the GPU. We discuss how production serving frameworks use chunked prefill to maintain steady token generation rates.
