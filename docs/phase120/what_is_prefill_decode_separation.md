## What Is Prefill/Decode Separation?

---

### The Problem

A large language model handles two very different workloads during inference. First, it must process the entire user prompt in one go, computing attention across all prompt tokens simultaneously. This is called the prefill phase. Then, it must generate output tokens one by one, each depending on all previous tokens. This is called the decode phase. These two phases have opposite hardware bottlenecks: prefill is compute-bound, while decode is memory-bandwidth-bound. When they run on the same GPU, one phase always starves the other of the resource it needs most.

---

### Definition

**Prefill/Decode Separation** is the architectural decision to run the prompt-processing phase (prefill) and token-generation phase (decode) on different hardware or at different times, rather than interleaving them on the same GPU. Prefill needs massive matrix multiply throughput (FLOPs), while decode needs high memory bandwidth to stream KV caches. Separating them allows each phase to run on hardware optimized for its specific bottleneck.

**How it works:**
```
Colocated serving (inefficient):
  GPU 1: [Prefill prompt A] → [Decode token 1] → [Prefill prompt B] → [Decode token 1]
  Problem: prefill wants compute, decode wants bandwidth; they fight for resources
  Result: GPU is underutilized in both phases

Separated serving (efficient):
  Prefill GPUs: [Prefill prompt A] → [Prefill prompt B] → [Prefill prompt C]
  Decode GPUs:  [Decode A token 1..N] || [Decode B token 1..N] || [Decode C token 1..N]
  
  Prefill GPUs: max out tensor cores (compute-bound)
  Decode GPUs:  max out HBM bandwidth (memory-bound)
  Result: each GPU type operates at its strength
```

**Key characteristics:**
- **Prefill phase:** processes all prompt tokens at once. Time scales with prompt length. FLOP-intensive because attention computes Q@K^T for all pairs.
- **Decode phase:** generates one token per forward pass. Time scales with output length. Memory-bandwidth-intensive because each forward pass must load the full KV cache for all previous tokens.
- **KV cache handoff:** after prefill, the computed key and value tensors must transfer from prefill GPUs to decode GPUs

**Why this matters:**
- Prefill on an H100 achieves >80% compute utilization because matrix multiplies are large
- Decode on the same H100 achieves <10% compute utilization because it is waiting for memory
- Separating them onto different GPU pools can improve total throughput by 2-3x
- High-throughput serving (batch size 8+) benefits most because decode batches amortize memory bandwidth

---

### Real-Life Analogy

Imagine a restaurant with a kitchen and a dining room.
- **Prefill:** The kitchen receives a complex order with ten special instructions. The chef reads the entire ticket, gathers all ingredients, and preps everything before cooking begins. This is mentally intensive but happens once per order. The chef needs a big brain (compute).
- **Decode:** The waiter brings out dishes one at a time to the table. Each trip is short and simple, but the waiter must walk back and forth many times. The limiting factor is not the waiter's intelligence but how fast they can walk (memory bandwidth).
- **The trade-off:** If the same person is both chef and waiter, they spend most of their time walking, and the kitchen sits idle. Separating the roles means hiring a dedicated chef (prefill GPU) who never leaves the kitchen and dedicated waiters (decode GPUs) who only walk. Throughput increases because each person specializes in what they are good at. The cost is coordination: the kitchen must hand off plated dishes to the waiters efficiently.

---

### Tiny Numeric Example

**Prefill phase (batch size 1, prompt length 1024):**
```
Model: 7B parameters, 4096 hidden dim, 32 heads
Attention FLOPs: 2 * batch * seq^2 * heads * head_dim
                = 2 * 1 * 1024^2 * 32 * 128
                = 8.6 trillion FLOPs

Time on A100 (312 TFLOP/s theoretical):
  Actual compute utilization: ~70%
  Effective throughput: ~218 TFLOP/s
  Time: 8.6e12 / 218e12 = 0.039 seconds

Memory bandwidth used:
  KV cache written: 2 * 1024 * 4096 * 2 bytes = 16.8 MB
  Bandwidth: negligible compared to compute
```

**Decode phase (batch size 1, generating 1 token):**
```
Attention FLOPs: 2 * 1 * 1024 * 32 * 128 = 8.4 billion FLOPs
Time at 218 TFLOP/s: 8.4e9 / 218e12 = 0.000039 seconds

But memory bandwidth:
  KV cache read: 2 * 1024 * 4096 * 2 bytes = 16.8 MB per token
  At A100 bandwidth (2 TB/s): 16.8e6 / 2e9 = 0.000008 seconds

Actual decode time: ~0.015 seconds per token
Why? Overheads, kernel launch, attention implementation inefficiencies.
Compute utilization during decode: <5%
```

**Throughput comparison for 100 prompts of 1024 tokens, generating 100 tokens each:**
```
Colocated on 8x A100:
  Prefill time: 100 * 0.039s = 3.9s
  Decode time:  100 * 100 * 0.015s = 150s
  Total time:   ~154s
  Throughput:   100 requests / 154s = 0.65 requests/sec

Disaggregated (4 prefill + 4 decode GPUs):
  Prefill GPUs: 100 prompts / 4 GPUs = 25 each
  Prefill time: 25 * 0.039s = 0.98s (parallel)
  Decode GPUs:  100 * 100 tokens / 4 GPUs = 2500 tokens each
  Decode time:  2500 * 0.015s = 37.5s (parallel)
  Total time:   ~38.5s
  Throughput:   100 / 38.5 = 2.6 requests/sec  (4x improvement)
```

---

### Common Confusion

1. **"Prefill is always slower than decode."** For very long prompts, prefill can take longer than a single decode step. But per-token cost, decode is far more expensive because it cannot parallelize across the sequence. A 2048-token prefill is one large matrix multiply; 2048 decode steps are 2048 tiny memory-bound operations.

2. **"Separation means two copies of the model weights."** Yes, prefill and decode GPUs each load the full model weights. This doubles memory usage but is the trade-off for specialization. Weight sharing across NVLink or via CPU DRAM is an active research area.

3. **"Prefill/Decode separation only matters for batch size 1."** Actually, it matters more for large batches. Large decode batches improve memory bandwidth utilization, making decode GPUs more efficient. Small batches see less benefit because decode overhead dominates.

4. **"You can separate prefill and decode on the same GPU by time-slicing."** That is chunked prefill, not full separation. Time-slicing on one GPU still suffers from the hardware mismatch. True disaggregation uses physically different GPU pools.

5. **"KV cache transfer between GPUs is a bottleneck."** For small batches, yes. But at scale, the transfer is pipelined: while decode GPU 1 processes batch A, prefill GPU 1 prepares batch B. With InfiniBand or NVLink, transfer latency is amortized across large batches.

6. **"Prefill GPUs sit idle after all prompts are processed."** In steady-state high-throughput serving, new requests arrive continuously. Prefill GPUs process incoming prompts as fast as they arrive, and decode GPUs drain them. Idle time is minimal if load balancing is correct.

7. **"This only applies to transformer models."** While transformers make the distinction clearest due to their KV cache, any autoregressive model with stateful inference has a prefill-equivalent (initial state computation) and decode-equivalent (stateful generation). The principle generalizes.

---

### Where It Is Used in Our Code

`src/phase120/phase120_serving_concepts.py` — We simulate LLM inference with distinct prefill and decode phases, profiling compute vs. memory bandwidth for each. We show how prefill time scales with prompt length while decode time scales with output length, then simulate disaggregated serving to demonstrate the throughput improvement.

`src/phase120/phase120_serving_colab.py` — We profile real prefill and decode times on a T4 GPU using LLaMA-3.2-3B. We measure the compute/memory asymmetry and calculate theoretical throughput gains from disaggregated serving, while noting that T4 is not the ideal hardware for this architecture.
