## What Is Disaggregated Serving?

---

### The Problem

Modern LLM serving systems pack as many requests as possible onto each GPU to maximize utilization. But the prefill phase (compute-heavy) and decode phase (memory-bandwidth-heavy) fight for the same silicon resources. A GPU running prefill wastes memory bandwidth; a GPU running decode wastes compute units. In a datacenter with thousands of GPUs, this mismatch means you are paying for H100s but using them like cheap bandwidth cards or underloaded compute engines. How do you architect a system where every dollar of GPU time is spent on the right kind of work?

---

### Definition

**Disaggregated Serving** is a datacenter-scale inference architecture that physically separates prefill computation and decode computation onto different pools of GPUs. Prefill GPUs are optimized for raw compute throughput (large matrix multiplies), while decode GPUs are optimized for memory bandwidth and KV cache capacity. Requests flow from prefill GPUs to decode GPUs via a KV cache handoff, allowing each pool to operate at its hardware sweet spot.

**How it works:**
```
Traditional colocated serving:
  All GPUs are identical
  Each GPU runs both prefill AND decode for its assigned requests
  Result: GPUs spend most of their time memory-bound in decode,
         with compute units sitting idle

Disaggregated serving:
  Prefill Cluster (H100s with high compute):
    - Receives new requests
    - Processes entire prompt in one forward pass
    - Computes KV cache for all prompt tokens
    - Ships KV cache to decode cluster
    - Immediately picks up next request

  Decode Cluster (A100s or H100s with high bandwidth):
    - Receives KV cache from prefill cluster
    - Generates tokens one at a time
    - Batches many requests together to saturate memory bandwidth
    - Returns completed responses

  Load Balancer:
    - Routes incoming requests to least-loaded prefill GPU
    - Routes KV caches to decode GPUs with available capacity
```

**Key techniques:**
- **KV cache migration:** transferring key and value tensors from prefill to decode GPUs via high-speed interconnect (NVLink, InfiniBand)
- **Chunked prefill as bridge:** when load is uneven, prefill GPUs can process prompts in chunks and hand off incrementally
- **Dynamic batching on decode:** decode GPUs accumulate requests into large batches to maximize memory bandwidth utilization
- **Cost modeling:** deciding how many prefill vs. decode GPUs to provision based on traffic patterns (prompt length distribution, output length distribution, arrival rate)

**Why this matters:**
- Colocated serving achieves ~30-50% of peak GPU capability because phases conflict
- Disaggregated serving can achieve 70-90% of each GPU's specialized capability
- For high-throughput workloads (batch size 8+), total throughput improves 2-3x
- Cost per token drops because you are not paying for idle compute or wasted memory bandwidth

---

### Real-Life Analogy

Imagine a massive airport baggage system.
- **Colocated serving:** Each baggage handler both checks passports (prefill) and drives luggage carts (decode). Passport checking requires careful reading and decision-making (compute). Cart driving requires moving quickly through hallways (bandwidth). When a handler is reading passports, carts sit idle. When driving carts, the handler is not processing new passengers. The airport needs twice as many handlers as necessary because each one is only productive half the time.
- **Disaggregated serving:** The airport builds a passport control wing and a separate cart delivery wing. Passport officers never leave their booths; they specialize in rapid, accurate checks. Cart drivers never touch passports; they loop continuously between terminals. Passengers flow from passport control to cart pickup via a moving walkway (KV cache handoff). The passport wing is designed with bright lights and magnifying glasses (compute). The cart wing is designed with wide corridors and fast vehicles (bandwidth). The same total staff now moves 3x as many passengers because nobody is switching tasks.
- **The trade-off:** The airport needs two separate buildings instead of one. There is a cost to the moving walkway infrastructure. If passenger volume is low, the dedicated wings are underutilized and the single-building model is cheaper. Disaggregation only wins at scale.

---

### Tiny Numeric Example

**Datacenter with 16 GPUs, 1000 requests/hour:**
```
Request profile:
  Average prompt length: 512 tokens
  Average output length: 256 tokens
  Batch size target: 8

Colocated serving (16 identical A100s):
  Each GPU handles ~62 requests
  Prefill time per request: 512 tokens * 0.0001s/token = 0.051s
  Decode time per request: 256 tokens * 0.015s/token = 3.84s
  Total time per request: ~3.9s
  But with batching, decode can overlap:
    Effective throughput: ~4 requests/sec per GPU
    Total throughput: 16 * 4 = 64 requests/sec
    Capacity at 1000 requests/hour: easily handled, but inefficient
    GPU utilization: 30% compute, 25% bandwidth

Disaggregated serving (8 prefill + 8 decode A100s):
  Prefill cluster (8 GPUs):
    Each GPU: 125 requests/hour = 0.035 requests/sec
    Time per prefill: 0.051s
    Prefill GPU utilization: 85% compute
    
  Decode cluster (8 GPUs):
    Each GPU: 125 requests, 256 tokens each = 32,000 tokens
    Decode time: 32,000 * 0.015s / 8 GPUs = 60s per GPU
    With batch=8: effective time = 32,000 * 0.015s / 8 = 60s
    Decode GPU utilization: 80% bandwidth
    
  Total throughput: 8 * 16 = 128 requests/sec (theoretical)
  Effective capacity: 2x colocated for same hardware
  Cost per request: ~50% lower
```

**Provisioning ratio (prefill:decode GPUs):**
```
Traffic pattern A (short prompts, long outputs):
  128-token prompts, 1024-token outputs
  Ratio: 1 prefill GPU per 8 decode GPUs

Traffic pattern B (long prompts, short outputs):
  2048-token prompts, 64-token outputs
  Ratio: 4 prefill GPUs per 1 decode GPU

Traffic pattern C (balanced):
  512-token prompts, 256-token outputs
  Ratio: 1 prefill GPU per 2-3 decode GPUs
```

---

### Common Confusion

1. **"Disaggregated serving means microservices."** No. Microservices split by API endpoint. Disaggregated serving splits by computation phase within a single inference request. Both prefill and decode run the same model; they just run different phases on different hardware.

2. **"You need different GPU types for prefill and decode."** Not strictly. You can use the same GPU model for both pools. The separation is about workload specialization, not hardware heterogeneity. However, using H100s for prefill and A100s for decode is common because H100s have better compute and A100s have better price/bandwidth.

3. **"KV cache transfer takes longer than the decode itself."** For small batches over slow interconnect, this can be true. But with NVLink (900 GB/s) or InfiniBand, transferring a 512-token KV cache for a 7B model takes ~2ms. A single decode step takes 10-15ms, so transfer is 10-20% overhead, not a bottleneck.

4. **"Disaggregated serving increases latency."** For the first token, yes, because the request must traverse the prefill cluster before decode begins. But total time-to-complete can be lower because decode runs at higher throughput. For streaming APIs, users see the first token slightly later but subsequent tokens arrive faster.

5. **"This is only useful for cloud providers."** Any organization running LLM inference at scale benefits. If you have 4+ GPUs, you can create mini-clusters and see gains. The principles apply to on-premise, private cloud, and edge deployments.

6. **"Disaggregated serving is the same as pipeline parallelism."** Pipeline parallelism splits model layers across GPUs. Disaggregated serving splits *phases* across GPUs while each GPU still holds the full model. They are orthogonal: you can combine pipeline parallelism within the prefill cluster or decode cluster.

7. **"Once separated, you cannot mix prefill and decode on the same GPU."** In practice, systems allow overflow. If prefill GPUs are saturated, decode GPUs can handle small prefills. If decode GPUs are saturated, prefill GPUs can do short decodes. The separation is a scheduling preference, not a hard wall.

---

### Where It Is Used in Our Code

`src/phase120/phase120_serving_concepts.py` — We simulate a datacenter with colocated vs. disaggregated serving. We model request arrival rates, prompt lengths, and output lengths, then show how separating prefill and decode GPUs improves total throughput and reduces cost per token.

`src/phase120/phase120_serving_colab.py` — We profile real LLaMA inference on a T4 GPU and calculate theoretical throughput improvements if prefill and decode were separated. We discuss why real disaggregation requires H100-class hardware and NVLink for the KV cache handoff.
